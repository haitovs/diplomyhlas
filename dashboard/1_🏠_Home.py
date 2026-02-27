"""
Network Anomaly Analyzer - Home/Landing Page
Provides a stunning hero visual and entry point to the rest of the application.
"""

import streamlit as st
import sys
from pathlib import Path

_project_root = str(Path(__file__).parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from dashboard.theme import inject_theme, inject_sidebar_brand, COLORS
from dashboard.components import inject_components_css, animated_metric

st.set_page_config(
    page_title="Network Anomaly Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

inject_theme()
inject_components_css()
inject_sidebar_brand()

# ── Hero ─────────────────────────────────────────────────────────────────────
def render_hero():
    st.markdown("""
        <div class="hero-container">
            <div style="display: flex; justify-content: center; margin-bottom: 1rem; position:relative;">
                <div class="pulse-container">
                    <div class="pulse-dot"></div>
                    <span style="font-size: 0.85rem; font-weight: 600; letter-spacing: 0.05em;">SYSTEM ACTIVE</span>
                </div>
            </div>
            <h1 class="hero-title">Network Anomaly Detection</h1>
            <p class="hero-subtitle">
                Advanced machine learning system analyzing network flows in real-time.
                Detects DDoS, Brute Force, Port Scans, and Zero-Day threats with 98% accuracy.
            </p>
        </div>
    """, unsafe_allow_html=True)


# ── Quick Stats (animated metric cards) ──────────────────────────────────────
def render_quick_stats():
    st.markdown("<h3 style='text-align: center; margin-bottom: 2rem;'>System Capabilities</h3>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        animated_metric("Detection Accuracy", "98.2%", delta="LightGBM Engine", delta_color="success", icon="🎯")
    with col2:
        animated_metric("Threats Recognized", "15+", delta="Attack Classes", delta_color="normal", icon="🛡️")
    with col3:
        animated_metric("Inference Speed", "<15ms", delta="Per Batch", delta_color="success", icon="⚡")
    with col4:
        animated_metric("Training Data", "2.8M", delta="Flows (CICIDS2017)", delta_color="normal", icon="📊")


# ── How It Works ─────────────────────────────────────────────────────────────
def render_how_it_works():
    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; margin-bottom: 0.5rem;'>How It Works</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:{COLORS['text_muted']}; margin-bottom:2rem;'>Three-stage pipeline from raw traffic to actionable intelligence</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center; min-height:200px;">
            <div style="font-size:2.5rem; margin-bottom:0.75rem;">📡</div>
            <div style="font-size:1.5rem; font-weight:700; color:{COLORS['primary']}; margin-bottom:0.25rem;">01</div>
            <h4 style="margin:0 0 0.5rem 0;">Data Ingestion</h4>
            <p style="color:{COLORS['text_muted']}; line-height:1.6; font-size:0.9rem;">
                Live packet capture or PCAP upload. Flows are extracted and normalized into 78 CIC-standard features.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center; min-height:200px;">
            <div style="font-size:2.5rem; margin-bottom:0.75rem;">🧠</div>
            <div style="font-size:1.5rem; font-weight:700; color:{COLORS['accent']}; margin-bottom:0.25rem;">02</div>
            <h4 style="margin:0 0 0.5rem 0;">ML Analysis</h4>
            <p style="color:{COLORS['text_muted']}; line-height:1.6; font-size:0.9rem;">
                LightGBM classifier trained on 2.8M CICIDS2017 flows predicts attack type and confidence score.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center; min-height:200px;">
            <div style="font-size:2.5rem; margin-bottom:0.75rem;">📋</div>
            <div style="font-size:1.5rem; font-weight:700; color:{COLORS['success']}; margin-bottom:0.25rem;">03</div>
            <h4 style="margin:0 0 0.5rem 0;">Threat Report</h4>
            <p style="color:{COLORS['text_muted']}; line-height:1.6; font-size:0.9rem;">
                Visual dashboards, severity-ranked alerts, forensic drill-downs, and exportable CSV/JSON reports.
            </p>
        </div>
        """, unsafe_allow_html=True)


# ── Technology Badges ────────────────────────────────────────────────────────
def render_tech_badges():
    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    techs = [
        ("LightGBM", COLORS['success']),
        ("CICIDS2017", COLORS['info']),
        ("Streamlit", COLORS['danger']),
        ("Plotly", COLORS['secondary']),
        ("Scikit-Learn", COLORS['warning']),
        ("Pandas", COLORS['accent']),
    ]

    badges_html = " ".join(
        f'<span style="display:inline-block; padding:6px 16px; border-radius:20px; '
        f'background:{c}15; border:1px solid {c}30; color:{c}; font-size:0.8rem; '
        f'font-weight:600; letter-spacing:0.03em;">{name}</span>'
        for name, c in techs
    )
    st.markdown(
        f'<div style="text-align:center; display:flex; flex-wrap:wrap; gap:0.5rem; justify-content:center;">{badges_html}</div>',
        unsafe_allow_html=True,
    )


# ── Feature Cards (navigation tiles) ────────────────────────────────────────
def render_features():
    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; margin: 0 0 2rem 0;'>Core Modules</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">📡</div>
                <h3 style="margin-top:0;">Live Monitoring</h3>
                <p style="color: {COLORS['text_muted']}; line-height: 1.6;">
                    Stream and analyze network traffic in real-time with interactive attack simulation controls.
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Live Monitor", key="btn_live", type="primary", use_container_width=True):
            st.switch_page("pages/2_📡_Live_Monitor.py")

    with col2:
        st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">📁</div>
                <h3 style="margin-top:0;">PCAP Analysis</h3>
                <p style="color: {COLORS['text_muted']}; line-height: 1.6;">
                    Upload packet capture files for deep forensic analysis, protocol breakdown, and CSV export.
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Upload Dataset", key="btn_pcap", type="secondary", use_container_width=True):
            st.switch_page("pages/3_📁_PCAP_Analysis.py")

    with col3:
        st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">🧠</div>
                <h3 style="margin-top:0;">Model Intelligence</h3>
                <p style="color: {COLORS['text_muted']}; line-height: 1.6;">
                    Explore how the LightGBM classifier makes decisions via feature importance and trend analytics.
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("View AI Metrics", key="btn_model", type="secondary", use_container_width=True):
            st.switch_page("pages/5_📊_History.py")


# ── Footer ───────────────────────────────────────────────────────────────────
def render_footer():
    st.markdown(f"""
        <div style="text-align: center; margin-top: 4rem; padding-top: 2rem; border-top: 1px solid {COLORS['border']};">
            <p style="color: {COLORS['text_muted']}; font-size: 0.85rem;">
                <strong>Network Anomaly Analyzer v2.0</strong> &nbsp;·&nbsp; Diploma Project 2025
            </p>
        </div>
    """, unsafe_allow_html=True)


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    render_hero()
    render_quick_stats()
    render_how_it_works()
    render_tech_badges()
    render_features()
    render_footer()


if __name__ == "__main__":
    main()
