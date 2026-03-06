"""
Real-time Inference Engine
Processes traffic flows and returns predictions
"""

import numpy as np
import joblib
from pathlib import Path
from typing import Dict, List, Optional
import yaml


class RealtimePredictor:
    """Real-time prediction engine for network anomaly detection"""
    
    def __init__(self, model_path: str = 'models', config_path: str = 'config.yaml'):
        """Initialize predictor with trained model"""
        self.model_path = Path(model_path)
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_columns = None
        self.loaded = False
        
        # Try to load model
        self._load_model()
    
    def _load_model(self):
        """Load trained model and preprocessing artifacts"""
        try:
            # Try loading LightGBM first (best model)
            model_file = self.model_path / 'lightgbm_model.joblib'
            if not model_file.exists():
                model_file = self.model_path / 'xgboost_model.joblib'
            if not model_file.exists():
                model_file = self.model_path / 'random_forest_model.joblib'
            
            if model_file.exists():
                self.model = joblib.load(model_file)
                print(f"Loaded model: {model_file.name}")
            
            # Load scaler
            scaler_file = self.model_path / 'scaler.joblib'
            if scaler_file.exists():
                self.scaler = joblib.load(scaler_file)
            
            # Load label encoder
            encoder_file = self.model_path / 'label_encoder.joblib'
            if encoder_file.exists():
                self.label_encoder = joblib.load(encoder_file)
            
            # Load feature columns
            features_file = self.model_path / 'feature_columns.joblib'
            if features_file.exists():
                self.feature_columns = joblib.load(features_file)
            
            self.loaded = self.model is not None
            
        except Exception as e:
            print(f"Error loading model: {e}")
            self.loaded = False
    
    def _extract_features(self, flow: Dict) -> np.ndarray:
        """Extract features from a flow dictionary.

        If the flow dict already contains CICIDS2017 feature keys
        (e.g. from FlowAggregator), use them directly.
        Otherwise fall back to legacy per-packet mapping.
        """
        # Check if flow has CICIDS2017 keys directly (from FlowAggregator)
        has_cicids_keys = 'Flow Duration' in flow and 'Flow IAT Mean' in flow

        if has_cicids_keys and self.feature_columns:
            feature_vector = [flow.get(col, 0) for col in self.feature_columns]
            return np.array(feature_vector, dtype=np.float64).reshape(1, -1)

        # Legacy mapping for per-packet dicts
        features = {
            'Flow Duration': flow.get('duration', 0),
            'Total Fwd Packets': flow.get('fwd_packets', 0),
            'Total Backward Packets': flow.get('bwd_packets', 0),
            'Total Length of Fwd Packets': flow.get('fwd_bytes', 0),
            'Total Length of Bwd Packets': flow.get('bwd_bytes', 0),
            'Flow Bytes/s': flow.get('bytes_per_sec', 0),
            'Flow Packets/s': flow.get('packets_per_sec', 0),
            'Fwd Packet Length Max': flow.get('fwd_bytes', 0) / max(flow.get('fwd_packets', 1), 1),
            'Fwd Packet Length Mean': flow.get('fwd_bytes', 0) / max(flow.get('fwd_packets', 1), 1),
            'Bwd Packet Length Max': flow.get('bwd_bytes', 0) / max(flow.get('bwd_packets', 1), 1),
            'Bwd Packet Length Mean': flow.get('bwd_bytes', 0) / max(flow.get('bwd_packets', 1), 1),
        }

        if self.feature_columns:
            feature_vector = []
            for col in self.feature_columns:
                feature_vector.append(features.get(col, 0))
            return np.array(feature_vector, dtype=np.float64).reshape(1, -1)
        else:
            return np.array(list(features.values()), dtype=np.float64).reshape(1, -1)
    
    def predict(self, flow: Dict) -> Dict:
        """
        Predict if a flow is anomalous
        
        Returns:
            Dict with prediction, confidence, and label
        """
        # If model loaded, get real prediction
        if self.loaded:
            try:
                import warnings
                features = self._extract_features(flow)

                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    if self.scaler:
                        features = self.scaler.transform(features)
                    pred_class = self.model.predict(features)[0]
                    pred_proba = self.model.predict_proba(features)[0]
                confidence = float(np.max(pred_proba))
                
                # Get label name
                if self.label_encoder:
                    label = self.label_encoder.inverse_transform([pred_class])[0]
                else:
                    label = str(pred_class)
                
                return {
                    'prediction': label,
                    'is_anomaly': label != 'BENIGN',
                    'confidence': confidence,
                    'probabilities': {
                        self.label_encoder.inverse_transform([i])[0]: float(p) 
                        for i, p in enumerate(pred_proba)
                    } if self.label_encoder else {}
                }
            except Exception as e:
                print(f"Prediction error: {e}")

        # Model not loaded or prediction failed
        return {
            'prediction': 'UNKNOWN',
            'is_anomaly': False,
            'confidence': 0.0,
            'probabilities': {},
            'error': not self.loaded
        }
    
    def predict_batch(self, flows: List[Dict]) -> List[Dict]:
        """Predict for multiple flows"""
        return [self.predict(flow) for flow in flows]
    
    def get_model_info(self) -> Dict:
        """Get information about loaded model"""
        return {
            'loaded': self.loaded,
            'model_type': type(self.model).__name__ if self.model else None,
            'n_features': len(self.feature_columns) if self.feature_columns else 0,
            'classes': list(self.label_encoder.classes_) if self.label_encoder else [],
        }


if __name__ == "__main__":
    # Test predictor
    predictor = RealtimePredictor()
    print(f"Model loaded: {predictor.loaded}")
    print(f"Model info: {predictor.get_model_info()}")
    
    # Test prediction
    test_flow = {
        'duration': 5000,
        'fwd_packets': 10,
        'bwd_packets': 8,
        'fwd_bytes': 5000,
        'bwd_bytes': 4000,
        'packets_per_sec': 100,
        'bytes_per_sec': 10000,
        'label': 'BENIGN',
        'is_attack': False
    }
    
    result = predictor.predict(test_flow)
    print(f"Prediction: {result}")
