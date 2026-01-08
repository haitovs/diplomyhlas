"""
Live Simulation Dashboard
Real-time network anomaly detection with attack simulation
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path
from datetime import datetime
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.simulation import TrafficGenerator, AttackSimulator
from src.inference import RealtimePredictor

# Page configuration
st.set_page_config(
    page_title="Network Anomaly Detection - Live",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with fixed metric heights
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .status-live {
        color: #00ff00;
        animation: blink 1s infinite;
    }
    @keyframes blink {
        50% { opacity: 0.5; }
    }
    /* Dark theme for metric cards - fixed height */
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
    [data-testid="stMetricLabel"] {
        color: #a0c4e8 !important;
        font-weight: 600;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.8rem !important;
        font-weight: bold;
    }
    [data-testid="stMetricDelta"] {
        color: #4ade80 !important;
    }
    .attack-active {
        background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%) !important;
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    .stApp {
        background-color: #0e1117;
    }
    h1, h2, h3, h4 {
        color: #ffffff !important;
    }
    /* Alert styles */
    .alert-critical {
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 4px 0;
        border-left: 4px solid #fca5a5;
    }
    .alert-warning {
        background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 4px 0;
        border-left: 4px solid #fcd34d;
    }
    .alert-info {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 4px 0;
        border-left: 4px solid #93c5fd;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'traffic_gen' not in st.session_state:
    st.session_state.traffic_gen = TrafficGenerator(seed=42)
    st.session_state.attack_sim = AttackSimulator(st.session_state.traffic_gen)
    st.session_state.predictor = RealtimePredictor()
    st.session_state.traffic_history = []
    st.session_state.total_flows = 0
    st.session_state.total_attacks = 0
    st.session_state.attack_active = False


def generate_and_predict(n_flows: int = 20) -> pd.DataFrame:
    """Generate traffic and get predictions"""
    flows = st.session_state.attack_sim.generate_batch(n_flows)
    
    for flow in flows:
        # Get prediction
        pred = st.session_state.predictor.predict(flow)
        flow['ml_prediction'] = pred['prediction']
        flow['ml_confidence'] = pred['confidence']
        flow['ml_is_anomaly'] = pred['is_anomaly']
        
        # Update stats
        st.session_state.total_flows += 1
        if flow['is_attack'] or pred['is_anomaly']:
            st.session_state.total_attacks += 1
    
    # Add to history (keep last 500)
    st.session_state.traffic_history.extend(flows)
    st.session_state.traffic_history = st.session_state.traffic_history[-500:]
    
    return pd.DataFrame(flows)


def create_sidebar():
    """Create control sidebar"""
    st.sidebar.markdown("## 🎮 Simulation Controls")
    
    # Attack controls
    st.sidebar.markdown("### 🔥 Launch Attack")
    attack_type = st.sidebar.selectbox(
        "Attack Type",
        ["DDoS", "PortScan", "BruteForce", "Bot"]
    )
    
    attack_duration = st.sidebar.slider("Duration (seconds)", 10, 120, 30)
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🚀 START", type="primary", use_container_width=True):
            st.session_state.attack_sim.start_attack(attack_type, attack_duration)
            st.session_state.attack_active = True
    with col2:
        if st.button("🛑 STOP", type="secondary", use_container_width=True):
            st.session_state.attack_sim.stop_attack()
            st.session_state.attack_active = False
    
    # Attack status
    if st.session_state.attack_sim.attack_active:
        st.sidebar.error(f"🔴 ATTACK ACTIVE: {st.session_state.attack_sim.attack_type}")
    else:
        st.sidebar.success("🟢 No active attack")
    
    st.sidebar.markdown("---")
    
    # Model info
    st.sidebar.markdown("### 🤖 Model Info")
    model_info = st.session_state.predictor.get_model_info()
    st.sidebar.info(f"""
    **Model**: {model_info['model_type'] or 'Demo Mode'}  
    **Features**: {model_info['n_features']}  
    **Classes**: {len(model_info['classes'])}
    """)
    
    # Refresh settings
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Settings")
    auto_refresh = st.sidebar.checkbox("Auto Refresh", value=True)
    refresh_rate = st.sidebar.selectbox("Refresh Rate", ["2s", "5s", "10s"], index=0)
    
    return auto_refresh, int(refresh_rate.replace('s', ''))


def create_metrics(df: pd.DataFrame):
    """Create metrics row with fixed heights"""
    cols = st.columns(5)
    
    with cols[0]:
        st.metric(
            "📊 Total Flows",
            f"{st.session_state.total_flows:,}",
            f"+{len(df)}"
        )
    
    with cols[1]:
        attack_count = df['is_attack'].sum() if 'is_attack' in df.columns else 0
        st.metric(
            "🔴 Attacks Detected",
            f"{st.session_state.total_attacks:,}",
            f"+{attack_count}" if attack_count > 0 else "0"
        )
    
    with cols[2]:
        if len(df) > 0:
            avg_conf = df['ml_confidence'].mean() * 100
        else:
            avg_conf = 0
        st.metric(
            "🎯 Model Confidence",
            f"{avg_conf:.1f}%"
        )
    
    with cols[3]:
        total_bytes = df['total_bytes'].sum() if 'total_bytes' in df.columns else 0
        st.metric(
            "📦 Bytes/sec",
            f"{total_bytes/1e3:.1f} KB"
        )
    
    with cols[4]:
        unique_ips = df['src_ip'].nunique() if 'src_ip' in df.columns else 0
        st.metric(
            "🌐 Unique IPs",
            f"{unique_ips}"
        )


def create_traffic_chart():
    """Create traffic timeline chart"""
    if not st.session_state.traffic_history:
        return
    
    df_hist = pd.DataFrame(st.session_state.traffic_history[-100:])
    
    if df_hist.empty:
        return
    
    # Create figure
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Traffic volume
    fig.add_trace(
        go.Scatter(
            y=df_hist['total_bytes'].rolling(5).mean(),
            mode='lines',
            name='Traffic (bytes)',
            line=dict(color='#3b82f6', width=2),
            fill='tozeroy',
            fillcolor='rgba(59, 130, 246, 0.1)'
        ),
        secondary_y=False
    )
    
    # Attack markers
    attack_indices = df_hist[df_hist['is_attack'] == True].index.tolist()
    if attack_indices:
        fig.add_trace(
            go.Scatter(
                x=attack_indices,
                y=[df_hist.loc[i, 'total_bytes'] if i in df_hist.index else 0 for i in attack_indices],
                mode='markers',
                name='Attacks',
                marker=dict(color='#ef4444', size=10, symbol='x')
            ),
            secondary_y=False
        )
    
    fig.update_layout(
        height=250,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        xaxis=dict(showgrid=False, color='white'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', color='white'),
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_attack_distribution(df: pd.DataFrame):
    """Create attack type distribution"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Attack Types")
        if 'label' in df.columns:
            attack_counts = df[df['is_attack'] == True]['label'].value_counts()
            if len(attack_counts) > 0:
                fig = px.pie(
                    values=attack_counts.values,
                    names=attack_counts.index,
                    color_discrete_sequence=['#ef4444', '#f97316', '#eab308', '#22c55e']
                )
                fig.update_layout(
                    height=250,
                    margin=dict(l=0, r=0, t=10, b=0),
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No attacks detected yet")
    
    with col2:
        st.markdown("### 📡 Protocol Distribution")
        if 'protocol' in df.columns:
            proto_counts = df['protocol'].value_counts()
            fig = px.bar(
                x=proto_counts.index,
                y=proto_counts.values,
                color=proto_counts.index,
                color_discrete_map={'TCP': '#3b82f6', 'UDP': '#22c55e', 'ICMP': '#eab308'}
            )
            fig.update_layout(
                height=250,
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                xaxis=dict(color='white'),
                yaxis=dict(color='white'),
            )
            st.plotly_chart(fig, use_container_width=True)


def create_alerts(df: pd.DataFrame):
    """Create alerts section"""
    st.markdown("### ⚠️ Recent Alerts")
    
    attacks = df[df['is_attack'] == True].tail(8)
    
    if len(attacks) == 0:
        st.success("✅ No active threats detected")
        return
    
    for _, row in attacks.iterrows():
        severity = "critical" if row['label'] in ['DDoS', 'BruteForce'] else "warning"
        
        st.markdown(f"""
        <div class="alert-{severity}">
            <strong>{row['label']}</strong> | 
            {row['src_ip']}:{row['src_port']} → {row['dst_ip']}:{row['dst_port']} |
            Confidence: {row['ml_confidence']*100:.0f}%
        </div>
        """, unsafe_allow_html=True)


def create_log_table(df: pd.DataFrame):
    """Create traffic log"""
    st.markdown("### 📋 Live Traffic Log")
    
    if df.empty:
        return
    
    display_cols = ['timestamp', 'src_ip', 'dst_ip', 'protocol', 'total_bytes', 'ml_prediction', 'ml_confidence']
    available_cols = [c for c in display_cols if c in df.columns]
    
    display_df = df[available_cols].tail(15).copy()
    
    if 'timestamp' in display_df.columns:
        display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%H:%M:%S')
    if 'ml_confidence' in display_df.columns:
        display_df['ml_confidence'] = (display_df['ml_confidence'] * 100).round(1).astype(str) + '%'
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def main():
    # Header with live indicator
    st.markdown("""
        <h1 style="text-align: center;">
            🛡️ Network Anomaly Detection 
            <span class="status-live">● LIVE</span>
        </h1>
    """, unsafe_allow_html=True)
    
    # Sidebar
    auto_refresh, refresh_seconds = create_sidebar()
    
    # Generate data
    df = generate_and_predict(20)
    
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
        create_alerts(df)
    
    st.markdown("---")
    
    # Distribution charts
    create_attack_distribution(pd.DataFrame(st.session_state.traffic_history[-200:]))
    
    st.markdown("---")
    
    # Log table
    create_log_table(pd.DataFrame(st.session_state.traffic_history[-50:]))
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #6b7280; font-size: 0.8rem;">
            ML Network Anomaly Detection | Yhlas - Diploma Project 2025
        </div>
    """, unsafe_allow_html=True)
    
    # Auto refresh
    if auto_refresh:
        time.sleep(refresh_seconds)
        st.rerun()


if __name__ == "__main__":
    main()
