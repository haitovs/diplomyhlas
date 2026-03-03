"""
⚙️ Settings Page - Functional system configuration
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from dashboard.theme import inject_theme, inject_sidebar_brand, COLORS
from dashboard.components import page_header, init_shared_state, DEFAULT_SETTINGS

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")
inject_theme()
inject_sidebar_brand()
init_shared_state()

page_header("⚙️", "Global Settings", "System configuration")

settings = st.session_state.settings

# ── AI Model Configuration ───────────────────────────────────────────────────
st.markdown(f"""
<div class="settings-section">
    <div class="settings-section-header">
        <span class="ss-icon">🧠</span>
        <span class="ss-title">AI Model Configuration</span>
    </div>
    <div class="settings-section-desc">Configure the inference engine, decision thresholds, and sensitivity.</div>
</div>
""", unsafe_allow_html=True)

model_options = ["LightGBM (Prod)", "XGBoost", "LSTM Autoencoder", "Random Forest"]
current_model = settings.get('model', 'LightGBM (Prod)')
model_index = model_options.index(current_model) if current_model in model_options else 0

sensitivity_options = ["Low (Fewer False Positives)", "Balanced", "High (Catch Everything)"]
current_sens = settings.get('sensitivity', 'Balanced')

col1, col2 = st.columns(2)
with col1:
    model = st.selectbox("Active Inference Engine", model_options, index=model_index)
    threshold = st.slider("Anomaly Confidence Threshold", 0.0, 1.0,
                           settings.get('confidence_threshold', 0.70), 0.05,
                           help="Minimum confidence required to flag a flow as an attack")
with col2:
    sensitivity = st.select_slider("Heuristic Sensitivity", sensitivity_options, current_sens)

# ── Capture Interface Defaults ───────────────────────────────────────────────
st.markdown(f"""
<div class="settings-section">
    <div class="settings-section-header">
        <span class="ss-icon">📡</span>
        <span class="ss-title">Capture Interface Defaults</span>
    </div>
    <div class="settings-section-desc">Network interface and flow timeout parameters for the packet capture engine.</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    default_interface = st.selectbox("Default Listen Interface", ["Auto-Detect", "eth0", "wlan0", "lo", "en0", "lo0"])
    packet_limit = st.number_input("Max Packets Retained in RAM", 1000, 5000000, 100000)
with col2:
    flow_timeout = st.number_input("Idle Flow Timeout (seconds)", 30, 600, 120,
                                   help="Time before an inactive TCP session is considered closed")
    save_captures = st.toggle("Auto-Archive PCAPs to Disk", value=True)

# ── Alert Routing (informational) ───────────────────────────────────────────
st.markdown(f"""
<div class="settings-section">
    <div class="settings-section-header">
        <span class="ss-icon">🔔</span>
        <span class="ss-title">Alert Routing & Notifications</span>
    </div>
    <div class="settings-section-desc">External alert integrations planned for a future release.</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style="padding:1rem 1.25rem; border-radius:4px; background:rgba(245,158,11,0.06);
     border:1px solid rgba(245,158,11,0.12); border-left:3px solid {COLORS['primary']}; color:{COLORS['text_muted']};">
    Email, Slack, and Teams webhook integrations are planned for a future release.
    Currently, all alerts appear in the <strong>Attack Details</strong> page in real time.
</div>
""", unsafe_allow_html=True)

# ── Save / Reset ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
with col2:
    if st.button("Apply & Save", type="primary", use_container_width=True):
        st.session_state.settings['confidence_threshold'] = threshold
        st.session_state.settings['model'] = model
        st.session_state.settings['sensitivity'] = sensitivity
        st.success("Settings saved and applied.")
with col3:
    if st.button("Reset to Defaults", type="secondary", use_container_width=True):
        st.session_state.settings = dict(DEFAULT_SETTINGS)
        st.info("All settings restored to defaults.")
        st.rerun()

# Show current effective settings
st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
st.markdown("### 📋 Current Effective Settings")
eff = st.session_state.settings
st.markdown(f"""
<div style="display:grid; grid-template-columns:repeat(3,1fr); gap:1rem;">
    <div style="background:{COLORS['bg_tertiary']}; border:1px solid rgba(245,158,11,0.10);
         border-left:3px solid {COLORS['primary']}; border-radius:4px; padding:1rem;">
        <div style="color:{COLORS['text_muted']}; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.06em;
             font-family:'Space Grotesk',sans-serif; margin-bottom:0.25rem;">Model</div>
        <div style="font-weight:700; color:{COLORS['text_main']};">{eff.get('model', 'LightGBM (Prod)')}</div>
    </div>
    <div style="background:{COLORS['bg_tertiary']}; border:1px solid rgba(245,158,11,0.10);
         border-left:3px solid {COLORS['primary']}; border-radius:4px; padding:1rem;">
        <div style="color:{COLORS['text_muted']}; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.06em;
             font-family:'Space Grotesk',sans-serif; margin-bottom:0.25rem;">Threshold</div>
        <div style="font-weight:700; font-family:'JetBrains Mono',monospace; color:{COLORS['primary']};">{eff.get('confidence_threshold', 0.70):.2f}</div>
    </div>
    <div style="background:{COLORS['bg_tertiary']}; border:1px solid rgba(245,158,11,0.10);
         border-left:3px solid {COLORS['primary']}; border-radius:4px; padding:1rem;">
        <div style="color:{COLORS['text_muted']}; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.06em;
             font-family:'Space Grotesk',sans-serif; margin-bottom:0.25rem;">Sensitivity</div>
        <div style="font-weight:700; color:{COLORS['text_main']};">{eff.get('sensitivity', 'Balanced')}</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style="text-align:center; margin-top:3rem; padding-top:1.5rem; border-top:1px solid {COLORS['border']};">
    <p style="color:{COLORS['text_muted']}; font-size:0.85rem;">Network Anomaly Analyzer v2.0</p>
</div>
""", unsafe_allow_html=True)
