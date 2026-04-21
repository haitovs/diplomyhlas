import { useEffect, useState, useCallback, useRef } from 'react'
import { Zap, X, Terminal, Skull } from 'lucide-react'
import {
  getState, setAttack, setAllAttacks, stopAll, sendBurst,
  type DemoState,
} from '../services/api'
import { useT, useSettings } from '../i18n'

type AttackInfoStatic = {
  port: string; tool: string; severity: 'CRITICAL' | 'HIGH'
  nameKey: 'attack.ddos_name' | 'attack.portscan_name' | 'attack.ssh_name' | 'attack.ftp_name'
  descKey: 'attack.ddos_desc' | 'attack.portscan_desc' | 'attack.ssh_desc' | 'attack.ftp_desc'
}

const ATTACK_INFO: Record<string, AttackInfoStatic> = {
  ddos: {
    nameKey: 'attack.ddos_name',
    descKey: 'attack.ddos_desc',
    port: '80',
    tool: 'hping3 / scapy',
    severity: 'CRITICAL',
  },
  portscan: {
    nameKey: 'attack.portscan_name',
    descKey: 'attack.portscan_desc',
    port: '1-1024',
    tool: 'nmap SYN scan',
    severity: 'HIGH',
  },
  ssh: {
    nameKey: 'attack.ssh_name',
    descKey: 'attack.ssh_desc',
    port: '22',
    tool: 'hydra / patator',
    severity: 'CRITICAL',
  },
  ftp: {
    nameKey: 'attack.ftp_name',
    descKey: 'attack.ftp_desc',
    port: '21',
    tool: 'medusa / patator',
    severity: 'HIGH',
  },
}

const QUICK_CMDS = [
  { label: '$ send_syn x1', attack: 'ddos', count: 1, desc: 'Send 1 SYN packet' },
  { label: '$ send_syn x10', attack: 'ddos', count: 10, desc: 'Send 10 SYN packets' },
  { label: '$ scan_ports', attack: 'portscan', count: 5, desc: 'Scan 5 ports' },
  { label: '$ brute_ssh', attack: 'ssh', count: 5, desc: '5 SSH attempts' },
  { label: '$ brute_ftp', attack: 'ftp', count: 5, desc: '5 FTP attempts' },
]

const FLAGS: Record<string, string[]> = {
  ddos: ['SYN', 'SYN', 'SYN', 'SYN', 'RST'],
  portscan: ['SYN', 'SYN\u2192ACK', 'RST', 'filtered', 'closed'],
  ssh: ['PSH\u00b7ACK', 'ACK', 'PSH\u00b7ACK', 'FIN\u00b7ACK'],
  ftp: ['PSH\u00b7ACK', 'ACK', 'PSH\u00b7ACK', 'RST'],
}

const STATUS: Record<string, string[]> = {
  ddos: ['sent', 'sent', 'sent', 'dropped', 'retransmit'],
  portscan: ['open', 'closed', 'filtered', 'open', 'closed'],
  ssh: ['AUTH_FAIL', 'AUTH_FAIL', 'AUTH_FAIL', 'TIMEOUT', 'CONNECTED'],
  ftp: ['530 Login incorrect', '530 Login incorrect', 'TIMEOUT', '331 Password required'],
}

const BAD_STATUSES = new Set(['dropped', 'AUTH_FAIL', '530 Login incorrect', 'TIMEOUT', 'filtered', 'closed'])

const BOOT_SEQUENCE = [
  { delay: 0, html: '<span class="text-green-500">[*] Establishing connection to target...</span>' },
  { delay: 300, html: '<span class="text-green-500">[+] CONNECTION ESTABLISHED</span>' },
  { delay: 600, html: '<span class="text-green-400">[*] Initializing attack framework v4.2.1...</span>' },
  { delay: 900, html: '<span class="text-green-400">[*] Loading kernel modules...</span>' },
  { delay: 1100, html: '<span class="text-cyan-400">[+] Module: packet_forge .......... OK</span>' },
  { delay: 1300, html: '<span class="text-cyan-400">[+] Module: syn_engine ............ OK</span>' },
  { delay: 1500, html: '<span class="text-cyan-400">[+] Module: brute_core ............ OK</span>' },
  { delay: 1700, html: '<span class="text-cyan-400">[+] Module: port_scanner .......... OK</span>' },
  { delay: 2000, html: '<span class="text-yellow-500">[*] Verifying exploit payloads...</span>' },
  { delay: 2300, html: '<span class="text-green-500">[+] All systems nominal. Ready to engage.</span>' },
  { delay: 2500, html: '<span class="text-red-500">[!] ATTACK MODULES ARMED</span>' },
  { delay: 2700, html: '<span class="text-slate-600">\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500</span>' },
]

function rand(min: number, max: number) { return Math.floor(Math.random() * (max - min + 1)) + min }
function pick<T>(arr: T[]): T { return arr[rand(0, arr.length - 1)] }
function randIp() { return `${pick([10, 172, 192])}.${rand(0, 255)}.${rand(0, 255)}.${rand(1, 254)}` }
function ts() {
  const n = new Date()
  return n.toTimeString().slice(0, 8) + '.' + String(rand(0, 999)).padStart(3, '0')
}

interface TermLine { html: string }

const SEVERITY_COLORS: Record<string, { dot: string; text: string; bg: string }> = {
  CRITICAL: { dot: 'bg-red-500 shadow-[0_0_6px_rgba(255,0,0,0.8)]', text: 'text-red-500', bg: 'bg-red-500/10' },
  HIGH: { dot: 'bg-orange-500 shadow-[0_0_6px_rgba(249,115,22,0.8)]', text: 'text-orange-500', bg: 'bg-orange-500/10' },
}

export default function AttackSpace() {
  const t = useT()
  const { theme } = useSettings()
  const isDark = theme === 'dark'
  const [state, setState] = useState<DemoState | null>(null)
  const [targetIp, setTargetIp] = useState('127.0.0.1')
  const [pktCount, setPktCount] = useState('100')
  const [termLines, setTermLines] = useState<TermLine[]>([])
  const [flashedCmd, setFlashedCmd] = useState<number | null>(null)
  const [bootDone, setBootDone] = useState(false)
  const [hasEverAttacked, setHasEverAttacked] = useState(false)
  const [showHelp, setShowHelp] = useState(false)
  const termRef = useRef<HTMLDivElement>(null)
  const prevActiveCount = useRef(0)

  const attacks = state?.attacks ?? {}
  const activeCount = Object.values(attacks).filter(Boolean).length

  // Poll state
  useEffect(() => {
    const poll = () => getState().then(setState).catch(() => {})
    poll()
    const id = setInterval(poll, 2000)
    return () => clearInterval(id)
  }, [])

  // Boot sequence when first attack starts
  useEffect(() => {
    if (activeCount > 0 && prevActiveCount.current === 0 && !hasEverAttacked) {
      setHasEverAttacked(true)
      setBootDone(false)
      setTermLines([])

      BOOT_SEQUENCE.forEach((step, i) => {
        setTimeout(() => {
          setTermLines(prev => [...prev, { html: `<span class="text-slate-600">${ts()}</span> ${step.html}` }])
          if (i === BOOT_SEQUENCE.length - 1) {
            setTimeout(() => setBootDone(true), 800)
          }
        }, step.delay)
      })
    } else if (activeCount > 0 && prevActiveCount.current === 0 && hasEverAttacked) {
      setBootDone(true)
    }
    prevActiveCount.current = activeCount
  }, [activeCount, hasEverAttacked])

  // Generate terminal output when attacks active
  useEffect(() => {
    if (activeCount === 0) {
      setTermLines([
        { html: `<span class="text-slate-700">${ts()} root@kali:~# <span class="animate-blink text-green-500">_</span></span>` },
        { html: `<span class="text-slate-700">${ts()} ${t('attack.waiting_commands')}</span>` },
        { html: `<span class="text-slate-700">${ts()} ${t('attack.select_hint')}</span>` },
      ])
      setBootDone(false)
      return
    }

    if (!bootDone) return

    const id = setInterval(() => {
      const lines: TermLine[] = []

      lines.push({ html: `<span class="text-slate-600">${ts()}</span> <span class="text-green-500">root@kali</span><span class="text-slate-600">:</span><span class="text-cyan-400">~</span><span class="text-slate-600">$</span> <span class="text-slate-400">./attack_suite --target ${targetIp} --threads 4</span>` })
      lines.push({ html: `<span class="text-slate-600">${ts()}</span> <span class="text-yellow-500">[*] Framework initialized. Loading ${activeCount} ${t('attack.module')}...</span>` })
      lines.push({ html: `<span class="text-slate-600">${ts()}</span> <span class="text-cyan-400">[*] ${t('attack.target')}: ${targetIp} | Packet burst: ${pktCount}</span>` })

      Object.entries(attacks).forEach(([key, on]) => {
        if (on) {
          const info = ATTACK_INFO[key]
          lines.push({ html: `<span class="text-slate-600">${ts()}</span> <span class="text-red-500 font-bold">[!] MODULE LOADED: ${t(info.nameKey)} \u2192 ${targetIp}:${info.port}</span>` })
        }
      })

      lines.push({ html: `<span class="text-slate-700">${ts()} ${'─'.repeat(60)}</span>` })

      const activeKeys = Object.entries(attacks).filter(([, v]) => v).map(([k]) => k)
      for (let i = 0; i < rand(10, 18); i++) {
        const atk = pick(activeKeys)
        const info = ATTACK_INFO[atk]
        const srcIp = randIp()
        const srcPort = rand(1024, 65535)
        const dstPort = atk === 'portscan' ? rand(1, 1024) : parseInt(info.port.split('-')[0])
        const flag = pick(FLAGS[atk])
        const status = pick(STATUS[atk])
        const pktSize = rand(40, 1500)

        let color: string
        let statusStyle: string
        if (BAD_STATUSES.has(status)) {
          color = 'text-red-500'
          statusStyle = 'font-bold'
        } else if (status === 'retransmit') {
          color = 'text-yellow-500'
          statusStyle = ''
        } else if (status === 'CONNECTED' || status === 'open') {
          color = 'text-green-400'
          statusStyle = 'font-bold'
        } else {
          color = 'text-green-500'
          statusStyle = ''
        }

        lines.push({ html:
          `<span class="text-slate-700">${ts()}</span> ` +
          `<span class="text-green-400/70">${srcIp}:${srcPort}</span>` +
          `<span class="text-slate-700"> \u2192 </span>` +
          `<span class="text-green-400/70">${targetIp}:${dstPort}</span> ` +
          `<span class="text-cyan-400">[${flag}]</span> ` +
          `<span class="text-slate-600">${pktSize}B</span> ` +
          `<span class="${color} ${statusStyle}">${status}</span>`
        })
      }

      lines.push({ html: `<span class="text-slate-700">${ts()} ${'─'.repeat(60)}</span>` })
      const totalPkts = rand(2000, 25000)
      const dropRate = (Math.random() * 10.5 + 1.5).toFixed(1)
      lines.push({ html: `<span class="text-slate-600">${ts()}</span> <span class="text-yellow-500">[*] Burst complete: ${totalPkts.toLocaleString()} pkts | drop rate: ${dropRate}% | active modules: ${activeCount}</span>` })
      lines.push({ html: `<span class="text-slate-600">${ts()}</span> <span class="text-green-500">root@kali</span><span class="text-slate-600">:</span><span class="text-cyan-400">~</span><span class="text-slate-600">$</span> <span class="animate-blink text-green-500">_</span>` })

      setTermLines(lines)
    }, 1500)

    return () => clearInterval(id)
  }, [activeCount, attacks, targetIp, pktCount, bootDone])

  // Auto-scroll terminal
  useEffect(() => {
    if (termRef.current) termRef.current.scrollTop = termRef.current.scrollHeight
  }, [termLines])

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'a') {
        e.preventDefault()
        launchAll()
      }
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        killAll()
      }
      if (e.key === '?') {
        setShowHelp(true)
      }
      if (e.key === 'Escape') {
        setShowHelp(false)
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  })

  const toggleAttack = useCallback((key: string) => {
    const isOn = attacks[key] ?? false
    setAttack(key, !isOn).then(() => getState().then(setState))
  }, [attacks])

  const launchAll = useCallback(() => {
    setAllAttacks(true).then(() => getState().then(setState))
  }, [])

  const killAll = useCallback(() => {
    stopAll().then(() => getState().then(setState))
  }, [])

  const quickCmd = useCallback((attack: string, count: number, idx: number) => {
    setFlashedCmd(idx)
    setTimeout(() => setFlashedCmd(null), 300)
    sendBurst(attack, count)
  }, [])

  return (
    <div
      className="space-y-4 min-h-full"
      style={{
        background: isDark ? `
          repeating-linear-gradient(0deg, rgba(0,255,0,0.008) 0px, rgba(0,255,0,0.008) 1px, transparent 1px, transparent 3px),
          radial-gradient(ellipse at 20% 30%, rgba(255,0,0,0.04) 0%, transparent 60%),
          radial-gradient(ellipse at 80% 70%, rgba(0,255,0,0.025) 0%, transparent 60%),
          #000000
        ` : `
          radial-gradient(ellipse at 20% 30%, rgba(239,68,68,0.04) 0%, transparent 60%),
          radial-gradient(ellipse at 80% 70%, rgba(239,68,68,0.02) 0%, transparent 60%),
          #ffffff
        `,
      }}
    >
      {/* Machine Identity Banner */}
      <div className={`rounded-xl p-4 flex items-center gap-4 border-2 ${isDark ? 'border-red-500/40' : 'border-red-300'}`}
        style={{
          background: isDark
            ? 'linear-gradient(90deg, rgba(255,0,0,0.08) 0%, rgba(0,0,0,0.4) 100%)'
            : 'linear-gradient(90deg, rgba(239,68,68,0.08) 0%, rgba(248,250,252,0.8) 100%)',
        }}>
        <div className={`w-14 h-14 rounded-xl flex items-center justify-center border ${isDark ? 'bg-red-500/15 border-red-500/30' : 'bg-red-50 border-red-200'}`}>
          <Skull className={`w-7 h-7 ${isDark ? 'text-red-500' : 'text-red-600'}`} />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-3 flex-wrap">
            <span className={`text-lg font-bold font-['Share_Tech_Mono',monospace] tracking-wider ${isDark ? 'text-red-400' : 'text-red-600'}`}
              style={{ textShadow: isDark ? '0 0 12px rgba(255,0,0,0.4)' : '0 0 8px rgba(239,68,68,0.25)' }}>
              {t('machine.attacker_role')}
            </span>
            <span className={`text-xs px-2 py-0.5 rounded-full font-semibold border ${isDark ? 'bg-red-500/20 text-red-400 border-red-500/30' : 'bg-red-50 text-red-700 border-red-200'}`}>
              {t('machine.attacker_label')}
            </span>
          </div>
          <div className={`flex items-center gap-4 mt-1 text-sm font-mono ${isDark ? 'text-slate-400' : 'text-slate-700'}`}>
            <span>{t('machine.ip')}: <span className={isDark ? 'text-red-400' : 'text-red-600'}>{t('machine.attacker_ip')}</span></span>
            <span>{t('machine.os')}: <span className={isDark ? 'text-slate-300' : 'text-slate-800'}>{t('machine.attacker_os')}</span></span>
          </div>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse shadow-[0_0_6px_rgba(255,0,0,0.8)]"></span>
          <span className={`font-['JetBrains_Mono',monospace] font-semibold tracking-wider ${isDark ? 'text-red-400' : 'text-red-600'}`}>ATTACK READY</span>
        </div>
      </div>

      {/* Header with dramatic scanlines */}
      <div className={`relative text-center py-7 px-8 border rounded-sm overflow-hidden ${isDark ? 'border-red-500/15' : 'border-red-200'}`}
        style={{
          background: isDark ? `
            repeating-linear-gradient(0deg, transparent 0px, transparent 2px, rgba(255,0,0,0.03) 2px, rgba(255,0,0,0.03) 4px),
            linear-gradient(180deg, #0a0000 0%, #0d0505 100%)
          ` : `
            repeating-linear-gradient(0deg, transparent 0px, transparent 2px, rgba(239,68,68,0.025) 2px, rgba(239,68,68,0.025) 4px),
            linear-gradient(180deg, #fff5f5 0%, #ffffff 100%)
          `,
        }}>
        {/* Dual scanlines — top fast, bottom slow */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-red-500 to-transparent animate-scanline opacity-80" />
        <div className="absolute top-[40%] left-0 right-0 h-px bg-gradient-to-r from-transparent via-red-500/40 to-transparent animate-scanline" style={{ animationDuration: '4s', animationDelay: '1.4s' }} />
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-red-500/25 to-transparent" />

        {/* CRT vignette */}
        <div className="absolute inset-0 pointer-events-none" style={{
          background: isDark
            ? 'radial-gradient(ellipse at center, transparent 50%, rgba(0,0,0,0.4) 100%)'
            : 'radial-gradient(ellipse at center, transparent 60%, rgba(239,68,68,0.05) 100%)',
        }} />

        <h1 className="relative text-4xl font-extrabold text-red-500 tracking-[0.15em] font-['Share_Tech_Mono',monospace]"
          style={{ textShadow: isDark
            ? '0 0 30px rgba(255,0,0,0.45), 0 0 60px rgba(255,0,0,0.15), 0 0 100px rgba(255,0,0,0.08)'
            : '0 0 18px rgba(239,68,68,0.35), 0 0 40px rgba(239,68,68,0.12)' }}>
          &#9760; {t('attack.title')}
        </h1>
        <div className={`relative text-xs mt-1 tracking-wider font-['JetBrains_Mono',monospace] ${isDark ? 'text-slate-700' : 'text-slate-500'}`}>
          {t('attack.subtitle')}
        </div>
        <div className={`relative inline-block mt-3 px-4 py-1 border rounded-sm font-['JetBrains_Mono',monospace] text-sm tracking-wide ${isDark ? 'bg-[#0a0a0a] border-red-500/20 text-red-400' : 'bg-white border-red-200 text-red-600'}`}>
          <span className={isDark ? 'text-slate-600' : 'text-slate-500'}>{t('attack.target')}:</span> {targetIp}
          &nbsp;&nbsp;<span className={isDark ? 'text-slate-700' : 'text-slate-400'}>|</span>&nbsp;&nbsp;
          <span className={isDark ? 'text-slate-600' : 'text-slate-500'}>{t('attack.status_label')}:</span>{' '}
          {activeCount > 0
            ? <span className={`animate-pulse ${isDark ? 'text-red-500' : 'text-red-600'}`}>{t('attack.status_engaged')}</span>
            : <span className={isDark ? 'text-slate-700' : 'text-slate-500'}>{t('attack.status_standby')}</span>}
        </div>
      </div>

      {/* Config bar */}
      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className={`block text-[11px] font-['JetBrains_Mono',monospace] mb-1 uppercase tracking-wider ${isDark ? 'text-slate-600' : 'text-slate-500'}`}>{t('attack.target_ip')}</label>
          <input
            value={targetIp}
            onChange={(e) => setTargetIp(e.target.value)}
            className={`w-full rounded-sm px-3 py-2 font-['JetBrains_Mono',monospace] text-sm transition-all duration-300 focus:outline-none focus:border-red-500/60 focus:shadow-[0_0_12px_rgba(255,0,0,0.15),inset_0_0_12px_rgba(255,0,0,0.05)] border ${isDark ? 'bg-[#0a0a0a] text-red-400 border-[#1a1a1a]' : 'bg-white text-red-700 border-slate-200'}`}
            placeholder="e.g. 192.168.1.100"
          />
        </div>
        <div>
          <label className={`block text-[11px] font-['JetBrains_Mono',monospace] mb-1 uppercase tracking-wider ${isDark ? 'text-slate-600' : 'text-slate-500'}`}>{t('attack.packet_count')}</label>
          <select
            value={pktCount}
            onChange={(e) => setPktCount(e.target.value)}
            className={`w-full rounded-sm px-3 py-2 font-['JetBrains_Mono',monospace] text-sm appearance-none transition-all duration-300 focus:outline-none focus:border-red-500/60 focus:shadow-[0_0_12px_rgba(255,0,0,0.15),inset_0_0_12px_rgba(255,0,0,0.05)] border ${isDark ? 'bg-[#0a0a0a] text-red-400 border-[#1a1a1a]' : 'bg-white text-red-700 border-slate-200'}`}
          >
            {['10', '50', '100', '500', '1000'].map((v) => (
              <option key={v} value={v}>{v}</option>
            ))}
          </select>
        </div>
        <div className="flex items-end">
          <div className={`text-xs font-['JetBrains_Mono',monospace] pb-2.5 ${isDark ? 'text-slate-700' : 'text-slate-500'}`}>
            {t('attack.active_vectors')}: <span className={`font-bold ${isDark ? 'text-red-400' : 'text-red-600'}`}>{activeCount}/4</span>
          </div>
        </div>
      </div>

      {/* Attack grid 2x2 */}
      <div className="grid grid-cols-2 gap-3">
        {Object.entries(ATTACK_INFO).map(([key, info]) => {
          const isOn = attacks[key] ?? false
          const pktSent = isOn ? rand(800, 9999) : 0
          const sev = SEVERITY_COLORS[info.severity]
          const name = t(info.nameKey)
          const desc = t(info.descKey)
          return (
            <div key={key} className="space-y-2">
              <div
                className={`relative p-4 rounded-sm border transition-all duration-500 overflow-hidden ${
                  isOn
                    ? 'border-transparent animate-pulse-glow-border'
                    : isDark
                      ? 'border-[#1a1a1a] hover:border-red-500/20'
                      : 'border-slate-200 hover:border-red-300'
                }`}
                style={{
                  background: isOn
                    ? isDark
                      ? 'linear-gradient(135deg, #0f0505 0%, #120808 100%)'
                      : 'linear-gradient(135deg, #fff5f5 0%, #ffeaea 100%)'
                    : isDark
                      ? 'linear-gradient(135deg, #0a0a0a 0%, #0f0f0f 100%)'
                      : 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
                  ...(isOn ? {
                    borderImage: 'linear-gradient(135deg, #ff0000, #ff4444, #ff0000) 1',
                    boxShadow: isDark
                      ? '0 0 25px rgba(255,0,0,0.12), 0 0 50px rgba(255,0,0,0.05), inset 0 0 30px rgba(255,0,0,0.04)'
                      : '0 0 20px rgba(239,68,68,0.15), 0 0 40px rgba(239,68,68,0.06), inset 0 0 20px rgba(239,68,68,0.04)',
                  } : {}),
                }}
              >
                {/* Left accent bar */}
                <div className={`absolute top-0 left-0 w-[3px] h-full transition-all duration-500 ${
                  isOn
                    ? 'bg-red-500 shadow-[0_0_10px_rgba(255,0,0,0.8)]'
                    : isDark ? 'bg-[#1a1a1a]' : 'bg-slate-200'
                }`} />

                {/* Badge */}
                <span className={`absolute top-2.5 right-3 text-[10px] font-bold tracking-wider font-['JetBrains_Mono',monospace] px-2 py-0.5 rounded-sm border transition-all duration-500 ${
                  isOn
                    ? isDark
                      ? 'text-red-500 bg-red-500/10 border-red-500/30 animate-pulse-glow'
                      : 'text-red-600 bg-red-50 border-red-300 animate-pulse-glow'
                    : isDark
                      ? 'text-slate-700 border-[#1a1a1a]'
                      : 'text-slate-500 border-slate-200'
                }`}>
                  {isOn ? `\u25cf ${t('attack.active')}` : `\u25cb ${t('attack.idle')}`}
                </span>

                <div className={`font-['Share_Tech_Mono',monospace] text-base font-bold flex items-center gap-2 ${isDark ? 'text-red-400' : 'text-red-600'}`}
                  style={{ textShadow: isDark
                    ? (isOn ? '0 0 12px rgba(255,68,68,0.3)' : '0 0 8px rgba(255,68,68,0.15)')
                    : (isOn ? '0 0 10px rgba(239,68,68,0.25)' : 'none') }}>
                  {name}
                </div>
                <div className={`text-[11px] font-['JetBrains_Mono',monospace] mt-0.5 leading-snug ${isDark ? 'text-slate-600' : 'text-slate-500'}`}>{desc}</div>
                <div className={`text-[10px] font-['JetBrains_Mono',monospace] mt-1.5 flex items-center gap-1.5 ${isDark ? 'text-slate-700' : 'text-slate-500'}`}>
                  {t('attack.port_label')} <span className={`font-medium ${isDark ? 'text-red-400' : 'text-red-600'}`}>{info.port}</span>
                  {' \u00b7 '}{t('attack.tool_label')} <span className={`font-medium ${isDark ? 'text-red-400' : 'text-red-600'}`}>{info.tool}</span>
                  {' \u00b7 '}
                  <span className="inline-flex items-center gap-1">
                    <span className={`inline-block w-1.5 h-1.5 rounded-full ${sev.dot}`} />
                    <span className={`${sev.text} font-bold`}>{info.severity}</span>
                  </span>
                </div>
                <div className={`overflow-hidden transition-all duration-500 ${isOn ? 'max-h-10 opacity-100 mt-1.5' : 'max-h-0 opacity-0 mt-0'}`}>
                  <div className={`text-xs font-['JetBrains_Mono',monospace] ${isDark ? 'text-red-500' : 'text-red-600'}`}
                    style={{ textShadow: isDark ? '0 0 8px rgba(255,0,0,0.3)' : '0 0 6px rgba(239,68,68,0.2)' }}>
                    &#9658; {pktSent.toLocaleString()} {t('attack.packets_sent')} &nbsp;|&nbsp; {rand(80, 600)} {t('attack.pkt_per_sec')}
                  </div>
                </div>
              </div>
              <button
                onClick={() => toggleAttack(key)}
                className={`w-full py-2 rounded-sm text-xs font-['JetBrains_Mono',monospace] font-semibold tracking-wider transition-all duration-300 ${
                  isOn
                    ? isDark
                      ? 'bg-slate-800/50 text-slate-400 border border-slate-700 hover:bg-slate-700/50 hover:text-slate-300'
                      : 'bg-slate-100 text-slate-700 border border-slate-300 hover:bg-slate-200 hover:text-slate-800'
                    : isDark
                      ? 'bg-red-600/80 text-white border border-red-500 hover:bg-red-500 hover:shadow-[0_0_20px_rgba(255,0,0,0.3)]'
                      : 'bg-red-600 text-white border border-red-500 hover:bg-red-700 hover:shadow-[0_0_16px_rgba(239,68,68,0.3)]'
                }`}
              >
                {isOn ? `\u25a0 ${t('attack.stop')} ${name}` : `\u25b6 ${t('attack.launch')} ${name}`}
              </button>
            </div>
          )
        })}
      </div>

      {/* Quick commands */}
      <div>
        <h4 className={`text-xs font-['Share_Tech_Mono',monospace] tracking-wider mb-2 ${isDark ? 'text-red-400' : 'text-red-600'}`}>&gt; {t('attack.quick_commands')}</h4>
        <div className={`rounded-sm p-3 border ${isDark ? 'bg-[#060606] border-[#151515]' : 'bg-slate-50 border-slate-200'}`}>
          <div className={`text-[11px] font-['JetBrains_Mono',monospace] mb-2 ${isDark ? 'text-red-400' : 'text-red-600'}`}>$ {t('attack.fire_forget')}</div>
          <div className="grid grid-cols-5 gap-2">
            {QUICK_CMDS.map((cmd, i) => (
              <div key={i} className="text-center">
                <button
                  onClick={() => quickCmd(cmd.attack, cmd.count, i)}
                  className={`w-full py-2 border rounded-sm text-xs font-['JetBrains_Mono',monospace] transition-all duration-150 ${
                    flashedCmd === i
                      ? isDark
                        ? 'border-red-500 text-red-400 bg-red-500/10 shadow-[0_0_12px_rgba(255,0,0,0.3)]'
                        : 'border-red-500 text-red-700 bg-red-50 shadow-[0_0_10px_rgba(239,68,68,0.25)]'
                      : isDark
                        ? 'bg-[#0a0a0a] border-[#1a1a1a] text-slate-400 hover:border-red-500/40 hover:text-red-400 hover:bg-red-500/5 hover:shadow-[0_0_8px_rgba(255,0,0,0.1)]'
                        : 'bg-white border-slate-200 text-slate-700 hover:border-red-300 hover:text-red-700 hover:bg-red-50 hover:shadow-[0_0_8px_rgba(239,68,68,0.1)]'
                  } active:scale-95`}
                >
                  {cmd.label}
                </button>
                <div className={`text-[10px] mt-1 font-['JetBrains_Mono',monospace] ${isDark ? 'text-slate-700' : 'text-slate-500'}`}>{cmd.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Launch All / Kill All */}
      <div className="grid grid-cols-2 gap-3">
        <button
          onClick={launchAll}
          className={`group relative flex items-center justify-center gap-2 py-3 text-white border border-red-500 rounded-sm font-['JetBrains_Mono',monospace] text-sm font-semibold tracking-wider transition-all duration-300 active:scale-[0.98] ${
            isDark
              ? 'bg-red-600/80 hover:bg-red-500 hover:shadow-[0_0_25px_rgba(255,0,0,0.3)]'
              : 'bg-red-600 hover:bg-red-700 hover:shadow-[0_0_18px_rgba(239,68,68,0.35)]'
          }`}
        >
          <Zap className="w-4 h-4" /> {t('attack.launch_all')}
          <span className="absolute right-3 text-[9px] text-red-300/40 font-normal tracking-normal opacity-0 group-hover:opacity-100 transition-opacity">Ctrl+A</span>
        </button>
        <button
          onClick={killAll}
          className={`group relative flex items-center justify-center gap-2 py-3 rounded-sm font-['JetBrains_Mono',monospace] text-sm font-semibold tracking-wider transition-all duration-300 active:scale-[0.98] border ${
            isDark
              ? 'bg-slate-800/50 hover:bg-slate-700/50 text-slate-300 border-slate-700 hover:shadow-[0_0_15px_rgba(100,116,139,0.1)]'
              : 'bg-white hover:bg-slate-50 text-slate-700 border-slate-300 hover:shadow-[0_0_10px_rgba(100,116,139,0.12)]'
          }`}
        >
          <X className="w-4 h-4" /> {t('attack.kill_all')}
          <span className="absolute right-3 text-[9px] text-slate-500/40 font-normal tracking-normal opacity-0 group-hover:opacity-100 transition-opacity">Ctrl+K</span>
        </button>
      </div>

      {activeCount > 0 && (
        <div className="text-center">
          <span className={`text-xs font-['JetBrains_Mono',monospace] animate-pulse-glow ${isDark ? 'text-red-500' : 'text-red-600'}`}>
            &#9888; {activeCount} {t('attack.attacks_running')}
          </span>
        </div>
      )}

      {/* Terminal */}
      <div>
        <h4 className={`text-xs font-['Share_Tech_Mono',monospace] tracking-wider mb-2 ${isDark ? 'text-red-400' : 'text-red-600'}`}>&gt; {t('attack.live_terminal')}</h4>
        <div className={`border rounded-sm overflow-hidden ${isDark ? 'border-[#1a1a1a]' : 'border-slate-200'}`} style={{ background: isDark ? '#030303' : '#030303' }}>
          {/* Title bar */}
          <div className={`flex items-center gap-2 px-3 py-2 border-b ${isDark ? 'bg-[#0a0a0a] border-[#1a1a1a]' : 'bg-slate-100 border-slate-200'}`}>
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 shadow-[0_0_4px_rgba(255,0,0,0.5)]" />
            <span className="w-2.5 h-2.5 rounded-full bg-yellow-500 shadow-[0_0_4px_rgba(234,179,8,0.5)]" />
            <span className="w-2.5 h-2.5 rounded-full bg-green-500 shadow-[0_0_4px_rgba(34,197,94,0.5)]" />
            <span className={`text-[11px] font-['JetBrains_Mono',monospace] ml-2 ${isDark ? 'text-slate-700' : 'text-slate-500'}`}>
              attack_suite — {activeCount > 0 ? `${targetIp} — ${activeCount} ${t('attack.module')}` : t('attack.terminal_idle')}
            </span>
            {activeCount > 0 && (
              <span className={`ml-auto text-[10px] font-['JetBrains_Mono',monospace] animate-pulse ${isDark ? 'text-red-500/60' : 'text-red-600/80'}`}>{t('attack.rec')}</span>
            )}
          </div>
          {/* Body */}
          <div
            ref={termRef}
            className="relative p-4 max-h-[380px] overflow-y-auto font-['JetBrains_Mono',monospace] text-xs leading-relaxed text-green-500"
            style={{
              textShadow: '0 0 5px rgba(0,255,0,0.2)',
              background: `
                repeating-linear-gradient(0deg, transparent 0px, transparent 2px, rgba(0,255,0,0.008) 2px, rgba(0,255,0,0.008) 4px),
                #030303
              `,
            }}
          >
            {termLines.map((line, i) => (
              <div key={i} className="whitespace-pre-wrap break-all py-px" dangerouslySetInnerHTML={{ __html: line.html }} />
            ))}
          </div>
        </div>
      </div>

      {activeCount > 0 && (
        <div className={`flex items-center gap-2 rounded-md px-4 py-3 text-sm font-['JetBrains_Mono',monospace] border ${isDark ? 'bg-sky-500/10 border-sky-500/20 text-sky-300' : 'bg-sky-50 border-sky-200 text-sky-700'}`}>
          <Terminal className="w-4 h-4" />
          {t('attack.monitor_hint')}
        </div>
      )}

      {/* Keyboard Shortcuts Modal */}
      {showHelp && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
          onClick={() => setShowHelp(false)}
        >
          <div
            className="relative w-full max-w-md mx-4 border border-red-500/30 rounded-sm overflow-hidden"
            style={{
              background: 'linear-gradient(180deg, #0a0505 0%, #0d0808 100%)',
              boxShadow: '0 0 40px rgba(255,0,0,0.15), 0 0 80px rgba(255,0,0,0.05)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Scanline accent */}
            <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-red-500 to-transparent" />

            <div className="p-6">
              <h2
                className="text-xl font-bold text-red-500 font-['Share_Tech_Mono',monospace] tracking-wider mb-1"
                style={{ textShadow: '0 0 20px rgba(255,0,0,0.4)' }}
              >
                {t('attack.shortcuts_title')}
              </h2>
              <div className="h-px bg-gradient-to-r from-red-500/40 via-slate-700 to-transparent mb-5" />

              <div className="space-y-3 font-['JetBrains_Mono',monospace] text-sm">
                {[
                  { keys: 'Ctrl + A', desc: t('attack.shortcut_launch') },
                  { keys: 'Ctrl + K', desc: t('attack.shortcut_kill') },
                  { keys: '?', desc: t('attack.shortcut_help') },
                  { keys: 'Esc', desc: t('attack.shortcut_close') },
                ].map(({ keys, desc }) => (
                  <div key={keys} className="flex items-center justify-between">
                    <kbd className="inline-block px-2.5 py-1 bg-[#151515] border border-red-500/20 rounded-sm text-green-400 text-xs tracking-wider min-w-[90px] text-center">
                      {keys}
                    </kbd>
                    <span className="text-slate-400 text-xs">{desc}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="px-6 pb-4">
              <div className="h-px bg-slate-800 mb-3" />
              <div className="text-[10px] text-slate-700 font-['JetBrains_Mono',monospace] text-center">
                press <span className="text-red-400">Esc</span> or click outside to close
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
