"""
⚙️ Settings Page - Configure analyzer settings
"""

import streamlit as st

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0a0f1a 0%, #111827 100%); }
    h1, h2, h3 { color: #f8fafc !important; }
</style>
""", unsafe_allow_html=True)

st.title("⚙️ Settings")

# Model Settings
st.markdown("### 🧠 Model Configuration")
col1, col2 = st.columns(2)

with col1:
    model = st.selectbox("Primary Model", ["XGBoost", "LSTM Autoencoder", "Random Forest"])
    threshold = st.slider("Detection Threshold", 0.0, 1.0, 0.5, 0.05)

with col2:
    sensitivity = st.select_slider("Sensitivity", ["Low", "Medium", "High"], "Medium")
    use_ensemble = st.checkbox("Use Ensemble (multiple models)", value=True)

st.markdown("---")

# Alert Settings
st.markdown("### 🔔 Alert Configuration")
col1, col2 = st.columns(2)

with col1:
    enable_sound = st.checkbox("Enable Sound Alerts", value=True)
    enable_email = st.checkbox("Email Notifications", value=False)

with col2:
    severity_filter = st.multiselect("Alert on severity", ["Critical", "High", "Medium", "Low"], 
                                      default=["Critical", "High"])

if enable_email:
    email = st.text_input("Email Address", placeholder="admin@example.com")

st.markdown("---")

# Capture Settings
st.markdown("### 📡 Capture Settings")
col1, col2 = st.columns(2)

with col1:
    default_interface = st.selectbox("Default Interface", ["Auto", "Wi-Fi", "Ethernet", "eth0"])
    packet_limit = st.number_input("Max Packets per Session", 1000, 1000000, 100000)

with col2:
    flow_timeout = st.number_input("Flow Timeout (seconds)", 30, 600, 120)
    save_captures = st.checkbox("Auto-save Captures", value=False)

st.markdown("---")

# Display Settings
st.markdown("### 🎨 Display Settings")
col1, col2 = st.columns(2)

with col1:
    refresh_rate = st.selectbox("Dashboard Refresh", ["Manual", "5s", "10s", "30s"])
    theme = st.selectbox("Theme", ["Dark (Cybersecurity)", "Light"])

with col2:
    rows_per_page = st.number_input("Rows per Table", 10, 100, 25)
    show_normal = st.checkbox("Show Normal Traffic", value=False)

st.markdown("---")

# Save button
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    if st.button("💾 Save Settings", width='stretch'):
        st.success("✅ Settings saved!")

st.markdown("---")
st.markdown("<p style='text-align:center; color:#64748b;'>Yhlas Network Analyzer v2.0</p>", unsafe_allow_html=True)
