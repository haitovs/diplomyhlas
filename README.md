# ML Network Anomaly Detection

Using machine learning to detect anomalies in network traffic.

## 🎯 Project Overview

This project implements a machine learning-based intrusion detection system (IDS) that analyzes network traffic and classifies it as normal or one of several attack types.

## ✨ Features

- **Multi-class Classification**: Detects 15+ attack types (DDoS, Port Scan, Brute Force, etc.)
- **Multiple Data Sources**: Real-time simulation, pre-recorded scenarios, file upload
- **Professional Dashboard**: Streamlit-based with modern cybersecurity UI
- **ML-Powered Detection**: LightGBM model with 98%+ accuracy
- **Interactive Controls**: Attack simulation, live metrics, data export
- **Lightweight**: Fast inference, no GPU required for demonstrations

## 📊 Dataset

- **CICIDS2017**: Canadian Institute for Cybersecurity
- ~2.8 million network flows
- 80+ features per flow
- 15 classes (1 benign + 14 attack types)

## 🚀 Quick Start

### For Demonstration (Recommended)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate sample datasets (if not already done)
python scripts/generate_samples.py

# 3. Run enhanced dashboard
streamlit run dashboard/app_v2.py

# 4. Open browser to http://localhost:8501
```

### For Full Development

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# OR: .\venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download dataset (optional for training)
python scripts/download_data.py

# 4. Train model (optional - pre-trained model included)
python src/train.py

# 5. Run dashboard
streamlit run dashboard/app_v2.py
```

## 📁 Project Structure

```
yhlas-ml-detect-anomalies/
├── dashboard/
│   ├── app_v2.py         # ✨ Enhanced dashboard (NEW)
│   ├── app.py            # Original dashboard
│   ├── components.py     # ✨ Reusable UI components
│   └── live_dashboard.py # Live simulation
├── src/
│   ├── data/
│   │   ├── data_sources.py  # ✨ Data source manager (NEW)
│   │   └── loader.py        # Data loading
│   ├── inference/
│   │   └── realtime.py      # ML prediction engine
│   ├── simulation/
│   │   └── traffic_generator.py  # Traffic & attack simulation
│   └── models/           # Model definitions
├── data/
│   ├── samples/          # ✨ Pre-recorded demo datasets (NEW)
│   ├── raw/              # Original CSV files
│   └── processed/        # Cleaned data
├── models/               # Trained models (LightGBM, etc.)
├── scripts/
│   └── generate_samples.py  # ✨ Dataset generator (NEW)
├── DEMO_GUIDE.md        # ✨ Presentation guide (NEW)
├── config.yaml          # Configuration
└── requirements.txt     # Dependencies
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
