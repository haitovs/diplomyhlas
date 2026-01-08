"""
Live Capture Module - Real-time network packet capture
"""

import threading
import queue
from typing import Optional, Callable
from datetime import datetime

try:
    from scapy.all import sniff, IP, TCP, UDP, conf
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False


class LiveCapture:
    """Real-time network packet capture with feature extraction"""
    
    def __init__(self, interface: Optional[str] = None):
        self.interface = interface or conf.iface
        self.packet_queue = queue.Queue(maxsize=10000)
        self.running = False
        self.thread = None
        self.packet_count = 0
        self.start_time = None
        self.callbacks = []
    
    def get_interfaces(self) -> list:
        """Get available network interfaces"""
        if not SCAPY_AVAILABLE:
            return []
        try:
            from scapy.all import get_if_list
            return get_if_list()
        except:
            return ['eth0', 'wlan0']
    
    def start(self, interface: Optional[str] = None):
        """Start capturing packets in background"""
        if not SCAPY_AVAILABLE:
            raise ImportError("scapy required: pip install scapy")
        
        if interface:
            self.interface = interface
        
        self.running = True
        self.start_time = datetime.now()
        self.packet_count = 0
        
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop capturing"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
    
    def _capture_loop(self):
        """Capture loop running in background"""
        try:
            sniff(
                iface=self.interface,
                prn=self._process_packet,
                store=False,
                stop_filter=lambda x: not self.running
            )
        except Exception as e:
            print(f"Capture error: {e}")
    
    def _process_packet(self, packet):
        """Process and queue packet"""
        if IP not in packet:
            return
        
        ip = packet[IP]
        
        pkt_info = {
            'timestamp': datetime.now(),
            'src_ip': ip.src,
            'dst_ip': ip.dst,
            'protocol': 'TCP' if TCP in packet else 'UDP' if UDP in packet else 'Other',
            'src_port': packet[TCP].sport if TCP in packet else (packet[UDP].sport if UDP in packet else 0),
            'dst_port': packet[TCP].dport if TCP in packet else (packet[UDP].dport if UDP in packet else 0),
            'length': len(packet),
        }
        
        self.packet_count += 1
        
        try:
            self.packet_queue.put_nowait(pkt_info)
        except queue.Full:
            self.packet_queue.get()  # Remove oldest
            self.packet_queue.put_nowait(pkt_info)
        
        for callback in self.callbacks:
            callback(pkt_info)
    
    def get_packets(self, max_count: int = 100) -> list:
        """Get queued packets"""
        packets = []
        while len(packets) < max_count and not self.packet_queue.empty():
            try:
                packets.append(self.packet_queue.get_nowait())
            except queue.Empty:
                break
        return packets
    
    def get_stats(self) -> dict:
        """Get capture statistics"""
        elapsed = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        return {
            'interface': self.interface,
            'running': self.running,
            'packet_count': self.packet_count,
            'packets_per_sec': self.packet_count / max(elapsed, 1),
            'elapsed_seconds': elapsed,
            'queue_size': self.packet_queue.qsize(),
        }
    
    def add_callback(self, callback: Callable):
        """Add packet callback function"""
        self.callbacks.append(callback)
