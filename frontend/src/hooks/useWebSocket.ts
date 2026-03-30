import { useEffect, useRef, useState } from 'react'
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
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const mountedRef = useRef(true)

  useEffect(() => {
    mountedRef.current = true

    function connect() {
      // Don't connect if unmounted or already connecting/open
      if (!mountedRef.current) return
      if (wsRef.current && (wsRef.current.readyState === WebSocket.CONNECTING || wsRef.current.readyState === WebSocket.OPEN)) return

      const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
      const ws = new WebSocket(`${proto}://${window.location.host}/api/monitor/ws`)
      wsRef.current = ws

      ws.onopen = () => {
        if (mountedRef.current) setConnected(true)
      }

      ws.onclose = () => {
        if (mountedRef.current) {
          setConnected(false)
          // Reconnect with backoff
          if (reconnectTimer.current) clearTimeout(reconnectTimer.current)
          reconnectTimer.current = setTimeout(connect, 3000)
        }
      }

      ws.onerror = () => {
        // onclose will fire after onerror, which handles reconnection
      }

      ws.onmessage = (evt) => {
        if (!mountedRef.current) return
        try {
          const msg: WsTick = JSON.parse(evt.data)
          if (msg.flows && msg.flows.length > 0) {
            setFlows((prev) => [...prev, ...msg.flows].slice(-2000))
          }
          if (msg.state) setState(msg.state)
          setActive(msg.active)
        } catch {
          // ignore malformed messages
        }
      }
    }

    connect()

    return () => {
      mountedRef.current = false
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current)
      if (wsRef.current) {
        wsRef.current.onclose = null // prevent reconnect on intentional close
        wsRef.current.close()
      }
    }
  }, [])

  return { flows, state, active, connected }
}
