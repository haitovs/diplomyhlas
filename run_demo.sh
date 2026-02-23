#!/bin/bash

# Network Anomaly Detection - Quick Start Script
# This script launches the enhanced dashboard

echo "============================================"
echo "Yhlas Network Anomaly Detection"
echo "Starting Enhanced Dashboard..."
echo "============================================"
echo ""

# Check if we're in the right directory
if [ ! -f "dashboard/app_v2.py" ]; then
    echo "❌ Error: dashboard/app_v2.py not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Check if streamlit is installed
if ! python3 -m streamlit --version &> /dev/null; then
    echo "⚠️  Streamlit not found. Installing dependencies..."
    python3 -m pip install -r requirements.txt --quiet
fi

# Check if sample datasets exist
if [ ! -d "data/samples" ] || [ -z "$(ls -A data/samples/*.csv 2>/dev/null)" ]; then
    echo "📊 Generating sample datasets..."
    python3 scripts/generate_samples.py
    echo ""
fi

# Launch dashboard
echo "🚀 Launching dashboard..."
echo "📱 Open your browser to: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 -m streamlit run dashboard/app_v2.py

