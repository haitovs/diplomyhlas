"""
Centralized Theme Configuration
Provides modern, professional cybersecurity dark theme for all pages
"""

import streamlit as st

# Global color palette
COLORS = {
    "bg_primary": "#0a0f1a",
    "bg_secondary": "#111827",
    "bg_tertiary": "rgba(30, 41, 59, 0.6)",

    "primary": "#6366f1",      # Indigo
    "secondary": "#8b5cf6",    # Purple
    "accent": "#06b6d4",       # Cyan

    "success": "#10b981",      # Emerald
    "warning": "#f59e0b",      # Amber
    "danger": "#ef4444",       # Red
    "info": "#3b82f6",         # Blue

    "text_main": "#f8fafc",
    "text_muted": "#94a3b8",

    "border": "rgba(99, 102, 241, 0.2)"
}

# ── Plotly Template ──────────────────────────────────────────────────────────
PLOTLY_TEMPLATE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(
        family="Inter, sans-serif",
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
        gridcolor="rgba(148,163,184,0.08)",
        zerolinecolor="rgba(148,163,184,0.12)",
        tickfont=dict(color=COLORS["text_muted"]),
        title=dict(font=dict(color=COLORS["text_muted"])),
    ),
    yaxis=dict(
        gridcolor="rgba(148,163,184,0.08)",
        zerolinecolor="rgba(148,163,184,0.12)",
        tickfont=dict(color=COLORS["text_muted"]),
        title=dict(font=dict(color=COLORS["text_muted"])),
    ),
    colorway=[
        COLORS["primary"], COLORS["accent"], COLORS["success"],
        COLORS["warning"], COLORS["danger"], COLORS["secondary"],
        COLORS["info"],
    ],
    margin=dict(l=0, r=0, t=30, b=0),
)


def apply_chart_theme(fig):
    """Apply the unified dark theme to any Plotly figure."""
    fig.update_layout(**PLOTLY_TEMPLATE)
    return fig


def inject_theme():
    """Injects core CSS shared across all dashboard pages"""

    st.markdown("""
    <style>
        /* Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        /* Global Reset & Base */
        .stApp {
            background: linear-gradient(135deg, """ + COLORS['bg_primary'] + """ 0%, """ + COLORS['bg_secondary'] + """ 100%);
            font-family: 'Inter', sans-serif;
            color: """ + COLORS['text_main'] + """;
        }

        /* ── Spacing utilities ─────────────────────────────── */
        .section-gap  { margin-top: 2.5rem; }
        .card-gap     { margin-top: 1.25rem; }
        .section-divider {
            border: none;
            border-top: 1px solid rgba(99,102,241,0.15);
            margin: 2.5rem 0;
        }

        /* ── Hero Section ──────────────────────────────────── */
        .hero-container {
            text-align: center;
            padding: 4rem 2rem 3rem 2rem;
            background: radial-gradient(circle at 50% 0%, rgba(99, 102, 241, 0.15) 0%, transparent 70%);
            border-bottom: 1px solid """ + COLORS['border'] + """;
            margin-bottom: 3rem;
            position: relative;
            overflow: hidden;
        }

        /* subtle animated grid behind the hero */
        .hero-container::before {
            content: '';
            position: absolute;
            inset: 0;
            background-image:
                linear-gradient(rgba(99,102,241,0.04) 1px, transparent 1px),
                linear-gradient(90deg, rgba(99,102,241,0.04) 1px, transparent 1px);
            background-size: 40px 40px;
            animation: gridScroll 25s linear infinite;
            pointer-events: none;
        }
        @keyframes gridScroll {
            0%   { background-position: 0 0; }
            100% { background-position: 40px 40px; }
        }

        .hero-title {
            font-size: 3.5rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, """ + COLORS['primary'] + """ 0%, """ + COLORS['accent'] + """ 100%);
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
            font-family: 'Inter', sans-serif !important;
            color: """ + COLORS['text_main'] + """ !important;
            letter-spacing: -0.01em;
        }

        code, pre {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* ── Glass-morphism Cards ──────────────────────────── */
        .glass-card {
            background: rgba(30, 41, 59, 0.45);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(99,102,241,0.15);
            border-radius: 16px;
            padding: 1.75rem;
            transition: all 0.3s ease;
        }
        .glass-card:hover {
            border-color: rgba(99,102,241,0.35);
            box-shadow: 0 8px 32px rgba(0,0,0,0.25);
        }

        .feature-card {
            background: rgba(30, 41, 59, 0.45);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid """ + COLORS['border'] + """;
            border-radius: 16px;
            padding: 2rem 1.5rem;
            transition: all 0.3s ease;
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
            transform: translateY(-5px);
            border-color: rgba(99, 102, 241, 0.5);
            box-shadow: 0 10px 40px rgba(99,102,241,0.15), 0 0 0 1px rgba(99,102,241,0.2);
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

        /* ── Metrics Redesign ──────────────────────────────── */
        [data-testid="stMetric"] {
            background: rgba(30, 41, 59, 0.45);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid """ + COLORS['border'] + """;
            border-radius: 16px;
            padding: 1.25rem 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            height: 100%;
            transition: all 0.3s ease;
        }

        [data-testid="stMetric"]:hover {
            border-color: rgba(99,102,241,0.35);
            box-shadow: 0 6px 20px rgba(0,0,0,0.2);
        }

        [data-testid="stMetricLabel"] {
            color: """ + COLORS['text_muted'] + """ !important;
            font-size: 0.8rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        [data-testid="stMetricValue"] {
            color: """ + COLORS['text_main'] + """ !important;
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
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.2);
            border-radius: 20px;
            width: fit-content;
        }

        .pulse-dot {
            width: 8px;
            height: 8px;
            background-color: """ + COLORS['success'] + """;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
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
        .status-indicator.success .dot { background: #10b981; box-shadow: 0 0 6px #10b981; }

        /* ── Primary Button Override ───────────────────────── */
        .stButton > button[data-testid="baseButton-primary"] {
            background: linear-gradient(135deg, """ + COLORS['primary'] + """ 0%, """ + COLORS['accent'] + """ 100%);
            border: none;
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .stButton > button[data-testid="baseButton-primary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4);
        }

        /* Secondary Button Override */
        .stButton > button[data-testid="baseButton-secondary"] {
            background: rgba(30, 41, 59, 0.45);
            backdrop-filter: blur(8px);
            border: 1px solid """ + COLORS['border'] + """;
            color: """ + COLORS['text_main'] + """;
            border-radius: 8px;
            transition: all 0.3s ease;
        }

        .stButton > button[data-testid="baseButton-secondary"]:hover {
            border-color: """ + COLORS['primary'] + """;
            color: """ + COLORS['primary'] + """;
        }

        /* ── Sidebar – Branding ────────────────────────────── */
        [data-testid="stSidebar"] {
            background: rgba(10, 15, 26, 0.97);
            backdrop-filter: blur(16px);
            border-right: 1px solid """ + COLORS['border'] + """;
        }

        [data-testid="stSidebar"] .sidebar-brand {
            text-align: center;
            padding: 1.5rem 1rem 1rem 1rem;
            border-bottom: 1px solid rgba(99,102,241,0.12);
            margin-bottom: 1rem;
        }
        [data-testid="stSidebar"] .sidebar-brand .brand-icon {
            font-size: 2rem;
            margin-bottom: 0.25rem;
        }
        [data-testid="stSidebar"] .sidebar-brand .brand-title {
            font-size: 1rem;
            font-weight: 700;
            background: linear-gradient(135deg, """ + COLORS['primary'] + """, """ + COLORS['accent'] + """);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        [data-testid="stSidebar"] .sidebar-brand .brand-sub {
            font-size: 0.7rem;
            color: """ + COLORS['text_muted'] + """;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        /* ── Styled Dataframes ─────────────────────────────── */
        [data-testid="stDataFrame"] table {
            border-collapse: separate;
            border-spacing: 0;
        }
        [data-testid="stDataFrame"] thead th {
            background: rgba(99,102,241,0.15) !important;
            color: """ + COLORS['text_main'] + """ !important;
            font-weight: 600 !important;
            font-size: 0.8rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.04em !important;
            border-bottom: 2px solid rgba(99,102,241,0.3) !important;
        }
        [data-testid="stDataFrame"] tbody tr:hover td {
            background: rgba(99,102,241,0.06) !important;
        }
        [data-testid="stDataFrame"] tbody td {
            border-bottom: 1px solid rgba(148,163,184,0.06) !important;
            font-size: 0.85rem !important;
        }

        /* ── Page header bar ───────────────────────────────── */
        .page-header {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.75rem 1.25rem;
            background: rgba(30,41,59,0.4);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(99,102,241,0.1);
            border-radius: 12px;
            margin-bottom: 2rem;
        }
        .page-header .ph-icon {
            font-size: 1.5rem;
        }
        .page-header .ph-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: """ + COLORS['text_main'] + """;
        }
        .page-header .ph-sep {
            color: rgba(148,163,184,0.3);
            font-weight: 300;
        }
        .page-header .ph-sub {
            color: """ + COLORS['text_muted'] + """;
            font-size: 0.85rem;
        }

        /* ── Scrollbar ─────────────────────────────────────── */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb {
            background: rgba(99, 102, 241, 0.35);
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover { background: """ + COLORS['primary'] + """; }

        /* ── Hide default elements ─────────────────────────── */
        #MainMenu {visibility: hidden;}
        header[data-testid="stHeader"] {background: transparent;}

        /* ── Settings card sections ────────────────────────── */
        .settings-section {
            background: rgba(30,41,59,0.4);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(99,102,241,0.12);
            border-radius: 16px;
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
            color: """ + COLORS['text_main'] + """;
        }
        .settings-section-desc {
            color: """ + COLORS['text_muted'] + """;
            font-size: 0.85rem;
            margin-bottom: 1.25rem;
        }

        /* ── Severity badges ───────────────────────────────── */
        .sev-badge {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.8rem;
            letter-spacing: 0.02em;
        }
        .sev-critical { background: rgba(239,68,68,0.18); color: #fca5a5; border: 1px solid rgba(239,68,68,0.3); }
        .sev-high     { background: rgba(245,158,11,0.18); color: #fcd34d; border: 1px solid rgba(245,158,11,0.3); }
        .sev-medium   { background: rgba(59,130,246,0.18); color: #93c5fd; border: 1px solid rgba(59,130,246,0.3); }
        .sev-low      { background: rgba(16,185,129,0.18); color: #6ee7b7; border: 1px solid rgba(16,185,129,0.3); }
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
