import { useState, useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { SettingsContext, type Lang } from './i18n'
import { VMProvider } from './contexts/VMContext'
import VMGate from './components/VMGate'
import Layout from './components/Layout'
import Monitoring from './pages/Monitoring'
import Workspace from './pages/Workspace'
import AttackSpace from './pages/AttackSpace'
import HowItWorks from './pages/HowItWorks'
import Report from './pages/Report'

export default function App() {
  const [lang, setLang] = useState<Lang>(() =>
    (localStorage.getItem('lang') as Lang) || 'tk'
  )
  const [theme, setTheme] = useState<'dark' | 'light'>(() =>
    (localStorage.getItem('theme') as 'dark' | 'light') || 'light'
  )

  useEffect(() => { localStorage.setItem('lang', lang) }, [lang])
  useEffect(() => { localStorage.setItem('theme', theme) }, [theme])

  // Apply theme to document
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    if (theme === 'light') {
      document.body.className = 'bg-[#f5f6f8] text-slate-800 antialiased'
    } else {
      document.body.className = 'bg-[#060b14] text-slate-200 antialiased'
    }
  }, [theme])

  return (
    <SettingsContext.Provider value={{ lang, theme, setLang, setTheme }}>
      <VMProvider>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/monitoring" element={<VMGate vmId="ids"><Monitoring /></VMGate>} />
            <Route path="/workspace" element={<VMGate vmId="traffic"><Workspace /></VMGate>} />
            <Route path="/attack" element={<VMGate vmId="attacker"><AttackSpace /></VMGate>} />
            <Route path="/report" element={<Report />} />
            <Route path="/docs" element={<HowItWorks />} />
            <Route path="*" element={<Navigate to="/monitoring" replace />} />
          </Route>
        </Routes>
      </VMProvider>
    </SettingsContext.Provider>
  )
}
