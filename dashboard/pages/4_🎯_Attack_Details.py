"""
🎯 Attack Analysis Page - Real detections from Live Monitor, PCAP, and Live Capture
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from dashboard.theme import inject_theme, inject_sidebar_brand, COLORS, apply_chart_theme
from dashboard.components import page_header, severity_badge, init_shared_state

st.set_page_config(page_title="Attack Analysis", page_icon="🎯", layout="wide")
inject_theme()
inject_sidebar_brand()
init_shared_state()

page_header("🎯", "Attack Analysis", "Threat forensics & event log")

# ── Build DataFrame from real detection log ─────────────────────────────────
detection_log = st.session_state.detection_log

if not detection_log:
    st.markdown(f"""
    <div style="text-align:center; padding:4rem 2rem; margin:2rem 0;
         border:2px dashed rgba(245,158,11,0.20); border-radius:4px;
         background:{COLORS['bg_tertiary']};">
        <div style="font-size:4rem; margin-bottom:1rem;">🛡️</div>
        <h3 style="margin-bottom:0.5rem; font-family:'Space Grotesk',sans-serif;">No Threats Detected Yet</h3>
        <p style="color:{COLORS['text_muted']}; max-width:450px; margin:0 auto; line-height:1.7;">
            Start the <strong>Live Monitor</strong> with attack simulation or live network capture,
            or upload a <strong>PCAP file</strong> to begin detecting threats.
        </p>
        <div style="display:flex; gap:1rem; justify-content:center; margin-top:1.5rem;">
            <span style="color:{COLORS['text_muted']}; font-size:0.8rem; padding:4px 12px;
                  border:1px solid rgba(245,158,11,0.15); border-radius:2px;">📡 Live Monitor</span>
            <span style="color:{COLORS['text_muted']}; font-size:0.8rem; padding:4px 12px;
                  border:1px solid rgba(245,158,11,0.15); border-radius:2px;">📁 PCAP Analysis</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

df = pd.DataFrame(detection_log)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# ── Sidebar filters ──────────────────────────────────────────────────────────
st.sidebar.markdown("### ⏱️ Data Controls")
attack_types = sorted(df['type'].unique().tolist())
selected_types = st.sidebar.multiselect("Filter by Type", attack_types, default=attack_types)

source_options = sorted(df['source'].unique().tolist())
selected_sources = st.sidebar.multiselect("Filter by Source", source_options, default=source_options)

df = df[df['type'].isin(selected_types) & df['source'].isin(selected_sources)]

# ── Attack Summary metrics ───────────────────────────────────────────────────
st.markdown("### 📊 Attack Summary")
cols = st.columns(4)
cols[0].metric("Total Attacks Logged", len(df))
cr_count = len(df[df['severity'] == 'Critical']) if len(df) > 0 else 0
cols[1].metric("Critical Severity", cr_count)
cols[2].metric("Unique Origins", df['src_ip'].nunique() if len(df) > 0 else 0)
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
    df['minute'] = df['timestamp'].dt.floor('1min')
    minutely = df.groupby('minute').size().reset_index(name='count')
    fig = px.bar(minutely, x='minute', y='count', color_discrete_sequence=[COLORS['primary']])
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

display_df = df[['id', 'timestamp', 'type', 'src_ip', 'dst_port', 'severity', 'confidence', 'source']].copy()
display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
display_df['confidence'] = (display_df['confidence'] * 100).round(1).astype(str) + '%'

table_rows = ""
for _, row in display_df.head(50).iterrows():
    sev_html = severity_badge(row['severity'])
    table_rows += f"""
    <tr>
        <td style="font-family:'JetBrains Mono',monospace; font-size:0.8rem;">{row['id']}</td>
        <td>{row['timestamp']}</td>
        <td><strong>{row['type']}</strong></td>
        <td style="font-family:'JetBrains Mono',monospace; font-size:0.8rem;">{row['src_ip']}</td>
        <td>{row['dst_port']}</td>
        <td>{sev_html}</td>
        <td style="font-family:'JetBrains Mono',monospace;">{row['confidence']}</td>
        <td style="font-size:0.8rem;">{row['source']}</td>
    </tr>"""

th_style = f"padding:10px 12px; text-align:left; color:{COLORS['text_main']}; font-size:0.75rem; font-family:'Space Grotesk',sans-serif; text-transform:uppercase; letter-spacing:0.06em; border-bottom:2px solid rgba(245,158,11,0.25);"

st.markdown(f"""
<div style="overflow-x:auto; border-radius:4px; border:1px solid rgba(245,158,11,0.12);">
<table style="width:100%; border-collapse:collapse; font-size:0.85rem;">
<thead>
    <tr style="background:rgba(245,158,11,0.10);">
        <th style="{th_style}">ID</th>
        <th style="{th_style}">Timestamp</th>
        <th style="{th_style}">Type</th>
        <th style="{th_style}">Source IP</th>
        <th style="{th_style}">Port</th>
        <th style="{th_style}">Severity</th>
        <th style="{th_style}">Confidence</th>
        <th style="{th_style}">Source</th>
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

    label_style = f"color:{COLORS['text_muted']}; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:0.25rem; font-family:'Space Grotesk',sans-serif;"

    st.markdown(f"""
    <div class="tactical-panel" style="border-top:3px solid {sev_color};">
        <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:1.25rem;">
            <h3 style="margin:0; color:{sev_color};">{attack['type']} Detected</h3>
            {severity_badge(attack['severity'])}
        </div>
        <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:1.5rem;">
            <div>
                <div style="{label_style}">Event ID</div>
                <div style="font-weight:700; font-family:'JetBrains Mono',monospace;">{attack['id']}</div>
            </div>
            <div>
                <div style="{label_style}">Source Origin</div>
                <div style="font-weight:700; font-family:'JetBrains Mono',monospace;">{attack['src_ip']}</div>
            </div>
            <div>
                <div style="{label_style}">Target Vector</div>
                <div style="font-weight:700; font-family:'JetBrains Mono',monospace;">{attack['dst_ip']}:{attack['dst_port']}</div>
            </div>
            <div>
                <div style="{label_style}">AI Confidence</div>
                <div style="font-weight:700; font-family:'JetBrains Mono',monospace; color:{COLORS['primary']};">{attack['confidence']*100:.1f}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card-gap"></div>', unsafe_allow_html=True)
    st.markdown("#### 🛡️ Automated Response Suggestion")

    attack_type = attack['type']
    src_ip = attack['src_ip']
    dst_port = attack['dst_port']

    if 'DDoS' in attack_type or 'DoS' in attack_type:
        st.error(f"RECOMMENDATION: Apply aggressive rate limiting. Consider dropping all traffic from {src_ip} at the edge gateway.")
    elif 'Patator' in attack_type or 'BruteForce' in attack_type or 'SSH' in attack_type or 'FTP' in attack_type:
        st.warning(f"RECOMMENDATION: Account lockout thresholds exceeded. Block {src_ip} and enforce MFA for port {dst_port} access.")
    elif 'PortScan' in attack_type:
        st.info(f"RECOMMENDATION: Reconnaissance detected. Add {src_ip} to monitoring watch-list and restrict access.")
    elif 'Bot' in attack_type:
        st.error(f"RECOMMENDATION: Bot activity detected from {src_ip}. Isolate host, scan for malware, and block C2 communication.")
    else:
        st.success("RECOMMENDATION: Logged for analyst review. Monitor for recurring patterns.")

st.markdown(f"""
<div style="text-align:center; margin-top:3rem; padding-top:1.5rem; border-top:1px solid {COLORS['border']};">
    <p style="color:{COLORS['text_muted']}; font-size:0.85rem;">Network Anomaly Analyzer v2.0</p>
</div>
""", unsafe_allow_html=True)
