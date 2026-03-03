"""
Reusable UI Components for Streamlit Dashboard
Professional loading indicators, progress bars, and widgets
"""

import streamlit as st
import time
from datetime import datetime
from typing import Optional, Callable, List, Dict


# ── Cross-Page Shared State ─────────────────────────────────────────────────

DEFAULT_SETTINGS = {
    'confidence_threshold': 0.70,
    'model': 'LightGBM (Prod)',
    'sensitivity': 'Balanced',
}


def init_shared_state():
    """Initialize shared session-state keys used across all pages."""
    if 'detection_log' not in st.session_state:
        st.session_state.detection_log = []

    if 'session_metrics' not in st.session_state:
        st.session_state.session_metrics = {
            'total_flows': 0,
            'total_threats': 0,
            'by_type': {},
            'by_source': {},
            'session_start': datetime.now(),
        }

    if 'settings' not in st.session_state:
        st.session_state.settings = dict(DEFAULT_SETTINGS)

    if 'pcap_results' not in st.session_state:
        st.session_state.pcap_results = None


def append_detections(detections: List[Dict], source: str = "unknown"):
    """Push anomaly detections into the shared log with IDs and severity.

    Each detection dict should contain at minimum:
        prediction, confidence, is_anomaly,
        src_ip, dst_ip, dst_port  (optional but recommended)
    """
    init_shared_state()
    metrics = st.session_state.session_metrics

    for det in detections:
        if not det.get('is_anomaly', False):
            continue

        conf = det.get('confidence', 0)
        if conf < 0.9:
            severity = 'Medium'
        elif conf < 0.95:
            severity = 'High'
        else:
            severity = 'Critical'

        entry = {
            'id': f"ATK-{10000 + len(st.session_state.detection_log)}",
            'timestamp': det.get('timestamp', datetime.now()),
            'type': det.get('prediction', 'Unknown'),
            'src_ip': det.get('src_ip', 'N/A'),
            'dst_ip': det.get('dst_ip', 'N/A'),
            'dst_port': det.get('dst_port', ''),
            'confidence': conf,
            'severity': severity,
            'source': source,
        }
        st.session_state.detection_log.append(entry)

        # Update counters
        metrics['total_threats'] += 1
        attack_type = entry['type']
        metrics['by_type'][attack_type] = metrics['by_type'].get(attack_type, 0) + 1
        metrics['by_source'][source] = metrics['by_source'].get(source, 0) + 1

    metrics['total_flows'] += len(detections)


def loading_spinner(text: str = "Processing", duration: Optional[float] = None):
    """Show a professional loading spinner"""
    with st.spinner(text):
        if duration:
            time.sleep(duration)


def progress_bar(steps: list, step_duration: float = 0.3):
    """Show a progress bar with step labels"""
    progress_text = st.empty()
    progress = st.progress(0)

    for i, step in enumerate(steps):
        progress_text.text(f"⚙️ {step}...")
        progress.progress((i + 1) / len(steps))
        time.sleep(step_duration)

    time.sleep(0.2)
    progress_text.empty()
    progress.empty()


def animated_metric(label: str, value: str, delta: Optional[str] = None,
                    delta_color: str = "normal", icon: str = "📊"):
    """Create an animated metric card with icon"""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-content">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {f'<div class="metric-delta {delta_color}">{delta}</div>' if delta else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)


def status_badge(text: str, status: str = "success"):
    """Create a status badge"""
    colors = {
        'success': ('#22c55e', '#064e3b'),
        'warning': ('#f59e0b', '#78350f'),
        'error': ('#ef4444', '#7f1d1d'),
        'info': ('#0ea5e9', '#0c4a6e')
    }

    bg_color, text_color = colors.get(status, colors['info'])

    st.markdown(f"""
    <span style="
        background: {bg_color}20;
        color: {bg_color};
        border: 1px solid {bg_color}40;
        padding: 4px 12px;
        border-radius: 2px;
        font-size: 0.875rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        font-family: 'Space Grotesk', sans-serif;
        display: inline-block;
    ">{text}</span>
    """, unsafe_allow_html=True)


def severity_badge(severity: str) -> str:
    """Return an HTML span for a severity badge (for use inside tables/markdown)."""
    css_class = {
        "Critical": "sev-critical",
        "High": "sev-high",
        "Medium": "sev-medium",
        "Low": "sev-low",
    }.get(severity, "sev-medium")
    return f'<span class="sev-badge {css_class}">{severity}</span>'


def page_header(icon: str, title: str, subtitle: str = ""):
    """Render a breadcrumb-style page header bar."""
    sub_html = ""
    if subtitle:
        sub_html = f'<span class="ph-sep">/</span><span class="ph-sub">{subtitle}</span>'
    st.markdown(f"""
    <div class="page-header">
        <span class="ph-icon">{icon}</span>
        <span class="ph-title">{title}</span>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def alert_box(message: str, alert_type: str = "info", icon: str = "ℹ️"):
    """Create an alert box"""
    type_styles = {
        'info': ('rgba(14,165,233,0.12)', '#0ea5e9'),
        'success': ('rgba(34,197,94,0.12)', '#22c55e'),
        'warning': ('rgba(245,158,11,0.12)', '#f59e0b'),
        'error': ('rgba(239,68,68,0.12)', '#ef4444'),
    }

    background, border_color = type_styles.get(alert_type, type_styles['info'])

    st.markdown(f"""
    <div style="
        background: {background};
        color: {border_color};
        padding: 12px 16px;
        border-radius: 2px;
        border-left: 3px solid {border_color};
        margin: 8px 0;
        display: flex;
        align-items: center;
        gap: 12px;
    ">
        <span style="font-size: 1.25rem;">{icon}</span>
        <span style="color: #e2e8f0;">{message}</span>
    </div>
    """, unsafe_allow_html=True)


def export_button(data, filename: str, file_format: str = "csv", label: str = "📥 Export Data"):
    """Create a download button for data export"""
    if file_format == 'csv':
        file_data = data.to_csv(index=False).encode('utf-8')
        mime_type = 'text/csv'
    elif file_format == 'json':
        if hasattr(data, 'to_json'):
            file_data = data.to_json(orient='records', indent=2).encode('utf-8')
        else:
            import json
            file_data = json.dumps(data, indent=2).encode('utf-8')
        mime_type = 'application/json'
    else:
        raise ValueError(f"Unsupported format: {file_format}")

    st.download_button(
        label=label,
        data=file_data,
        file_name=filename,
        mime=mime_type
    )


def info_card(title: str, content: str, icon: str = "📌"):
    """Create an information card"""
    st.markdown(f"""
    <div style="
        background: rgba(245,158,11,0.06);
        border: 1px solid rgba(245,158,11,0.12);
        border-left: 3px solid #f59e0b;
        border-radius: 2px;
        padding: 16px;
        margin: 8px 0;
    ">
        <div style="
            font-size: 1.1rem;
            font-weight: 700;
            color: #f59e0b;
            font-family: 'Space Grotesk', sans-serif;
            margin-bottom: 8px;
        ">
            {icon} {title}
        </div>
        <div style="color: #e2e8f0;">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)


def section_header(title: str, subtitle: Optional[str] = None, icon: str = ""):
    """Create a section header with optional subtitle"""
    header_html = f'<h2 style="color: #e2e8f0; font-family: Space Grotesk, sans-serif; margin-bottom: 0.5rem;">{icon} {title}</h2>'
    if subtitle:
        header_html += f'<p style="color: #7c8aa4; margin-bottom: 1rem;">{subtitle}</p>'

    st.markdown(header_html, unsafe_allow_html=True)


def data_source_selector(manager, key: str = "data_source"):
    """Create a data source selector with information display"""
    from src.data.data_sources import get_data_source_options

    source_options = get_data_source_options(manager)

    selected_name = st.selectbox(
        "📊 Data Source",
        options=list(source_options.keys()),
        key=key,
        help="Select where to load network traffic data from"
    )

    selected_id = source_options[selected_name]

    if selected_id != manager.current_source:
        manager.set_source(selected_id)

    source_info = manager.get_source_info()

    with st.expander("ℹ️ Source Information", expanded=False):
        st.json(source_info)

    return selected_id


def simulate_processing(steps: Optional[list] = None, total_duration: float = 1.5):
    """Simulate data processing with visual feedback"""
    if steps is None:
        steps = [
            "Loading data",
            "Extracting features",
            "Running model inference",
            "Computing statistics",
            "Generating visualizations"
        ]

    step_duration = total_duration / len(steps)
    progress_bar(steps, step_duration)


# CSS for custom components
COMPONENTS_CSS = """
<style>
    .metric-card {
        background: #131d2e;
        border: 1px solid rgba(245,158,11,0.10);
        border-left: 3px solid #f59e0b;
        border-radius: 4px;
        padding: 1.25rem;
        display: flex;
        gap: 1rem;
        align-items: center;
        transition: all 0.25s ease;
    }

    .metric-card:hover {
        border-color: rgba(245,158,11,0.25);
        box-shadow: 0 4px 16px rgba(0,0,0,0.25);
    }

    .metric-icon {
        font-size: 2rem;
    }

    .metric-content {
        flex: 1;
    }

    .metric-label {
        color: #7c8aa4;
        font-size: 0.8rem;
        margin-bottom: 0.25rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        font-weight: 500;
    }

    .metric-value {
        color: #f59e0b;
        font-size: 1.75rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
    }

    .metric-delta {
        font-size: 0.85rem;
        margin-top: 0.25rem;
    }

    .metric-delta.success {
        color: #22c55e;
    }

    .metric-delta.warning {
        color: #f59e0b;
    }

    .metric-delta.error {
        color: #ef4444;
    }

    .metric-delta.normal {
        color: #7c8aa4;
    }
</style>
"""


def inject_components_css():
    """Inject CSS for custom components"""
    st.markdown(COMPONENTS_CSS, unsafe_allow_html=True)
