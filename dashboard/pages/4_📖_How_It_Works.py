"""
📖 How It Works - Comprehensive documentation page
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from dashboard.theme import inject_theme, inject_sidebar_brand, COLORS
from dashboard.components import page_header, init_shared_state
from dashboard.i18n import t

st.set_page_config(page_title="How It Works", page_icon="📖", layout="wide")
inject_theme()
inject_sidebar_brand()
init_shared_state()

page_header("📖", t('how_it_works.page_title'), t('how_it_works.page_subtitle'))

tabs = st.tabs([
    t('how_it_works.tab_what_is_nad'),
    t('how_it_works.tab_cicids2017'),
    t('how_it_works.tab_ml_models'),
    t('how_it_works.tab_feature_engineering'),
    t('how_it_works.tab_architecture'),
    t('how_it_works.tab_attack_types'),
    t('how_it_works.tab_glossary'),
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: What Is Network Anomaly Detection
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown(f"## {t('how_it_works.nad_title')}")
    st.markdown(f"""
    {t('how_it_works.nad_intro')}

    ### {t('how_it_works.nad_why_title')}
    - {t('how_it_works.nad_why_volume')}
    - {t('how_it_works.nad_why_speed')}
    - {t('how_it_works.nad_why_sophistication')}

    ### {t('how_it_works.nad_ids_vs_ips')}
    | Feature | {t('how_it_works.nad_ids_header')} | {t('how_it_works.nad_ips_header')} |
    |---------|---------------------------|----------------------------|
    | Action | {t('how_it_works.nad_ids_action')} | {t('how_it_works.nad_ips_action')} |
    | Placement | {t('how_it_works.nad_ids_placement')} | {t('how_it_works.nad_ips_placement')} |
    | Latency | {t('how_it_works.nad_ids_latency')} | {t('how_it_works.nad_ips_latency')} |
    | Risk | {t('how_it_works.nad_ids_risk')} | {t('how_it_works.nad_ips_risk')} |

    {t('how_it_works.nad_system_note')}

    ### {t('how_it_works.nad_approaches_title')}
    - {t('how_it_works.nad_signature_desc')}
    - {t('how_it_works.nad_anomaly_desc')}
    """)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: The CICIDS2017 Dataset
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown(f"## {t('how_it_works.cicids_title')}")
    st.markdown(f"""
    {t('how_it_works.cicids_intro')}

    ### {t('how_it_works.cicids_key_facts')}
    - {t('how_it_works.cicids_created')}
    - {t('how_it_works.cicids_total_flows')}
    - {t('how_it_works.cicids_features')}
    - {t('how_it_works.cicids_protocols')}

    ### {t('how_it_works.cicids_breakdown_title')}

    | Day | Date | Activity |
    |-----|------|----------|
    | Monday | July 3 | {t('how_it_works.cicids_monday')} |
    | Tuesday | July 4 | {t('how_it_works.cicids_tuesday')} |
    | Wednesday | July 5 | {t('how_it_works.cicids_wednesday')} |
    | Thursday | July 6 | {t('how_it_works.cicids_thursday')} |
    | Friday | July 7 | {t('how_it_works.cicids_friday')} |

    ### {t('how_it_works.cicids_classes_title')}
    {t('how_it_works.cicids_classes_intro')}

    1. {t('how_it_works.cicids_class_benign')}
    2. {t('how_it_works.cicids_class_bot')}
    3. {t('how_it_works.cicids_class_ddos')}
    4. {t('how_it_works.cicids_class_dos_hulk')}
    5. {t('how_it_works.cicids_class_ftp')}
    6. {t('how_it_works.cicids_class_portscan')}
    7. {t('how_it_works.cicids_class_ssh')}
    """)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3: Machine Learning Models
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown(f"## {t('how_it_works.ml_title')}")

    st.markdown(f"### {t('how_it_works.ml_lightgbm_title')}")
    st.markdown(f"""
    {t('how_it_works.ml_lightgbm_desc')}

    {t('how_it_works.ml_lightgbm_how')}
    - {t('how_it_works.ml_lightgbm_how_1')}
    - {t('how_it_works.ml_lightgbm_how_2')}
    - {t('how_it_works.ml_lightgbm_how_3')}

    {t('how_it_works.ml_lightgbm_why')}
    - {t('how_it_works.ml_lightgbm_why_1')}
    - {t('how_it_works.ml_lightgbm_why_2')}
    - {t('how_it_works.ml_lightgbm_why_3')}
    - {t('how_it_works.ml_lightgbm_why_4')}

    {t('how_it_works.ml_lightgbm_params')}
    - {t('how_it_works.ml_lightgbm_params_1')}
    - {t('how_it_works.ml_lightgbm_params_2')}
    """)

    st.markdown("---")
    st.markdown(f"### {t('how_it_works.ml_rf_title')}")
    st.markdown(f"""
    {t('how_it_works.ml_rf_desc')}

    {t('how_it_works.ml_rf_how')}
    - {t('how_it_works.ml_rf_how_1')}
    - {t('how_it_works.ml_rf_how_2')}
    - {t('how_it_works.ml_rf_how_3')}
    - {t('how_it_works.ml_rf_how_4')}

    {t('how_it_works.ml_rf_pros')}
    {t('how_it_works.ml_rf_cons')}
    """)

    st.markdown("---")
    st.markdown(f"### {t('how_it_works.ml_xgb_title')}")
    st.markdown(f"""
    {t('how_it_works.ml_xgb_desc')}

    {t('how_it_works.ml_xgb_how')}
    - {t('how_it_works.ml_xgb_how_1')}
    - {t('how_it_works.ml_xgb_how_2')}
    - {t('how_it_works.ml_xgb_how_3')}

    {t('how_it_works.ml_xgb_pros')}
    {t('how_it_works.ml_xgb_cons')}
    """)

    st.markdown("---")
    st.markdown(f"### {t('how_it_works.ml_lstm_title')}")
    st.markdown(f"""
    {t('how_it_works.ml_lstm_desc')}

    {t('how_it_works.ml_lstm_how')}
    - {t('how_it_works.ml_lstm_how_1')}
    - {t('how_it_works.ml_lstm_how_2')}
    - {t('how_it_works.ml_lstm_how_3')}
    - {t('how_it_works.ml_lstm_how_4')}

    {t('how_it_works.ml_lstm_arch')}
    - {t('how_it_works.ml_lstm_arch_1')}
    - {t('how_it_works.ml_lstm_arch_2')}
    - {t('how_it_works.ml_lstm_arch_3')}
    - {t('how_it_works.ml_lstm_arch_4')}
    - {t('how_it_works.ml_lstm_arch_5')}

    {t('how_it_works.ml_lstm_pros')}
    {t('how_it_works.ml_lstm_cons')}
    """)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4: Feature Engineering
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown(f"## {t('how_it_works.fe_title')}")

    st.markdown(f"""
    ### {t('how_it_works.fe_what_title')}
    {t('how_it_works.fe_what_desc')}

    - {t('how_it_works.fe_packet_counts')}
    - {t('how_it_works.fe_byte_counts')}
    - {t('how_it_works.fe_timing')}
    - {t('how_it_works.fe_tcp_flags')}
    - {t('how_it_works.fe_statistical')}

    ### {t('how_it_works.fe_pipeline_title')}
    """)

    st.markdown(f"""
    ```
    Raw Packets          Flow Aggregation         Feature Vector (78-dim)
    ┌──────────┐        ┌─────────────────┐      ┌──────────────────────┐
    │ PKT 1    │───┐    │ Group by:       │      │ Flow Duration        │
    │ PKT 2    │───┤    │  src_ip:dst_ip  │      │ Total Fwd Packets    │
    │ PKT 3    │───┼───>│  src_port:dport │─────>│ Total Bwd Packets    │
    │ ...      │───┤    │  protocol       │      │ Fwd Packet Len Mean  │
    │ PKT N    │───┘    │                 │      │ Flow Bytes/s         │
    └──────────┘        └─────────────────┘      │ ... (78 features)    │
                                                  └──────────────────────┘
    ```
    """)

    st.markdown(f"""
    ### {t('how_it_works.fe_scaler_title')}
    {t('how_it_works.fe_scaler_desc')}

    {t('how_it_works.fe_scaler_formula')}

    {t('how_it_works.fe_scaler_explain')}

    ### {t('how_it_works.fe_smote_title')}
    {t('how_it_works.fe_smote_desc')}

    - {t('how_it_works.fe_smote_1')}
    - {t('how_it_works.fe_smote_2')}
    - {t('how_it_works.fe_smote_3')}
    """)

    # Feature importance image
    fi_path = Path(__file__).parent.parent.parent / 'models' / 'feature_importance.png'
    if fi_path.exists():
        st.markdown(f"### {t('how_it_works.fe_importance_title')}")
        st.image(str(fi_path), use_container_width=True)
    else:
        st.info(t('how_it_works.fe_importance_missing'))

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5: System Architecture
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown(f"## {t('how_it_works.arch_title')}")
    st.markdown(f"### {t('how_it_works.arch_pipeline_title')}")

    box_style = "border-radius:4px; padding:0.75rem 1.25rem; text-align:center; min-width:140px;"

    st.markdown(f"""
    <div style="background:{COLORS['bg_tertiary']}; border:1px solid rgba(245,158,11,0.12);
         border-top:2px solid {COLORS['primary']}; border-radius:4px; padding:2rem; margin:1rem 0;">
        <div style="display:flex; align-items:center; justify-content:center; gap:0.5rem; flex-wrap:wrap;">
            <div style="background:{COLORS['primary']}15; border:1px solid {COLORS['primary']}30;
                 {box_style}">
                <div style="font-size:1.5rem;">📡</div>
                <div style="font-weight:700; font-size:0.9rem; font-family:'Space Grotesk',sans-serif;">{t('how_it_works.arch_box_data_source')}</div>
                <div style="color:{COLORS['text_muted']}; font-size:0.75rem;">{t('how_it_works.arch_box_data_source_sub')}</div>
            </div>
            <div style="color:{COLORS['primary']}; font-size:1.5rem;">→</div>
            <div style="background:{COLORS['secondary']}15; border:1px solid {COLORS['secondary']}30;
                 {box_style}">
                <div style="font-size:1.5rem;">🔄</div>
                <div style="font-weight:700; font-size:0.9rem; font-family:'Space Grotesk',sans-serif;">{t('how_it_works.arch_box_feature')}</div>
                <div style="color:{COLORS['text_muted']}; font-size:0.75rem;">{t('how_it_works.arch_box_feature_sub')}</div>
            </div>
            <div style="color:{COLORS['primary']}; font-size:1.5rem;">→</div>
            <div style="background:{COLORS['success']}15; border:1px solid {COLORS['success']}30;
                 {box_style}">
                <div style="font-size:1.5rem;">📏</div>
                <div style="font-weight:700; font-size:0.9rem; font-family:'Space Grotesk',sans-serif;">{t('how_it_works.arch_box_scaler')}</div>
                <div style="color:{COLORS['text_muted']}; font-size:0.75rem;">{t('how_it_works.arch_box_scaler_sub')}</div>
            </div>
            <div style="color:{COLORS['primary']}; font-size:1.5rem;">→</div>
            <div style="background:{COLORS['primary']}15; border:1px solid {COLORS['primary']}30;
                 {box_style}">
                <div style="font-size:1.5rem;">🧠</div>
                <div style="font-weight:700; font-size:0.9rem; font-family:'Space Grotesk',sans-serif;">{t('how_it_works.arch_box_lightgbm')}</div>
                <div style="color:{COLORS['text_muted']}; font-size:0.75rem;">{t('how_it_works.arch_box_lightgbm_sub')}</div>
            </div>
            <div style="color:{COLORS['primary']}; font-size:1.5rem;">→</div>
            <div style="background:{COLORS['danger']}15; border:1px solid {COLORS['danger']}30;
                 {box_style}">
                <div style="font-size:1.5rem;">🎯</div>
                <div style="font-weight:700; font-size:0.9rem; font-family:'Space Grotesk',sans-serif;">{t('how_it_works.arch_box_classify')}</div>
                <div style="color:{COLORS['text_muted']}; font-size:0.75rem;">{t('how_it_works.arch_box_classify_sub')}</div>
            </div>
            <div style="color:{COLORS['primary']}; font-size:1.5rem;">→</div>
            <div style="background:{COLORS['primary']}15; border:1px solid {COLORS['primary']}30;
                 {box_style}">
                <div style="font-size:1.5rem;">📋</div>
                <div style="font-weight:700; font-size:0.9rem; font-family:'Space Grotesk',sans-serif;">{t('how_it_works.arch_box_verdict')}</div>
                <div style="color:{COLORS['text_muted']}; font-size:0.75rem;">{t('how_it_works.arch_box_verdict_sub')}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    ### {t('how_it_works.arch_sources_title')}
    | Source | Description | Use Case |
    |--------|-------------|----------|
    | **{t('how_it_works.arch_source_live')}** | {t('how_it_works.arch_source_live_desc')} | {t('how_it_works.arch_source_live_use')} |

    ### {t('how_it_works.arch_threshold_title')}
    {t('how_it_works.arch_threshold_desc')}

    - {t('how_it_works.arch_threshold_rule')}
    - {t('how_it_works.arch_severity_rule')}
    """)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6: Attack Types Explained
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown(f"## {t('how_it_works.attack_types_title')}")
    st.markdown(t('how_it_works.attack_types_intro'))

    attacks = [
        {'name': t('how_it_works.attack_ddos_name'), 'icon': '🌊', 'description': t('how_it_works.attack_ddos_desc')},
        {'name': t('how_it_works.attack_dos_hulk_name'), 'icon': '💥', 'description': t('how_it_works.attack_dos_hulk_desc')},
        {'name': t('how_it_works.attack_portscan_name'), 'icon': '🔍', 'description': t('how_it_works.attack_portscan_desc')},
        {'name': t('how_it_works.attack_ftp_name'), 'icon': '🔓', 'description': t('how_it_works.attack_ftp_desc')},
        {'name': t('how_it_works.attack_ssh_name'), 'icon': '🔑', 'description': t('how_it_works.attack_ssh_desc')},
        {'name': t('how_it_works.attack_bot_name'), 'icon': '🤖', 'description': t('how_it_works.attack_bot_desc')},
    ]

    for attack in attacks:
        with st.expander(f"{attack['icon']}  {attack['name']}", expanded=False):
            st.markdown(attack['description'])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 7: Glossary
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[6]:
    st.markdown(f"## {t('how_it_works.glossary_title')}")

    glossary = t('how_it_works.glossary')
    glossary_display = [
        ("Network Flow", "network_flow"),
        ("PCAP", "pcap"),
        ("IDS / IPS", "ids_ips"),
        ("CICIDS2017", "cicids2017"),
        ("Gradient Boosting", "gradient_boosting"),
        ("LightGBM", "lightgbm"),
        ("Random Forest", "random_forest"),
        ("XGBoost", "xgboost"),
        ("Autoencoder", "autoencoder"),
        ("LSTM", "lstm"),
        ("SMOTE", "smote"),
        ("StandardScaler", "standard_scaler"),
        ("Feature Importance", "feature_importance"),
        ("F1 Score", "f1_score"),
        ("Precision", "precision"),
        ("Recall", "recall"),
        ("False Positive", "false_positive"),
        ("False Negative", "false_negative"),
        ("Confidence Score", "confidence_score"),
        ("Confidence Threshold", "confidence_threshold"),
        ("Severity Level", "severity_level"),
        ("TCP Flags", "tcp_flags"),
        ("IAT", "iat"),
        ("Scapy", "scapy"),
        ("DDoS", "ddos"),
        ("Brute Force", "brute_force"),
        ("Port Scan", "port_scan"),
        ("Botnet", "botnet"),
        ("C2 (Command and Control)", "c2"),
    ]

    if isinstance(glossary, dict):
        for term, key in glossary_display:
            definition = glossary.get(key, key)
            st.markdown(f"**{term}** -- {definition}")
    else:
        # Fallback if glossary is not a dict (wrong locale structure)
        for term, key in glossary_display:
            st.markdown(f"**{term}** -- {t(f'how_it_works.glossary.{key}')}")

st.markdown(f"""
<div style="text-align:center; margin-top:3rem; padding-top:1.5rem; border-top:1px solid {COLORS['border']};">
    <p style="color:{COLORS['text_muted']}; font-size:0.85rem;">{t('common.app_version')}</p>
</div>
""", unsafe_allow_html=True)
