import { useEffect, useState, useCallback, useRef } from 'react'
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Label,
} from 'recharts'
import {
  Activity, ShieldAlert, BarChart3, Ban,
  Wifi, WifiOff, Trash2, ShieldX, Monitor, ChevronRight,
  Shield, AlertTriangle, Radio, Download,
} from 'lucide-react'
import {
  getStats, getHistory, blockIp, unblockIp, clearHistory,
  type Stats, type FlowEntry,
} from '../services/api'
import { useMonitorWs } from '../hooks/useWebSocket'
import { useT, useSettings } from '../i18n'

const COLORS_PIE = ['#ef4444', '#f59e0b', '#22d3ee', '#8b5cf6', '#ec4899', '#22c55e']

/* ── Custom tooltip ─────────────────────────────────────────────────── */

function ChartTooltip({ active, payload, label, isDark }: any) {
  if (!active || !payload?.length) return null
  return (
    <div className={`${isDark ? 'bg-[#0c1222] border-amber-500/20' : 'bg-white border-slate-200'} border rounded-lg px-4 py-3 shadow-xl ${isDark ? 'shadow-black/40' : 'shadow-slate-200/60'} backdrop-blur-sm`}>
      <p className={`text-[11px] ${isDark ? 'text-slate-500' : 'text-slate-500'} font-mono mb-1.5`}>{label}</p>
      {payload.map((p: any, i: number) => (
        <div key={i} className="flex items-center gap-2 text-xs">
          <span className="w-2 h-2 rounded-full" style={{ background: p.color }} />
          <span className={`${isDark ? 'text-slate-400' : 'text-slate-600'} capitalize`}>{p.dataKey}:</span>
          <span className={`font-bold font-mono ${isDark ? 'text-slate-200' : 'text-slate-800'}`}>{p.value}</span>
        </div>
      ))}
    </div>
  )
}

function PieTooltip({ active, payload, isDark, t }: any) {
  if (!active || !payload?.length) return null
  const d = payload[0]
  return (
    <div className={`${isDark ? 'bg-[#0c1222] border-amber-500/20' : 'bg-white border-slate-200'} border rounded-lg px-4 py-3 shadow-xl ${isDark ? 'shadow-black/40' : 'shadow-slate-200/60'} backdrop-blur-sm`}>
      <p className={`text-xs font-semibold ${isDark ? 'text-slate-200' : 'text-slate-800'}`}>{d.name}</p>
      <p className="text-xs font-mono text-amber-500 mt-0.5">{d.value} {t('common.flows')}</p>
    </div>
  )
}

/* ── Pie label renderer ─────────────────────────────────────────────── */

function renderPieLabel({ cx, cy, midAngle, innerRadius, outerRadius, name, percent }: any) {
  const RADIAN = Math.PI / 180
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5
  const x = cx + radius * Math.cos(-midAngle * RADIAN)
  const y = cy + radius * Math.sin(-midAngle * RADIAN)
  if (percent < 0.05) return null
  return (
    <text x={x} y={y} fill="#e2e8f0" textAnchor="middle" dominantBaseline="central"
      fontSize={10} fontWeight={600} fontFamily="Inter, sans-serif">
      {name.length > 8 ? name.slice(0, 7) + '..' : name}
    </text>
  )
}

/* ── Severity badge ─────────────────────────────────────────────────── */

function SeverityBadge({ confidence, t }: { confidence: number; t: (key: any) => string }) {
  const pct = confidence * 100
  if (pct >= 90) {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide bg-red-500/15 text-red-400 border border-red-500/25 animate-pulse">
        {t('severity.critical')}
      </span>
    )
  }
  if (pct >= 75) {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide bg-amber-500/15 text-amber-400 border border-amber-500/25">
        {t('severity.high')}
      </span>
    )
  }
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide bg-sky-500/15 text-sky-400 border border-sky-500/25">
      {t('severity.medium')}
    </span>
  )
}

/* ── Empty / Loading states ─────────────────────────────────────────── */

function EmptyFlows({ t, isDark }: { t: (key: any) => string; isDark: boolean }) {
  return (
    <div className={`flex flex-col items-center justify-center py-14 ${isDark ? 'text-slate-600' : 'text-slate-400'} select-none`}>
      <div className="text-4xl mb-3 opacity-40 font-mono leading-none">
        {'  .-~~~-.'}
        <br />
        {".'       '."}
        <br />
        {'|  0   0  |'}
        <br />
        {"'._  ^  _.'"}
        <br />
        {"   '---'"}
      </div>
      <p className={`text-sm font-medium ${isDark ? 'text-slate-500' : 'text-slate-500'} mt-2`}>{t('monitor.no_flow_data')}</p>
      <p className={`text-xs ${isDark ? 'text-slate-600' : 'text-slate-400'} mt-1`}>{t('monitor.start_hint')}</p>
    </div>
  )
}


function EmptyChart({ message, isDark }: { message: string; isDark: boolean }) {
  return (
    <div className={`h-[220px] flex flex-col items-center justify-center ${isDark ? 'text-slate-600 border-white/[0.06]' : 'text-slate-400 border-slate-200'} border border-dashed rounded-md`}>
      <div className="text-2xl mb-2 opacity-30 font-mono">{'{ }'}</div>
      <p className="text-xs">{message}</p>
    </div>
  )
}

function SecureState({ t, isDark }: { t: (key: any) => string; isDark: boolean }) {
  return (
    <div className={`h-[200px] flex flex-col items-center justify-center border border-dashed border-emerald-500/15 rounded-md select-none`}>
      <Shield className="w-8 h-8 text-emerald-500/40 mb-2" />
      <p className="text-sm font-semibold text-emerald-500">{t('monitor.system_secure')}</p>
      <p className={`text-[11px] ${isDark ? 'text-slate-600' : 'text-slate-400'} mt-0.5`}>{t('monitor.no_threats')}</p>
    </div>
  )
}

/* ── Skeleton loader ────────────────────────────────────────────────── */

function Skeleton({ className = '' }: { className?: string }) {
  return <div className={`animate-pulse rounded bg-slate-700/30 ${className}`} />
}

/* ── Main component ─────────────────────────────────────────────────── */

export default function Monitoring() {
  const t = useT()
  const { theme } = useSettings()
  const isDark = theme === 'dark'

  const { flows: wsFlows, active, connected } = useMonitorWs()
  const [stats, setStats] = useState<Stats | null>(null)
  const [history, setHistory] = useState<FlowEntry[]>([])
  const prevAnomalyCount = useRef(0)

  // Load from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem('detection_history')
      if (saved) setHistory(JSON.parse(saved))
    } catch {}
  }, [])

  // Save to localStorage when history changes (debounced)
  useEffect(() => {
    const timeout = setTimeout(() => {
      try {
        localStorage.setItem('detection_history', JSON.stringify(history.slice(-500)))
      } catch {}
    }, 1000)
    return () => clearTimeout(timeout)
  }, [history])

  // Threat notification sound
  const playAlertSound = useCallback(() => {
    try {
      const ctx = new AudioContext()
      const osc = ctx.createOscillator()
      const gain = ctx.createGain()
      osc.connect(gain)
      gain.connect(ctx.destination)
      osc.frequency.value = 800
      gain.gain.value = 0.1
      osc.start()
      osc.stop(ctx.currentTime + 0.15)
    } catch {}
  }, [])

  // Play alert when anomaly count increases
  useEffect(() => {
    const currentAnomalyCount = history.filter(f => f.is_anomaly).length
    if (currentAnomalyCount > prevAnomalyCount.current && prevAnomalyCount.current > 0) {
      playAlertSound()
    }
    prevAnomalyCount.current = currentAnomalyCount
  }, [history, playAlertSound])

  // Poll stats every 2s
  useEffect(() => {
    const poll = () => {
      getStats().then(setStats).catch(() => {})
      getHistory(100).then(setHistory).catch(() => {})
    }
    poll()
    const id = setInterval(poll, 2000)
    return () => clearInterval(id)
  }, [])

  // Merge WS flows into local history
  useEffect(() => {
    if (wsFlows.length > 0) {
      setHistory((prev) => [...prev, ...wsFlows].slice(-500))
    }
  }, [wsFlows])

  const handleBlock = useCallback((ip: string) => {
    blockIp(ip).catch(() => {})
  }, [])

  const handleUnblock = useCallback((ip: string) => {
    unblockIp(ip).catch(() => {})
  }, [])

  const handleClear = useCallback(() => {
    clearHistory().then(() => {
      setHistory([])
      prevAnomalyCount.current = 0
      localStorage.removeItem('detection_history')
      getStats().then(setStats)
    })
  }, [])

  // CSV Export
  const exportCsv = useCallback(() => {
    if (history.length === 0) return
    const headers = ['timestamp','src_ip','dst_ip','dst_port','protocol','prediction','confidence','is_anomaly']
    const rows = history.map(f => headers.map(h => String((f as any)[h] ?? '')).join(','))
    const csv = [headers.join(','), ...rows].join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `detection_report_${new Date().toISOString().slice(0,10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }, [history])

  // Timeline data: group by second
  const timelineData = (() => {
    const buckets = new Map<string, { time: string; benign: number; threats: number }>()
    history.slice(-200).forEach((f) => {
      const sec = f.timestamp.slice(11, 19)
      if (!buckets.has(sec)) buckets.set(sec, { time: sec, benign: 0, threats: 0 })
      const b = buckets.get(sec)!
      if (f.is_anomaly) b.threats++
      else b.benign++
    })
    return Array.from(buckets.values()).slice(-30)
  })()

  // Pie data
  const pieData = stats
    ? Object.entries(stats.distribution).map(([name, value]) => ({ name, value }))
    : []

  // Recent alerts
  const recentAlerts = history
    .filter((f) => f.is_anomaly)
    .slice(-10)
    .reverse()

  // System health score (inverse of threat_pct, clamped)
  const healthPct = Math.max(0, Math.min(100, 100 - (stats?.threat_pct ?? 0)))

  return (
    <div className="space-y-6">
      {/* ── WebSocket reconnection banner ─────────────────────────── */}
      {!connected && (
        <div className="flex items-center gap-2 px-4 py-2 bg-amber-500/10 border border-amber-500/20 rounded-lg text-sm text-amber-400">
          <WifiOff className="w-4 h-4" />
          {t('monitor.reconnecting')}
        </div>
      )}

      {/* ── Machine Identity Banner ───────────────────────────────── */}
      <div className={`rounded-xl p-4 flex items-center gap-4 border-2 ${
        isDark
          ? 'bg-gradient-to-r from-amber-500/5 to-transparent border-amber-500/30'
          : 'bg-gradient-to-r from-amber-50 to-white border-amber-300'
      }`}>
        <div className={`w-14 h-14 rounded-xl flex items-center justify-center ${
          isDark ? 'bg-amber-500/15' : 'bg-amber-100'
        }`}>
          <Shield className="w-7 h-7 text-amber-500" />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-3 flex-wrap">
            <span className={`text-lg font-bold ${isDark ? 'text-slate-100' : 'text-slate-900'}`}>
              {t('machine.ids_role')}
            </span>
            <span className={`text-xs px-2 py-0.5 rounded-full font-semibold bg-amber-500/20 text-amber-600 border border-amber-500/30`}>
              {t('machine.ids_label')}
            </span>
          </div>
          <div className={`flex items-center gap-4 mt-1 text-sm font-mono ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
            <span>{t('machine.ip')}: <span className={isDark ? 'text-amber-400' : 'text-amber-600'}>{t('machine.ids_ip')}</span></span>
            <span>{t('machine.os')}: <span className={isDark ? 'text-slate-300' : 'text-slate-700'}>{t('machine.ids_os')}</span></span>
          </div>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className={isDark ? 'text-emerald-400' : 'text-emerald-600'}>MONITORING</span>
        </div>
      </div>

      {/* ── Page Header with breadcrumb ───────────────────────────── */}
      <div className="flex items-center justify-between">
        <div className="flex flex-col gap-1">
          <div className={`flex items-center gap-2 text-[11px] ${isDark ? 'text-slate-600' : 'text-slate-400'} font-mono`}>
            <Monitor className="w-3 h-3" />
            <span>{t('monitor.breadcrumb')}</span>
            <ChevronRight className="w-3 h-3" />
            <span className="text-amber-500/70">{t('sidebar.monitoring')}</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20">
              <Activity className="w-5 h-5 text-amber-500" />
            </div>
            <div>
              <h1 className={`text-xl font-bold ${isDark ? 'text-slate-200' : 'text-slate-900'} tracking-tight`}>{t('monitor.title')}</h1>
              <p className={`text-xs ${isDark ? 'text-slate-500' : 'text-slate-500'} mt-0.5`}>{t('monitor.subtitle')}</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          {/* Connection indicator */}
          <span className={`flex items-center gap-2 text-xs font-mono px-3 py-1.5 rounded-lg border transition-all duration-300 ${
            connected
              ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20 shadow-sm shadow-emerald-500/5'
              : 'text-red-400 bg-red-500/10 border-red-500/20 shadow-sm shadow-red-500/5'
          }`}>
            {connected ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
            {connected ? t('common.connected') : t('common.disconnected')}
          </span>
          {active && (
            <span className="flex items-center gap-2 text-xs font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1.5 rounded-lg shadow-sm shadow-emerald-500/5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse-glow" />
              {t('common.live')}
            </span>
          )}
          <button
            onClick={exportCsv}
            className={`flex items-center gap-1.5 text-xs ${isDark ? 'text-slate-400 bg-white/[0.03] border-white/5' : 'text-slate-500 bg-slate-100 border-slate-200'} hover:text-amber-400 hover:bg-amber-500/10 border hover:border-amber-500/20 px-3 py-1.5 rounded-lg transition-all duration-200`}
          >
            <Download className="w-3 h-3" /> {t('monitor.export_csv')}
          </button>
          <button
            onClick={handleClear}
            className={`flex items-center gap-1.5 text-xs ${isDark ? 'text-slate-400 bg-white/[0.03] border-white/5' : 'text-slate-500 bg-slate-100 border-slate-200'} hover:text-red-400 hover:bg-red-500/10 border hover:border-red-500/20 px-3 py-1.5 rounded-lg transition-all duration-200`}
          >
            <Trash2 className="w-3 h-3" /> {t('common.clear')}
          </button>
        </div>
      </div>

      {/* ── Metric cards ──────────────────────────────────────────── */}
      <div className="grid grid-cols-4 gap-4">
        <MetricCard
          icon={<BarChart3 className="w-5 h-5 text-amber-500" />}
          label={t('monitor.total_flows')}
          value={stats ? stats.total_flows.toLocaleString() : undefined}
          accent="amber"
          isDark={isDark}
          loading={!stats}
        />
        <MetricCard
          icon={<ShieldAlert className="w-5 h-5 text-red-500" />}
          label={t('monitor.threats_detected')}
          value={stats ? stats.anomalies.toString() : undefined}
          sub={stats ? `${stats.threat_pct}%` : undefined}
          accent="red"
          danger
          isDark={isDark}
          loading={!stats}
        />
        <MetricCard
          icon={<Activity className="w-5 h-5 text-cyan-400" />}
          label={t('monitor.avg_confidence')}
          value={stats ? `${stats.avg_confidence}%` : undefined}
          accent="cyan"
          isDark={isDark}
          loading={!stats}
        />
        <MetricCard
          icon={<Ban className="w-5 h-5 text-orange-400" />}
          label={t('monitor.blocked_ips')}
          value={stats ? stats.blocked_count.toString() : undefined}
          accent="orange"
          isDark={isDark}
          loading={!stats}
        />
      </div>

      {/* ── Network stats bar ─────────────────────────────────────── */}
      {stats && (
        <div className={`flex items-center gap-6 px-5 py-3.5 ${isDark ? 'bg-[#131d2e] border-amber-500/10' : 'bg-slate-50 border-slate-200'} border border-l-[3px] border-l-amber-500 rounded-lg text-xs transition-all duration-500`}>
          <span className={isDark ? 'text-slate-500' : 'text-slate-600'}>
            <strong className="text-amber-500">{stats.unique_src}</strong> {t('monitor.source_ips')}
          </span>
          <span className={`w-px h-4 ${isDark ? 'bg-white/[0.06]' : 'bg-slate-200'}`} />
          <span className={isDark ? 'text-slate-500' : 'text-slate-600'}>
            <strong className="text-amber-500">{stats.unique_dst}</strong> {t('monitor.dest_ips')}
          </span>
          <span className={`w-px h-4 ${isDark ? 'bg-white/[0.06]' : 'bg-slate-200'}`} />
          <span className={isDark ? 'text-slate-500' : 'text-slate-600'}>
            {t('monitor.top_port')}: <strong className="text-amber-500">{stats.top_port}</strong>
          </span>
          <span className={`w-px h-4 ${isDark ? 'bg-white/[0.06]' : 'bg-slate-200'}`} />
          <span className={isDark ? 'text-slate-500' : 'text-slate-600'}>
            {t('monitor.avg_throughput')}: <strong className="text-amber-500">{stats.avg_throughput.toLocaleString()} B/s</strong>
          </span>
        </div>
      )}

      {/* ── System Health + Threat Level ───────────────────────────── */}
      <div className="grid grid-cols-3 gap-4">
        <div className={`${isDark ? 'bg-[#0c1222] border-amber-500/10' : 'bg-white border-slate-200'} border rounded-lg p-5`}>
          <div className="flex items-center gap-2 mb-4">
            <Shield className="w-4 h-4 text-emerald-500" />
            <h3 className={`text-sm font-semibold ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>{t('monitor.system_health')}</h3>
          </div>
          <SystemHealthGauge pct={healthPct} t={t} isDark={isDark} />
        </div>
        <div className={`${isDark ? 'bg-[#0c1222] border-amber-500/10' : 'bg-white border-slate-200'} border rounded-lg p-5`}>
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="w-4 h-4 text-amber-500" />
            <h3 className={`text-sm font-semibold ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>{t('monitor.threat_level')}</h3>
          </div>
          <ThreatGauge pct={stats?.threat_pct ?? 0} t={t} isDark={isDark} />
        </div>
        <div className={`${isDark ? 'bg-[#0c1222] border-amber-500/10' : 'bg-white border-slate-200'} border rounded-lg p-5`}>
          <div className="flex items-center gap-2 mb-4">
            <Radio className="w-4 h-4 text-cyan-400" />
            <h3 className={`text-sm font-semibold ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>{t('monitor.quick_stats')}</h3>
          </div>
          <div className="space-y-3 mt-2">
            <QuickStat label={t('monitor.flows_per_min')} value={stats ? Math.round(stats.total_flows / Math.max(1, history.length) * 60).toString() : '--'} color="text-amber-500" isDark={isDark} />
            <QuickStat label={t('monitor.anomaly_ratio')} value={`${stats?.threat_pct ?? 0}%`} color={stats && stats.threat_pct > 30 ? 'text-red-400' : stats && stats.threat_pct > 10 ? 'text-amber-400' : 'text-emerald-400'} isDark={isDark} />
            <QuickStat label={t('monitor.unique_protocols')} value={pieData.length.toString()} color="text-cyan-400" isDark={isDark} />
            <QuickStat label={t('monitor.blocked')} value={`${stats?.blocked_count ?? 0} ${t('common.ips')}`} color="text-orange-400" isDark={isDark} />
          </div>
        </div>
      </div>

      {/* ── Recent flows table ────────────────────────────────────── */}
      <div className={`${isDark ? 'bg-[#0c1222] border-amber-500/10' : 'bg-white border-slate-200'} border rounded-lg overflow-hidden transition-all duration-300`}>
        <div className={`px-5 py-3.5 border-b ${isDark ? 'border-amber-500/10 bg-[#0c1222]' : 'border-slate-200 bg-white'} flex items-center justify-between`}>
          <div className="flex items-center gap-2">
            <Activity className="w-3.5 h-3.5 text-amber-500/60" />
            <span className={`text-sm font-semibold ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>{t('monitor.recent_flows')}</span>
          </div>
          <span className={`text-[11px] ${isDark ? 'text-slate-600 bg-white/[0.03]' : 'text-slate-500 bg-slate-100'} font-mono px-2 py-0.5 rounded`}>{history.length} {t('common.entries')}</span>
        </div>
        <div className="overflow-x-auto max-h-[340px] overflow-y-auto">
          {history.length === 0 ? (
            <EmptyFlows t={t} isDark={isDark} />
          ) : (
            <table className="w-full text-xs font-mono">
              <thead className={`sticky top-0 ${isDark ? 'bg-[#0a0f1a]' : 'bg-slate-50'} z-10`}>
                <tr className={`${isDark ? 'text-slate-500 border-white/[0.06]' : 'text-slate-500 border-slate-200'} border-b`}>
                  <th className="px-5 py-2.5 text-left font-medium">{t('table.time')}</th>
                  <th className="px-5 py-2.5 text-left font-medium">{t('table.src_ip')}</th>
                  <th className="px-5 py-2.5 text-left font-medium">{t('table.dst_ip')}</th>
                  <th className="px-5 py-2.5 text-left font-medium">{t('table.port')}</th>
                  <th className="px-5 py-2.5 text-left font-medium">{t('table.protocol')}</th>
                  <th className="px-5 py-2.5 text-left font-medium">{t('table.prediction')}</th>
                  <th className="px-5 py-2.5 text-left font-medium">{t('table.confidence')}</th>
                  <th className="px-5 py-2.5 text-left font-medium">{t('table.action')}</th>
                </tr>
              </thead>
              <tbody>
                {history.slice(-20).reverse().map((f, i) => (
                  <tr
                    key={i}
                    className={`border-b ${isDark ? 'border-white/[0.03]' : 'border-slate-100'} transition-colors duration-200 ${
                      f.is_anomaly
                        ? 'bg-red-500/[0.05] hover:bg-red-500/[0.1]'
                        : isDark
                          ? i % 2 === 0
                            ? 'bg-transparent hover:bg-white/[0.02]'
                            : 'bg-white/[0.015] hover:bg-white/[0.035]'
                          : i % 2 === 0
                            ? 'bg-transparent hover:bg-slate-50'
                            : 'bg-slate-50/50 hover:bg-slate-100/50'
                    }`}
                  >
                    <td className={`px-5 py-2 ${isDark ? 'text-slate-500' : 'text-slate-500'}`}>{f.timestamp.slice(11, 19)}</td>
                    <td className={`px-5 py-2 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>{f.src_ip}</td>
                    <td className={`px-5 py-2 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>{f.dst_ip}</td>
                    <td className={`px-5 py-2 ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>{f.dst_port}</td>
                    <td className="px-5 py-2">
                      <span className={`px-1.5 py-0.5 rounded ${isDark ? 'bg-white/[0.04] text-slate-400' : 'bg-slate-100 text-slate-600'}`}>{f.protocol}</span>
                    </td>
                    <td className={`px-5 py-2 font-semibold ${
                      f.is_anomaly ? 'text-red-400' : 'text-emerald-400'
                    }`}>{f.prediction}</td>
                    <td className="px-5 py-2">
                      <span className="text-amber-500 font-semibold">{(f.confidence * 100).toFixed(1)}%</span>
                    </td>
                    <td className="px-5 py-2">
                      {f.is_anomaly && f.src_ip !== 'N/A' && (
                        <button
                          onClick={() => handleBlock(f.src_ip)}
                          className="text-red-400/60 hover:text-red-400 hover:scale-110 transition-all duration-150"
                          title={`${t('common.block')} ${f.src_ip}`}
                        >
                          <ShieldX className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* ── Charts row ────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 gap-4">
        {/* Traffic Timeline */}
        <div className={`${isDark ? 'bg-[#0c1222] border-amber-500/10' : 'bg-white border-slate-200'} border rounded-lg p-5 transition-all duration-300`}>
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="w-4 h-4 text-amber-500/60" />
            <h3 className={`text-sm font-semibold ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>{t('monitor.traffic_timeline')}</h3>
          </div>
          {timelineData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={timelineData}>
                <defs>
                  <linearGradient id="gradBenign" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#22c55e" stopOpacity={0.25} />
                    <stop offset="100%" stopColor="#22c55e" stopOpacity={0.02} />
                  </linearGradient>
                  <linearGradient id="gradThreats" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#ef4444" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#ef4444" stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" tick={{ fill: isDark ? '#475569' : '#64748b', fontSize: 10 }} axisLine={{ stroke: isDark ? '#1e293b' : '#e2e8f0' }} tickLine={false} />
                <YAxis tick={{ fill: isDark ? '#475569' : '#64748b', fontSize: 10 }} axisLine={{ stroke: isDark ? '#1e293b' : '#e2e8f0' }} tickLine={false} />
                <Tooltip content={<ChartTooltip isDark={isDark} />} />
                <Area
                  type="monotone" dataKey="benign" stackId="1"
                  stroke="#22c55e" fill="url(#gradBenign)" strokeWidth={2}
                  animationDuration={600}
                />
                <Area
                  type="monotone" dataKey="threats" stackId="1"
                  stroke="#ef4444" fill="url(#gradThreats)" strokeWidth={2}
                  animationDuration={600}
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <EmptyChart message={t('monitor.waiting_data')} isDark={isDark} />
          )}
        </div>

        {/* Threat Distribution */}
        <div className={`${isDark ? 'bg-[#0c1222] border-amber-500/10' : 'bg-white border-slate-200'} border rounded-lg p-5 transition-all duration-300`}>
          <div className="flex items-center gap-2 mb-4">
            <ShieldAlert className="w-4 h-4 text-red-500/60" />
            <h3 className={`text-sm font-semibold ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>{t('monitor.threat_distribution')}</h3>
          </div>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%" cy="50%"
                  innerRadius={45} outerRadius={85}
                  dataKey="value" paddingAngle={3}
                  animationDuration={600}
                  label={renderPieLabel}
                  labelLine={false}
                >
                  {pieData.map((_, i) => (
                    <Cell key={i} fill={COLORS_PIE[i % COLORS_PIE.length]} stroke="transparent" />
                  ))}
                  <Label
                    value={`${pieData.reduce((s, d) => s + d.value, 0)}`}
                    position="center"
                    fill="#f59e0b"
                    fontSize={20}
                    fontWeight="bold"
                    fontFamily="JetBrains Mono, monospace"
                  />
                </Pie>
                <Tooltip content={<PieTooltip isDark={isDark} t={t} />} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <EmptyChart message={t('monitor.no_threat_data')} isDark={isDark} />
          )}
        </div>
      </div>

      {/* ── Recent alerts ─────────────────────────────────────────── */}
      <div className={`${isDark ? 'bg-[#0c1222] border-amber-500/10' : 'bg-white border-slate-200'} border rounded-lg p-5 transition-all duration-300`}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-red-500/60" />
            <h3 className={`text-sm font-semibold ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>{t('monitor.recent_threats')}</h3>
          </div>
          {recentAlerts.length > 0 && (
            <span className={`text-[11px] font-mono bg-red-500/10 px-2 py-0.5 rounded text-red-400/70`}>
              {recentAlerts.length} {t('monitor.alerts')}
            </span>
          )}
        </div>
        {recentAlerts.length > 0 ? (
          <div className="space-y-2 max-h-[260px] overflow-y-auto pr-1">
            {recentAlerts.map((a, i) => {
              const conf = a.confidence * 100
              const borderColor = conf >= 90 ? 'border-l-red-500' : conf >= 75 ? 'border-l-amber-500' : 'border-l-sky-500'
              const bgColor = conf >= 90 ? 'bg-red-500/[0.06]' : conf >= 75 ? 'bg-amber-500/[0.04]' : 'bg-sky-500/[0.04]'
              return (
                <div
                  key={i}
                  className={`flex items-center justify-between px-4 py-2.5 border-l-[3px] ${borderColor} ${bgColor} rounded-md text-xs transition-all duration-300 hover:translate-x-0.5`}
                >
                  <div className="flex items-center gap-3">
                    <SeverityBadge confidence={a.confidence} t={t} />
                    <div>
                      <span className={`font-semibold ${isDark ? 'text-slate-200' : 'text-slate-800'}`}>{a.prediction}</span>
                      <span className={`${isDark ? 'text-slate-500' : 'text-slate-500'} font-mono ml-2`}>{a.src_ip} &rarr; {a.dst_ip}:{a.dst_port}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-amber-500 font-mono font-bold">{conf.toFixed(1)}%</span>
                    <span className={`${isDark ? 'text-slate-600' : 'text-slate-400'} font-mono`}>{a.timestamp.slice(11, 19)}</span>
                  </div>
                </div>
              )
            })}
          </div>
        ) : (
          <SecureState t={t} isDark={isDark} />
        )}
      </div>

      {/* ── Blocked IPs ───────────────────────────────────────────── */}
      {stats && stats.blocked_ips.length > 0 && (
        <div className={`${isDark ? 'bg-[#0c1222] border-amber-500/10' : 'bg-white border-slate-200'} border rounded-lg p-5 transition-all duration-300`}>
          <div className="flex items-center gap-2 mb-4">
            <Ban className="w-4 h-4 text-red-500/60" />
            <h3 className={`text-sm font-semibold ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
              {t('monitor.blocked_ips')} ({stats.blocked_ips.length})
            </h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {stats.blocked_ips.map((ip) => (
              <span
                key={ip}
                className="group flex items-center gap-2 px-3 py-1.5 bg-red-500/10 border border-red-500/20 rounded-lg text-xs font-mono text-red-400 transition-all duration-200 hover:bg-red-500/15 hover:border-red-500/30"
              >
                {ip}
                <button
                  onClick={() => handleUnblock(ip)}
                  className="opacity-50 group-hover:opacity-100 hover:text-red-300 transition-all duration-150"
                >
                  &times;
                </button>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}


// ── Sub-components ──────────────────────────────────────────────────────

function MetricCard({ icon, label, value, sub, danger, accent = 'amber', isDark, loading }: {
  icon: React.ReactNode
  label: string
  value?: string
  sub?: string
  danger?: boolean
  accent?: 'amber' | 'red' | 'cyan' | 'orange'
  isDark: boolean
  loading?: boolean
}) {
  const accentMap: Record<string, string> = {
    amber: 'border-l-amber-500 hover:shadow-amber-500/5',
    red: 'border-l-red-500 hover:shadow-red-500/5',
    cyan: 'border-l-cyan-400 hover:shadow-cyan-400/5',
    orange: 'border-l-orange-400 hover:shadow-orange-400/5',
  }
  return (
    <div className={`group flex items-center gap-4 px-5 py-5 ${isDark ? 'bg-[#131d2e] border-amber-500/10 hover:border-amber-500/20 hover:bg-[#162035]' : 'bg-slate-50 border-slate-200 hover:border-slate-300 hover:bg-slate-100'} border border-l-[3px] ${accentMap[accent]} rounded-lg transition-all duration-300 hover:shadow-lg hover:-translate-y-0.5 cursor-default`}>
      <div className={`p-2.5 rounded-lg ${isDark ? 'bg-white/[0.03] group-hover:bg-white/[0.06]' : 'bg-white group-hover:bg-white'} transition-all duration-300 group-hover:scale-110`}>
        {icon}
      </div>
      <div className="transition-all duration-300">
        <div className={`text-[11px] ${isDark ? 'text-slate-500' : 'text-slate-500'} uppercase tracking-wider font-medium`}>{label}</div>
        {loading ? (
          <Skeleton className="h-7 w-20 mt-1" />
        ) : (
          <div className={`text-2xl font-bold font-mono mt-0.5 transition-colors duration-300 ${danger ? 'text-red-400' : 'text-amber-500'}`}>{value}</div>
        )}
        {loading ? (
          sub !== undefined ? <Skeleton className="h-3 w-12 mt-1.5" /> : null
        ) : (
          sub && <div className={`text-xs ${isDark ? 'text-slate-500' : 'text-slate-500'} mt-0.5`}>{sub}</div>
        )}
      </div>
    </div>
  )
}

function QuickStat({ label, value, color, isDark }: { label: string; value: string; color: string; isDark: boolean }) {
  return (
    <div className={`flex items-center justify-between px-3 py-2 rounded-md ${isDark ? 'bg-white/[0.02] border-white/[0.04]' : 'bg-slate-50 border-slate-200'} border`}>
      <span className={`text-[11px] ${isDark ? 'text-slate-500' : 'text-slate-500'}`}>{label}</span>
      <span className={`text-sm font-bold font-mono ${color}`}>{value}</span>
    </div>
  )
}

function SystemHealthGauge({ pct, t, isDark }: { pct: number; t: (key: any) => string; isDark: boolean }) {
  const color = pct >= 80 ? '#22c55e' : pct >= 50 ? '#f59e0b' : '#ef4444'
  const label = pct >= 80 ? t('monitor.healthy') : pct >= 50 ? t('monitor.degraded') : t('monitor.critical')
  const clamp = Math.min(Math.max(pct, 0), 100)

  // Full circle gauge
  const radius = 55
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (clamp / 100) * circumference

  return (
    <div className="flex flex-col items-center">
      <svg width="150" height="150" viewBox="0 0 150 150">
        {/* Background circle */}
        <circle cx="75" cy="75" r={radius} fill="none" stroke={isDark ? '#1e293b' : '#e2e8f0'} strokeWidth="10" />
        {/* Progress circle */}
        <circle
          cx="75" cy="75" r={radius} fill="none"
          stroke={color} strokeWidth="10" strokeLinecap="round"
          strokeDasharray={circumference} strokeDashoffset={offset}
          transform="rotate(-90 75 75)"
          style={{
            transition: 'stroke-dashoffset 1s ease-in-out, stroke 0.5s ease',
            filter: `drop-shadow(0 0 8px ${color}40)`,
          }}
        />
        {/* Value */}
        <text x="75" y="70" textAnchor="middle" fill={color} fontSize="26" fontWeight="bold" fontFamily="JetBrains Mono, monospace">
          {clamp.toFixed(0)}%
        </text>
        {/* Label */}
        <text x="75" y="90" textAnchor="middle" fill={isDark ? '#64748b' : '#94a3b8'} fontSize="11" fontFamily="Inter, sans-serif">
          {label}
        </text>
      </svg>
    </div>
  )
}

function ThreatGauge({ pct, t, isDark }: { pct: number; t: (key: any) => string; isDark: boolean }) {
  const color = pct > 30 ? '#ef4444' : pct > 10 ? '#f59e0b' : '#22c55e'
  const label = pct > 30 ? t('monitor.high_level') : pct > 10 ? t('monitor.moderate_level') : t('monitor.low_level')
  const clamp = Math.min(Math.max(pct, 0), 100)
  const angle = (clamp / 100) * 180 - 90
  const rad = (angle * Math.PI) / 180
  const r = 55
  const cx = 75, cy = 75
  const x = cx + r * Math.cos(rad)
  const y = cy + r * Math.sin(rad)

  return (
    <div className="flex flex-col items-center">
      <svg width="150" height="100" viewBox="0 0 150 100">
        {/* Background arc */}
        <path
          d="M 20 75 A 55 55 0 0 1 130 75"
          fill="none" stroke={isDark ? '#1e293b' : '#e2e8f0'} strokeWidth="10" strokeLinecap="round"
        />
        {/* Colored arc */}
        <path
          d={`M 20 75 A 55 55 0 ${clamp > 50 ? 1 : 0} 1 ${x} ${y}`}
          fill="none" stroke={color} strokeWidth="10" strokeLinecap="round"
          style={{
            transition: 'all 1s ease-in-out',
            filter: `drop-shadow(0 0 6px ${color}40)`,
          }}
        />
        {/* Value text */}
        <text x="75" y="70" textAnchor="middle" fill={color} fontSize="22" fontWeight="bold" fontFamily="JetBrains Mono, monospace">
          {pct.toFixed(1)}%
        </text>
        <text x="75" y="90" textAnchor="middle" fill={isDark ? '#64748b' : '#94a3b8'} fontSize="10" fontFamily="Inter, sans-serif" letterSpacing="1">
          {label}
        </text>
      </svg>
    </div>
  )
}
