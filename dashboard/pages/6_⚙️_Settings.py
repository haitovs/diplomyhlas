"""
⚙️ Settings Page - Configure analyzer settings
"""

import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from dashboard.theme import inject_theme, COLORS

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")
inject_theme()

st.title("⚙️ Global Settings")
st.markdown("Configure system behaviors, model parameters, and alert routing.")

# --- AI Model Configuration ---
st.markdown("---")
st.markdown(f"### 🧠 AI Model Configuration")
col1, col2 = st.columns(2)

with col1:
    model = st.selectbox("Active Inference Engine", ["LightGBM (Prod)", "XGBoost", "LSTM Autoencoder", "Random Forest"])
    threshold = st.slider("Anomaly Confidence Threshold", 0.0, 1.0, 0.70, 0.05, 
                          help="Minimum confidence required to flag a flow as an attack")

with col2:
    sensitivity = st.select_slider("Heuristic Sensitivity", ["Low (Fewer False Positives)", "Balanced", "High (Catch Everything)"], "Balanced")
    use_ensemble = st.toggle("Enable Ensemble Verification", value=True, help="Cross-check LightGBM results with LSTM before alerting")


# --- Alert Routing ---
st.markdown("---")
st.markdown(f"### 🔔 Alert Routing & Notifications")
col1, col2 = st.columns(2)

with col1:
    enable_sound = st.toggle("Browser Audio Alerts", value=True)
    enable_email = st.toggle("Email Notifications (SMTP)", value=False)
    
    if enable_email:
        email = st.text_input("SOC Distribution List", placeholder="soc-alerts@company.internal")

with col2:
    severity_filter = st.multiselect("Route Alerts for Severity:", ["Critical", "High", "Medium", "Low"], 
                                      default=["Critical", "High"])
    webhook = st.text_input("Slack/Teams Webhook URL", placeholder="https://hooks.slack.com/services/...")


# --- Capture Settings ---
st.markdown("---")
st.markdown(f"### 📡 Capture Interface Defaults")
col1, col2 = st.columns(2)

with col1:
    default_interface = st.selectbox("Default Listen Interface", ["Auto-Detect", "eth0", "wlan0", "lo", "en0"])
    packet_limit = st.number_input("Max Packets Retained in RAM", 1000, 5000000, 100000)

with col2:
    flow_timeout = st.number_input("Idle Flow Timeout (seconds)", 30, 600, 120, help="Time before an inactive TCP session is considered closed")
    save_captures = st.toggle("Auto-Archive PCAPs to Disk", value=True)


# --- Save ---
st.markdown("---")
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    if st.button("Apply & Save", type="primary", use_container_width=True):
        st.success("✅ Configuration synchronized successfully.")

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:{COLORS['text_muted']};font-size:0.875rem;'>Yhlas Network Analyzer v2.0</p>", unsafe_allow_html=True)
