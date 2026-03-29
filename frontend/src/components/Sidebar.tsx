import { NavLink } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { Activity, Monitor, Skull, Shield, Circle, Sun, Moon, Languages } from 'lucide-react'
import { getState, type DemoState } from '../services/api'
import { useSettings, useT, type Lang } from '../i18n'

const linkKeys = [
  { to: '/monitoring', icon: Activity, label: 'sidebar.monitoring' as const, desc: 'sidebar.monitoring_desc' as const },
  { to: '/workspace', icon: Monitor, label: 'sidebar.workspace' as const, desc: 'sidebar.workspace_desc' as const },
  { to: '/attack', icon: Skull, label: 'sidebar.attack' as const, desc: 'sidebar.attack_desc' as const },
]

export default function Sidebar() {
  const t = useT()
  const { lang, theme, setLang, setTheme } = useSettings()
  const [state, setState] = useState<DemoState | null>(null)
  const isDark = theme === 'dark'

  useEffect(() => {
    const poll = () => getState().then(setState).catch(() => {})
    poll()
    const id = setInterval(poll, 3000)
    return () => clearInterval(id)
  }, [])

  const benignOn = state?.benign_active ?? false
  const attackCount = state ? Object.values(state.attacks).filter(Boolean).length : 0
  const anyActive = benignOn || attackCount > 0

  return (
    <aside className={`w-[260px] shrink-0 flex flex-col border-r transition-colors duration-300 ${
      isDark ? 'bg-[#0a0f1a] border-white/[0.06]' : 'bg-white border-slate-200'
    }`}>
      {/* Brand */}
      <div className={`p-5 border-b ${isDark ? 'border-white/[0.06]' : 'border-slate-200'}`}>
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center border ${
            isDark
              ? 'bg-gradient-to-br from-amber-500/20 to-amber-600/10 border-amber-500/20'
              : 'bg-amber-50 border-amber-200'
          }`}>
            <Shield className="w-5 h-5 text-amber-500" />
          </div>
          <div>
            <div className={`text-sm font-bold tracking-wide ${isDark ? 'text-slate-100' : 'text-slate-800'}`}>
              {t('sidebar.brand')}
            </div>
            <div className={`text-[10px] font-medium uppercase tracking-widest ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
              {t('sidebar.subtitle')}
            </div>
          </div>
        </div>
      </div>

      {/* Status indicator */}
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

      {/* Navigation */}
      <nav className="flex-1 px-3 pt-2 space-y-0.5">
        <div className={`px-3 py-2 text-[10px] uppercase tracking-widest font-semibold ${
          isDark ? 'text-slate-600' : 'text-slate-400'
        }`}>{t('sidebar.nav')}</div>
        {linkKeys.map(({ to, icon: Icon, label, desc }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `group flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200 ${
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
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center transition-all ${
                  isActive
                    ? isDark ? 'bg-amber-500/15' : 'bg-amber-100'
                    : isDark ? 'bg-white/[0.03] group-hover:bg-white/[0.06]' : 'bg-slate-100 group-hover:bg-slate-200'
                }`}>
                  <Icon className="w-4 h-4" />
                </div>
                <div>
                  <div className="font-medium leading-tight">{t(label)}</div>
                  <div className={`text-[10px] leading-tight mt-0.5 ${
                    isActive
                      ? isDark ? 'text-amber-500/60' : 'text-amber-500/70'
                      : isDark ? 'text-slate-600' : 'text-slate-400'
                  }`}>{t(desc)}</div>
                </div>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Settings */}
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

      {/* Footer */}
      <div className={`p-4 border-t ${isDark ? 'border-white/[0.06]' : 'border-slate-200'}`}>
        <div className="flex items-center justify-between">
          <div className={`text-[10px] font-mono ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>v1.0</div>
          <div className={`flex items-center gap-1.5 text-[10px] font-mono ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500/60" />
            LightGBM
          </div>
        </div>
      </div>
    </aside>
  )
}
