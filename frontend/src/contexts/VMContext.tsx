import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from 'react'

export type VMId = 'ids' | 'traffic' | 'attacker'
export type VMStatus = 'off' | 'booting' | 'running'

interface VMRecord {
  status: VMStatus
  bootStartedAt: number | null
}

interface VMState {
  ids: VMRecord
  traffic: VMRecord
  attacker: VMRecord
}

interface VMContextValue {
  vms: VMState
  start: (id: VMId) => void
  shutdown: (id: VMId) => void
  isRunning: (id: VMId) => boolean
}

const STORAGE_KEY = 'vm_state_v1'
const BOOT_DURATION_MS = 62_000

function defaultRecord(): VMRecord {
  return { status: 'off', bootStartedAt: null }
}

function defaultState(): VMState {
  return { ids: defaultRecord(), traffic: defaultRecord(), attacker: defaultRecord() }
}

function loadState(): VMState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return defaultState()
    const parsed = JSON.parse(raw) as Partial<VMState>
    const hydrated = defaultState()
    ;(['ids', 'traffic', 'attacker'] as VMId[]).forEach((id) => {
      const saved = parsed?.[id]
      if (!saved) return
      if (saved.status === 'booting' && typeof saved.bootStartedAt === 'number') {
        const elapsed = Date.now() - saved.bootStartedAt
        hydrated[id] = elapsed >= BOOT_DURATION_MS
          ? { status: 'running', bootStartedAt: null }
          : { status: 'booting', bootStartedAt: saved.bootStartedAt }
      } else if (saved.status === 'running') {
        hydrated[id] = { status: 'running', bootStartedAt: null }
      }
    })
    return hydrated
  } catch {
    return defaultState()
  }
}

const VMContext = createContext<VMContextValue>({
  vms: defaultState(),
  start: () => {},
  shutdown: () => {},
  isRunning: () => false,
})

export function VMProvider({ children }: { children: ReactNode }) {
  const [vms, setVms] = useState<VMState>(() => loadState())
  const timersRef = useRef<Partial<Record<VMId, number>>>({})

  useEffect(() => {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(vms)) } catch {}
  }, [vms])

  const finishBoot = useCallback((id: VMId) => {
    setVms((prev) => {
      if (prev[id].status !== 'booting') return prev
      return { ...prev, [id]: { status: 'running', bootStartedAt: null } }
    })
  }, [])

  useEffect(() => {
    ;(['ids', 'traffic', 'attacker'] as VMId[]).forEach((id) => {
      const rec = vms[id]
      if (rec.status === 'booting' && rec.bootStartedAt && !timersRef.current[id]) {
        const remaining = Math.max(0, BOOT_DURATION_MS - (Date.now() - rec.bootStartedAt))
        timersRef.current[id] = window.setTimeout(() => {
          timersRef.current[id] = undefined
          finishBoot(id)
        }, remaining)
      }
      if (rec.status !== 'booting' && timersRef.current[id]) {
        window.clearTimeout(timersRef.current[id])
        timersRef.current[id] = undefined
      }
    })
    return () => {
      Object.values(timersRef.current).forEach((t) => t && window.clearTimeout(t))
      timersRef.current = {}
    }
  }, [vms, finishBoot])

  const start = useCallback((id: VMId) => {
    setVms((prev) => {
      if (prev[id].status !== 'off') return prev
      return { ...prev, [id]: { status: 'booting', bootStartedAt: Date.now() } }
    })
  }, [])

  const shutdown = useCallback((id: VMId) => {
    setVms((prev) => ({ ...prev, [id]: { status: 'off', bootStartedAt: null } }))
  }, [])

  const isRunning = useCallback((id: VMId) => vms[id].status === 'running', [vms])

  const value = useMemo(() => ({ vms, start, shutdown, isRunning }), [vms, start, shutdown, isRunning])

  return <VMContext.Provider value={value}>{children}</VMContext.Provider>
}

export function useVM() {
  return useContext(VMContext)
}

export const VM_BOOT_DURATION_MS = BOOT_DURATION_MS
