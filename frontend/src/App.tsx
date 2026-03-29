import { useState, useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { SettingsContext, type Lang } from './i18n'
import Layout from './components/Layout'
import Monitoring from './pages/Monitoring'
import Workspace from './pages/Workspace'
import AttackSpace from './pages/AttackSpace'

export default function App() {
  const [lang, setLang] = useState<Lang>(() =>
    (localStorage.getItem('lang') as Lang) || 'tk'
  )
  const [theme, setTheme] = useState<'dark' | 'light'>(() =>
    (localStorage.getItem('theme') as 'dark' | 'light') || 'dark'
  )

  useEffect(() => { localStorage.setItem('lang', lang) }, [lang])
  useEffect(() => { localStorage.setItem('theme', theme) }, [theme])

  // Apply theme to document
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    if (theme === 'light') {
      document.body.className = 'bg-[#f0f2f5] text-slate-800 antialiased'
    } else {
      document.body.className = 'bg-[#060b14] text-slate-200 antialiased'
    }
  }, [theme])

  return (
    <SettingsContext.Provider value={{ lang, theme, setLang, setTheme }}>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/monitoring" element={<Monitoring />} />
          <Route path="/workspace" element={<Workspace />} />
          <Route path="/attack" element={<AttackSpace />} />
          <Route path="*" element={<Navigate to="/monitoring" replace />} />
        </Route>
      </Routes>
    </SettingsContext.Provider>
  )
}
