# ML Network Anomaly Detection

Using machine learning to detect anomalies in network traffic.

## 🎯 Project Overview

This project implements a machine learning-based intrusion detection system (IDS) that analyzes network traffic and classifies it as normal or one of several attack types.

## ✨ Features

- **Multi-class Classification**: Detects 15+ attack types
- **Multiple Models**: XGBoost, Random Forest, LSTM Autoencoder
- **Real-time Dashboard**: Streamlit-based monitoring
- **GPU Accelerated**: Optimized for NVIDIA RTX GPUs

## 📊 Dataset

- **CICIDS2017**: Canadian Institute for Cybersecurity
- ~2.8 million network flows
- 80+ features per flow
- 15 classes (1 benign + 14 attack types)

## 🚀 Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download dataset
python scripts/download_data.py

# 4. Train model
python src/train.py

# 5. Run dashboard
streamlit run dashboard/app.py
```

## 📁 Project Structure

```
yhlas-ml-detect-anomalies/
├── data/
│   ├── raw/              # Original CSV files
│   ├── processed/        # Cleaned data
│   └── models/           # Saved models
├── src/
│   ├── data/             # Data loading & preprocessing
│   ├── models/           # ML model definitions
│   ├── training/         # Training loops
│   └── utils/            # Utilities
├── dashboard/            # Streamlit app
├── notebooks/            # Jupyter notebooks
├── scripts/              # Helper scripts
├── config.yaml           # Configuration
└── requirements.txt      # Dependencies
```

## 🧠 Models

| Model | Type | Accuracy | Use Case |
|-------|------|----------|----------|
| XGBoost | Supervised | 98%+ | Primary classifier |
| Random Forest | Supervised | 96%+ | Baseline |
| LSTM Autoencoder | Unsupervised | 94%+ | Zero-day detection |

## 📈 Results

- **Accuracy**: 98.2%
- **Precision**: 97.5%
- **Recall**: 96.8%
- **F1-Score**: 97.1%

## 🔧 Requirements

- Python 3.10+
- NVIDIA GPU with CUDA 11.8
- 24GB RAM recommended
- 10GB disk space

## 👤 Author

Yhlas - Diploma Project 2025
