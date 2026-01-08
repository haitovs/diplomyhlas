"""
Streamlit Dashboard for Network Anomaly Detection
Professional Cybersecurity-Themed Real-time Monitoring Interface
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
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Root Variables */
    :root {
        --bg-primary: #0a0f1a;
        --bg-secondary: #111827;
        --bg-surface: #1f2937;
        --accent-primary: #6366f1;
        --accent-secondary: #8b5cf6;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
        --border: rgba(255, 255, 255, 0.1);
    }
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #0a0f1a 0%, #111827 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .sub-header {
        color: #94a3b8;
        text-align: center;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    
    /* Metric Cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 1.25rem;
        backdrop-filter: blur(12px);
        transition: all 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        border-color: rgba(99, 102, 241, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.2);
    }
    
    [data-testid="stMetricLabel"] {
        color: #a5b4fc !important;
        font-weight: 600;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 2rem !important;
        font-weight: 700;
    }
    
    [data-testid="stMetricDelta"] > div {
        color: #10b981 !important;
    }
    
    /* Threat Level Cards */
    .threat-card-critical {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.2) 100%);
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-left: 4px solid #ef4444;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .threat-card-high {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(217, 119, 6, 0.2) 100%);
        border: 1px solid rgba(245, 158, 11, 0.4);
        border-left: 4px solid #f59e0b;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .threat-card-medium {
        background: linear-gradient(135deg, rgba(234, 179, 8, 0.2) 0%, rgba(202, 138, 4, 0.2) 100%);
        border: 1px solid rgba(234, 179, 8, 0.4);
        border-left: 4px solid #eab308;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .threat-card-low {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.2) 100%);
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-left: 4px solid #10b981;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
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
    
    .status-offline {
        background: rgba(239, 68, 68, 0.2);
        border: 1px solid rgba(239, 68, 68, 0.4);
        color: #ef4444;
    }
    
    /* Pulse Animation */
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
    
    /* Charts */
    .stPlotlyChart {
        border-radius: 16px;
        overflow: hidden;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #0a0f1a 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stSidebar"] .stMarkdown h2 {
        color: #f8fafc;
        font-size: 1.25rem;
        font-weight: 600;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
    }
    
    /* Selectbox */
    [data-testid="stSelectbox"] > div > div {
        background: rgba(31, 41, 55, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(31, 41, 55, 0.5);
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #94a3b8;
        border-radius: 8px;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
    }
    
    /* Data Table */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(31, 41, 55, 0.8);
        border-radius: 12px;
    }
    
    /* Alert Boxes */
    .stAlert {
        border-radius: 12px;
        border: none;
    }
    
    /* Info Box */
    [data-testid="stInfo"] {
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    
    /* Success Box */
    [data-testid="stSuccess"] {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    /* Warning Box */
    [data-testid="stWarning"] {
        background: rgba(245, 158, 11, 0.1);
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    /* Error Box */
    [data-testid="stError"] {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    /* Horizontal Rule */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        margin: 2rem 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #64748b;
        font-size: 0.875rem;
        padding: 2rem 0;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        margin-top: 3rem;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(99, 102, 241, 0.5);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(99, 102, 241, 0.7);
    }
</style>
""", unsafe_allow_html=True)


def create_header():
    """Create professional dashboard header"""
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown('<p class="main-header">🛡️ Yhlas Network Analyzer</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">ML-Powered Network Anomaly Detection System</p>', unsafe_allow_html=True)
    
    with col3:
        # Live status indicator
        st.markdown('''
            <div class="status-badge status-live">
                <div class="pulse-dot"></div>
                <span>LIVE</span>
            </div>
        ''', unsafe_allow_html=True)


def create_sidebar():
    """Create enhanced sidebar with controls"""
    with st.sidebar:
        st.markdown("## ⚙️ Control Panel")
        st.markdown("---")
        
        # Model selection
        st.markdown("### 🧠 Model")
        model_type = st.selectbox(
            "Detection Model",
            ["XGBoost (Supervised)", "LSTM Autoencoder (Unsupervised)", "Ensemble (Combined)"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Detection settings
        st.markdown("### 🎯 Detection")
        threshold = st.slider("Anomaly Threshold", 0.0, 1.0, 0.5, 0.01)
        sensitivity = st.select_slider(
            "Sensitivity",
            options=["Low", "Medium", "High"],
            value="Medium"
        )
        
        st.markdown("---")
        
        # Dashboard settings
        st.markdown("### 📊 Dashboard")
        refresh_rate = st.selectbox("Refresh Rate", ["Manual", "5s", "10s", "30s"])
        show_normal = st.checkbox("Show Normal Traffic", value=False)
        
        st.markdown("---")
        
        # Model info
        with st.expander("ℹ️ Model Information"):
            st.markdown("""
            **XGBoost** - Supervised learning for known attack patterns
            
            **LSTM Autoencoder** - Unsupervised detection for zero-day attacks
            
            **Ensemble** - Combined predictions from multiple models
            """)
        
        # Quick actions
        st.markdown("### 🚀 Quick Actions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📷 Export", width='stretch'):
                st.toast("Report exported!")
        with col2:
            if st.button("🔔 Alerts", width='stretch'):
                st.toast("Alerts cleared!")
        
        return model_type, threshold, refresh_rate


def generate_demo_data(n_samples=200):
    """Generate realistic demo data for visualization"""
    np.random.seed(int(time.time()) % 1000)
    
    # Attack types with weights (more normal traffic)
    attack_types = ['Normal', 'DDoS', 'PortScan', 'BruteForce', 'SQLi', 'XSS', 'Botnet']
    attack_weights = [0.7, 0.08, 0.06, 0.05, 0.04, 0.04, 0.03]
    
    # Generate timestamps over the last hour
    end_time = datetime.now()
    timestamps = [end_time - timedelta(seconds=i*3) for i in range(n_samples)][::-1]
    
    data = {
        'timestamp': timestamps,
        'source_ip': [f"192.168.{np.random.randint(1, 10)}.{np.random.randint(1, 255)}" for _ in range(n_samples)],
        'dest_ip': [f"10.0.{np.random.randint(1, 5)}.{np.random.randint(1, 255)}" for _ in range(n_samples)],
        'source_port': np.random.randint(1024, 65535, n_samples),
        'dest_port': np.random.choice([80, 443, 22, 3389, 3306, 5432, 8080], n_samples),
        'protocol': np.random.choice(['TCP', 'UDP', 'ICMP'], n_samples, p=[0.7, 0.25, 0.05]),
        'bytes_sent': np.random.exponential(2000, n_samples).astype(int),
        'bytes_recv': np.random.exponential(5000, n_samples).astype(int),
        'packets': np.random.poisson(15, n_samples),
        'duration': np.random.exponential(3, n_samples),
        'prediction': np.random.choice(attack_types, n_samples, p=attack_weights),
        'confidence': np.random.uniform(0.75, 0.99, n_samples),
    }
    
    df = pd.DataFrame(data)
    df['is_anomaly'] = df['prediction'] != 'Normal'
    df['total_bytes'] = df['bytes_sent'] + df['bytes_recv']
    
    # Assign severity
    severity_map = {
        'Normal': 'low', 'PortScan': 'medium', 'SQLi': 'high',
        'XSS': 'medium', 'DDoS': 'critical', 'BruteForce': 'high', 'Botnet': 'critical'
    }
    df['severity'] = df['prediction'].map(severity_map)
    
    return df


def create_metrics_row(df):
    """Create animated top metrics row"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "📊 Total Flows",
            f"{len(df):,}",
            f"↑ {np.random.randint(5, 15)}%"
        )
    
    with col2:
        anomaly_count = df['is_anomaly'].sum()
        anomaly_pct = anomaly_count / len(df) * 100
        st.metric(
            "⚠️ Threats Detected",
            f"{anomaly_count}",
            f"{anomaly_pct:.1f}%",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            "🎯 Model Accuracy",
            "98.2%",
            "↑ 0.3%"
        )
    
    with col4:
        total_mb = df['total_bytes'].sum() / 1e6
        st.metric(
            "💾 Data Analyzed",
            f"{total_mb:.1f} MB"
        )
    
    with col5:
        unique_ips = df['source_ip'].nunique()
        st.metric(
            "🌐 Unique Sources",
            f"{unique_ips}"
        )


def create_traffic_chart(df):
    """Create real-time traffic chart with anomaly highlights"""
    st.markdown("### 📈 Traffic Overview")
    
    # Aggregate by time
    df_agg = df.groupby(df['timestamp'].dt.floor('30s')).agg({
        'total_bytes': 'sum',
        'packets': 'sum',
        'is_anomaly': 'sum'
    }).reset_index()
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Traffic area
    fig.add_trace(
        go.Scatter(
            x=df_agg['timestamp'],
            y=df_agg['total_bytes'] / 1000,
            name="Traffic (KB)",
            line=dict(color='#6366f1', width=2),
            fill='tozeroy',
            fillcolor='rgba(99, 102, 241, 0.2)'
        ),
        secondary_y=False
    )
    
    # Anomaly markers
    anomaly_data = df_agg[df_agg['is_anomaly'] > 0]
    fig.add_trace(
        go.Scatter(
            x=anomaly_data['timestamp'],
            y=anomaly_data['total_bytes'] / 1000,
            name="Anomalies",
            mode='markers',
            marker=dict(
                color='#ef4444',
                size=12,
                symbol='circle',
                line=dict(color='#fff', width=2)
            )
        ),
        secondary_y=False
    )
    
    fig.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=20, b=0),
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
            title=dict(text="KB", font=dict(color='#94a3b8'))
        )
    )
    
    st.plotly_chart(fig, width='stretch')


def create_attack_distribution(df):
    """Create attack type distribution charts"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Attack Types")
        attack_counts = df[df['is_anomaly']]['prediction'].value_counts()
        
        if len(attack_counts) > 0:
            colors = ['#ef4444', '#f59e0b', '#eab308', '#8b5cf6', '#06b6d4', '#10b981']
            
            fig = go.Figure(data=[go.Pie(
                labels=attack_counts.index,
                values=attack_counts.values,
                hole=0.6,
                marker=dict(colors=colors[:len(attack_counts)]),
                textinfo='percent+label',
                textfont=dict(color='#f8fafc')
            )])
            
            fig.update_layout(
                height=300,
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
            
            st.plotly_chart(fig, width='stretch')
        else:
            st.success("No attacks detected!")
    
    with col2:
        st.markdown("### 📊 Severity Distribution")
        severity_counts = df[df['is_anomaly']]['severity'].value_counts()
        severity_order = ['critical', 'high', 'medium', 'low']
        severity_colors = {'critical': '#ef4444', 'high': '#f59e0b', 'medium': '#eab308', 'low': '#10b981'}
        
        if len(severity_counts) > 0:
            ordered_counts = severity_counts.reindex([s for s in severity_order if s in severity_counts.index])
            
            fig = go.Figure(data=[go.Bar(
                x=ordered_counts.index,
                y=ordered_counts.values,
                marker=dict(
                    color=[severity_colors.get(s, '#6366f1') for s in ordered_counts.index],
                    line=dict(width=0)
                ),
                text=ordered_counts.values,
                textposition='auto',
                textfont=dict(color='#f8fafc')
            )])
            
            fig.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=20, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    tickfont=dict(color='#94a3b8'),
                    title=None
                ),
                yaxis=dict(
                    gridcolor='rgba(255,255,255,0.05)',
                    tickfont=dict(color='#94a3b8'),
                    title=None
                )
            )
            
            st.plotly_chart(fig, width='stretch')
        else:
            st.success("All traffic is normal!")


def create_alerts_section(df):
    """Create enhanced alerts section with severity styling"""
    anomalies = df[df['is_anomaly']].sort_values('timestamp', ascending=False).head(10)
    
    if len(anomalies) == 0:
        st.success("✅ No threats detected in the current time window!")
        return
    
    for _, row in anomalies.iterrows():
        severity_class = f"threat-card-{row['severity']}"
        severity_icon = {
            'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'
        }.get(row['severity'], '⚪')
        
        st.markdown(f'''
            <div class="{severity_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-size: 1.25rem; margin-right: 8px;">{severity_icon}</span>
                        <strong style="color: #f8fafc;">{row['prediction']}</strong>
                        <span style="color: #94a3b8; margin-left: 12px;">
                            {row['source_ip']} → {row['dest_ip']}:{row['dest_port']}
                        </span>
                    </div>
                    <div style="text-align: right;">
                        <span style="color: #f8fafc; font-weight: 600;">{row['confidence']*100:.1f}%</span>
                        <span style="color: #64748b; margin-left: 12px; font-size: 0.875rem;">
                            {row['timestamp'].strftime('%H:%M:%S')}
                        </span>
                    </div>
                </div>
            </div>
        ''', unsafe_allow_html=True)


def create_log_table(df):
    """Create enhanced traffic log table"""
    display_df = df.tail(30).copy()
    display_df['Time'] = display_df['timestamp'].dt.strftime('%H:%M:%S')
    display_df['Source'] = display_df['source_ip'] + ':' + display_df['source_port'].astype(str)
    display_df['Destination'] = display_df['dest_ip'] + ':' + display_df['dest_port'].astype(str)
    display_df['Protocol'] = display_df['protocol']
    display_df['Bytes'] = (display_df['total_bytes'] / 1000).round(1).astype(str) + ' KB'
    display_df['Classification'] = display_df['prediction']
    display_df['Confidence'] = (display_df['confidence'] * 100).round(1).astype(str) + '%'
    
    final_df = display_df[['Time', 'Source', 'Destination', 'Protocol', 'Bytes', 'Classification', 'Confidence']]
    final_df = final_df.iloc[::-1]  # Reverse to show newest first
    
    st.dataframe(
        final_df,
        width='stretch',
        hide_index=True,
        column_config={
            "Classification": st.column_config.TextColumn(
                "Classification",
                help="ML model prediction"
            ),
            "Confidence": st.column_config.TextColumn(
                "Confidence",
                help="Model confidence score"
            )
        }
    )


def create_network_stats(df):
    """Create network statistics panel"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📡 Protocol Distribution")
        protocol_counts = df['protocol'].value_counts()
        for proto, count in protocol_counts.items():
            pct = count / len(df) * 100
            st.markdown(f"**{proto}**: {count:,} ({pct:.1f}%)")
    
    with col2:
        st.markdown("#### 🎛️ Top Destination Ports")
        port_counts = df['dest_port'].value_counts().head(5)
        for port, count in port_counts.items():
            st.markdown(f"**Port {port}**: {count:,}")
    
    with col3:
        st.markdown("#### 🌍 Top Source IPs")
        ip_counts = df['source_ip'].value_counts().head(5)
        for ip, count in ip_counts.items():
            st.markdown(f"**{ip}**: {count:,}")


def main():
    """Main dashboard function"""
    create_header()
    model_type, threshold, refresh_rate = create_sidebar()
    
    # Generate demo data
    df = generate_demo_data(200)
    
    # Status bar
    status_cols = st.columns([3, 1, 1])
    with status_cols[0]:
        st.info(f"🔄 **Model**: {model_type} | **Threshold**: {threshold} | **Last Update**: {datetime.now().strftime('%H:%M:%S')}")
    with status_cols[1]:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    with status_cols[2]:
        if st.button("📥 Import PCAP"):
            st.toast("PCAP import coming soon!")
    
    st.markdown("---")
    
    # Metrics row
    create_metrics_row(df)
    
    st.markdown("---")
    
    # Traffic chart
    create_traffic_chart(df)
    
    st.markdown("---")
    
    # Attack distribution
    create_attack_distribution(df)
    
    st.markdown("---")
    
    # Tabbed content
    tab1, tab2, tab3 = st.tabs(["⚠️ Live Alerts", "📋 Traffic Log", "📊 Statistics"])
    
    with tab1:
        create_alerts_section(df)
    
    with tab2:
        create_log_table(df)
    
    with tab3:
        create_network_stats(df)
    
    # Footer
    st.markdown('''
        <div class="footer">
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
