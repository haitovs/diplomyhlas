"""
☠️ Attacker Console — Advanced hacker terminal for launching attacks.
Dark terminal aesthetic with red/green accents, quick commands, and live output.
"""

import streamlit as st
import random
import time
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dashboard.demo_state import read_state, set_attack, set_all_attacks, stop_all, queue_burst

st.set_page_config(page_title="Attacker Console", page_icon="☠️", layout="wide")

# ── CSS: Hacker terminal theme ───────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700;800&family=Share+Tech+Mono&display=swap');

/* ---- Hide sidebar ---- */
[data-testid="stSidebar"] { display: none; }

/* ---- Background with scan lines ---- */
[data-testid="stAppViewContainer"] {
    background: #000000;
    background-image:
        repeating-linear-gradient(
            0deg,
            rgba(0,255,0,0.008) 0px,
            rgba(0,255,0,0.008) 1px,
            transparent 1px,
            transparent 3px
        ),
        radial-gradient(ellipse at 20% 30%, rgba(255,0,0,0.04) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 70%, rgba(0,255,0,0.025) 0%, transparent 60%);
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMainBlockContainer"] { max-width: 1200px; }

/* ---- Global text ---- */
* {
    font-family: 'JetBrains Mono', 'Share Tech Mono', monospace !important;
}
div[data-testid="stMarkdownContainer"] p,
div[data-testid="stMarkdownContainer"] li {
    color: #777;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
}
div[data-testid="stMarkdownContainer"] h4 {
    color: #ff4444;
    font-family: 'Share Tech Mono', monospace;
    letter-spacing: 0.08em;
}

/* ---- Scan-line header ---- */
.atk-header {
    background: linear-gradient(180deg, #0a0000 0%, #0d0505 100%);
    border: 1px solid #ff000025;
    border-radius: 2px;
    padding: 1.8rem 2rem 1.4rem;
    margin-bottom: 1.2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.atk-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent 0%, #ff0000 50%, transparent 100%);
    animation: scanline 2.8s ease-in-out infinite;
}
.atk-header::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, #ff000040, transparent);
}
@keyframes scanline {
    0%   { transform: translateX(-100%); opacity: 0.6; }
    50%  { opacity: 1; }
    100% { transform: translateX(100%); opacity: 0.6; }
}
.atk-header h1 {
    font-family: 'Share Tech Mono', monospace;
    font-size: 2.4rem;
    font-weight: 800;
    color: #ff0000;
    margin: 0;
    text-shadow: 0 0 30px rgba(255,0,0,0.35), 0 0 60px rgba(255,0,0,0.12);
    letter-spacing: 0.15em;
}
.atk-header .subtitle {
    color: #444;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    margin-top: 0.4rem;
    letter-spacing: 0.06em;
}
.atk-header .target-display {
    display: inline-block;
    margin-top: 0.7rem;
    padding: 0.25rem 1rem;
    background: #0a0a0a;
    border: 1px solid #ff000030;
    border-radius: 2px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #ff4444;
    letter-spacing: 0.05em;
}
.atk-header .target-display span {
    color: #555;
}

/* ---- Attack card ---- */
.atk-card {
    background: linear-gradient(135deg, #0a0a0a 0%, #0f0f0f 100%);
    border: 1px solid #1a1a1a;
    border-radius: 3px;
    padding: 1.1rem 1.2rem;
    margin-bottom: 0.6rem;
    transition: border-color 0.3s, box-shadow 0.3s;
    position: relative;
    overflow: hidden;
}
.atk-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: #1a1a1a;
    transition: background 0.3s;
}
.atk-card:hover {
    border-color: #ff000030;
}
.atk-card:hover::before {
    background: #ff000060;
}
.atk-card.active {
    border-color: #ff0000;
    box-shadow: 0 0 25px rgba(255,0,0,0.08), inset 0 0 30px rgba(255,0,0,0.03);
}
.atk-card.active::before {
    background: #ff0000;
    box-shadow: 0 0 8px rgba(255,0,0,0.6);
}
.atk-badge {
    position: absolute;
    top: 10px; right: 12px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    padding: 2px 8px;
    border-radius: 2px;
}
.atk-badge.active-badge {
    color: #ff0000;
    background: #ff000015;
    border: 1px solid #ff000040;
    animation: pulse-badge 1.2s ease-in-out infinite;
}
.atk-badge.idle-badge {
    color: #333;
    background: transparent;
    border: 1px solid #1a1a1a;
}
@keyframes pulse-badge {
    0%, 100% { opacity: 1; box-shadow: 0 0 6px rgba(255,0,0,0.3); }
    50% { opacity: 0.5; box-shadow: 0 0 2px rgba(255,0,0,0.1); }
}
.atk-card .name {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.05rem;
    font-weight: 700;
    color: #ff4444;
    margin-bottom: 3px;
    text-shadow: 0 0 8px rgba(255,68,68,0.15);
}
.atk-card .desc {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #555;
    line-height: 1.45;
    margin-bottom: 6px;
}
.atk-card .meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: #333;
}
.atk-card .meta b {
    color: #ff4444;
    font-weight: 500;
}
.atk-card .pkt-counter {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #ff0000;
    margin-top: 6px;
    text-shadow: 0 0 6px rgba(255,0,0,0.25);
}

/* ---- Quick command section ---- */
.qcmd-section {
    background: #060606;
    border: 1px solid #151515;
    border-radius: 3px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.4rem;
}
.qcmd-section .section-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
    color: #ff4444;
    margin-bottom: 0.5rem;
    letter-spacing: 0.06em;
}

/* ---- Terminal output ---- */
.terminal-box {
    background: #050505;
    border: 1px solid #1a1a1a;
    border-radius: 3px;
    padding: 0;
    position: relative;
    overflow: hidden;
}
.terminal-bar {
    background: #0f0f0f;
    border-bottom: 1px solid #1a1a1a;
    padding: 0.35rem 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.terminal-bar .dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    display: inline-block;
}
.terminal-bar .dot.r { background: #ff0000; }
.terminal-bar .dot.y { background: #ffaa00; }
.terminal-bar .dot.g { background: #00ff00; }
.terminal-bar .title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #444;
    margin-left: 0.5rem;
    letter-spacing: 0.04em;
}
.terminal-body {
    padding: 0.8rem 1rem;
    max-height: 380px;
    overflow-y: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    line-height: 1.55;
    color: #00ff00;
    text-shadow: 0 0 4px rgba(0,255,0,0.15);
}
.terminal-body::-webkit-scrollbar { width: 4px; }
.terminal-body::-webkit-scrollbar-track { background: #0a0a0a; }
.terminal-body::-webkit-scrollbar-thumb { background: #222; border-radius: 2px; }
.t-line { padding: 1px 0; white-space: pre-wrap; word-break: break-all; }
.t-red { color: #ff4444; }
.t-green { color: #00ff00; }
.t-yellow { color: #ffaa00; }
.t-dim { color: #333; }
.t-cyan { color: #00cccc; }
.t-white { color: #999; }
.t-prompt { color: #ff0000; }
.t-time { color: #444; }

/* ---- Streamlit button overrides ---- */
.stButton > button {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.06em !important;
    border-radius: 2px !important;
    transition: all 0.15s !important;
}

/* ---- Input field styling ---- */
div[data-testid="stTextInput"] input {
    background: #0a0a0a !important;
    color: #ff4444 !important;
    border: 1px solid #1a1a1a !important;
    font-family: 'JetBrains Mono', monospace !important;
    border-radius: 2px !important;
}
div[data-testid="stTextInput"] label {
    color: #555 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
}
div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background: #0a0a0a !important;
    border: 1px solid #1a1a1a !important;
    border-radius: 2px !important;
}
div[data-testid="stSelectbox"] label {
    color: #555 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
}
</style>
""", unsafe_allow_html=True)

# ── State ─────────────────────────────────────────────────────────────────
state = read_state()
attacks = state.get("attacks", {})
active_count = sum(1 for v in attacks.values() if v)

# ── Session defaults ──────────────────────────────────────────────────────
if "target_ip" not in st.session_state:
    st.session_state.target_ip = "127.0.0.1"
if "packet_count" not in st.session_state:
    st.session_state.packet_count = "100"

# ── Attack definitions ────────────────────────────────────────────────────
ATTACK_INFO = {
    "ddos": {
        "name": "DDoS SYN FLOOD",
        "desc": "Exhaust target connection table with spoofed SYN packets",
        "port": "80",
        "tool": "hping3 / scapy",
        "severity": "CRITICAL",
    },
    "portscan": {
        "name": "PORT SCANNER",
        "desc": "Sequential port probe for service discovery and recon",
        "port": "1-1024",
        "tool": "nmap SYN scan",
        "severity": "HIGH",
    },
    "ssh": {
        "name": "SSH BRUTE FORCE",
        "desc": "Dictionary attack against SSH with credential stuffing",
        "port": "22",
        "tool": "hydra / patator",
        "severity": "CRITICAL",
    },
    "ftp": {
        "name": "FTP BRUTE FORCE",
        "desc": "Brute-force FTP login with common password lists",
        "port": "21",
        "tool": "medusa / patator",
        "severity": "HIGH",
    },
}

# ── Header ────────────────────────────────────────────────────────────────
target_ip = st.session_state.target_ip
st.markdown(f"""
<div class="atk-header">
    <h1>☠️ ATTACK CONSOLE</h1>
    <div class="subtitle">[ network penetration toolkit // educational use only ]</div>
    <div class="target-display">
        <span>TARGET:</span> {target_ip}
        &nbsp;&nbsp;<span>|</span>&nbsp;&nbsp;
        <span>STATUS:</span> {"<span style='color:#ff0000;'>ENGAGED</span>" if active_count > 0 else "<span style='color:#333;'>STANDBY</span>"}
    </div>
</div>
""", unsafe_allow_html=True)

# ── Target configuration bar ─────────────────────────────────────────────
cfg1, cfg2, cfg3 = st.columns([3, 2, 2])
with cfg1:
    new_ip = st.text_input(
        "TARGET IP",
        value=st.session_state.target_ip,
        key="ip_input",
        placeholder="e.g. 192.168.1.100",
    )
    if new_ip != st.session_state.target_ip:
        st.session_state.target_ip = new_ip
        target_ip = new_ip
with cfg2:
    pkt_options = ["10", "50", "100", "500", "1000"]
    pkt_choice = st.selectbox(
        "PACKET COUNT",
        pkt_options,
        index=pkt_options.index(st.session_state.packet_count)
        if st.session_state.packet_count in pkt_options
        else 2,
        key="pkt_select",
    )
    st.session_state.packet_count = pkt_choice
with cfg3:
    st.markdown(
        f"""<div style="padding-top:1.7rem;">
        <span style="font-size:0.72rem; color:#333;">ACTIVE VECTORS:
        <span style="color:#ff4444; font-weight:700;">{active_count}/4</span></span>
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown('<div style="margin-bottom:0.6rem;"></div>', unsafe_allow_html=True)

# ── Attack grid (2x2) ────────────────────────────────────────────────────
col_left, col_right = st.columns(2)

for idx, (atk_key, info) in enumerate(ATTACK_INFO.items()):
    is_active = attacks.get(atk_key, False)
    card_cls = "atk-card active" if is_active else "atk-card"
    badge_cls = "atk-badge active-badge" if is_active else "atk-badge idle-badge"
    badge_text = "● ACTIVE" if is_active else "○ IDLE"

    pkt_sent = random.randint(800, 9999) if is_active else 0
    pkt_html = (
        f'<div class="pkt-counter">▸ {pkt_sent:,} packets sent &nbsp;|&nbsp; '
        f'{random.randint(80, 600)} pkt/s</div>'
        if is_active
        else ""
    )

    card_html = f"""
    <div class="{card_cls}">
        <span class="{badge_cls}">{badge_text}</span>
        <div class="name">{info['name']}</div>
        <div class="desc">{info['desc']}</div>
        <div class="meta">
            PORT <b>{info['port']}</b>
            &nbsp;·&nbsp; TOOL <b>{info['tool']}</b>
            &nbsp;·&nbsp; SEV <b>{info['severity']}</b>
        </div>
        {pkt_html}
    </div>
    """

    col = col_left if idx % 2 == 0 else col_right
    with col:
        st.markdown(card_html, unsafe_allow_html=True)
        if is_active:
            if st.button(
                f"■ STOP {info['name']}",
                key=f"stop_{atk_key}",
                type="secondary",
                width="stretch",
            ):
                set_attack(atk_key, False)
                st.rerun()
        else:
            if st.button(
                f"▶ LAUNCH {info['name']}",
                key=f"start_{atk_key}",
                type="primary",
                width="stretch",
            ):
                set_attack(atk_key, True)
                st.rerun()

# ── Quick Commands ────────────────────────────────────────────────────────
st.markdown('<div style="margin-top:0.8rem;"></div>', unsafe_allow_html=True)
st.markdown("#### > QUICK COMMANDS")

QUICK_CMDS = [
    {
        "label": f"send_syn --target {target_ip} --port 80 --count 1",
        "short": "$ send_syn x1",
        "desc": "Send 1 SYN packet",
        "attack": "ddos",
        "count": 1,
        "key": "qc_syn1",
    },
    {
        "label": f"send_syn --target {target_ip} --port 80 --count 10",
        "short": "$ send_syn x10",
        "desc": "Send 10 SYN packets",
        "attack": "ddos",
        "count": 10,
        "key": "qc_syn10",
    },
    {
        "label": f"scan_ports --target {target_ip} --range 1-100",
        "short": "$ scan_ports",
        "desc": "Scan 5 ports",
        "attack": "portscan",
        "count": 5,
        "key": "qc_scan",
    },
    {
        "label": f"brute_ssh --target {target_ip} --attempts 5",
        "short": "$ brute_ssh",
        "desc": "5 SSH attempts",
        "attack": "ssh",
        "count": 5,
        "key": "qc_ssh",
    },
    {
        "label": f"brute_ftp --target {target_ip} --attempts 5",
        "short": "$ brute_ftp",
        "desc": "5 FTP attempts",
        "attack": "ftp",
        "count": 5,
        "key": "qc_ftp",
    },
]

st.markdown(
    '<div class="qcmd-section">'
    '<div class="section-title">$ quick commands — fire &amp; forget (no need to stop)</div>'
    "</div>",
    unsafe_allow_html=True,
)

qc_cols = st.columns(len(QUICK_CMDS))
for i, cmd in enumerate(QUICK_CMDS):
    with qc_cols[i]:
        if st.button(
            cmd["short"],
            key=cmd["key"],
            help=cmd["label"],
            width="stretch",
        ):
            queue_burst(cmd["attack"], cmd["count"])
            st.rerun()
        st.markdown(
            f'<div style="font-size:0.62rem; color:#333; margin-top:-0.6rem; '
            f'padding-bottom:0.3rem; text-align:center;">{cmd["desc"]}</div>',
            unsafe_allow_html=True,
        )

# ── Launch All / Kill All ─────────────────────────────────────────────────
st.markdown('<div style="margin-top:0.5rem;"></div>', unsafe_allow_html=True)

btn_l, btn_r = st.columns(2)
with btn_l:
    if st.button(
        "⚡  LAUNCH ALL ATTACKS",
        type="primary",
        key="launch_all",
        width="stretch",
    ):
        set_all_attacks(True)
        st.rerun()
with btn_r:
    if st.button(
        "✕  KILL ALL",
        type="secondary",
        key="kill_all",
        width="stretch",
    ):
        stop_all()
        st.rerun()

if active_count > 0:
    st.markdown(
        f"""<div style="text-align:center; margin:0.4rem 0 0.2rem;">
        <span style="font-family:'JetBrains Mono',monospace; font-size:0.78rem;
        color:#ff0000; animation: pulse-badge 1.2s ease-in-out infinite;">
        ⚠ {active_count} ATTACK{'S' if active_count != 1 else ''} RUNNING
        </span></div>""",
        unsafe_allow_html=True,
    )

# ── Live Terminal ─────────────────────────────────────────────────────────
st.markdown('<div style="margin-top:0.8rem;"></div>', unsafe_allow_html=True)
st.markdown("#### > LIVE TERMINAL")

now = datetime.datetime.now()


def ts():
    """Generate a realistic timestamp string."""
    offset = random.uniform(0, 1.4)
    t = now - datetime.timedelta(seconds=offset)
    return t.strftime("%H:%M:%S.") + f"{random.randint(0, 999):03d}"


def rand_ip():
    return (
        f"{random.choice([10, 172, 192])}."
        f"{random.randint(0, 255)}."
        f"{random.randint(0, 255)}."
        f"{random.randint(1, 254)}"
    )


FLAGS_MAP = {
    "ddos": ["SYN", "SYN", "SYN", "SYN", "RST"],
    "portscan": ["SYN", "SYN→ACK", "RST", "filtered", "closed"],
    "ssh": ["PSH·ACK", "ACK", "PSH·ACK", "FIN·ACK"],
    "ftp": ["PSH·ACK", "ACK", "PSH·ACK", "RST"],
}

STATUS_MAP = {
    "ddos": ["sent", "sent", "sent", "dropped", "retransmit"],
    "portscan": ["open", "closed", "filtered", "open", "closed"],
    "ssh": ["AUTH_FAIL", "AUTH_FAIL", "AUTH_FAIL", "TIMEOUT", "CONNECTED"],
    "ftp": ["530 Login incorrect", "530 Login incorrect", "TIMEOUT", "331 Password required"],
}

if active_count > 0:
    lines = []
    lines.append(
        f'<div class="t-line t-dim">{ts()} root@kali:~# ./attack_suite '
        f"--target {target_ip} --threads 4</div>"
    )
    lines.append(
        f'<div class="t-line t-yellow">{ts()} [*] Framework initialized. '
        f"Loading {active_count} attack module(s)...</div>"
    )
    lines.append(
        f'<div class="t-line t-cyan">{ts()} [*] Target: {target_ip} '
        f"| Packet burst: {pkt_choice}</div>"
    )

    # Module load lines
    for atk_key, info in ATTACK_INFO.items():
        if attacks.get(atk_key, False):
            lines.append(
                f'<div class="t-line t-red">{ts()} [!] MODULE LOADED: '
                f'{info["name"]} → {target_ip}:{info["port"]}</div>'
            )

    lines.append(f'<div class="t-line t-dim">{ts()} {"─" * 60}</div>')

    # Generate packet-by-packet output
    for _ in range(random.randint(10, 18)):
        active_keys = [k for k, v in attacks.items() if v]
        atk = random.choice(active_keys)
        info = ATTACK_INFO[atk]

        src_ip = rand_ip()
        src_port = random.randint(1024, 65535)
        dst_port = (
            random.randint(1, 1024)
            if atk == "portscan"
            else int(info["port"].split("-")[0])
        )
        flag = random.choice(FLAGS_MAP[atk])
        status = random.choice(STATUS_MAP[atk])
        pkt_size = random.randint(40, 1500)

        color = "t-green"
        if status in (
            "dropped", "AUTH_FAIL", "530 Login incorrect",
            "TIMEOUT", "filtered", "closed",
        ):
            color = "t-red"
        elif status in ("retransmit",):
            color = "t-yellow"

        line = (
            f'<span class="t-time">{ts()}</span> '
            f'<span class="t-white">{src_ip}:{src_port}</span>'
            f'<span class="t-dim"> → </span>'
            f'<span class="t-white">{target_ip}:{dst_port}</span> '
            f'<span class="t-cyan">[{flag}]</span> '
            f'<span class="t-dim">{pkt_size}B</span> '
            f'<span class="{color}">{status}</span>'
        )
        lines.append(f'<div class="t-line">{line}</div>')

    lines.append(f'<div class="t-line t-dim">{ts()} {"─" * 60}</div>')

    # Summary
    total_pkts = random.randint(2000, 25000)
    drop_rate = random.uniform(1.5, 12.0)
    lines.append(
        f'<div class="t-line t-yellow">{ts()} [*] Burst complete: '
        f"{total_pkts:,} pkts | drop rate: {drop_rate:.1f}% | "
        f"active modules: {active_count}</div>"
    )
    lines.append(
        f'<div class="t-line t-prompt">{ts()} root@kali:~# _</div>'
    )

    terminal_content = "\n".join(lines)

    st.markdown(
        f"""<div class="terminal-box">
        <div class="terminal-bar">
            <span class="dot r"></span>
            <span class="dot y"></span>
            <span class="dot g"></span>
            <span class="title">attack_suite — {target_ip} — {active_count} module(s)</span>
        </div>
        <div class="terminal-body">{terminal_content}</div>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown("")
    st.info(
        "Open the **Live Monitor** page in another tab to see these attacks detected in real-time.",
        icon="📡",
    )

    # Auto-refresh while attacks are running
    time.sleep(1.5)
    st.rerun()

else:
    idle_lines = [
        f'<div class="t-line t-dim">{ts()} root@kali:~# _</div>',
        f'<div class="t-line t-dim">{ts()} # Waiting for commands...</div>',
        f'<div class="t-line t-dim">{ts()} # Select an attack or run a quick command above.</div>',
    ]
    st.markdown(
        f"""<div class="terminal-box">
        <div class="terminal-bar">
            <span class="dot r"></span>
            <span class="dot y"></span>
            <span class="dot g"></span>
            <span class="title">attack_suite — idle</span>
        </div>
        <div class="terminal-body">{"".join(idle_lines)}</div>
        </div>""",
        unsafe_allow_html=True,
    )
