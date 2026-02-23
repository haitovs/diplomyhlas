"""
Generate sample datasets for demonstration purposes
Creates pre-recorded traffic scenarios for showcase demos
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.simulation.traffic_generator import TrafficGenerator, AttackSimulator
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_normal_traffic(n_flows=1000):
    """Generate clean benign traffic"""
    print("Generating normal traffic dataset...")
    gen = TrafficGenerator(seed=42)
    flows = gen.generate_batch(n_flows)
    df = pd.DataFrame(flows)
    return df

def generate_ddos_attack(n_flows=1000):
    """Generate DDoS attack scenario"""
    print("Generating DDoS attack dataset...")
    gen = TrafficGenerator(seed=123)
    attack_sim = AttackSimulator(gen)
    
    flows = []
    # Normal traffic first (30%)
    flows.extend(gen.generate_batch(int(n_flows * 0.3)))
    
    # Start DDoS attack (70%)
    attack_sim.start_attack('DDoS', duration_sec=999)
    flows.extend(attack_sim.generate_batch(int(n_flows * 0.7)))
    
    df = pd.DataFrame(flows)
    return df

def generate_port_scan(n_flows=1000):
    """Generate port scanning scenario"""
    print("Generating port scan dataset...")
    gen = TrafficGenerator(seed=456)
    attack_sim = AttackSimulator(gen)
    
    flows = []
    # Normal traffic (40%)
    flows.extend(gen.generate_batch(int(n_flows * 0.4)))
    
    # Port scan (60%)
    attack_sim.start_attack('PortScan', duration_sec=999)
    flows.extend(attack_sim.generate_batch(int(n_flows * 0.6)))
    
    df = pd.DataFrame(flows)
    return df

def generate_mixed_threats(n_flows=2000):
    """Generate multiple attack types"""
    print("Generating mixed threats dataset...")
    gen = TrafficGenerator(seed=789)
    attack_sim = AttackSimulator(gen)
    
    flows = []
    # Normal start (20%)
    flows.extend(gen.generate_batch(int(n_flows * 0.2)))
    
    # DDoS attack (25%)
    attack_sim.start_attack('DDoS', duration_sec=999)
    flows.extend(attack_sim.generate_batch(int(n_flows * 0.25)))
    attack_sim.stop_attack()
    
    # Brief normal (10%)
    flows.extend(gen.generate_batch(int(n_flows * 0.1)))
    
    # Port scan (20%)
    attack_sim.start_attack('PortScan', duration_sec=999)
    flows.extend(attack_sim.generate_batch(int(n_flows * 0.2)))
    attack_sim.stop_attack()
    
    # Brute force (15%)
    attack_sim.start_attack('BruteForce', duration_sec=999)
    flows.extend(attack_sim.generate_batch(int(n_flows * 0.15)))
    attack_sim.stop_attack()
    
    # Recovery normal (10%)
    flows.extend(gen.generate_batch(int(n_flows * 0.1)))
    
    df = pd.DataFrame(flows)
    return df

def generate_daily_pattern(n_flows=3000):
    """Generate realistic daily traffic pattern"""
    print("Generating daily pattern dataset...")
    gen = TrafficGenerator(seed=101)
    attack_sim = AttackSimulator(gen)
    
    flows = []
    start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Simulate 24-hour period with varying traffic
    for hour in range(24):
        # Traffic patterns based on time of day
        if 1 <= hour <= 6:  # Night - low traffic
            batch_size = int(n_flows * 0.01)
        elif 7 <= hour <= 9:  # Morning - medium traffic
            batch_size = int(n_flows * 0.03)
        elif 10 <= hour <= 17:  # Business hours - high traffic
            batch_size = int(n_flows * 0.05)
        elif 18 <= hour <= 23:  # Evening - medium traffic
            batch_size = int(n_flows * 0.025)
        else:  # Midnight
            batch_size = int(n_flows * 0.01)
        
        # Add some attacks during business hours
        if hour == 14:  # Attack at 2 PM
            attack_sim.start_attack('DDoS', duration_sec=999)
            flows.extend(attack_sim.generate_batch(batch_size))
            attack_sim.stop_attack()
        elif hour == 20:  # Port scan at 8 PM
            attack_sim.start_attack('PortScan', duration_sec=999)
            flows.extend(attack_sim.generate_batch(batch_size))
            attack_sim.stop_attack()
        else:
            flows.extend(gen.generate_batch(batch_size))
    
    df = pd.DataFrame(flows)
    return df

def save_dataset(df, filename, output_dir='data/samples'):
    """Save dataset with metadata"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    filepath = output_path / filename
    df.to_csv(filepath, index=False)
    
    # Print statistics
    total = len(df)
    attacks = df['is_attack'].sum()
    benign = total - attacks
    
    print(f"  Saved: {filepath}")
    print(f"  Total flows: {total:,}")
    print(f"  Benign: {benign:,} ({benign/total*100:.1f}%)")
    print(f"  Attacks: {attacks:,} ({attacks/total*100:.1f}%)")
    if attacks > 0:
        print(f"  Attack types: {df[df['is_attack']]['label'].value_counts().to_dict()}")
    print()

def main():
    """Generate all sample datasets"""
    print("=" * 60)
    print("Generating Sample Datasets for Network Anomaly Detection")
    print("=" * 60)
    print()
    
    # Create output directory
    output_dir = 'data/samples'
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate datasets
    datasets = [
        (generate_normal_traffic(1000), 'normal_traffic.csv'),
        (generate_ddos_attack(1000), 'ddos_attack.csv'),
        (generate_port_scan(1000), 'port_scan.csv'),
        (generate_mixed_threats(2000), 'mixed_threats.csv'),
        (generate_daily_pattern(3000), 'daily_pattern.csv'),
    ]
    
    for df, filename in datasets:
        save_dataset(df, filename, output_dir)
    
    print("=" * 60)
    print("✓ All sample datasets generated successfully!")
    print("=" * 60)

if __name__ == '__main__':
    main()
