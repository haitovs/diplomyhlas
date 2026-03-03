"""
📡 Live Monitor Page
Combines file/simulation data sources with real-time analysis visualizations.
Includes Live Network Capture mode for sniffing real packets.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path
from datetime import datetime, timedelta
import time

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.data_sources import DataSourceManager, SimulationDataSource
from src.inference.realtime import RealtimePredictor
from dashboard.theme import inject_theme, inject_sidebar_brand, COLORS, apply_chart_theme
from dashboard.components import page_header, init_shared_state, append_detections
from dashboard.i18n import t

st.set_page_config(page_title="Live Monitor", page_icon="📡", layout="wide")
inject_theme()
inject_sidebar_brand()
init_shared_state()

if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataSourceManager()
    st.session_state.predictor = RealtimePredictor()
    st.session_state.history_df = pd.DataFrame()
    st.session_state.total_processed = 0
    st.session_state.is_monitoring = False

# Live capture state
if 'live_capture_obj' not in st.session_state:
    st.session_state.live_capture_obj = None
    st.session_state.live_capture_active = False
    st.session_state.live_capture_source_mode = False


def create_sidebar():
    with st.sidebar:
        st.markdown(f"### ⚙️ {t('live.control_panel')}")

        if not st.session_state.is_monitoring:
            if st.button(f"▶️ {t('live.start_monitoring')}", type="primary", use_container_width=True):
                st.session_state.is_monitoring = True
                st.rerun()
        else:
            if st.button(f"⏹️ {t('live.stop_monitoring')}", type="secondary", use_container_width=True):
                st.session_state.is_monitoring = False
                # Stop live capture if running
                if st.session_state.live_capture_obj and st.session_state.live_capture_active:
                    st.session_state.live_capture_obj.stop()
                    st.session_state.live_capture_active = False
                st.rerun()

        if st.button(f"🗑️ {t('live.clear_history')}", use_container_width=True):
            st.session_state.history_df = pd.DataFrame()
            st.session_state.total_processed = 0
            st.rerun()

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        # ── Data Source Selector (including Live Capture) ────────────────
        st.markdown(f"### 📊 {t('live.data_source')}")
        sources = st.session_state.data_manager.list_sources()
        source_dict = {name: sid for sid, name, desc in sources}
        source_dict[t('live.live_network_capture')] = "live_capture"

        selected_name = st.selectbox(
            t('live.select_source'),
            options=list(source_dict.keys()),
            label_visibility="collapsed"
        )
        selected_id = source_dict[selected_name]

        # Handle Live Network Capture mode
        if selected_id == "live_capture":
            st.session_state.live_capture_source_mode = True
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            st.markdown(f"### 🔌 {t('live.capture_interface')}")
            st.info(t('live.sudo_required'), icon="🔒")

            try:
                from src.capture.network_capture import get_available_interfaces, create_capture
                ifaces = get_available_interfaces()
                iface_names = [f"{i.name} ({i.ip})" for i in ifaces]
                iface_map = {f"{i.name} ({i.ip})": i.name for i in ifaces}

                if iface_names:
                    selected_iface_name = st.selectbox(t('live.interface'), iface_names)
                    selected_iface = iface_map[selected_iface_name]
                else:
                    st.warning(t('live.no_interfaces'))
                    selected_iface = "lo0"

                # Start/stop live capture
                if st.session_state.is_monitoring and not st.session_state.live_capture_active:
                    capture = create_capture(selected_iface)
                    try:
                        capture.start()
                        st.session_state.live_capture_obj = capture
                        st.session_state.live_capture_active = True
                    except Exception as e:
                        st.error(t('live.capture_failed', error=str(e)))
                        st.session_state.is_monitoring = False

                if st.session_state.live_capture_active and st.session_state.live_capture_obj:
                    stats = st.session_state.live_capture_obj.get_stats()
                    st.markdown(f"""
                    <div style="padding:0.5rem; border-radius:4px; background:rgba(245,158,11,0.06);
                         border:1px solid rgba(245,158,11,0.15); border-left:3px solid {COLORS['primary']};
                         margin-top:0.5rem; font-size:0.85rem;">
                        <div style="color:{COLORS['primary']}; font-weight:700; font-family:'Space Grotesk',sans-serif;">{t('live.capturing_on', interface=stats['interface'])}</div>
                        <div style="color:{COLORS['text_muted']}; font-family:'JetBrains Mono',monospace;">{t('live.packets_count', count=stats['packet_count'], rate=f"{stats['packets_per_second']:.1f}")}</div>
                    </div>
                    """, unsafe_allow_html=True)
            except ImportError:
                st.error(t('live.scapy_not_available'))
        else:
            st.session_state.live_capture_source_mode = False
            # Stop live capture if we switched away
            if st.session_state.live_capture_active and st.session_state.live_capture_obj:
                st.session_state.live_capture_obj.stop()
                st.session_state.live_capture_active = False

            if selected_id != st.session_state.data_manager.current_source:
                st.session_state.data_manager.set_source(selected_id)
                st.session_state.history_df = pd.DataFrame()
                st.session_state.total_processed = 0

            if 'simulation' in selected_id:
                st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
                st.markdown(f"### ⚡ {t('live.attack_simulation')}")
                attack_type = st.selectbox("Type", ["DDoS", "PortScan", "BruteForce", "Bot", "SQLi"], label_visibility="collapsed")

                col1, col2 = st.columns(2)
                source = st.session_state.data_manager.get_current_source()

                attack_active = False
                if hasattr(source, 'attack_sim') and hasattr(source.attack_sim, 'attack_active'):
                    attack_active = source.attack_sim.attack_active

                with col1:
                    if st.button(t('common.start'), disabled=attack_active, use_container_width=True):
                        source.start_attack(attack_type, duration_sec=60)
                        st.rerun()
                with col2:
                    if st.button(t('common.stop'), disabled=not attack_active, use_container_width=True):
                        source.stop_attack()
                        st.rerun()

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown(f"### 🔧 {t('live.parameters')}")
        refresh_rate = st.selectbox(t('live.refresh_rate'), [t('live.manual'), "1s", "3s", "5s"], index=1)
        batch_size = st.slider(t('live.flows_per_batch'), 10, 200, 50)

        return refresh_rate, batch_size


def process_data(batch_size):
    threshold = st.session_state.settings.get('confidence_threshold', 0.70)

    if st.session_state.live_capture_source_mode:
        # Live Capture mode: get packets from capture object
        if not st.session_state.live_capture_active or not st.session_state.live_capture_obj:
            return pd.DataFrame()

        packets = st.session_state.live_capture_obj.get_packets(max_packets=batch_size)
        if not packets:
            return pd.DataFrame()

        new_data = pd.DataFrame(packets)
    else:
        # Standard data source mode
        new_data = st.session_state.data_manager.get_data(n_samples=batch_size)

    if len(new_data) == 0:
        return pd.DataFrame()

    predictions = st.session_state.predictor.predict_batch(new_data.to_dict('records'))

    new_data['ml_prediction'] = [p['prediction'] for p in predictions]
    new_data['ml_confidence'] = [p['confidence'] for p in predictions]
    new_data['ml_is_anomaly'] = [
        p['is_anomaly'] and p['confidence'] >= threshold for p in predictions
    ]

    if 'timestamp' not in new_data.columns:
        current_time = datetime.now()
        new_data['timestamp'] = [current_time - timedelta(seconds=i) for i in range(len(new_data))[::-1]]

    st.session_state.total_processed += len(new_data)
    st.session_state.history_df = pd.concat([st.session_state.history_df, new_data], ignore_index=True)

    if len(st.session_state.history_df) > 1000:
        st.session_state.history_df = st.session_state.history_df.tail(1000)

    # Push anomalies to shared detection log
    source_label = "Live Capture" if st.session_state.live_capture_source_mode else "Live Monitor"
    anomalies = new_data[new_data['ml_is_anomaly']]
    if len(anomalies) > 0:
        anomaly_dets = []
        for _, row in anomalies.iterrows():
            anomaly_dets.append({
                'prediction': row['ml_prediction'],
                'confidence': row['ml_confidence'],
                'is_anomaly': True,
                'src_ip': row.get('src_ip', 'N/A'),
                'dst_ip': row.get('dst_ip', 'N/A'),
                'dst_port': row.get('dst_port', ''),
                'timestamp': row.get('timestamp', datetime.now()),
            })
        append_detections(anomaly_dets, source=source_label)

    # Update session metrics
    st.session_state.session_metrics['total_flows'] += len(new_data)

    return new_data


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
        status = t('live.status_live_capture') if st.session_state.live_capture_source_mode and st.session_state.is_monitoring else (
            t('live.status_active') if st.session_state.is_monitoring else t('live.status_paused')
        )
        st.metric(t('live.status'), status)


def render_threat_gauge(df):
    has_data = len(df) > 0 and 'ml_is_anomaly' in df.columns
    if has_data and len(df) > 0:
        threat_pct = df['ml_is_anomaly'].mean() * 100
    else:
        threat_pct = 0

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
    avg_bytes = df['bytes_per_sec'].mean() if 'bytes_per_sec' in df.columns else (df['flow_bytes_per_s'].mean() if 'flow_bytes_per_s' in df.columns else 0)

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

    anomalies = df[df['ml_is_anomaly']].tail(5)

    if len(anomalies) == 0:
        st.markdown(f"""
            <div style="padding:1rem; border-radius:4px; background:rgba(34,197,94,0.08);
                 color:{COLORS['success']}; border:1px solid rgba(34,197,94,0.2);
                 border-left:3px solid {COLORS['success']};">
                ✅ {t('live.system_secure_no_threats')}
            </div>
        """, unsafe_allow_html=True)
        return

    for _, row in anomalies.iterrows():
        conf = row['ml_confidence'] * 100
        if conf > 90:
            sev_color = COLORS['danger']
        elif conf > 80:
            sev_color = COLORS['warning']
        else:
            sev_color = COLORS['info']

        ts = row.get('timestamp', '')
        ts_str = ts.strftime('%H:%M:%S') if hasattr(ts, 'strftime') else str(ts)

        st.markdown(f"""
            <div style="padding:0.75rem 1rem; border-radius:4px; background:rgba(239,68,68,0.06);
                 border-left:3px solid {sev_color}; margin-bottom:0.5rem;
                 display:flex; justify-content:space-between; align-items:center;">
                <div style="display:flex; align-items:center; gap:0.75rem;">
                    <strong style="color:{COLORS['text_main']};">{row['ml_prediction']}</strong>
                    <span style="color:{COLORS['text_muted']}; font-size:0.85rem; font-family:'JetBrains Mono',monospace;">
                        {row.get('src_ip','N/A')} → {row.get('dst_ip','N/A')}:{row.get('dst_port','')}
                    </span>
                </div>
                <div style="display:flex; align-items:center; gap:1rem;">
                    <span style="color:{COLORS['text_muted']}; font-size:0.75rem; font-family:'JetBrains Mono',monospace;">{ts_str}</span>
                    <span style="color:{COLORS['primary']}; font-family:'JetBrains Mono',monospace; font-weight:700;">{conf:.1f}%</span>
                </div>
            </div>
        """, unsafe_allow_html=True)


def main():
    page_header("📡", t('live.page_title'), t('live.page_subtitle'))

    if st.session_state.is_monitoring:
        mode_label = t('live.live_packet_capture_mode') if st.session_state.live_capture_source_mode else t('live.actively_screening')
        st.markdown(f"""
            <div class="pulse-container" style="margin-bottom: 1.5rem;">
                <div class="pulse-dot"></div>
                <span style="font-size: 0.85rem; font-weight: 600; color:{COLORS['success']}">{mode_label}</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info(t('live.system_paused'))

    refresh_rate, batch_size = create_sidebar()

    if st.session_state.is_monitoring:
        process_data(batch_size)

    display_df = st.session_state.history_df.tail(300)

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

    if st.session_state.is_monitoring and refresh_rate != t('live.manual'):
        seconds = int(refresh_rate.replace('s', ''))
        time.sleep(seconds)
        st.rerun()


if __name__ == "__main__":
    main()
