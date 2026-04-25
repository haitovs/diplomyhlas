import { NavLink } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { Activity, Monitor, Skull, FileBarChart, BookOpen, Circle, Sun, Moon, Languages, ChevronLeft, ChevronRight, Terminal, ChevronDown, ChevronUp } from 'lucide-react'
import { getState, type DemoState } from '../services/api'
import { useSettings, useT, type Lang } from '../i18n'

const linkKeys = [
  { to: '/monitoring', icon: Activity, label: 'sidebar.monitoring' as const, desc: 'sidebar.monitoring_desc' as const },
  { to: '/workspace', icon: Monitor, label: 'sidebar.workspace' as const, desc: 'sidebar.workspace_desc' as const },
  { to: '/attack', icon: Skull, label: 'sidebar.attack' as const, desc: 'sidebar.attack_desc' as const },
  { to: '/report', icon: FileBarChart, label: 'sidebar.report' as const, desc: 'sidebar.report_desc' as const },
  { to: '/docs', icon: BookOpen, label: 'sidebar.docs' as const, desc: 'sidebar.docs_desc' as const },
]

export default function Sidebar() {
  const t = useT()
  const { lang, theme, setLang, setTheme } = useSettings()
  const [state, setState] = useState<DemoState | null>(null)
  const [collapsed, setCollapsed] = useState(window.innerWidth < 1024)
  const isDark = theme === 'dark'

  useEffect(() => {
    const handleResize = () => {
      setCollapsed(window.innerWidth < 1024)
    }
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  useEffect(() => {
    const poll = () => getState().then(setState).catch(() => {})
    poll()
    const id = setInterval(poll, 3000)
    return () => clearInterval(id)
  }, [])

  const [hintsOpen, setHintsOpen] = useState(false)

  const benignOn = state?.benign_active ?? false
  const attackCount = state ? Object.values(state.attacks).filter(Boolean).length : 0
  const anyActive = benignOn || attackCount > 0

  return (
    <aside className={`${collapsed ? 'w-18' : 'w-[280px]'} shrink-0 flex flex-col border-r transition-all duration-300 ${
      isDark ? 'bg-[#0a0f1a] border-white/[0.06]' : 'bg-[#f8f9fb] border-slate-200'
    }`}>
      {/* Collapse toggle + Brand */}
      <div className={`p-5 border-b ${isDark ? 'border-white/[0.06]' : 'border-slate-200'}`}>
        <div className={`flex items-center ${collapsed ? 'justify-center' : 'gap-3'}`}>
          {!collapsed && (
            <img src="/oguzhan_logo.png" alt="Logo" className="w-11 h-11 rounded-xl object-contain" />
          )}
          {!collapsed && (
            <div className="flex-1 min-w-0">
              <div className={`text-[15px] font-bold tracking-wide ${isDark ? 'text-slate-100' : 'text-slate-800'}`}>
                {t('sidebar.brand')}
              </div>
              <div className={`text-[11px] font-medium uppercase tracking-widest ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
                {t('sidebar.subtitle')}
              </div>
            </div>
          )}
          <button
            onClick={() => setCollapsed(c => !c)}
            className={`flex items-center justify-center w-7 h-7 rounded-md transition-colors shrink-0 ${
              isDark ? 'hover:bg-white/[0.06] text-slate-500' : 'hover:bg-slate-200 text-slate-400'
            }`}
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Status indicator — full when expanded */}
      {!collapsed && (
        <div className={`mx-4 mt-4 mb-2 px-3 py-2.5 rounded-lg border ${
          isDark ? 'bg-white/[0.02] border-white/[0.04]' : 'bg-slate-50 border-slate-200'
        }`}>
          <div className="flex items-center gap-2 text-[11px]">
            <Circle className={`w-2 h-2 fill-current ${anyActive ? 'text-emerald-400' : 'text-slate-400'}`} />
            <span className={`font-medium ${anyActive ? 'text-emerald-500' : isDark ? 'text-slate-500' : 'text-slate-400'}`}>
              {anyActive ? t('sidebar.system_active') : t('sidebar.system_idle')}
            </span>
          </div>
          {anyActive && (
            <div className="mt-1.5 space-y-0.5">
              {benignOn && (
                <div className={`text-[10px] font-mono pl-4 ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
                  {t('sidebar.benign_traffic')}: <span className="text-emerald-500">{state?.benign_speed ?? 1}x</span>
                </div>
              )}
              {attackCount > 0 && (
                <div className={`text-[10px] font-mono pl-4 ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
                  {t('sidebar.active_attacks')}: <span className="text-red-500">{attackCount}/4</span>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Status dot — collapsed only */}
      {collapsed && (
        <div className="flex justify-center mt-4 mb-2">
          <Circle className={`w-2.5 h-2.5 fill-current ${anyActive ? 'text-emerald-400' : 'text-slate-400'}`} />
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 px-3 pt-2 space-y-0.5">
        {!collapsed && (
          <div className={`px-3 py-2 text-[10px] uppercase tracking-widest font-semibold ${
            isDark ? 'text-slate-600' : 'text-slate-400'
          }`}>{t('sidebar.nav')}</div>
        )}
        {linkKeys.map(({ to, icon: Icon, label, desc }) => (
          <NavLink
            key={to}
            to={to}
            title={collapsed ? t(label) : undefined}
            className={({ isActive }) =>
              `group flex items-center ${collapsed ? 'justify-center' : ''} gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200 ${
                isActive
                  ? isDark
                    ? 'bg-amber-500/10 text-amber-400 shadow-[inset_0_0_0_1px_rgba(245,158,11,0.15)]'
                    : 'bg-amber-50 text-amber-600 shadow-[inset_0_0_0_1px_rgba(245,158,11,0.25)]'
                  : isDark
                    ? 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.03]'
                    : 'text-slate-500 hover:text-slate-700 hover:bg-slate-50'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <div className={`w-9 h-9 rounded-lg flex items-center justify-center transition-all shrink-0 ${
                  isActive
                    ? isDark ? 'bg-amber-500/15' : 'bg-amber-100'
                    : isDark ? 'bg-white/[0.03] group-hover:bg-white/[0.06]' : 'bg-slate-100 group-hover:bg-slate-200'
                }`}>
                  <Icon className="w-[18px] h-[18px]" />
                </div>
                {!collapsed && (
                  <div>
                    <div className="font-medium leading-tight text-[14px]">{t(label)}</div>
                    <div className={`text-[11px] leading-tight mt-0.5 ${
                      isActive
                        ? isDark ? 'text-amber-500/60' : 'text-amber-500/70'
                        : isDark ? 'text-slate-600' : 'text-slate-400'
                    }`}>{t(desc)}</div>
                  </div>
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Settings — hidden when collapsed */}
      {!collapsed && (
        <div className={`px-4 py-3 border-t ${isDark ? 'border-white/[0.06]' : 'border-slate-200'}`}>
          {/* Language toggle */}
          <div className="flex items-center justify-between mb-2">
            <div className={`flex items-center gap-1.5 text-[10px] ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
              <Languages className="w-3 h-3" />
              {t('common.language')}
            </div>
            <div className={`flex rounded-md overflow-hidden border ${isDark ? 'border-white/[0.08]' : 'border-slate-200'}`}>
              {(['tk', 'en'] as Lang[]).map((l) => (
                <button
                  key={l}
                  onClick={() => setLang(l)}
                  className={`px-2.5 py-1 text-[10px] font-semibold uppercase transition-all ${
                    lang === l
                      ? 'bg-amber-500 text-white'
                      : isDark
                        ? 'bg-white/[0.03] text-slate-500 hover:text-slate-300'
                        : 'bg-slate-50 text-slate-400 hover:text-slate-600'
                  }`}
                >
                  {l === 'tk' ? 'TK' : 'EN'}
                </button>
              ))}
            </div>
          </div>
          {/* Theme toggle */}
          <div className="flex items-center justify-between">
            <div className={`flex items-center gap-1.5 text-[10px] ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
              {isDark ? <Moon className="w-3 h-3" /> : <Sun className="w-3 h-3" />}
              {t('common.theme')}
            </div>
            <button
              onClick={() => setTheme(isDark ? 'light' : 'dark')}
              className={`relative w-10 h-5 rounded-full transition-colors duration-300 ${
                isDark ? 'bg-amber-500/30' : 'bg-slate-300'
              }`}
            >
              <div className={`absolute top-0.5 w-4 h-4 rounded-full transition-all duration-300 ${
                isDark
                  ? 'left-5.5 bg-amber-500'
                  : 'left-0.5 bg-white shadow'
              }`} />
            </button>
          </div>
        </div>
      )}

      {/* Quick Start hints — hidden when collapsed */}
      {!collapsed && (
        <div className={`px-3 pb-1 border-t ${isDark ? 'border-white/[0.06]' : 'border-slate-200'}`}>
          <button
            onClick={() => setHintsOpen(o => !o)}
            className={`w-full flex items-center gap-2 py-2.5 text-[11px] font-medium transition-colors ${
              isDark ? 'text-slate-500 hover:text-slate-300' : 'text-slate-400 hover:text-slate-600'
            }`}
          >
            <Terminal className="w-3.5 h-3.5 flex-shrink-0" />
            <span className="flex-1 text-left uppercase tracking-wider text-[10px]">Quick Start</span>
            {hintsOpen ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>

          {hintsOpen && (
            <div className={`mb-2 rounded-lg border overflow-hidden text-[11px] font-mono ${
              isDark ? 'border-white/[0.06] bg-[#050810]' : 'border-slate-200 bg-slate-50'
            }`}>
              {/* Dev mode */}
              <div className={`px-3 py-2 border-b ${isDark ? 'border-white/[0.05]' : 'border-slate-200'}`}>
                <div className={`text-[9px] uppercase tracking-wider mb-1.5 ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
                  Dev mode
                </div>
                <div className={`${isDark ? 'text-emerald-400' : 'text-emerald-600'}`}>./run_app.sh</div>
                <div className={`text-[10px] mt-0.5 ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
                  → localhost:<span className={isDark ? 'text-amber-500' : 'text-amber-600'}>5173</span>
                  <span className="ml-2 opacity-60">(api :8000)</span>
                </div>
              </div>

              {/* Docker */}
              <div className={`px-3 py-2 border-b ${isDark ? 'border-white/[0.05]' : 'border-slate-200'}`}>
                <div className={`text-[9px] uppercase tracking-wider mb-1.5 ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
                  Docker / Production
                </div>
                <div className={`${isDark ? 'text-cyan-400' : 'text-cyan-600'}`}>make build && make run</div>
                <div className={`text-[10px] mt-0.5 ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
                  → localhost:<span className={isDark ? 'text-amber-500' : 'text-amber-600'}>4086</span>
                </div>
              </div>

              {/* Stop */}
              <div className="px-3 py-2">
                <div className={`text-[9px] uppercase tracking-wider mb-1.5 ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
                  Stop Docker
                </div>
                <div className={`${isDark ? 'text-red-400' : 'text-red-600'}`}>make stop</div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Footer — hidden when collapsed */}
      {!collapsed && (
        <div className={`p-4 border-t ${isDark ? 'border-white/[0.06]' : 'border-slate-200'}`}>
          <div className="flex items-center justify-between">
            <div className={`text-[10px] font-mono ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>v1.0</div>
            <div className={`flex items-center gap-1.5 text-[10px] font-mono ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-500/60" />
              LightGBM
            </div>
          </div>
        </div>
      )}
    </aside>
  )
}
