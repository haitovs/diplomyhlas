"""
Generate Sample Data
Creates synthetic network traffic data for testing
"""

import numpy as np
import pandas as pd
from pathlib import Path


def generate_sample_data(n_samples: int = 10000, output_dir: str = 'data/raw'):
    """Generate synthetic CICIDS2017-like data"""
    
    print(f"Generating {n_samples:,} samples...")
    np.random.seed(42)
    
    # Create directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Define attack types and their proportions
    attack_types = {
        'BENIGN': 0.70,
        'DDoS': 0.10,
        'PortScan': 0.08,
        'DoS Hulk': 0.05,
        'Bot': 0.03,
        'FTP-Patator': 0.02,
        'SSH-Patator': 0.02,
    }
    
    # Generate labels
    labels = np.random.choice(
        list(attack_types.keys()),
        size=n_samples,
        p=list(attack_types.values())
    )
    
    # Generate base features
    data = {
        'Flow Duration': np.random.exponential(1000000, n_samples),
        'Total Fwd Packets': np.random.poisson(10, n_samples),
        'Total Backward Packets': np.random.poisson(8, n_samples),
        'Total Length of Fwd Packets': np.random.exponential(1000, n_samples),
        'Total Length of Bwd Packets': np.random.exponential(800, n_samples),
        'Fwd Packet Length Max': np.random.exponential(500, n_samples),
        'Fwd Packet Length Min': np.abs(np.random.normal(50, 30, n_samples)),
        'Fwd Packet Length Mean': np.random.exponential(200, n_samples),
        'Fwd Packet Length Std': np.random.exponential(100, n_samples),
        'Bwd Packet Length Max': np.random.exponential(400, n_samples),
        'Bwd Packet Length Min': np.abs(np.random.normal(40, 25, n_samples)),
        'Bwd Packet Length Mean': np.random.exponential(150, n_samples),
        'Bwd Packet Length Std': np.random.exponential(80, n_samples),
        'Flow Bytes/s': np.random.exponential(10000, n_samples),
        'Flow Packets/s': np.random.exponential(100, n_samples),
        'Flow IAT Mean': np.random.exponential(10000, n_samples),
        'Flow IAT Std': np.random.exponential(5000, n_samples),
        'Flow IAT Max': np.random.exponential(50000, n_samples),
        'Flow IAT Min': np.abs(np.random.normal(100, 50, n_samples)),
        'Fwd IAT Total': np.random.exponential(20000, n_samples),
        'Fwd IAT Mean': np.random.exponential(5000, n_samples),
        'Fwd IAT Std': np.random.exponential(3000, n_samples),
        'Fwd IAT Max': np.random.exponential(15000, n_samples),
        'Fwd IAT Min': np.abs(np.random.normal(50, 30, n_samples)),
        'Bwd IAT Total': np.random.exponential(18000, n_samples),
        'Bwd IAT Mean': np.random.exponential(4500, n_samples),
        'Bwd IAT Std': np.random.exponential(2500, n_samples),
        'Bwd IAT Max': np.random.exponential(12000, n_samples),
        'Bwd IAT Min': np.abs(np.random.normal(45, 25, n_samples)),
        'Fwd PSH Flags': np.random.randint(0, 2, n_samples),
        'Fwd URG Flags': np.random.randint(0, 2, n_samples),
        'Fwd Header Length': np.random.exponential(200, n_samples),
        'Bwd Header Length': np.random.exponential(180, n_samples),
        'Fwd Packets/s': np.random.exponential(50, n_samples),
        'Bwd Packets/s': np.random.exponential(40, n_samples),
        'Min Packet Length': np.abs(np.random.normal(20, 10, n_samples)),
        'Max Packet Length': np.random.exponential(1000, n_samples),
        'Packet Length Mean': np.random.exponential(300, n_samples),
        'Packet Length Std': np.random.exponential(150, n_samples),
        'Packet Length Variance': np.random.exponential(25000, n_samples),
        'FIN Flag Count': np.random.randint(0, 3, n_samples),
        'SYN Flag Count': np.random.randint(0, 3, n_samples),
        'RST Flag Count': np.random.randint(0, 2, n_samples),
        'PSH Flag Count': np.random.randint(0, 3, n_samples),
        'ACK Flag Count': np.random.randint(0, 10, n_samples),
        'URG Flag Count': np.random.randint(0, 2, n_samples),
        'CWE Flag Count': np.random.randint(0, 2, n_samples),
        'ECE Flag Count': np.random.randint(0, 2, n_samples),
        'Down/Up Ratio': np.random.exponential(1, n_samples),
        'Average Packet Size': np.random.exponential(250, n_samples),
        'Avg Fwd Segment Size': np.random.exponential(200, n_samples),
        'Avg Bwd Segment Size': np.random.exponential(180, n_samples),
        'Fwd Avg Bytes/Bulk': np.random.exponential(100, n_samples),
        'Fwd Avg Packets/Bulk': np.random.exponential(5, n_samples),
        'Fwd Avg Bulk Rate': np.random.exponential(1000, n_samples),
        'Bwd Avg Bytes/Bulk': np.random.exponential(80, n_samples),
        'Bwd Avg Packets/Bulk': np.random.exponential(4, n_samples),
        'Bwd Avg Bulk Rate': np.random.exponential(800, n_samples),
        'Subflow Fwd Packets': np.random.poisson(5, n_samples),
        'Subflow Fwd Bytes': np.random.exponential(500, n_samples),
        'Subflow Bwd Packets': np.random.poisson(4, n_samples),
        'Subflow Bwd Bytes': np.random.exponential(400, n_samples),
        'Init_Win_bytes_forward': np.random.randint(0, 65536, n_samples),
        'Init_Win_bytes_backward': np.random.randint(0, 65536, n_samples),
        'act_data_pkt_fwd': np.random.poisson(3, n_samples),
        'min_seg_size_forward': np.random.randint(20, 100, n_samples),
        'Active Mean': np.random.exponential(10000, n_samples),
        'Active Std': np.random.exponential(5000, n_samples),
        'Active Max': np.random.exponential(30000, n_samples),
        'Active Min': np.abs(np.random.normal(100, 50, n_samples)),
        'Idle Mean': np.random.exponential(50000, n_samples),
        'Idle Std': np.random.exponential(20000, n_samples),
        'Idle Max': np.random.exponential(100000, n_samples),
        'Idle Min': np.abs(np.random.normal(1000, 500, n_samples)),
    }
    
    # Add attack-specific patterns
    is_ddos = labels == 'DDoS'
    is_portscan = labels == 'PortScan'
    is_dos = np.isin(labels, ['DoS Hulk'])
    is_bot = labels == 'Bot'
    
    # DDoS: High packet count, short duration
    data['Total Fwd Packets'][is_ddos] *= 5
    data['Flow Duration'][is_ddos] *= 0.2
    data['Flow Packets/s'][is_ddos] *= 10
    
    # PortScan: Many connections, few packets each
    data['Total Fwd Packets'][is_portscan] = np.random.poisson(2, sum(is_portscan))
    data['SYN Flag Count'][is_portscan] = np.random.randint(1, 5, sum(is_portscan))
    
    # DoS: High bytes, moderate packets
    data['Total Length of Fwd Packets'][is_dos] *= 3
    data['Flow Bytes/s'][is_dos] *= 5
    
    # Bot: Periodic behavior
    data['Flow IAT Std'][is_bot] *= 0.1
    data['Active Std'][is_bot] *= 0.5
    
    # Create DataFrame
    df = pd.DataFrame(data)
    df['Label'] = labels
    
    # Add some noise
    for col in df.select_dtypes(include=[np.number]).columns:
        noise = np.random.normal(0, df[col].std() * 0.05, len(df))
        df[col] = df[col] + noise
        df[col] = df[col].clip(lower=0)  # No negative values
    
    # Save
    output_file = output_path / 'sample_data.csv'
    df.to_csv(output_file, index=False)
    
    print(f"\n✓ Created: {output_file}")
    print(f"  Shape: {df.shape}")
    print(f"  Features: {len(df.columns) - 1}")
    print(f"\nLabel distribution:")
    for label, count in df['Label'].value_counts().items():
        pct = count / len(df) * 100
        print(f"  {label}: {count:,} ({pct:.1f}%)")
    
    return df


if __name__ == "__main__":
    generate_sample_data(n_samples=50000)
