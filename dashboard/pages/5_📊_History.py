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
from dashboard.theme import inject_theme, inject_sidebar_brand, COLORS, apply_chart_theme
from dashboard.components import page_header

st.set_page_config(page_title="History Analytics", page_icon="📊", layout="wide")
inject_theme()
inject_sidebar_brand()

page_header("📊", "Master Analytics", "Historical baselines & macro trends")

col1, col2 = st.columns([3, 1])
with col1:
    time_range = st.selectbox("Resolution Window", ["Last 7 Days", "Last 30 Days", "Current Quarter"], label_visibility="collapsed")
with col2:
    st.button("🔄 Sync with Database", use_container_width=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── Generate historical data ─────────────────────────────────────────────────
np.random.seed(42)
days = 30
hours = days * 24

timestamps = [datetime.now() - timedelta(hours=i) for i in range(hours)][::-1]
traffic_data = np.random.exponential(5000, hours) * (1 + 0.6 * np.sin(np.linspace(0, 4 * np.pi, hours)))
attack_data = np.random.poisson(3, hours) * (1 + 0.4 * np.random.rand(hours))

df = pd.DataFrame({
    'timestamp': timestamps,
    'traffic_kb': traffic_data,
    'attacks': attack_data.astype(int),
    'unique_ips': np.random.randint(50, 200, hours),
})
df['date'] = df['timestamp'].dt.date
df['hour'] = df['timestamp'].dt.hour
df['dow'] = df['timestamp'].dt.dayofweek  # 0=Mon

# ── Macro Snapshot ───────────────────────────────────────────────────────────
st.markdown("### 📈 Macro Snapshot")
cols = st.columns(4)
cols[0].metric("Aggregated Traffic", f"{df['traffic_kb'].sum()/1e6:.2f} GB")
cols[1].metric("Total Network Events", f"{df['attacks'].sum():,}")
cols[2].metric("Daily Attack Velocity", f"{df['attacks'].sum()/days:.1f}/day")
cols[3].metric("Bandwidth Peak", f"{df['traffic_kb'].max()/1000:.1f} MB/hr")

# ── Bandwidth Utilization Trend ──────────────────────────────────────────────
st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
st.markdown("### 📈 Bandwidth Utilization Trend")
daily_traffic = df.groupby('date')['traffic_kb'].sum().reset_index()
fig = px.area(daily_traffic, x='date', y='traffic_kb', color_discrete_sequence=[COLORS['primary']])
apply_chart_theme(fig)
fig.update_layout(height=300, yaxis_title='Traffic (KB)', xaxis_title="")
st.plotly_chart(fig, use_container_width=True)

# ── Threat Frequency Trend ───────────────────────────────────────────────────
st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
st.markdown("### ⚠️ Threat Frequency Trend")
daily_attacks = df.groupby('date')['attacks'].sum().reset_index()
fig = px.bar(daily_attacks, x='date', y='attacks', color_discrete_sequence=[COLORS['danger']])
apply_chart_theme(fig)
fig.update_layout(height=300, yaxis_title="Threats Logged", xaxis_title="")
st.plotly_chart(fig, use_container_width=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── Diurnal & Clustering side-by-side ────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🕐 Average Diurnal Traffic Wave")
    hourly = df.groupby('hour')['traffic_kb'].mean().reset_index()
    fig = px.line(hourly, x='hour', y='traffic_kb', markers=True, color_discrete_sequence=[COLORS['success']])
    apply_chart_theme(fig)
    fig.update_layout(height=280, xaxis_title="Hour of Day", yaxis_title="Avg Traffic (KB)")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### 🎯 Attack Clustering by Time")
    hourly_attacks = df.groupby('hour')['attacks'].mean().reset_index()
    fig = px.bar(hourly_attacks, x='hour', y='attacks', color_discrete_sequence=[COLORS['warning']])
    apply_chart_theme(fig)
    fig.update_layout(height=280, xaxis_title="Hour of Day", yaxis_title="Avg Threats")
    st.plotly_chart(fig, use_container_width=True)

# ── Heatmap: Hour-of-Day x Day-of-Week ──────────────────────────────────────
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("### 🗓️ Attack Heatmap — Hour vs Day of Week")

heatmap_data = df.groupby(['dow', 'hour'])['attacks'].mean().reset_index()
heatmap_pivot = heatmap_data.pivot(index='dow', columns='hour', values='attacks').fillna(0)

day_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
fig = go.Figure(data=go.Heatmap(
    z=heatmap_pivot.values,
    x=[f"{h}:00" for h in heatmap_pivot.columns],
    y=[day_labels[d] for d in heatmap_pivot.index],
    colorscale=[
        [0, "rgba(99,102,241,0.05)"],
        [0.5, "rgba(245,158,11,0.5)"],
        [1, "rgba(239,68,68,0.85)"],
    ],
    hoverongaps=False,
    colorbar=dict(
        title=dict(text="Avg Attacks", font=dict(color=COLORS['text_muted'])),
        tickfont=dict(color=COLORS['text_muted']),
    ),
))
apply_chart_theme(fig)
fig.update_layout(height=280, yaxis=dict(autorange="reversed"))
st.plotly_chart(fig, use_container_width=True)

# ── Extreme Event Highlights (proper Streamlit cards) ────────────────────────
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("### 🏆 Extreme Event Highlights")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="glass-card" style="border-left:4px solid {COLORS['primary']};">
        <div style="font-weight:700; margin-bottom:0.75rem;">Peak Bandwidth Days</div>
    </div>
    """, unsafe_allow_html=True)
    top_traffic = df.groupby('date')['traffic_kb'].sum().nlargest(3)
    for date, val in top_traffic.items():
        st.markdown(f"&nbsp;&nbsp;📈 **{date}**: `{val/1000:.1f} MB`")

with col2:
    st.markdown(f"""
    <div class="glass-card" style="border-left:4px solid {COLORS['warning']};">
        <div style="font-weight:700; margin-bottom:0.75rem;">Highest Threat Intensity</div>
    </div>
    """, unsafe_allow_html=True)
    top_attacks = df.groupby('date')['attacks'].sum().nlargest(3)
    for date, val in top_attacks.items():
        st.markdown(f"&nbsp;&nbsp;⚠️ **{date}**: `{val} alerts`")

with col3:
    st.markdown(f"""
    <div class="glass-card" style="border-left:4px solid {COLORS['accent']};">
        <div style="font-weight:700; margin-bottom:0.75rem;">Consistent Bottlenecks</div>
    </div>
    """, unsafe_allow_html=True)
    busy_hours = df.groupby('hour')['traffic_kb'].mean().nlargest(3)
    for hour, val in busy_hours.items():
        st.markdown(f"&nbsp;&nbsp;🕐 **{hour}:00**: `{val:.0f} KB/hr`")

st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

st.download_button(
    "📥 Download Master Rollup (CSV)",
    df.to_csv(index=False),
    file_name=f"history_rollup_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv",
    type="primary"
)

st.markdown(f"""
<div style="text-align:center; margin-top:3rem; padding-top:1.5rem; border-top:1px solid {COLORS['border']};">
    <p style="color:{COLORS['text_muted']}; font-size:0.85rem;">Network Anomaly Analyzer v2.0</p>
</div>
""", unsafe_allow_html=True)
