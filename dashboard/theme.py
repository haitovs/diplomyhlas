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
        
        /* Hero Section */
        .hero-container {
            text-align: center;
            padding: 4rem 2rem;
            background: radial-gradient(circle at 50% 0%, rgba(99, 102, 241, 0.15) 0%, transparent 70%);
            border-bottom: 1px solid """ + COLORS['border'] + """;
            margin-bottom: 3rem;
        }
        
        .hero-title {
            font-size: 4rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, """ + COLORS['primary'] + """ 0%, """ + COLORS['accent'] + """ 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }
        
        .hero-subtitle {
            font-size: 1.25rem;
            color: """ + COLORS['text_muted'] + """;
            max-width: 600px;
            margin: 0 auto 2rem auto;
            line-height: 1.6;
        }
        
        /* Typography */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Inter', sans-serif !important;
            color: """ + COLORS['text_main'] + """ !important;
            letter-spacing: -0.01em;
        }
        
        code, pre {
            font-family: 'JetBrains Mono', monospace !important;
        }
        
        /* Cards */
        .feature-card {
            background: """ + COLORS['bg_tertiary'] + """;
            border: 1px solid """ + COLORS['border'] + """;
            border-radius: 16px;
            padding: 1.5rem;
            transition: all 0.3s ease;
            height: 100%;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            border-color: rgba(99, 102, 241, 0.5);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }
        
        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            display: inline-block;
            background: linear-gradient(135deg, """ + COLORS['primary'] + """ 0%, """ + COLORS['accent'] + """ 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Metrics Redesign */
        [data-testid="stMetric"] {
            background: """ + COLORS['bg_tertiary'] + """;
            border: 1px solid """ + COLORS['border'] + """;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        [data-testid="stMetricLabel"] {
            color: """ + COLORS['text_muted'] + """ !important;
            font-size: 0.9rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        [data-testid="stMetricValue"] {
            color: """ + COLORS['text_main'] + """ !important;
            font-size: 2.5rem;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace !important;
        }
        
        /* Status Elements */
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
        
        /* Primary Button Override */
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
            background: """ + COLORS['bg_tertiary'] + """;
            border: 1px solid """ + COLORS['border'] + """;
            color: """ + COLORS['text_main'] + """;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        .stButton > button[data-testid="baseButton-secondary"]:hover {
            border-color: """ + COLORS['primary'] + """;
            color: """ + COLORS['primary'] + """;
        }
        
        /* Sidebar Polish */
        [data-testid="stSidebar"] {
            background: rgba(10, 15, 26, 0.95);
            backdrop-filter: blur(10px);
            border-right: 1px solid """ + COLORS['border'] + """;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: """ + COLORS['bg_secondary'] + """; }
        ::-webkit-scrollbar-thumb { 
            background: rgba(99, 102, 241, 0.5); 
            border-radius: 4px; 
        }
        ::-webkit-scrollbar-thumb:hover { background: """ + COLORS['primary'] + """; }
        
        /* Hide elements */
        #MainMenu {visibility: hidden;}
        header[data-testid="stHeader"] {background: transparent;}
    </style>
    """, unsafe_allow_html=True)
