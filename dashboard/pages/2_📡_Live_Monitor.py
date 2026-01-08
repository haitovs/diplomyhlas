"""
📡 Live Monitor Page - Real-time network traffic capture
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path
from datetime import datetime
import time

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

st.set_page_config(page_title="Live Monitor", page_icon="📡", layout="wide")

# Theme
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0a0f1a 0%, #111827 100%); }
    h1, h2, h3 { color: #f8fafc !important; }
    .live-indicator {
        display: inline-flex; align-items: center; gap: 8px;
        background: rgba(16, 185, 129, 0.2); border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 8px 16px; border-radius: 20px; color: #10b981;
    }
</style>
""", unsafe_allow_html=True)

st.title("📡 Live Network Monitor")

# Initialize session state
if 'capture_running' not in st.session_state:
    st.session_state.capture_running = False
if 'packets' not in st.session_state:
    st.session_state.packets = []

# Controls
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    interface = st.selectbox(
        "Network Interface",
        ["Wi-Fi", "Ethernet", "eth0", "wlan0", "Loopback"],
        help="Select network interface to capture"
    )

with col2:
    if st.session_state.capture_running:
        if st.button("⏹️ Stop Capture", type="secondary", width='stretch'):
            st.session_state.capture_running = False
            st.rerun()
    else:
        if st.button("▶️ Start Capture", type="primary", width='stretch'):
            st.session_state.capture_running = True
            st.rerun()

with col3:
    if st.button("🗑️ Clear", width='stretch'):
        st.session_state.packets = []
        st.rerun()

st.markdown("---")

# Status
if st.session_state.capture_running:
    st.markdown('<div class="live-indicator">🔴 LIVE - Capturing on ' + interface + '</div>', unsafe_allow_html=True)
else:
    st.info("⏸️ Capture stopped. Click 'Start Capture' to begin monitoring.")

# Metrics row
cols = st.columns(5)
packet_count = len(st.session_state.packets)
cols[0].metric("Packets", packet_count)
cols[1].metric("Threats", "0")
cols[2].metric("Bytes/s", "0 KB")
cols[3].metric("PPS", "0")
cols[4].metric("Uptime", "0:00")

# Simulated live data (demo mode)
if st.session_state.capture_running:
    import numpy as np
    
    # Add simulated packet
    new_packet = {
        'time': datetime.now().strftime('%H:%M:%S'),
        'src_ip': f"192.168.1.{np.random.randint(1, 255)}",
        'dst_ip': f"10.0.0.{np.random.randint(1, 255)}",
        'protocol': np.random.choice(['TCP', 'UDP', 'ICMP'], p=[0.7, 0.25, 0.05]),
        'port': np.random.choice([80, 443, 22, 3389, 8080]),
        'length': np.random.randint(64, 1500),
        'status': np.random.choice(['Normal', 'Normal', 'Normal', 'Suspicious'], p=[0.3, 0.3, 0.3, 0.1]),
    }
    st.session_state.packets.append(new_packet)
    
    # Keep last 100
    if len(st.session_state.packets) > 100:
        st.session_state.packets = st.session_state.packets[-100:]

st.markdown("---")

# Live chart
st.markdown("### 📈 Traffic Timeline")
if st.session_state.packets:
    df = pd.DataFrame(st.session_state.packets)
    
    # Traffic chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(df))),
        y=df['length'],
        mode='lines+markers',
        name='Bytes',
        line=dict(color='#6366f1', width=2),
        fill='tozeroy',
        fillcolor='rgba(99, 102, 241, 0.2)'
    ))
    fig.update_layout(
        height=250,
        margin=dict(l=0, r=0, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title=None),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title='Bytes'),
    )
    st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Packet table
st.markdown("### 📋 Recent Packets")
if st.session_state.packets:
    df = pd.DataFrame(st.session_state.packets[-20:][::-1])
    st.dataframe(df, width='stretch', hide_index=True)
else:
    st.info("No packets captured yet. Start capture to see live traffic.")

# Auto-refresh
if st.session_state.capture_running:
    time.sleep(1)
    st.rerun()

st.markdown("---")
st.markdown("<p style='text-align:center; color:#64748b;'>Note: Using simulated data for demo</p>", unsafe_allow_html=True)
