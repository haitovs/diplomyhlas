"""
PCAP Analyzer - Extract network features from PCAP files
Compatible with CICIDS2017 dataset format
"""

from pathlib import Path
from typing import Optional, Dict, List
from collections import defaultdict
import pandas as pd
import numpy as np

try:
    from scapy.all import rdpcap, PcapReader, IP, TCP, UDP, Raw
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False


class PcapAnalyzer:
    """Analyze PCAP files and extract flow-based features"""
    
    PROTOCOL_MAP = {1: 'ICMP', 6: 'TCP', 17: 'UDP'}
    
    def __init__(self, flow_timeout: float = 120.0):
        self.flow_timeout = flow_timeout
        self.flows = {}
    
    def analyze(self, filepath: str, max_packets: Optional[int] = None) -> pd.DataFrame:
        """Load PCAP and extract features"""
        if not SCAPY_AVAILABLE:
            raise ImportError("scapy required: pip install scapy")
        
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        self.flows.clear()
        packet_count = 0
        
        with PcapReader(str(filepath)) as reader:
            for packet in reader:
                if max_packets and packet_count >= max_packets:
                    break
                self._process_packet(packet)
                packet_count += 1
        
        return self._extract_features()
    
    def _process_packet(self, packet):
        """Process single packet into flow"""
        if IP not in packet:
            return
        
        ip = packet[IP]
        src_ip, dst_ip = ip.src, ip.dst
        protocol = ip.proto
        timestamp = float(packet.time)
        
        src_port = dst_port = 0
        flags = {}
        
        if TCP in packet:
            tcp = packet[TCP]
            src_port, dst_port = tcp.sport, tcp.dport
            flags = {
                'SYN': bool(tcp.flags & 0x02),
                'ACK': bool(tcp.flags & 0x10),
                'FIN': bool(tcp.flags & 0x01),
                'RST': bool(tcp.flags & 0x04),
                'PSH': bool(tcp.flags & 0x08),
            }
        elif UDP in packet:
            udp = packet[UDP]
            src_port, dst_port = udp.sport, udp.dport
        
        # Create bidirectional flow key
        key = tuple(sorted([(src_ip, src_port), (dst_ip, dst_port)])) + (protocol,)
        is_forward = (src_ip, src_port) <= (dst_ip, dst_port)
        
        pkt_info = {
            'timestamp': timestamp,
            'length': len(packet),
            'payload': len(packet[Raw].load) if Raw in packet else 0,
            'flags': flags,
        }
        
        if key not in self.flows:
            self.flows[key] = {
                'src_ip': src_ip, 'dst_ip': dst_ip,
                'src_port': src_port, 'dst_port': dst_port,
                'protocol': protocol, 'start': timestamp,
                'fwd': [], 'bwd': [], 'fwd_iat': [], 'bwd_iat': [],
                'last_fwd': timestamp, 'last_bwd': timestamp,
                'syn': 0, 'ack': 0, 'fin': 0, 'rst': 0, 'psh': 0,
            }
        
        flow = self.flows[key]
        flow['end'] = timestamp
        
        if is_forward:
            if flow['fwd']:
                flow['fwd_iat'].append(timestamp - flow['last_fwd'])
            flow['last_fwd'] = timestamp
            flow['fwd'].append(pkt_info)
        else:
            if flow['bwd']:
                flow['bwd_iat'].append(timestamp - flow['last_bwd'])
            flow['last_bwd'] = timestamp
            flow['bwd'].append(pkt_info)
        
        # Count flags
        for flag in ['syn', 'ack', 'fin', 'rst', 'psh']:
            if flags.get(flag.upper()):
                flow[flag] += 1
    
    def _extract_features(self) -> pd.DataFrame:
        """Extract CICIDS2017-compatible features from flows"""
        features = []
        
        for key, f in self.flows.items():
            duration = max(f.get('end', f['start']) - f['start'], 1e-6)
            
            fwd_lens = [p['length'] for p in f['fwd']]
            bwd_lens = [p['length'] for p in f['bwd']]
            all_lens = fwd_lens + bwd_lens
            
            features.append({
                'src_ip': f['src_ip'], 'dst_ip': f['dst_ip'],
                'src_port': f['src_port'], 'dst_port': f['dst_port'],
                'protocol': self.PROTOCOL_MAP.get(f['protocol'], 'Other'),
                'flow_duration': duration * 1e6,
                'total_fwd_packets': len(f['fwd']),
                'total_bwd_packets': len(f['bwd']),
                'total_fwd_bytes': sum(fwd_lens),
                'total_bwd_bytes': sum(bwd_lens),
                'fwd_packet_mean': np.mean(fwd_lens) if fwd_lens else 0,
                'bwd_packet_mean': np.mean(bwd_lens) if bwd_lens else 0,
                'flow_bytes_per_s': sum(all_lens) / duration,
                'flow_packets_per_s': len(all_lens) / duration,
                'fwd_iat_mean': np.mean(f['fwd_iat']) * 1e6 if f['fwd_iat'] else 0,
                'bwd_iat_mean': np.mean(f['bwd_iat']) * 1e6 if f['bwd_iat'] else 0,
                'syn_count': f['syn'], 'ack_count': f['ack'],
                'fin_count': f['fin'], 'rst_count': f['rst'],
                'psh_count': f['psh'],
                'packet_mean': np.mean(all_lens) if all_lens else 0,
                'packet_std': np.std(all_lens) if len(all_lens) > 1 else 0,
            })
        
        return pd.DataFrame(features) if features else pd.DataFrame()
    
    def get_summary(self) -> Dict:
        """Get analysis summary"""
        df = self._extract_features()
        if df.empty:
            return {'status': 'No flows'}
        
        return {
            'total_flows': len(df),
            'total_packets': df['total_fwd_packets'].sum() + df['total_bwd_packets'].sum(),
            'unique_ips': df['src_ip'].nunique() + df['dst_ip'].nunique(),
            'protocols': df['protocol'].value_counts().to_dict(),
        }
