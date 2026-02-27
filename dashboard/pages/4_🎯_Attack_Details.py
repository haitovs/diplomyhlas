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
from dashboard.theme import inject_theme, inject_sidebar_brand, COLORS, apply_chart_theme
from dashboard.components import page_header, severity_badge

st.set_page_config(page_title="Attack Analysis", page_icon="🎯", layout="wide")
inject_theme()
inject_sidebar_brand()

page_header("🎯", "Attack Analysis", "Threat forensics & event log")

# ── Generate demo attack data ────────────────────────────────────────────────
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

# ── Sidebar filters ──────────────────────────────────────────────────────────
st.sidebar.markdown("### ⏱️ Data Controls")
time_filter = st.sidebar.selectbox("Period", ["Last 24 Hours", "Last 48 Hours", "Last 7 Days"])
selected_types = st.sidebar.multiselect("Filter by Type", attack_types, default=attack_types)

df = df[df['type'].isin(selected_types)]

# ── Attack Summary metrics ───────────────────────────────────────────────────
st.markdown("### 📊 Attack Summary")
cols = st.columns(4)
cols[0].metric("Total Attacks Logged", len(df))
cr_count = len(df[df['severity'] == 'Critical']) if len(df) > 0 else 0
cols[1].metric("Critical Severity", cr_count)
cols[2].metric("Unique Origins", df['source_ip'].nunique() if len(df) > 0 else 0)
avg_conf = f"{df['confidence'].mean()*100:.1f}%" if len(df) > 0 else "0.0%"
cols[3].metric("Avg Model Confidence", avg_conf)

st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

# ── Charts row ───────────────────────────────────────────────────────────────
if len(df) == 0:
    st.info("No attacks match the current filters. Adjust the type selection above.")
    st.stop()

col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    st.markdown("#### Attack Type Vectors")
    type_counts = df['type'].value_counts()
    fig = px.pie(
        values=type_counts.values, names=type_counts.index, hole=0.6,
        color_discrete_sequence=[COLORS['danger'], COLORS['warning'], COLORS['primary'], COLORS['accent'], COLORS['success']]
    )
    fig.update_traces(textfont=dict(color=COLORS['text_main']))
    apply_chart_theme(fig)
    fig.update_layout(height=320)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### Temporal Distribution")
    df['hour'] = df['timestamp'].dt.floor('1h')
    hourly = df.groupby('hour').size().reset_index(name='count')
    fig = px.bar(hourly, x='hour', y='count', color_discrete_sequence=[COLORS['primary']])
    apply_chart_theme(fig)
    fig.update_layout(height=320, xaxis_title="Time", yaxis_title="Events")
    st.plotly_chart(fig, use_container_width=True)

with col3:
    st.markdown("#### Severity")
    sev_counts = df['severity'].value_counts()
    sev_colors = {'Critical': COLORS['danger'], 'High': COLORS['warning'], 'Medium': COLORS['info']}
    fig = go.Figure(data=[go.Pie(
        labels=sev_counts.index,
        values=sev_counts.values,
        hole=0.55,
        marker=dict(colors=[sev_colors.get(s, COLORS['text_muted']) for s in sev_counts.index]),
        textfont=dict(color=COLORS['text_main']),
    )])
    apply_chart_theme(fig)
    fig.update_layout(height=320, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

# ── Security Event Log with color-coded severity ────────────────────────────
st.markdown("### 📋 Security Event Log")

display_df = df[['id', 'timestamp', 'type', 'source_ip', 'target_port', 'severity', 'confidence']].copy()
display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
display_df['confidence'] = (display_df['confidence'] * 100).round(1).astype(str) + '%'

# Build HTML table with severity badges
table_rows = ""
for _, row in display_df.head(50).iterrows():
    sev_html = severity_badge(row['severity'])
    table_rows += f"""
    <tr>
        <td style="font-family:'JetBrains Mono',monospace; font-size:0.8rem;">{row['id']}</td>
        <td>{row['timestamp']}</td>
        <td><strong>{row['type']}</strong></td>
        <td style="font-family:'JetBrains Mono',monospace; font-size:0.8rem;">{row['source_ip']}</td>
        <td>{row['target_port']}</td>
        <td>{sev_html}</td>
        <td style="font-family:'JetBrains Mono',monospace;">{row['confidence']}</td>
    </tr>"""

st.markdown(f"""
<div style="overflow-x:auto; border-radius:12px; border:1px solid rgba(99,102,241,0.12);">
<table style="width:100%; border-collapse:collapse; font-size:0.85rem;">
<thead>
    <tr style="background:rgba(99,102,241,0.12);">
        <th style="padding:10px 12px; text-align:left; color:{COLORS['text_main']}; font-size:0.75rem;
            text-transform:uppercase; letter-spacing:0.04em; border-bottom:2px solid rgba(99,102,241,0.25);">ID</th>
        <th style="padding:10px 12px; text-align:left; color:{COLORS['text_main']}; font-size:0.75rem;
            text-transform:uppercase; letter-spacing:0.04em; border-bottom:2px solid rgba(99,102,241,0.25);">Timestamp</th>
        <th style="padding:10px 12px; text-align:left; color:{COLORS['text_main']}; font-size:0.75rem;
            text-transform:uppercase; letter-spacing:0.04em; border-bottom:2px solid rgba(99,102,241,0.25);">Type</th>
        <th style="padding:10px 12px; text-align:left; color:{COLORS['text_main']}; font-size:0.75rem;
            text-transform:uppercase; letter-spacing:0.04em; border-bottom:2px solid rgba(99,102,241,0.25);">Source IP</th>
        <th style="padding:10px 12px; text-align:left; color:{COLORS['text_main']}; font-size:0.75rem;
            text-transform:uppercase; letter-spacing:0.04em; border-bottom:2px solid rgba(99,102,241,0.25);">Port</th>
        <th style="padding:10px 12px; text-align:left; color:{COLORS['text_main']}; font-size:0.75rem;
            text-transform:uppercase; letter-spacing:0.04em; border-bottom:2px solid rgba(99,102,241,0.25);">Severity</th>
        <th style="padding:10px 12px; text-align:left; color:{COLORS['text_main']}; font-size:0.75rem;
            text-transform:uppercase; letter-spacing:0.04em; border-bottom:2px solid rgba(99,102,241,0.25);">Confidence</th>
    </tr>
</thead>
<tbody style="color:{COLORS['text_muted']};">
    {table_rows}
</tbody>
</table>
</div>
""", unsafe_allow_html=True)

# ── Forensic Investigation Workbench ─────────────────────────────────────────
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("### 🔍 Forensic Investigation Workbench")
id_list = df['id'].tolist() if len(df) > 0 else []
selected_id = st.selectbox("Select Attack ID for detailed forensics", id_list) if id_list else None

if selected_id:
    attack = df[df['id'] == selected_id].iloc[0]
    sev_color = COLORS['danger'] if attack['severity'] == 'Critical' else (
        COLORS['warning'] if attack['severity'] == 'High' else COLORS['info']
    )

    st.markdown(f"""
    <div class="glass-card" style="border-top:3px solid {sev_color};">
        <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:1.25rem;">
            <h3 style="margin:0; color:{sev_color};">{attack['type']} Detected</h3>
            {severity_badge(attack['severity'])}
        </div>
        <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:1.5rem;">
            <div>
                <div style="color:{COLORS['text_muted']}; font-size:0.8rem; text-transform:uppercase;
                     letter-spacing:0.04em; margin-bottom:0.25rem;">Event ID</div>
                <div style="font-weight:700; font-family:'JetBrains Mono',monospace;">{attack['id']}</div>
            </div>
            <div>
                <div style="color:{COLORS['text_muted']}; font-size:0.8rem; text-transform:uppercase;
                     letter-spacing:0.04em; margin-bottom:0.25rem;">Source Origin</div>
                <div style="font-weight:700; font-family:'JetBrains Mono',monospace;">{attack['source_ip']}</div>
            </div>
            <div>
                <div style="color:{COLORS['text_muted']}; font-size:0.8rem; text-transform:uppercase;
                     letter-spacing:0.04em; margin-bottom:0.25rem;">Target Vector</div>
                <div style="font-weight:700; font-family:'JetBrains Mono',monospace;">{attack['target_ip']}:{attack['target_port']}</div>
            </div>
            <div>
                <div style="color:{COLORS['text_muted']}; font-size:0.8rem; text-transform:uppercase;
                     letter-spacing:0.04em; margin-bottom:0.25rem;">AI Confidence</div>
                <div style="font-weight:700; font-family:'JetBrains Mono',monospace;">{attack['confidence']*100:.1f}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card-gap"></div>', unsafe_allow_html=True)
    st.markdown("#### 🛡️ Automated Response Suggestion")

    if attack['type'] == 'DDoS':
        st.error(f"RECOMMENDATION: Apply aggressive rate limiting. Consider dropping all traffic from {attack['source_ip']} at the edge gateway.")
    elif attack['type'] == 'BruteForce':
        st.warning(f"RECOMMENDATION: Account lockout thresholds exceeded. Block {attack['source_ip']} and enforce MFA for port {attack['target_port']} access.")
    elif attack['type'] == 'PortScan':
        st.info(f"RECOMMENDATION: Reconnaissance detected. Add {attack['source_ip']} to monitoring watch-list.")
    else:
        st.success("RECOMMENDATION: Logged for analyst review.")

st.markdown(f"""
<div style="text-align:center; margin-top:3rem; padding-top:1.5rem; border-top:1px solid {COLORS['border']};">
    <p style="color:{COLORS['text_muted']}; font-size:0.85rem;">Network Anomaly Analyzer v2.0</p>
</div>
""", unsafe_allow_html=True)
