"""
Centralized Theme Configuration
Tactical SOC / War Room aesthetic — dark navy, amber operational accents,
sharp corners, monospace data readouts.
"""

import streamlit as st
from dashboard.i18n import t, get_lang, set_lang, SUPPORTED_LANGS

# Global color palette — Tactical SOC
COLORS = {
    "bg_primary": "#060b14",
    "bg_secondary": "#0c1222",
    "bg_tertiary": "#131d2e",

    "primary": "#f59e0b",       # Amber — SOC operational
    "secondary": "#0ea5e9",     # Blue
    "accent": "#22d3ee",        # Cyan

    "success": "#22c55e",       # Green
    "warning": "#f59e0b",       # Amber
    "danger": "#ef4444",        # Red
    "info": "#0ea5e9",          # Blue

    "text_main": "#e2e8f0",
    "text_muted": "#7c8aa4",

    "border": "rgba(245,158,11,0.12)",
}

# ── Plotly Template ──────────────────────────────────────────────────────────
PLOTLY_TEMPLATE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(
        family="Space Grotesk, Inter, sans-serif",
        color=COLORS["text_main"],
        size=13,
    ),
    title=dict(font=dict(color=COLORS["text_main"], size=16)),
    legend=dict(
        font=dict(color=COLORS["text_muted"], size=12),
        bgcolor="rgba(0,0,0,0)",
        borderwidth=0,
        orientation="h",
        yanchor="bottom",
        y=-0.25,
        xanchor="center",
        x=0.5,
    ),
    xaxis=dict(
        gridcolor="rgba(245,158,11,0.06)",
        zerolinecolor="rgba(245,158,11,0.10)",
        tickfont=dict(color=COLORS["text_muted"]),
        title=dict(font=dict(color=COLORS["text_muted"])),
    ),
    yaxis=dict(
        gridcolor="rgba(245,158,11,0.06)",
        zerolinecolor="rgba(245,158,11,0.10)",
        tickfont=dict(color=COLORS["text_muted"]),
        title=dict(font=dict(color=COLORS["text_muted"])),
    ),
    colorway=[
        COLORS["primary"], COLORS["secondary"], COLORS["success"],
        COLORS["danger"], COLORS["accent"], COLORS["info"],
        "#a78bfa",
    ],
    margin=dict(l=0, r=0, t=30, b=0),
)


def apply_chart_theme(fig):
    """Apply the unified dark theme to any Plotly figure."""
    fig.update_layout(**PLOTLY_TEMPLATE)
    return fig


def inject_theme():
    """Injects core CSS shared across all dashboard pages — Tactical SOC theme."""

    # Load fonts via <link> (non-blocking)
    st.markdown(
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700'
        '&family=JetBrains+Mono:wght@400;500'
        '&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">',
        unsafe_allow_html=True,
    )

    st.markdown("""
    <style>
        /* ── Global Base ─────────────────────────────────── */
        .stApp {
            background: """ + COLORS['bg_primary'] + """;
            background-image:
                linear-gradient(rgba(245,158,11,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(245,158,11,0.03) 1px, transparent 1px);
            background-size: 32px 32px;
            font-family: 'Inter', sans-serif;
            color: """ + COLORS['text_main'] + """;
        }

        /* ── Spacing utilities ─────────────────────────────── */
        .section-gap  { margin-top: 2.5rem; }
        .card-gap     { margin-top: 1.25rem; }
        .section-divider {
            border: none;
            border-top: 1px solid rgba(245,158,11,0.12);
            margin: 0.75rem 0;
        }

        /* ── Column layout ──────────────────────────────────── */
        [data-testid="stHorizontalBlock"] {
            gap: 1rem;
        }

        /* ── Hero Section ────────────────────────────────── */
        .hero-container {
            text-align: center;
            padding: 4rem 2rem 3rem 2rem;
            background: radial-gradient(circle at 50% 50%, rgba(245,158,11,0.06) 0%, transparent 70%);
            border-bottom: 1px solid """ + COLORS['border'] + """;
            margin-bottom: 3rem;
            position: relative;
            overflow: hidden;
        }

        /* Radar rings */
        .hero-container::before {
            content: '';
            position: absolute;
            top: 50%; left: 50%;
            width: 4px; height: 4px;
            border-radius: 50%;
            transform: translate(-50%, -50%);
            box-shadow:
                0 0 0 80px transparent,
                0 0 0 120px rgba(245,158,11,0.04),
                0 0 0 121px transparent,
                0 0 0 180px rgba(245,158,11,0.03),
                0 0 0 181px transparent,
                0 0 0 240px rgba(245,158,11,0.02);
            pointer-events: none;
        }

        .hero-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 3.5rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, """ + COLORS['primary'] + """ 0%, #fbbf24 50%, """ + COLORS['primary'] + """ 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
            position: relative;
        }

        .hero-subtitle {
            font-size: 1.15rem;
            color: """ + COLORS['text_muted'] + """;
            max-width: 600px;
            margin: 0 auto 2rem auto;
            line-height: 1.7;
            position: relative;
        }

        /* ── Typography ────────────────────────────────────── */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Space Grotesk', sans-serif !important;
            color: """ + COLORS['text_main'] + """ !important;
            letter-spacing: -0.01em;
        }

        code, pre {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* ── Tactical Panels ─────────────────────────────── */
        .glass-card, .tactical-panel {
            background: """ + COLORS['bg_tertiary'] + """;
            border: 1px solid rgba(245,158,11,0.10);
            border-top: 2px solid """ + COLORS['primary'] + """;
            border-radius: 4px;
            padding: 1.75rem;
            transition: border-color 0.25s ease, box-shadow 0.25s ease;
        }
        .glass-card:hover, .tactical-panel:hover {
            border-color: rgba(245,158,11,0.25);
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }

        .feature-card {
            background: """ + COLORS['bg_tertiary'] + """;
            border: 1px solid rgba(245,158,11,0.08);
            border-left: 3px solid transparent;
            border-radius: 4px;
            padding: 2rem 1.5rem;
            transition: border-color 0.25s ease, background 0.25s ease, box-shadow 0.25s ease;
            display: flex;
            flex-direction: column;
            min-height: 220px;
            cursor: pointer;
        }

        .feature-card p {
            flex: 1;
            margin-bottom: 1.5rem;
        }

        .feature-card:hover {
            border-left-color: """ + COLORS['primary'] + """;
            background: rgba(245,158,11,0.04);
            box-shadow: 0 4px 20px rgba(0,0,0,0.25);
        }

        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 0.75rem;
            display: inline-block;
        }

        /* ── Metrics — Amber left border ─────────────────── */
        [data-testid="stMetric"] {
            background: """ + COLORS['bg_tertiary'] + """;
            border: 1px solid rgba(245,158,11,0.10);
            border-left: 3px solid """ + COLORS['primary'] + """;
            border-radius: 4px;
            padding: 1.25rem 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            height: 100%;
            transition: border-color 0.25s ease, box-shadow 0.25s ease;
        }

        [data-testid="stMetric"]:hover {
            border-color: rgba(245,158,11,0.25);
            box-shadow: 0 4px 16px rgba(0,0,0,0.25);
        }

        [data-testid="stMetricLabel"] {
            color: """ + COLORS['text_muted'] + """ !important;
            font-size: 0.8rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        [data-testid="stMetricValue"] {
            color: """ + COLORS['primary'] + """ !important;
            font-size: 2rem;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* ── Status Elements ───────────────────────────────── */
        .pulse-container {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            background: rgba(245,158,11,0.08);
            border: 1px solid rgba(245,158,11,0.20);
            border-radius: 4px;
            width: fit-content;
        }

        .pulse-dot {
            width: 8px;
            height: 8px;
            background-color: """ + COLORS['primary'] + """;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(245,158,11,0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(245,158,11,0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(245,158,11,0); }
        }

        .status-indicator {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.85rem;
            font-weight: 600;
        }
        .status-indicator .dot {
            width: 8px; height: 8px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        .status-indicator.danger .dot { background: #ef4444; box-shadow: 0 0 6px #ef4444; }
        .status-indicator.warning .dot { background: #f59e0b; box-shadow: 0 0 6px #f59e0b; }
        .status-indicator.success .dot { background: #22c55e; box-shadow: 0 0 6px #22c55e; }

        /* ── Primary Button ──────────────────────────────── */
        .stButton > button[data-testid="baseButton-primary"] {
            background: linear-gradient(135deg, """ + COLORS['primary'] + """ 0%, #d97706 100%);
            border: none;
            color: #060b14;
            padding: 0.75rem 1.5rem;
            border-radius: 4px;
            font-weight: 700;
            font-family: 'Space Grotesk', sans-serif;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            transition: box-shadow 0.25s ease, filter 0.25s ease;
        }
        .stButton > button[data-testid="baseButton-primary"]:hover {
            box-shadow: 0 4px 20px rgba(245,158,11,0.35);
            filter: brightness(1.1);
        }

        /* Secondary Button */
        .stButton > button[data-testid="baseButton-secondary"] {
            background: transparent;
            border: 1px solid rgba(245,158,11,0.30);
            color: """ + COLORS['primary'] + """;
            border-radius: 4px;
            font-family: 'Space Grotesk', sans-serif;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            transition: border-color 0.25s ease, background 0.25s ease;
        }
        .stButton > button[data-testid="baseButton-secondary"]:hover {
            border-color: """ + COLORS['primary'] + """;
            background: rgba(245,158,11,0.08);
        }

        /* ══════════════════════════════════════════════════════
           SIDEBAR — Fully custom SOC command panel
           ══════════════════════════════════════════════════════ */

        /* Hide default Streamlit nav — we build our own */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }

        /* Sidebar container */
        [data-testid="stSidebar"] {
            background: """ + COLORS['bg_primary'] + """ !important;
            border-right: 1px solid rgba(245,158,11,0.15);
        }
        [data-testid="stSidebar"] > div:first-child {
            background: """ + COLORS['bg_primary'] + """ !important;
            padding-top: 0 !important;
        }

        /* ── Sidebar branding block ──────────────────────── */
        .sidebar-brand {
            text-align: center;
            padding: 1.5rem 1rem 1rem 1rem;
            margin: 0 0 0.25rem 0;
            border-bottom: 1px solid rgba(245,158,11,0.10);
            background: linear-gradient(180deg, rgba(245,158,11,0.04) 0%, transparent 100%);
        }
        .sidebar-brand .brand-icon {
            font-size: 2.25rem;
            margin-bottom: 0.35rem;
        }
        .sidebar-brand .brand-title {
            font-size: 0.85rem;
            font-weight: 700;
            font-family: 'Space Grotesk', sans-serif;
            letter-spacing: 0.02em;
            background: linear-gradient(135deg, """ + COLORS['primary'] + """, #fbbf24);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .sidebar-brand .brand-sub {
            font-size: 0.6rem;
            color: """ + COLORS['text_muted'] + """;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-top: 0.2rem;
        }

        /* ── System status indicator ────────────────────── */
        .sidebar-status {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.4rem;
            margin-top: 0.6rem;
            padding: 0.3rem 0.75rem;
            background: rgba(34,197,94,0.08);
            border: 1px solid rgba(34,197,94,0.15);
            border-radius: 3px;
            display: inline-flex;
        }
        .sidebar-status .status-dot {
            width: 6px; height: 6px;
            background: #22c55e;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        .sidebar-status .status-text {
            font-size: 0.6rem;
            font-weight: 700;
            letter-spacing: 0.10em;
            text-transform: uppercase;
            color: #22c55e;
            font-family: 'JetBrains Mono', monospace;
        }

        /* ── Section labels ─────────────────────────────── */
        .sidebar-section-label {
            font-size: 0.6rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.14em;
            color: rgba(245,158,11,0.45);
            padding: 0.85rem 1rem 0.3rem 1.15rem;
            font-family: 'Space Grotesk', sans-serif;
        }

        /* ── Custom page links (st.page_link) ───────────── */
        [data-testid="stSidebar"] [data-testid="stPageLink-nav"] a,
        [data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] {
            display: flex !important;
            align-items: center !important;
            gap: 0.55rem !important;
            padding: 0.5rem 1rem !important;
            margin: 1px 0.5rem !important;
            border-radius: 3px !important;
            border-left: 3px solid transparent !important;
            color: """ + COLORS['text_muted'] + """ !important;
            font-family: 'Space Grotesk', sans-serif !important;
            font-size: 0.83rem !important;
            font-weight: 500 !important;
            text-decoration: none !important;
            transition: all 0.2s ease !important;
            background: transparent !important;
        }
        [data-testid="stSidebar"] [data-testid="stPageLink-nav"] a:hover,
        [data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover {
            background: rgba(245,158,11,0.06) !important;
            border-left-color: rgba(245,158,11,0.35) !important;
            color: """ + COLORS['text_main'] + """ !important;
        }
        /* Active page link */
        [data-testid="stSidebar"] [data-testid="stPageLink-nav"] a[aria-current="page"],
        [data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"] {
            background: rgba(245,158,11,0.08) !important;
            border-left-color: """ + COLORS['primary'] + """ !important;
            color: """ + COLORS['primary'] + """ !important;
            font-weight: 700 !important;
        }
        /* Page link icon */
        [data-testid="stSidebar"] [data-testid="stPageLink-nav"] a span:first-child,
        [data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] span:first-child {
            font-size: 1rem !important;
            width: 1.25rem;
            text-align: center;
        }

        /* ── Sidebar thin dividers ──────────────────────── */
        .sidebar-divider {
            border: none;
            border-top: 1px solid rgba(245,158,11,0.08);
            margin: 0.5rem 1rem;
        }

        /* ── Sidebar footer ─────────────────────────────── */
        .sidebar-footer {
            text-align: center;
            padding: 0.75rem 1rem;
            font-size: 0.6rem;
            color: """ + COLORS['text_muted'] + """;
            letter-spacing: 0.04em;
            font-family: 'JetBrains Mono', monospace;
            border-top: 1px solid rgba(245,158,11,0.08);
            margin-top: 0.5rem;
        }

        /* ── Sidebar widget styling ──────────────────────── */
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            font-size: 0.75rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.08em !important;
            color: """ + COLORS['text_muted'] + """ !important;
            margin-top: 0.75rem !important;
            margin-bottom: 0.35rem !important;
            padding-left: 0.75rem !important;
        }
        [data-testid="stSidebar"] .stButton > button {
            border-radius: 3px !important;
            font-family: 'Space Grotesk', sans-serif !important;
            font-size: 0.82rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.04em !important;
        }
        [data-testid="stSidebar"] .stSelectbox > div > div {
            border-radius: 3px !important;
            border-color: rgba(245,158,11,0.15) !important;
            background: """ + COLORS['bg_tertiary'] + """ !important;
            font-size: 0.82rem !important;
        }
        [data-testid="stSidebar"] .stSlider > div > div > div {
            color: """ + COLORS['primary'] + """ !important;
        }
        [data-testid="stSidebar"] hr {
            border-color: rgba(245,158,11,0.08) !important;
        }
        /* Sidebar collapse button */
        [data-testid="stSidebar"] button[data-testid="stBaseButton-headerNoPadding"] {
            color: """ + COLORS['text_muted'] + """ !important;
        }

        /* ── Compact language selector in sidebar ────────── */
        .sidebar-lang-wrap {
            padding: 0.35rem 0.75rem;
        }
        .sidebar-lang-label {
            font-size: 0.6rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.10em;
            color: """ + COLORS['text_muted'] + """;
            font-family: 'Space Grotesk', sans-serif;
            margin-bottom: 0.2rem;
            padding-left: 0.25rem;
        }

        /* ── Styled Dataframes ────────────────────────────── */
        [data-testid="stDataFrame"] table {
            border-collapse: separate;
            border-spacing: 0;
        }
        [data-testid="stDataFrame"] thead th {
            background: rgba(245,158,11,0.12) !important;
            color: """ + COLORS['text_main'] + """ !important;
            font-weight: 600 !important;
            font-size: 0.8rem !important;
            font-family: 'Space Grotesk', sans-serif !important;
            text-transform: uppercase !important;
            letter-spacing: 0.04em !important;
            border-bottom: 2px solid rgba(245,158,11,0.25) !important;
        }
        [data-testid="stDataFrame"] tbody tr:hover td {
            background: rgba(245,158,11,0.04) !important;
        }
        [data-testid="stDataFrame"] tbody td {
            border-bottom: 1px solid rgba(245,158,11,0.06) !important;
            font-size: 0.85rem !important;
        }

        /* ── Page header bar ─────────────────────────────── */
        .page-header {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.75rem 1.25rem;
            background: """ + COLORS['bg_tertiary'] + """;
            border: 1px solid rgba(245,158,11,0.10);
            border-left: 3px solid """ + COLORS['primary'] + """;
            border-radius: 2px;
            margin-bottom: 2rem;
        }
        .page-header .ph-icon { font-size: 1.5rem; }
        .page-header .ph-title {
            font-size: 1.1rem;
            font-weight: 700;
            font-family: 'Space Grotesk', sans-serif;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: """ + COLORS['text_main'] + """;
        }
        .page-header .ph-sep { color: rgba(245,158,11,0.30); font-weight: 300; }
        .page-header .ph-sub { color: """ + COLORS['text_muted'] + """; font-size: 0.85rem; }

        /* ── Scrollbar ────────────────────────────────────── */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(245,158,11,0.30); border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: """ + COLORS['primary'] + """; }

        /* ── Hide default chrome ──────────────────────────── */
        #MainMenu {visibility: hidden;}
        header[data-testid="stHeader"] {background: transparent;}

        /* ── Settings sections ────────────────────────────── */
        .settings-section {
            background: """ + COLORS['bg_tertiary'] + """;
            border: 1px solid rgba(245,158,11,0.10);
            border-top: 2px solid """ + COLORS['primary'] + """;
            border-radius: 4px;
            padding: 1.75rem;
            margin-bottom: 1.5rem;
        }
        .settings-section-header {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.5rem;
        }
        .settings-section-header .ss-icon { font-size: 1.5rem; }
        .settings-section-header .ss-title {
            font-size: 1.15rem;
            font-weight: 700;
            font-family: 'Space Grotesk', sans-serif;
            color: """ + COLORS['text_main'] + """;
        }
        .settings-section-desc {
            color: """ + COLORS['text_muted'] + """;
            font-size: 0.85rem;
            margin-bottom: 1.25rem;
        }

        /* ── Severity badges ──────────────────────────────── */
        .sev-badge {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 2px;
            font-weight: 700;
            font-size: 0.75rem;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            font-family: 'Space Grotesk', sans-serif;
        }
        .sev-critical {
            background: rgba(239,68,68,0.18);
            color: #fca5a5;
            border: 1px solid rgba(239,68,68,0.3);
            animation: criticalPulse 2s ease-in-out infinite;
        }
        .sev-high     { background: rgba(245,158,11,0.18); color: #fcd34d; border: 1px solid rgba(245,158,11,0.3); }
        .sev-medium   { background: rgba(14,165,233,0.18); color: #7dd3fc; border: 1px solid rgba(14,165,233,0.3); }
        .sev-low      { background: rgba(34,197,94,0.18); color: #86efac; border: 1px solid rgba(34,197,94,0.3); }

        @keyframes criticalPulse {
            0%, 100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); }
            50% { box-shadow: 0 0 8px 2px rgba(239,68,68,0.3); }
        }
    </style>
    """, unsafe_allow_html=True)


def inject_sidebar_brand():
    """Build fully custom SOC sidebar — branding, navigation, language, footer."""
    with st.sidebar:
        # ── Brand header ────────────────────────────────────
        st.markdown(f"""
        <div class="sidebar-brand">
            <div class="brand-icon">🛡️</div>
            <div class="brand-title">{t('sidebar.brand_title')}</div>
            <div class="brand-sub">{t('sidebar.brand_subtitle')}</div>
            <div style="margin-top:0.6rem; text-align:center;">
                <span class="sidebar-status">
                    <span class="status-dot"></span>
                    <span class="status-text">{t('sidebar.status_online')}</span>
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Operations section ──────────────────────────────
        st.markdown(f'<div class="sidebar-section-label">{t("sidebar.section_operations")}</div>', unsafe_allow_html=True)
        st.page_link("1_🏠_Home.py", label=t("sidebar.nav_home"), icon="🏠")
        st.page_link("pages/2_📡_Live_Monitor.py", label=t("sidebar.nav_live_monitor"), icon="📡")

        # ── Intelligence section ────────────────────────────
        st.markdown(f'<div class="sidebar-section-label">{t("sidebar.section_intelligence")}</div>', unsafe_allow_html=True)
        st.page_link("pages/3_📊_Detection_Report.py", label=t("sidebar.nav_detection_report"), icon="📊")

        # ── Simulation section ─────────────────────────────
        st.markdown(f'<div class="sidebar-section-label">{t("sidebar.section_simulation")}</div>', unsafe_allow_html=True)
        st.page_link("pages/5_💻_Traffic_Simulator.py", label=t("sidebar.nav_traffic_simulator"), icon="💻")
        st.page_link("pages/6_☠️_Attacker_Console.py", label=t("sidebar.nav_attacker_console"), icon="☠️")

        # ── System section ──────────────────────────────────
        st.markdown(f'<div class="sidebar-section-label">{t("sidebar.section_system")}</div>', unsafe_allow_html=True)
        st.page_link("pages/4_📖_How_It_Works.py", label=t("sidebar.nav_how_it_works"), icon="📖")

        # ── Divider + Language ──────────────────────────────
        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-lang-label">🌐 {t("common.language")}</div>', unsafe_allow_html=True)
        lang_codes = list(SUPPORTED_LANGS.keys())
        lang_labels = list(SUPPORTED_LANGS.values())
        current_lang = get_lang()
        current_idx = lang_codes.index(current_lang) if current_lang in lang_codes else 0
        selected_label = st.selectbox(
            t("common.language"),
            lang_labels,
            index=current_idx,
            key="sidebar_lang_select",
            label_visibility="collapsed",
        )
        selected_code = lang_codes[lang_labels.index(selected_label)]
        if selected_code != current_lang:
            set_lang(selected_code)
            st.rerun()

        # ── Footer ──────────────────────────────────────────
        st.markdown(f"""
        <div class="sidebar-footer">
            {t('common.app_version')}<br>
            {t('common.diploma_project')}
        </div>
        """, unsafe_allow_html=True)
