"""
Dataset Download Script
Downloads CICIDS2017 or NSL-KDD datasets
"""

import os
import sys
import requests
from pathlib import Path
import zipfile
import urllib.request
from tqdm import tqdm


class DownloadProgressBar(tqdm):
    """Progress bar for downloads"""
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_file(url: str, output_path: str):
    """Download a file with progress bar"""
    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=output_path) as t:
        urllib.request.urlretrieve(url, filename=output_path, reporthook=t.update_to)


def download_cicids2017():
    """Download CICIDS2017 dataset"""
    print("\n" + "="*60)
    print("CICIDS2017 Dataset Download")
    print("="*60)
    
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("""
The CICIDS2017 dataset needs to be downloaded manually from:
https://www.unb.ca/cic/datasets/ids-2017.html

Please:
1. Visit the link above
2. Download the "MachineLearningCVE" CSV files
3. Extract them to: data/raw/

Expected files:
- Monday-WorkingHours.pcap_ISCX.csv
- Tuesday-WorkingHours.pcap_ISCX.csv
- Wednesday-workingHours.pcap_ISCX.csv
- Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv
- Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv
- Friday-WorkingHours-Morning.pcap_ISCX.csv
- Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv
- Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv

Total size: ~500MB compressed, ~2.8GB uncompressed
    """)
    
    # Check if files exist
    expected_files = [
        'Monday-WorkingHours.pcap_ISCX.csv',
        'Tuesday-WorkingHours.pcap_ISCX.csv',
    ]
    
    found = 0
    for f in expected_files:
        if (output_dir / f).exists():
            print(f"✓ Found: {f}")
            found += 1
    
    if found == 0:
        print("\n⚠️ No dataset files found. Please download manually.")
    else:
        print(f"\n✓ Found {found} file(s). You may proceed with training.")


def download_nsl_kdd():
    """Download NSL-KDD dataset"""
    print("\n" + "="*60)
    print("NSL-KDD Dataset Download")
    print("="*60)
    
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # NSL-KDD is hosted on Kaggle and UNB
    print("""
NSL-KDD dataset can be downloaded from:
https://www.unb.ca/cic/datasets/nsl.html

Or from Kaggle:
https://www.kaggle.com/datasets/hassan06/nslkdd

Please download and place these files in data/raw/:
- KDDTrain+.csv
- KDDTest+.csv

Total size: ~25MB
    """)


def create_sample_data():
    """Create sample data for testing"""
    import numpy as np
    import pandas as pd
    
    print("\n" + "="*60)
    print("Creating Sample Data for Testing")
    print("="*60)
    
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample data similar to CICIDS2017
    np.random.seed(42)
    n_samples = 10000
    
    # Generate features
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
    }
    
    # Add more features to match CICIDS2017 (~80 features)
    for i in range(60):
        data[f'Feature_{i}'] = np.random.normal(0, 1, n_samples)
    
    # Generate labels
    labels = np.random.choice(
        ['BENIGN', 'DDoS', 'PortScan', 'Bot', 'DoS Hulk'],
        n_samples,
        p=[0.7, 0.1, 0.1, 0.05, 0.05]
    )
    data['Label'] = labels
    
    df = pd.DataFrame(data)
    
    # Save as sample file
    output_path = output_dir / 'sample_data.csv'
    df.to_csv(output_path, index=False)
    
    print(f"✓ Created sample data: {output_path}")
    print(f"  Samples: {n_samples:,}")
    print(f"  Features: {len(df.columns) - 1}")
    print(f"  Labels: {df['Label'].value_counts().to_dict()}")
    print("\nNote: This is synthetic data for testing. Use real CICIDS2017 for actual training.")


def main():
    print("="*60)
    print("Network Anomaly Detection - Data Download")
    print("="*60)
    
    print("""
Select dataset to download:
1. CICIDS2017 (recommended, manual download required)
2. NSL-KDD (smaller, for quick experiments)
3. Create sample data (for testing only)
    """)
    
    choice = input("Enter choice (1/2/3): ").strip()
    
    if choice == '1':
        download_cicids2017()
    elif choice == '2':
        download_nsl_kdd()
    elif choice == '3':
        create_sample_data()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
