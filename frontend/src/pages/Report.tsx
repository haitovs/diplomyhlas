import { useEffect, useState, useCallback } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, AreaChart, Area,
} from 'recharts'
import {
  FileBarChart, ShieldAlert, AlertTriangle, Target, Download, Trash2,
  ChevronRight, Shield, Crosshair, Clock, Activity,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import {
  getHistory, getStats, clearHistory,
  type FlowEntry, type Stats,
} from '../services/api'
import { useT, useSettings } from '../i18n'

const SEVERITY_COLORS = { Critical: '#ef4444', High: '#f59e0b', Medium: '#38bdf8' }
const PIE_COLORS = ['#ef4444', '#f59e0b', '#38bdf8']

function getSeverity(confidence: number): 'Critical' | 'High' | 'Medium' {
  if (confidence >= 0.95) return 'Critical'
  if (confidence >= 0.85) return 'High'
  return 'Medium'
}

function getAutoResponse(prediction: string, srcIp: string, port: number): string {
  const lower = prediction.toLowerCase()
  if (lower.includes('ddos')) return `Apply rate limiting. Review traffic from ${srcIp} at gateway.`
  if (lower.includes('ssh') || lower.includes('ftp') || lower.includes('patator'))
    return `Account lockout triggered. Block ${srcIp} and enforce MFA on port ${port}.`
  if (lower.includes('port') || lower.includes('scan'))
    return `Reconnaissance detected. Add ${srcIp} to watchlist.`
  if (lower.includes('bot'))
    return `Bot activity from ${srcIp}. Isolate host, scan for malware.`
  return 'Logged for analyst review. Monitor for recurring patterns.'
}

/* ── Tooltip components ─────────────────────────────────────────────── */

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

function PieTooltip({ active, payload, isDark }: any) {
  if (!active || !payload?.length) return null
  const d = payload[0]
  return (
    <div className={`${isDark ? 'bg-[#0c1222] border-amber-500/20' : 'bg-white border-slate-200'} border rounded-lg px-4 py-3 shadow-xl ${isDark ? 'shadow-black/40' : 'shadow-slate-200/60'} backdrop-blur-sm`}>
      <p className={`text-xs font-semibold ${isDark ? 'text-slate-200' : 'text-slate-800'}`}>{d.name}</p>
      <p className="text-xs font-mono text-amber-500 mt-0.5">{d.value}</p>
    </div>
  )
}

/* ── Severity badge ─────────────────────────────────────────────────── */

function SeverityBadge({ confidence, t }: { confidence: number; t: (key: any) => string }) {
  const sev = getSeverity(confidence)
  if (sev === 'Critical') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide bg-red-500/15 text-red-400 border border-red-500/25 animate-pulse">
        {t('severity.critical')}
      </span>
    )
  }
  if (sev === 'High') {
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

/* ── Main component ─────────────────────────────────────────────────── */

export default function Report() {
  const t = useT()
  const { theme } = useSettings()
  const isDark = theme === 'dark'

  const [history, setHistory] = useState<FlowEntry[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [selectedEvent, setSelectedEvent] = useState<FlowEntry | null>(null)

  const poll = useCallback(() => {
    getHistory(1000).then(setHistory).catch(() => {})
    getStats().then(setStats).catch(() => {})
  }, [])

  useEffect(() => {
    poll()
    const id = setInterval(poll, 3000)
    return () => clearInterval(id)
  }, [poll])

  const threats = history.filter(f => f.is_anomaly)
  const criticalCount = threats.filter(f => f.confidence >= 0.95).length
  const threatPct = stats ? stats.threat_pct : 0

  // Attack vector data from stats distribution
  const vectorData = stats
    ? Object.entries(stats.distribution)
        .filter(([k]) => k.toLowerCase() !== 'benign')
        .map(([name, value]) => ({ name, value }))
        .sort((a, b) => b.value - a.value)
    : []

  // Severity breakdown from threats
  const sevCounts = { Critical: 0, High: 0, Medium: 0 }
  threats.forEach(f => { sevCounts[getSeverity(f.confidence)]++ })
  const severityData = Object.entries(sevCounts)
    .filter(([, v]) => v > 0)
    .map(([name, value]) => ({ name, value }))

  // Temporal data: group threats by minute
  const temporalMap = new Map<string, number>()
  threats.forEach(f => {
    const d = new Date(f.timestamp)
    const key = `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
    temporalMap.set(key, (temporalMap.get(key) || 0) + 1)
  })
  const temporalData = Array.from(temporalMap.entries())
    .map(([time, count]) => ({ time, count }))
    .sort((a, b) => a.time.localeCompare(b.time))

  // CSV export
  const exportCSV = () => {
    const header = 'id,timestamp,type,src_ip,dst_ip,port,severity,confidence,source'
    const rows = threats.map((f) => {
      const id = eventIdFor(f)
      const sev = getSeverity(f.confidence)
      // Escape commas in fields
      const safe = (v: any) => {
        const s = String(v ?? '')
        return s.includes(',') ? `"${s.replace(/"/g, '""')}"` : s
      }
      return [id, f.timestamp, f.prediction, f.src_ip, f.dst_ip, f.dst_port, sev, f.confidence.toFixed(4), f.source].map(safe).join(',')
    })
    const csv = [header, ...rows].join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `detection-report-${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleClear = () => {
    clearHistory().then(() => {
      setHistory([])
      setSelectedEvent(null)
    }).catch(() => {})
  }

  const cardClass = `rounded-xl border p-5 ${isDark ? 'bg-[#0a1020]/80 border-amber-500/10' : 'bg-white border-slate-200 shadow-sm'}`
  const headingClass = `text-[11px] uppercase tracking-widest font-semibold ${isDark ? 'text-slate-500' : 'text-slate-400'}`

  // Sorted threats (newest first) with stable ID based on timestamp+src
  const sortedThreats = [...threats].reverse()
  const eventIdFor = (f: FlowEntry) => {
    // Stable ID from timestamp hash — doesn't change on data refresh
    const ts = new Date(f.timestamp).getTime()
    const short = (ts % 100000).toString().padStart(5, '0')
    return `ATK-${short}`
  }

  return (
    <div className="space-y-6">

        {/* ── Header ──────────────────────────────────────────────── */}
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div>
            <div className={`flex items-center gap-2 text-[11px] font-mono ${isDark ? 'text-slate-600' : 'text-slate-400'} mb-2`}>
              <FileBarChart className="w-3 h-3" />
              {t('report.breadcrumb')}
              <ChevronRight className="w-3 h-3" />
              {t('report.title')}
            </div>
            <h1 className={`text-2xl font-bold tracking-tight ${isDark ? 'text-slate-100' : 'text-slate-800'}`}>
              {t('report.title')}
            </h1>
            <p className={`text-sm mt-1 ${isDark ? 'text-slate-500' : 'text-slate-500'}`}>
              {t('report.subtitle')}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={exportCSV}
              disabled={threats.length === 0}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
                threats.length > 0
                  ? 'bg-amber-500 text-white hover:bg-amber-600 shadow-lg shadow-amber-500/20'
                  : isDark ? 'bg-white/5 text-slate-600 cursor-not-allowed' : 'bg-slate-100 text-slate-400 cursor-not-allowed'
              }`}
            >
              <Download className="w-3.5 h-3.5" />
              {t('report.export_csv')}
            </button>
            <button
              onClick={handleClear}
              disabled={history.length === 0}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
                history.length > 0
                  ? isDark ? 'bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20' : 'bg-red-50 text-red-500 border border-red-200 hover:bg-red-100'
                  : isDark ? 'bg-white/5 text-slate-600 cursor-not-allowed' : 'bg-slate-100 text-slate-400 cursor-not-allowed'
              }`}
            >
              <Trash2 className="w-3.5 h-3.5" />
              {t('report.clear_data')}
            </button>
          </div>
        </div>

        {/* ── 4 Metric cards ──────────────────────────────────────── */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: 'report.session_flows' as const, value: stats?.total_flows ?? 0, icon: Activity, color: 'text-sky-400' },
            { label: 'report.session_threats' as const, value: stats?.anomalies ?? 0, icon: ShieldAlert, color: 'text-red-400' },
            { label: 'report.threat_rate' as const, value: `${threatPct.toFixed(1)}%`, icon: Target, color: 'text-amber-400' },
            { label: 'report.critical_count' as const, value: criticalCount, icon: AlertTriangle, color: 'text-red-500' },
          ].map(({ label, value, icon: Icon, color }) => (
            <div key={label} className={cardClass}>
              <div className="flex items-center justify-between mb-3">
                <span className={headingClass}>{t(label)}</span>
                <Icon className={`w-4 h-4 ${color}`} />
              </div>
              <div className={`text-2xl font-bold font-mono ${isDark ? 'text-slate-100' : 'text-slate-800'}`}>
                {value}
              </div>
            </div>
          ))}
        </div>

        {/* ── Empty state ─────────────────────────────────────────── */}
        {threats.length === 0 ? (
          <div className={`${cardClass} flex flex-col items-center justify-center py-20 text-center`}>
            <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-5 ${isDark ? 'bg-amber-500/10' : 'bg-amber-50'}`}>
              <Shield className={`w-8 h-8 ${isDark ? 'text-amber-500/60' : 'text-amber-400'}`} />
            </div>
            <h3 className={`text-lg font-semibold mb-2 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
              {t('report.no_threats_title')}
            </h3>
            <p className={`text-sm max-w-md mb-4 ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
              {t('report.no_threats_desc')}
            </p>
            <Link
              to="/attack"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold bg-amber-500 text-white hover:bg-amber-600 transition-colors"
            >
              <Crosshair className="w-3.5 h-3.5" />
              Attack Space
            </Link>
          </div>
        ) : (
          <>
            {/* ── Charts row ──────────────────────────────────────── */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {/* Attack Type Vectors */}
              <div className={cardClass}>
                <h3 className={`${headingClass} mb-4`}>{t('report.attack_vectors')}</h3>
                <div className="h-[260px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={vectorData} layout="vertical" margin={{ left: 10, right: 20, top: 5, bottom: 5 }}>
                      <XAxis type="number" tick={{ fontSize: 10, fill: isDark ? '#64748b' : '#94a3b8' }} />
                      <YAxis type="category" dataKey="name" width={100} tick={{ fontSize: 10, fill: isDark ? '#94a3b8' : '#64748b' }} />
                      <Tooltip content={<ChartTooltip isDark={isDark} />} />
                      <Bar dataKey="value" fill="#f59e0b" radius={[0, 4, 4, 0]} barSize={20} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Severity Breakdown */}
              <div className={cardClass}>
                <h3 className={`${headingClass} mb-4`}>{t('report.severity_breakdown')}</h3>
                <div className="h-[260px] flex items-center justify-center">
                  {severityData.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={severityData}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={100}
                          paddingAngle={3}
                          dataKey="value"
                          label={({ name, percent }: any) => (percent ?? 0) > 0.05 ? `${name} ${((percent ?? 0) * 100).toFixed(0)}%` : ''}
                          labelLine={false}
                        >
                          {severityData.map((entry, i) => (
                            <Cell
                              key={entry.name}
                              fill={SEVERITY_COLORS[entry.name as keyof typeof SEVERITY_COLORS] || PIE_COLORS[i % PIE_COLORS.length]}
                            />
                          ))}
                        </Pie>
                        <Tooltip content={<PieTooltip isDark={isDark} />} />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <p className={`text-sm ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>No data</p>
                  )}
                </div>
              </div>
            </div>

            {/* ── Temporal Distribution ────────────────────────────── */}
            <div className={cardClass}>
              <h3 className={`${headingClass} mb-4`}>{t('report.temporal')}</h3>
              <div className="h-[200px]">
                {temporalData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={temporalData} margin={{ left: 0, right: 20, top: 5, bottom: 5 }}>
                      <defs>
                        <linearGradient id="threatGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#f59e0b" stopOpacity={0.3} />
                          <stop offset="100%" stopColor="#f59e0b" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <XAxis dataKey="time" tick={{ fontSize: 10, fill: isDark ? '#64748b' : '#94a3b8' }} />
                      <YAxis tick={{ fontSize: 10, fill: isDark ? '#64748b' : '#94a3b8' }} />
                      <Tooltip content={<ChartTooltip isDark={isDark} />} />
                      <Area type="monotone" dataKey="count" stroke="#f59e0b" fill="url(#threatGrad)" strokeWidth={2} />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center">
                    <p className={`text-sm ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>No temporal data</p>
                  </div>
                )}
              </div>
            </div>

            {/* ── Security Event Log ──────────────────────────────── */}
            <div className={cardClass}>
              <h3 className={`${headingClass} mb-4`}>{t('report.event_log')}</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className={`border-b ${isDark ? 'border-white/[0.06]' : 'border-slate-200'}`}>
                      {[
                        'report.col_id' as const,
                        'report.col_time' as const,
                        'report.col_type' as const,
                        'report.col_src' as const,
                        'report.col_port' as const,
                        'report.col_severity' as const,
                        'report.col_confidence' as const,
                      ].map(k => (
                        <th key={k} className={`text-left py-2.5 px-3 font-semibold ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
                          {t(k)}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {sortedThreats.slice(0, 100).map((f, i) => {
                      const eventId = eventIdFor(f)
                      const isSelected = selectedEvent?.timestamp === f.timestamp && selectedEvent?.src_ip === f.src_ip
                      return (
                        <tr
                          key={i}
                          onClick={() => setSelectedEvent(f)}
                          className={`border-b cursor-pointer transition-colors ${
                            isSelected
                              ? isDark ? 'bg-amber-500/10 border-amber-500/20' : 'bg-amber-50 border-amber-200'
                              : isDark ? 'border-white/[0.04] hover:bg-white/[0.02]' : 'border-slate-100 hover:bg-slate-50'
                          }`}
                        >
                          <td className={`py-2.5 px-3 font-mono font-bold ${isDark ? 'text-amber-400' : 'text-amber-600'}`}>{eventId}</td>
                          <td className={`py-2.5 px-3 font-mono ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
                            {new Date(f.timestamp).toLocaleTimeString()}
                          </td>
                          <td className={`py-2.5 px-3 font-semibold ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>{f.prediction}</td>
                          <td className={`py-2.5 px-3 font-mono ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>{f.src_ip}</td>
                          <td className={`py-2.5 px-3 font-mono ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>{f.dst_port}</td>
                          <td className="py-2.5 px-3"><SeverityBadge confidence={f.confidence} t={t} /></td>
                          <td className={`py-2.5 px-3 font-mono ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                            {(f.confidence * 100).toFixed(1)}%
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* ── Forensic Workbench ──────────────────────────────── */}
            <div className={`${cardClass} border-l-4 ${isDark ? 'border-l-amber-500/40' : 'border-l-amber-400'}`}>
              <div className="flex items-center gap-2 mb-4">
                <Crosshair className={`w-4 h-4 ${isDark ? 'text-amber-400' : 'text-amber-500'}`} />
                <h3 className={headingClass}>{t('report.forensic')}</h3>
              </div>

              {selectedEvent ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    {/* Event ID */}
                    <div>
                      <span className={`text-[10px] uppercase tracking-wider font-semibold ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
                        {t('report.event_id')}
                      </span>
                      <p className={`text-sm font-mono font-bold mt-1 ${isDark ? 'text-amber-400' : 'text-amber-600'}`}>
                        {eventIdFor(selectedEvent)}
                      </p>
                    </div>
                    {/* Timestamp */}
                    <div>
                      <span className={`text-[10px] uppercase tracking-wider font-semibold ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
                        {t('report.col_time')}
                      </span>
                      <p className={`text-sm font-mono mt-1 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                        {new Date(selectedEvent.timestamp).toLocaleString()}
                      </p>
                    </div>
                    {/* Source Origin */}
                    <div>
                      <span className={`text-[10px] uppercase tracking-wider font-semibold ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
                        {t('report.source_origin')}
                      </span>
                      <p className={`text-sm font-mono mt-1 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                        {selectedEvent.src_ip}
                      </p>
                    </div>
                    {/* Target Vector */}
                    <div>
                      <span className={`text-[10px] uppercase tracking-wider font-semibold ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
                        {t('report.target_vector')}
                      </span>
                      <p className={`text-sm font-mono mt-1 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                        {selectedEvent.dst_ip}:{selectedEvent.dst_port}
                      </p>
                    </div>
                  </div>

                  {/* AI Confidence bar */}
                  <div>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className={`text-[10px] uppercase tracking-wider font-semibold ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
                        {t('report.ai_confidence')}
                      </span>
                      <span className={`text-sm font-mono font-bold ${isDark ? 'text-slate-200' : 'text-slate-800'}`}>
                        {(selectedEvent.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className={`w-full h-2 rounded-full overflow-hidden ${isDark ? 'bg-white/[0.06]' : 'bg-slate-200'}`}>
                      <div
                        className="h-full rounded-full transition-all duration-500"
                        style={{
                          width: `${selectedEvent.confidence * 100}%`,
                          background: selectedEvent.confidence >= 0.95
                            ? '#ef4444'
                            : selectedEvent.confidence >= 0.85
                              ? '#f59e0b'
                              : '#38bdf8',
                        }}
                      />
                    </div>
                  </div>

                  {/* Auto Response */}
                  <div className={`rounded-lg p-4 ${isDark ? 'bg-amber-500/5 border border-amber-500/15' : 'bg-amber-50 border border-amber-200'}`}>
                    <div className="flex items-center gap-2 mb-2">
                      <Clock className={`w-3.5 h-3.5 ${isDark ? 'text-amber-400' : 'text-amber-500'}`} />
                      <span className={`text-[10px] uppercase tracking-wider font-bold ${isDark ? 'text-amber-400' : 'text-amber-600'}`}>
                        {t('report.response')}
                      </span>
                    </div>
                    <p className={`text-sm leading-relaxed ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                      {getAutoResponse(selectedEvent.prediction, selectedEvent.src_ip, selectedEvent.dst_port)}
                    </p>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center py-12">
                  <p className={`text-sm ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
                    {t('report.select_event')}
                  </p>
                </div>
              )}
            </div>
          </>
        )}
    </div>
  )
}
