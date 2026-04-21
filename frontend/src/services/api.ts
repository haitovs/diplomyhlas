const BASE = ''

async function json<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, init)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

function post<T>(url: string, body: unknown): Promise<T> {
  return json<T>(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}

// State
export const getState = () => json<DemoState>('/api/state')
export const setBenign = (active: boolean, speed = 1.0) =>
  post<Ok>('/api/state/benign', { active, speed })
export const setAttack = (attack_type: string, active: boolean) =>
  post<Ok>('/api/state/attack', { attack_type, active })
export const setAllAttacks = (active: boolean) =>
  post<Ok>('/api/state/attack/all', { active })
export const stopAll = () => post<Ok>('/api/state/stop', {})
export const sendBurst = (attack_type: string, count: number) =>
  post<Ok>('/api/state/burst', { attack_type, count })

// Monitor
export const getHistory = (limit = 500) =>
  json<FlowEntry[]>(`/api/monitor/history?limit=${limit}`)
export const getStats = () => json<Stats>('/api/monitor/stats')
export const blockIp = (ip: string) =>
  post<{ ok: boolean; blocked: string[] }>('/api/monitor/block', { ip })
export const unblockIp = (ip: string) =>
  post<{ ok: boolean; blocked: string[] }>('/api/monitor/unblock', { ip })
export const clearHistory = () => post<Ok>('/api/monitor/clear', {})
export const getDefender = () => json<DefenderState>('/api/monitor/defender')
export const setDefender = (enabled: boolean) =>
  post<{ ok: boolean; enabled: boolean }>('/api/monitor/defender', { enabled })

// Inference
export const getModelInfo = () => json<ModelInfo>('/api/inference/model')

// Types
export interface DemoState {
  benign_active: boolean
  benign_speed: number
  attacks: Record<string, boolean>
  bursts: { type: string; count: number }[]
  last_update: number
}

export interface FlowEntry {
  timestamp: string
  src_ip: string
  dst_ip: string
  src_port: number
  dst_port: number
  protocol: string
  prediction: string
  confidence: number
  is_anomaly: boolean
  total_packets: number
  total_bytes: number
  flow_bytes_per_s: number
  source: string
}

export interface Stats {
  total_flows: number
  anomalies: number
  threat_pct: number
  avg_confidence: number
  blocked_count: number
  blocked_ips: string[]
  defender_enabled: boolean
  auto_blocked_count: number
  distribution: Record<string, number>
  unique_src: number
  unique_dst: number
  top_port: string
  avg_throughput: number
}

export interface DefenderState {
  enabled: boolean
  auto_blocked_count: number
  blocked_count: number
}

export interface ModelInfo {
  loaded: boolean
  model_type: string | null
  n_features: number
  classes: string[]
}

// System metrics
export const getSystemMetrics = () => json<SystemMetrics>('/api/system')

export interface SystemMetrics {
  cpu_pct: number
  mem_pct: number
  mem_used_gb: number
  mem_total_gb: number
  disk_pct: number
  disk_used_gb: number
  disk_total_gb: number
  net_down_mbps: number
  net_up_mbps: number
  net_total_recv_gb: number
  net_total_sent_gb: number
  connections: number
  packets_recv: number
  packets_sent: number
  hostname: string
  os: string
  uptime: string
}

interface Ok {
  ok: boolean
}
