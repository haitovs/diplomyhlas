"""
Main Training Script
End-to-end training pipeline for network anomaly detection
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import yaml
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from src.data import DataLoader, Preprocessor
from src.models import BaselineModels, AnomalyDetector


def train_baseline_models(X_train, y_train, X_val, y_val, X_test, y_test, class_names):
    """Train and evaluate baseline models"""
    print("\n" + "="*60)
    print("TRAINING BASELINE MODELS")
    print("="*60)
    
    models = BaselineModels()
    results = models.compare_models(X_train, y_train, X_val, y_val, X_test, y_test)
    
    # Save best model
    models.save_model(models.best_model_name)
    
    # Plot feature importance
    if models.best_model:
        importance = models.get_feature_importance(models.best_model_name)
        plt.figure(figsize=(12, 8))
        plt.barh(range(min(20, len(importance))), sorted(importance, reverse=True)[:20])
        plt.title(f'Top 20 Feature Importances ({models.best_model_name})')
        plt.tight_layout()
        plt.savefig('models/feature_importance.png', dpi=150)
        print("Saved feature importance plot to models/feature_importance.png")
    
    return results


def train_autoencoder(X_train_normal, X_val, y_val, X_test, y_test):
    """Train autoencoder for unsupervised anomaly detection"""
    print("\n" + "="*60)
    print("TRAINING LSTM AUTOENCODER")
    print("="*60)
    
    detector = AnomalyDetector()
    detector.create_model(input_dim=X_train_normal.shape[1])
    
    # Train on normal traffic only
    history = detector.train(X_train_normal, X_val[y_val == 0])
    
    # Set threshold
    detector.set_threshold(X_train_normal, percentile=95)
    
    # Evaluate
    y_pred = detector.predict(X_test)
    y_test_binary = (y_test > 0).astype(int)  # 0 = normal, 1 = any attack
    
    from sklearn.metrics import accuracy_score, f1_score, classification_report
    
    accuracy = accuracy_score(y_test_binary, y_pred)
    f1 = f1_score(y_test_binary, y_pred)
    
    print(f"\nAutoencoder Results (Binary Classification):")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  F1 Score: {f1:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test_binary, y_pred, target_names=['Normal', 'Attack']))
    
    # Save model
    detector.save()
    
    # Plot training history
    plt.figure(figsize=(10, 5))
    plt.plot(history['train_loss'], label='Train Loss')
    if history['val_loss']:
        plt.plot(history['val_loss'], label='Val Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('LSTM Autoencoder Training')
    plt.legend()
    plt.tight_layout()
    plt.savefig('models/autoencoder_training.png', dpi=150)
    print("Saved training plot to models/autoencoder_training.png")
    
    return {'accuracy': accuracy, 'f1_score': f1}


def main():
    parser = argparse.ArgumentParser(description='Train network anomaly detection models')
    parser.add_argument('--config', type=str, default='config.yaml', help='Config file path')
    parser.add_argument('--model', type=str, default='all', 
                        choices=['all', 'baseline', 'autoencoder'],
                        help='Which model(s) to train')
    parser.add_argument('--sample', type=float, default=None,
                        help='Sample ratio for development (0.0-1.0)')
    args = parser.parse_args()
    
    # Load config
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    
    print("="*60)
    print("NETWORK ANOMALY DETECTION - TRAINING PIPELINE")
    print("="*60)
    
    # Create output directories
    Path('models').mkdir(exist_ok=True)
    Path('data/processed').mkdir(parents=True, exist_ok=True)
    
    # Load data
    print("\n[1/4] Loading data...")
    loader = DataLoader(args.config)
    
    sample_ratio = args.sample or config['data'].get('sample_ratio', 1.0)
    
    # Try loading CICIDS2017, fallback to sample data
    import pandas as pd
    sample_file = Path('data/raw/sample_data.csv')
    
    try:
        df = loader.load_cicids2017(sample_ratio=sample_ratio)
    except Exception as e:
        print(f"CICIDS2017 not found: {e}")
        if sample_file.exists():
            print(f"Loading sample data from {sample_file}...")
            df = pd.read_csv(sample_file)
            print(f"Loaded {len(df):,} samples")
        else:
            print("\nNo data found! Run: python scripts/generate_sample.py")
            print("Or download CICIDS2017 from: https://www.unb.ca/cic/datasets/ids-2017.html")
            return
    
    # Preprocess
    print("\n[2/4] Preprocessing...")
    preprocessor = Preprocessor(args.config)
    df = preprocessor.clean_data(df)
    df = preprocessor.encode_labels(df)
    
    X, y = preprocessor.prepare_features(df)
    X = preprocessor.scale_features(X)
    
    # Split
    print("\n[3/4] Splitting data...")
    X_train, X_val, X_test, y_train, y_val, y_test = preprocessor.split_data(X, y)
    
    # Get class names
    class_names = list(preprocessor.label_encoder.classes_)
    
    # Save preprocessor
    preprocessor.save_artifacts()
    
    # Train models
    print("\n[4/4] Training models...")
    
    results = {}
    
    if args.model in ['all', 'baseline']:
        # Handle imbalance for supervised models
        X_train_balanced, y_train_balanced = preprocessor.handle_imbalance(X_train, y_train, method='smote')
        results['baseline'] = train_baseline_models(
            X_train_balanced, y_train_balanced, 
            X_val, y_val, 
            X_test, y_test,
            class_names
        )
    
    if args.model in ['all', 'autoencoder']:
        # Get only normal traffic for autoencoder
        X_train_normal = X_train[y_train == 0]
        print(f"\nNormal traffic samples for autoencoder: {len(X_train_normal):,}")
        
        results['autoencoder'] = train_autoencoder(
            X_train_normal, X_val, y_val, X_test, y_test
        )
    
    print("\n" + "="*60)
    print("TRAINING COMPLETE!")
    print("="*60)
    print(f"\nModels saved to: models/")
    print(f"Artifacts saved to: models/")


if __name__ == "__main__":
    main()
