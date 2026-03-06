"""
Flow Aggregator - Groups raw packets into bidirectional flows and
extracts all 74 CICIDS2017-compatible features for ML inference.

Usage:
    aggregator = FlowAggregator()
    # In packet callback:
    aggregator.add_packet(scapy_packet)
    # Periodically:
    finished_flows = aggregator.flush()
    # Each flow dict has keys matching feature_columns.joblib
"""

import threading
import time
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple

try:
    from scapy.all import IP, TCP, UDP, ICMP, Raw
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False


# Timeouts
IDLE_TIMEOUT = 3.0     # seconds without a packet → flush
ACTIVE_TIMEOUT = 30.0  # max flow lifetime


class _FlowState:
    """Internal state for a single bidirectional flow."""
    __slots__ = [
        'src_ip', 'dst_ip', 'src_port', 'dst_port', 'protocol',
        'start_time', 'last_time',
        'fwd_lengths', 'bwd_lengths',
        'fwd_timestamps', 'bwd_timestamps',
        'fwd_header_lens', 'bwd_header_lens',
        'fwd_psh', 'fwd_urg',
        'fin', 'syn', 'rst', 'psh', 'ack', 'urg', 'cwe', 'ece',
        'init_win_fwd', 'init_win_bwd',
        'fwd_act_data_pkts',
        'active_times', 'idle_times',
        '_last_active_start', '_last_active_end',
    ]

    def __init__(self, src_ip, dst_ip, src_port, dst_port, protocol, ts):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.src_port = src_port
        self.dst_port = dst_port
        self.protocol = protocol
        self.start_time = ts
        self.last_time = ts

        self.fwd_lengths: List[int] = []
        self.bwd_lengths: List[int] = []
        self.fwd_timestamps: List[float] = []
        self.bwd_timestamps: List[float] = []
        self.fwd_header_lens: List[int] = []
        self.bwd_header_lens: List[int] = []

        self.fwd_psh = 0
        self.fwd_urg = 0

        # TCP flag counters (overall)
        self.fin = 0
        self.syn = 0
        self.rst = 0
        self.psh = 0
        self.ack = 0
        self.urg = 0
        self.cwe = 0
        self.ece = 0

        self.init_win_fwd = -1
        self.init_win_bwd = -1
        self.fwd_act_data_pkts = 0

        self.active_times: List[float] = []
        self.idle_times: List[float] = []
        self._last_active_start = ts
        self._last_active_end = ts


def _safe_stats(values):
    """Return (mean, std, max, min, total) for a list; zeros if empty."""
    if not values:
        return 0.0, 0.0, 0.0, 0.0, 0.0
    a = np.array(values, dtype=np.float64)
    return float(a.mean()), float(a.std()), float(a.max()), float(a.min()), float(a.sum())


class FlowAggregator:
    """Thread-safe flow aggregator producing CICIDS2017-compatible feature dicts."""

    def __init__(self, idle_timeout: float = IDLE_TIMEOUT,
                 active_timeout: float = ACTIVE_TIMEOUT):
        self.idle_timeout = idle_timeout
        self.active_timeout = active_timeout
        self._flows: Dict[tuple, _FlowState] = {}
        self._lock = threading.Lock()

    # ── Public API ────────────────────────────────────────────────────────

    def add_packet(self, packet) -> None:
        """Ingest a raw Scapy packet.  Called from the capture thread."""
        if not packet.haslayer(IP):
            return

        ip = packet[IP]
        src_ip, dst_ip = ip.src, ip.dst
        protocol = ip.proto
        ts = time.time()
        pkt_len = len(packet)

        src_port = dst_port = 0
        tcp_flags_int = 0
        header_len = (ip.ihl or 5) * 4  # IP header length
        win_size = -1

        if packet.haslayer(TCP):
            tcp = packet[TCP]
            src_port, dst_port = tcp.sport, tcp.dport
            tcp_flags_int = int(tcp.flags)
            header_len += (tcp.dataofs or 5) * 4
            win_size = tcp.window
        elif packet.haslayer(UDP):
            udp = packet[UDP]
            src_port, dst_port = udp.sport, udp.dport
            header_len += 8

        has_payload = packet.haslayer(Raw) and len(packet[Raw].load) > 0

        # Bidirectional key: sort endpoints so (A→B) and (B→A) share same flow
        ep1 = (src_ip, src_port)
        ep2 = (dst_ip, dst_port)
        if ep1 <= ep2:
            key = (ep1, ep2, protocol)
            is_forward = True
        else:
            key = (ep2, ep1, protocol)
            is_forward = False

        with self._lock:
            if key not in self._flows:
                self._flows[key] = _FlowState(
                    src_ip, dst_ip, src_port, dst_port, protocol, ts
                )

            f = self._flows[key]
            f.last_time = ts

            # Active / idle tracking (1-second threshold)
            gap = ts - f._last_active_end
            if gap > 1.0:
                active_duration = f._last_active_end - f._last_active_start
                if active_duration > 0:
                    f.active_times.append(active_duration)
                f.idle_times.append(gap)
                f._last_active_start = ts
            f._last_active_end = ts

            if is_forward:
                f.fwd_lengths.append(pkt_len)
                f.fwd_timestamps.append(ts)
                f.fwd_header_lens.append(header_len)
                if win_size >= 0 and f.init_win_fwd < 0:
                    f.init_win_fwd = win_size
                if has_payload:
                    f.fwd_act_data_pkts += 1
                if tcp_flags_int & 0x08:  # PSH
                    f.fwd_psh += 1
                if tcp_flags_int & 0x20:  # URG
                    f.fwd_urg += 1
            else:
                f.bwd_lengths.append(pkt_len)
                f.bwd_timestamps.append(ts)
                f.bwd_header_lens.append(header_len)
                if win_size >= 0 and f.init_win_bwd < 0:
                    f.init_win_bwd = win_size

            # Global TCP flag counts
            if tcp_flags_int & 0x01:
                f.fin += 1
            if tcp_flags_int & 0x02:
                f.syn += 1
            if tcp_flags_int & 0x04:
                f.rst += 1
            if tcp_flags_int & 0x08:
                f.psh += 1
            if tcp_flags_int & 0x10:
                f.ack += 1
            if tcp_flags_int & 0x20:
                f.urg += 1
            if tcp_flags_int & 0x40:
                f.ece += 1
            if tcp_flags_int & 0x80:
                f.cwe += 1

    def flush(self) -> List[Dict]:
        """Flush flows that are idle or exceeded active timeout.
        Returns list of CICIDS2017-feature dicts ready for ML."""
        now = time.time()
        finished = []

        with self._lock:
            expired_keys = [
                k for k, f in self._flows.items()
                if (now - f.last_time > self.idle_timeout)
                   or (now - f.start_time > self.active_timeout)
            ]
            for k in expired_keys:
                f = self._flows.pop(k)
                features = self._extract_features(f)
                if features:
                    finished.append(features)

        return finished

    def flush_all(self) -> List[Dict]:
        """Force-flush every active flow (e.g. on stop)."""
        with self._lock:
            flows = list(self._flows.values())
            self._flows.clear()

        result = []
        for f in flows:
            features = self._extract_features(f)
            if features:
                result.append(features)
        return result

    def active_flow_count(self) -> int:
        with self._lock:
            return len(self._flows)

    # ── Feature extraction ────────────────────────────────────────────────

    def _extract_features(self, f: _FlowState) -> Optional[Dict]:
        """Convert a _FlowState into a dict with all 74 CICIDS2017 feature names."""

        total_fwd = len(f.fwd_lengths)
        total_bwd = len(f.bwd_lengths)
        total_pkts = total_fwd + total_bwd
        if total_pkts == 0:
            return None

        duration_sec = max(f.last_time - f.start_time, 1e-6)
        duration_us = duration_sec * 1e6

        fwd_mean, fwd_std, fwd_max, fwd_min, fwd_total = _safe_stats(f.fwd_lengths)
        bwd_mean, bwd_std, bwd_max, bwd_min, bwd_total = _safe_stats(f.bwd_lengths)

        all_lengths = f.fwd_lengths + f.bwd_lengths
        pkt_mean, pkt_std, pkt_max, pkt_min, pkt_total = _safe_stats(all_lengths)
        pkt_var = float(np.var(all_lengths)) if all_lengths else 0.0

        # IAT (inter-arrival time) in microseconds
        def iat_from_timestamps(ts_list):
            if len(ts_list) < 2:
                return []
            a = np.array(ts_list)
            return ((a[1:] - a[:-1]) * 1e6).tolist()

        fwd_iat = iat_from_timestamps(f.fwd_timestamps)
        bwd_iat = iat_from_timestamps(f.bwd_timestamps)
        all_ts = sorted(f.fwd_timestamps + f.bwd_timestamps)
        flow_iat = iat_from_timestamps(all_ts)

        fwd_iat_mean, fwd_iat_std, fwd_iat_max, fwd_iat_min, fwd_iat_total = _safe_stats(fwd_iat)
        bwd_iat_mean, bwd_iat_std, bwd_iat_max, bwd_iat_min, bwd_iat_total = _safe_stats(bwd_iat)
        flow_iat_mean, flow_iat_std, flow_iat_max, flow_iat_min, _ = _safe_stats(flow_iat)

        flow_bytes_per_s = pkt_total / duration_sec
        flow_pkts_per_s = total_pkts / duration_sec
        fwd_pkts_per_s = total_fwd / duration_sec
        bwd_pkts_per_s = total_bwd / duration_sec

        down_up = (total_bwd / total_fwd) if total_fwd > 0 else 0.0
        avg_pkt_size = pkt_total / total_pkts if total_pkts > 0 else 0.0

        fwd_hdr_total = sum(f.fwd_header_lens) if f.fwd_header_lens else 0
        bwd_hdr_total = sum(f.bwd_header_lens) if f.bwd_header_lens else 0

        # Active / idle stats (in microseconds)
        active_us = [t * 1e6 for t in f.active_times]
        idle_us = [t * 1e6 for t in f.idle_times]
        act_mean, act_std, act_max, act_min, _ = _safe_stats(active_us)
        idle_mean, idle_std, idle_max, idle_min, _ = _safe_stats(idle_us)

        # min_seg_size_forward = min forward header length
        min_seg_fwd = min(f.fwd_header_lens) if f.fwd_header_lens else 0

        features = {
            # ---- Exactly the 74 features from feature_columns.joblib ----
            'Flow Duration': duration_us,
            'Total Fwd Packets': total_fwd,
            'Total Backward Packets': total_bwd,
            'Total Length of Fwd Packets': fwd_total,
            'Total Length of Bwd Packets': bwd_total,
            'Fwd Packet Length Max': fwd_max,
            'Fwd Packet Length Min': fwd_min,
            'Fwd Packet Length Mean': fwd_mean,
            'Fwd Packet Length Std': fwd_std,
            'Bwd Packet Length Max': bwd_max,
            'Bwd Packet Length Min': bwd_min,
            'Bwd Packet Length Mean': bwd_mean,
            'Bwd Packet Length Std': bwd_std,
            'Flow Bytes/s': flow_bytes_per_s,
            'Flow Packets/s': flow_pkts_per_s,
            'Flow IAT Mean': flow_iat_mean,
            'Flow IAT Std': flow_iat_std,
            'Flow IAT Max': flow_iat_max,
            'Flow IAT Min': flow_iat_min,
            'Fwd IAT Total': fwd_iat_total,
            'Fwd IAT Mean': fwd_iat_mean,
            'Fwd IAT Std': fwd_iat_std,
            'Fwd IAT Max': fwd_iat_max,
            'Fwd IAT Min': fwd_iat_min,
            'Bwd IAT Total': bwd_iat_total,
            'Bwd IAT Mean': bwd_iat_mean,
            'Bwd IAT Std': bwd_iat_std,
            'Bwd IAT Max': bwd_iat_max,
            'Bwd IAT Min': bwd_iat_min,
            'Fwd PSH Flags': f.fwd_psh,
            'Fwd URG Flags': f.fwd_urg,
            'Fwd Header Length': fwd_hdr_total,
            'Bwd Header Length': bwd_hdr_total,
            'Fwd Packets/s': fwd_pkts_per_s,
            'Bwd Packets/s': bwd_pkts_per_s,
            'Min Packet Length': pkt_min,
            'Max Packet Length': pkt_max,
            'Packet Length Mean': pkt_mean,
            'Packet Length Std': pkt_std,
            'Packet Length Variance': pkt_var,
            'FIN Flag Count': f.fin,
            'SYN Flag Count': f.syn,
            'RST Flag Count': f.rst,
            'PSH Flag Count': f.psh,
            'ACK Flag Count': f.ack,
            'URG Flag Count': f.urg,
            'CWE Flag Count': f.cwe,
            'ECE Flag Count': f.ece,
            'Down/Up Ratio': down_up,
            'Average Packet Size': avg_pkt_size,
            'Avg Fwd Segment Size': fwd_mean,     # same as fwd pkt len mean
            'Avg Bwd Segment Size': bwd_mean,     # same as bwd pkt len mean
            'Fwd Avg Bytes/Bulk': 0,               # bulk metrics not available per-packet
            'Fwd Avg Packets/Bulk': 0,
            'Fwd Avg Bulk Rate': 0,
            'Bwd Avg Bytes/Bulk': 0,
            'Bwd Avg Packets/Bulk': 0,
            'Bwd Avg Bulk Rate': 0,
            'Subflow Fwd Packets': total_fwd,
            'Subflow Fwd Bytes': fwd_total,
            'Subflow Bwd Packets': total_bwd,
            'Subflow Bwd Bytes': bwd_total,
            'Init_Win_bytes_forward': f.init_win_fwd if f.init_win_fwd >= 0 else 0,
            'Init_Win_bytes_backward': f.init_win_bwd if f.init_win_bwd >= 0 else 0,
            'act_data_pkt_fwd': f.fwd_act_data_pkts,
            'min_seg_size_forward': min_seg_fwd,
            'Active Mean': act_mean,
            'Active Std': act_std,
            'Active Max': act_max,
            'Active Min': act_min,
            'Idle Mean': idle_mean,
            'Idle Std': idle_std,
            'Idle Max': idle_max,
            'Idle Min': idle_min,
        }

        # ── Metadata (not fed to ML, but useful for display) ──
        proto_map = {1: 'ICMP', 6: 'TCP', 17: 'UDP'}
        features['_meta'] = {
            'src_ip': f.src_ip,
            'dst_ip': f.dst_ip,
            'src_port': f.src_port,
            'dst_port': f.dst_port,
            'protocol': proto_map.get(f.protocol, 'OTHER'),
            'timestamp': datetime.now(),
            'is_live': True,
        }

        return features
