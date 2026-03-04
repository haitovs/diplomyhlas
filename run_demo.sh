#!/bin/bash
# Network Anomaly Analyzer - Quick Start Script

echo "🛡️ Starting Network Anomaly Analyzer (v2.0)..."

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null
then
    echo "⚙️ Streamlit not found. Installing requirements..."
    pip install -r requirements.txt
fi

echo "🚀 Launching Dashboard..."
# Launch the new main entry point
streamlit run dashboard/1_🏠_Home.py
