"""
Network Anomaly Analyzer - Home/Landing Page
Provides a stunning hero visual and entry point to the rest of the application.
"""

import streamlit as st
import pandas as pd
import time
import sys
from pathlib import Path

# Ensure project root is on sys.path so 'dashboard' and 'src' packages resolve
_project_root = str(Path(__file__).parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from dashboard.theme import inject_theme, COLORS

# Page configuration MUST be the first Streamlit command
st.set_page_config(
    page_title="Network Anomaly Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject custom CSS
inject_theme()

def render_hero():
    """Renders the top hero section"""
    st.markdown("""
        <div class="hero-container">
            <div style="display: flex; justify-content: center; margin-bottom: 1rem;">
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

def render_quick_stats():
    """Renders animated statistics"""
    st.markdown("<h3 style='text-align: center; margin-bottom: 2rem;'>System Capabilities</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="DETECTION ACCURACY", value="98.2%", delta="LightGBM Engine")
    with col2:
        st.metric(label="THREATS RECOGNIZED", value="15+", delta="Attack Classes")
    with col3:
        st.metric(label="INFERENCE SPEED", value="<15ms", delta="Per Batch", delta_color="inverse")
    with col4:
        st.metric(label="TRAINING DATA", value="2.8M", delta="Flows (CICIDS2017)")

def render_features():
    """Renders the main feature cards with navigation logic"""
    st.markdown("<h3 style='text-align: center; margin: 3rem 0 2rem 0;'>Core Modules</h3>", unsafe_allow_html=True)
    
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

def render_footer():
    """Renders clean footer"""
    st.markdown(f"""
        <div style="text-align: center; margin-top: 5rem; padding-top: 2rem; border-top: 1px solid {COLORS['border']};">
            <p style="color: {COLORS['text_muted']}; font-size: 0.9rem;">
                <strong>Network Anomaly Analyzer v2.0</strong> • Diploma Project 2025
            </p>
        </div>
    """, unsafe_allow_html=True)

def main():
    render_hero()
    render_quick_stats()
    render_features()
    render_footer()

if __name__ == "__main__":
    main()
