"""
📡 Live Monitor Page
Combines file/simulation data sources with real-time analysis visualizations
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
from dashboard.components import page_header

st.set_page_config(page_title="Live Monitor", page_icon="📡", layout="wide")
inject_theme()
inject_sidebar_brand()

if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataSourceManager()
    st.session_state.predictor = RealtimePredictor()
    st.session_state.history_df = pd.DataFrame()
    st.session_state.total_processed = 0
    st.session_state.is_monitoring = False


def create_sidebar():
    with st.sidebar:
        st.markdown("### ⚙️ Control Panel")

        if not st.session_state.is_monitoring:
            if st.button("▶️ Start Monitoring", type="primary", use_container_width=True):
                st.session_state.is_monitoring = True
                st.rerun()
        else:
            if st.button("⏹️ Stop Monitoring", type="secondary", use_container_width=True):
                st.session_state.is_monitoring = False
                st.rerun()

        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.history_df = pd.DataFrame()
            st.session_state.total_processed = 0
            st.rerun()

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        st.markdown("### 📊 Data Source")
        sources = st.session_state.data_manager.list_sources()
        source_dict = {name: sid for sid, name, desc in sources}

        selected_name = st.selectbox(
            "Select Source",
            options=list(source_dict.keys()),
            label_visibility="collapsed"
        )
        selected_id = source_dict[selected_name]

        if selected_id != st.session_state.data_manager.current_source:
            st.session_state.data_manager.set_source(selected_id)
            st.session_state.history_df = pd.DataFrame()
            st.session_state.total_processed = 0

        if 'simulation' in selected_id:
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            st.markdown("### ⚡ Attack Simulation")
            attack_type = st.selectbox("Type", ["DDoS", "PortScan", "BruteForce", "Bot", "SQLi"], label_visibility="collapsed")

            col1, col2 = st.columns(2)
            source = st.session_state.data_manager.get_current_source()

            attack_active = False
            if hasattr(source, 'attack_sim') and hasattr(source.attack_sim, 'attack_active'):
                attack_active = source.attack_sim.attack_active

            with col1:
                if st.button("Start", disabled=attack_active, use_container_width=True):
                    source.start_attack(attack_type, duration_sec=60)
                    st.rerun()
            with col2:
                if st.button("Stop", disabled=not attack_active, use_container_width=True):
                    source.stop_attack()
                    st.rerun()

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown("### 🔧 Parameters")
        refresh_rate = st.selectbox("Refresh Rate", ["Manual", "1s", "3s", "5s"], index=1)
        batch_size = st.slider("Flows/batch", 10, 200, 50)

        return refresh_rate, batch_size


def process_data(batch_size):
    new_data = st.session_state.data_manager.get_data(n_samples=batch_size)
    if len(new_data) == 0:
        return pd.DataFrame()

    predictions = st.session_state.predictor.predict_batch(new_data.to_dict('records'))

    new_data['ml_prediction'] = [p['prediction'] for p in predictions]
    new_data['ml_confidence'] = [p['confidence'] for p in predictions]
    new_data['ml_is_anomaly'] = [p['is_anomaly'] for p in predictions]

    if 'timestamp' not in new_data.columns:
        current_time = datetime.now()
        new_data['timestamp'] = [current_time - timedelta(seconds=i) for i in range(len(new_data))[::-1]]

    st.session_state.total_processed += len(new_data)
    st.session_state.history_df = pd.concat([st.session_state.history_df, new_data], ignore_index=True)

    if len(st.session_state.history_df) > 1000:
        st.session_state.history_df = st.session_state.history_df.tail(1000)

    return new_data


def render_top_metrics(df):
    has_data = len(df) > 0 and 'ml_is_anomaly' in df.columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("TOTAL FLOWS", f"{st.session_state.total_processed:,}")
    with col2:
        anomalies = int(df['ml_is_anomaly'].sum()) if has_data else 0
        pct = (anomalies / len(df) * 100) if has_data and len(df) > 0 else 0
        st.metric("THREATS DETECTED", f"{anomalies}", f"{pct:.1f}%", delta_color="inverse")
    with col3:
        conf = df['ml_confidence'].mean() * 100 if has_data else 0
        st.metric("AVG CONFIDENCE", f"{conf:.1f}%")
    with col4:
        st.metric("STATUS", "ACTIVE" if st.session_state.is_monitoring else "PAUSED")


def render_threat_gauge(df):
    """Render a radial gauge for current threat level."""
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
        title=dict(text="Threat Level", font=dict(color=COLORS['text_muted'], size=14)),
        gauge=dict(
            axis=dict(range=[0, 100], tickfont=dict(color=COLORS['text_muted']), tickcolor=COLORS['text_muted']),
            bar=dict(color=bar_color),
            bgcolor="rgba(30,41,59,0.5)",
            borderwidth=0,
            steps=[
                dict(range=[0, 10], color="rgba(16,185,129,0.12)"),
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
        st.info("Waiting for data... Click 'Start Monitoring' in the sidebar.")
        return

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("#### Traffic Timeline")
        df_sorted = df.sort_values('timestamp')
        df_sorted['sec'] = pd.to_datetime(df_sorted['timestamp']).dt.floor('1s')
        agg = df_sorted.groupby('sec').agg({'ml_is_anomaly': 'sum', 'src_ip': 'count'}).reset_index()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=agg['sec'], y=agg['src_ip'], name="Total", fill='tozeroy',
            line=dict(color=COLORS['primary']), fillcolor="rgba(99,102,241,0.15)"
        ))

        anomalies = agg[agg['ml_is_anomaly'] > 0]
        if len(anomalies) > 0:
            fig.add_trace(go.Scatter(
                x=anomalies['sec'], y=anomalies['src_ip'], mode='markers', name='Threats',
                marker=dict(color=COLORS['danger'], size=10, symbol='circle')
            ))

        apply_chart_theme(fig)
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("#### Threat Distribution")
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
                     border:1px dashed {COLORS['border']}; border-radius:12px;">
                    <span style="color:{COLORS['success']}; font-weight:600;">No threats detected</span>
                </div>
            """, unsafe_allow_html=True)


def render_network_stats(df):
    """Mini network stats bar below main metrics."""
    if len(df) == 0 or 'ml_is_anomaly' not in df.columns:
        return

    unique_src = df['src_ip'].nunique() if 'src_ip' in df.columns else 0
    unique_dst = df['dst_ip'].nunique() if 'dst_ip' in df.columns else 0
    top_port = int(df['dst_port'].mode().iloc[0]) if 'dst_port' in df.columns and len(df) > 0 else "-"
    avg_bytes = df['flow_bytes_per_s'].mean() if 'flow_bytes_per_s' in df.columns else 0

    st.markdown(f"""
    <div style="display:flex; gap:1.5rem; flex-wrap:wrap; padding:0.75rem 1rem;
         background:rgba(30,41,59,0.35); border:1px solid rgba(99,102,241,0.1);
         border-radius:10px; margin-bottom:1.5rem;">
        <span style="color:{COLORS['text_muted']}; font-size:0.8rem;">
            <strong style="color:{COLORS['text_main']};">{unique_src}</strong> Source IPs
        </span>
        <span style="color:{COLORS['text_muted']}; font-size:0.8rem;">
            <strong style="color:{COLORS['text_main']};">{unique_dst}</strong> Dest IPs
        </span>
        <span style="color:{COLORS['text_muted']}; font-size:0.8rem;">
            Top Port: <strong style="color:{COLORS['text_main']};">{top_port}</strong>
        </span>
        <span style="color:{COLORS['text_muted']}; font-size:0.8rem;">
            Avg Throughput: <strong style="color:{COLORS['text_main']};">{avg_bytes:,.0f} B/s</strong>
        </span>
    </div>
    """, unsafe_allow_html=True)


def render_recent_alerts(df):
    st.markdown("#### Recent Threats")

    if len(df) == 0 or 'ml_is_anomaly' not in df.columns:
        st.markdown(f"""
            <div style="padding:1rem; border-radius:10px; background:rgba(16,185,129,0.08);
                 color:{COLORS['success']}; border:1px solid rgba(16,185,129,0.2);">
                ✅ System secure. No data processed yet.
            </div>
        """, unsafe_allow_html=True)
        return

    anomalies = df[df['ml_is_anomaly']].tail(5)

    if len(anomalies) == 0:
        st.markdown(f"""
            <div style="padding:1rem; border-radius:10px; background:rgba(16,185,129,0.08);
                 color:{COLORS['success']}; border:1px solid rgba(16,185,129,0.2);">
                ✅ System secure. No recent threats logged.
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
            <div style="padding:0.75rem 1rem; border-radius:10px; background:rgba(239,68,68,0.06);
                 border-left:4px solid {sev_color}; margin-bottom:0.5rem;
                 display:flex; justify-content:space-between; align-items:center;">
                <div style="display:flex; align-items:center; gap:0.75rem;">
                    <strong style="color:white;">{row['ml_prediction']}</strong>
                    <span style="color:{COLORS['text_muted']}; font-size:0.85rem;">
                        {row.get('src_ip','N/A')} → {row.get('dst_ip','N/A')}:{row.get('dst_port','')}
                    </span>
                </div>
                <div style="display:flex; align-items:center; gap:1rem;">
                    <span style="color:{COLORS['text_muted']}; font-size:0.75rem; font-family:monospace;">{ts_str}</span>
                    <span style="color:white; font-family:monospace; font-weight:600;">{conf:.1f}%</span>
                </div>
            </div>
        """, unsafe_allow_html=True)


def main():
    page_header("📡", "Live Monitor", "Real-time network traffic analysis")

    if st.session_state.is_monitoring:
        st.markdown(f"""
            <div class="pulse-container" style="margin-bottom: 1.5rem;">
                <div class="pulse-dot"></div>
                <span style="font-size: 0.85rem; font-weight: 600; color:{COLORS['success']}">ACTIVELY SCREENING TRAFFIC</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("System paused. Click 'Start Monitoring' in the sidebar to begin processing traffic.")

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
        st.markdown("#### System Health")
        render_threat_gauge(display_df)

    st.markdown('<div class="card-gap"></div>', unsafe_allow_html=True)
    render_recent_alerts(display_df)

    if st.session_state.is_monitoring and refresh_rate != "Manual":
        seconds = int(refresh_rate.replace('s', ''))
        time.sleep(seconds)
        st.rerun()


if __name__ == "__main__":
    main()
