"""
Baseline Models Module
Traditional ML models: XGBoost, Random Forest, LightGBM
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
import xgboost as xgb
import lightgbm as lgb
import joblib
from pathlib import Path
from typing import Optional, Dict, Any
import yaml


class BaselineModels:
    """Collection of traditional ML models for classification"""
    
    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.models = {}
        self.best_model = None
        self.best_model_name = None
    
    def create_xgboost(self) -> xgb.XGBClassifier:
        """Create XGBoost classifier"""
        params = self.config['models']['xgboost']
        
        model = xgb.XGBClassifier(
            n_estimators=params['n_estimators'],
            max_depth=params['max_depth'],
            learning_rate=params['learning_rate'],
            subsample=params['subsample'],
            colsample_bytree=params['colsample_bytree'],
            random_state=params['random_state'],
            n_jobs=params['n_jobs'],
            tree_method='gpu_hist' if params.get('use_gpu', False) else 'hist',
            objective='multi:softmax',
            eval_metric='mlogloss',
            early_stopping_rounds=10,
            verbosity=1,
        )
        
        self.models['xgboost'] = model
        return model
    
    def create_random_forest(self) -> RandomForestClassifier:
        """Create Random Forest classifier"""
        params = self.config['models']['random_forest']
        
        model = RandomForestClassifier(
            n_estimators=params['n_estimators'],
            max_depth=params['max_depth'],
            min_samples_split=params['min_samples_split'],
            random_state=params['random_state'],
            n_jobs=params['n_jobs'],
            verbose=1,
        )
        
        self.models['random_forest'] = model
        return model
    
    def create_lightgbm(self) -> lgb.LGBMClassifier:
        """Create LightGBM classifier"""
        model = lgb.LGBMClassifier(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.1,
            random_state=42,
            n_jobs=-1,
            device='gpu',  # Use GPU if available
            verbose=1,
        )
        
        self.models['lightgbm'] = model
        return model
    
    def train(
        self, 
        model_name: str,
        X_train: np.ndarray, 
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None
    ) -> Any:
        """
        Train a specific model
        
        Args:
            model_name: 'xgboost', 'random_forest', or 'lightgbm'
            X_train, y_train: Training data
            X_val, y_val: Validation data (optional, for early stopping)
        """
        if model_name not in self.models:
            if model_name == 'xgboost':
                self.create_xgboost()
            elif model_name == 'random_forest':
                self.create_random_forest()
            elif model_name == 'lightgbm':
                self.create_lightgbm()
            else:
                raise ValueError(f"Unknown model: {model_name}")
        
        model = self.models[model_name]
        print(f"\nTraining {model_name}...")
        
        if model_name == 'xgboost' and X_val is not None:
            model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                verbose=True
            )
        elif model_name == 'lightgbm' and X_val is not None:
            model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
            )
        else:
            model.fit(X_train, y_train)
        
        return model
    
    def predict(self, model_name: str, X: np.ndarray) -> np.ndarray:
        """Make predictions with a trained model"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not trained!")
        return self.models[model_name].predict(X)
    
    def predict_proba(self, model_name: str, X: np.ndarray) -> np.ndarray:
        """Get prediction probabilities"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not trained!")
        return self.models[model_name].predict_proba(X)
    
    def evaluate(
        self, 
        model_name: str,
        X_test: np.ndarray, 
        y_test: np.ndarray,
        class_names: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a trained model
        
        Returns:
            Dictionary with metrics
        """
        y_pred = self.predict(model_name, X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        print(f"\n{model_name} Results:")
        print(f"  Accuracy: {accuracy:.4f}")
        print(f"  F1 Score: {f1:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=class_names))
        
        return {
            'model_name': model_name,
            'accuracy': accuracy,
            'f1_score': f1,
            'predictions': y_pred,
            'confusion_matrix': confusion_matrix(y_test, y_pred),
        }
    
    def compare_models(
        self, 
        X_train: np.ndarray, 
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict[str, Dict]:
        """
        Train and compare all models
        
        Returns:
            Dictionary of results for each model
        """
        results = {}
        
        for name in ['random_forest', 'xgboost', 'lightgbm']:
            try:
                self.train(name, X_train, y_train, X_val, y_val)
                results[name] = self.evaluate(name, X_test, y_test)
            except Exception as e:
                print(f"Error training {name}: {e}")
                results[name] = {'error': str(e)}
        
        # Find best model
        best_f1 = 0
        for name, res in results.items():
            if 'f1_score' in res and res['f1_score'] > best_f1:
                best_f1 = res['f1_score']
                self.best_model_name = name
                self.best_model = self.models[name]
        
        print(f"\nBest model: {self.best_model_name} (F1: {best_f1:.4f})")
        return results
    
    def get_feature_importance(self, model_name: str) -> np.ndarray:
        """Get feature importances"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not trained!")
        return self.models[model_name].feature_importances_
    
    def save_model(self, model_name: str, path: str = 'models'):
        """Save a trained model"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        model = self.models[model_name]
        model_path = path / f"{model_name}_model.joblib"
        joblib.dump(model, model_path)
        print(f"Saved {model_name} to {model_path}")
    
    def load_model(self, model_name: str, path: str = 'models'):
        """Load a saved model"""
        path = Path(path)
        model_path = path / f"{model_name}_model.joblib"
        self.models[model_name] = joblib.load(model_path)
        print(f"Loaded {model_name} from {model_path}")


if __name__ == "__main__":
    # Test model creation
    models = BaselineModels()
    models.create_xgboost()
    models.create_random_forest()
    print("Models created successfully")
