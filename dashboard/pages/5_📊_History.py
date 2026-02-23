"""
📊 History Page
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

st.set_page_config(page_title="History Analytics", page_icon="📊", layout="wide")
inject_theme()

st.title("📊 Master Analytics")
st.markdown("Historical traffic baselines and macro-level attack trends over extended periods.")

st.markdown(f"""
<style>
    .stat-box {{
        background: {COLORS['bg_tertiary']};
        border-radius: 12px;
        padding: 1.5rem;
        border-left: 4px solid {COLORS['primary']};
    }}
    .stat-label {{ color: {COLORS['text_muted']}; font-size: 0.9rem; margin-bottom: 0.5rem; }}
    .stat-val {{ font-size: 1.5rem; font-weight: bold; margin: 0; }}
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    time_range = st.selectbox("Resolution Window", ["Last 7 Days", "Last 30 Days", "Current Quarter"], label_visibility="collapsed")
with col2:
    st.button("🔄 Sync with Database", use_container_width=True)

st.markdown("---")

np.random.seed(42)
days = 30
hours = days * 24

timestamps = [datetime.now() - timedelta(hours=i) for i in range(hours)][::-1]
traffic_data = np.random.exponential(5000, hours) * (1 + 0.6 * np.sin(np.linspace(0, 4*np.pi, hours)))
attack_data = np.random.poisson(3, hours) * (1 + 0.4 * np.random.rand(hours))

df = pd.DataFrame({
    'timestamp': timestamps,
    'traffic_kb': traffic_data,
    'attacks': attack_data.astype(int),
    'unique_ips': np.random.randint(50, 200, hours),
})
df['date'] = df['timestamp'].dt.date
df['hour'] = df['timestamp'].dt.hour

st.markdown("### 📈 Macro Snapshot")
cols = st.columns(4)
cols[0].metric("Aggregated Traffic", f"{df['traffic_kb'].sum()/1e6:.2f} GB")
cols[1].metric("Total Network Events", f"{df['attacks'].sum():,}")
cols[2].metric("Daily Attack Velocity", f"{df['attacks'].sum()/days:.1f}/day")
cols[3].metric("Bandwidth Peak", f"{df['traffic_kb'].max()/1000:.1f} MB/hr")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 📈 Bandwidth Utilization Trend")
daily_traffic = df.groupby('date')['traffic_kb'].sum().reset_index()
fig = px.area(
    daily_traffic, x='date', y='traffic_kb', 
    color_discrete_sequence=[COLORS['primary']]
)
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    height=300,
    margin=dict(t=10, l=0, r=0, b=0),
    xaxis=dict(gridcolor=COLORS['bg_tertiary'], title=""),
    yaxis=dict(gridcolor=COLORS['bg_tertiary'], title='Traffic (KB)'),
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### ⚠️ Threat Frequency Trend")
daily_attacks = df.groupby('date')['attacks'].sum().reset_index()
fig = px.bar(
    daily_attacks, x='date', y='attacks',
    color_discrete_sequence=[COLORS['danger']]
)
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    height=300,
    margin=dict(t=10, l=0, r=0, b=0),
    xaxis=dict(gridcolor=COLORS['bg_tertiary'], title=""),
    yaxis=dict(gridcolor=COLORS['bg_tertiary'], title="Threats Logged"),
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🕐 Average Diurnal Traffic Wave")
    hourly = df.groupby('hour')['traffic_kb'].mean().reset_index()
    fig = px.line(
        hourly, x='hour', y='traffic_kb', markers=True,
        color_discrete_sequence=[COLORS['success']]
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=250, margin=dict(t=10, l=0, r=0, b=0),
        xaxis_title="Hour of Day", yaxis_title="Average Traffic (KB)",
        xaxis=dict(gridcolor=COLORS['bg_tertiary']), yaxis=dict(gridcolor=COLORS['bg_tertiary'])
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### 🎯 Attack Clustering by Time")
    hourly_attacks = df.groupby('hour')['attacks'].mean().reset_index()
    fig = px.bar(
        hourly_attacks, x='hour', y='attacks',
        color_discrete_sequence=[COLORS['warning']]
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=250, margin=dict(t=10, l=0, r=0, b=0),
        xaxis_title="Hour of Day", yaxis_title="Average Threats",
        xaxis=dict(gridcolor=COLORS['bg_tertiary']), yaxis=dict(gridcolor=COLORS['bg_tertiary'])
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("### 🏆 Extreme Event Highlights")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("<div class='stat-box'>", unsafe_allow_html=True)
    st.markdown("<p style='margin:0 0 1rem 0;font-weight:bold;color:#f8fafc'>Peak Bandwidth Days</p>", unsafe_allow_html=True)
    top_traffic = df.groupby('date')['traffic_kb'].sum().nlargest(3)
    for date, val in top_traffic.items():
        st.write(f"📈 {date}: `{val/1000:.1f} MB`")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='stat-box'>", unsafe_allow_html=True)
    st.markdown("<p style='margin:0 0 1rem 0;font-weight:bold;color:#f8fafc'>Highest Threat Intensity</p>", unsafe_allow_html=True)
    top_attacks = df.groupby('date')['attacks'].sum().nlargest(3)
    for date, val in top_attacks.items():
        st.write(f"⚠️ {date}: `{val} alerts`")
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='stat-box'>", unsafe_allow_html=True)
    st.markdown("<p style='margin:0 0 1rem 0;font-weight:bold;color:#f8fafc'>Consistent Bottlenecks</p>", unsafe_allow_html=True)
    busy_hours = df.groupby('hour')['traffic_kb'].mean().nlargest(3)
    for hour, val in busy_hours.items():
        st.write(f"🕐 {hour}:00: `{val:.0f} KB/hr`")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

st.download_button(
    "📥 Download Master Rollup (CSV)",
    df.to_csv(index=False),
    file_name=f"history_rollup_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv",
    type="primary"
)

st.markdown(f"<p style='text-align:center; color:{COLORS['text_muted']};font-size:0.875rem;'>Yhlas Network Analyzer v2.0</p>", unsafe_allow_html=True)
