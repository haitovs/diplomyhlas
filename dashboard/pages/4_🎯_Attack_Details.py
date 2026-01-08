"""
🎯 Attack Analysis Page - Deep dive into detected attacks
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Attack Analysis", page_icon="🎯", layout="wide")

# Theme
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0a0f1a 0%, #111827 100%); }
    h1, h2, h3 { color: #f8fafc !important; }
    .attack-card {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 12px; padding: 1.5rem; margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎯 Attack Analysis")
st.markdown("Deep analysis of detected threats and attack patterns")

# Generate demo attack data
np.random.seed(42)
attack_types = ['DDoS', 'PortScan', 'BruteForce', 'SQLi', 'XSS', 'Botnet']

attacks = []
for i in range(50):
    attacks.append({
        'id': f"ATK-{1000+i}",
        'timestamp': datetime.now() - timedelta(hours=np.random.randint(0, 48)),
        'type': np.random.choice(attack_types),
        'source_ip': f"45.{np.random.randint(0,255)}.{np.random.randint(0,255)}.{np.random.randint(0,255)}",
        'target_ip': f"192.168.1.{np.random.randint(1, 50)}",
        'target_port': np.random.choice([22, 80, 443, 3389, 3306]),
        'packets': np.random.randint(50, 5000),
        'bytes': np.random.randint(10000, 500000),
        'severity': np.random.choice(['Critical', 'High', 'Medium'], p=[0.2, 0.5, 0.3]),
        'confidence': np.random.uniform(0.75, 0.99),
    })

df = pd.DataFrame(attacks)

# Time filter
st.sidebar.markdown("### ⏱️ Time Range")
time_filter = st.sidebar.selectbox("Period", ["Last 24 Hours", "Last 48 Hours", "Last Week"])

# Attack type filter
st.sidebar.markdown("### 🎯 Attack Type")
selected_types = st.sidebar.multiselect("Filter by type", attack_types, default=attack_types)

# Filter data
df = df[df['type'].isin(selected_types)]

# Summary metrics
st.markdown("### 📊 Attack Summary")
cols = st.columns(4)
cols[0].metric("Total Attacks", len(df))
cols[1].metric("Critical", len(df[df['severity'] == 'Critical']))
cols[2].metric("Unique Sources", df['source_ip'].nunique())
cols[3].metric("Avg Confidence", f"{df['confidence'].mean()*100:.1f}%")

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Attack Type Distribution")
    type_counts = df['type'].value_counts()
    colors = ['#ef4444', '#f59e0b', '#eab308', '#10b981', '#06b6d4', '#8b5cf6']
    fig = px.pie(values=type_counts.values, names=type_counts.index, hole=0.5,
                 color_discrete_sequence=colors)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=300)
    st.plotly_chart(fig, width='stretch')

with col2:
    st.markdown("#### Attacks Over Time")
    df['hour'] = df['timestamp'].dt.hour
    hourly = df.groupby('hour').size().reset_index(name='count')
    fig = px.bar(hourly, x='hour', y='count', color_discrete_sequence=['#6366f1'])
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                     height=300, xaxis_title="Hour", yaxis_title="Attacks")
    st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Attack details table
st.markdown("### 📋 Attack Details")
display_df = df[['id', 'timestamp', 'type', 'source_ip', 'target_port', 'severity', 'confidence']].copy()
display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
display_df['confidence'] = (display_df['confidence'] * 100).round(1).astype(str) + '%'

st.dataframe(display_df, width='stretch', hide_index=True)

# Selected attack details
st.markdown("---")
st.markdown("### 🔍 Attack Investigation")
selected_id = st.selectbox("Select attack to investigate", df['id'].tolist())

if selected_id:
    attack = df[df['id'] == selected_id].iloc[0]
    
    cols = st.columns(3)
    with cols[0]:
        st.markdown(f"""
        **Attack ID:** {attack['id']}  
        **Type:** {attack['type']}  
        **Severity:** {attack['severity']}
        """)
    with cols[1]:
        st.markdown(f"""
        **Source:** {attack['source_ip']}  
        **Target:** {attack['target_ip']}:{attack['target_port']}  
        **Time:** {attack['timestamp']}
        """)
    with cols[2]:
        st.markdown(f"""
        **Packets:** {attack['packets']:,}  
        **Bytes:** {attack['bytes']:,}  
        **Confidence:** {attack['confidence']*100:.1f}%
        """)
    
    # Recommendations
    st.markdown("#### 🛡️ Recommended Actions")
    if attack['type'] == 'DDoS':
        st.warning("⚡ Enable rate limiting and consider blocking source IP")
    elif attack['type'] == 'BruteForce':
        st.warning("🔐 Implement account lockout and strong password policy")
    elif attack['type'] == 'PortScan':
        st.info("🔍 Monitor for follow-up attacks from this source")
    else:
        st.info("📋 Review logs and consider firewall rule updates")

st.markdown("---")
st.markdown("<p style='text-align:center; color:#64748b;'>Yhlas Network Analyzer v2.0</p>", unsafe_allow_html=True)
