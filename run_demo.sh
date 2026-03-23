#!/bin/bash
# ============================================================
#  Network Anomaly Analyzer - Demo Runner
#  Launches the dashboard (all controls are in the UI)
# ============================================================

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "============================================"
echo "  Network Anomaly Analyzer - Demo"
echo "============================================"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found. Please install Python 3.11+."
    exit 1
fi

# Check / install deps
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "Installing requirements..."
    pip3 install -r requirements.txt
fi

# Generate sample data if missing
if [ ! -d "data/samples" ] || [ -z "$(ls -A data/samples 2>/dev/null)" ]; then
    echo "Generating sample datasets..."
    python3 scripts/generate_samples.py
    echo ""
fi

echo "Starting dashboard on http://localhost:4086 ..."
echo ""
echo "  Everything is controlled from the UI:"
echo "    - Start/Stop packet capture"
echo "    - Launch attack simulations"
echo "    - Block malicious IPs"
echo ""
echo "  NOTE: Run with sudo for packet capture & attacks:"
echo "    sudo ./run_demo.sh"
echo ""
echo "  Press Ctrl+C to stop."
echo "============================================"
echo ""

streamlit run "dashboard/1_🏠_Home.py" \
    --server.port 4086 \
    --server.headless true
