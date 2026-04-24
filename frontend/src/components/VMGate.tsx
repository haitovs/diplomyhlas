import { useEffect, useRef, useState, type ReactNode } from 'react'
import { Power, Terminal as TerminalIcon, Shield, Monitor, Skull, ChevronRight } from 'lucide-react'
import { useT, useSettings, type TranslationKey } from '../i18n'
import { useVM, VM_BOOT_DURATION_MS, type VMId } from '../contexts/VMContext'
import { IDS_BOOT, TRAFFIC_BOOT, ATTACKER_BOOT, type BootLine } from './vmBootSequences'
import { setAllAttacks, setBenign, setDefender } from '../services/api'

interface VMMeta {
  hostname: string
  distro: string
  ip: string
  accent: 'amber' | 'blue' | 'red'
  icon: typeof Shield
  boot: BootLine[]
  titleKey: TranslationKey
  descKey: TranslationKey
  poweredOffKey: TranslationKey
}

const META: Record<VMId, VMMeta> = {
  ids: {
    hostname: 'ids-node',
    distro: 'Rocky Linux 9.3 (Blue Onyx)',
    ip: '10.10.10.5',
    accent: 'amber',
    icon: Shield,
    boot: IDS_BOOT,
    titleKey: 'vm.ids_title',
    descKey: 'vm.ids_desc',
    poweredOffKey: 'vm.ids_off',
  },
  traffic: {
    hostname: 'ws-client',
    distro: 'Ubuntu 22.04.3 LTS (Jammy)',
    ip: '192.168.1.42',
    accent: 'blue',
    icon: Monitor,
    boot: TRAFFIC_BOOT,
    titleKey: 'vm.traffic_title',
    descKey: 'vm.traffic_desc',
    poweredOffKey: 'vm.traffic_off',
  },
  attacker: {
    hostname: 'adversary',
    distro: 'Kali GNU/Linux 2025.1',
    ip: '10.10.10.66',
    accent: 'red',
    icon: Skull,
    boot: ATTACKER_BOOT,
    titleKey: 'vm.attacker_title',
    descKey: 'vm.attacker_desc',
    poweredOffKey: 'vm.attacker_off',
  },
}

const ACCENTS: Record<VMMeta['accent'], {
  bg: string; bgDim: string; border: string; text: string; glow: string; btn: string; btnHover: string;
}> = {
  amber: {
    bg: 'bg-amber-500', bgDim: 'bg-amber-500/15', border: 'border-amber-500/40',
    text: 'text-amber-500', glow: 'shadow-[0_0_60px_rgba(245,158,11,0.35)]',
    btn: 'bg-amber-500 hover:bg-amber-400', btnHover: 'hover:shadow-[0_0_40px_rgba(245,158,11,0.5)]',
  },
  blue: {
    bg: 'bg-blue-500', bgDim: 'bg-blue-500/15', border: 'border-blue-500/40',
    text: 'text-blue-500', glow: 'shadow-[0_0_60px_rgba(59,130,246,0.35)]',
    btn: 'bg-blue-500 hover:bg-blue-400', btnHover: 'hover:shadow-[0_0_40px_rgba(59,130,246,0.5)]',
  },
  red: {
    bg: 'bg-red-500', bgDim: 'bg-red-500/15', border: 'border-red-500/40',
    text: 'text-red-500', glow: 'shadow-[0_0_60px_rgba(239,68,68,0.35)]',
    btn: 'bg-red-500 hover:bg-red-400', btnHover: 'hover:shadow-[0_0_40px_rgba(239,68,68,0.5)]',
  },
}

function PoweredOff({ vmId }: { vmId: VMId }) {
  const t = useT()
  const { theme } = useSettings()
  const { start } = useVM()
  const isDark = theme === 'dark'
  const meta = META[vmId]
  const a = ACCENTS[meta.accent]
  const Icon = meta.icon

  return (
    <div className={`min-h-[72vh] flex items-center justify-center rounded-2xl border-2 border-dashed ${
      isDark ? 'border-white/[0.06] bg-[#0a0f1a]' : 'border-slate-300 bg-slate-50'
    }`}>
      <div className="flex flex-col items-center gap-6 max-w-xl text-center px-8">
        <div className={`w-24 h-24 rounded-2xl flex items-center justify-center border ${a.border} ${a.bgDim}`}>
          <Icon className={`w-12 h-12 ${a.text}`} />
        </div>

        <div className="space-y-2">
          <div className={`text-[10px] font-mono tracking-[0.3em] uppercase ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
            {t('vm.virtual_machine')} • {meta.hostname}
          </div>
          <h2 className={`text-2xl font-bold ${isDark ? 'text-slate-100' : 'text-slate-900'}`}>
            {t(meta.poweredOffKey)}
          </h2>
          <p className={`text-sm ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
            {t(meta.descKey)}
          </p>
        </div>

        <div className={`grid grid-cols-3 gap-3 w-full text-left font-mono text-[11px] ${
          isDark ? 'text-slate-500' : 'text-slate-500'
        }`}>
          <div className={`p-3 rounded-lg border ${isDark ? 'border-white/[0.05] bg-white/[0.02]' : 'border-slate-200 bg-white'}`}>
            <div className="opacity-60 uppercase tracking-wider text-[9px] mb-1">{t('vm.hostname')}</div>
            <div className={`${isDark ? 'text-slate-200' : 'text-slate-800'} truncate`}>{meta.hostname}</div>
          </div>
          <div className={`p-3 rounded-lg border ${isDark ? 'border-white/[0.05] bg-white/[0.02]' : 'border-slate-200 bg-white'}`}>
            <div className="opacity-60 uppercase tracking-wider text-[9px] mb-1">{t('vm.os')}</div>
            <div className={`${isDark ? 'text-slate-200' : 'text-slate-800'} truncate`}>{meta.distro.split(' ')[0]}</div>
          </div>
          <div className={`p-3 rounded-lg border ${isDark ? 'border-white/[0.05] bg-white/[0.02]' : 'border-slate-200 bg-white'}`}>
            <div className="opacity-60 uppercase tracking-wider text-[9px] mb-1">{t('vm.ip')}</div>
            <div className={`${isDark ? 'text-slate-200' : 'text-slate-800'} truncate`}>{meta.ip}</div>
          </div>
        </div>

        <button
          onClick={() => start(vmId)}
          className={`group relative flex items-center gap-3 px-10 py-5 rounded-2xl font-bold text-white transition-all duration-300 ${a.btn} ${a.btnHover} ${a.glow}`}
        >
          <Power className="w-6 h-6 transition-transform group-hover:scale-110" />
          <span className="tracking-wide">{t('vm.start_vm')}</span>
          <ChevronRight className="w-5 h-5 opacity-60 transition-transform group-hover:translate-x-1" />
        </button>

        <div className={`text-[11px] font-mono ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
          {t('vm.boot_hint')}
        </div>
      </div>
    </div>
  )
}

function Booting({ vmId }: { vmId: VMId }) {
  const t = useT()
  const { theme } = useSettings()
  const { vms } = useVM()
  const isDark = theme === 'dark'
  const meta = META[vmId]
  const a = ACCENTS[meta.accent]
  const startedAt = vms[vmId].bootStartedAt ?? Date.now()

  const [elapsed, setElapsed] = useState(() => Date.now() - startedAt)
  const logRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const id = window.setInterval(() => setElapsed(Date.now() - startedAt), 120)
    return () => window.clearInterval(id)
  }, [startedAt])

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight
  }, [elapsed])

  const visibleLines = meta.boot.filter((l) => l.at <= elapsed)
  const progressPct = Math.min(100, (elapsed / VM_BOOT_DURATION_MS) * 100)
  const secondsLeft = Math.max(0, Math.ceil((VM_BOOT_DURATION_MS - elapsed) / 1000))

  return (
    <div className={`min-h-[72vh] rounded-2xl border overflow-hidden ${
      isDark ? 'border-white/[0.08] bg-[#05080f]' : 'border-slate-800 bg-[#05080f]'
    } flex flex-col`}>
      {/* fake terminal header */}
      <div className="flex items-center gap-2 px-4 py-2.5 bg-[#0c1222] border-b border-white/[0.05]">
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-red-500/80" />
          <span className="w-3 h-3 rounded-full bg-amber-500/80" />
          <span className="w-3 h-3 rounded-full bg-emerald-500/80" />
        </div>
        <div className="flex-1 flex items-center justify-center gap-2 text-xs font-mono text-slate-400">
          <TerminalIcon className="w-3.5 h-3.5" />
          <span>{meta.hostname}@console — tty1</span>
        </div>
        <div className={`text-[11px] font-mono ${a.text}`}>
          {t('vm.booting')} • {secondsLeft}s
        </div>
      </div>

      {/* progress strip */}
      <div className="h-1 bg-white/[0.04] overflow-hidden">
        <div
          className={`h-full ${a.bg} transition-all duration-100`}
          style={{ width: `${progressPct}%` }}
        />
      </div>

      {/* log */}
      <div
        ref={logRef}
        className="flex-1 overflow-y-auto px-5 py-4 font-mono text-[13px] leading-[1.55] selection:bg-white/10"
        style={{ maxHeight: 'calc(100vh - 220px)' }}
      >
        {visibleLines.map((line, i) => (
          <div key={i} className={line.cls ?? 'text-slate-300'}>
            {line.text}
          </div>
        ))}
        <div className="flex items-center gap-1 mt-1 text-slate-600">
          <span>{meta.hostname} login:</span>
          <span className={`inline-block w-2 h-4 ${a.bg} animate-pulse`} />
        </div>
      </div>
    </div>
  )
}

function VMChip({ vmId }: { vmId: VMId }) {
  const t = useT()
  const { theme } = useSettings()
  const { shutdown } = useVM()
  const isDark = theme === 'dark'
  const meta = META[vmId]
  const a = ACCENTS[meta.accent]
  const Icon = meta.icon

  const confirmShutdown = () => {
    if (!window.confirm(t('vm.shutdown_confirm'))) return
    if (vmId === 'attacker') setAllAttacks(false).catch(() => {})
    if (vmId === 'traffic') setBenign(false).catch(() => {})
    if (vmId === 'ids') setDefender(false).catch(() => {})
    shutdown(vmId)
  }

  return (
    <div className={`fixed bottom-5 right-5 z-40 flex items-center gap-2 pl-3 pr-1.5 py-1.5 rounded-xl border shadow-xl backdrop-blur-sm ${
      isDark
        ? 'bg-[#0c1222]/90 border-white/[0.08] shadow-black/60'
        : 'bg-white/95 border-slate-200 shadow-slate-400/30'
    }`}>
      <div className={`w-6 h-6 rounded-md flex items-center justify-center ${a.bgDim}`}>
        <Icon className={`w-3.5 h-3.5 ${a.text}`} />
      </div>
      <div className="flex flex-col text-[10px] leading-tight font-mono">
        <span className={isDark ? 'text-slate-300' : 'text-slate-700'}>{meta.hostname}</span>
        <span className={`${a.text} flex items-center gap-1`}>
          <span className={`w-1.5 h-1.5 rounded-full ${a.bg} animate-pulse`} />
          {t('vm.running')}
        </span>
      </div>
      <button
        onClick={confirmShutdown}
        title={t('vm.shutdown')}
        className={`flex items-center gap-1 ml-1 px-2 py-1.5 rounded-lg text-[10px] font-semibold transition-all ${
          isDark
            ? 'bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/20'
            : 'bg-red-50 text-red-600 hover:bg-red-100 border border-red-200'
        }`}
      >
        <Power className="w-3 h-3" />
        {t('vm.shutdown')}
      </button>
    </div>
  )
}

export default function VMGate({ vmId, children }: { vmId: VMId; children: ReactNode }) {
  const { vms } = useVM()
  const status = vms[vmId].status

  if (status === 'off') return <PoweredOff vmId={vmId} />
  if (status === 'booting') return <Booting vmId={vmId} />
  return (
    <>
      {children}
      <VMChip vmId={vmId} />
    </>
  )
}
