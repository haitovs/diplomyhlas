"""
Traffic Simulator — Normal workstation sending benign network traffic.
Styled as a modern dark desktop environment.
"""

import random
import time
import sys
from pathlib import Path
from datetime import datetime

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dashboard.demo_state import read_state, set_benign

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Traffic Simulator", page_icon="💻", layout="wide")

# ---------------------------------------------------------------------------
# Theme — dark desktop workstation
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

/* ---- hide sidebar & default chrome ---- */
[data-testid="stSidebar"] { display: none; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stAppViewContainer"] {
    background: #0f172a;
}
[data-testid="stMainBlockContainer"] {
    padding-top: 1rem;
}

/* ---- top taskbar ---- */
.taskbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 0.65rem 1.25rem;
    margin-bottom: 1rem;
    font-family: 'Inter', sans-serif;
}
.taskbar-left {
    display: flex;
    align-items: center;
    gap: 14px;
}
.taskbar-hostname {
    font-weight: 700;
    font-size: 0.9rem;
    color: #e2e8f0;
    letter-spacing: 0.02em;
}
.taskbar-sep {
    width: 1px;
    height: 18px;
    background: #475569;
}
.taskbar-item {
    font-size: 0.8rem;
    color: #94a3b8;
    font-weight: 500;
}
.taskbar-right {
    display: flex;
    align-items: center;
    gap: 12px;
}
.net-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    display: inline-block;
}
.net-dot-on {
    background: #22c55e;
    box-shadow: 0 0 6px #22c55e88;
    animation: blink-dot 2s infinite;
}
.net-dot-off {
    background: #ef4444;
    box-shadow: 0 0 6px #ef444488;
}
@keyframes blink-dot {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* ---- panels ---- */
.panel {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 1.1rem 1.25rem;
    height: 100%;
}
.panel-title {
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    font-size: 0.85rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.panel-title-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #3b82f6;
    display: inline-block;
}

/* ---- activity log ---- */
.log-scroll {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 6px;
    padding: 0.75rem 0.9rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    line-height: 1.7;
    max-height: 370px;
    overflow-y: auto;
    color: #22c55e;
}
.log-scroll::-webkit-scrollbar { width: 4px; }
.log-scroll::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
.log-line {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.log-ts { color: #64748b; }
.log-method { color: #3b82f6; font-weight: 600; }
.log-url { color: #22c55e; }
.log-status { color: #94a3b8; }
.log-size { color: #475569; }
.log-empty {
    color: #475569;
    text-align: center;
    padding: 3rem 0;
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
}

/* ---- system info ---- */
.sys-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.45rem 0;
    border-bottom: 1px solid #1e293b;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
}
.sys-row:last-child { border-bottom: none; }
.sys-label { color: #94a3b8; }
.sys-value { color: #e2e8f0; font-weight: 600; }
.bar-track {
    width: 100%;
    height: 6px;
    background: #0f172a;
    border-radius: 3px;
    margin-top: 4px;
    overflow: hidden;
}
.bar-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.3s ease;
}
.bar-blue { background: #3b82f6; }
.bar-green { background: #22c55e; }
.bar-amber { background: #f59e0b; }

/* ---- bottom control bar ---- */
.control-bar {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 0.75rem 1.25rem;
    margin-top: 1rem;
}

/* ---- tip box ---- */
.tip-box {
    background: #172554;
    border: 1px solid #1e40af;
    border-radius: 8px;
    padding: 0.7rem 1rem;
    margin-top: 0.75rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    color: #93c5fd;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ---- Streamlit widget overrides ---- */
.stSelectbox label, .stSlider label {
    color: #94a3b8 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
}
div[data-testid="stMarkdownContainer"] p {
    color: #94a3b8;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
state = read_state()
is_active = state["benign_active"]
current_speed = state.get("benign_speed", 1.0)

now_str = datetime.now().strftime("%H:%M:%S")
date_str = datetime.now().strftime("%a %b %d")

# ---------------------------------------------------------------------------
# Taskbar
# ---------------------------------------------------------------------------
net_dot_cls = "net-dot-on" if is_active else "net-dot-off"
net_label = "Connected" if is_active else "Disconnected"
st.markdown(f"""
<div class="taskbar">
    <div class="taskbar-left">
        <span class="taskbar-hostname">WORKSTATION-01</span>
        <div class="taskbar-sep"></div>
        <span class="taskbar-item">{date_str}</span>
        <div class="taskbar-sep"></div>
        <span class="taskbar-item">{now_str}</span>
    </div>
    <div class="taskbar-right">
        <span class="taskbar-item">{net_label}</span>
        <span class="net-dot {net_dot_cls}"></span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Main two-panel area
# ---------------------------------------------------------------------------
col_log, col_sys = st.columns([3, 2], gap="medium")

# ---- Left: Network Activity Log ----
with col_log:
    activities = [
        ("GET",  "https://example.com/index.html",       "200", "1.2 KB",  "42ms"),
        ("GET",  "https://api.service.com/v2/data",      "200", "3.5 KB",  "87ms"),
        ("POST", "https://mail.provider.com/send",       "201", "0.8 KB",  "124ms"),
        ("GET",  "https://cdn.images.io/photo.jpg",      "200", "45.0 KB", "31ms"),
        ("DNS",  "example.com -> 93.184.216.34",         "OK",  "64 B",    "4ms"),
        ("GET",  "https://docs.project.dev/readme",      "200", "2.1 KB",  "56ms"),
        ("TLS",  "handshake api.service.com:443",        "OK",  "1.4 KB",  "18ms"),
        ("GET",  "https://news.site.org/latest",         "200", "8.2 KB",  "93ms"),
        ("DNS",  "mail.provider.com -> 10.0.0.25",       "OK",  "64 B",    "3ms"),
        ("GET",  "https://storage.cloud.io/report.pdf",  "200", "125 KB",  "210ms"),
        ("GET",  "https://fonts.gstatic.com/s/inter",    "200", "18.4 KB", "22ms"),
        ("POST", "https://analytics.app.io/event",       "204", "0.3 KB",  "67ms"),
        ("GET",  "https://github.com/notifications",     "200", "4.7 KB",  "105ms"),
        ("DNS",  "cdn.images.io -> 104.18.12.33",        "OK",  "64 B",    "5ms"),
        ("GET",  "https://weather.api.com/today",        "200", "1.0 KB",  "48ms"),
    ]

    if is_active:
        base_ts = time.time()
        log_lines = []
        for i in range(14):
            method, url, status, size, latency = random.choice(activities)
            offset_ms = random.randint(0, 1999)
            ts = time.strftime("%H:%M:%S", time.localtime(base_ts)) + f".{offset_ms:03d}"
            log_lines.append(
                f'<div style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">'
                f'<span style="color:#64748b;">{ts}</span> '
                f'<span style="color:#3b82f6; font-weight:600;">{method:4s}</span> '
                f'<span style="color:#22c55e;">{url}</span> '
                f'<span style="color:#94a3b8;">[{status}]</span> '
                f'<span style="color:#475569;">{size} {latency}</span>'
                f'</div>'
            )
        log_content = "\n".join(log_lines)
    else:
        log_content = '<div style="color:#475569; text-align:center; padding:3rem 0; font-family:Inter,sans-serif; font-size:0.85rem;">No active traffic. Press Start to begin.</div>'

    st.markdown(f"""
    <div style="background:#1e293b; border:1px solid #334155; border-radius:10px; padding:1.1rem 1.25rem;">
        <div style="font-family:Inter,sans-serif; font-weight:700; font-size:0.85rem; color:#94a3b8;
             text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.75rem; display:flex; align-items:center; gap:8px;">
            <span style="width:6px; height:6px; border-radius:50%; background:#3b82f6; display:inline-block;"></span>
            Network Activity
        </div>
        <div style="background:#0f172a; border:1px solid #1e293b; border-radius:6px; padding:0.75rem 0.9rem;
             font-family:JetBrains Mono,monospace; font-size:0.75rem; line-height:1.7;
             max-height:370px; overflow-y:auto; color:#22c55e;">
            {log_content}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---- Right: System Info ----
with col_sys:
    if is_active:
        cpu = random.randint(12, 38)
        mem = random.randint(42, 61)
        net_down = round(random.uniform(1.2, 8.5), 1)
        net_up = round(random.uniform(0.3, 2.4), 1)
        conns = random.randint(6, 24)
        packets = random.randint(120, 480)
    else:
        cpu = random.randint(2, 6)
        mem = random.randint(35, 42)
        net_down = 0.0
        net_up = 0.0
        conns = 0
        packets = 0

    ROW = 'display:flex; justify-content:space-between; align-items:center; padding:0.45rem 0; border-bottom:1px solid #1e293b; font-family:JetBrains Mono,monospace; font-size:0.78rem;'
    LBL = 'color:#94a3b8;'
    VAL = 'color:#e2e8f0; font-weight:600;'
    TRACK = 'width:100%; height:6px; background:#0f172a; border-radius:3px; margin-top:4px; overflow:hidden;'

    def bar_html(pct, color):
        return f'<div style="{TRACK}"><div style="height:100%; border-radius:3px; background:{color}; width:{pct}%;"></div></div>'

    sys_html = f"""
    <div style="background:#1e293b; border:1px solid #334155; border-radius:10px; padding:1.1rem 1.25rem;">
        <div style="font-family:Inter,sans-serif; font-weight:700; font-size:0.85rem; color:#94a3b8;
             text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.75rem; display:flex; align-items:center; gap:8px;">
            <span style="width:6px; height:6px; border-radius:50%; background:#3b82f6; display:inline-block;"></span>
            System Info
        </div>
        <div style="{ROW}"><span style="{LBL}">CPU</span><span style="{VAL}">{cpu}%</span></div>
        {bar_html(cpu, '#3b82f6')}
        <div style="{ROW}"><span style="{LBL}">Memory</span><span style="{VAL}">{mem}%</span></div>
        {bar_html(mem, '#f59e0b')}
        <div style="{ROW}"><span style="{LBL}">Net Down</span><span style="{VAL}">{net_down} MB/s</span></div>
        {bar_html(min(int(net_down / 10 * 100), 100), '#22c55e')}
        <div style="{ROW}"><span style="{LBL}">Net Up</span><span style="{VAL}">{net_up} MB/s</span></div>
        {bar_html(min(int(net_up / 5 * 100), 100), '#22c55e')}
        <div style="{ROW}"><span style="{LBL}">Connections</span><span style="{VAL}">{conns}</span></div>
        <div style="{ROW}"><span style="{LBL}">Packets / sec</span><span style="{VAL}">{packets}</span></div>
        <div style="{ROW}"><span style="{LBL}">Hostname</span><span style="{VAL}">WORKSTATION-01</span></div>
        <div style="{ROW}"><span style="{LBL}">OS</span><span style="{VAL}">Ubuntu 22.04</span></div>
        <div style="{ROW} border-bottom:none;"><span style="{LBL}">Uptime</span><span style="{VAL}">3d 14h 22m</span></div>
    </div>
    """
    st.markdown(sys_html, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Bottom control bar
# ---------------------------------------------------------------------------
st.markdown('<div class="control-bar">', unsafe_allow_html=True)

ctrl_left, ctrl_mid, ctrl_right = st.columns([2, 2, 3], gap="medium")

with ctrl_left:
    if not is_active:
        if st.button("Start Traffic", type="primary", key="start_benign", icon=":material/play_arrow:", width="stretch"):
            set_benign(True, current_speed)
            st.rerun()
    else:
        if st.button("Stop Traffic", type="secondary", key="stop_benign", icon=":material/stop:", width="stretch"):
            set_benign(False)
            st.rerun()

with ctrl_mid:
    speed = st.select_slider(
        "Speed",
        options=[0.5, 1.0, 2.0, 5.0],
        value=current_speed,
        format_func=lambda x: f"{x}x",
        key="speed_slider",
    )
    if speed != current_speed:
        set_benign(is_active, speed)

st.markdown('</div>', unsafe_allow_html=True)

# ---- Tip ----
if is_active:
    st.markdown("""
    <div class="tip-box">
        <span>📡</span>
        <span>Open <strong>Live Monitor</strong> in another tab to watch this traffic analyzed by the ML model in real time.</span>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Auto-refresh while active
# ---------------------------------------------------------------------------
if is_active:
    time.sleep(2)
    st.rerun()
