"""
Network Capture Module
Captures real network traffic from selected interface
"""

import subprocess
import re
from typing import List, Dict, Optional, Generator
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


def get_windows_interfaces() -> List[NetworkInterface]:
    """Get network interfaces on Windows using PowerShell"""
    interfaces = []
    
    try:
        # Use PowerShell to get network adapters
        cmd = 'powershell "Get-NetAdapter | Where-Object {$_.Status -eq \'Up\'} | Select-Object Name, InterfaceDescription, MacAddress | ConvertTo-Json"'
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        if result.returncode == 0 and result.stdout.strip():
            import json
            adapters = json.loads(result.stdout)
            
            # Handle single adapter case
            if isinstance(adapters, dict):
                adapters = [adapters]
            
            for adapter in adapters:
                name = adapter.get('Name', 'Unknown')
                desc = adapter.get('InterfaceDescription', name)
                
                # Get IP address
                ip_cmd = f'powershell "(Get-NetIPAddress -InterfaceAlias \'{name}\' -AddressFamily IPv4 -ErrorAction SilentlyContinue).IPAddress"'
                ip_result = subprocess.run(ip_cmd, capture_output=True, text=True, shell=True)
                ip = ip_result.stdout.strip() if ip_result.returncode == 0 else "N/A"
                
                interfaces.append(NetworkInterface(name=name, ip=ip, description=desc))
    
    except Exception as e:
        print(f"Error getting interfaces: {e}")
    
    # Add common fallback interfaces
    if not interfaces:
        interfaces = [
            NetworkInterface("Wi-Fi", description="Wireless Network"),
            NetworkInterface("Ethernet", description="Wired Network"),
        ]
    
    return interfaces


def get_available_interfaces() -> List[NetworkInterface]:
    """Get list of available network interfaces"""
    if SCAPY_AVAILABLE:
        try:
            ifaces = get_if_list()
            return [NetworkInterface(name=iface, ip=get_if_addr(iface)) for iface in ifaces if iface]
        except:
            pass
    
    # Fallback to Windows method
    return get_windows_interfaces()


class PacketCapture:
    """Captures network packets from a specific interface"""
    
    def __init__(self, interface: str = None):
        self.interface = interface
        self.packet_queue = queue.Queue(maxsize=1000)
        self.running = False
        self.capture_thread = None
        self.packet_count = 0
        self.start_time = None
    
    def _packet_callback(self, packet):
        """Process captured packet"""
        if not self.running:
            return
        
        try:
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


class SimulatedCapture:
    """Simulated packet capture for when Scapy is not available"""
    
    def __init__(self, interface: str = None):
        self.interface = interface
        self.running = False
        self.packet_queue = queue.Queue(maxsize=500)
        self.packet_count = 0
        self.start_time = None
        self.generator_thread = None
    
    def _generate_packet(self) -> Dict:
        """Generate a simulated packet"""
        import random
        
        protocols = ['TCP', 'UDP', 'ICMP']
        protocol = random.choices(protocols, weights=[0.75, 0.20, 0.05])[0]
        
        return {
            'timestamp': datetime.now(),
            'src_ip': f"192.168.1.{random.randint(1, 254)}",
            'dst_ip': f"10.0.0.{random.randint(1, 254)}",
            'src_port': random.randint(49152, 65535),
            'dst_port': random.choice([80, 443, 53, 22, 3389]),
            'protocol': protocol,
            'total_bytes': random.randint(64, 1500),
            'fwd_packets': 1,
            'bwd_packets': 0,
            'fwd_bytes': random.randint(64, 1500),
            'bwd_bytes': 0,
            'duration': random.uniform(0, 1000),
            'packets_per_sec': random.uniform(1, 100),
            'bytes_per_sec': random.uniform(100, 10000),
            'label': 'SIMULATED',
            'is_attack': False,
            'is_live': True
        }
    
    def _generator_loop(self):
        """Generate packets in background"""
        while self.running:
            try:
                packet = self._generate_packet()
                self.packet_queue.put(packet, block=False)
                self.packet_count += 1
            except queue.Full:
                pass
            time.sleep(0.05)  # ~20 packets/second
    
    def start(self):
        """Start simulated capture"""
        self.running = True
        self.start_time = datetime.now()
        self.packet_count = 0
        
        self.generator_thread = threading.Thread(target=self._generator_loop, daemon=True)
        self.generator_thread.start()
        print(f"Started SIMULATED capture (Scapy not available)")
    
    def stop(self):
        """Stop capture"""
        self.running = False
        if self.generator_thread:
            self.generator_thread.join(timeout=2)
    
    def get_packets(self, max_packets: int = 50) -> List[Dict]:
        """Get packets from queue"""
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
            'interface': f"{self.interface} (SIMULATED)",
            'packet_count': self.packet_count,
            'elapsed_seconds': elapsed,
            'packets_per_second': self.packet_count / max(elapsed, 1),
            'queue_size': self.packet_queue.qsize()
        }


def create_capture(interface: str = None) -> PacketCapture:
    """Factory function to create appropriate capture object"""
    if SCAPY_AVAILABLE:
        return PacketCapture(interface)
    else:
        return SimulatedCapture(interface)


if __name__ == "__main__":
    # Test interface detection
    print("Available network interfaces:")
    for iface in get_available_interfaces():
        print(f"  - {iface.name}: {iface.ip} ({iface.description})")
    
    print(f"\nScapy available: {SCAPY_AVAILABLE}")
