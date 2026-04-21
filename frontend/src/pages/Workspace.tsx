import { useEffect, useState, useRef, useCallback } from 'react'
import {
  Play, Square, Cpu, HardDrive, Terminal, ChevronDown,
  Globe, Clock, Gauge, Server, Activity, ArrowDown, ArrowUp, Zap, Radio, Monitor,
} from 'lucide-react'
import { getState, setBenign, getSystemMetrics, type DemoState, type SystemMetrics } from '../services/api'
import { useT, useSettings } from '../i18n'

/* ------------------------------------------------------------------ */
/*  Static data                                                        */
/* ------------------------------------------------------------------ */

const ACTIVITIES = [
  { method: 'GET',  url: 'https://example.com/index.html',       status: '200', size: '1.2 KB',  latency: '42ms' },
  { method: 'GET',  url: 'https://api.service.com/v2/data',      status: '200', size: '3.5 KB',  latency: '87ms' },
  { method: 'POST', url: 'https://mail.provider.com/send',       status: '201', size: '0.8 KB',  latency: '124ms' },
  { method: 'GET',  url: 'https://cdn.images.io/photo.jpg',      status: '200', size: '45.0 KB', latency: '31ms' },
  { method: 'DNS',  url: 'example.com -> 93.184.216.34',         status: 'OK',  size: '64 B',    latency: '4ms' },
  { method: 'GET',  url: 'https://docs.project.dev/readme',      status: '200', size: '2.1 KB',  latency: '56ms' },
  { method: 'TLS',  url: 'handshake api.service.com:443',        status: 'OK',  size: '1.4 KB',  latency: '18ms' },
  { method: 'GET',  url: 'https://news.site.org/latest',         status: '200', size: '8.2 KB',  latency: '93ms' },
  { method: 'DNS',  url: 'mail.provider.com -> 10.0.0.25',       status: 'OK',  size: '64 B',    latency: '3ms' },
  { method: 'GET',  url: 'https://storage.cloud.io/report.pdf',  status: '200', size: '125 KB',  latency: '210ms' },
  { method: 'GET',  url: 'https://fonts.gstatic.com/s/inter',    status: '200', size: '18.4 KB', latency: '22ms' },
  { method: 'POST', url: 'https://analytics.app.io/event',       status: '204', size: '0.3 KB',  latency: '67ms' },
  { method: 'GET',  url: 'https://github.com/notifications',     status: '200', size: '4.7 KB',  latency: '105ms' },
  { method: 'GET',  url: 'https://weather.api.com/today',        status: '200', size: '1.0 KB',  latency: '48ms' },
]

const METHOD_STYLE: Record<string, string> = {
  GET:  'bg-blue-500/20 text-blue-400 border-blue-500/30',
  POST: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  DNS:  'bg-purple-500/20 text-purple-400 border-purple-500/30',
  TLS:  'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
}

const INTERFACES = ['eth0', 'wlan0', 'lo0'] as const

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

function rand(min: number, max: number) {
  return Math.floor(Math.random() * (max - min + 1)) + min
}

function fmtTime(d: Date) {
  return d.toTimeString().slice(0, 8) + '.' + String(rand(0, 999)).padStart(3, '0')
}

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

interface LogLine {
  ts: string
  method: string
  url: string
  status: string
  size: string
  latency: string
}

/* ------------------------------------------------------------------ */
/*  Inline keyframes (injected once)                                   */
/* ------------------------------------------------------------------ */

const STYLE_ID = 'workspace-anims'
const KEYFRAMES = `
@keyframes ws-pulse-glow {
  0%, 100% { box-shadow: 0 0 0 0 rgba(59,130,246,0.25); }
  50%      { box-shadow: 0 0 16px 4px rgba(59,130,246,0.15); }
}
@keyframes ws-blink {
  0%, 100% { opacity: 1; }
  50%      { opacity: 0; }
}
@keyframes ws-spin-slow {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}
`

function ensureStyles() {
  if (typeof document === 'undefined') return
  if (!document.getElementById(STYLE_ID)) {
    const el = document.createElement('style')
    el.id = STYLE_ID
    el.textContent = KEYFRAMES
    document.head.appendChild(el)
  }
}

/* ================================================================== */
/*  Component                                                          */
/* ================================================================== */

export default function Workspace() {
  const t = useT()
  const { theme } = useSettings()
  const isDark = theme === 'dark'

  const [state, setState] = useState<DemoState | null>(null)
  const [speed, setSpeed] = useState(1.0)
  const [logs, setLogs] = useState<LogLine[]>(() => {
    try { return JSON.parse(sessionStorage.getItem('ws_logs') ?? '[]') } catch { return [] }
  })
  const [iface, setIface] = useState<(typeof INTERFACES)[number]>('eth0')
  const [ifaceOpen, setIfaceOpen] = useState(false)
  const [sys, setSys] = useState<SystemMetrics | null>(null)
  const logRef = useRef<HTMLDivElement>(null)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const isActive = state?.benign_active ?? false

  // Inject CSS keyframes
  useEffect(ensureStyles, [])

  // Poll state + system metrics
  useEffect(() => {
    const poll = () => {
      getState().then((s) => { setState(s); setSpeed(s.benign_speed || 1.0) }).catch(() => {})
      getSystemMetrics().then(setSys).catch(() => {})
    }
    poll()
    const id = setInterval(poll, 2000)
    return () => clearInterval(id)
  }, [])

  // Generate log lines when active
  useEffect(() => {
    if (isActive) {
      intervalRef.current = setInterval(() => {
        const now = new Date()
        const entry = ACTIVITIES[rand(0, ACTIVITIES.length - 1)]
        setLogs((prev) => [...prev.slice(-100), {
          ts: fmtTime(now),
          ...entry,
        }])
      }, 500)
    } else {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
    return () => { if (intervalRef.current) clearInterval(intervalRef.current) }
  }, [isActive])

  // Auto-scroll log + persist to sessionStorage
  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight
    try { sessionStorage.setItem('ws_logs', JSON.stringify(logs.slice(-100))) } catch {}
  }, [logs])

  const toggleTraffic = useCallback(() => {
    setBenign(!isActive, speed).then(() => getState().then(setState))
  }, [isActive, speed])

  const changeSpeed = useCallback((s: number) => {
    setSpeed(s)
    if (isActive) setBenign(true, s)
  }, [isActive])

  // Real system stats from server
  const cpu = sys?.cpu_pct ?? 0
  const mem = sys?.mem_pct ?? 0
  const netDown = sys?.net_down_mbps?.toFixed(2) ?? '0.0'
  const netUp = sys?.net_up_mbps?.toFixed(2) ?? '0.0'
  const conns = sys?.connections ?? 0
  const packets = sys ? sys.packets_recv + sys.packets_sent : 0

  const now = new Date()

  return (
    <div className="space-y-4">
      {/* ============ Machine Identity Banner ============ */}
      <div className={`rounded-xl p-4 flex items-center gap-4 border-2 ${
        isDark
          ? 'bg-gradient-to-r from-blue-500/5 to-transparent border-blue-500/30'
          : 'bg-gradient-to-r from-blue-50 to-white border-blue-300'
      }`}>
        <div className={`w-14 h-14 rounded-xl flex items-center justify-center ${
          isDark ? 'bg-blue-500/15' : 'bg-blue-100'
        }`}>
          <Monitor className="w-7 h-7 text-blue-500" />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-3 flex-wrap">
            <span className={`text-lg font-bold ${isDark ? 'text-slate-100' : 'text-slate-900'}`}>
              {t('machine.workstation_role')}
            </span>
            <span className={`text-xs px-2 py-0.5 rounded-full font-semibold bg-blue-500/20 text-blue-600 border border-blue-500/30`}>
              {t('machine.workstation_label')}
            </span>
          </div>
          <div className={`flex items-center gap-4 mt-1 text-sm font-mono ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
            <span>{t('machine.ip')}: <span className={isDark ? 'text-blue-400' : 'text-blue-600'}>{t('machine.workstation_ip')}</span></span>
            <span>{t('machine.os')}: <span className={isDark ? 'text-slate-300' : 'text-slate-700'}>{t('machine.workstation_os')}</span></span>
          </div>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <span className={`w-2 h-2 rounded-full ${isActive ? 'bg-blue-500 animate-pulse' : 'bg-slate-500'}`}></span>
          <span className={isActive ? (isDark ? 'text-blue-400' : 'text-blue-600') : (isDark ? 'text-slate-500' : 'text-slate-500')}>
            {isActive ? 'GENERATING TRAFFIC' : 'IDLE'}
          </span>
        </div>
      </div>

      {/* ============ Taskbar ============ */}
      <div
        className={`relative flex items-center justify-between rounded-xl px-5 py-3 border overflow-hidden ${
          isDark
            ? 'border-[#334155]'
            : 'border-slate-200'
        }`}
        style={{
          background: isDark
            ? 'linear-gradient(180deg, #1e293b 0%, #162032 100%)'
            : 'linear-gradient(180deg, #ffffff 0%, #f8fafc 100%)',
        }}
      >
        {/* Window control dots */}
        <div className="flex items-center gap-5">
          <div className="flex items-center gap-1.5 mr-2">
            <span className="w-3 h-3 rounded-full bg-[#ff5f57] border border-[#e0443e]" />
            <span className="w-3 h-3 rounded-full bg-[#febc2e] border border-[#d4a123]" />
            <span className="w-3 h-3 rounded-full bg-[#28c840] border border-[#1aab29]" />
          </div>

          <span className={`font-bold text-sm tracking-wide flex items-center gap-2 ${
            isDark ? 'text-slate-200' : 'text-slate-800'
          }`}>
            <Terminal className={`w-3.5 h-3.5 ${isDark ? 'text-slate-400' : 'text-slate-500'}`} />
            {t('workspace.hostname')}
          </span>

          <div className={`w-px h-[18px] ${isDark ? 'bg-[#475569]' : 'bg-slate-300'}`} />

          <span className={`text-xs font-medium flex items-center gap-1.5 ${
            isDark ? 'text-slate-400' : 'text-slate-500'
          }`}>
            <Clock className="w-3 h-3" />
            {now.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
            {' '}{now.toTimeString().slice(0, 8)}
          </span>

          <div className={`w-px h-[18px] ${isDark ? 'bg-[#475569]' : 'bg-slate-300'}`} />

          {/* Network interface selector */}
          <div className="relative">
            <button
              onClick={() => setIfaceOpen(!ifaceOpen)}
              className={`flex items-center gap-1.5 text-xs font-mono transition-colors duration-200 rounded-md px-2.5 py-1 border ${
                isDark
                  ? 'text-slate-400 hover:text-slate-200 bg-[#0f172a]/50 border-[#334155]'
                  : 'text-slate-500 hover:text-slate-700 bg-slate-100 border-slate-200'
              }`}
            >
              <Radio className="w-3 h-3" />
              {iface}
              <ChevronDown className={`w-3 h-3 transition-transform duration-200 ${ifaceOpen ? 'rotate-180' : ''}`} />
            </button>
            {ifaceOpen && (
              <div className={`absolute top-full left-0 mt-1 border rounded-md z-50 min-w-[120px] overflow-hidden ${
                isDark
                  ? 'bg-[#1e293b] border-[#334155] shadow-2xl shadow-black/60'
                  : 'bg-white border-slate-300 shadow-xl shadow-slate-400/30'
              }`}>
                {INTERFACES.map((n) => (
                  <button
                    key={n}
                    onClick={() => { setIface(n); setIfaceOpen(false) }}
                    className={`block w-full text-left text-xs font-mono px-3 py-2 transition-colors duration-150 ${
                      n === iface
                        ? isDark
                          ? 'bg-blue-600/30 text-blue-300'
                          : 'bg-blue-100 text-blue-700 font-semibold'
                        : isDark
                          ? 'text-slate-300 hover:bg-[#334155]/60 hover:text-slate-100'
                          : 'text-slate-700 hover:bg-slate-100'
                    }`}
                  >
                    {n}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center gap-4">
          {/* Connection count badge */}
          <span className={`flex items-center gap-1.5 text-xs font-mono rounded-md px-2.5 py-1 transition-all duration-500 border ${
            isDark
              ? 'bg-[#0f172a]/60 border-[#334155]'
              : 'bg-slate-100 border-slate-200'
          }`}>
            <Globe className={`w-3 h-3 ${isDark ? 'text-slate-400' : 'text-slate-500'}`} />
            <span className={`font-semibold transition-colors duration-500 ${conns > 0 ? 'text-emerald-400' : 'text-slate-500'}`}>
              {conns}
            </span>
            <span className="text-slate-500">{t('common.conn')}</span>
          </span>

          <span className={`text-xs font-medium transition-colors duration-500 ${
            isDark ? 'text-slate-400' : 'text-slate-500'
          }`}>
            {isActive ? t('common.connected') : t('common.disconnected')}
          </span>
          <span
            className={`w-2.5 h-2.5 rounded-full transition-all duration-500 ${
              isActive
                ? 'bg-emerald-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]'
                : 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]'
            }`}
            style={isActive ? { animation: 'ws-pulse-glow 2s ease-in-out infinite' } : {}}
          />
        </div>
      </div>

      {/* ============ Main panels ============ */}
      <div className="grid grid-cols-[3fr_2fr] gap-4">
        {/* ---------- Network Activity Log ---------- */}
        <div className={`border rounded-xl p-5 transition-all duration-500 ${
          isDark
            ? 'bg-[#1e293b] border-[#334155]'
            : 'bg-white border-slate-200'
        }`}>
          <div className="flex items-center justify-between mb-3">
            <div className={`flex items-center gap-2 text-xs font-bold uppercase tracking-wider ${
              isDark ? 'text-slate-400' : 'text-slate-600'
            }`}>
              <Activity className="w-3.5 h-3.5 text-blue-500" />
              {t('workspace.network_activity')}
            </div>
            {isActive && (
              <span className="text-[10px] font-mono text-emerald-500/70 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" style={{ animation: 'ws-blink 1s steps(1) infinite' }} />
                {t('common.live')}
              </span>
            )}
          </div>

          <div
            ref={logRef}
            className={`border rounded-lg p-3 font-mono text-xs leading-[1.85] max-h-[370px] overflow-y-auto ${
              isDark
                ? 'bg-[#0f172a] border-[#1e293b]/80'
                : 'bg-slate-50 border-slate-200'
            }`}
            style={{ scrollBehavior: 'smooth' }}
          >
            {logs.length > 0 ? (
              logs.map((l, i) => (
                <div
                  key={i}
                  className="whitespace-nowrap overflow-hidden text-ellipsis flex items-center gap-2 py-[1px] transition-opacity duration-300"
                >
                  <span className={`tabular-nums text-[11px] shrink-0 ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>{l.ts}</span>
                  <span
                    className={`inline-flex items-center justify-center w-[38px] shrink-0 text-[10px] font-bold rounded border px-1 py-[0.5px] ${
                      METHOD_STYLE[l.method] ?? 'bg-slate-500/20 text-slate-400 border-slate-500/30'
                    }`}
                  >
                    {l.method}
                  </span>
                  <span className="text-emerald-400/90 truncate">{l.url}</span>
                  <span className="text-slate-500 shrink-0">[{l.status}]</span>
                  <span className={`shrink-0 ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>{l.size}</span>
                  <span className={`shrink-0 ${isDark ? 'text-slate-700' : 'text-slate-400'}`}>{l.latency}</span>
                </div>
              ))
            ) : (
              /* Empty / stopped state */
              <div className="flex flex-col items-center justify-center py-16 select-none">
                <Terminal className={`w-8 h-8 mb-3 ${isDark ? 'text-slate-700' : 'text-slate-300'}`} />
                <div className={`font-mono text-sm mb-1 ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
                  <span className={isDark ? 'text-slate-500' : 'text-slate-400'}>$</span> {t('workspace.awaiting')}
                  <span style={{ animation: 'ws-blink 1s steps(1) infinite' }}>_</span>
                </div>
                <p className={`text-[11px] mt-2 ${isDark ? 'text-slate-700' : 'text-slate-400'}`}>
                  {t('workspace.start_hint')} <span className="text-blue-500 font-semibold">{t('workspace.start_traffic')}</span> {t('workspace.press')}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* ---------- System Info ---------- */}
        <div className={`border rounded-xl p-5 ${
          isDark
            ? 'bg-[#1e293b] border-[#334155]'
            : 'bg-white border-slate-200'
        }`}>
          <div className={`flex items-center gap-2 text-xs font-bold uppercase tracking-wider mb-4 ${
            isDark ? 'text-slate-400' : 'text-slate-600'
          }`}>
            <Server className="w-3.5 h-3.5 text-blue-500" />
            {t('workspace.system_info')}
          </div>

          <div className="space-y-1">
            <SysRow isDark={isDark} icon={<Cpu className="w-3.5 h-3.5 text-blue-400" />}   label={t('workspace.cpu')}      value={`${cpu}%`}            pct={cpu}                                         color="bg-blue-500"    glow="shadow-[0_0_6px_rgba(59,130,246,0.3)]" />
            <SysRow isDark={isDark} icon={<HardDrive className="w-3.5 h-3.5 text-amber-400" />} label={t('workspace.memory')}   value={`${mem}%`}            pct={mem}                                         color="bg-amber-500"   glow="shadow-[0_0_6px_rgba(245,158,11,0.3)]" />
            <SysRow isDark={isDark} icon={<ArrowDown className="w-3.5 h-3.5 text-emerald-400" />} label={t('workspace.net_down')} value={`${netDown} ${t('common.mbps')}`}    pct={Math.min(Number(netDown) / 10 * 100, 100)}  color="bg-emerald-500" glow="shadow-[0_0_6px_rgba(34,197,94,0.3)]" />
            <SysRow isDark={isDark} icon={<ArrowUp className="w-3.5 h-3.5 text-emerald-400" />}   label={t('workspace.net_up')} value={`${netUp} ${t('common.mbps')}`}      pct={Math.min(Number(netUp) / 5 * 100, 100)}     color="bg-emerald-500" glow="shadow-[0_0_6px_rgba(34,197,94,0.3)]" />

            <div className={`pt-2 mt-2 border-t space-y-0 ${isDark ? 'border-[#334155]/60' : 'border-slate-200'}`}>
              <SysRowText isDark={isDark} icon={<Globe className="w-3.5 h-3.5 text-blue-400" />}    label={t('workspace.connections')}  value={String(conns)} highlight={conns > 0} />
              <SysRowText isDark={isDark} icon={<Zap className="w-3.5 h-3.5 text-amber-400" />}     label={t('workspace.packets_sec')} value={String(packets)} highlight={packets > 0} />
              <SysRowText isDark={isDark} icon={<Terminal className="w-3.5 h-3.5 text-slate-500" />} label={t('workspace.hostname_label')}     value={sys?.hostname ?? '—'} />
              <SysRowText isDark={isDark} icon={<Server className="w-3.5 h-3.5 text-slate-500" />}   label={t('workspace.os')}           value={sys?.os ?? '—'} />
              <SysRowText isDark={isDark} icon={<Gauge className="w-3.5 h-3.5 text-slate-500" />}    label={t('workspace.uptime')}       value={sys?.uptime ?? '—'} />
            </div>
          </div>
        </div>
      </div>

      {/* ============ Control bar ============ */}
      <div
        className={`border rounded-xl px-6 py-4 flex items-center gap-8 ${
          isDark
            ? 'border-[#334155]'
            : 'border-slate-200'
        }`}
        style={{
          background: isDark
            ? 'linear-gradient(180deg, #1e293b 0%, #182235 100%)'
            : 'linear-gradient(180deg, #ffffff 0%, #f8fafc 100%)',
        }}
      >
        <button
          onClick={toggleTraffic}
          className={`group relative flex items-center gap-3 px-8 py-3 rounded-xl text-sm font-bold tracking-wide transition-all duration-300 border ${
            isActive
              ? isDark
                ? 'bg-red-500/10 text-red-400 hover:bg-red-500/20 border-red-500/30 hover:border-red-500/50'
                : 'bg-red-50 text-red-600 hover:bg-red-100 border-red-300 hover:border-red-400 shadow-sm'
              : 'bg-blue-600 text-white hover:bg-blue-500 border-blue-400/30 shadow-[0_0_20px_rgba(59,130,246,0.25)] hover:shadow-[0_0_28px_rgba(59,130,246,0.4)]'
          }`}
        >
          {isActive ? (
            <Square className="w-4.5 h-4.5 transition-transform duration-300 group-hover:scale-110" />
          ) : (
            <Play
              className="w-4.5 h-4.5 transition-transform duration-300 group-hover:translate-x-0.5"
            />
          )}
          {isActive ? t('workspace.stop_btn') : t('workspace.start_btn')}
        </button>

        <div className={`h-8 w-px ${isDark ? 'bg-[#334155]' : 'bg-slate-200'}`} />

        <div className="flex items-center gap-3">
          <span className={`text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5 ${
            isDark ? 'text-slate-500' : 'text-slate-500'
          }`}>
            <Gauge className="w-3 h-3" />
            {t('workspace.speed')}
          </span>
          <div className={`flex items-center gap-1.5 rounded-lg p-1 border ${
            isDark
              ? 'bg-[#0f172a]/60 border-[#334155]/60'
              : 'bg-slate-100 border-slate-200'
          }`}>
            {[0.5, 1.0, 2.0, 5.0].map((s) => (
              <button
                key={s}
                onClick={() => changeSpeed(s)}
                className={`px-3.5 py-1.5 rounded-md text-xs font-mono font-semibold transition-all duration-200 ${
                  speed === s
                    ? 'bg-blue-600/30 text-blue-400 shadow-[0_0_8px_rgba(59,130,246,0.15)] border border-blue-500/30'
                    : isDark
                      ? 'text-slate-500 hover:text-slate-300 hover:bg-[#1e293b]/60 border border-transparent'
                      : 'text-slate-500 hover:text-slate-700 hover:bg-slate-200 border border-transparent'
                }`}
              >
                {s}x
              </button>
            ))}
          </div>
        </div>

        {/* Live stats in control bar */}
        {isActive && (
          <div className="ml-auto flex items-center gap-4 text-xs font-mono text-slate-500 transition-opacity duration-500">
            <span className="flex items-center gap-1">
              <ArrowDown className="w-3 h-3 text-emerald-500" />
              <span className="text-emerald-400">{netDown}</span> {t('common.mbps')}
            </span>
            <span className="flex items-center gap-1">
              <ArrowUp className="w-3 h-3 text-emerald-500" />
              <span className="text-emerald-400">{netUp}</span> {t('common.mbps')}
            </span>
          </div>
        )}
      </div>

      {/* ============ Tip (with pulse animation) ============ */}
      <div
        className={`flex items-center gap-3 border rounded-xl px-5 py-3.5 text-sm transition-all duration-500 ${
          isActive
            ? 'bg-[#172554]/80 border-[#1e40af]/60 text-blue-300 opacity-100 translate-y-0'
            : 'bg-[#172554]/30 border-[#1e40af]/20 text-blue-400/50 opacity-60 translate-y-0'
        }`}
        style={isActive ? { animation: 'ws-pulse-glow 3s ease-in-out infinite' } : {}}
      >
        <Activity className={`w-4 h-4 shrink-0 transition-colors duration-500 ${isActive ? 'text-blue-400' : 'text-blue-500/30'}`} />
        <span>
          {t('workspace.tip').split('**').map((part, i) =>
            i % 2 === 1
              ? <strong key={i} className="text-blue-200">{part}</strong>
              : <span key={i}>{part}</span>
          )}
        </span>
      </div>
    </div>
  )
}


/* ================================================================== */
/*  Sub-components                                                     */
/* ================================================================== */

function SysRow({ icon, label, value, pct, color, glow, isDark }: {
  icon: React.ReactNode; label: string; value: string; pct: number; color: string; glow?: string; isDark: boolean
}) {
  return (
    <div>
      <div className="flex items-center justify-between py-2 font-mono text-[13px]">
        <span className={`flex items-center gap-2 ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>{icon} {label}</span>
        <span className={`font-semibold tabular-nums ${isDark ? 'text-slate-200' : 'text-slate-800'}`}>{value}</span>
      </div>
      <div className={`w-full h-1.5 rounded-full overflow-hidden ${isDark ? 'bg-[#0f172a]' : 'bg-slate-200'}`}>
        <div
          className={`h-full rounded-full ${color} ${glow ?? ''} transition-all duration-700 ease-out`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

function SysRowText({ icon, label, value, highlight, isDark }: {
  icon?: React.ReactNode; label: string; value: string; highlight?: boolean; isDark: boolean
}) {
  return (
    <div className={`flex items-center justify-between py-2 border-b last:border-b-0 font-mono text-[13px] ${
      isDark ? 'border-[#1e293b]/60' : 'border-slate-100'
    }`}>
      <span className={`flex items-center gap-2 ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
        {icon}
        {label}
      </span>
      <span className={`font-semibold tabular-nums transition-colors duration-500 ${
        highlight ? 'text-emerald-400' : isDark ? 'text-slate-200' : 'text-slate-800'
      }`}>
        {value}
      </span>
    </div>
  )
}
