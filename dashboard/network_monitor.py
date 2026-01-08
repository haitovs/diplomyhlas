"""
Network Monitor Dashboard
Real-time network traffic monitoring with interface selection
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path
from datetime import datetime
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.capture import get_available_interfaces, create_capture, SCAPY_AVAILABLE
from src.simulation import TrafficGenerator, AttackSimulator
from src.inference import RealtimePredictor

# Page configuration
st.set_page_config(
    page_title="Network Monitor - Live Capture",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6f 100%);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #3d5a7f;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    [data-testid="stMetricLabel"] { color: #a0c4e8 !important; font-weight: 600; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 1.8rem !important; }
    [data-testid="stMetricDelta"] { color: #4ade80 !important; }
    .stApp { background-color: #0e1117; }
    h1, h2, h3, h4 { color: #ffffff !important; }
    .status-live { color: #00ff00; animation: blink 1s infinite; }
    .status-offline { color: #ff4444; }
    @keyframes blink { 50% { opacity: 0.5; } }
    .interface-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #0f3460;
        margin: 0.5rem 0;
    }
    .capture-active {
        background: linear-gradient(135deg, #065f46 0%, #047857 100%);
        border-color: #10b981;
    }
    .alert-box {
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
        color: white;
        padding: 12px;
        border-radius: 8px;
        margin: 4px 0;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'capture' not in st.session_state:
    st.session_state.capture = None
    st.session_state.predictor = RealtimePredictor()
    st.session_state.traffic_history = []
    st.session_state.total_packets = 0
    st.session_state.total_anomalies = 0
    st.session_state.capture_mode = 'simulation'  # 'live' or 'simulation'
    st.session_state.selected_interface = None
    # Simulation fallback
    st.session_state.traffic_gen = TrafficGenerator(seed=42)
    st.session_state.attack_sim = AttackSimulator(st.session_state.traffic_gen)


def get_traffic_data(n_packets: int = 30) -> pd.DataFrame:
    """Get traffic data from capture or simulation"""
    packets = []
    
    if st.session_state.capture_mode == 'live' and st.session_state.capture:
        # Get from live capture
        packets = st.session_state.capture.get_packets(n_packets)
    else:
        # Use simulation
        packets = st.session_state.attack_sim.generate_batch(n_packets)
    
    # Get predictions
    for pkt in packets:
        pred = st.session_state.predictor.predict(pkt)
        pkt['ml_prediction'] = pred['prediction']
        pkt['ml_confidence'] = pred['confidence']
        pkt['ml_is_anomaly'] = pred['is_anomaly']
        
        st.session_state.total_packets += 1
        if pred['is_anomaly'] or pkt.get('is_attack', False):
            st.session_state.total_anomalies += 1
    
    # Add to history
    st.session_state.traffic_history.extend(packets)
    st.session_state.traffic_history = st.session_state.traffic_history[-500:]
    
    return pd.DataFrame(packets) if packets else pd.DataFrame()


def create_sidebar():
    """Create control sidebar with interface selection"""
    st.sidebar.markdown("## 📡 Network Monitor")
    
    # Mode selection
    st.sidebar.markdown("### 🔄 Capture Mode")
    mode = st.sidebar.radio(
        "Select Mode",
        ["Simulation", "Live Capture"],
        index=0 if st.session_state.capture_mode == 'simulation' else 1
    )
    
    if mode == "Simulation":
        st.session_state.capture_mode = 'simulation'
        
        # Attack controls for simulation
        st.sidebar.markdown("### 🔥 Attack Simulation")
        attack_type = st.sidebar.selectbox("Attack Type", ["DDoS", "PortScan", "BruteForce", "Bot"])
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("🚀 Start Attack", use_container_width=True):
                st.session_state.attack_sim.start_attack(attack_type, 30)
        with col2:
            if st.button("🛑 Stop", use_container_width=True):
                st.session_state.attack_sim.stop_attack()
        
        if st.session_state.attack_sim.attack_active:
            st.sidebar.error(f"⚠️ {st.session_state.attack_sim.attack_type} ACTIVE")
        else:
            st.sidebar.success("✅ Normal traffic")
    
    else:
        st.session_state.capture_mode = 'live'
        
        # Interface selection
        st.sidebar.markdown("### 🌐 Network Interface")
        
        interfaces = get_available_interfaces()
        interface_names = [f"{iface.name} ({iface.ip})" for iface in interfaces]
        
        if interface_names:
            selected = st.sidebar.selectbox("Select Interface", interface_names)
            selected_iface = interfaces[interface_names.index(selected)]
            
            # Scapy status
            if SCAPY_AVAILABLE:
                st.sidebar.success("✅ Scapy available")
            else:
                st.sidebar.warning("⚠️ Scapy not installed - using simulation")
            
            # Capture controls
            col1, col2 = st.sidebar.columns(2)
            with col1:
                if st.button("▶️ Start", use_container_width=True):
                    if st.session_state.capture:
                        st.session_state.capture.stop()
                    st.session_state.capture = create_capture(selected_iface.name)
                    st.session_state.capture.start()
                    st.session_state.selected_interface = selected_iface.name
            with col2:
                if st.button("⏹️ Stop", use_container_width=True):
                    if st.session_state.capture:
                        st.session_state.capture.stop()
                        st.session_state.capture = None
            
            # Capture status
            if st.session_state.capture and st.session_state.capture.running:
                stats = st.session_state.capture.get_stats()
                st.sidebar.markdown(f"""
                <div class="interface-card capture-active">
                    <strong>🟢 CAPTURING</strong><br>
                    Interface: {stats['interface']}<br>
                    Packets: {stats['packet_count']:,}<br>
                    Rate: {stats['packets_per_second']:.1f}/sec
                </div>
                """, unsafe_allow_html=True)
            else:
                st.sidebar.info("Click Start to begin capture")
        else:
            st.sidebar.error("No network interfaces found")
    
    st.sidebar.markdown("---")
    
    # Refresh settings
    st.sidebar.markdown("### ⚙️ Settings")
    auto_refresh = st.sidebar.checkbox("Auto Refresh", value=True)
    refresh_rate = st.sidebar.selectbox("Refresh Rate", ["1s", "2s", "5s"], index=1)
    
    return auto_refresh, int(refresh_rate.replace('s', ''))


def create_metrics(df: pd.DataFrame):
    """Create metrics row"""
    cols = st.columns(5)
    
    with cols[0]:
        st.metric("📊 Total Packets", f"{st.session_state.total_packets:,}", f"+{len(df)}")
    
    with cols[1]:
        anomalies = len(df[df.get('ml_is_anomaly', False) == True]) if not df.empty else 0
        st.metric("🚨 Anomalies", f"{st.session_state.total_anomalies:,}", f"+{anomalies}")
    
    with cols[2]:
        mode_text = "LIVE" if st.session_state.capture_mode == 'live' else "SIM"
        st.metric("📡 Mode", mode_text)
    
    with cols[3]:
        total_bytes = df['total_bytes'].sum() if 'total_bytes' in df.columns else 0
        st.metric("📦 Bytes/sec", f"{total_bytes/1e3:.1f} KB")
    
    with cols[4]:
        unique_ips = df['src_ip'].nunique() if 'src_ip' in df.columns and not df.empty else 0
        st.metric("🌐 Unique IPs", f"{unique_ips}")


def create_traffic_chart():
    """Create traffic timeline"""
    if not st.session_state.traffic_history:
        return
    
    df = pd.DataFrame(st.session_state.traffic_history[-100:])
    
    if df.empty or 'total_bytes' not in df.columns:
        return
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(
            y=df['total_bytes'].rolling(5, min_periods=1).mean(),
            mode='lines',
            name='Traffic',
            line=dict(color='#3b82f6', width=2),
            fill='tozeroy',
            fillcolor='rgba(59, 130, 246, 0.1)'
        ),
        secondary_y=False
    )
    
    # Mark anomalies
    if 'ml_is_anomaly' in df.columns:
        anomaly_mask = df['ml_is_anomaly'] == True
        if anomaly_mask.any():
            fig.add_trace(
                go.Scatter(
                    x=df[anomaly_mask].index.tolist(),
                    y=df.loc[anomaly_mask, 'total_bytes'].tolist(),
                    mode='markers',
                    name='Anomaly',
                    marker=dict(color='#ef4444', size=10, symbol='x')
                ),
                secondary_y=False
            )
    
    fig.update_layout(
        height=250,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", y=1.02),
        xaxis=dict(showgrid=False, color='white'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', color='white'),
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_protocol_chart():
    """Create protocol distribution"""
    if not st.session_state.traffic_history:
        return
    
    df = pd.DataFrame(st.session_state.traffic_history[-200:])
    
    if df.empty or 'protocol' not in df.columns:
        return
    
    proto_counts = df['protocol'].value_counts()
    
    fig = go.Figure(data=[
        go.Bar(
            x=proto_counts.index.tolist(),
            y=proto_counts.values.tolist(),
            marker_color=['#3b82f6', '#22c55e', '#eab308', '#ef4444'][:len(proto_counts)]
        )
    ])
    
    fig.update_layout(
        height=200,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(color='white'),
        yaxis=dict(color='white'),
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_log_table(df: pd.DataFrame):
    """Create traffic log"""
    if df.empty:
        return
    
    display_cols = ['timestamp', 'src_ip', 'dst_ip', 'protocol', 'total_bytes', 'ml_prediction', 'ml_confidence']
    available = [c for c in display_cols if c in df.columns]
    
    if not available:
        return
    
    display_df = df[available].tail(15).copy()
    
    if 'timestamp' in display_df.columns:
        display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%H:%M:%S')
    if 'ml_confidence' in display_df.columns:
        display_df['ml_confidence'] = (display_df['ml_confidence'] * 100).round(1).astype(str) + '%'
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def create_alerts(df: pd.DataFrame):
    """Show recent anomalies"""
    if df.empty:
        st.success("✅ No anomalies detected")
        return
    
    anomalies = df[df.get('ml_is_anomaly', False) == True].tail(5)
    
    if len(anomalies) == 0:
        st.success("✅ No anomalies detected")
        return
    
    for _, row in anomalies.iterrows():
        st.markdown(f"""
        <div class="alert-box">
            <strong>{row.get('ml_prediction', 'UNKNOWN')}</strong> |
            {row.get('src_ip', 'N/A')}:{row.get('src_port', 'N/A')} → 
            {row.get('dst_ip', 'N/A')}:{row.get('dst_port', 'N/A')} |
            Confidence: {row.get('ml_confidence', 0)*100:.0f}%
        </div>
        """, unsafe_allow_html=True)


def export_data():
    """Export captured data to CSV"""
    if st.session_state.traffic_history:
        df = pd.DataFrame(st.session_state.traffic_history)
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Export CSV",
            csv,
            "network_capture.csv",
            "text/csv",
            use_container_width=True
        )


def main():
    # Header
    capture_status = "LIVE" if st.session_state.capture_mode == 'live' else "SIMULATION"
    status_class = "status-live" if st.session_state.capture_mode == 'live' else ""
    
    st.markdown(f"""
        <h1 style="text-align: center;">
            📡 Network Monitor 
            <span class="{status_class}">● {capture_status}</span>
        </h1>
    """, unsafe_allow_html=True)
    
    # Sidebar
    auto_refresh, refresh_seconds = create_sidebar()
    
    # Get data
    df = get_traffic_data(30)
    
    st.markdown("---")
    
    # Metrics
    create_metrics(df)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📊 Traffic Timeline")
        create_traffic_chart()
    
    with col2:
        st.markdown("### ⚠️ Alerts")
        create_alerts(df)
    
    st.markdown("---")
    
    # Protocol and Log
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 📡 Protocols")
        create_protocol_chart()
        export_data()
    
    with col2:
        st.markdown("### 📋 Traffic Log")
        create_log_table(pd.DataFrame(st.session_state.traffic_history[-50:]))
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #6b7280; font-size: 0.8rem;">
            Network Anomaly Detection | Yhlas - Diploma Project 2025
        </div>
    """, unsafe_allow_html=True)
    
    # Auto refresh
    if auto_refresh:
        time.sleep(refresh_seconds)
        st.rerun()


if __name__ == "__main__":
    main()
