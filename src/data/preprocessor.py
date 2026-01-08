"""
Data Preprocessor Module
Feature engineering, cleaning, and transformation
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from typing import Tuple, List, Optional, Dict
import yaml
import joblib
from pathlib import Path


class Preprocessor:
    """Handles data preprocessing and feature engineering"""
    
    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.scaler = None
        self.label_encoder = LabelEncoder()
        self.feature_columns = None
        self.target_column = self.config['features']['target_column']
        
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the dataset
        - Remove duplicates
        - Handle missing values
        - Remove infinite values
        - Strip column names
        """
        print(f"Original shape: {df.shape}")
        
        # Strip column names
        df.columns = df.columns.str.strip()
        
        # Drop specified columns
        drop_cols = self.config['features'].get('drop_columns', [])
        existing_drop = [c for c in drop_cols if c in df.columns]
        if existing_drop:
            df = df.drop(columns=existing_drop)
            print(f"Dropped columns: {existing_drop}")
        
        # Remove duplicates
        before = len(df)
        df = df.drop_duplicates()
        print(f"Removed {before - len(df):,} duplicates")
        
        # Handle missing values
        missing = df.isnull().sum().sum()
        if missing > 0:
            print(f"Found {missing:,} missing values")
            # For numeric columns, fill with median
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
            # For categorical, fill with mode
            cat_cols = df.select_dtypes(include=['object']).columns
            for col in cat_cols:
                if col != self.target_column:
                    df[col] = df[col].fillna(df[col].mode()[0] if len(df[col].mode()) > 0 else 'unknown')
        
        # Replace infinite values
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.fillna(0)
        
        print(f"Final shape: {df.shape}")
        return df
    
    def encode_labels(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode target labels to integers"""
        if self.target_column not in df.columns:
            raise ValueError(f"Target column '{self.target_column}' not found!")
        
        # Clean label values
        df[self.target_column] = df[self.target_column].str.strip()
        
        # Encode
        df['label_encoded'] = self.label_encoder.fit_transform(df[self.target_column])
        
        # Print mapping
        print("\nLabel mapping:")
        for i, label in enumerate(self.label_encoder.classes_):
            count = (df[self.target_column] == label).sum()
            print(f"  {i}: {label} ({count:,} samples)")
        
        return df
    
    def scale_features(
        self, 
        X: np.ndarray, 
        fit: bool = True,
        method: str = 'standard'
    ) -> np.ndarray:
        """
        Scale numeric features
        
        Args:
            X: Feature matrix
            fit: Whether to fit the scaler or just transform
            method: 'standard', 'minmax', or 'robust'
        """
        if method == 'standard':
            if self.scaler is None:
                self.scaler = StandardScaler()
        elif method == 'minmax':
            if self.scaler is None:
                self.scaler = MinMaxScaler()
        
        if fit:
            return self.scaler.fit_transform(X)
        else:
            return self.scaler.transform(X)
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare feature matrix X and target vector y
        """
        # Get feature columns (all except target)
        self.feature_columns = [c for c in df.columns if c not in [self.target_column, 'label_encoded']]
        
        # Convert to numeric, coercing errors
        X = df[self.feature_columns].apply(pd.to_numeric, errors='coerce').fillna(0).values
        y = df['label_encoded'].values
        
        print(f"Features shape: {X.shape}")
        print(f"Target shape: {y.shape}")
        
        return X, y
    
    def split_data(
        self, 
        X: np.ndarray, 
        y: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Split data into train/validation/test sets
        """
        train_ratio = self.config['data']['train_ratio']
        val_ratio = self.config['data']['val_ratio']
        test_ratio = self.config['data']['test_ratio']
        
        # First split: train and temp (val + test)
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y,
            test_size=(val_ratio + test_ratio),
            random_state=42,
            stratify=y
        )
        
        # Second split: val and test
        val_size = val_ratio / (val_ratio + test_ratio)
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp,
            test_size=(1 - val_size),
            random_state=42,
            stratify=y_temp
        )
        
        print(f"\nData split:")
        print(f"  Train: {len(X_train):,} ({len(X_train)/len(X)*100:.1f}%)")
        print(f"  Val:   {len(X_val):,} ({len(X_val)/len(X)*100:.1f}%)")
        print(f"  Test:  {len(X_test):,} ({len(X_test)/len(X)*100:.1f}%)")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def handle_imbalance(
        self, 
        X: np.ndarray, 
        y: np.ndarray,
        method: str = 'smote'
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Handle class imbalance
        
        Args:
            method: 'smote', 'undersample', or 'combined'
        """
        print(f"\nHandling imbalance with: {method}")
        print(f"Before: {len(X):,} samples")
        
        if method == 'smote':
            sampler = SMOTE(random_state=42)
            X_res, y_res = sampler.fit_resample(X, y)
        elif method == 'undersample':
            sampler = RandomUnderSampler(random_state=42)
            X_res, y_res = sampler.fit_resample(X, y)
        elif method == 'combined':
            # First undersample majority, then SMOTE minority
            under = RandomUnderSampler(sampling_strategy=0.5, random_state=42)
            X_temp, y_temp = under.fit_resample(X, y)
            smote = SMOTE(random_state=42)
            X_res, y_res = smote.fit_resample(X_temp, y_temp)
        else:
            return X, y
        
        print(f"After: {len(X_res):,} samples")
        return X_res, y_res
    
    def save_artifacts(self, path: str = 'models'):
        """Save preprocessing artifacts"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        if self.scaler:
            joblib.dump(self.scaler, path / 'scaler.joblib')
        joblib.dump(self.label_encoder, path / 'label_encoder.joblib')
        joblib.dump(self.feature_columns, path / 'feature_columns.joblib')
        print(f"Saved artifacts to {path}")
    
    def load_artifacts(self, path: str = 'models'):
        """Load preprocessing artifacts"""
        path = Path(path)
        self.scaler = joblib.load(path / 'scaler.joblib')
        self.label_encoder = joblib.load(path / 'label_encoder.joblib')
        self.feature_columns = joblib.load(path / 'feature_columns.joblib')
        print(f"Loaded artifacts from {path}")


if __name__ == "__main__":
    # Test preprocessor
    preprocessor = Preprocessor()
    print("Preprocessor initialized")
