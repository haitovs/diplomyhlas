"""
📊 History Page - Historical trends and analytics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="History", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0a0f1a 0%, #111827 100%); }
    h1, h2, h3 { color: #f8fafc !important; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Historical Analytics")
st.markdown("View trends and patterns over time")

# Time range selection
col1, col2 = st.columns([3, 1])
with col1:
    time_range = st.selectbox("Time Range", ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Custom"])
with col2:
    if st.button("🔄 Refresh"):
        st.rerun()

st.markdown("---")

# Generate historical data
np.random.seed(42)
days = 30
hours = days * 24

timestamps = [datetime.now() - timedelta(hours=i) for i in range(hours)][::-1]
traffic_data = np.random.exponential(1000, hours) * (1 + 0.5 * np.sin(np.linspace(0, 4*np.pi, hours)))
attack_data = np.random.poisson(2, hours) * (1 + 0.3 * np.random.rand(hours))

df = pd.DataFrame({
    'timestamp': timestamps,
    'traffic_kb': traffic_data,
    'attacks': attack_data.astype(int),
    'unique_ips': np.random.randint(50, 200, hours),
})
df['date'] = df['timestamp'].dt.date
df['hour'] = df['timestamp'].dt.hour

# Summary metrics
st.markdown("### 📈 Summary Statistics")
cols = st.columns(4)
cols[0].metric("Total Traffic", f"{df['traffic_kb'].sum()/1e6:.1f} GB")
cols[1].metric("Total Attacks", f"{df['attacks'].sum():,}")
cols[2].metric("Avg Daily Attacks", f"{df['attacks'].sum()/days:.1f}")
cols[3].metric("Peak Traffic", f"{df['traffic_kb'].max()/1000:.1f} MB/hr")

st.markdown("---")

# Traffic over time
st.markdown("### 📈 Traffic Trend")
daily_traffic = df.groupby('date')['traffic_kb'].sum().reset_index()
fig = px.area(daily_traffic, x='date', y='traffic_kb', 
              color_discrete_sequence=['#6366f1'])
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    height=300,
    xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
    yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title='KB'),
)
st.plotly_chart(fig, width='stretch')

# Attacks over time
st.markdown("### ⚠️ Attack Trend")
daily_attacks = df.groupby('date')['attacks'].sum().reset_index()
fig = px.bar(daily_attacks, x='date', y='attacks',
             color_discrete_sequence=['#ef4444'])
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    height=300,
    xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
    yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
)
st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Hourly patterns
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🕐 Hourly Traffic Pattern")
    hourly = df.groupby('hour')['traffic_kb'].mean().reset_index()
    fig = px.line(hourly, x='hour', y='traffic_kb', markers=True,
                  color_discrete_sequence=['#10b981'])
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=250,
    )
    st.plotly_chart(fig, width='stretch')

with col2:
    st.markdown("### 🎯 Hourly Attack Pattern")
    hourly_attacks = df.groupby('hour')['attacks'].mean().reset_index()
    fig = px.bar(hourly_attacks, x='hour', y='attacks',
                 color_discrete_sequence=['#f59e0b'])
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=250,
    )
    st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Top statistics
st.markdown("### 🏆 Top Statistics")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Peak Traffic Days**")
    top_traffic = df.groupby('date')['traffic_kb'].sum().nlargest(5)
    for date, val in top_traffic.items():
        st.write(f"📅 {date}: {val/1000:.1f} MB")

with col2:
    st.markdown("**Highest Attack Days**")
    top_attacks = df.groupby('date')['attacks'].sum().nlargest(5)
    for date, val in top_attacks.items():
        st.write(f"⚠️ {date}: {val} attacks")

with col3:
    st.markdown("**Busiest Hours**")
    busy_hours = df.groupby('hour')['traffic_kb'].mean().nlargest(5)
    for hour, val in busy_hours.items():
        st.write(f"🕐 {hour}:00 - {val:.0f} KB avg")

# Export
st.markdown("---")
st.download_button(
    "📥 Export Historical Data",
    df.to_csv(index=False),
    file_name=f"history_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)

st.markdown("---")
st.markdown("<p style='text-align:center; color:#64748b;'>Yhlas Network Analyzer v2.0</p>", unsafe_allow_html=True)
