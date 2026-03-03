"""
📊 History Page - Real session data from Live Monitor, PCAP, and Live Capture
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
from dashboard.components import page_header, init_shared_state
from dashboard.i18n import t

st.set_page_config(page_title="History Analytics", page_icon="📊", layout="wide")
inject_theme()
inject_sidebar_brand()
init_shared_state()

page_header("📊", t('history.page_title'), t('history.page_subtitle'))

# ── Check for data ──────────────────────────────────────────────────────────
detection_log = st.session_state.detection_log
metrics = st.session_state.session_metrics
history_df = st.session_state.get('history_df', pd.DataFrame())

has_detections = len(detection_log) > 0
has_traffic = len(history_df) > 0

if not has_detections and not has_traffic:
    st.markdown(f"""
    <div style="text-align:center; padding:4rem 2rem; margin:2rem 0;
         border:2px dashed rgba(245,158,11,0.20); border-radius:4px;
         background:{COLORS['bg_tertiary']};">
        <div style="font-size:4rem; margin-bottom:1rem;">📊</div>
        <h3 style="margin-bottom:0.5rem; font-family:'Space Grotesk',sans-serif;">{t('history.empty_title')}</h3>
        <p style="color:{COLORS['text_muted']}; max-width:450px; margin:0 auto; line-height:1.7;">
            {t('history.empty_desc')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Session Snapshot ────────────────────────────────────────────────────────
st.markdown(f"### 📈 {t('history.session_snapshot')}")
session_duration = (datetime.now() - metrics['session_start']).total_seconds() / 60

cols = st.columns(4)
cols[0].metric(t('history.total_flows_processed'), f"{metrics['total_flows']:,}")
cols[1].metric(t('history.threats_detected'), f"{metrics['total_threats']:,}")
threat_rate = (metrics['total_threats'] / max(metrics['total_flows'], 1)) * 100
cols[2].metric(t('history.threat_rate'), f"{threat_rate:.1f}%")
cols[3].metric(t('history.session_duration'), f"{session_duration:.0f} {t('history.min_suffix')}")

st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

# ── Source Breakdown ────────────────────────────────────────────────────────
if metrics['by_source']:
    st.markdown(f"### 📡 {t('history.detection_sources')}")
    source_cols = st.columns(len(metrics['by_source']))
    source_colors = {
        'Live Monitor': COLORS['primary'],
        'PCAP Analysis': COLORS['accent'],
        'Live Capture': COLORS['success'],
    }
    for i, (source, count) in enumerate(metrics['by_source'].items()):
        with source_cols[i]:
            color = source_colors.get(source, COLORS['info'])
            st.markdown(f"""
            <div style="background:{COLORS['bg_tertiary']}; border:1px solid rgba(245,158,11,0.10);
                 border-radius:4px; padding:1.25rem; border-left:3px solid {color};">
                <div style="color:{COLORS['text_muted']}; font-size:0.8rem; text-transform:uppercase;
                     letter-spacing:0.06em; margin-bottom:0.5rem; font-family:'Space Grotesk',sans-serif;">{source}</div>
                <div style="font-size:1.75rem; font-weight:700; font-family:'JetBrains Mono',monospace;
                     color:{COLORS['primary']};">{count}</div>
                <div style="color:{COLORS['text_muted']}; font-size:0.8rem;">{t('history.threats_detected_label')}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

# ── Detection Timeline ──────────────────────────────────────────────────────
if has_detections:
    det_df = pd.DataFrame(detection_log)
    det_df['timestamp'] = pd.to_datetime(det_df['timestamp'])

    st.markdown(f"### ⚠️ {t('history.detection_timeline')}")
    det_df['minute'] = det_df['timestamp'].dt.floor('1min')
    timeline = det_df.groupby('minute').size().reset_index(name='threats')
    fig = px.bar(timeline, x='minute', y='threats', color_discrete_sequence=[COLORS['danger']])
    apply_chart_theme(fig)
    fig.update_layout(height=300, yaxis_title=t('common.threats'), xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    # ── Threat Type Breakdown ────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### 🎯 {t('history.threat_type_breakdown')}")
        if metrics['by_type']:
            type_df = pd.DataFrame(list(metrics['by_type'].items()), columns=['Type', 'Count'])
            fig = px.pie(type_df, values='Count', names='Type', hole=0.55,
                         color_discrete_sequence=[COLORS['danger'], COLORS['warning'], COLORS['accent'],
                                                  COLORS['primary'], COLORS['success'], COLORS['info']])
            fig.update_traces(textfont=dict(color=COLORS['text_main']))
            apply_chart_theme(fig)
            fig.update_layout(height=320)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f"### 📊 {t('history.severity_distribution')}")
        sev_counts = det_df['severity'].value_counts()
        sev_colors_map = {'Critical': COLORS['danger'], 'High': COLORS['warning'], 'Medium': COLORS['info']}
        fig = go.Figure(data=[go.Pie(
            labels=sev_counts.index,
            values=sev_counts.values,
            hole=0.55,
            marker=dict(colors=[sev_colors_map.get(s, COLORS['text_muted']) for s in sev_counts.index]),
            textfont=dict(color=COLORS['text_main']),
        )])
        apply_chart_theme(fig)
        fig.update_layout(height=320, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

# ── Traffic Volume Timeline (from Live Monitor history_df) ──────────────────
if has_traffic and 'timestamp' in history_df.columns and 'ml_is_anomaly' in history_df.columns:
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown(f"### 📈 {t('history.traffic_volume_timeline')}")

    traffic_df = history_df.copy()
    traffic_df['timestamp'] = pd.to_datetime(traffic_df['timestamp'])
    traffic_df['sec'] = traffic_df['timestamp'].dt.floor('5s')
    vol = traffic_df.groupby('sec').agg(
        total=('ml_is_anomaly', 'count'),
        threats=('ml_is_anomaly', 'sum')
    ).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=vol['sec'], y=vol['total'], name=t('history.chart_total_flows'), fill='tozeroy',
        line=dict(color=COLORS['primary']), fillcolor="rgba(245,158,11,0.12)"
    ))
    fig.add_trace(go.Scatter(
        x=vol['sec'], y=vol['threats'], name=t('history.chart_threats'), fill='tozeroy',
        line=dict(color=COLORS['danger']), fillcolor="rgba(239,68,68,0.15)"
    ))
    apply_chart_theme(fig)
    fig.update_layout(height=300, yaxis_title=t('history.chart_flows_axis'), xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

# ── Export ───────────────────────────────────────────────────────────────────
st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
if has_detections:
    export_df = pd.DataFrame(detection_log)
    st.download_button(
        f"📥 {t('history.export_detections')}",
        export_df.to_csv(index=False),
        file_name=f"session_detections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        type="primary"
    )

st.markdown(f"""
<div style="text-align:center; margin-top:3rem; padding-top:1.5rem; border-top:1px solid {COLORS['border']};">
    <p style="color:{COLORS['text_muted']}; font-size:0.85rem;">{t('common.app_version')}</p>
</div>
""", unsafe_allow_html=True)
