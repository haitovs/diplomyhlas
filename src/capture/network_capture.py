"""
Network Capture Module
Captures real network traffic from selected interface
"""

import subprocess
import re
from typing import List, Dict, Optional, Callable
from datetime import datetime
import threading
import queue
import time

# Try to import scapy (may need admin rights)
try:
    from scapy.all import sniff, get_if_list, get_if_addr, IP, TCP, UDP, ICMP, Raw
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("Warning: Scapy not available. Install with: pip install scapy")


class NetworkInterface:
    """Represents a network interface"""
    def __init__(self, name: str, ip: str = None, description: str = None):
        self.name = name
        self.ip = ip or "N/A"
        self.description = description or name


def get_available_interfaces() -> List[NetworkInterface]:
    """Get list of available network interfaces"""
    if SCAPY_AVAILABLE:
        try:
            ifaces = get_if_list()
            return [NetworkInterface(name=iface, ip=get_if_addr(iface)) for iface in ifaces if iface]
        except:
            pass

    # Fallback
    return [
        NetworkInterface("lo0", ip="127.0.0.1", description="Loopback"),
    ]


class PacketCapture:
    """Captures network packets from a specific interface"""

    def __init__(self, interface: str = None, packet_processor: Callable = None):
        self.interface = interface
        self.packet_queue = queue.Queue(maxsize=1000)
        self.running = False
        self.capture_thread = None
        self.packet_count = 0
        self.start_time = None
        self.packet_processor = packet_processor

    def _packet_callback(self, packet):
        """Process captured packet"""
        if not self.running:
            return

        try:
            # If an external processor is set (e.g. FlowAggregator), send raw packet
            if self.packet_processor:
                self.packet_processor(packet)
                self.packet_count += 1
                return

            flow = self._extract_flow_features(packet)
            if flow:
                self.packet_queue.put(flow, block=False)
                self.packet_count += 1
        except queue.Full:
            pass  # Drop packet if queue is full
        except Exception as e:
            pass  # Silently ignore malformed packets

    def _extract_flow_features(self, packet) -> Optional[Dict]:
        """Extract features from a packet"""
        if not packet.haslayer(IP):
            return None

        ip_layer = packet[IP]

        # Basic flow info
        flow = {
            'timestamp': datetime.now(),
            'src_ip': ip_layer.src,
            'dst_ip': ip_layer.dst,
            'src_port': 0,
            'dst_port': 0,
            'protocol': 'OTHER',
            'total_bytes': len(packet),
            'fwd_packets': 1,
            'bwd_packets': 0,
            'fwd_bytes': len(packet),
            'bwd_bytes': 0,
            'duration': 0,
            'packets_per_sec': 0,
            'bytes_per_sec': 0,
            'label': 'CAPTURED',
            'is_attack': False,
            'is_live': True
        }

        # TCP/UDP specific
        if packet.haslayer(TCP):
            tcp = packet[TCP]
            flow['protocol'] = 'TCP'
            flow['src_port'] = tcp.sport
            flow['dst_port'] = tcp.dport
            flow['tcp_flags'] = str(tcp.flags)
        elif packet.haslayer(UDP):
            udp = packet[UDP]
            flow['protocol'] = 'UDP'
            flow['src_port'] = udp.sport
            flow['dst_port'] = udp.dport
        elif packet.haslayer(ICMP):
            flow['protocol'] = 'ICMP'

        return flow

    def start(self):
        """Start packet capture in background thread"""
        if not SCAPY_AVAILABLE:
            raise RuntimeError("Scapy not available. Install with: pip install scapy")

        self.running = True
        self.start_time = datetime.now()
        self.packet_count = 0

        def capture_loop():
            try:
                sniff(
                    iface=self.interface,
                    prn=self._packet_callback,
                    store=False,
                    stop_filter=lambda x: not self.running
                )
            except Exception as e:
                print(f"Capture error: {e}")
                self.running = False

        self.capture_thread = threading.Thread(target=capture_loop, daemon=True)
        self.capture_thread.start()
        print(f"Started capture on {self.interface}")

    def stop(self):
        """Stop packet capture"""
        self.running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
        print(f"Stopped capture. Total packets: {self.packet_count}")

    def get_packets(self, max_packets: int = 50) -> List[Dict]:
        """Get captured packets from queue"""
        packets = []
        try:
            while len(packets) < max_packets:
                packet = self.packet_queue.get_nowait()
                packets.append(packet)
        except queue.Empty:
            pass
        return packets

    def get_stats(self) -> Dict:
        """Get capture statistics"""
        elapsed = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        return {
            'running': self.running,
            'interface': self.interface,
            'packet_count': self.packet_count,
            'elapsed_seconds': elapsed,
            'packets_per_second': self.packet_count / max(elapsed, 1),
            'queue_size': self.packet_queue.qsize()
        }


if __name__ == "__main__":
    # Test interface detection
    print("Available network interfaces:")
    for iface in get_available_interfaces():
        print(f"  - {iface.name}: {iface.ip} ({iface.description})")

    print(f"\nScapy available: {SCAPY_AVAILABLE}")
