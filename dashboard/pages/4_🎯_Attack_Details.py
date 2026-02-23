"""
🎯 Attack Analysis Page
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from dashboard.theme import inject_theme, COLORS

st.set_page_config(page_title="Attack Analysis", page_icon="🎯", layout="wide")
inject_theme()

st.title("🎯 Attack Analysis")
st.markdown("Deep analysis of detected threats and historical attack patterns")

st.markdown(f"""
<style>
    .attack-card {{
        background: {COLORS['bg_tertiary']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: transform 0.2s ease;
    }}
    .attack-card:hover {{
        transform: translateY(-2px);
        border-color: {COLORS['accent']};
    }}
</style>
""", unsafe_allow_html=True)

# Generate demo attack data (mocking a database since there's no DB hooked up)
np.random.seed(42)
attack_types = ['DDoS', 'PortScan', 'BruteForce', 'SQLi', 'Botnet']

attacks = []
for i in range(150):
    attacks.append({
        'id': f"ATK-{1000+i}",
        'timestamp': datetime.now() - timedelta(hours=np.random.randint(0, 168)),
        'type': np.random.choice(attack_types),
        'source_ip': f"45.{np.random.randint(0,255)}.{np.random.randint(0,255)}.{np.random.randint(0,255)}",
        'target_ip': f"192.168.1.{np.random.randint(1, 50)}",
        'target_port': np.random.choice([22, 80, 443, 3389, 3306]),
        'packets': np.random.randint(50, 5000),
        'bytes': np.random.randint(10000, 500000),
        'severity': np.random.choice(['Critical', 'High', 'Medium'], p=[0.15, 0.45, 0.4]),
        'confidence': np.random.uniform(0.75, 0.99),
    })

df = pd.DataFrame(attacks)

st.sidebar.markdown("### ⏱️ Data Controls")
time_filter = st.sidebar.selectbox("Period", ["Last 24 Hours", "Last 48 Hours", "Last 7 Days"])
selected_types = st.sidebar.multiselect("Filter by Type", attack_types, default=attack_types)

df = df[df['type'].isin(selected_types)]

st.markdown("### 📊 Attack Summary")
cols = st.columns(4)
cols[0].metric("Total Attacks Logged", len(df))
cr_count = len(df[df['severity'] == 'Critical'])
cols[1].metric("Critical Severity", cr_count)
cols[2].metric("Unique Origins", df['source_ip'].nunique())
cols[3].metric("Avg Model Confidence", f"{df['confidence'].mean()*100:.1f}%")

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Attack Type Vectors")
    type_counts = df['type'].value_counts()
    fig = px.pie(
        values=type_counts.values, names=type_counts.index, hole=0.6,
        color_discrete_sequence=[COLORS['danger'], COLORS['warning'], COLORS['primary'], COLORS['accent'], COLORS['success']]
    )
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=320, showlegend=True, margin=dict(t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### Temporal Distribution")
    df['hour'] = df['timestamp'].dt.floor('1h')
    hourly = df.groupby('hour').size().reset_index(name='count')
    fig = px.bar(hourly, x='hour', y='count', color_discrete_sequence=[COLORS['primary']])
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=320, xaxis_title="Time", yaxis_title="Events", margin=dict(t=0, b=0),
        xaxis=dict(gridcolor=COLORS['bg_tertiary']), yaxis=dict(gridcolor=COLORS['bg_tertiary'])
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("### 📋 Security Event Log")
display_df = df[['id', 'timestamp', 'type', 'source_ip', 'target_port', 'severity', 'confidence']].copy()
display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
display_df['confidence'] = (display_df['confidence'] * 100).round(1).astype(str) + '%'

st.dataframe(display_df, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown("### 🔍 Forensic Investigation Workbench")
selected_id = st.selectbox("Select Attack ID for detailed forensics", df['id'].tolist())

if selected_id:
    attack = df[df['id'] == selected_id].iloc[0]
    
    st.markdown(f"""
        <div class="attack-card">
            <h3 style="margin-top:0; color:{COLORS['danger'] if attack['severity']=='Critical' else COLORS['warning']}">{attack['type']} Detected</h3>
            <div style="display:flex; justify-content:space-between; margin-top:1rem;">
                <div>
                    <p style="color:{COLORS['text_muted']}; margin:0;">Event ID</p>
                    <p><strong>{attack['id']}</strong></p>
                </div>
                <div>
                    <p style="color:{COLORS['text_muted']}; margin:0;">Source Origin</p>
                    <p><strong>{attack['source_ip']}</strong></p>
                </div>
                <div>
                    <p style="color:{COLORS['text_muted']}; margin:0;">Target Vector</p>
                    <p><strong>{attack['target_ip']}:{attack['target_port']}</strong></p>
                </div>
                <div>
                    <p style="color:{COLORS['text_muted']}; margin:0;">AI Confidence</p>
                    <p><strong>{attack['confidence']*100:.1f}%</strong></p>
                </div>
            </div>
            <hr style="border-color:{COLORS['border']}; margin: 1rem 0;" />
            <h4 style="margin:0;">🛡️ Automated Response Suggestion</h4>
    """, unsafe_allow_html=True)
    
    if attack['type'] == 'DDoS':
        st.error(f"SYSTEM RECOMMENDATION: Apply aggressive rate limiting. Consider dropping all traffic from {attack['source_ip']} at the edge edge gateway.")
    elif attack['type'] == 'BruteForce':
        st.warning(f"SYSTEM RECOMMENDATION: Account lockout thresholds exceeded. Block {attack['source_ip']} and enforce MFA for port {attack['target_port']} access.")
    elif attack['type'] == 'PortScan':
        st.info(f"SYSTEM RECOMMENDATION: Reconnaissance detected. Add {attack['source_ip']} to monitoring watch-list.")
    else:
        st.success("SYSTEM RECOMMENDATION: Logged for analyst review.")
        
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:{COLORS['text_muted']};font-size:0.875rem;'>Yhlas Network Analyzer v2.0</p>", unsafe_allow_html=True)
