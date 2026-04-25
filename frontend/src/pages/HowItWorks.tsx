import { useState, useEffect, useRef, useCallback } from 'react'
import { Link } from 'react-router-dom'
import {
  Database, Brain, FileBarChart, ArrowRight, Shield, Globe, Cpu, Layers,
  Monitor as MonitorIcon, Skull, Eye, Network, Zap, BookOpen, Target,
  Server, Code2, Boxes, GraduationCap, Sparkles, Gauge, Lock,
  AlertTriangle, CheckCircle2, KeyRound, FileCode2, Package,
  ExternalLink, X, TrendingUp, Calendar, DollarSign,
} from 'lucide-react'
import { useT, useSettings } from '../i18n'

/* ─────────────────────────────────────────────────────────── */
/*  Types                                                      */
/* ─────────────────────────────────────────────────────────── */

type Tab = 'overview' | 'topology' | 'defender' | 'pipeline' | 'dataset' | 'attacks' | 'realcases' | 'tech' | 'benefits' | 'architecture'

interface RealCaseData {
  id: string
  year: number
  attackColor: string
  severity: 'critical' | 'high' | 'medium'
  articleUrl: string
  nameKey: 'rc.dyn.name' | 'rc.github.name' | 'rc.equifax.name' | 'rc.colonial.name' | 'rc.solarwinds.name' | 'rc.mariposa.name' | 'rc.heartbleed.name' | 'rc.shodan.name' | 'rc.heartland.name'
  attackKey: 'rc.dyn.attack' | 'rc.github.attack' | 'rc.equifax.attack' | 'rc.colonial.attack' | 'rc.solarwinds.attack' | 'rc.mariposa.attack' | 'rc.heartbleed.attack' | 'rc.shodan.attack' | 'rc.heartland.attack'
  descKey: 'rc.dyn.desc' | 'rc.github.desc' | 'rc.equifax.desc' | 'rc.colonial.desc' | 'rc.solarwinds.desc' | 'rc.mariposa.desc' | 'rc.heartbleed.desc' | 'rc.shodan.desc' | 'rc.heartland.desc'
  impactKey: 'rc.dyn.impact' | 'rc.github.impact' | 'rc.equifax.impact' | 'rc.colonial.impact' | 'rc.solarwinds.impact' | 'rc.mariposa.impact' | 'rc.heartbleed.impact' | 'rc.shodan.impact' | 'rc.heartland.impact'
  detailKey: 'rc.dyn.detail' | 'rc.github.detail' | 'rc.equifax.detail' | 'rc.colonial.detail' | 'rc.solarwinds.detail' | 'rc.mariposa.detail' | 'rc.heartbleed.detail' | 'rc.shodan.detail' | 'rc.heartland.detail'
}

/* ─────────────────────────────────────────────────────────── */
/*  Static data                                                */
/* ─────────────────────────────────────────────────────────── */

const REAL_CASES: RealCaseData[] = [
  { id: 'dyn',        year: 2016, attackColor: 'red',    severity: 'critical', articleUrl: 'https://en.wikipedia.org/wiki/2016_Dyn_cyberattack',                         nameKey: 'rc.dyn.name',        attackKey: 'rc.dyn.attack',        descKey: 'rc.dyn.desc',        impactKey: 'rc.dyn.impact',        detailKey: 'rc.dyn.detail' },
  { id: 'github',     year: 2018, attackColor: 'red',    severity: 'critical', articleUrl: 'https://github.blog/news-insights/policy-news-and-insights/february-28th-ddos-incident-report/', nameKey: 'rc.github.name',     attackKey: 'rc.github.attack',     descKey: 'rc.github.desc',     impactKey: 'rc.github.impact',     detailKey: 'rc.github.detail' },
  { id: 'equifax',    year: 2017, attackColor: 'orange', severity: 'critical', articleUrl: 'https://en.wikipedia.org/wiki/2017_Equifax_data_breach',                       nameKey: 'rc.equifax.name',    attackKey: 'rc.equifax.attack',    descKey: 'rc.equifax.desc',    impactKey: 'rc.equifax.impact',    detailKey: 'rc.equifax.detail' },
  { id: 'colonial',   year: 2021, attackColor: 'orange', severity: 'critical', articleUrl: 'https://en.wikipedia.org/wiki/Colonial_Pipeline_ransomware_attack',             nameKey: 'rc.colonial.name',   attackKey: 'rc.colonial.attack',   descKey: 'rc.colonial.desc',   impactKey: 'rc.colonial.impact',   detailKey: 'rc.colonial.detail' },
  { id: 'solarwinds', year: 2020, attackColor: 'purple', severity: 'critical', articleUrl: 'https://en.wikipedia.org/wiki/2020_United_States_federal_government_data_breach', nameKey: 'rc.solarwinds.name', attackKey: 'rc.solarwinds.attack', descKey: 'rc.solarwinds.desc', impactKey: 'rc.solarwinds.impact', detailKey: 'rc.solarwinds.detail' },
  { id: 'mariposa',   year: 2010, attackColor: 'violet', severity: 'high',     articleUrl: 'https://en.wikipedia.org/wiki/Mariposa_botnet',                                 nameKey: 'rc.mariposa.name',   attackKey: 'rc.mariposa.attack',   descKey: 'rc.mariposa.desc',   impactKey: 'rc.mariposa.impact',   detailKey: 'rc.mariposa.detail' },
  { id: 'heartbleed', year: 2014, attackColor: 'red',    severity: 'critical', articleUrl: 'https://heartbleed.com',                                                        nameKey: 'rc.heartbleed.name', attackKey: 'rc.heartbleed.attack', descKey: 'rc.heartbleed.desc', impactKey: 'rc.heartbleed.impact', detailKey: 'rc.heartbleed.detail' },
  { id: 'shodan',     year: 2013, attackColor: 'yellow', severity: 'medium',   articleUrl: 'https://www.shodan.io',                                                         nameKey: 'rc.shodan.name',     attackKey: 'rc.shodan.attack',     descKey: 'rc.shodan.desc',     impactKey: 'rc.shodan.impact',     detailKey: 'rc.shodan.detail' },
  { id: 'heartland',  year: 2008, attackColor: 'orange', severity: 'critical', articleUrl: 'https://en.wikipedia.org/wiki/Heartland_Payment_Systems#Data_breach',           nameKey: 'rc.heartland.name',  attackKey: 'rc.heartland.attack',  descKey: 'rc.heartland.desc',  impactKey: 'rc.heartland.impact',  detailKey: 'rc.heartland.detail' },
]

const ATTACK_TYPES = [
  { name: 'BENIGN',                    severity: 'safe',     descKey: 'at.benign' as const },
  { name: 'DDoS',                      severity: 'critical', descKey: 'at.ddos' as const },
  { name: 'PortScan',                  severity: 'medium',   descKey: 'at.portscan' as const },
  { name: 'SSH-Patator',               severity: 'high',     descKey: 'at.ssh' as const },
  { name: 'FTP-Patator',               severity: 'high',     descKey: 'at.ftp' as const },
  { name: 'Bot',                       severity: 'high',     descKey: 'at.bot' as const },
  { name: 'Infiltration',              severity: 'critical', descKey: 'at.infiltration' as const },
  { name: 'Web Attack - Brute Force',  severity: 'high',     descKey: 'at.web_brute' as const },
  { name: 'Web Attack - XSS',          severity: 'high',     descKey: 'at.web_xss' as const },
  { name: 'Web Attack - SQL Injection',severity: 'critical', descKey: 'at.web_sql' as const },
  { name: 'Heartbleed',                severity: 'critical', descKey: 'at.heartbleed' as const },
  { name: 'DoS Hulk',                  severity: 'high',     descKey: 'at.dos_hulk' as const },
  { name: 'DoS GoldenEye',             severity: 'high',     descKey: 'at.dos_goldeneye' as const },
  { name: 'DoS Slowloris',             severity: 'medium',   descKey: 'at.dos_slowloris' as const },
  { name: 'DoS Slowhttptest',          severity: 'medium',   descKey: 'at.dos_slowhttp' as const },
]

const MODEL_METRICS = [
  { key: 'docs.model_accuracy' as const, value: '99.7%', bar: 99.7 },
  { key: 'docs.model_precision' as const, value: '99.6%', bar: 99.6 },
  { key: 'docs.model_recall' as const, value: '99.5%', bar: 99.5 },
  { key: 'docs.model_f1' as const, value: '99.5%', bar: 99.5 },
]

/* ─────────────────────────────────────────────────────────── */
/*  Styles                                                     */
/* ─────────────────────────────────────────────────────────── */

const STYLE_ID = 'howitworks-anims'
const KEYFRAMES = `
@keyframes tab-slide-in {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes flow-dot {
  0%   { opacity: 0; transform: translateX(0%); }
  10%  { opacity: 1; }
  90%  { opacity: 1; }
  100% { opacity: 0; transform: translateX(100%); }
}
@keyframes flow-dot-rev {
  0%   { opacity: 0; transform: translateX(100%); }
  10%  { opacity: 1; }
  90%  { opacity: 1; }
  100% { opacity: 0; transform: translateX(0%); }
}
@keyframes bar-fill {
  from { width: 0%; }
  to   { width: var(--bar-w); }
}
@keyframes count-up {
  from { opacity: 0; transform: scale(0.85); }
  to   { opacity: 1; transform: scale(1); }
}
@keyframes pulse-ring {
  0%   { transform: scale(1);    opacity: 0.6; }
  100% { transform: scale(1.5);  opacity: 0; }
}
@keyframes modal-in {
  from { opacity: 0; transform: scale(0.96) translateY(8px); }
  to   { opacity: 1; transform: scale(1) translateY(0); }
}
@keyframes stagger-in {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}
.tab-content { animation: tab-slide-in 0.3s ease-out both; }
.modal-panel  { animation: modal-in 0.22s cubic-bezier(.22,1,.36,1) both; }
`

function ensureStyles() {
  if (typeof document === 'undefined' || document.getElementById(STYLE_ID)) return
  const el = document.createElement('style')
  el.id = STYLE_ID
  el.textContent = KEYFRAMES
  document.head.appendChild(el)
}

/* ─────────────────────────────────────────────────────────── */
/*  Hooks                                                      */
/* ─────────────────────────────────────────────────────────── */

function useCountUp(target: number, active: boolean, duration = 1200) {
  const [val, setVal] = useState(0)
  useEffect(() => {
    if (!active) { setVal(0); return }
    let start = 0
    const inc = target / (duration / 16)
    const id = setInterval(() => {
      start += inc
      if (start >= target) { setVal(target); clearInterval(id) }
      else setVal(Math.round(start))
    }, 16)
    return () => clearInterval(id)
  }, [active, target, duration])
  return val
}

/* ─────────────────────────────────────────────────────────── */
/*  Case Modal                                                 */
/* ─────────────────────────────────────────────────────────── */

function CaseModal({ c, isDark, onClose }: { c: RealCaseData; isDark: boolean; onClose: () => void }) {
  const t = useT()

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', onKey)
    document.body.style.overflow = 'hidden'
    return () => { document.removeEventListener('keydown', onKey); document.body.style.overflow = '' }
  }, [onClose])

  const severityColor = {
    critical: 'bg-red-500/15 text-red-400 border-red-500/30',
    high:     'bg-orange-500/15 text-orange-400 border-orange-500/30',
    medium:   'bg-yellow-500/15 text-yellow-400 border-yellow-500/30',
  }[c.severity]

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(6px)' }}
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className={`modal-panel relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl border shadow-2xl ${
        isDark ? 'bg-[#0d1424] border-white/[0.1]' : 'bg-white border-slate-200'
      }`}>
        {/* Header */}
        <div className={`sticky top-0 z-10 px-6 pt-5 pb-4 border-b ${isDark ? 'bg-[#0d1424] border-white/[0.07]' : 'bg-white border-slate-100'}`}>
          <button
            onClick={onClose}
            className={`absolute top-4 right-4 p-1.5 rounded-lg transition-colors ${isDark ? 'text-slate-500 hover:text-slate-200 hover:bg-white/[0.06]' : 'text-slate-400 hover:text-slate-700 hover:bg-slate-100'}`}
          >
            <X className="w-4 h-4" />
          </button>

          <div className="flex items-start gap-4 pr-8">
            <div className={`w-12 h-12 rounded-xl shrink-0 flex items-center justify-center ${isDark ? 'bg-red-500/15' : 'bg-red-50'}`}>
              <AlertTriangle className="w-6 h-6 text-red-400" />
            </div>
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2 mb-1">
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider border ${severityColor}`}>
                  {t(c.attackKey)}
                </span>
                <span className={`text-[10px] font-mono flex items-center gap-1 ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
                  <Calendar className="w-3 h-3" />{c.year}
                </span>
              </div>
              <h2 className={`text-lg font-bold leading-tight ${isDark ? 'text-slate-100' : 'text-slate-900'}`}>
                {t(c.nameKey)}
              </h2>
            </div>
          </div>
        </div>

        {/* Body */}
        <div className="px-6 py-5 space-y-5">
          {/* Description */}
          <p className={`text-sm leading-relaxed ${isDark ? 'text-slate-300' : 'text-slate-600'}`}>
            {t(c.descKey)}
          </p>

          {/* Impact box */}
          <div className={`rounded-xl border p-4 flex items-start gap-3 ${isDark ? 'bg-amber-500/5 border-amber-500/20' : 'bg-amber-50 border-amber-200'}`}>
            <DollarSign className={`w-4 h-4 shrink-0 mt-0.5 ${isDark ? 'text-amber-400' : 'text-amber-600'}`} />
            <div>
              <div className={`text-[10px] uppercase tracking-wider font-bold mb-1 ${isDark ? 'text-amber-400/70' : 'text-amber-600/70'}`}>Impact</div>
              <p className={`text-sm font-medium ${isDark ? 'text-amber-200' : 'text-amber-900'}`}>{t(c.impactKey)}</p>
            </div>
          </div>

          {/* Extended detail */}
          <div className={`rounded-xl border p-4 ${isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-slate-50 border-slate-200'}`}>
            <div className={`flex items-center gap-2 text-[10px] uppercase tracking-wider font-bold mb-2 ${isDark ? 'text-emerald-400/70' : 'text-emerald-600/70'}`}>
              <Shield className="w-3.5 h-3.5" />
              How our IDS would catch it
            </div>
            <p className={`text-sm leading-relaxed ${isDark ? 'text-slate-300' : 'text-slate-600'}`}>
              {t(c.detailKey)}
            </p>
          </div>

          {/* Article link */}
          <a
            href={c.articleUrl}
            target="_blank"
            rel="noopener noreferrer"
            className={`flex items-center justify-center gap-2 w-full py-3 px-5 rounded-xl text-sm font-semibold transition-all border ${
              isDark
                ? 'bg-amber-500/10 border-amber-500/30 text-amber-400 hover:bg-amber-500/20 hover:border-amber-500/50'
                : 'bg-amber-50 border-amber-200 text-amber-700 hover:bg-amber-100 hover:border-amber-300'
            }`}
          >
            <ExternalLink className="w-4 h-4" />
            Read Full Article
          </a>
        </div>
      </div>
    </div>
  )
}

/* ─────────────────────────────────────────────────────────── */
/*  Animated Topology Diagram                                  */
/* ─────────────────────────────────────────────────────────── */

function TopologyDiagram({ isDark }: { isDark: boolean }) {
  return (
    <div className={`rounded-xl border p-8 ${isDark ? 'bg-[#0a0f1a] border-amber-500/20' : 'bg-white border-amber-200/60 shadow-sm'}`}>
      <div className="grid grid-cols-3 gap-4 items-center">
        {/* Workstation */}
        <div className={`rounded-xl border-2 p-5 text-center relative ${isDark ? 'border-blue-500/40 bg-blue-500/5' : 'border-blue-300 bg-blue-50/50'}`}>
          <div className="absolute -right-4 top-1/2 -translate-y-1/2 z-10 flex items-center w-8 overflow-hidden">
            <div className="w-3 h-3 rounded-full bg-blue-400 flex-shrink-0"
              style={{ animation: 'flow-dot 2s ease-in-out infinite' }} />
          </div>
          <div className={`inline-flex w-12 h-12 rounded-xl items-center justify-center mb-2 ${isDark ? 'bg-blue-500/15 text-blue-400' : 'bg-blue-100 text-blue-600'}`}>
            <MonitorIcon className="w-6 h-6" />
          </div>
          <div className={`text-xs font-bold uppercase tracking-wider ${isDark ? 'text-blue-400' : 'text-blue-600'}`}>WORKSTATION</div>
          <div className={`text-[10px] font-mono mt-1 ${isDark ? 'text-slate-500' : 'text-slate-500'}`}>192.168.1.10</div>
          <div className={`text-[9px] uppercase tracking-widest mt-2 px-2 py-0.5 rounded-full inline-block ${isDark ? 'bg-blue-500/10 text-blue-400' : 'bg-blue-100 text-blue-700'}`}>Normal User</div>
          <div className={`mt-2 text-[9px] ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>HTTPS · DNS · API</div>
        </div>

        {/* IDS center */}
        <div className={`rounded-xl border-2 p-5 text-center relative ${isDark ? 'border-amber-500/50 bg-amber-500/5 shadow-[0_0_30px_rgba(245,158,11,0.12)]' : 'border-amber-300 bg-amber-50/70'}`}>
          {/* pulse ring */}
          <div className="absolute inset-0 rounded-xl border-2 border-amber-400/30 pointer-events-none"
            style={{ animation: 'pulse-ring 2s ease-out infinite' }} />
          <div className="absolute -top-2 left-1/2 -translate-x-1/2">
            <div className={`px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-widest ${isDark ? 'bg-amber-500 text-black' : 'bg-amber-500 text-white'}`}>
              Monitoring
            </div>
          </div>
          {/* attacker flow dot */}
          <div className="absolute -left-4 top-[60%] -translate-y-1/2 z-10 w-8 overflow-hidden">
            <div className="w-3 h-3 rounded-full bg-red-400 flex-shrink-0"
              style={{ animation: 'flow-dot-rev 2.5s ease-in-out 1s infinite' }} />
          </div>
          <div className={`inline-flex w-12 h-12 rounded-xl items-center justify-center mb-2 relative ${isDark ? 'bg-amber-500/15 text-amber-400' : 'bg-amber-100 text-amber-600'}`}>
            <Shield className="w-6 h-6" />
            <Eye className={`absolute w-3.5 h-3.5 -right-1 -bottom-1 ${isDark ? 'text-amber-300' : 'text-amber-600'}`} />
          </div>
          <div className={`text-xs font-bold uppercase tracking-wider ${isDark ? 'text-amber-400' : 'text-amber-600'}`}>IDS SENSOR</div>
          <div className={`text-[10px] font-mono mt-1 ${isDark ? 'text-slate-500' : 'text-slate-500'}`}>192.168.1.1</div>
          <div className={`text-[9px] uppercase tracking-widest mt-2 px-2 py-0.5 rounded-full inline-block ${isDark ? 'bg-amber-500/10 text-amber-400' : 'bg-amber-100 text-amber-700'}`}>Defender</div>
          <div className={`mt-2 text-[9px] ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>LightGBM · Alerts · Block</div>
        </div>

        {/* Attacker */}
        <div className={`rounded-xl border-2 p-5 text-center relative ${isDark ? 'border-red-500/40 bg-red-500/5' : 'border-red-300 bg-red-50/50'}`}>
          <div className="absolute -left-4 top-1/2 -translate-y-1/2 z-10 w-8 overflow-hidden">
            <div className="w-3 h-3 rounded-full bg-red-400 flex-shrink-0"
              style={{ animation: 'flow-dot-rev 2.5s ease-in-out infinite' }} />
          </div>
          <div className={`inline-flex w-12 h-12 rounded-xl items-center justify-center mb-2 ${isDark ? 'bg-red-500/15 text-red-400' : 'bg-red-100 text-red-600'}`}>
            <Skull className="w-6 h-6" />
          </div>
          <div className={`text-xs font-bold uppercase tracking-wider ${isDark ? 'text-red-400' : 'text-red-600'}`}>ATTACKER</div>
          <div className={`text-[10px] font-mono mt-1 ${isDark ? 'text-slate-500' : 'text-slate-500'}`}>10.0.0.50</div>
          <div className={`text-[9px] uppercase tracking-widest mt-2 px-2 py-0.5 rounded-full inline-block ${isDark ? 'bg-red-500/10 text-red-400' : 'bg-red-100 text-red-700'}`}>Threat Actor</div>
          <div className={`mt-2 text-[9px] ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>Kali · nmap · hydra</div>
        </div>
      </div>

      <div className={`mt-6 pt-5 border-t border-dashed grid grid-cols-2 gap-3 text-xs ${isDark ? 'border-amber-500/15 text-slate-400' : 'border-amber-300/40 text-slate-600'}`}>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-blue-400" />
          <ArrowRight className="w-3 h-3" />
          <div className="w-2 h-2 rounded-full bg-amber-400" />
          <span>Workstation → IDS (legitimate)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-red-400" />
          <ArrowRight className="w-3 h-3" />
          <div className="w-2 h-2 rounded-full bg-amber-400" />
          <span>Attacker → IDS (malicious)</span>
        </div>
      </div>
    </div>
  )
}

/* ─────────────────────────────────────────────────────────── */
/*  Main Component                                             */
/* ─────────────────────────────────────────────────────────── */

export default function HowItWorks() {
  const t = useT()
  const { theme } = useSettings()
  const isDark = theme === 'dark'
  const [tab, setTab] = useState<Tab>('overview')
  const [selectedCase, setSelectedCase] = useState<RealCaseData | null>(null)
  const [overviewActive, setOverviewActive] = useState(false)

  useEffect(ensureStyles, [])

  // Trigger counter animation when overview tab is active
  useEffect(() => {
    if (tab === 'overview') {
      const id = setTimeout(() => setOverviewActive(true), 100)
      return () => clearTimeout(id)
    } else {
      setOverviewActive(false)
    }
  }, [tab])

  const tabs: { id: Tab; label: string; icon: typeof BookOpen }[] = [
    { id: 'overview',      label: t('docs.tab_overview'),     icon: BookOpen },
    { id: 'topology',      label: t('docs.tab_topology'),     icon: Network },
    { id: 'defender',      label: t('docs.tab_defender'),     icon: Shield },
    { id: 'pipeline',      label: t('docs.tab_pipeline'),     icon: Brain },
    { id: 'dataset',       label: t('docs.tab_dataset'),      icon: Database },
    { id: 'attacks',       label: t('docs.tab_attacks'),      icon: Skull },
    { id: 'realcases',     label: t('docs.tab_realcases'),    icon: AlertTriangle },
    { id: 'tech',          label: t('docs.tab_tech'),         icon: Boxes },
    { id: 'benefits',      label: t('docs.tab_benefits'),     icon: Sparkles },
    { id: 'architecture',  label: t('docs.tab_architecture'), icon: Layers },
  ]

  const sev = useCallback((s: string) => {
    switch (s) {
      case 'critical': return isDark ? 'bg-red-500/15 text-red-400 border-red-500/30'    : 'bg-red-50 text-red-600 border-red-200'
      case 'high':     return isDark ? 'bg-orange-500/15 text-orange-400 border-orange-500/30' : 'bg-orange-50 text-orange-600 border-orange-200'
      case 'medium':   return isDark ? 'bg-yellow-500/15 text-yellow-400 border-yellow-500/30' : 'bg-yellow-50 text-yellow-600 border-yellow-200'
      case 'safe':     return isDark ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30' : 'bg-emerald-50 text-emerald-600 border-emerald-200'
      default:         return isDark ? 'bg-slate-500/15 text-slate-400 border-slate-500/30'  : 'bg-slate-50 text-slate-600 border-slate-200'
    }
  }, [isDark])

  const card  = isDark ? 'bg-[#0a0f1a] border-amber-500/20' : 'bg-white border-amber-200/60 shadow-sm'
  const hcard = isDark ? 'bg-[#0a0f1a] border-amber-500/20 hover:border-amber-500/40 transition-colors' : 'bg-white border-amber-200/60 hover:border-amber-300 shadow-sm transition-colors'

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${isDark ? 'bg-amber-500/15 text-amber-400' : 'bg-amber-100 text-amber-600'}`}>
          <BookOpen className="w-6 h-6" />
        </div>
        <div>
          <h1 className={`text-2xl font-bold tracking-tight ${isDark ? 'text-slate-100' : 'text-slate-800'}`}>
            {t('docs.title')}
          </h1>
          <p className={`text-sm mt-0.5 ${isDark ? 'text-slate-500' : 'text-slate-500'}`}>
            {t('docs.subtitle')}
          </p>
        </div>
      </div>

      {/* Tab navigation — horizontal scroll */}
      <div className={`rounded-xl border ${isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-slate-100 border-slate-200'}`}>
        <div className="overflow-x-auto scrollbar-hide">
          <div className="flex gap-0.5 p-1 min-w-max">
            {tabs.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setTab(id)}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium whitespace-nowrap transition-all duration-200 ${
                  tab === id
                    ? isDark
                      ? 'bg-amber-500/15 text-amber-400 shadow-[inset_0_0_0_1px_rgba(245,158,11,0.2)]'
                      : 'bg-white text-amber-600 shadow-sm'
                    : isDark
                      ? 'text-slate-500 hover:text-slate-300 hover:bg-white/[0.03]'
                      : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                <Icon className="w-3.5 h-3.5 shrink-0" />
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ── Tab Content ── */}
      <div key={tab} className="tab-content">

        {/* ══ OVERVIEW ══ */}
        {tab === 'overview' && (
          <div className="space-y-6">
            <div>
              <h2 className={`text-lg font-semibold mb-2 ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>{t('docs.overview_title')}</h2>
              <p className={`text-sm leading-relaxed max-w-4xl ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>{t('docs.overview_intro')}</p>
            </div>

            {/* Problem + Solution */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className={`rounded-xl border p-6 ${card}`}>
                <div className="flex items-center gap-3 mb-3">
                  <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${isDark ? 'bg-red-500/15 text-red-400' : 'bg-red-50 text-red-600'}`}>
                    <AlertTriangle className="w-5 h-5" />
                  </div>
                  <h3 className={`text-base font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>{t('docs.overview_problem')}</h3>
                </div>
                <p className={`text-sm leading-relaxed ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>{t('docs.overview_problem_desc')}</p>
              </div>
              <div className={`rounded-xl border p-6 ${card}`}>
                <div className="flex items-center gap-3 mb-3">
                  <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${isDark ? 'bg-emerald-500/15 text-emerald-400' : 'bg-emerald-50 text-emerald-600'}`}>
                    <CheckCircle2 className="w-5 h-5" />
                  </div>
                  <h3 className={`text-base font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>{t('docs.overview_solution')}</h3>
                </div>
                <p className={`text-sm leading-relaxed ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>{t('docs.overview_solution_desc')}</p>
              </div>
            </div>

            {/* Animated key stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {([
                { val: '99.7%', raw: 997, denom: 10, unit: '%', labelKey: 'stats.detection_accuracy' as const, icon: Target, color: 'amber' },
                { val: '2.8M',  raw: 28,  denom: 10, unit: 'M', labelKey: 'stats.training_flows' as const,     icon: Database, color: 'blue' },
                { val: '15+',   raw: 15,  denom: 1,  unit: '+', labelKey: 'stats.attack_types' as const,       icon: Skull,  color: 'red' },
                { val: '<15ms', raw: 15,  denom: 1,  unit: 'ms',labelKey: 'stats.latency' as const,            icon: Zap,    color: 'emerald' },
              ] as const).map(({ val, labelKey, icon: Icon, color }) => (
                <div key={labelKey} className={`rounded-xl border p-5 text-center ${card}`}
                  style={{ animation: 'count-up 0.5s ease-out both' }}>
                  <Icon className={`w-5 h-5 mx-auto mb-2 text-${color === 'amber' ? 'amber' : color === 'blue' ? 'blue' : color === 'red' ? 'red' : 'emerald'}-500/70`} />
                  <div className={`text-2xl font-bold font-mono text-${color === 'amber' ? 'amber' : color === 'blue' ? 'blue' : color === 'red' ? 'red' : 'emerald'}-${isDark ? '400' : '600'}`}>
                    {overviewActive ? val : '—'}
                  </div>
                  <div className={`text-[10px] mt-1 font-medium uppercase tracking-wider ${isDark ? 'text-slate-500' : 'text-slate-500'}`}>{t(labelKey)}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ══ TOPOLOGY ══ */}
        {tab === 'topology' && (
          <div className="space-y-6">
            <div>
              <h2 className={`text-lg font-semibold mb-2 ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>{t('docs.topology_title')}</h2>
              <p className={`text-sm leading-relaxed max-w-4xl ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>{t('docs.topology_desc')}</p>
            </div>

            <TopologyDiagram isDark={isDark} />

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {([
                { to: '/workspace',  icon: MonitorIcon, title: t('docs.topology_workstation'), role: t('docs.topology_workstation_role'), desc: t('docs.topology_workstation_desc'), color: 'blue' },
                { to: '/attack',     icon: Skull,       title: t('docs.topology_attacker'),    role: t('docs.topology_attacker_role'),    desc: t('docs.topology_attacker_desc'),    color: 'red' },
                { to: '/monitoring', icon: Shield,      title: t('docs.topology_ids'),         role: t('docs.topology_ids_role'),         desc: t('docs.topology_ids_desc'),         color: 'amber' },
              ] as const).map(({ to, icon: Icon, title, role, desc, color }) => (
                <Link key={to} to={to} className={`rounded-xl border p-5 block ${hcard}`}>
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center mb-3 ${
                    color === 'blue' ? (isDark ? 'text-blue-400 bg-blue-500/15' : 'text-blue-600 bg-blue-50') :
                    color === 'red'  ? (isDark ? 'text-red-400 bg-red-500/15'   : 'text-red-600 bg-red-50') :
                    isDark ? 'text-amber-400 bg-amber-500/15' : 'text-amber-600 bg-amber-50'
                  }`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className={`text-[10px] uppercase tracking-wider font-semibold mb-1 ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>{role}</div>
                  <h3 className={`text-sm font-semibold mb-1.5 ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>{title}</h3>
                  <p className={`text-xs leading-relaxed mb-3 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>{desc}</p>
                  <div className={`flex items-center gap-1 text-xs font-mono font-semibold ${isDark ? 'text-amber-400' : 'text-amber-600'}`}>
                    <span>{to}</span><ArrowRight className="w-3 h-3" />
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* ══ DEFENDER ══ */}
        {tab === 'defender' && (
          <div className="space-y-6">
            <div className="flex items-center gap-3">
              <div className={`w-11 h-11 rounded-xl flex items-center justify-center ${isDark ? 'bg-emerald-500/15 text-emerald-400' : 'bg-emerald-50 text-emerald-600'}`}>
                <Shield className="w-6 h-6" />
              </div>
              <div>
                <h2 className={`text-lg font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>{t('docs.defender_title')}</h2>
                <p className={`text-sm mt-0.5 max-w-3xl ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>{t('docs.defender_intro')}</p>
              </div>
            </div>

            {/* Interactive IDS vs IPS comparison */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className={`rounded-xl border-2 p-5 ${isDark ? 'border-slate-700 bg-slate-800/30' : 'border-slate-200 bg-slate-50'}`}>
                <div className={`flex items-center gap-2 mb-3 text-sm font-bold ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                  <Eye className="w-4 h-4" /> IDS — Passive Mode
                </div>
                <div className="space-y-1.5 text-xs">
                  {['Captures all traffic', 'Classifies with ML', 'Generates alerts', '✗ Does NOT block'].map((s, i) => (
                    <div key={i} className={`flex items-center gap-2 ${s.startsWith('✗') ? (isDark ? 'text-red-400' : 'text-red-600') : (isDark ? 'text-slate-400' : 'text-slate-600')}`}>
                      <div className={`w-1.5 h-1.5 rounded-full ${s.startsWith('✗') ? 'bg-red-400' : 'bg-slate-400'}`} />
                      {s.replace('✗ ', '')}
                    </div>
                  ))}
                </div>
              </div>
              <div className={`rounded-xl border-2 p-5 ${isDark ? 'border-emerald-500/40 bg-emerald-500/5' : 'border-emerald-300 bg-emerald-50/60'}`}>
                <div className={`flex items-center gap-2 mb-3 text-sm font-bold ${isDark ? 'text-emerald-400' : 'text-emerald-700'}`}>
                  <Shield className="w-4 h-4" /> IPS — Defender Mode ON
                </div>
                <div className="space-y-1.5 text-xs">
                  {['Captures all traffic', 'Classifies with ML', 'Generates alerts', '✓ Blocks malicious IPs'].map((s, i) => (
                    <div key={i} className={`flex items-center gap-2 ${s.startsWith('✓') ? (isDark ? 'text-emerald-400' : 'text-emerald-700') : (isDark ? 'text-slate-400' : 'text-slate-600')}`}>
                      <div className={`w-1.5 h-1.5 rounded-full ${s.startsWith('✓') ? 'bg-emerald-400' : 'bg-slate-400'}`} />
                      {s.replace('✓ ', '')}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Steps */}
            <div className={`rounded-xl border p-6 ${card}`}>
              <h3 className={`text-sm font-semibold mb-4 ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>{t('docs.defender_how_title')}</h3>
              <ol className="space-y-3">
                {[1, 2, 3, 4].map((n) => (
                  <li key={n} className="flex gap-3"
                    style={{ animation: `stagger-in 0.3s ease-out ${n * 80}ms both` }}>
                    <span className={`shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${isDark ? 'bg-emerald-500/20 text-emerald-400' : 'bg-emerald-100 text-emerald-700'}`}>{n}</span>
                    <p className={`text-sm leading-relaxed ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>{t(`docs.defender_how_${n}` as any)}</p>
                  </li>
                ))}
              </ol>
            </div>

            <div className={`rounded-xl border-l-4 border p-4 flex gap-3 ${isDark ? 'bg-amber-500/5 border-amber-500/20 border-l-amber-500' : 'bg-amber-50 border-amber-200 border-l-amber-500'}`}>
              <AlertTriangle className={`w-5 h-5 shrink-0 ${isDark ? 'text-amber-400' : 'text-amber-600'}`} />
              <p className={`text-sm leading-relaxed ${isDark ? 'text-amber-100/80' : 'text-amber-900/80'}`}>{t('docs.defender_note')}</p>
            </div>
          </div>
        )}

        {/* ══ PIPELINE ══ */}
        {tab === 'pipeline' && (
          <div className="space-y-6">
            <h2 className={`text-lg font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>{t('docs.pipeline_title')}</h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 relative">
              {[
                { step: 1, icon: Database, title: t('docs.step1_title'), desc: t('docs.step1_desc'), color: 'blue' },
                { step: 2, icon: Brain,    title: t('docs.step2_title'), desc: t('docs.step2_desc'), color: 'amber' },
                { step: 3, icon: FileBarChart, title: t('docs.step3_title'), desc: t('docs.step3_desc'), color: 'emerald' },
              ].map(({ step, icon: Icon, title, desc, color }, idx) => (
                <div key={step} className="relative"
                  style={{ animation: `stagger-in 0.35s ease-out ${idx * 120}ms both` }}>
                  <div className={`rounded-xl border p-6 h-full ${hcard}`}>
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center mb-4 text-sm font-bold ${
                      color === 'blue' ? (isDark ? 'bg-blue-500/15 text-blue-400' : 'bg-blue-50 text-blue-600') :
                      color === 'amber' ? (isDark ? 'bg-amber-500/15 text-amber-400' : 'bg-amber-50 text-amber-600') :
                      (isDark ? 'bg-emerald-500/15 text-emerald-400' : 'bg-emerald-50 text-emerald-600')
                    }`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <div className={`text-[10px] uppercase tracking-widest font-bold mb-1 ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>Step {step}</div>
                    <h3 className={`text-sm font-semibold mb-2 ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>{title}</h3>
                    <p className={`text-xs leading-relaxed ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>{desc}</p>
                  </div>
                  {idx < 2 && (
                    <div className="hidden md:flex absolute top-1/2 -right-3 -translate-y-1/2 z-10">
                      <ArrowRight className={`w-5 h-5 ${isDark ? 'text-amber-500/40' : 'text-amber-400'}`} />
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Model metrics with animated bars */}
            <div className={`rounded-xl border p-6 ${card}`}>
              <h3 className={`text-sm font-semibold mb-4 ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>{t('docs.model_title')}</h3>
              <div className="space-y-3">
                {MODEL_METRICS.map(({ key, value, bar }) => (
                  <div key={key}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className={isDark ? 'text-slate-400' : 'text-slate-600'}>{t(key)}</span>
                      <span className={`font-mono font-bold ${isDark ? 'text-amber-400' : 'text-amber-600'}`}>{value}</span>
                    </div>
                    <div className={`h-2 rounded-full overflow-hidden ${isDark ? 'bg-white/[0.05]' : 'bg-slate-100'}`}>
                      <div
                        className={`h-full rounded-full ${isDark ? 'bg-amber-500' : 'bg-amber-400'}`}
                        style={{ '--bar-w': `${bar}%`, animation: 'bar-fill 1s ease-out 0.2s both' } as any}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ══ DATASET ══ */}
        {tab === 'dataset' && (
          <div className="space-y-6">
            <div>
              <h2 className={`text-lg font-semibold mb-2 ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>{t('docs.dataset_title')}</h2>
              <p className={`text-sm leading-relaxed max-w-3xl ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>{t('docs.dataset_desc')}</p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {([
                { labelKey: 'docs.dataset_flows' as const,    val: '2.8M', icon: Layers,  color: 'amber' },
                { labelKey: 'docs.dataset_features' as const, val: '80+',  icon: Cpu,     color: 'blue' },
                { labelKey: 'docs.dataset_days' as const,     val: '5',    icon: Globe,   color: 'emerald' },
                { labelKey: 'docs.dataset_classes' as const,  val: '15',   icon: Shield,  color: 'red' },
              ] as const).map(({ labelKey, val, icon: Icon, color }, i) => (
                <div key={labelKey} className={`rounded-xl border p-5 text-center ${card}`}
                  style={{ animation: `stagger-in 0.3s ease-out ${i * 80}ms both` }}>
                  <Icon className={`w-6 h-6 mx-auto mb-2 text-${color}-${isDark ? '400' : '500'} opacity-70`} />
                  <div className={`text-3xl font-bold font-mono mb-1 text-${color}-${isDark ? '400' : '600'}`}>{val}</div>
                  <div className={`text-[10px] font-semibold uppercase tracking-wider ${isDark ? 'text-slate-500' : 'text-slate-500'}`}>{t(labelKey)}</div>
                </div>
              ))}
            </div>

            {/* Attack classes table */}
            <div className={`rounded-xl border overflow-hidden ${card}`}>
              <div className={`px-5 py-3 border-b flex items-center justify-between ${isDark ? 'border-white/[0.06]' : 'border-slate-100'}`}>
                <h3 className={`text-sm font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>{t('docs.attacks_title')}</h3>
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full ${isDark ? 'bg-amber-500/10 text-amber-400' : 'bg-amber-50 text-amber-700'}`}>15 classes</span>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className={isDark ? 'bg-white/[0.02]' : 'bg-slate-50'}>
                      {['Class', 'Severity', 'Description'].map(h => (
                        <th key={h} className={`text-left px-5 py-2.5 text-[10px] font-semibold uppercase tracking-wider ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {ATTACK_TYPES.map(({ name, severity, descKey }, i) => (
                      <tr key={name} className={`${isDark ? 'border-t border-white/[0.03]' : 'border-t border-slate-100'} ${
                        i % 2 !== 0 ? (isDark ? 'bg-white/[0.01]' : 'bg-slate-50/50') : ''
                      }`}>
                        <td className={`px-5 py-2 font-mono font-medium text-xs ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>{name}</td>
                        <td className="px-5 py-2">
                          <span className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase border ${sev(severity)}`}>{severity}</span>
                        </td>
                        <td className={`px-5 py-2 text-xs ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>{t(descKey)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ══ ATTACKS ══ */}
        {tab === 'attacks' && (
          <div className="space-y-5">
            <h2 className={`text-lg font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>{t('docs.attacks_title')}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {[
                { titleKey: 'docs.attack_ddos' as const, severity: 'critical', icon: Zap,       howKey: 'docs.attack_ddos_how_desc' as const,      detectKey: 'docs.attack_ddos_detect_desc' as const,      ports: ['Any TCP'],          tools: ['hping3','LOIC','Scapy'] },
                { titleKey: 'docs.attack_portscan' as const, severity: 'medium', icon: Target,   howKey: 'docs.attack_portscan_how_desc' as const,   detectKey: 'docs.attack_portscan_detect_desc' as const,  ports: ['1-1024','1-65535'], tools: ['nmap','masscan'] },
                { titleKey: 'docs.attack_ssh' as const,   severity: 'high',    icon: KeyRound,  howKey: 'docs.attack_ssh_how_desc' as const,         detectKey: 'docs.attack_ssh_detect_desc' as const,       ports: ['22 (SSH)'],         tools: ['hydra','patator'] },
                { titleKey: 'docs.attack_ftp' as const,   severity: 'high',    icon: Lock,      howKey: 'docs.attack_ftp_how_desc' as const,         detectKey: 'docs.attack_ftp_detect_desc' as const,       ports: ['21 (FTP)'],         tools: ['medusa','ncrack'] },
              ].map(({ titleKey, severity, icon: Icon, howKey, detectKey, ports, tools }, idx) => (
                <div key={titleKey} className={`rounded-xl border p-6 ${hcard}`}
                  style={{ animation: `stagger-in 0.35s ease-out ${idx * 100}ms both` }}>
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${isDark ? 'bg-red-500/10 text-red-400' : 'bg-red-50 text-red-600'}`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <h3 className={`text-sm font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>{t(titleKey)}</h3>
                    </div>
                    <span className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase border ${sev(severity)}`}>{severity}</span>
                  </div>
                  <div className="space-y-3">
                    <div>
                      <div className={`text-[10px] uppercase tracking-wider font-semibold mb-1 ${isDark ? 'text-red-400/80' : 'text-red-600/80'}`}>{t('docs.attack_ddos_how')}</div>
                      <p className={`text-xs leading-relaxed ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>{t(howKey)}</p>
                    </div>
                    <div>
                      <div className={`text-[10px] uppercase tracking-wider font-semibold mb-1 ${isDark ? 'text-emerald-400/80' : 'text-emerald-600/80'}`}>{t('docs.attack_ddos_detect')}</div>
                      <p className={`text-xs leading-relaxed ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>{t(detectKey)}</p>
                    </div>
                    <div className={`pt-3 border-t grid grid-cols-2 gap-3 ${isDark ? 'border-white/[0.05]' : 'border-slate-100'}`}>
                      {[{ label: 'Ports', items: ports, style: isDark ? 'bg-white/[0.03] text-slate-300 border-white/[0.06]' : 'bg-slate-50 text-slate-700 border-slate-200' },
                        { label: 'Tools', items: tools, style: isDark ? 'bg-amber-500/5 text-amber-400 border-amber-500/20' : 'bg-amber-50 text-amber-700 border-amber-200' }
                      ].map(({ label, items, style }) => (
                        <div key={label}>
                          <div className={`text-[10px] uppercase tracking-wider font-semibold mb-1 ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>{label}</div>
                          <div className="flex flex-wrap gap-1">
                            {items.map(p => <span key={p} className={`inline-block px-2 py-0.5 text-[10px] font-mono rounded border ${style}`}>{p}</span>)}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ══ REAL CASES ══ */}
        {tab === 'realcases' && (
          <div className="space-y-5">
            <div>
              <h2 className={`text-lg font-semibold mb-2 ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>{t('docs.realcases_title')}</h2>
              <p className={`text-sm leading-relaxed max-w-4xl ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>{t('docs.realcases_intro')}</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {REAL_CASES.map((c, idx) => (
                <button
                  key={c.id}
                  onClick={() => setSelectedCase(c)}
                  className={`rounded-xl border p-5 text-left w-full group transition-all duration-200 ${hcard} cursor-pointer`}
                  style={{ animation: `stagger-in 0.3s ease-out ${idx * 60}ms both` }}
                >
                  {/* Top row */}
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <div className="flex items-start gap-3 min-w-0">
                      <div className={`shrink-0 w-8 h-8 rounded-lg flex items-center justify-center mt-0.5 ${
                        c.attackColor === 'red'    ? (isDark ? 'bg-red-500/15 text-red-400' : 'bg-red-50 text-red-600') :
                        c.attackColor === 'orange' ? (isDark ? 'bg-orange-500/15 text-orange-400' : 'bg-orange-50 text-orange-600') :
                        c.attackColor === 'purple' ? (isDark ? 'bg-purple-500/15 text-purple-400' : 'bg-purple-50 text-purple-600') :
                        c.attackColor === 'violet' ? (isDark ? 'bg-violet-500/15 text-violet-400' : 'bg-violet-50 text-violet-600') :
                        isDark ? 'bg-yellow-500/15 text-yellow-400' : 'bg-yellow-50 text-yellow-600'
                      }`}>
                        <AlertTriangle className="w-4 h-4" />
                      </div>
                      <div className="min-w-0">
                        <h3 className={`text-sm font-semibold leading-tight ${isDark ? 'text-slate-100' : 'text-slate-800'}`}>{t(c.nameKey)}</h3>
                        <div className="flex items-center gap-2 mt-1">
                          <span className={`text-[10px] font-mono flex items-center gap-1 ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
                            <Calendar className="w-3 h-3" />{c.year}
                          </span>
                          <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full uppercase tracking-wide border ${sev(c.severity)}`}>
                            {t(c.attackKey)}
                          </span>
                        </div>
                      </div>
                    </div>
                    <ExternalLink className={`w-3.5 h-3.5 shrink-0 mt-1 opacity-0 group-hover:opacity-100 transition-opacity ${isDark ? 'text-amber-400' : 'text-amber-600'}`} />
                  </div>

                  <p className={`text-xs leading-relaxed line-clamp-3 ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
                    {t(c.descKey)}
                  </p>

                  <div className={`mt-3 pt-3 border-t flex items-start gap-2 ${isDark ? 'border-white/[0.05]' : 'border-slate-100'}`}>
                    <TrendingUp className={`w-3.5 h-3.5 shrink-0 mt-px ${isDark ? 'text-amber-400' : 'text-amber-600'}`} />
                    <span className={`text-[11px] leading-relaxed ${isDark ? 'text-amber-400' : 'text-amber-700'}`}>{t(c.impactKey)}</span>
                  </div>

                  <div className={`mt-2 text-[10px] font-medium flex items-center gap-1 ${isDark ? 'text-slate-600 group-hover:text-amber-400' : 'text-slate-400 group-hover:text-amber-600'} transition-colors`}>
                    Click to read full analysis →
                  </div>
                </button>
              ))}
            </div>

            <div className={`rounded-xl border-l-4 border p-4 flex gap-3 ${isDark ? 'bg-emerald-500/5 border-emerald-500/20 border-l-emerald-500' : 'bg-emerald-50 border-emerald-200 border-l-emerald-500'}`}>
              <CheckCircle2 className={`w-5 h-5 shrink-0 ${isDark ? 'text-emerald-400' : 'text-emerald-600'}`} />
              <p className={`text-sm leading-relaxed ${isDark ? 'text-emerald-100/80' : 'text-emerald-900/80'}`}>{t('docs.realcases_footer')}</p>
            </div>
          </div>
        )}

        {/* ══ TECH ══ */}
        {tab === 'tech' && (
          <div className="space-y-5">
            <h2 className={`text-lg font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>{t('docs.tech_title')}</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {([
                { titleKey: 'docs.tech_frontend' as const, icon: Code2,   color: 'blue',   items: [['React 19','UI library'],['TypeScript','Type-safe JS'],['Vite','Build tool'],['Tailwind CSS','Styling'],['Recharts','Visualization'],['Lucide Icons','Icon set']] },
                { titleKey: 'docs.tech_backend' as const,  icon: Server,  color: 'emerald',items: [['FastAPI','Web framework'],['Python 3.11','Runtime'],['Uvicorn','ASGI server'],['WebSockets','Real-time'],['psutil','Sys metrics'],['pandas','Data ops']] },
                { titleKey: 'docs.tech_ml' as const,       icon: Brain,   color: 'amber',  items: [['LightGBM','Classifier'],['scikit-learn','ML utils'],['joblib','Model I/O'],['NumPy','Numerics'],['PyTorch','Autoencoder'],['CICIDS2017','Dataset']] },
                { titleKey: 'docs.tech_deploy' as const,   icon: Package, color: 'purple', items: [['Docker','Containers'],['Compose','Orchestration'],['Caddy','Reverse proxy'],['Auto HTTPS','TLS certs'],['Ubuntu','Host OS'],['Linux','Foundation']] },
              ] as const).map(({ titleKey, icon: Icon, color, items }, ci) => (
                <div key={titleKey} className={`rounded-xl border p-5 ${card}`}
                  style={{ animation: `stagger-in 0.35s ease-out ${ci * 80}ms both` }}>
                  <div className={`flex items-center gap-2 mb-4`}>
                    <div className={`w-9 h-9 rounded-lg flex items-center justify-center text-${color}-${isDark?'400':'600'} bg-${color}-${isDark?'500/15':'50'}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <h3 className={`text-sm font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>{t(titleKey)}</h3>
                  </div>
                  <div className="space-y-1.5">
                    {items.map(([name, desc]) => (
                      <div key={name} className={`rounded-lg px-3 py-2 flex items-center justify-between group hover:scale-[1.02] transition-transform ${isDark ? 'bg-white/[0.02] hover:bg-white/[0.04]' : 'bg-slate-50 hover:bg-slate-100'}`}>
                        <span className={`text-xs font-mono font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>{name}</span>
                        <span className={`text-[10px] ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>{desc}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ══ BENEFITS ══ */}
        {tab === 'benefits' && (
          <div className="space-y-5">
            <h2 className={`text-lg font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>{t('docs.benefits_title')}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {([
                { titleKey: 'docs.benefit_accuracy' as const,    descKey: 'docs.benefit_accuracy_desc' as const,    icon: Target,        color: 'emerald', pct: 99.7 },
                { titleKey: 'docs.benefit_realtime' as const,    descKey: 'docs.benefit_realtime_desc' as const,    icon: Zap,           color: 'amber',   pct: 100 },
                { titleKey: 'docs.benefit_educational' as const, descKey: 'docs.benefit_educational_desc' as const, icon: GraduationCap, color: 'blue',    pct: 85 },
                { titleKey: 'docs.benefit_extensible' as const,  descKey: 'docs.benefit_extensible_desc' as const,  icon: Boxes,         color: 'purple',  pct: 90 },
                { titleKey: 'docs.benefit_openSource' as const,  descKey: 'docs.benefit_openSource_desc' as const,  icon: Gauge,         color: 'cyan',    pct: 100 },
                { titleKey: 'docs.benefit_modern' as const,      descKey: 'docs.benefit_modern_desc' as const,      icon: Sparkles,      color: 'rose',    pct: 95 },
              ] as const).map(({ titleKey, descKey, icon: Icon, color, pct }, i) => (
                <div key={titleKey} className={`rounded-xl border p-5 ${hcard}`}
                  style={{ animation: `stagger-in 0.3s ease-out ${i * 80}ms both` }}>
                  <div className={`w-11 h-11 rounded-lg flex items-center justify-center mb-3 text-${color}-${isDark?'400':'600'} bg-${color}-${isDark?'500/15':'50'}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <h3 className={`text-sm font-semibold mb-1.5 ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>{t(titleKey)}</h3>
                  <p className={`text-xs leading-relaxed mb-3 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>{t(descKey)}</p>
                  <div className={`h-1.5 rounded-full overflow-hidden ${isDark ? 'bg-white/[0.05]' : 'bg-slate-100'}`}>
                    <div
                      className={`h-full rounded-full bg-${color}-${isDark ? '500' : '400'}`}
                      style={{ '--bar-w': `${pct}%`, animation: 'bar-fill 1s ease-out 0.3s both' } as any}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ══ ARCHITECTURE ══ */}
        {tab === 'architecture' && (
          <div className="space-y-5">
            <h2 className={`text-lg font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>{t('docs.arch_title')}</h2>

            {/* Visual layer diagram */}
            <div className="space-y-2">
              {([
                { labelKey: 'arch.frontend_layer' as const, icon: Code2,   items: ['React 19', 'TypeScript', 'Tailwind CSS', 'Recharts', 'WebSocket client'], color: 'blue' },
                { labelKey: 'arch.backend_layer' as const,  icon: Server,  items: ['FastAPI', 'Uvicorn', 'WebSocket server', 'REST API', 'psutil'], color: 'emerald' },
                { labelKey: 'arch.ml_layer' as const,       icon: Brain,   items: ['LightGBM classifier', '74 CICIDS2017 features', '15 attack classes', '99.7% accuracy'], color: 'amber' },
              ] as const).map(({ labelKey, icon: Icon, items, color }, i) => (
                <div key={labelKey} className={`rounded-xl border p-4 flex items-center gap-4 ${hcard}`}
                  style={{ animation: `stagger-in 0.3s ease-out ${i * 100}ms both` }}>
                  <div className={`shrink-0 w-10 h-10 rounded-lg flex items-center justify-center text-${color}-${isDark?'400':'600'} bg-${color}-${isDark?'500/15':'50'}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className={`text-xs font-semibold uppercase tracking-wider mb-2 ${isDark ? `text-${color}-400` : `text-${color}-600`}`}>{t(labelKey)}</div>
                    <div className="flex flex-wrap gap-1.5">
                      {items.map(item => (
                        <span key={item} className={`text-[10px] font-mono px-2 py-0.5 rounded border ${isDark ? 'bg-white/[0.03] text-slate-300 border-white/[0.07]' : 'bg-slate-50 text-slate-700 border-slate-200'}`}>
                          {item}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}

              {/* Connecting arrows */}
              <div className="flex justify-center gap-2 py-1">
                {[0, 1].map(i => (
                  <ArrowRight key={i} className={`w-4 h-4 rotate-90 ${isDark ? 'text-amber-500/40' : 'text-amber-400'}`} />
                ))}
              </div>
            </div>

            {/* ASCII diagram */}
            <div className={`rounded-xl border p-6 font-mono text-[11px] leading-relaxed overflow-x-auto ${isDark ? 'bg-[#0a0f1a] border-amber-500/20' : 'bg-slate-50 border-slate-200'}`}>
              <pre className={isDark ? 'text-slate-400' : 'text-slate-600'}>{`
  ┌──────────────┐     HTTP/WS      ┌──────────────────┐
  │   React UI   │ ◄──────────────► │    FastAPI        │
  │  Dashboard   │   REST + WS      │    Backend        │
  └──────────────┘                  └────────┬─────────┘
                                             │ /predict
                                    ┌────────▼─────────┐
                                    │    ML Engine      │
                                    │   (LightGBM)     │
                                    └────────┬─────────┘
                                             │
                                    ┌────────▼─────────┐
                                    │  lgbm_model.pkl  │
                                    └──────────────────┘

  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │  Capture │─►│  Flow    │─►│ Feature  │─►│LightGBM  │
  │ (packets)│  │ Aggreg.  │  │ Extract. │  │Classifier│
  └──────────┘  └──────────┘  └──────────┘  └──────────┘
`}</pre>
            </div>
          </div>
        )}

      </div>{/* end tab-content */}

      {/* Case Modal */}
      {selectedCase && (
        <CaseModal
          c={selectedCase}
          isDark={isDark}
          onClose={() => setSelectedCase(null)}
        />
      )}
    </div>
  )
}
