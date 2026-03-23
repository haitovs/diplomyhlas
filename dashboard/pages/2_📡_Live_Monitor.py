"""
📡 Live Monitor Page
Analyze network traffic files with ML-based anomaly detection.
Load benign or malicious traffic → ML model classifies each flow → Block threats.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import joblib
import sys
from pathlib import Path
from datetime import datetime, timedelta
import time

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.inference.realtime import RealtimePredictor
from dashboard.theme import inject_theme, inject_sidebar_brand, COLORS, apply_chart_theme
from dashboard.components import page_header, init_shared_state, append_detections
from dashboard.i18n import t

st.set_page_config(page_title="Live Monitor", page_icon="📡", layout="wide")
inject_theme()
inject_sidebar_brand()
init_shared_state()

# ── Paths ─────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent.parent
SAMPLES_DIR = PROJECT_ROOT / "data" / "samples"
BENIGN_FILE = SAMPLES_DIR / "benign_flows.csv"
MALICIOUS_FILE = SAMPLES_DIR / "malicious_flows.csv"

# ── Session state init ────────────────────────────────────────────────────
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
if 'is_monitoring' not in st.session_state:
    st.session_state.is_monitoring = False
if 'capture_obj' not in st.session_state:
    st.session_state.capture_obj = None
if 'aggregator' not in st.session_state:
    st.session_state.aggregator = None


# ── IP Blocking ──────────────────────────────────────────────────────────

def block_ip(ip: str):
    st.session_state.blocked_ips.add(ip)


def unblock_ip(ip: str):
    st.session_state.blocked_ips.discard(ip)


def is_blocked(ip: str) -> bool:
    return ip in st.session_state.blocked_ips


# ── Load & Predict from CSV ──────────────────────────────────────────────

def load_and_predict(csv_path: Path, source_label: str):
    """Load a CSV with 74 CICIDS2017 features, run ML predictions, add to history."""
    df = pd.read_csv(csv_path)
    feature_cols = st.session_state.feature_columns
    predictor = st.session_state.predictor
    threshold = st.session_state.settings.get('confidence_threshold', 0.70)
    blocked = st.session_state.blocked_ips

    rows = []
    anomaly_dets = []

    for _, row in df.iterrows():
        src_ip = row.get('_src_ip', 'N/A')

        # Skip blocked IPs
        if src_ip in blocked:
            continue

        # Build flow dict from CICIDS2017 feature columns
        flow = {col: float(row.get(col, 0)) for col in feature_cols}

        result = predictor.predict(flow)

        entry = {
            'timestamp': datetime.now() + timedelta(milliseconds=len(rows) * 50),
            'src_ip': src_ip,
            'dst_ip': row.get('_dst_ip', 'N/A'),
            'src_port': int(np.random.randint(1024, 65535)),
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
        rows.append(entry)

        if entry['ml_is_anomaly']:
            anomaly_dets.append({
                'prediction': entry['ml_prediction'],
                'confidence': entry['ml_confidence'],
                'is_anomaly': True,
                'src_ip': entry['src_ip'],
                'dst_ip': entry['dst_ip'],
                'dst_port': entry['dst_port'],
                'timestamp': entry['timestamp'],
            })

    if rows:
        new_data = pd.DataFrame(rows)
        st.session_state.total_processed += len(new_data)
        st.session_state.history_df = pd.concat(
            [st.session_state.history_df, new_data], ignore_index=True
        )
        if len(st.session_state.history_df) > 2000:
            st.session_state.history_df = st.session_state.history_df.tail(2000)

        if anomaly_dets:
            append_detections(anomaly_dets, source=source_label)

        st.session_state.session_metrics['total_flows'] += len(new_data)

    return len(rows), len(anomaly_dets)


# ── Live Capture ─────────────────────────────────────────────────────────

def start_capture(interface: str):
    """Start packet capture with FlowAggregator."""
    try:
        from src.capture.network_capture import PacketCapture
        from src.capture.flow_aggregator import FlowAggregator

        aggregator = FlowAggregator()
        capture = PacketCapture(interface=interface, packet_processor=aggregator.add_packet)
        capture.start()
        st.session_state.capture_obj = capture
        st.session_state.aggregator = aggregator
    except Exception as e:
        st.error(t('live.capture_failed', error=str(e)))
        st.session_state.is_monitoring = False


def stop_capture():
    """Stop capture and flush remaining flows."""
    st.session_state.is_monitoring = False
    if st.session_state.capture_obj:
        st.session_state.capture_obj.stop()
    if st.session_state.aggregator:
        remaining = st.session_state.aggregator.flush_all()
        if remaining:
            _process_live_flows(remaining)
    st.session_state.capture_obj = None
    st.session_state.aggregator = None


def _process_live_flows(flows: list):
    """Run ML prediction on live-captured flows."""
    if not flows:
        return
    threshold = st.session_state.settings.get('confidence_threshold', 0.70)
    predictor = st.session_state.predictor
    blocked = st.session_state.blocked_ips

    rows = []
    anomaly_dets = []

    for flow in flows:
        meta = flow.pop('_meta', {})
        src_ip = meta.get('src_ip', 'N/A')
        if src_ip in blocked:
            continue
        result = predictor.predict(flow)
        row = {
            'timestamp': meta.get('timestamp', datetime.now()),
            'src_ip': src_ip,
            'dst_ip': meta.get('dst_ip', 'N/A'),
            'src_port': meta.get('src_port', 0),
            'dst_port': meta.get('dst_port', 0),
            'protocol': meta.get('protocol', 'OTHER'),
            'ml_prediction': result['prediction'],
            'ml_confidence': result['confidence'],
            'ml_is_anomaly': result['is_anomaly'] and result['confidence'] >= threshold,
            'total_packets': flow.get('Total Fwd Packets', 0) + flow.get('Total Backward Packets', 0),
            'total_bytes': flow.get('Total Length of Fwd Packets', 0) + flow.get('Total Length of Bwd Packets', 0),
            'flow_duration': flow.get('Flow Duration', 0),
            'flow_bytes_per_s': flow.get('Flow Bytes/s', 0),
        }
        rows.append(row)
        if row['ml_is_anomaly']:
            anomaly_dets.append({
                'prediction': row['ml_prediction'],
                'confidence': row['ml_confidence'],
                'is_anomaly': True,
                'src_ip': row['src_ip'],
                'dst_ip': row['dst_ip'],
                'dst_port': row['dst_port'],
                'timestamp': row['timestamp'],
            })

    if rows:
        new_data = pd.DataFrame(rows)
        st.session_state.total_processed += len(new_data)
        st.session_state.history_df = pd.concat(
            [st.session_state.history_df, new_data], ignore_index=True
        )
        if len(st.session_state.history_df) > 2000:
            st.session_state.history_df = st.session_state.history_df.tail(2000)
        if anomaly_dets:
            append_detections(anomaly_dets, source="Live Capture")
        st.session_state.session_metrics['total_flows'] += len(new_data)


def process_live_data():
    """Drain FlowAggregator for finished flows."""
    if not st.session_state.aggregator:
        return
    flows = st.session_state.aggregator.flush()
    _process_live_flows(flows)


# ── Sidebar ──────────────────────────────────────────────────────────────

def create_sidebar():
    with st.sidebar:
        # ── Traffic Loading ──────────────────────────────────────
        st.markdown(f"### 📂 {t('live.load_traffic')}")

        if st.button(f"✅ {t('live.load_benign')}", use_container_width=True, type="secondary", key="btn_benign"):
            n_flows, n_threats = load_and_predict(BENIGN_FILE, "Benign File")
            st.session_state['_last_load'] = f"Loaded {n_flows} benign flows"
            st.rerun()

        if st.button(f"☠️ {t('live.load_malicious')}", use_container_width=True, type="primary", key="btn_malicious"):
            n_flows, n_threats = load_and_predict(MALICIOUS_FILE, "Malicious File")
            st.session_state['_last_load'] = f"Loaded {n_flows} flows, {n_threats} threats detected!"
            st.rerun()

        # Show last load result
        if '_last_load' in st.session_state:
            msg = st.session_state['_last_load']
            if 'threat' in msg.lower():
                st.error(msg, icon="🚨")
            else:
                st.success(msg, icon="✅")

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        # ── Clear ──────────────────────────────────────
        if st.button(f"🗑️ {t('live.clear_history')}", use_container_width=True):
            st.session_state.history_df = pd.DataFrame()
            st.session_state.total_processed = 0
            st.session_state.pop('_last_load', None)
            st.rerun()

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        # ── Live Capture (Advanced) ──────────────────────────────
        with st.expander(f"🔌 {t('live.live_capture_advanced')}", expanded=False):
            st.info(t('live.sudo_required'), icon="🔒")

            try:
                from src.capture.network_capture import get_available_interfaces
                ifaces = get_available_interfaces()
                iface_names = [f"{i.name} ({i.ip})" for i in ifaces]
                iface_map = {f"{i.name} ({i.ip})": i.name for i in ifaces}
                default_idx = 0
                for idx, name in enumerate(iface_names):
                    if 'lo0' in name or 'loopback' in name.lower():
                        default_idx = idx
                        break
                selected_iface_name = st.selectbox(
                    t('live.interface'), iface_names, index=default_idx
                )
                selected_iface = iface_map[selected_iface_name]
            except ImportError:
                st.error(t('live.scapy_not_available'))
                selected_iface = "lo0"

            if not st.session_state.is_monitoring:
                if st.button(f"▶️ {t('live.start_monitoring')}", type="primary", use_container_width=True):
                    st.session_state.is_monitoring = True
                    start_capture(selected_iface)
                    st.rerun()
            else:
                if st.button(f"⏹️ {t('live.stop_monitoring')}", type="secondary", use_container_width=True):
                    stop_capture()
                    st.rerun()

            if st.session_state.capture_obj and st.session_state.capture_obj.running:
                stats = st.session_state.capture_obj.get_stats()
                flow_count = st.session_state.aggregator.active_flow_count() if st.session_state.aggregator else 0
                st.markdown(f"""
                <div style="padding:0.5rem; border-radius:4px; background:rgba(245,158,11,0.06);
                     border:1px solid rgba(245,158,11,0.15); border-left:3px solid {COLORS['primary']};
                     margin-top:0.5rem; font-size:0.85rem;">
                    <div style="color:{COLORS['primary']}; font-weight:700;">{t('live.capturing_on', interface=stats['interface'])}</div>
                    <div style="color:{COLORS['text_muted']}; font-family:'JetBrains Mono',monospace;">{t('live.packets_count', count=stats['packet_count'], rate=f"{stats['packets_per_second']:.1f}")}</div>
                    <div style="color:{COLORS['text_muted']}; font-family:'JetBrains Mono',monospace;">{t('live.active_flows', count=flow_count)}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        # ── Model info ──────────────────────────────────────
        st.markdown(f"### 🧠 {t('live.model_info')}")
        model_info = st.session_state.predictor.get_model_info()
        if model_info['loaded']:
            st.success(f"{model_info['model_type']} — {model_info['n_features']} features", icon="✅")
        else:
            st.error(t('live.model_not_loaded'), icon="❌")

        # ── Blocked IPs ──────────────────────────────────────
        if st.session_state.blocked_ips:
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            st.markdown(f"### 🚫 {t('live.blocked_ips')}")
            for blocked_ip in list(st.session_state.blocked_ips):
                col_ip, col_unblock = st.columns([3, 1])
                with col_ip:
                    st.markdown(f'<span style="color:{COLORS["danger"]}; font-family:JetBrains Mono,monospace; font-size:0.8rem;">{blocked_ip}</span>', unsafe_allow_html=True)
                with col_unblock:
                    if st.button("✕", key=f"unblock_{blocked_ip}"):
                        unblock_ip(blocked_ip)
                        st.rerun()

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown(f"### 🔧 {t('live.parameters')}")
        refresh_rate = st.selectbox(t('live.refresh_rate'), [t('live.manual'), "1s", "3s", "5s"], index=0)

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
    apply_chart_theme(fig)
    fig.update_layout(height=220, margin=dict(l=20, r=20, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)


def render_charts(df):
    if len(df) == 0 or 'ml_is_anomaly' not in df.columns:
        st.info(t('live.waiting_for_data'))
        return

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown(f"#### {t('live.traffic_timeline')}")
        df_sorted = df.sort_values('timestamp')
        df_sorted['sec'] = pd.to_datetime(df_sorted['timestamp']).dt.floor('1s')
        agg = df_sorted.groupby('sec').agg(
            threats=('ml_is_anomaly', 'sum'),
            total=('ml_is_anomaly', 'count')
        ).reset_index()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=agg['sec'], y=agg['total'], name=t('common.total'), fill='tozeroy',
            line=dict(color=COLORS['primary']), fillcolor="rgba(245,158,11,0.12)"
        ))

        anomalies = agg[agg['threats'] > 0]
        if len(anomalies) > 0:
            fig.add_trace(go.Scatter(
                x=anomalies['sec'], y=anomalies['total'], mode='markers', name=t('common.threats'),
                marker=dict(color=COLORS['danger'], size=10, symbol='circle')
            ))

        apply_chart_theme(fig)
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown(f"#### {t('live.threat_distribution')}")
        anomalies_df = df[df['ml_is_anomaly']]
        if len(anomalies_df) > 0:
            counts = anomalies_df['ml_prediction'].value_counts()
            fig = go.Figure(data=[go.Pie(
                labels=counts.index, values=counts.values, hole=0.6,
                marker=dict(colors=[COLORS['danger'], COLORS['warning'], COLORS['accent'], COLORS['primary']]),
                textfont=dict(color=COLORS['text_main']),
            )])
            apply_chart_theme(fig)
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown(f"""
                <div style="height:250px; display:flex; align-items:center; justify-content:center;
                     border:1px dashed rgba(245,158,11,0.15); border-radius:4px;">
                    <span style="color:{COLORS['success']}; font-weight:700; font-family:'Space Grotesk',sans-serif; text-transform:uppercase; letter-spacing:0.04em;">{t('live.no_threats_detected')}</span>
                </div>
            """, unsafe_allow_html=True)


def render_network_stats(df):
    if len(df) == 0 or 'ml_is_anomaly' not in df.columns:
        return

    unique_src = df['src_ip'].nunique() if 'src_ip' in df.columns else 0
    unique_dst = df['dst_ip'].nunique() if 'dst_ip' in df.columns else 0
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
        already_blocked = is_blocked(src_ip)

        col_alert, col_block = st.columns([5, 1])
        with col_alert:
            blocked_badge = ""
            if already_blocked:
                blocked_badge = f'<span style="background:rgba(239,68,68,0.15); color:{COLORS["danger"]}; padding:2px 8px; border-radius:2px; font-size:0.7rem; font-weight:700; margin-left:0.5rem;">BLOCKED</span>'

            st.markdown(f"""
                <div style="padding:0.75rem 1rem; border-radius:4px; background:rgba(239,68,68,0.06);
                     border-left:3px solid {sev_color}; margin-bottom:0.5rem;
                     display:flex; justify-content:space-between; align-items:center;">
                    <div style="display:flex; align-items:center; gap:0.75rem;">
                        <strong style="color:{COLORS['text_main']};">{row['ml_prediction']}</strong>
                        <span style="color:{COLORS['text_muted']}; font-size:0.85rem; font-family:'JetBrains Mono',monospace;">
                            {src_ip} → {row.get('dst_ip','N/A')}:{row.get('dst_port','')}
                        </span>
                        {blocked_badge}
                    </div>
                    <div style="display:flex; align-items:center; gap:1rem;">
                        <span style="color:{COLORS['text_muted']}; font-size:0.75rem; font-family:'JetBrains Mono',monospace;">{ts_str}</span>
                        <span style="color:{COLORS['primary']}; font-family:'JetBrains Mono',monospace; font-weight:700;">{conf:.1f}%</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        with col_block:
            if not already_blocked and src_ip != 'N/A':
                if st.button(f"🚫 {t('live.block')}", key=f"block_{idx}_{src_ip}", use_container_width=True):
                    block_ip(src_ip)
                    st.rerun()
            elif already_blocked:
                st.markdown(f'<div style="text-align:center; padding-top:0.5rem; color:{COLORS["danger"]}; font-size:0.75rem; font-weight:700;">🚫</div>', unsafe_allow_html=True)


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    page_header("📡", t('live.page_title'), t('live.page_subtitle'))

    if st.session_state.is_monitoring:
        st.markdown(f"""
            <div class="pulse-container" style="margin-bottom: 1.5rem;">
                <div class="pulse-dot"></div>
                <span style="font-size: 0.85rem; font-weight: 600; color:{COLORS['success']}">{t('live.live_packet_capture_mode')}</span>
            </div>
        """, unsafe_allow_html=True)

    refresh_rate = create_sidebar()

    # Process live capture data if active
    if st.session_state.is_monitoring:
        process_live_data()

    display_df = st.session_state.history_df.tail(500)

    render_top_metrics(display_df)
    render_network_stats(display_df)

    col_charts, col_gauge = st.columns([3, 1])
    with col_charts:
        render_charts(display_df)
    with col_gauge:
        st.markdown(f"#### {t('live.system_health')}")
        render_threat_gauge(display_df)

    st.markdown('<div class="card-gap"></div>', unsafe_allow_html=True)
    render_recent_alerts(display_df)

    # Auto-refresh for live capture
    if st.session_state.is_monitoring and refresh_rate != t('live.manual'):
        seconds = int(refresh_rate.replace('s', ''))
        time.sleep(seconds)
        st.rerun()


if __name__ == "__main__":
    main()
