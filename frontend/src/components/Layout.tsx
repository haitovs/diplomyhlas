import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import { useSettings } from '../i18n'

export default function Layout() {
  const { theme } = useSettings()
  const isDark = theme === 'dark'

  return (
    <div className={`flex h-screen overflow-hidden transition-colors duration-300 ${
      isDark ? 'bg-[#060b14]' : 'bg-[#f5f6f8]'
    }`}>
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-[1400px] mx-auto p-6">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
