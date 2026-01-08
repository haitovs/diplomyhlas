"""
Data Loader Module
Handles loading and initial processing of network traffic datasets
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, List, Optional
import yaml
from tqdm import tqdm


class DataLoader:
    """Loads and manages network traffic datasets"""
    
    # CICIDS2017 file mapping
    CICIDS_FILES = {
        'monday': 'Monday-WorkingHours.pcap_ISCX.csv',
        'tuesday': 'Tuesday-WorkingHours.pcap_ISCX.csv',
        'wednesday': 'Wednesday-workingHours.pcap_ISCX.csv',
        'thursday_morning': 'Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv',
        'thursday_afternoon': 'Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv',
        'friday_morning': 'Friday-WorkingHours-Morning.pcap_ISCX.csv',
        'friday_afternoon_portscan': 'Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv',
        'friday_afternoon_ddos': 'Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv',
    }
    
    # Attack label mappings
    ATTACK_MAPPING = {
        'BENIGN': 0,
        'Bot': 1,
        'DDoS': 2,
        'DoS GoldenEye': 3,
        'DoS Hulk': 4,
        'DoS Slowhttptest': 5,
        'DoS slowloris': 6,
        'FTP-Patator': 7,
        'Heartbleed': 8,
        'Infiltration': 9,
        'PortScan': 10,
        'SSH-Patator': 11,
        'Web Attack – Brute Force': 12,
        'Web Attack – Sql Injection': 13,
        'Web Attack – XSS': 14,
    }
    
    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.raw_path = Path(self.config['data']['raw_path'])
        self.processed_path = Path(self.config['data']['processed_path'])
        
        # Create directories
        self.raw_path.mkdir(parents=True, exist_ok=True)
        self.processed_path.mkdir(parents=True, exist_ok=True)
    
    def load_cicids2017(
        self, 
        files: Optional[List[str]] = None,
        sample_ratio: float = 1.0
    ) -> pd.DataFrame:
        """
        Load CICIDS2017 dataset
        
        Args:
            files: List of file keys to load, or None for all
            sample_ratio: Fraction of data to sample (for development)
            
        Returns:
            Combined DataFrame
        """
        if files is None:
            files = list(self.CICIDS_FILES.keys())
        
        dfs = []
        for file_key in tqdm(files, desc="Loading files"):
            if file_key not in self.CICIDS_FILES:
                print(f"Warning: Unknown file key '{file_key}'")
                continue
                
            file_path = self.raw_path / self.CICIDS_FILES[file_key]
            
            if not file_path.exists():
                print(f"Warning: File not found: {file_path}")
                continue
            
            # Load with low_memory=False to avoid mixed type warnings
            df = pd.read_csv(file_path, low_memory=False)
            
            # Sample if needed
            if sample_ratio < 1.0:
                df = df.sample(frac=sample_ratio, random_state=42)
            
            dfs.append(df)
            print(f"  Loaded {file_key}: {len(df):,} rows")
        
        if not dfs:
            raise ValueError("No data files found!")
        
        # Combine all DataFrames
        combined = pd.concat(dfs, ignore_index=True)
        print(f"\nTotal rows: {len(combined):,}")
        
        return combined
    
    def load_nsl_kdd(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load NSL-KDD dataset
        
        Returns:
            Tuple of (train_df, test_df)
        """
        train_path = self.raw_path / 'KDDTrain+.csv'
        test_path = self.raw_path / 'KDDTest+.csv'
        
        # NSL-KDD column names
        columns = [
            'duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes',
            'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in',
            'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations',
            'num_shells', 'num_access_files', 'num_outbound_cmds', 'is_host_login',
            'is_guest_login', 'count', 'srv_count', 'serror_rate', 'srv_serror_rate',
            'rerror_rate', 'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate',
            'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
            'dst_host_same_srv_rate', 'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
            'dst_host_srv_diff_host_rate', 'dst_host_serror_rate', 'dst_host_srv_serror_rate',
            'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'label', 'difficulty'
        ]
        
        train_df = pd.read_csv(train_path, names=columns)
        test_df = pd.read_csv(test_path, names=columns)
        
        return train_df, test_df
    
    def get_class_distribution(self, df: pd.DataFrame, label_col: str = 'Label') -> pd.Series:
        """Get distribution of classes"""
        return df[label_col].value_counts()
    
    def save_processed(self, df: pd.DataFrame, name: str) -> Path:
        """Save processed DataFrame"""
        output_path = self.processed_path / f"{name}.parquet"
        df.to_parquet(output_path, index=False)
        print(f"Saved: {output_path}")
        return output_path
    
    def load_processed(self, name: str) -> pd.DataFrame:
        """Load processed DataFrame"""
        input_path = self.processed_path / f"{name}.parquet"
        return pd.read_parquet(input_path)


def get_attack_label_name(label_id: int) -> str:
    """Convert numeric label to attack name"""
    inv_mapping = {v: k for k, v in DataLoader.ATTACK_MAPPING.items()}
    return inv_mapping.get(label_id, f"Unknown_{label_id}")


if __name__ == "__main__":
    # Test loading
    loader = DataLoader()
    print("DataLoader initialized")
    print(f"Raw path: {loader.raw_path}")
    print(f"Processed path: {loader.processed_path}")
