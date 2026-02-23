"""
Data Source Manager
Unified interface for multiple data sources: simulation, pre-recorded, upload
"""

import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.simulation.traffic_generator import TrafficGenerator, AttackSimulator


class DataSource:
    """Base class for data sources"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def get_data(self, n_samples: int = 100) -> pd.DataFrame:
        """Get data from this source"""
        raise NotImplementedError
    
    def get_info(self) -> Dict:
        """Get information about this data source"""
        return {
            'name': self.name,
            'description': self.description,
            'type': self.__class__.__name__
        }


class SimulationDataSource(DataSource):
    """Real-time traffic simulation"""
    
    def __init__(self, seed: Optional[int] = None, enable_attacks: bool = True):
        super().__init__(
            name="Real-time Simulation",
            description="Generate network traffic in real-time with optional attacks"
        )
        self.generator = TrafficGenerator(seed=seed)
        self.attack_simulator = AttackSimulator(self.generator) if enable_attacks else None
        self.attack_active = False
        self.attack_type = None
    
    def get_data(self, n_samples: int = 100) -> pd.DataFrame:
        """Generate simulated traffic flows"""
        if self.attack_active and self.attack_simulator:
            flows = self.attack_simulator.generate_batch(n_samples)
        else:
            flows = self.generator.generate_batch(n_samples)
        return pd.DataFrame(flows)
    
    def start_attack(self, attack_type: str, duration_sec: int = 30):
        """Start attack simulation"""
        if self.attack_simulator:
            self.attack_simulator.start_attack(attack_type, duration_sec)
            self.attack_active = True
            self.attack_type = attack_type
    
    def stop_attack(self):
        """Stop attack simulation"""
        if self.attack_simulator:
            self.attack_simulator.stop_attack()
            self.attack_active = False
            self.attack_type = None
    
    def get_info(self) -> Dict:
        info = super().get_info()
        info.update({
            'attack_enabled': self.attack_simulator is not None,
            'attack_active': self.attack_active,
            'attack_type': self.attack_type
        })
        return info


class PreRecordedDataSource(DataSource):
    """Load pre-recorded datasets"""
    
    def __init__(self, dataset_path: str):
        self.dataset_path = Path(dataset_path)
        
        # Extract name from filename
        name = self.dataset_path.stem.replace('_', ' ').title()
        
        super().__init__(
            name=f"Pre-recorded: {name}",
            description=f"Load {name} scenario dataset"
        )
        
        # Load the dataset
        self.data = self._load_dataset()
        self.current_index = 0
    
    def _load_dataset(self) -> pd.DataFrame:
        """Load dataset from file"""
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found: {self.dataset_path}")
        
        return pd.read_csv(self.dataset_path)
    
    def get_data(self, n_samples: int = 100) -> pd.DataFrame:
        """Get batch of samples from dataset"""
        # Loop through dataset
        if self.current_index >= len(self.data):
            self.current_index = 0  # Reset to beginning
        
        end_index = min(self.current_index + n_samples, len(self.data))
        samples = self.data.iloc[self.current_index:end_index].copy()
        
        self.current_index = end_index
        
        # If we didn't get enough samples, loop back
        if len(samples) < n_samples:
            additional_needed = n_samples - len(samples)
            self.current_index = 0
            additional = self.data.iloc[0:additional_needed].copy()
            samples = pd.concat([samples, additional], ignore_index=True)
            self.current_index = additional_needed
        
        return samples
    
    def reset(self):
        """Reset to beginning of dataset"""
        self.current_index = 0
    
    def get_info(self) -> Dict:
        info = super().get_info()
        info.update({
            'total_samples': len(self.data),
            'current_index': self.current_index,
            'attacks': int(self.data['is_attack'].sum()) if 'is_attack' in self.data.columns else 0,
            'benign': int((~self.data['is_attack']).sum()) if 'is_attack' in self.data.columns else len(self.data),
            'attack_types': self.data[self.data['is_attack']]['label'].value_counts().to_dict() if 'is_attack' in self.data.columns else {}
        })
        return info


class UploadedDataSource(DataSource):
    """User-uploaded dataset"""
    
    def __init__(self, uploaded_file, file_name: str):
        super().__init__(
            name=f"Uploaded: {file_name}",
            description=f"User uploaded file: {file_name}"
        )
        
        # Load uploaded file
        self.data = pd.read_csv(uploaded_file)
        self.current_index = 0
        
        # Validate required columns
        self._validate_data()
    
    def _validate_data(self):
        """Validate that uploaded data has required columns"""
        required_cols = ['src_ip', 'dst_ip', 'protocol']
        missing_cols = [col for col in required_cols if col not in self.data.columns]
        
        if missing_cols:
            raise ValueError(f"Uploaded file missing required columns: {missing_cols}")
        
        # Add default values for optional columns
        if 'is_attack' not in self.data.columns:
            self.data['is_attack'] = False
        if 'label' not in self.data.columns:
            self.data['label'] = 'BENIGN'
    
    def get_data(self, n_samples: int = 100) -> pd.DataFrame:
        """Get batch of samples from uploaded data"""
        if self.current_index >= len(self.data):
            self.current_index = 0
        
        end_index = min(self.current_index + n_samples, len(self.data))
        samples = self.data.iloc[self.current_index:end_index].copy()
        self.current_index = end_index
        
        return samples
    
    def reset(self):
        """Reset to beginning"""
        self.current_index = 0
    
    def get_info(self) -> Dict:
        info = super().get_info()
        info.update({
            'total_samples': len(self.data),
            'current_index': self.current_index,
            'columns': list(self.data.columns)
        })
        return info


class DataSourceManager:
    """Manages multiple data sources and provides unified access"""
    
    def __init__(self, samples_dir: str = 'data/samples'):
        self.samples_dir = Path(samples_dir)
        self.sources: Dict[str, DataSource] = {}
        self.current_source: Optional[str] = None
        
        # Initialize default sources
        self._initialize_sources()
    
    def _initialize_sources(self):
        """Initialize available data sources"""
        # Add simulation source
        self.add_source('simulation', SimulationDataSource(seed=42))
        
        # Add pre-recorded datasets
        if self.samples_dir.exists():
            for csv_file in self.samples_dir.glob('*.csv'):
                source_id = f"prerecorded_{csv_file.stem}"
                try:
                    self.add_source(source_id, PreRecordedDataSource(csv_file))
                except Exception as e:
                    print(f"Error loading {csv_file.name}: {e}")
        
        # Set default source
        if 'simulation' in self.sources:
            self.current_source = 'simulation'
    
    def add_source(self, source_id: str, source: DataSource):
        """Add a data source"""
        self.sources[source_id] = source
    
    def set_source(self, source_id: str):
        """Switch to a different data source"""
        if source_id not in self.sources:
            raise ValueError(f"Unknown source: {source_id}")
        self.current_source = source_id
    
    def get_current_source(self) -> Optional[DataSource]:
        """Get currently active data source"""
        if self.current_source:
            return self.sources[self.current_source]
        return None
    
    def get_data(self, n_samples: int = 100) -> pd.DataFrame:
        """Get data from current source"""
        source = self.get_current_source()
        if source:
            return source.get_data(n_samples)
        return pd.DataFrame()
    
    def list_sources(self) -> List[Tuple[str, str, str]]:
        """List available sources (id, name, description)"""
        return [
            (source_id, source.name, source.description)
            for source_id, source in self.sources.items()
        ]
    
    def get_source_info(self, source_id: Optional[str] = None) -> Dict:
        """Get information about a source"""
        if source_id is None:
            source_id = self.current_source
        
        if source_id in self.sources:
            return self.sources[source_id].get_info()
        return {}


# Convenience function for Streamlit
def get_data_source_options(manager: DataSourceManager) -> Dict[str, str]:
    """Get data source options for Streamlit selectbox"""
    return {
        source.name: source_id
        for source_id, source in manager.sources.items()
    }


if __name__ == '__main__':
    # Test data source manager
    print("Testing Data Source Manager")
    print("=" * 60)
    
    manager = DataSourceManager()
    
    print("\nAvailable sources:")
    for source_id, name, desc in manager.list_sources():
        print(f"  [{source_id}] {name}")
        print(f"      {desc}")
    
    print("\nTesting simulation source...")
    manager.set_source('simulation')
    data = manager.get_data(10)
    print(f"  Got {len(data)} flows")
    print(f"  Columns: {list(data.columns)}")
    
    # Try pre-recorded data
    prerecorded = [sid for sid in manager.sources.keys() if sid.startswith('prerecorded_')]
    if prerecorded:
        print(f"\nTesting pre-recorded source: {prerecorded[0]}")
        manager.set_source(prerecorded[0])
        info = manager.get_source_info()
        print(f"  {info}")
        data = manager.get_data(5)
        print(f"  Got {len(data)} flows")
    
    print("\n✓ Data source manager working!")
