"""
⚙️ Settings Page - Functional system configuration
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from dashboard.theme import inject_theme, inject_sidebar_brand, COLORS
from dashboard.components import page_header, init_shared_state, DEFAULT_SETTINGS
from dashboard.i18n import t, get_lang, set_lang, SUPPORTED_LANGS

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")
inject_theme()
inject_sidebar_brand()
init_shared_state()

page_header("⚙️", t('settings.page_title'), t('settings.page_subtitle'))

settings = st.session_state.settings

# ── Language Selection ───────────────────────────────────────────────────────
st.markdown(f"""
<div class="settings-section">
    <div class="settings-section-header">
        <span class="ss-icon">🌐</span>
        <span class="ss-title">{t('common.language')}</span>
    </div>
</div>
""", unsafe_allow_html=True)

lang_codes = list(SUPPORTED_LANGS.keys())
lang_labels = list(SUPPORTED_LANGS.values())
current_lang = get_lang()
current_idx = lang_codes.index(current_lang) if current_lang in lang_codes else 0

selected_lang_label = st.selectbox(
    t('common.language'),
    lang_labels,
    index=current_idx,
    key="settings_lang_select",
    label_visibility="collapsed",
)
selected_lang_code = lang_codes[lang_labels.index(selected_lang_label)]
if selected_lang_code != current_lang:
    set_lang(selected_lang_code)
    st.rerun()

# ── AI Model Configuration ───────────────────────────────────────────────────
st.markdown(f"""
<div class="settings-section">
    <div class="settings-section-header">
        <span class="ss-icon">🧠</span>
        <span class="ss-title">{t('settings.ai_model_config')}</span>
    </div>
    <div class="settings-section-desc">{t('settings.ai_model_config_desc')}</div>
</div>
""", unsafe_allow_html=True)

model_options = [t('settings.model_lightgbm'), t('settings.model_xgboost'), t('settings.model_lstm'), t('settings.model_rf')]
current_model = settings.get('model', t('settings.model_lightgbm'))
model_index = model_options.index(current_model) if current_model in model_options else 0

sensitivity_options = [t('settings.sensitivity_low'), t('settings.sensitivity_balanced'), t('settings.sensitivity_high')]
current_sens = settings.get('sensitivity', t('settings.sensitivity_balanced'))

col1, col2 = st.columns(2)
with col1:
    model = st.selectbox(t('settings.active_engine'), model_options, index=model_index)
    threshold = st.slider(t('settings.confidence_threshold'), 0.0, 1.0,
                           settings.get('confidence_threshold', 0.70), 0.05,
                           help=t('settings.confidence_threshold_help'))
with col2:
    sensitivity = st.select_slider(t('settings.heuristic_sensitivity'), sensitivity_options, current_sens)

# ── Capture Interface Defaults ───────────────────────────────────────────────
st.markdown(f"""
<div class="settings-section">
    <div class="settings-section-header">
        <span class="ss-icon">📡</span>
        <span class="ss-title">{t('settings.capture_defaults')}</span>
    </div>
    <div class="settings-section-desc">{t('settings.capture_defaults_desc')}</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    default_interface = st.selectbox(t('settings.default_interface'), [t('settings.interface_auto'), "eth0", "wlan0", "lo", "en0", "lo0"])
    packet_limit = st.number_input(t('settings.max_packets_ram'), 1000, 5000000, 100000)
with col2:
    flow_timeout = st.number_input(t('settings.flow_timeout'), 30, 600, 120,
                                   help=t('settings.flow_timeout_help'))
    save_captures = st.toggle(t('settings.auto_archive'), value=True)

# ── Alert Routing (informational) ───────────────────────────────────────────
st.markdown(f"""
<div class="settings-section">
    <div class="settings-section-header">
        <span class="ss-icon">🔔</span>
        <span class="ss-title">{t('settings.alert_routing')}</span>
    </div>
    <div class="settings-section-desc">{t('settings.alert_routing_desc')}</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style="padding:1rem 1.25rem; border-radius:4px; background:rgba(245,158,11,0.06);
     border:1px solid rgba(245,158,11,0.12); border-left:3px solid {COLORS['primary']}; color:{COLORS['text_muted']};">
    {t('settings.alert_routing_info')}
</div>
""", unsafe_allow_html=True)

# ── Save / Reset ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
with col2:
    if st.button(t('settings.apply_save'), type="primary", use_container_width=True):
        st.session_state.settings['confidence_threshold'] = threshold
        st.session_state.settings['model'] = model
        st.session_state.settings['sensitivity'] = sensitivity
        st.success(t('settings.settings_saved'))
with col3:
    if st.button(t('settings.reset_defaults'), type="secondary", use_container_width=True):
        st.session_state.settings = dict(DEFAULT_SETTINGS)
        st.info(t('settings.settings_reset'))
        st.rerun()

# Show current effective settings
st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
st.markdown(f"### 📋 {t('settings.current_settings')}")
eff = st.session_state.settings
st.markdown(f"""
<div style="display:grid; grid-template-columns:repeat(3,1fr); gap:1rem;">
    <div style="background:{COLORS['bg_tertiary']}; border:1px solid rgba(245,158,11,0.10);
         border-left:3px solid {COLORS['primary']}; border-radius:4px; padding:1rem;">
        <div style="color:{COLORS['text_muted']}; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.06em;
             font-family:'Space Grotesk',sans-serif; margin-bottom:0.25rem;">{t('settings.label_model')}</div>
        <div style="font-weight:700; color:{COLORS['text_main']};">{eff.get('model', t('settings.model_lightgbm'))}</div>
    </div>
    <div style="background:{COLORS['bg_tertiary']}; border:1px solid rgba(245,158,11,0.10);
         border-left:3px solid {COLORS['primary']}; border-radius:4px; padding:1rem;">
        <div style="color:{COLORS['text_muted']}; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.06em;
             font-family:'Space Grotesk',sans-serif; margin-bottom:0.25rem;">{t('settings.label_threshold')}</div>
        <div style="font-weight:700; font-family:'JetBrains Mono',monospace; color:{COLORS['primary']};">{eff.get('confidence_threshold', 0.70):.2f}</div>
    </div>
    <div style="background:{COLORS['bg_tertiary']}; border:1px solid rgba(245,158,11,0.10);
         border-left:3px solid {COLORS['primary']}; border-radius:4px; padding:1rem;">
        <div style="color:{COLORS['text_muted']}; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.06em;
             font-family:'Space Grotesk',sans-serif; margin-bottom:0.25rem;">{t('settings.label_sensitivity')}</div>
        <div style="font-weight:700; color:{COLORS['text_main']};">{eff.get('sensitivity', 'Balanced')}</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style="text-align:center; margin-top:3rem; padding-top:1.5rem; border-top:1px solid {COLORS['border']};">
    <p style="color:{COLORS['text_muted']}; font-size:0.85rem;">{t('common.app_version')}</p>
</div>
""", unsafe_allow_html=True)
