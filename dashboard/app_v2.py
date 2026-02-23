"""
Enhanced Streamlit Dashboard for Network Anomaly Detection
Professional Cybersecurity-Themed Real-time Monitoring Interface with Multiple Data Sources
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from pathlib import Path
import time
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.data_sources import DataSourceManager, SimulationDataSource
from src.inference.realtime import RealtimePredictor
from dashboard import components

# Page configuration
st.set_page_config(
    page_title="Yhlas Network Analyzer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Cybersecurity Theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Root Variables */
    :root {
        --bg-primary: #0a0f1a;
        --bg-secondary: #111827;
        --accent-primary: #6366f1;
        --accent-secondary: #8b5cf6;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
        
        /* Spacing System */
        --space-xs: 0.25rem;
        --space-sm: 0.5rem;
        --space-md: 1rem;
        --space-lg: 1.5rem;
        --space-xl: 2rem;
        --space-2xl: 3rem;
        
        /* Font Sizes */
        --text-xs: 0.75rem;
        --text-sm: 0.875rem;
        --text-base: 1rem;
        --text-lg: 1.125rem;
        --text-xl: 1.25rem;
        --text-2xl: 1.5rem;
        --text-3xl: 1.875rem;
    }
    
    /* Main App Background */
    .stApp {
        background: linear-gradient(135deg, #0a0f1a 0%, #111827 100%);
        font-family: 'Inter', sans-serif;
        color: #f8fafc;
    }
    
    /* Main Content Area */
    .main .block-container {
        padding-top: var(--space-xl);
        padding-bottom: var(--space-2xl);
        max-width: 1200px;
    }
    
    /* Headers */
    .main-header {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: var(--text-3xl);
        font-weight: 700;
        text-align: center;
        margin-bottom: var(--space-sm);
    }
    
    .sub-header {
        color: #94a3b8;
        text-align: center;
        font-size: var(--text-base);
        margin-bottom: var(--space-2xl);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #f8fafc;
    }
    
    /* Sidebar Headers */
    [data-testid="stSidebar"] h2 {
        color: #f8fafc;
        font-size: var(--text-xl);
        font-weight: 600;
        margin-bottom: var(--space-md);
    }
    
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] h4 {
        color: #cbd5e1;
        font-size: var(--text-sm);
        font-weight: 500;
        margin-top: var(--space-lg);
        margin-bottom: var(--space-sm);
    }
    
    /* Selectbox Styling */
    .stSelectbox label, .stSlider label {
        color: #cbd5e1 !important;
        font-weight: 500;
    }
    
    .stSelectbox > div > div {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 8px;
        color: #f8fafc;
    }
    
    /* Metric Cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 12px;
        padding: var(--space-md) var(--space-lg);
        min-height: 100px;
        transition: all 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(99, 102, 241, 0.3);
        border-color: rgba(99, 102, 241, 0.5);
    }
    
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: var(--text-xs);
        font-weight: 500;
    }
    
    [data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-size: var(--text-2xl);
        font-weight: 700;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.875rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: var(--space-sm) var(--space-lg);
        min-height: 42px;
        font-weight: 600;
        font-size: var(--text-sm);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Status Badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    .status-live {
        background: rgba(16, 185, 129, 0.2);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #10b981;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .pulse-dot {
        width: 8px;
        height: 8px;
        background: #10b981;
        border-radius: 50%;
        animation: pulse 2s ease-in-out infinite;
    }
    
    /* Threat/Alert Cards */
    .threat-card-critical {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.2) 100%);
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-left: 3px solid #ef4444;
        border-radius: 10px;
        padding: var(--space-lg);
        margin: var(--space-md) 0;
    }
    
    .threat-card-high {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(217, 119, 6, 0.2) 100%);
        border: 1px solid rgba(245, 158, 11, 0.4);
        border-left: 3px solid #f59e0b;
        border-radius: 10px;
        padding: var(--space-lg);
        margin: var(--space-md) 0;
    }
    
    .threat-card-medium {
        background: linear-gradient(135deg, rgba(234, 179, 8, 0.2) 0%, rgba(202, 138, 4, 0.2) 100%);
        border: 1px solid rgba(234, 179, 8, 0.4);
        border-left: 3px solid #eab308;
        border-radius: 10px;
        padding: var(--space-lg);
        margin: var(--space-md) 0;
    }
    
    .threat-card-low {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.2) 100%);
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-left: 3px solid #10b981;
        border-radius: 10px;
        padding: var(--space-lg);
        margin: var(--space-md) 0;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: transparent;
        margin-bottom: var(--space-md);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 8px;
        color: #94a3b8;
        padding: var(--space-sm) var(--space-lg);
        font-size: var(--text-sm);
        font-weight: 500;
        min-height: 40px;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(99, 102, 241, 0.15);
        color: #cbd5e1;
        border-color: rgba(99, 102, 241, 0.3);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, rgba(139, 92, 246, 0.3) 100%);
        border-color: rgba(99, 102, 241, 0.6);
        color: #f8fafc !important;
        font-weight: 600;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 8px;
        color: #f8fafc;
        font-weight: 500;
        padding: var(--space-sm) var(--space-md);
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(99, 102, 241, 0.15);
        border-color: rgba(99, 102, 241, 0.4);
    }
    
    /* Info/Warning/Success Boxes */
    .stAlert {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 8px;
        color: #f8fafc;
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        background: rgba(30, 41, 59, 0.5);
        border: 2px dashed rgba(99, 102, 241, 0.3);
        border-radius: 10px;
        padding: var(--space-lg);
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(99, 102, 241, 0.6);
        background: rgba(99, 102, 241, 0.08);
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background: rgba(99, 102, 241, 0.2);
    }
    
    .stSlider [role="slider"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    }
    
    /* Markdown Text */
    .stMarkdown {
        color: #f8fafc;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #f8fafc;
    }
    
    /* Horizontal Rule */
    hr {
        border: none;
        border-top: 1px solid rgba(99, 102, 241, 0.15);
        margin: var(--space-2xl) 0;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #6366f1 !important;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1e293b;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataSourceManager()
    st.session_state.predictor = RealtimePredictor()
    st.session_state.history_df = pd.DataFrame()
    st.session_state.total_processed = 0


def create_header():
    """Create professional dashboard header"""
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown('<p class="main-header">🛡️ Yhlas Network Analyzer</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">ML-Powered Network Anomaly Detection System</p>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('''
            <div class="status-badge status-live">
                <div class="pulse-dot"></div>
                <span>LIVE</span>
            </div>
        ''', unsafe_allow_html=True)


def create_sidebar():
    """Create enhanced sidebar with data source selection"""
    with st.sidebar:
        st.markdown("## ⚙️ Control Panel")
        st.markdown("---")
        
        # Data source selection
        st.markdown("### 📊 Data Source")
        
        # Get available sources
        sources = st.session_state.data_manager.list_sources()
        source_dict = {name: sid for sid, name, desc in sources}
        
        selected_name = st.selectbox(
            "Select Data Source",
            options=list(source_dict.keys()),
            label_visibility="collapsed",
            help="Choose where to load network traffic data from"
        )
        
        selected_id = source_dict[selected_name]
        
        # Update current source
        if selected_id != st.session_state.data_manager.current_source:
            st.session_state.data_manager.set_source(selected_id)
            st.session_state.history_df = pd.DataFrame()  # Reset history
        
        # Show source info
        source_info = st.session_state.data_manager.get_source_info()
        with st.expander("ℹ️ Source Info"):
            st.json(source_info, expanded=False)
        
        # File upload section
        st.markdown("#### 📤 Upload Custom CSV")
        uploaded_file = st.file_uploader(
            "Upload network traffic data",
            type=['csv'],
            help="Upload a CSV file with network traffic data. Required columns: src_ip, dst_ip, protocol",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            try:
                from src.data.data_sources import UploadedDataSource
                
                # Create uploaded data source
                upload_source_id = f"uploaded_{uploaded_file.name}"
                
                # Only create if not already exists
                if upload_source_id not in st.session_state.data_manager.sources:
                    upload_source = UploadedDataSource(uploaded_file, uploaded_file.name)
                    st.session_state.data_manager.add_source(upload_source_id, upload_source)
                    st.session_state.data_manager.set_source(upload_source_id)
                    st.session_state.history_df = pd.DataFrame()
                    st.success(f"✅ Loaded {uploaded_file.name}")
                else:
                    st.info(f"Using uploaded file: {uploaded_file.name}")
                    
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
                st.info("Make sure your CSV has columns: src_ip, dst_ip, protocol")
        
        st.markdown("---")
        
        # Attack simulation controls (if simulation source)
        if 'simulation' in selected_id:
            st.markdown("### ⚡ Attack Simulation")
            attack_type = st.selectbox(
                "Attack Type",
                ["DDoS", "PortScan", "BruteForce", "Bot"],
                label_visibility="collapsed"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("▶️ Start", width='stretch'):
                    source = st.session_state.data_manager.get_current_source()
                    if isinstance(source, SimulationDataSource):
                        source.start_attack(attack_type, duration_sec=60)
                        st.success(f"Started {attack_type} attack!")
            with col2:
                if st.button("⏹️ Stop", width='stretch'):
                    source = st.session_state.data_manager.get_current_source()
                    if isinstance(source, SimulationDataSource):
                        source.stop_attack()
                        st.info("Attack stopped")
            
            st.markdown("---")
        
        # Detection settings
        st.markdown("### 🎯 Detection")
        threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.7, 0.05)
        
        st.markdown("---")
        
        # Display settings
        st.markdown("### 📺 Display")
        refresh_rate = st.selectbox("Refresh Rate", ["Manual", "3s", "5s", "10s"])
        batch_size = st.slider("Flows per Batch", 10, 200, 50, 10)
        
        st.markdown("---")
        
        # Model info
        with st.expander("🤖 Model Info"):
            try:
                model_info = st.session_state.predictor.get_model_info()
                st.json(model_info)
            except:
                st.warning("Model not loaded")
        
        return threshold, refresh_rate, batch_size


def process_data(batch_size):
    """Process new data batch"""
    # Get data from current source
    new_data = st.session_state.data_manager.get_data(n_samples=batch_size)
    
    if len(new_data) == 0:
        return pd.DataFrame()
    
    # Get predictions
    predictions = st.session_state.predictor.predict_batch(new_data.to_dict('records'))
    
    # Add predictions to dataframe
    new_data['ml_prediction'] = [p['prediction'] for p in predictions]
    new_data['ml_confidence'] = [p['confidence'] for p in predictions]
    new_data['ml_is_anomaly'] = [p['is_anomaly'] for p in predictions]
    
    # Add timestamp if not exists
    if 'timestamp' not in new_data.columns:
        current_time = datetime.now()
        new_data['timestamp'] = [current_time - timedelta(seconds=i) for i in range(len(new_data))[::-1]]
    
    # Append to history
    st.session_state.total_processed += len(new_data)
    st.session_state.history_df = pd.concat([st.session_state.history_df, new_data], ignore_index=True)
    
    # Keep only last 1000 records
    if len(st.session_state.history_df) > 1000:
        st.session_state.history_df = st.session_state.history_df.tail(1000)
    
    return new_data


def create_metrics_row(df):
    """Create animated top metrics row"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_flows = st.session_state.total_processed
    
    with col1:
        st.metric(
            "📊 Total Flows",
            f"{total_flows:,}",
            f"+{len(df)}"
        )
    
    with col2:
        anomaly_count = df['ml_is_anomaly'].sum() if len(df) > 0 else 0
        anomaly_pct = (anomaly_count / len(df) * 100) if len(df) > 0 else 0
        st.metric(
            "⚠️ Threats Detected",
            f"{int(anomaly_count)}",
            f"{anomaly_pct:.1f}%",
            delta_color="inverse"
        )
    
    with col3:
        avg_conf = df['ml_confidence'].mean() if len(df) > 0 else 0
        st.metric(
            "🎯 Avg Confidence",
            f"{avg_conf*100:.1f}%"
        )
    
    with col4:
        if 'fwd_bytes' in df.columns and 'bwd_bytes' in df.columns:
            total_mb = (df['fwd_bytes'].sum() + df['bwd_bytes'].sum()) / 1e6
        else:
            total_mb = len(df) * 0.5  # Estimate
        st.metric(
            "💾 Data Analyzed",
            f"{total_mb:.2f} MB"
        )
    
    with col5:
        unique_ips = df['src_ip'].nunique() if 'src_ip' in df.columns else 0
        st.metric(
            "🌐 Unique Sources",
            f"{unique_ips}"
        )


def create_traffic_chart(df):
    """Create real-time traffic chart with anomaly highlights"""
    st.markdown("#### 📈 Traffic Timeline")
    
    if len(df) == 0:
        st.info("No data to display")
        return
    
    # Ensure timestamp column
    if 'timestamp' not in df.columns:
        df['timestamp'] = pd.date_range(end=datetime.now(), periods=len(df), freq='1s')
    
    # Aggregate by time windows
    df_sorted = df.sort_values('timestamp')
    df_sorted['time_window'] = pd.to_datetime(df_sorted['timestamp']).dt.floor('10s')
    
    df_agg = df_sorted.groupby('time_window').agg({
        'ml_is_anomaly': ['sum', 'count']
    }).reset_index()
    
    df_agg.columns = ['timestamp', 'anomalies', 'total']
    
    fig = go.Figure()
    
    # Total traffic
    fig.add_trace(go.Scatter(
        x=df_agg['timestamp'],
        y=df_agg['total'],
        name="Total Flows",
        line=dict(color='#6366f1', width=2),
        fill='tozeroy',
        fillcolor='rgba(99, 102, 241, 0.2)'
    ))
    
    # Anomalies
    anomaly_windows = df_agg[df_agg['anomalies'] > 0]
    if len(anomaly_windows) > 0:
        fig.add_trace(go.Scatter(
            x=anomaly_windows['timestamp'],
            y=anomaly_windows['total'],
            name="Anomalies Detected",
            mode='markers',
            marker=dict(
                color='#ef4444',
                size=12,
                symbol='circle',
                line=dict(color='#fff', width=2)
            )
        ))
    
    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=30, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color='#94a3b8')
        ),
        hovermode="x unified",
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.05)',
            tickfont=dict(color='#94a3b8')
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.05)',
            tickfont=dict(color='#94a3b8'),
            title=dict(text="Flows", font=dict(color='#94a3b8'))
        )
    )
    
    st.plotly_chart(fig, width='stretch')


def create_attack_distribution(df):
    """Create attack type distribution charts"""
    col1, col2 = st.columns(2)
    
    anomalies_df = df[df['ml_is_anomaly']]
    
    with col1:
        st.markdown("#### 🎯 Attack Types")
        
        if len(anomalies_df) > 0:
            attack_counts = anomalies_df['ml_prediction'].value_counts()
            colors = ['#ef4444', '#f59e0b', '#eab308', '#8b5cf6', '#06b6d4', '#10b981']
            
            fig = go.Figure(data=[go.Pie(
                labels=attack_counts.index,
                values=attack_counts.values,
                hole=0.5,
                marker=dict(colors=colors[:len(attack_counts)]),
                textinfo='percent+label',
                textfont=dict(color='#f8fafc', size=11)
            )])
            
            fig.update_layout(
                height=350,
                margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                annotations=[dict(
                    text=f'{len(attack_counts)}<br>Types',
                    x=0.5, y=0.5,
                    font=dict(size=20, color='#f8fafc'),
                    showarrow=False
                )]
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("✅ No attacks detected!")
    
    with col2:
        st.markdown("#### 📊 Confidence Distribution")
        
        if len(df) > 0:
            fig = go.Figure(data=[go.Histogram(
                x=df['ml_confidence'],
                nbinsx=15,
                marker=dict(
                    color='#6366f1',
                    line=dict(width=1, color='#8b5cf6')
                )
            )])
            
            fig.update_layout(
                height=350,
                margin=dict(l=20, r=20, t=20, b=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    gridcolor='rgba(255,255,255,0.05)',
                    tickfont=dict(color='#94a3b8'),
                    title=dict(text="Confidence", font=dict(color='#94a3b8'))
                ),
                yaxis=dict(
                    gridcolor='rgba(255,255,255,0.05)',
                    tickfont=dict(color='#94a3b8'),
                    title=dict(text="Count", font=dict(color='#94a3b8'))
                ),
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")


def create_alerts_section(df):
    """Create enhanced alerts section"""
    anomalies = df[df['ml_is_anomaly']].tail(10)
    
    if len(anomalies) == 0:
        st.success("✅ No threats detected in current data!")
        return
    
    # Assign severity based on attack type
    severity_map = {
        'DDoS': 'critical', 'Bot': 'critical', 'Botnet': 'critical',
        'BruteForce': 'high', 'SQLi': 'high',
        'PortScan': 'medium', 'XSS': 'medium',
        'BENIGN': 'low'
    }
    
    for _, row in anomalies.iterrows():
        pred = row.get('ml_prediction', 'Unknown')
        severity = severity_map.get(pred, 'medium')
        severity_icon = {
            'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'
        }.get(severity, '⚪')
        
        src_ip = row.get('src_ip', 'N/A')
        dst_ip = row.get('dst_ip', 'N/A')
        dst_port = row.get('dst_port', 0)
        confidence = row.get('ml_confidence', 0)
        timestamp = row.get('timestamp', datetime.now())
        
        st.markdown(f'''
            <div class="threat-card-{severity}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-size: 1.25rem; margin-right: 8px;">{severity_icon}</span>
                        <strong style="color: #f8fafc;">{pred}</strong>
                        <span style="color: #94a3b8; margin-left: 12px;">
                            {src_ip} → {dst_ip}:{dst_port}
                        </span>
                    </div>
                    <div style="text-align: right;">
                        <span style="color: #f8fafc; font-weight: 600;">{confidence*100:.1f}%</span>
                        <span style="color: #64748b; margin-left: 12px; font-size: 0.875rem;">
                            {pd.to_datetime(timestamp).strftime('%H:%M:%S')}
                        </span>
                    </div>
                </div>
            </div>
        ''', unsafe_allow_html=True)


def main():
    """Main dashboard function"""
    create_header()
    threshold, refresh_rate, batch_size = create_sidebar()
    
    # Control buttons
    col1, col2, col3 = st.columns([3, 1.5, 1.5])
    with col1:
        st.info(f"🔄 **Last Update**: {datetime.now().strftime('%H:%M:%S')} | **Refresh**: {refresh_rate}")
    with col2:
        if st.button("🔄 Refresh Now"):
            with st.spinner("Processing data..."):
                time.sleep(0.3)  # Visual feedback
                st.rerun()
    with col3:
        if st.button("🗑️ Clear History"):
            st.session_state.history_df = pd.DataFrame()
            st.session_state.total_processed = 0
            st.success("History cleared!")
            time.sleep(0.5)
            st.rerun()
    
    st.markdown("---")
    
    # Process new data
    with st.spinner("⚙️ Analyzing network traffic..."):
        new_data = process_data(batch_size)
    
    # Use history for visualizations
    display_df = st.session_state.history_df.tail(500)
    
    if len(display_df) > 0:
        # Metrics row
        create_metrics_row(display_df)
        
        st.markdown("---")
        
        # Traffic chart
        create_traffic_chart(display_df)
        
        st.markdown("---")
        
        # Attack distribution
        create_attack_distribution(display_df)
        
        st.markdown("---")
        
        # Tabbed content
        tab1, tab2 = st.tabs(["⚠️ Live Alerts", "📥 Export Data"])
        
        with tab1:
            create_alerts_section(display_df)
        
        with tab2:
            st.markdown("### Export Analysis Results")
            
            col1, col2 = st.columns(2)
            with col1:
                components.export_button(
                    display_df,
                    f"network_traffic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "csv",
                    "📥 Export as CSV"
                )
            with col2:
                components.export_button(
                    display_df,
                    f"network_traffic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    "json",
                    "📥 Export as JSON"
                )
    else:
        st.info("No data available. Click 'Refresh Now' to load data.")
    
    # Footer
    st.markdown('''
        <div style="text-align: center; color: #64748b; font-size: 0.875rem; padding: 2rem 0; border-top: 1px solid rgba(255, 255, 255, 0.05); margin-top: 3rem;">
            <p>Yhlas Network Analyzer v2.0 | ML-Powered Network Anomaly Detection</p>
            <p>Diploma Project 2025 | Built with ❤️</p>
        </div>
    ''', unsafe_allow_html=True)
    
    # Auto refresh
    if refresh_rate != "Manual":
        seconds = int(refresh_rate.replace('s', ''))
        time.sleep(seconds)
        st.rerun()


if __name__ == "__main__":
    main()
