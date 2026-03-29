import { useEffect, useRef, useCallback, useState } from 'react'
import type { FlowEntry, DemoState } from '../services/api'

interface WsTick {
  type: 'tick'
  flows: FlowEntry[]
  state: DemoState
  active: boolean
}

interface UseMonitorWs {
  flows: FlowEntry[]
  state: DemoState | null
  active: boolean
  connected: boolean
}

export function useMonitorWs(): UseMonitorWs {
  const [flows, setFlows] = useState<FlowEntry[]>([])
  const [state, setState] = useState<DemoState | null>(null)
  const [active, setActive] = useState(false)
  const [connected, setConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  const connect = useCallback(() => {
    const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const ws = new WebSocket(`${proto}://${window.location.host}/api/monitor/ws`)
    wsRef.current = ws

    ws.onopen = () => setConnected(true)
    ws.onclose = () => {
      setConnected(false)
      setTimeout(connect, 2000)
    }
    ws.onerror = () => ws.close()

    ws.onmessage = (evt) => {
      const msg: WsTick = JSON.parse(evt.data)
      if (msg.flows && msg.flows.length > 0) {
        setFlows((prev) => [...prev, ...msg.flows].slice(-2000))
      }
      if (msg.state) setState(msg.state)
      setActive(msg.active)
    }
  }, [])

  useEffect(() => {
    connect()
    return () => {
      wsRef.current?.close()
    }
  }, [connect])

  return { flows, state, active, connected }
}
