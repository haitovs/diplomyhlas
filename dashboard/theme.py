"""
Centralized Theme Configuration
Tactical SOC / War Room aesthetic — dark navy, amber operational accents,
sharp corners, monospace data readouts.
"""

import streamlit as st

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

    st.markdown("""
    <style>
        /* Google Fonts — Space Grotesk for headings, Inter for body, JetBrains Mono for data */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700&display=swap');

        /* ── Fix Streamlit sidebar theme derivation warnings ── */
        :root {
            --sidebar-widget-background-color: """ + COLORS['bg_tertiary'] + """;
            --sidebar-widget-border-color: rgba(245,158,11,0.15);
            --sidebar-skeleton-background-color: """ + COLORS['bg_secondary'] + """;
        }
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"],
        [data-testid="stSidebar"] .stSelectbox,
        [data-testid="stSidebar"] .stSlider,
        [data-testid="stSidebar"] .stNumberInput {
            --widget-background-color: """ + COLORS['bg_tertiary'] + """;
            --widget-border-color: rgba(245,158,11,0.15);
        }

        /* ── Global Reset & Base — Tactical grid background ─── */
        .stApp {
            background: """ + COLORS['bg_primary'] + """;
            background-image:
                linear-gradient(rgba(245,158,11,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(245,158,11,0.03) 1px, transparent 1px);
            background-size: 32px 32px;
            font-family: 'Inter', sans-serif;
            color: """ + COLORS['text_main'] + """;
            position: relative;
        }

        /* Scanline overlay */
        .stApp::after {
            content: '';
            position: fixed;
            inset: 0;
            background: repeating-linear-gradient(
                0deg,
                transparent,
                transparent 2px,
                rgba(0,0,0,0.03) 2px,
                rgba(0,0,0,0.03) 4px
            );
            pointer-events: none;
            z-index: 9999;
        }

        /* ── Spacing utilities ─────────────────────────────── */
        .section-gap  { margin-top: 2.5rem; }
        .card-gap     { margin-top: 1.25rem; }
        .section-divider {
            border: none;
            border-top: 1px solid rgba(245,158,11,0.12);
            margin: 2.5rem 0;
        }

        /* ── Hero Section — Radar animation ──────────────────── */
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
            width: 500px; height: 500px;
            transform: translate(-50%, -50%);
            border-radius: 50%;
            background:
                radial-gradient(circle, transparent 30%, transparent 30.5%),
                radial-gradient(circle, transparent 49%, rgba(245,158,11,0.06) 49.5%, rgba(245,158,11,0.06) 50%, transparent 50.5%),
                radial-gradient(circle, transparent 69%, rgba(245,158,11,0.04) 69.5%, rgba(245,158,11,0.04) 70%, transparent 70.5%),
                radial-gradient(circle, transparent 89%, rgba(245,158,11,0.03) 89.5%, rgba(245,158,11,0.03) 90%, transparent 90.5%);
            pointer-events: none;
        }

        /* Radar sweep line */
        .hero-container::after {
            content: '';
            position: absolute;
            top: 50%; left: 50%;
            width: 250px; height: 2px;
            background: linear-gradient(90deg, rgba(245,158,11,0.5), transparent);
            transform-origin: left center;
            animation: radarSweep 4s linear infinite;
            pointer-events: none;
        }

        @keyframes radarSweep {
            0%   { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
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

        /* ── Tactical Panels (replaces glass-card) ───────────── */
        .glass-card, .tactical-panel {
            background: """ + COLORS['bg_tertiary'] + """;
            border: 1px solid rgba(245,158,11,0.10);
            border-top: 2px solid """ + COLORS['primary'] + """;
            border-radius: 4px;
            padding: 1.75rem;
            transition: all 0.25s ease;
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
            transition: all 0.25s ease;
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

        /* Force Streamlit columns to stretch equally */
        [data-testid="stHorizontalBlock"] {
            align-items: stretch;
        }

        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            display: flex;
            flex-direction: column;
        }

        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] > div {
            flex: 1;
            display: flex;
            flex-direction: column;
        }

        /* ── Metrics Redesign — Amber left border ────────────── */
        [data-testid="stMetric"] {
            background: """ + COLORS['bg_tertiary'] + """;
            border: 1px solid rgba(245,158,11,0.10);
            border-left: 3px solid """ + COLORS['primary'] + """;
            border-radius: 4px;
            padding: 1.25rem 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            height: 100%;
            transition: all 0.25s ease;
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

        /* ── Animated status indicator (generic) ──────────── */
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

        /* ── Primary Button Override — Amber gradient ────────── */
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
            transition: all 0.25s ease;
        }

        .stButton > button[data-testid="baseButton-primary"]:hover {
            box-shadow: 0 4px 20px rgba(245,158,11,0.35);
            filter: brightness(1.1);
        }

        /* Secondary Button Override — Amber outlined */
        .stButton > button[data-testid="baseButton-secondary"] {
            background: transparent;
            border: 1px solid rgba(245,158,11,0.30);
            color: """ + COLORS['primary'] + """;
            border-radius: 4px;
            font-family: 'Space Grotesk', sans-serif;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            transition: all 0.25s ease;
        }

        .stButton > button[data-testid="baseButton-secondary"]:hover {
            border-color: """ + COLORS['primary'] + """;
            background: rgba(245,158,11,0.08);
        }

        /* ── Sidebar — Amber right-edge accent line ──────────── */
        [data-testid="stSidebar"] {
            background: """ + COLORS['bg_primary'] + """;
            border-right: 2px solid """ + COLORS['primary'] + """;
        }

        [data-testid="stSidebar"] .sidebar-brand {
            text-align: center;
            padding: 1.5rem 1rem 1rem 1rem;
            border-bottom: 1px solid rgba(245,158,11,0.12);
            margin-bottom: 1rem;
        }
        [data-testid="stSidebar"] .sidebar-brand .brand-icon {
            font-size: 2rem;
            margin-bottom: 0.25rem;
        }
        [data-testid="stSidebar"] .sidebar-brand .brand-title {
            font-size: 1rem;
            font-weight: 700;
            font-family: 'Space Grotesk', sans-serif;
            background: linear-gradient(135deg, """ + COLORS['primary'] + """, #fbbf24);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        [data-testid="stSidebar"] .sidebar-brand .brand-sub {
            font-size: 0.7rem;
            color: """ + COLORS['text_muted'] + """;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        /* ── Styled Dataframes — Amber headers ────────────── */
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

        /* ── Page header bar — Sharp, amber left border ──────── */
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
        .page-header .ph-icon {
            font-size: 1.5rem;
        }
        .page-header .ph-title {
            font-size: 1.1rem;
            font-weight: 700;
            font-family: 'Space Grotesk', sans-serif;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: """ + COLORS['text_main'] + """;
        }
        .page-header .ph-sep {
            color: rgba(245,158,11,0.30);
            font-weight: 300;
        }
        .page-header .ph-sub {
            color: """ + COLORS['text_muted'] + """;
            font-size: 0.85rem;
        }

        /* ── Scrollbar — Amber ────────────────────────────── */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb {
            background: rgba(245,158,11,0.30);
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover { background: """ + COLORS['primary'] + """; }

        /* ── Hide default elements ─────────────────────────── */
        #MainMenu {visibility: hidden;}
        header[data-testid="stHeader"] {background: transparent;}

        /* ── Settings card sections — Sharp, amber top accent ── */
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

        /* ── Severity badges — Sharp, uppercase, critical pulse ── */
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
    """Inject sidebar branding block — call once per page."""
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand">
            <div class="brand-icon">🛡️</div>
            <div class="brand-title">Network Anomaly Analyzer</div>
            <div class="brand-sub">ML-Powered Threat Detection</div>
        </div>
        """, unsafe_allow_html=True)
