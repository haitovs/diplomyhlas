"""
Reusable UI Components for Streamlit Dashboard
Professional loading indicators, progress bars, and widgets
"""

import streamlit as st
import time
from typing import Optional, Callable


def loading_spinner(text: str = "Processing", duration: Optional[float] = None):
    """
    Show a professional loading spinner
    
    Args:
        text: Loading message
        duration: Optional duration to show spinner (for simulation)
    """
    with st.spinner(text):
        if duration:
            time.sleep(duration)
            

def progress_bar(steps: list, step_duration: float = 0.3):
    """
    Show a progress bar with step labels
    
    Args:
        steps: List of step names
        step_duration: Time to wait between steps
    """
    progress_text = st.empty()
    progress = st.progress(0)
    
    for i, step in enumerate(steps):
        progress_text.text(f"⚙️ {step}...")
        progress.progress((i + 1) / len(steps))
        time.sleep(step_duration)
    
    # Clear when done
    time.sleep(0.2)
    progress_text.empty()
    progress.empty()


def animated_metric(label: str, value: str, delta: Optional[str] = None, 
                   delta_color: str = "normal", icon: str = "📊"):
    """
    Create an animated metric card with icon
    """
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
    """
    Create a status badge
    
    Args:
        text: Badge text
        status: 'success', 'warning', 'error', 'info'
    """
    colors = {
        'success': ('#10b981', '#064e3b'),
        'warning': ('#f59e0b', '#78350f'),
        'error': ('#ef4444', '#7f1d1d'),
        'info': ('#3b82f6', '#1e3a8a')
    }
    
    bg_color, text_color = colors.get(status, colors['info'])
    
    st.markdown(f"""
    <span style="
        background: {bg_color}20;
        color: {bg_color};
        border: 1px solid {bg_color}40;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.875rem;
        font-weight: 600;
        display: inline-block;
    ">{text}</span>
    """, unsafe_allow_html=True)


def alert_box(message: str, alert_type: str = "info", icon: str = "ℹ️"):
    """
    Create an alert box
    
    Args:
        message: Alert message
        alert_type: 'info', 'success', 'warning', 'error'
        icon: Optional icon
    """
    type_styles = {
        'info': ('linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)', '#93c5fd'),
        'success': ('linear-gradient(135deg, #10b981 0%, #059669 100%)', '#6ee7b7'),
        'warning': ('linear-gradient(135deg, #f59e0b 0%, #d97706 100%)', '#fcd34d'),
        'error': ('linear-gradient(135deg, #ef4444 0%, #dc2626 100%)', '#fca5a5'),
    }
    
    background, border_color = type_styles.get(alert_type, type_styles['info'])
    
    st.markdown(f"""
    <div style="
        background: {background};
        color: white;
        padding: 12px 16px;
        border-radius: 8px;
        border-left: 4px solid {border_color};
        margin: 8px 0;
        display: flex;
        align-items: center;
        gap: 12px;
    ">
        <span style="font-size: 1.25rem;">{icon}</span>
        <span>{message}</span>
    </div>
    """, unsafe_allow_html=True)


def export_button(data, filename: str, file_format: str = "csv", label: str = "📥 Export Data"):
    """
    Create a download button for data export
    
    Args:
        data: DataFrame or dict to export
        filename: Output filename
        file_format: 'csv' or 'json'
        label: Button label
    """
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
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
    ">
        <div style="
            font-size: 1.1rem;
            font-weight: 600;
            color: #a5b4fc;
            margin-bottom: 8px;
        ">
            {icon} {title}
        </div>
        <div style="color: #cbd5e1;">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)


def section_header(title: str, subtitle: Optional[str] = None, icon: str = ""):
    """Create a section header with optional subtitle"""
    header_html = f'<h2 style="color: #ffffff; margin-bottom: 0.5rem;">{icon} {title}</h2>'
    if subtitle:
        header_html += f'<p style="color: #94a3b8; margin-bottom: 1rem;">{subtitle}</p>'
    
    st.markdown(header_html, unsafe_allow_html=True)


def data_source_selector(manager, key: str = "data_source"):
    """
    Create a data source selector with information display
    
    Args:
        manager: DataSourceManager instance
        key: Unique key for the widget
    
    Returns:
        Selected source ID
    """
    from src.data.data_sources import get_data_source_options
    
    # Get available sources
    source_options = get_data_source_options(manager)
    
    # Create selector
    selected_name = st.selectbox(
        "📊 Data Source",
        options=list(source_options.keys()),
        key=key,
        help="Select where to load network traffic data from"
    )
    
    # Get selected source ID
    selected_id = source_options[selected_name]
    
    # Show source info
    if selected_id != manager.current_source:
        manager.set_source(selected_id)
    
    source_info = manager.get_source_info()
    
    # Display source information
    with st.expander("ℹ️ Source Information", expanded=False):
        st.json(source_info)
    
    return selected_id


def simulate_processing(steps: Optional[list] = None, total_duration: float = 1.5):
    """
    Simulate data processing with visual feedback
    
    Args:
        steps: List of processing step names
        total_duration: Total time to simulate
    """
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
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 1.25rem;
        display: flex;
        gap: 1rem;
        align-items: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(99, 102, 241, 0.2);
    }
    
    .metric-icon {
        font-size: 2rem;
    }
    
    .metric-content {
        flex: 1;
    }
    
    .metric-label {
        color: #94a3b8;
        font-size: 0.875rem;
        margin-bottom: 0.25rem;
    }
    
    .metric-value {
        color: #ffffff;
        font-size: 1.75rem;
        font-weight: 700;
    }
    
    .metric-delta {
        font-size: 0.875rem;
        margin-top: 0.25rem;
    }
    
    .metric-delta.success {
        color: #10b981;
    }
    
    .metric-delta.warning {
        color: #f59e0b;
    }
    
    .metric-delta.error {
        color: #ef4444;
    }
</style>
"""


def inject_components_css():
    """Inject CSS for custom components"""
    st.markdown(COMPONENTS_CSS, unsafe_allow_html=True)


if __name__ == '__main__':
    # Demo of components
    st.set_page_config(page_title="Components Demo", layout="wide")
    
    inject_components_css()
    
    st.title("🎨 UI Components Demo")
    
    st.header("Status Badges")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        status_badge("Success", "success")
    with col2:
        status_badge("Warning", "warning")
    with col3:
        status_badge("Error", "error")
    with col4:
        status_badge("Info", "info")
    
    st.header("Alert Boxes")
    alert_box("This is an info message", "info", "ℹ️")
    alert_box("Operation successful!", "success", "✅")
    alert_box("Warning: High traffic detected", "warning", "⚠️")
    alert_box("Critical: System under attack!", "error", "🚨")
    
    st.header("Info Cards")
    info_card("Model Information", "LightGBM classifier with 98% accuracy", "🤖")
    
    st.header("Progress Simulation")
    if st.button("Simulate Processing"):
        simulate_processing()
        st.success("Processing complete!")
