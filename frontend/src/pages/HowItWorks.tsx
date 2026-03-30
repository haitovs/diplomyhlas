import { useState } from 'react'
import { Database, Brain, FileBarChart, ArrowRight, Shield, Globe, Cpu, Layers } from 'lucide-react'
import { useT, useSettings } from '../i18n'

type Tab = 'pipeline' | 'dataset' | 'attacks' | 'architecture'

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
  const [tab, setTab] = useState<Tab>('pipeline')

  const tabs: { id: Tab; label: string }[] = [
    { id: 'pipeline', label: t('docs.tab_pipeline') },
    { id: 'dataset', label: t('docs.tab_dataset') },
    { id: 'attacks', label: t('docs.tab_attacks') },
    { id: 'architecture', label: t('docs.tab_architecture') },
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

  return (
    <div className={`flex-1 overflow-auto transition-colors duration-300 ${isDark ? 'bg-[#060b14]' : 'bg-[#f5f6f8]'}`}>
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className={`text-2xl font-bold tracking-tight ${isDark ? 'text-slate-100' : 'text-slate-800'}`}>
            {t('docs.title')}
          </h1>
          <p className={`text-sm mt-1 ${isDark ? 'text-slate-500' : 'text-slate-500'}`}>
            {t('docs.subtitle')}
          </p>
        </div>

        {/* Tab navigation */}
        <div className={`flex gap-1 p-1 rounded-xl mb-8 ${isDark ? 'bg-white/[0.03] border border-white/[0.06]' : 'bg-slate-100 border border-slate-200'}`}>
          {tabs.map(({ id, label }) => (
            <button
              key={id}
              onClick={() => setTab(id)}
              className={`flex-1 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                tab === id
                  ? isDark
                    ? 'bg-amber-500/15 text-amber-400 shadow-[inset_0_0_0_1px_rgba(245,158,11,0.2)]'
                    : 'bg-white text-amber-600 shadow-sm'
                  : isDark
                    ? 'text-slate-500 hover:text-slate-300'
                    : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        {/* Pipeline tab */}
        {tab === 'pipeline' && (
          <div className="space-y-8">
            <h2 className={`text-lg font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
              {t('docs.pipeline_title')}
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[
                { step: 1, icon: Database, title: t('docs.step1_title'), desc: t('docs.step1_desc'), color: 'cyan' },
                { step: 2, icon: Brain, title: t('docs.step2_title'), desc: t('docs.step2_desc'), color: 'amber' },
                { step: 3, icon: FileBarChart, title: t('docs.step3_title'), desc: t('docs.step3_desc'), color: 'emerald' },
              ].map(({ step, icon: Icon, title, desc }, idx) => (
                <div key={step} className="relative">
                  <div className={`rounded-xl border p-6 h-full transition-colors ${
                    isDark
                      ? 'bg-[#0a0f1a] border-amber-500/20 hover:border-amber-500/40'
                      : 'bg-white border-amber-200/60 hover:border-amber-300 shadow-sm'
                  }`}>
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
                  <div key={key} className={`rounded-xl border p-5 text-center transition-colors ${
                    isDark
                      ? 'bg-[#0a0f1a] border-amber-500/20'
                      : 'bg-white border-amber-200/60 shadow-sm'
                  }`}>
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

            {/* Stat cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: t('docs.dataset_flows'), icon: Layers },
                { label: t('docs.dataset_features'), icon: Cpu },
                { label: t('docs.dataset_days'), icon: Globe },
                { label: t('docs.dataset_classes'), icon: Shield },
              ].map(({ label, icon: Icon }) => (
                <div key={label} className={`rounded-xl border p-5 text-center transition-colors ${
                  isDark
                    ? 'bg-[#0a0f1a] border-amber-500/20'
                    : 'bg-white border-amber-200/60 shadow-sm'
                }`}>
                  <Icon className={`w-6 h-6 mx-auto mb-2 ${isDark ? 'text-amber-500/60' : 'text-amber-500'}`} />
                  <div className={`text-sm font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
                    {label}
                  </div>
                </div>
              ))}
            </div>

            {/* Dataset attack types table */}
            <div className={`rounded-xl border overflow-hidden ${
              isDark ? 'bg-[#0a0f1a] border-amber-500/20' : 'bg-white border-amber-200/60 shadow-sm'
            }`}>
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

        {/* Attacks tab */}
        {tab === 'attacks' && (
          <div className="space-y-6">
            <h2 className={`text-lg font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
              {t('docs.attacks_title')}
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {ATTACK_TYPES.map(({ name, severity, desc }) => (
                <div key={name} className={`rounded-xl border p-5 transition-colors ${
                  isDark
                    ? 'bg-[#0a0f1a] border-amber-500/20 hover:border-amber-500/40'
                    : 'bg-white border-amber-200/60 hover:border-amber-300 shadow-sm'
                }`}>
                  <div className="flex items-start justify-between mb-3">
                    <h3 className={`text-sm font-semibold font-mono ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
                      {name}
                    </h3>
                    <span className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase border ${severityColor(severity)}`}>
                      {severity}
                    </span>
                  </div>
                  <p className={`text-xs leading-relaxed ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                    {desc}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Architecture tab */}
        {tab === 'architecture' && (
          <div className="space-y-8">
            <h2 className={`text-lg font-semibold ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
              {t('docs.arch_title')}
            </h2>

            <div className={`rounded-xl border p-8 font-mono text-xs leading-relaxed overflow-x-auto ${
              isDark
                ? 'bg-[#0a0f1a] border-amber-500/20'
                : 'bg-white border-amber-200/60 shadow-sm'
            }`}>
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
  │  Deployment         │  Docker + Docker Compose                    │
  └─────────────────────┴───────────────────────────────────────────────┘
`}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
