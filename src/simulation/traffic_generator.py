"""
Traffic Generator Module
Generates realistic network traffic patterns for simulation
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Generator, Dict, List
import time
import random


class TrafficGenerator:
    """Generates realistic network traffic flows"""
    
    # IP ranges for simulation
    INTERNAL_SUBNETS = ['192.168.1', '192.168.2', '10.0.0', '172.16.0']
    EXTERNAL_IPS = [
        '8.8.8.8', '1.1.1.1', '208.67.222.222',  # DNS
        '151.101.1.140', '104.244.42.1',  # CDN
        '13.107.42.14', '20.190.128.0',  # Microsoft
        '172.217.14.206', '142.250.80.46',  # Google
    ]
    
    # Protocol distribution (realistic)
    PROTOCOLS = {
        'TCP': 0.75,
        'UDP': 0.20,
        'ICMP': 0.05
    }
    
    # Common ports
    COMMON_PORTS = {
        80: 0.25,    # HTTP
        443: 0.40,   # HTTPS
        53: 0.10,    # DNS
        22: 0.05,    # SSH
        3389: 0.03,  # RDP
        445: 0.02,   # SMB
        25: 0.02,    # SMTP
        21: 0.01,    # FTP
    }
    
    def __init__(self, seed: int = None):
        if seed:
            np.random.seed(seed)
            random.seed(seed)
        
        self.flow_id = 0
        self.start_time = datetime.now()
        
    def _get_time_factor(self) -> float:
        """Get traffic multiplier based on time of day"""
        hour = datetime.now().hour
        # Peak hours: 9-17 (business hours)
        if 9 <= hour <= 17:
            return 1.0 + np.random.uniform(0, 0.3)
        # Evening: 18-22
        elif 18 <= hour <= 22:
            return 0.7 + np.random.uniform(0, 0.2)
        # Night: 23-6
        else:
            return 0.3 + np.random.uniform(0, 0.1)
    
    def _generate_ip(self, internal: bool = True) -> str:
        """Generate random IP address"""
        if internal:
            subnet = random.choice(self.INTERNAL_SUBNETS)
            return f"{subnet}.{random.randint(1, 254)}"
        else:
            if random.random() < 0.3:
                return random.choice(self.EXTERNAL_IPS)
            return f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
    
    def _generate_port(self) -> int:
        """Generate destination port based on realistic distribution"""
        if random.random() < 0.85:
            ports = list(self.COMMON_PORTS.keys())
            weights = list(self.COMMON_PORTS.values())
            return random.choices(ports, weights=weights)[0]
        return random.randint(1024, 65535)
    
    def _generate_protocol(self) -> str:
        """Generate protocol based on distribution"""
        return random.choices(
            list(self.PROTOCOLS.keys()),
            weights=list(self.PROTOCOLS.values())
        )[0]
    
    def generate_flow(self) -> Dict:
        """Generate a single network flow"""
        self.flow_id += 1
        
        # Direction: internal-to-external (outbound) or internal (lateral)
        is_outbound = random.random() < 0.7
        
        src_ip = self._generate_ip(internal=True)
        dst_ip = self._generate_ip(internal=not is_outbound)
        
        protocol = self._generate_protocol()
        dst_port = self._generate_port()
        src_port = random.randint(49152, 65535)  # Ephemeral port
        
        # Flow characteristics vary by protocol
        if protocol == 'TCP':
            duration = np.random.exponential(5000)  # ms
            fwd_packets = max(1, int(np.random.exponential(10)))
            bwd_packets = max(0, int(np.random.exponential(8)))
        elif protocol == 'UDP':
            duration = np.random.exponential(1000)
            fwd_packets = max(1, int(np.random.poisson(5)))
            bwd_packets = max(0, int(np.random.poisson(3)))
        else:  # ICMP
            duration = np.random.exponential(500)
            fwd_packets = random.randint(1, 4)
            bwd_packets = random.randint(0, 2)
        
        # Packet sizes
        fwd_bytes = fwd_packets * int(np.random.exponential(500))
        bwd_bytes = bwd_packets * int(np.random.exponential(400))
        
        return {
            'flow_id': self.flow_id,
            'timestamp': datetime.now(),
            'src_ip': src_ip,
            'src_port': src_port,
            'dst_ip': dst_ip,
            'dst_port': dst_port,
            'protocol': protocol,
            'duration': duration,
            'fwd_packets': fwd_packets,
            'bwd_packets': bwd_packets,
            'fwd_bytes': fwd_bytes,
            'bwd_bytes': bwd_bytes,
            'total_bytes': fwd_bytes + bwd_bytes,
            'packets_per_sec': (fwd_packets + bwd_packets) / max(duration / 1000, 0.001),
            'bytes_per_sec': (fwd_bytes + bwd_bytes) / max(duration / 1000, 0.001),
            'label': 'BENIGN',
            'is_attack': False
        }
    
    def generate_batch(self, n: int = 10) -> List[Dict]:
        """Generate a batch of flows"""
        time_factor = self._get_time_factor()
        adjusted_n = int(n * time_factor)
        return [self.generate_flow() for _ in range(adjusted_n)]
    
    def stream(self, interval_ms: int = 100) -> Generator[Dict, None, None]:
        """Continuously stream flows"""
        while True:
            yield self.generate_flow()
            time.sleep(interval_ms / 1000)


class AttackSimulator:
    """Simulates various network attacks"""
    
    def __init__(self, traffic_gen: TrafficGenerator):
        self.traffic_gen = traffic_gen
        self.attack_active = False
        self.attack_type = None
        self.attack_start = None
        self.attack_duration = 0
    
    def start_attack(self, attack_type: str, duration_sec: int = 30):
        """Start an attack simulation"""
        self.attack_active = True
        self.attack_type = attack_type
        self.attack_start = datetime.now()
        self.attack_duration = duration_sec
    
    def stop_attack(self):
        """Stop current attack"""
        self.attack_active = False
        self.attack_type = None
    
    def _check_attack_timeout(self):
        """Check if attack should end"""
        if self.attack_active and self.attack_start:
            elapsed = (datetime.now() - self.attack_start).total_seconds()
            if elapsed >= self.attack_duration:
                self.stop_attack()
    
    def generate_ddos_flow(self) -> Dict:
        """Generate DDoS attack flow"""
        flow = self.traffic_gen.generate_flow()
        
        # DDoS characteristics: high volume, short duration
        flow['fwd_packets'] = int(np.random.exponential(100))
        flow['bwd_packets'] = random.randint(0, 2)
        flow['fwd_bytes'] = flow['fwd_packets'] * int(np.random.exponential(1400))
        flow['bwd_bytes'] = flow['bwd_packets'] * 64
        flow['duration'] = np.random.exponential(100)  # Very short
        flow['packets_per_sec'] = flow['fwd_packets'] / max(flow['duration'] / 1000, 0.001)
        flow['bytes_per_sec'] = flow['fwd_bytes'] / max(flow['duration'] / 1000, 0.001)
        
        # Same destination (victim)
        flow['dst_ip'] = '192.168.1.100'
        flow['dst_port'] = random.choice([80, 443])
        
        flow['label'] = 'DDoS'
        flow['is_attack'] = True
        
        return flow
    
    def generate_portscan_flow(self) -> Dict:
        """Generate port scan flow"""
        flow = self.traffic_gen.generate_flow()
        
        # Port scan: single packet to sequential ports
        flow['fwd_packets'] = 1
        flow['bwd_packets'] = random.choice([0, 1])  # May or may not get response
        flow['fwd_bytes'] = 64
        flow['bwd_bytes'] = 64 if flow['bwd_packets'] else 0
        flow['duration'] = np.random.exponential(50)
        flow['protocol'] = 'TCP'
        
        # Sequential ports
        flow['dst_port'] = random.randint(1, 1024)
        
        flow['label'] = 'PortScan'
        flow['is_attack'] = True
        
        return flow
    
    def generate_bruteforce_flow(self) -> Dict:
        """Generate brute force attack flow (SSH/FTP)"""
        flow = self.traffic_gen.generate_flow()
        
        # Failed login attempts
        flow['fwd_packets'] = random.randint(3, 8)
        flow['bwd_packets'] = random.randint(2, 5)
        flow['fwd_bytes'] = flow['fwd_packets'] * random.randint(50, 200)
        flow['bwd_bytes'] = flow['bwd_packets'] * random.randint(30, 100)
        flow['duration'] = np.random.exponential(2000)
        flow['protocol'] = 'TCP'
        flow['dst_port'] = random.choice([22, 21, 3389])  # SSH, FTP, RDP
        
        flow['label'] = 'BruteForce'
        flow['is_attack'] = True
        
        return flow
    
    def generate_bot_flow(self) -> Dict:
        """Generate bot/C2 communication flow"""
        flow = self.traffic_gen.generate_flow()
        
        # Bot characteristics: periodic beacons, small packets
        flow['fwd_packets'] = random.randint(1, 3)
        flow['bwd_packets'] = random.randint(1, 3)
        flow['fwd_bytes'] = flow['fwd_packets'] * random.randint(50, 150)
        flow['bwd_bytes'] = flow['bwd_packets'] * random.randint(50, 500)
        flow['duration'] = np.random.exponential(1000)
        
        # External C2 server
        flow['dst_ip'] = f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
        flow['dst_port'] = random.choice([443, 8080, 4444, 6666])
        
        flow['label'] = 'Bot'
        flow['is_attack'] = True
        
        return flow
    
    def generate_flow(self) -> Dict:
        """Generate a flow based on current attack state"""
        self._check_attack_timeout()
        
        if not self.attack_active:
            return self.traffic_gen.generate_flow()
        
        # Mix attack traffic with normal traffic
        attack_prob = random.random()
        
        if attack_prob < 0.6:  # 60% attack traffic during attack
            if self.attack_type == 'DDoS':
                return self.generate_ddos_flow()
            elif self.attack_type == 'PortScan':
                return self.generate_portscan_flow()
            elif self.attack_type == 'BruteForce':
                return self.generate_bruteforce_flow()
            elif self.attack_type == 'Bot':
                return self.generate_bot_flow()
        
        return self.traffic_gen.generate_flow()
    
    def generate_batch(self, n: int = 10) -> List[Dict]:
        """Generate a batch of flows"""
        return [self.generate_flow() for _ in range(n)]


if __name__ == "__main__":
    # Test traffic generation
    gen = TrafficGenerator(seed=42)
    attacks = AttackSimulator(gen)
    
    print("=== Normal Traffic ===")
    for flow in gen.generate_batch(5):
        print(f"{flow['src_ip']}:{flow['src_port']} -> {flow['dst_ip']}:{flow['dst_port']} | {flow['protocol']} | {flow['label']}")
    
    print("\n=== DDoS Attack ===")
    attacks.start_attack('DDoS', duration_sec=10)
    for flow in attacks.generate_batch(5):
        print(f"{flow['src_ip']}:{flow['src_port']} -> {flow['dst_ip']}:{flow['dst_port']} | {flow['protocol']} | {flow['label']}")
