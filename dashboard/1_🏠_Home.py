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
from dashboard.components import inject_components_css, animated_metric, init_shared_state
from dashboard.i18n import t

st.set_page_config(
    page_title="Network Anomaly Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

inject_theme()
inject_components_css()
inject_sidebar_brand()
init_shared_state()

# ── Hero ─────────────────────────────────────────────────────────────────────
def render_hero():
    st.markdown(f"""
        <div class="hero-container">
            <div style="display: flex; justify-content: center; margin-bottom: 1rem; position:relative;">
                <div class="pulse-container">
                    <div class="pulse-dot"></div>
                    <span style="font-size: 0.85rem; font-weight: 700; letter-spacing: 0.08em; text-transform:uppercase; font-family:'Space Grotesk',sans-serif;">{t('home.system_active')}</span>
                </div>
            </div>
            <h1 class="hero-title">{t('home.hero_title')}</h1>
            <p class="hero-subtitle">
                {t('home.hero_subtitle')}
            </p>
        </div>
    """, unsafe_allow_html=True)


# ── Quick Stats (animated metric cards) ──────────────────────────────────────
def render_quick_stats():
    st.markdown(f"<h3 style='text-align: center; margin-bottom: 2rem; font-family: Space Grotesk, sans-serif;'>{t('home.capabilities_title')}</h3>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        animated_metric(t('home.accuracy_label'), t('home.accuracy_value'), delta=t('home.accuracy_delta'), delta_color="success", icon="🎯")
    with col2:
        animated_metric(t('home.threats_label'), t('home.threats_value'), delta=t('home.threats_delta'), delta_color="normal", icon="🛡️")
    with col3:
        animated_metric(t('home.speed_label'), t('home.speed_value'), delta=t('home.speed_delta'), delta_color="success", icon="⚡")
    with col4:
        animated_metric(t('home.training_label'), t('home.training_value'), delta=t('home.training_delta'), delta_color="normal", icon="📊")


# ── How It Works ─────────────────────────────────────────────────────────────
def render_how_it_works():
    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; margin-bottom: 0.5rem; font-family: Space Grotesk, sans-serif;'>{t('home.how_it_works_title')}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:{COLORS['text_muted']}; margin-bottom:2rem;'>{t('home.how_it_works_subtitle')}</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center; min-height:200px;">
            <div style="font-size:2.5rem; margin-bottom:0.75rem;">📡</div>
            <div style="font-size:1.5rem; font-weight:700; color:{COLORS['primary']}; margin-bottom:0.25rem;">{t('home.step1_number')}</div>
            <h4 style="margin:0 0 0.5rem 0;">{t('home.step1_title')}</h4>
            <p style="color:{COLORS['text_muted']}; line-height:1.6; font-size:0.9rem;">
                {t('home.step1_desc')}
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center; min-height:200px;">
            <div style="font-size:2.5rem; margin-bottom:0.75rem;">🧠</div>
            <div style="font-size:1.5rem; font-weight:700; color:{COLORS['secondary']}; margin-bottom:0.25rem;">{t('home.step2_number')}</div>
            <h4 style="margin:0 0 0.5rem 0;">{t('home.step2_title')}</h4>
            <p style="color:{COLORS['text_muted']}; line-height:1.6; font-size:0.9rem;">
                {t('home.step2_desc')}
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center; min-height:200px;">
            <div style="font-size:2.5rem; margin-bottom:0.75rem;">📋</div>
            <div style="font-size:1.5rem; font-weight:700; color:{COLORS['success']}; margin-bottom:0.25rem;">{t('home.step3_number')}</div>
            <h4 style="margin:0 0 0.5rem 0;">{t('home.step3_title')}</h4>
            <p style="color:{COLORS['text_muted']}; line-height:1.6; font-size:0.9rem;">
                {t('home.step3_desc')}
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
        f'<span style="display:inline-block; padding:6px 16px; border-radius:2px; '
        f'background:{c}15; border:1px solid {c}30; color:{c}; font-size:0.8rem; '
        f'font-weight:700; letter-spacing:0.04em; text-transform:uppercase; '
        f'font-family:Space Grotesk,sans-serif;">{name}</span>'
        for name, c in techs
    )
    st.markdown(
        f'<div style="text-align:center; display:flex; flex-wrap:wrap; gap:0.5rem; justify-content:center;">{badges_html}</div>',
        unsafe_allow_html=True,
    )


# ── Feature Cards (navigation tiles) ────────────────────────────────────────
def render_features():
    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; margin: 0 0 2rem 0; font-family: Space Grotesk, sans-serif;'>{t('home.core_modules_title')}</h3>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">📡</div>
                <h3 style="margin-top:0;">{t('home.live_monitor_title')}</h3>
                <p style="color: {COLORS['text_muted']}; line-height: 1.6;">
                    {t('home.live_monitor_desc')}
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button(t('home.live_monitor_btn'), key="btn_live", type="primary", use_container_width=True):
            st.switch_page("pages/2_📡_Live_Monitor.py")

    with col2:
        st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">📁</div>
                <h3 style="margin-top:0;">{t('home.pcap_title')}</h3>
                <p style="color: {COLORS['text_muted']}; line-height: 1.6;">
                    {t('home.pcap_desc')}
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button(t('home.pcap_btn'), key="btn_pcap", type="secondary", use_container_width=True):
            st.switch_page("pages/3_📁_PCAP_Analysis.py")

    with col3:
        st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">🧠</div>
                <h3 style="margin-top:0;">{t('home.model_intel_title')}</h3>
                <p style="color: {COLORS['text_muted']}; line-height: 1.6;">
                    {t('home.model_intel_desc')}
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button(t('home.model_intel_btn'), key="btn_model", type="secondary", use_container_width=True):
            st.switch_page("pages/5_📊_History.py")

    with col4:
        st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">📖</div>
                <h3 style="margin-top:0;">{t('home.docs_title')}</h3>
                <p style="color: {COLORS['text_muted']}; line-height: 1.6;">
                    {t('home.docs_desc')}
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button(t('home.docs_btn'), key="btn_docs", type="secondary", use_container_width=True):
            st.switch_page("pages/7_📖_How_It_Works.py")


# ── Footer ───────────────────────────────────────────────────────────────────
def render_footer():
    st.markdown(f"""
        <div style="text-align: center; margin-top: 4rem; padding-top: 2rem; border-top: 1px solid {COLORS['border']};">
            <p style="color: {COLORS['text_muted']}; font-size: 0.85rem;">
                <strong>{t('common.app_version')}</strong> &nbsp;·&nbsp; {t('common.diploma_project')}
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
