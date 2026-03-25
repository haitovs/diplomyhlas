"""
📡 Live Monitor Page
Real-time network traffic analysis dashboard.
Reads traffic from the Traffic Simulator and Attacker Console via shared state,
runs ML predictions, and displays results with blocking capability.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import joblib
import random
import sys
from pathlib import Path
from datetime import datetime, timedelta
import time

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.inference.realtime import RealtimePredictor
from dashboard.theme import inject_theme, inject_sidebar_brand, COLORS, apply_chart_theme
from dashboard.components import page_header, init_shared_state, append_detections
from dashboard.demo_state import read_state, any_active, pop_bursts
from dashboard.i18n import t

st.set_page_config(page_title="Live Monitor", page_icon="📡", layout="wide")
inject_theme()
inject_sidebar_brand()
init_shared_state()

# ── Paths & Data ─────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent.parent
SAMPLES_DIR = PROJECT_ROOT / "data" / "samples"
BENIGN_FILE = SAMPLES_DIR / "benign_flows.csv"
MALICIOUS_FILE = SAMPLES_DIR / "malicious_flows.csv"

# ── Session state ────────────────────────────────────────────────────────
if 'predictor' not in st.session_state:
    st.session_state.predictor = RealtimePredictor()
if 'feature_columns' not in st.session_state:
    try:
        st.session_state.feature_columns = list(
            joblib.load(PROJECT_ROOT / "models" / "feature_columns.joblib")
        )
    except Exception:
        st.session_state.feature_columns = []
if 'history_df' not in st.session_state:
    st.session_state.history_df = pd.DataFrame()
if 'total_processed' not in st.session_state:
    st.session_state.total_processed = 0
if 'blocked_ips' not in st.session_state:
    st.session_state.blocked_ips = set()
if 'benign_data' not in st.session_state:
    try:
        st.session_state.benign_data = pd.read_csv(BENIGN_FILE)
    except Exception:
        st.session_state.benign_data = pd.DataFrame()
if 'malicious_data' not in st.session_state:
    try:
        st.session_state.malicious_data = pd.read_csv(MALICIOUS_FILE)
    except Exception:
        st.session_state.malicious_data = pd.DataFrame()
if 'benign_idx' not in st.session_state:
    st.session_state.benign_idx = 0
if 'malicious_idx' not in st.session_state:
    st.session_state.malicious_idx = 0

# Attack type → label mapping for filtering malicious flows
ATTACK_LABEL_MAP = {
    "ddos": ["DDoS"],
    "portscan": ["PortScan"],
    "ssh": ["SSH-Patator"],
    "ftp": ["FTP-Patator"],
}


# ── IP Blocking ──────────────────────────────────────────────────────────

def block_ip(ip: str):
    st.session_state.blocked_ips.add(ip)

def unblock_ip(ip: str):
    st.session_state.blocked_ips.discard(ip)

def is_blocked(ip: str) -> bool:
    return ip in st.session_state.blocked_ips


# ── Flow Ingestion ───────────────────────────────────────────────────────

def ingest_flow(row: pd.Series, source: str):
    """Run ML prediction on one CSV row and add to history."""
    feature_cols = st.session_state.feature_columns
    predictor = st.session_state.predictor
    threshold = st.session_state.settings.get('confidence_threshold', 0.70)
    blocked = st.session_state.blocked_ips

    src_ip = row.get('_src_ip', 'N/A')
    if src_ip in blocked:
        return None

    flow = {col: float(row.get(col, 0)) for col in feature_cols}
    result = predictor.predict(flow)

    entry = {
        'timestamp': datetime.now(),
        'src_ip': src_ip,
        'dst_ip': row.get('_dst_ip', 'N/A'),
        'src_port': int(random.randint(1024, 65535)),
        'dst_port': int(row.get('_dst_port', 0)),
        'protocol': row.get('_protocol', 'TCP'),
        'ml_prediction': result['prediction'],
        'ml_confidence': result['confidence'],
        'ml_is_anomaly': result['is_anomaly'] and result['confidence'] >= threshold,
        'total_packets': int(flow.get('Total Fwd Packets', 0) + flow.get('Total Backward Packets', 0)),
        'total_bytes': int(flow.get('Total Length of Fwd Packets', 0) + flow.get('Total Length of Bwd Packets', 0)),
        'flow_duration': flow.get('Flow Duration', 0),
        'flow_bytes_per_s': flow.get('Flow Bytes/s', 0),
    }

    # Add to history
    new_row = pd.DataFrame([entry])
    st.session_state.history_df = pd.concat(
        [st.session_state.history_df, new_row], ignore_index=True
    )
    if len(st.session_state.history_df) > 2000:
        st.session_state.history_df = st.session_state.history_df.tail(2000)
    st.session_state.total_processed += 1
    st.session_state.session_metrics['total_flows'] += 1

    if entry['ml_is_anomaly']:
        append_detections([{
            'prediction': entry['ml_prediction'],
            'confidence': entry['ml_confidence'],
            'is_anomaly': True,
            'src_ip': entry['src_ip'],
            'dst_ip': entry['dst_ip'],
            'dst_port': entry['dst_port'],
            'timestamp': entry['timestamp'],
        }], source=source)

    return entry


def process_demo_tick():
    """Called each refresh — reads shared state and ingests appropriate flows."""
    demo = read_state()
    benign_df = st.session_state.benign_data
    malicious_df = st.session_state.malicious_data

    # Ingest benign flows if simulator is active
    if demo["benign_active"] and len(benign_df) > 0:
        speed = max(1, int(demo.get("benign_speed", 1)))
        for _ in range(speed):
            idx = st.session_state.benign_idx % len(benign_df)
            ingest_flow(benign_df.iloc[idx], "Traffic Simulator")
            st.session_state.benign_idx += 1

    # Ingest attack flows for each active (continuous) attack
    active_attacks = demo.get("attacks", {})
    if len(malicious_df) > 0:
        for atk_key, is_on in active_attacks.items():
            if not is_on:
                continue
            labels = ATTACK_LABEL_MAP.get(atk_key, [])
            matching = malicious_df[malicious_df['_label'].isin(labels)]
            if len(matching) == 0:
                matching = malicious_df
            for _ in range(random.randint(2, 5)):
                row = matching.iloc[random.randint(0, len(matching) - 1)]
                ingest_flow(row, f"Attack: {atk_key.upper()}")

    # Process one-shot bursts (quick commands)
    bursts = pop_bursts()
    if len(malicious_df) > 0:
        for burst in bursts:
            atk_type = burst.get("type", "ddos")
            count = burst.get("count", 1)
            labels = ATTACK_LABEL_MAP.get(atk_type, [])
            matching = malicious_df[malicious_df['_label'].isin(labels)]
            if len(matching) == 0:
                matching = malicious_df
            for _ in range(count):
                row = matching.iloc[random.randint(0, len(matching) - 1)]
                ingest_flow(row, f"Burst: {atk_type.upper()}")


# ── Sidebar ──────────────────────────────────────────────────────────────

def create_sidebar():
    with st.sidebar:
        st.markdown(f"### ⚙️ {t('live.control_panel')}")

        # Show what's active from other tabs
        demo = read_state()
        benign_on = demo["benign_active"]
        attacks_on = {k: v for k, v in demo.get("attacks", {}).items() if v}

        if benign_on or attacks_on:
            st.markdown(f"""
            <div style="padding:0.5rem; border-radius:4px; background:rgba(245,158,11,0.06);
                 border:1px solid rgba(245,158,11,0.15); border-left:3px solid {COLORS['primary']};
                 margin-bottom:0.75rem; font-size:0.85rem;">
                <div style="color:{COLORS['primary']}; font-weight:700;">RECEIVING TRAFFIC</div>
            """, unsafe_allow_html=True)
            if benign_on:
                st.markdown(f'<div style="color:{COLORS["success"]}; font-size:0.8rem; font-family:JetBrains Mono,monospace;">✅ Benign traffic active</div>', unsafe_allow_html=True)
            for atk_name in attacks_on:
                st.markdown(f'<div style="color:{COLORS["danger"]}; font-size:0.8rem; font-family:JetBrains Mono,monospace;">🚨 {atk_name.upper()} attack active</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Open Traffic Simulator or Attacker Console in another tab to start sending traffic.", icon="💡")

        if st.button(f"🗑️ {t('live.clear_history')}", width="stretch"):
            st.session_state.history_df = pd.DataFrame()
            st.session_state.total_processed = 0
            st.rerun()

        st.markdown('<hr style="border:none; border-top:1px solid rgba(245,158,11,0.08); margin:0.5rem 0;">', unsafe_allow_html=True)

        # ── Model info ──────────────────────────────────
        st.markdown(f"### 🧠 {t('live.model_info')}")
        model_info = st.session_state.predictor.get_model_info()
        if model_info['loaded']:
            st.success(f"{model_info['model_type']} — {model_info['n_features']} features", icon="✅")
        else:
            st.error(t('live.model_not_loaded'), icon="❌")

        # ── Blocked IPs ──────────────────────────────────
        if st.session_state.blocked_ips:
            st.markdown('<hr style="border:none; border-top:1px solid rgba(245,158,11,0.08); margin:0.5rem 0;">', unsafe_allow_html=True)
            st.markdown(f"### 🚫 {t('live.blocked_ips')} ({len(st.session_state.blocked_ips)})")
            for blocked_ip in list(st.session_state.blocked_ips):
                col_ip, col_unblock = st.columns([3, 1])
                with col_ip:
                    st.markdown(f'<span style="color:{COLORS["danger"]}; font-family:JetBrains Mono,monospace; font-size:0.8rem;">{blocked_ip}</span>', unsafe_allow_html=True)
                with col_unblock:
                    if st.button("✕", key=f"unblock_{blocked_ip}"):
                        unblock_ip(blocked_ip)
                        st.rerun()

        st.markdown('<hr style="border:none; border-top:1px solid rgba(245,158,11,0.08); margin:0.5rem 0;">', unsafe_allow_html=True)
        st.markdown(f"### 🔧 {t('live.parameters')}")
        refresh_rate = st.selectbox(t('live.refresh_rate'), ["1s", "2s", "3s", "5s"], index=0)

        return refresh_rate


# ── Visualization ────────────────────────────────────────────────────────

def render_top_metrics(df):
    has_data = len(df) > 0 and 'ml_is_anomaly' in df.columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(t('live.total_flows'), f"{st.session_state.total_processed:,}")
    with col2:
        anomalies = int(df['ml_is_anomaly'].sum()) if has_data else 0
        pct = (anomalies / len(df) * 100) if has_data and len(df) > 0 else 0
        st.metric(t('live.threats_detected'), f"{anomalies}", f"{pct:.1f}%", delta_color="inverse")
    with col3:
        conf = df['ml_confidence'].mean() * 100 if has_data else 0
        st.metric(t('live.avg_confidence'), f"{conf:.1f}%")
    with col4:
        blocked_count = len(st.session_state.blocked_ips)
        st.metric(t('live.blocked_ips'), f"{blocked_count}")


def render_traffic_timeline(df):
    """Large traffic timeline chart."""
    st.markdown(f"#### {t('live.traffic_timeline')}")

    if len(df) == 0 or 'ml_is_anomaly' not in df.columns:
        st.info(t('live.waiting_for_data'))
        return

    df_sorted = df.sort_values('timestamp')
    df_sorted['sec'] = pd.to_datetime(df_sorted['timestamp']).dt.floor('1s')

    agg = df_sorted.groupby('sec').agg(
        benign=('ml_is_anomaly', lambda x: (~x).sum()),
        threats=('ml_is_anomaly', 'sum'),
        total=('ml_is_anomaly', 'count'),
    ).reset_index()

    fig = go.Figure()

    # Benign traffic (green area)
    fig.add_trace(go.Scatter(
        x=agg['sec'], y=agg['benign'], name="Benign",
        fill='tozeroy',
        line=dict(color=COLORS['success'], width=2),
        fillcolor="rgba(34,197,94,0.15)",
    ))

    # Threat traffic (red area, stacked)
    if agg['threats'].sum() > 0:
        fig.add_trace(go.Scatter(
            x=agg['sec'], y=agg['threats'], name="Threats",
            fill='tozeroy',
            line=dict(color=COLORS['danger'], width=2),
            fillcolor="rgba(239,68,68,0.2)",
        ))

    fig.update_layout(
        height=300,
        yaxis_title="Flows / sec",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLORS["text_main"], size=12),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(color=COLORS["text_muted"]), bgcolor="rgba(0,0,0,0)", borderwidth=0,
        ),
        xaxis=dict(gridcolor="rgba(245,158,11,0.06)", tickfont=dict(color=COLORS["text_muted"])),
        yaxis=dict(gridcolor="rgba(245,158,11,0.06)", tickfont=dict(color=COLORS["text_muted"])),
        margin=dict(l=40, r=10, t=10, b=30),
    )
    st.plotly_chart(fig, width="stretch")


def render_threat_gauge(df):
    has_data = len(df) > 0 and 'ml_is_anomaly' in df.columns
    threat_pct = df['ml_is_anomaly'].mean() * 100 if has_data and len(df) > 0 else 0

    if threat_pct > 30:
        bar_color = COLORS['danger']
    elif threat_pct > 10:
        bar_color = COLORS['warning']
    else:
        bar_color = COLORS['success']

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=threat_pct,
        number=dict(suffix="%", font=dict(color=COLORS['text_main'], size=36)),
        title=dict(text=t('live.threat_level'), font=dict(color=COLORS['text_muted'], size=14)),
        gauge=dict(
            axis=dict(range=[0, 100], tickfont=dict(color=COLORS['text_muted']), tickcolor=COLORS['text_muted']),
            bar=dict(color=bar_color),
            bgcolor="rgba(30,41,59,0.5)",
            borderwidth=0,
            steps=[
                dict(range=[0, 10], color="rgba(34,197,94,0.12)"),
                dict(range=[10, 30], color="rgba(245,158,11,0.12)"),
                dict(range=[30, 100], color="rgba(239,68,68,0.12)"),
            ],
        ),
    ))
    fig.update_layout(
        height=220, margin=dict(l=20, r=20, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLORS["text_main"]),
    )
    st.plotly_chart(fig, width="stretch")


def render_threat_distribution(df):
    st.markdown(f"#### {t('live.threat_distribution')}")
    if len(df) == 0 or 'ml_is_anomaly' not in df.columns:
        return

    anomalies_df = df[df['ml_is_anomaly']]
    if len(anomalies_df) > 0:
        counts = anomalies_df['ml_prediction'].value_counts()
        fig = go.Figure(data=[go.Pie(
            labels=counts.index, values=counts.values, hole=0.6,
            marker=dict(colors=[COLORS['danger'], COLORS['warning'], COLORS['accent'], COLORS['primary'], '#8b5cf6', '#ec4899']),
            textfont=dict(color=COLORS['text_main']),
        )])
        fig.update_layout(
            height=220, margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=COLORS["text_main"]),
            legend=dict(font=dict(color=COLORS["text_muted"]), bgcolor="rgba(0,0,0,0)", borderwidth=0),
        )
        st.plotly_chart(fig, width="stretch")
    else:
        st.markdown(f"""
            <div style="height:200px; display:flex; align-items:center; justify-content:center;
                 border:1px dashed rgba(245,158,11,0.15); border-radius:4px;">
                <span style="color:{COLORS['success']}; font-weight:700; font-family:'Space Grotesk',sans-serif; text-transform:uppercase; letter-spacing:0.04em;">{t('live.no_threats_detected')}</span>
            </div>
        """, unsafe_allow_html=True)


def render_network_stats(df):
    if len(df) == 0 or 'ml_is_anomaly' not in df.columns:
        return

    unique_src = df['src_ip'].nunique()
    unique_dst = df['dst_ip'].nunique()
    if 'dst_port' in df.columns and len(df) > 0 and not df['dst_port'].mode().empty:
        top_port = int(df['dst_port'].mode().iloc[0])
    else:
        top_port = "-"
    avg_bytes = df['flow_bytes_per_s'].mean() if 'flow_bytes_per_s' in df.columns else 0

    st.markdown(f"""
    <div style="display:flex; gap:1.5rem; flex-wrap:wrap; padding:0.75rem 1rem;
         background:{COLORS['bg_tertiary']}; border:1px solid rgba(245,158,11,0.10);
         border-left:3px solid {COLORS['primary']}; border-radius:4px; margin-bottom:1.5rem;">
        <span style="color:{COLORS['text_muted']}; font-size:0.8rem;">
            <strong style="color:{COLORS['primary']};">{unique_src}</strong> {t('live.source_ips')}
        </span>
        <span style="color:{COLORS['text_muted']}; font-size:0.8rem;">
            <strong style="color:{COLORS['primary']};">{unique_dst}</strong> {t('live.dest_ips')}
        </span>
        <span style="color:{COLORS['text_muted']}; font-size:0.8rem;">
            {t('live.top_port')}: <strong style="color:{COLORS['primary']};">{top_port}</strong>
        </span>
        <span style="color:{COLORS['text_muted']}; font-size:0.8rem;">
            {t('live.avg_throughput')}: <strong style="color:{COLORS['primary']};">{avg_bytes:,.0f} B/s</strong>
        </span>
    </div>
    """, unsafe_allow_html=True)


def render_packet_table(df):
    """Show the last 20 flows in a compact dataframe table."""
    st.markdown("#### Recent Flows")

    if len(df) == 0 or 'timestamp' not in df.columns:
        st.info("No flow data yet.")
        return

    recent = df.sort_values('timestamp', ascending=False).head(20)

    df_display = pd.DataFrame({
        "Time": recent['timestamp'].apply(lambda x: x.strftime('%H:%M:%S') if hasattr(x, 'strftime') else str(x)),
        "Src IP": recent['src_ip'],
        "Dst IP": recent['dst_ip'],
        "Port": recent['dst_port'].astype(int),
        "Protocol": recent['protocol'],
        "Prediction": recent['ml_prediction'],
        "Confidence": recent['ml_confidence'].apply(lambda x: f"{x * 100:.1f}%"),
    }).reset_index(drop=True)

    st.dataframe(df_display, height=300, hide_index=True)


def render_recent_alerts(df):
    st.markdown(f"#### {t('live.recent_threats')}")

    if len(df) == 0 or 'ml_is_anomaly' not in df.columns:
        st.markdown(f"""
            <div style="padding:1rem; border-radius:4px; background:rgba(34,197,94,0.08);
                 color:{COLORS['success']}; border:1px solid rgba(34,197,94,0.2);
                 border-left:3px solid {COLORS['success']};">
                ✅ {t('live.system_secure_no_data')}
            </div>
        """, unsafe_allow_html=True)
        return

    anomalies = df[df['ml_is_anomaly']].tail(10)

    if len(anomalies) == 0:
        st.markdown(f"""
            <div style="padding:1rem; border-radius:4px; background:rgba(34,197,94,0.08);
                 color:{COLORS['success']}; border:1px solid rgba(34,197,94,0.2);
                 border-left:3px solid {COLORS['success']};">
                ✅ {t('live.system_secure_no_threats')}
            </div>
        """, unsafe_allow_html=True)
        return

    for idx, row in anomalies.iterrows():
        conf = row['ml_confidence'] * 100
        if conf > 90:
            sev_color = COLORS['danger']
        elif conf > 80:
            sev_color = COLORS['warning']
        else:
            sev_color = COLORS['info']

        ts = row.get('timestamp', '')
        ts_str = ts.strftime('%H:%M:%S') if hasattr(ts, 'strftime') else str(ts)
        src_ip = row.get('src_ip', 'N/A')
        dst_ip = row.get('dst_ip', 'N/A')
        dst_port = row.get('dst_port', '')
        prediction = row['ml_prediction']
        already_blocked = is_blocked(src_ip)

        col_info, col_action = st.columns([6, 1])
        with col_info:
            line = (
                f'<div style="padding:4px 10px; border-left:3px solid {sev_color}; '
                f'background:rgba(239,68,68,0.04); border-radius:2px; '
                f'font-size:0.82rem; line-height:1.6; max-height:40px; overflow:hidden;">'
                f'<strong style="color:{COLORS["text_main"]};">{prediction}</strong> '
                f'<span style="color:{COLORS["text_muted"]}; font-family:JetBrains Mono,monospace; font-size:0.78rem;">'
                f'{src_ip} &rarr; {dst_ip}:{dst_port}</span> '
                f'<span style="color:{COLORS["text_muted"]}; font-size:0.72rem; margin-left:0.5rem;">{ts_str}</span> '
                f'<span style="color:{COLORS["primary"]}; font-family:JetBrains Mono,monospace; font-weight:700; margin-left:0.5rem;">{conf:.1f}%</span>'
                f'</div>'
            )
            st.markdown(line, unsafe_allow_html=True)
        with col_action:
            if already_blocked:
                st.markdown(
                    f'<div style="text-align:center; color:{COLORS["danger"]}; '
                    f'font-size:0.7rem; font-weight:700; padding-top:6px;">BLOCKED</div>',
                    unsafe_allow_html=True,
                )
            elif src_ip != 'N/A':
                if st.button(f"🚫 {t('live.block')}", key=f"block_{idx}_{src_ip}", width="stretch"):
                    block_ip(src_ip)
                    st.rerun()


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    page_header("📡", t('live.page_title'), t('live.page_subtitle'))

    demo = read_state()
    is_receiving = any_active()

    if is_receiving:
        st.markdown(f"""
            <div class="pulse-container" style="margin-bottom: 1.5rem;">
                <div class="pulse-dot"></div>
                <span style="font-size: 0.85rem; font-weight: 600; color:{COLORS['success']}">{t('live.live_packet_capture_mode')}</span>
            </div>
        """, unsafe_allow_html=True)
        process_demo_tick()
    else:
        if st.session_state.total_processed == 0:
            st.info(t('live.system_paused'))

    refresh_rate = create_sidebar()
    display_df = st.session_state.history_df.tail(500)

    # Top metrics
    render_top_metrics(display_df)
    render_network_stats(display_df)

    # Packet data table
    render_packet_table(display_df)

    # Big traffic timeline
    render_traffic_timeline(display_df)

    # Gauge + Pie side by side
    col_gauge, col_pie = st.columns([1, 1])
    with col_gauge:
        st.markdown(f"#### {t('live.system_health')}")
        render_threat_gauge(display_df)
    with col_pie:
        render_threat_distribution(display_df)

    st.markdown('<div class="card-gap"></div>', unsafe_allow_html=True)
    render_recent_alerts(display_df)

    # Auto-refresh when traffic is active
    if is_receiving:
        seconds = int(refresh_rate.replace('s', ''))
        time.sleep(seconds)
        st.rerun()


if __name__ == "__main__":
    main()
