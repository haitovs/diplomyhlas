import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Database, Brain, FileBarChart, ArrowRight, Shield, Globe, Cpu, Layers,
  Monitor as MonitorIcon, Skull, Eye, Network, Zap, BookOpen, Target,
  Server, Code2, Boxes, GraduationCap, Sparkles, Gauge, Lock,
  AlertTriangle, CheckCircle2, KeyRound, FileCode2, Package,
} from 'lucide-react'
import { useT, useSettings } from '../i18n'

type Tab = 'overview' | 'topology' | 'pipeline' | 'dataset' | 'attacks' | 'tech' | 'benefits' | 'architecture'

const ATTACK_TYPES = [
  { name: 'BENIGN', severity: 'safe', desc: 'Normal network traffic with no malicious intent' },
  { name: 'DDoS', severity: 'critical', desc: 'Distributed Denial of Service flood attack' },
  { name: 'PortScan', severity: 'medium', desc: 'Sequential port probing for service discovery' },
  { name: 'SSH-Patator', severity: 'high', desc: 'SSH brute-force credential stuffing attack' },
  { name: 'FTP-Patator', severity: 'high', desc: 'FTP brute-force login attempt' },
  { name: 'Bot', severity: 'high', desc: 'Botnet command-and-control traffic patterns' },
  { name: 'Infiltration', severity: 'critical', desc: 'Network infiltration and lateral movement' },
  { name: 'Web Attack - Brute Force', severity: 'high', desc: 'HTTP authentication brute-force attack' },
  { name: 'Web Attack - XSS', severity: 'high', desc: 'Cross-site scripting injection via HTTP' },
  { name: 'Web Attack - SQL Injection', severity: 'critical', desc: 'SQL injection via crafted HTTP parameters' },
  { name: 'Heartbleed', severity: 'critical', desc: 'OpenSSL TLS heartbeat buffer over-read exploit' },
  { name: 'DoS Hulk', severity: 'high', desc: 'HTTP flood using unique URL parameters' },
  { name: 'DoS GoldenEye', severity: 'high', desc: 'HTTP Keep-Alive denial of service attack' },
  { name: 'DoS Slowloris', severity: 'medium', desc: 'Slow HTTP headers to exhaust connections' },
  { name: 'DoS Slowhttptest', severity: 'medium', desc: 'Slow HTTP POST body denial of service' },
]

const MODEL_METRICS = [
  { key: 'docs.model_accuracy' as const, value: '99.7%' },
  { key: 'docs.model_precision' as const, value: '99.6%' },
  { key: 'docs.model_recall' as const, value: '99.5%' },
  { key: 'docs.model_f1' as const, value: '99.5%' },
]

export default function HowItWorks() {
  const t = useT()
  const { theme } = useSettings()
  const isDark = theme === 'dark'
  const [tab, setTab] = useState<Tab>('overview')

  const tabs: { id: Tab; label: string; icon: typeof BookOpen }[] = [
    { id: 'overview', label: t('docs.tab_overview'), icon: BookOpen },
    { id: 'topology', label: t('docs.tab_topology'), icon: Network },
    { id: 'pipeline', label: t('docs.tab_pipeline'), icon: Brain },
    { id: 'dataset', label: t('docs.tab_dataset'), icon: Database },
    { id: 'attacks', label: t('docs.tab_attacks'), icon: Skull },
    { id: 'tech', label: t('docs.tab_tech'), icon: Boxes },
    { id: 'benefits', label: t('docs.tab_benefits'), icon: Sparkles },
    { id: 'architecture', label: t('docs.tab_architecture'), icon: Layers },
  ]

  const severityColor = (sev: string) => {
    switch (sev) {
      case 'critical': return isDark ? 'bg-red-500/15 text-red-400 border-red-500/30' : 'bg-red-50 text-red-600 border-red-200'
      case 'high': return isDark ? 'bg-orange-500/15 text-orange-400 border-orange-500/30' : 'bg-orange-50 text-orange-600 border-orange-200'
      case 'medium': return isDark ? 'bg-yellow-500/15 text-yellow-400 border-yellow-500/30' : 'bg-yellow-50 text-yellow-600 border-yellow-200'
      case 'safe': return isDark ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30' : 'bg-emerald-50 text-emerald-600 border-emerald-200'
      default: return isDark ? 'bg-slate-500/15 text-slate-400 border-slate-500/30' : 'bg-slate-50 text-slate-600 border-slate-200'
    }
  }

  const cardClass = isDark
    ? 'bg-[#0a0f1a] border-amber-500/20'
    : 'bg-white border-amber-200/60 shadow-sm'

  const hoverCardClass = isDark
    ? 'bg-[#0a0f1a] border-amber-500/20 hover:border-amber-500/40'
    : 'bg-white border-amber-200/60 hover:border-amber-300 shadow-sm'

  return (
    <div className="space-y-6">
        {/* Header */}
        <div className="mb-8 flex items-center gap-3">
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
            isDark ? 'bg-amber-500/15 text-amber-400' : 'bg-amber-100 text-amber-600'
          }`}>
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

        {/* Tab navigation */}
        <div className={`flex flex-wrap gap-1 p-1 rounded-xl mb-8 ${isDark ? 'bg-white/[0.03] border border-white/[0.06]' : 'bg-slate-100 border border-slate-200'}`}>
          {tabs.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setTab(id)}
              className={`flex-1 min-w-[110px] flex items-center justify-center gap-1.5 px-3 py-2.5 rounded-lg text-xs font-medium transition-all duration-200 ${
                tab === id
                  ? isDark
                    ? 'bg-amber-500/15 text-amber-400 shadow-[inset_0_0_0_1px_rgba(245,158,11,0.2)]'
                    : 'bg-white text-amber-600 shadow-sm'
                  : isDark
                    ? 'text-slate-500 hover:text-slate-300'
                    : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              {label}
            </button>
          ))}
        </div>

        {/* Overview tab */}
        {tab === 'overview' && (
          <div className="space-y-8">
            <div>
              <h2 className={`text-lg font-semibold mb-3 ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
                {t('docs.overview_title')}
              </h2>
              <p className={`text-sm leading-relaxed max-w-4xl ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
                {t('docs.overview_intro')}
              </p>
            </div>

            {/* Problem + Solution */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div className={`rounded-xl border p-6 ${cardClass}`}>
                <div className="flex items-center gap-3 mb-3">
                  <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${isDark ? 'bg-red-500/15 text-red-400' : 'bg-red-50 text-red-600'}`}>
                    <AlertTriangle className="w-5 h-5" />
                  </div>
                  <h3 className={`text-base font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
                    {t('docs.overview_problem')}
                  </h3>
                </div>
                <p className={`text-sm leading-relaxed ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                  {t('docs.overview_problem_desc')}
                </p>
              </div>

              <div className={`rounded-xl border p-6 ${cardClass}`}>
                <div className="flex items-center gap-3 mb-3">
                  <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${isDark ? 'bg-emerald-500/15 text-emerald-400' : 'bg-emerald-50 text-emerald-600'}`}>
                    <CheckCircle2 className="w-5 h-5" />
                  </div>
                  <h3 className={`text-base font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
                    {t('docs.overview_solution')}
                  </h3>
                </div>
                <p className={`text-sm leading-relaxed ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                  {t('docs.overview_solution_desc')}
                </p>
              </div>
            </div>

            {/* Key stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { val: '99.7%', label: 'Detection Accuracy', icon: Target },
                { val: '2.8M', label: 'Training Flows', icon: Database },
                { val: '15+', label: 'Attack Types', icon: Skull },
                { val: '<15ms', label: 'Latency', icon: Zap },
              ].map(({ val, label, icon: Icon }) => (
                <div key={label} className={`rounded-xl border p-5 text-center ${cardClass}`}>
                  <Icon className={`w-5 h-5 mx-auto mb-2 ${isDark ? 'text-amber-500/60' : 'text-amber-500'}`} />
                  <div className={`text-2xl font-bold font-mono ${isDark ? 'text-amber-400' : 'text-amber-600'}`}>
                    {val}
                  </div>
                  <div className={`text-[11px] mt-1 font-medium uppercase tracking-wider ${isDark ? 'text-slate-500' : 'text-slate-500'}`}>
                    {label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Topology tab */}
        {tab === 'topology' && (
          <div className="space-y-8">
            <div>
              <h2 className={`text-lg font-semibold mb-3 ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
                {t('docs.topology_title')}
              </h2>
              <p className={`text-sm leading-relaxed max-w-4xl ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
                {t('docs.topology_desc')}
              </p>
            </div>

            {/* Network diagram */}
            <div className={`rounded-xl border p-8 ${cardClass}`}>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-center relative">
                {/* Workstation */}
                <div className={`relative rounded-xl border-2 p-6 text-center ${
                  isDark ? 'border-blue-500/40 bg-blue-500/5' : 'border-blue-300 bg-blue-50/50'
                }`}>
                  <div className={`inline-flex w-14 h-14 rounded-xl items-center justify-center mb-3 ${
                    isDark ? 'bg-blue-500/15 text-blue-400' : 'bg-blue-100 text-blue-600'
                  }`}>
                    <MonitorIcon className="w-7 h-7" />
                  </div>
                  <div className={`text-sm font-bold uppercase tracking-wider mb-1 ${isDark ? 'text-blue-400' : 'text-blue-600'}`}>
                    WORKSTATION
                  </div>
                  <div className={`text-xs font-mono mb-2 ${isDark ? 'text-slate-500' : 'text-slate-500'}`}>
                    192.168.1.10
                  </div>
                  <div className={`text-[10px] uppercase tracking-widest font-semibold px-2 py-0.5 inline-block rounded-full ${
                    isDark ? 'bg-blue-500/10 text-blue-400' : 'bg-blue-100 text-blue-700'
                  }`}>
                    Normal User
                  </div>
                  <div className={`mt-3 text-[10px] ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
                    HTTPS · DNS · API
                  </div>
                </div>

                {/* IDS Sensor (center) */}
                <div className={`relative rounded-xl border-2 p-6 text-center ${
                  isDark ? 'border-amber-500/50 bg-amber-500/5 shadow-[0_0_40px_rgba(245,158,11,0.15)]' : 'border-amber-300 bg-amber-50/70 shadow-[0_0_40px_rgba(245,158,11,0.15)]'
                }`}>
                  <div className="absolute -top-2 left-1/2 -translate-x-1/2">
                    <div className={`px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-widest ${
                      isDark ? 'bg-amber-500 text-black' : 'bg-amber-500 text-white'
                    }`}>
                      Monitoring
                    </div>
                  </div>
                  <div className={`inline-flex w-14 h-14 rounded-xl items-center justify-center mb-3 relative ${
                    isDark ? 'bg-amber-500/15 text-amber-400' : 'bg-amber-100 text-amber-600'
                  }`}>
                    <Shield className="w-7 h-7" />
                    <div className="absolute -right-1 -bottom-1">
                      <Eye className={`w-4 h-4 ${isDark ? 'text-amber-300' : 'text-amber-600'}`} />
                    </div>
                  </div>
                  <div className={`text-sm font-bold uppercase tracking-wider mb-1 ${isDark ? 'text-amber-400' : 'text-amber-600'}`}>
                    IDS SENSOR
                  </div>
                  <div className={`text-xs font-mono mb-2 ${isDark ? 'text-slate-500' : 'text-slate-500'}`}>
                    192.168.1.1
                  </div>
                  <div className={`text-[10px] uppercase tracking-widest font-semibold px-2 py-0.5 inline-block rounded-full ${
                    isDark ? 'bg-amber-500/10 text-amber-400' : 'bg-amber-100 text-amber-700'
                  }`}>
                    Defender
                  </div>
                  <div className={`mt-3 text-[10px] ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
                    LightGBM · Alerts · Block
                  </div>
                </div>

                {/* Attacker */}
                <div className={`relative rounded-xl border-2 p-6 text-center ${
                  isDark ? 'border-red-500/40 bg-red-500/5' : 'border-red-300 bg-red-50/50'
                }`}>
                  <div className={`inline-flex w-14 h-14 rounded-xl items-center justify-center mb-3 ${
                    isDark ? 'bg-red-500/15 text-red-400' : 'bg-red-100 text-red-600'
                  }`}>
                    <Skull className="w-7 h-7" />
                  </div>
                  <div className={`text-sm font-bold uppercase tracking-wider mb-1 ${isDark ? 'text-red-400' : 'text-red-600'}`}>
                    ATTACKER
                  </div>
                  <div className={`text-xs font-mono mb-2 ${isDark ? 'text-slate-500' : 'text-slate-500'}`}>
                    10.0.0.50
                  </div>
                  <div className={`text-[10px] uppercase tracking-widest font-semibold px-2 py-0.5 inline-block rounded-full ${
                    isDark ? 'bg-red-500/10 text-red-400' : 'bg-red-100 text-red-700'
                  }`}>
                    Threat Actor
                  </div>
                  <div className={`mt-3 text-[10px] ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
                    Kali Linux · nmap · hydra
                  </div>
                </div>
              </div>

              {/* Traffic arrows */}
              <div className="mt-8 pt-6 border-t border-dashed grid grid-cols-1 md:grid-cols-2 gap-4 text-xs"
                style={{ borderColor: isDark ? 'rgba(245,158,11,0.15)' : 'rgba(245,158,11,0.3)' }}>
                <div className={`flex items-center gap-2 ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
                  <div className="flex items-center gap-1">
                    <div className={`w-3 h-3 rounded-full ${isDark ? 'bg-blue-400' : 'bg-blue-500'}`} />
                    <ArrowRight className="w-3 h-3" />
                    <div className={`w-3 h-3 rounded-full ${isDark ? 'bg-amber-400' : 'bg-amber-500'}`} />
                  </div>
                  <span>Workstation → IDS (legitimate traffic)</span>
                </div>
                <div className={`flex items-center gap-2 ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
                  <div className="flex items-center gap-1">
                    <div className={`w-3 h-3 rounded-full ${isDark ? 'bg-red-400' : 'bg-red-500'}`} />
                    <ArrowRight className="w-3 h-3" />
                    <div className={`w-3 h-3 rounded-full ${isDark ? 'bg-amber-400' : 'bg-amber-500'}`} />
                  </div>
                  <span>Attacker → IDS (malicious traffic)</span>
                </div>
              </div>
            </div>

            {/* Role cards with links */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                { to: '/workspace', icon: MonitorIcon, title: t('docs.topology_workstation'), role: t('docs.topology_workstation_role'), desc: t('docs.topology_workstation_desc'), color: 'blue' as const },
                { to: '/attack', icon: Skull, title: t('docs.topology_attacker'), role: t('docs.topology_attacker_role'), desc: t('docs.topology_attacker_desc'), color: 'red' as const },
                { to: '/monitoring', icon: Shield, title: t('docs.topology_ids'), role: t('docs.topology_ids_role'), desc: t('docs.topology_ids_desc'), color: 'amber' as const },
              ].map(({ to, icon: Icon, title, role, desc, color }) => {
                const colorMap = {
                  blue: isDark ? 'text-blue-400 bg-blue-500/15' : 'text-blue-600 bg-blue-50',
                  red: isDark ? 'text-red-400 bg-red-500/15' : 'text-red-600 bg-red-50',
                  amber: isDark ? 'text-amber-400 bg-amber-500/15' : 'text-amber-600 bg-amber-50',
                }
                return (
                  <Link key={to} to={to} className={`rounded-xl border p-5 transition-colors block ${hoverCardClass}`}>
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center mb-3 ${colorMap[color]}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <div className={`text-xs uppercase tracking-wider font-semibold mb-1 ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
                      {role}
                    </div>
                    <h3 className={`text-base font-semibold mb-2 ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
                      {title}
                    </h3>
                    <p className={`text-xs leading-relaxed mb-3 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                      {desc}
                    </p>
                    <div className={`flex items-center gap-1 text-xs font-mono font-semibold ${isDark ? 'text-amber-400' : 'text-amber-600'}`}>
                      <span>Open {to}</span>
                      <ArrowRight className="w-3 h-3" />
                    </div>
                  </Link>
                )
              })}
            </div>
          </div>
        )}

        {/* Pipeline tab */}
        {tab === 'pipeline' && (
          <div className="space-y-8">
            <h2 className={`text-lg font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
              {t('docs.pipeline_title')}
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[
                { step: 1, icon: Database, title: t('docs.step1_title'), desc: t('docs.step1_desc') },
                { step: 2, icon: Brain, title: t('docs.step2_title'), desc: t('docs.step2_desc') },
                { step: 3, icon: FileBarChart, title: t('docs.step3_title'), desc: t('docs.step3_desc') },
              ].map(({ step, icon: Icon, title, desc }, idx) => (
                <div key={step} className="relative">
                  <div className={`rounded-xl border p-6 h-full transition-colors ${hoverCardClass}`}>
                    <div className="flex items-center gap-3 mb-4">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-sm font-bold ${
                        isDark ? 'bg-amber-500/15 text-amber-400' : 'bg-amber-50 text-amber-600'
                      }`}>
                        {step}
                      </div>
                      <Icon className={`w-5 h-5 ${isDark ? 'text-amber-500/60' : 'text-amber-500'}`} />
                    </div>
                    <h3 className={`text-base font-semibold mb-2 ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
                      {title}
                    </h3>
                    <p className={`text-sm leading-relaxed ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                      {desc}
                    </p>
                  </div>
                  {idx < 2 && (
                    <div className="hidden md:flex absolute top-1/2 -right-3 -translate-y-1/2 z-10">
                      <ArrowRight className={`w-5 h-5 ${isDark ? 'text-amber-500/40' : 'text-amber-400'}`} />
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Model Performance */}
            <div className="mt-10">
              <h2 className={`text-lg font-semibold mb-4 ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
                {t('docs.model_title')}
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {MODEL_METRICS.map(({ key, value }) => (
                  <div key={key} className={`rounded-xl border p-5 text-center transition-colors ${cardClass}`}>
                    <div className={`text-2xl font-bold font-mono ${isDark ? 'text-amber-400' : 'text-amber-600'}`}>
                      {value}
                    </div>
                    <div className={`text-xs mt-1 font-medium ${isDark ? 'text-slate-500' : 'text-slate-500'}`}>
                      {t(key)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Dataset tab */}
        {tab === 'dataset' && (
          <div className="space-y-8">
            <h2 className={`text-lg font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
              {t('docs.dataset_title')}
            </h2>

            <p className={`text-sm leading-relaxed max-w-3xl ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
              {t('docs.dataset_desc')}
            </p>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: t('docs.dataset_flows'), icon: Layers },
                { label: t('docs.dataset_features'), icon: Cpu },
                { label: t('docs.dataset_days'), icon: Globe },
                { label: t('docs.dataset_classes'), icon: Shield },
              ].map(({ label, icon: Icon }) => (
                <div key={label} className={`rounded-xl border p-5 text-center transition-colors ${cardClass}`}>
                  <Icon className={`w-6 h-6 mx-auto mb-2 ${isDark ? 'text-amber-500/60' : 'text-amber-500'}`} />
                  <div className={`text-sm font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
                    {label}
                  </div>
                </div>
              ))}
            </div>

            <div className={`rounded-xl border overflow-hidden ${cardClass}`}>
              <div className={`px-5 py-3 border-b ${isDark ? 'border-white/[0.06]' : 'border-slate-100'}`}>
                <h3 className={`text-sm font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
                  {t('docs.attacks_title')}
                </h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className={isDark ? 'bg-white/[0.02]' : 'bg-slate-50'}>
                      <th className={`text-left px-5 py-2.5 text-xs font-semibold uppercase tracking-wider ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
                        Class
                      </th>
                      <th className={`text-left px-5 py-2.5 text-xs font-semibold uppercase tracking-wider ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
                        Severity
                      </th>
                      <th className={`text-left px-5 py-2.5 text-xs font-semibold uppercase tracking-wider ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
                        Description
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {ATTACK_TYPES.map(({ name, severity, desc }, i) => (
                      <tr key={name} className={`${
                        isDark
                          ? i % 2 === 0 ? '' : 'bg-white/[0.01]'
                          : i % 2 === 0 ? '' : 'bg-slate-50/50'
                      } ${isDark ? 'border-t border-white/[0.03]' : 'border-t border-slate-100'}`}>
                        <td className={`px-5 py-2.5 font-mono font-medium text-xs ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                          {name}
                        </td>
                        <td className="px-5 py-2.5">
                          <span className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase border ${severityColor(severity)}`}>
                            {severity}
                          </span>
                        </td>
                        <td className={`px-5 py-2.5 text-xs ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                          {desc}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Attacks tab (detailed) */}
        {tab === 'attacks' && (
          <div className="space-y-6">
            <h2 className={`text-lg font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
              {t('docs.attacks_title')}
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {[
                {
                  title: t('docs.attack_ddos'),
                  severity: 'critical',
                  icon: Zap,
                  how: t('docs.attack_ddos_how_desc'),
                  detect: t('docs.attack_ddos_detect_desc'),
                  ports: ['Any TCP'],
                  tools: ['hping3', 'LOIC', 'Scapy'],
                },
                {
                  title: t('docs.attack_portscan'),
                  severity: 'medium',
                  icon: Target,
                  how: t('docs.attack_portscan_how_desc'),
                  detect: t('docs.attack_portscan_detect_desc'),
                  ports: ['1-1024', '1-65535'],
                  tools: ['nmap', 'masscan', 'unicornscan'],
                },
                {
                  title: t('docs.attack_ssh'),
                  severity: 'high',
                  icon: KeyRound,
                  how: t('docs.attack_ssh_how_desc'),
                  detect: t('docs.attack_ssh_detect_desc'),
                  ports: ['22 (SSH)'],
                  tools: ['hydra', 'patator', 'medusa'],
                },
                {
                  title: t('docs.attack_ftp'),
                  severity: 'high',
                  icon: Lock,
                  how: t('docs.attack_ftp_how_desc'),
                  detect: t('docs.attack_ftp_detect_desc'),
                  ports: ['21 (FTP)'],
                  tools: ['hydra', 'patator', 'ncrack'],
                },
              ].map(({ title, severity, icon: Icon, how, detect, ports, tools }) => (
                <div key={title} className={`rounded-xl border p-6 ${hoverCardClass}`}>
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        isDark ? 'bg-red-500/10 text-red-400' : 'bg-red-50 text-red-600'
                      }`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <h3 className={`text-base font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
                        {title}
                      </h3>
                    </div>
                    <span className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase border ${severityColor(severity)}`}>
                      {severity}
                    </span>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <div className={`text-[11px] uppercase tracking-wider font-semibold mb-1 ${isDark ? 'text-red-400/80' : 'text-red-600/80'}`}>
                        {t('docs.attack_ddos_how')}
                      </div>
                      <p className={`text-xs leading-relaxed ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                        {how}
                      </p>
                    </div>

                    <div>
                      <div className={`text-[11px] uppercase tracking-wider font-semibold mb-1 ${isDark ? 'text-emerald-400/80' : 'text-emerald-600/80'}`}>
                        {t('docs.attack_ddos_detect')}
                      </div>
                      <p className={`text-xs leading-relaxed ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                        {detect}
                      </p>
                    </div>

                    <div className={`pt-3 border-t grid grid-cols-2 gap-3 ${isDark ? 'border-white/[0.05]' : 'border-slate-100'}`}>
                      <div>
                        <div className={`text-[10px] uppercase tracking-wider font-semibold mb-1 ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
                          Ports
                        </div>
                        <div className="flex flex-wrap gap-1">
                          {ports.map(p => (
                            <span key={p} className={`inline-block px-2 py-0.5 text-[10px] font-mono rounded border ${
                              isDark ? 'bg-white/[0.03] text-slate-300 border-white/[0.06]' : 'bg-slate-50 text-slate-700 border-slate-200'
                            }`}>
                              {p}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <div className={`text-[10px] uppercase tracking-wider font-semibold mb-1 ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
                          Tools
                        </div>
                        <div className="flex flex-wrap gap-1">
                          {tools.map(tl => (
                            <span key={tl} className={`inline-block px-2 py-0.5 text-[10px] font-mono rounded border ${
                              isDark ? 'bg-amber-500/5 text-amber-400 border-amber-500/20' : 'bg-amber-50 text-amber-700 border-amber-200'
                            }`}>
                              {tl}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Technologies tab */}
        {tab === 'tech' && (
          <div className="space-y-8">
            <h2 className={`text-lg font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
              {t('docs.tech_title')}
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
              {[
                {
                  title: t('docs.tech_frontend'),
                  icon: Code2,
                  color: 'blue' as const,
                  items: [
                    { name: 'React 19', desc: 'UI library' },
                    { name: 'TypeScript', desc: 'Type-safe JS' },
                    { name: 'Vite', desc: 'Build tool' },
                    { name: 'Tailwind CSS', desc: 'Styling' },
                    { name: 'Recharts', desc: 'Visualization' },
                    { name: 'Lucide Icons', desc: 'Icon set' },
                  ],
                },
                {
                  title: t('docs.tech_backend'),
                  icon: Server,
                  color: 'emerald' as const,
                  items: [
                    { name: 'FastAPI', desc: 'Web framework' },
                    { name: 'Python 3.11', desc: 'Runtime' },
                    { name: 'Uvicorn', desc: 'ASGI server' },
                    { name: 'WebSockets', desc: 'Real-time' },
                    { name: 'psutil', desc: 'Sys metrics' },
                    { name: 'pandas', desc: 'Data ops' },
                  ],
                },
                {
                  title: t('docs.tech_ml'),
                  icon: Brain,
                  color: 'amber' as const,
                  items: [
                    { name: 'LightGBM', desc: 'Classifier' },
                    { name: 'scikit-learn', desc: 'ML utils' },
                    { name: 'joblib', desc: 'Model I/O' },
                    { name: 'NumPy', desc: 'Numerics' },
                    { name: 'PyTorch', desc: 'Autoencoder' },
                    { name: 'CICIDS2017', desc: 'Dataset' },
                  ],
                },
                {
                  title: t('docs.tech_deploy'),
                  icon: Package,
                  color: 'purple' as const,
                  items: [
                    { name: 'Docker', desc: 'Containers' },
                    { name: 'Compose', desc: 'Orchestration' },
                    { name: 'Caddy', desc: 'Reverse proxy' },
                    { name: 'Auto HTTPS', desc: 'TLS certs' },
                    { name: 'Ubuntu', desc: 'Host OS' },
                    { name: 'Linux', desc: 'Foundation' },
                  ],
                },
              ].map(({ title, icon: Icon, color, items }) => {
                const colorMap = {
                  blue: isDark ? 'text-blue-400 bg-blue-500/15' : 'text-blue-600 bg-blue-50',
                  emerald: isDark ? 'text-emerald-400 bg-emerald-500/15' : 'text-emerald-600 bg-emerald-50',
                  amber: isDark ? 'text-amber-400 bg-amber-500/15' : 'text-amber-600 bg-amber-50',
                  purple: isDark ? 'text-purple-400 bg-purple-500/15' : 'text-purple-600 bg-purple-50',
                }
                return (
                  <div key={title} className={`rounded-xl border p-5 ${cardClass}`}>
                    <div className="flex items-center gap-2 mb-4">
                      <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${colorMap[color]}`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <h3 className={`text-base font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
                        {title}
                      </h3>
                    </div>
                    <div className="space-y-2">
                      {items.map(({ name, desc }) => (
                        <div key={name} className={`rounded-lg p-2 ${isDark ? 'bg-white/[0.02]' : 'bg-slate-50/60'}`}>
                          <div className={`text-xs font-mono font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
                            {name}
                          </div>
                          <div className={`text-[10px] ${isDark ? 'text-slate-500' : 'text-slate-500'}`}>
                            {desc}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Benefits tab */}
        {tab === 'benefits' && (
          <div className="space-y-8">
            <h2 className={`text-lg font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
              {t('docs.benefits_title')}
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {[
                { title: t('docs.benefit_accuracy'), desc: t('docs.benefit_accuracy_desc'), icon: Target, color: 'emerald' as const },
                { title: t('docs.benefit_realtime'), desc: t('docs.benefit_realtime_desc'), icon: Zap, color: 'amber' as const },
                { title: t('docs.benefit_educational'), desc: t('docs.benefit_educational_desc'), icon: GraduationCap, color: 'blue' as const },
                { title: t('docs.benefit_extensible'), desc: t('docs.benefit_extensible_desc'), icon: Boxes, color: 'purple' as const },
                { title: t('docs.benefit_openSource'), desc: t('docs.benefit_openSource_desc'), icon: Gauge, color: 'cyan' as const },
                { title: t('docs.benefit_modern'), desc: t('docs.benefit_modern_desc'), icon: Sparkles, color: 'rose' as const },
              ].map(({ title, desc, icon: Icon, color }) => {
                const colorMap = {
                  emerald: isDark ? 'text-emerald-400 bg-emerald-500/15' : 'text-emerald-600 bg-emerald-50',
                  amber: isDark ? 'text-amber-400 bg-amber-500/15' : 'text-amber-600 bg-amber-50',
                  blue: isDark ? 'text-blue-400 bg-blue-500/15' : 'text-blue-600 bg-blue-50',
                  purple: isDark ? 'text-purple-400 bg-purple-500/15' : 'text-purple-600 bg-purple-50',
                  cyan: isDark ? 'text-cyan-400 bg-cyan-500/15' : 'text-cyan-600 bg-cyan-50',
                  rose: isDark ? 'text-rose-400 bg-rose-500/15' : 'text-rose-600 bg-rose-50',
                }
                return (
                  <div key={title} className={`rounded-xl border p-5 ${hoverCardClass}`}>
                    <div className={`w-11 h-11 rounded-lg flex items-center justify-center mb-3 ${colorMap[color]}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <h3 className={`text-sm font-semibold mb-1.5 ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
                      {title}
                    </h3>
                    <p className={`text-xs leading-relaxed ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                      {desc}
                    </p>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Architecture tab */}
        {tab === 'architecture' && (
          <div className="space-y-8">
            <h2 className={`text-lg font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
              {t('docs.arch_title')}
            </h2>

            <div className={`rounded-xl border p-8 font-mono text-xs leading-relaxed overflow-x-auto ${cardClass}`}>
              <pre className={`${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
{`
  ┌─────────────────────────────────────────────────────────────────────┐
  │                      SYSTEM ARCHITECTURE                           │
  └─────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐     HTTP/WS      ┌──────────────────┐
  │              │ ◄──────────────► │                  │
  │    React     │                  │     FastAPI       │
  │   Frontend   │   REST + WS     │     Backend       │
  │              │                  │                  │
  └──────────────┘                  └────────┬─────────┘
        │                                    │
        │  Dashboard / Alerts                │  /predict
        │  Live WebSocket Feed               │  /stats
        │                                    │
                                    ┌────────▼─────────┐
                                    │                  │
                                    │    ML Engine      │
                                    │   (LightGBM)     │
                                    │                  │
                                    └────────┬─────────┘
                                             │
                                    ┌────────▼─────────┐
                                    │   Trained Model   │
                                    │  lgbm_model.pkl  │
                                    └──────────────────┘


  ┌─────────────────────────────────────────────────────────────────────┐
  │                    DATA PROCESSING PIPELINE                        │
  └─────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
  │   Network    │    │    Flow      │    │   Feature    │    │  LightGBM    │
  │   Capture    │───►│  Aggregator  │───►│  Extraction  │───►│  Classifier  │
  │  (packets)   │    │ (bidirect.)  │    │ (74 feats)   │    │ (15 classes) │
  └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
        │                                                           │
        │              Raw PCAP Data                                │
        │                                                           ▼
        │                                                   ┌──────────────┐
        └──────────────────────────────────────────────────►│   Threat     │
                         Ground Truth                       │   Report     │
                         Comparison                         └──────────────┘


  ┌─────────────────────────────────────────────────────────────────────┐
  │                        TECH STACK                                   │
  ├─────────────────────┬───────────────────────────────────────────────┤
  │  Frontend           │  React + TypeScript + Tailwind CSS           │
  │  Backend            │  Python + FastAPI + Uvicorn                  │
  │  ML Framework       │  LightGBM + scikit-learn                    │
  │  Dataset            │  CICIDS2017 (2.8M flows, 80+ features)      │
  │  Communication      │  REST API + WebSocket (real-time)           │
  │  Deployment         │  Docker + Docker Compose + Caddy            │
  └─────────────────────┴───────────────────────────────────────────────┘
`}
              </pre>
            </div>

            {/* Tech stack summary cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                { label: 'Frontend Layer', value: 'React + TS + Tailwind', icon: FileCode2 },
                { label: 'Backend Layer', value: 'FastAPI + WebSocket', icon: Server },
                { label: 'ML Layer', value: 'LightGBM + sklearn', icon: Brain },
              ].map(({ label, value, icon: Icon }) => (
                <div key={label} className={`rounded-xl border p-5 ${cardClass}`}>
                  <Icon className={`w-5 h-5 mb-2 ${isDark ? 'text-amber-500/60' : 'text-amber-500'}`} />
                  <div className={`text-[10px] uppercase tracking-wider font-semibold mb-1 ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
                    {label}
                  </div>
                  <div className={`text-sm font-mono ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
                    {value}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
    </div>
  )
}
