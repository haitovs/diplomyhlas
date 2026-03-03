"""
📁 PCAP Analysis Page - Import and analyze network capture files with ML classification
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys
from pathlib import Path
from datetime import datetime
import tempfile
import os

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from dashboard.theme import inject_theme, inject_sidebar_brand, COLORS, apply_chart_theme
from dashboard.components import page_header, init_shared_state, append_detections

st.set_page_config(page_title="PCAP Analysis", page_icon="📁", layout="wide")
inject_theme()
inject_sidebar_brand()
init_shared_state()

page_header("📁", "File Analysis", "Upload & inspect packet captures")

st.markdown(f"""
<style>
    .upload-box {{
        border: 2px dashed rgba(245,158,11,0.30);
        border-radius: 4px;
        padding: 4rem 2rem;
        text-align: center;
        background: {COLORS['bg_tertiary']};
        margin: 2rem 0;
        transition: all 0.25s ease;
    }}
    .upload-box:hover {{
        border-color: {COLORS['primary']};
        background: rgba(245,158,11,0.04);
        box-shadow: 0 0 30px rgba(245,158,11,0.06);
    }}
    .result-card {{
        background: {COLORS['bg_tertiary']};
        border: 1px solid rgba(245,158,11,0.10);
        border-radius: 4px;
        padding: 1.5rem;
        border-top: 3px solid;
    }}
</style>
""", unsafe_allow_html=True)


def _map_pcap_flow_to_predictor(row: pd.Series) -> dict:
    """Map PCAP-extracted flow features to the dict format RealtimePredictor expects."""
    return {
        'duration': row.get('flow_duration', 0),
        'fwd_packets': row.get('total_fwd_packets', 0),
        'bwd_packets': row.get('total_bwd_packets', 0),
        'fwd_bytes': row.get('total_fwd_bytes', 0),
        'bwd_bytes': row.get('total_bwd_bytes', 0),
        'packets_per_sec': row.get('flow_packets_per_s', 0),
        'bytes_per_sec': row.get('flow_bytes_per_s', 0),
        'src_ip': row.get('src_ip', 'N/A'),
        'dst_ip': row.get('dst_ip', 'N/A'),
        'dst_port': row.get('dst_port', 0),
    }


def _run_ml_classification(df: pd.DataFrame):
    """Run ML classification on extracted flows and display results."""
    from src.inference.realtime import RealtimePredictor

    predictor = RealtimePredictor()
    threshold = st.session_state.settings.get('confidence_threshold', 0.70)

    flow_dicts = [_map_pcap_flow_to_predictor(row) for _, row in df.iterrows()]
    predictions = predictor.predict_batch(flow_dicts)

    df['ml_prediction'] = [p['prediction'] for p in predictions]
    df['ml_confidence'] = [p['confidence'] for p in predictions]
    df['ml_is_anomaly'] = [
        p['is_anomaly'] and p['confidence'] >= threshold for p in predictions
    ]

    # ── Threat Assessment ────────────────────────────────────────────────
    st.markdown("### 🛡️ ML Threat Assessment")
    threats = df[df['ml_is_anomaly']]
    benign = df[~df['ml_is_anomaly']]
    threat_ratio = len(threats) / max(len(df), 1) * 100

    c1, c2, c3, c4 = st.columns(4)
    border_colors = [COLORS['danger'], COLORS['success'], COLORS['warning'], COLORS['primary']]
    labels = ["Threats Found", "Benign Flows", "Threat Ratio", "Avg Confidence"]
    values = [
        f"{len(threats)}",
        f"{len(benign)}",
        f"{threat_ratio:.1f}%",
        f"{df['ml_confidence'].mean()*100:.1f}%",
    ]
    for col, lbl, val, bc in zip([c1, c2, c3, c4], labels, values, border_colors):
        with col:
            st.markdown(f"""
            <div class="result-card" style="border-top-color:{bc};">
                <div style="color:{COLORS['text_muted']}; font-size:0.8rem; text-transform:uppercase;
                     letter-spacing:0.04em; margin-bottom:0.5rem;">{lbl}</div>
                <div style="font-size:1.75rem; font-weight:700; font-family:'JetBrains Mono',monospace;
                     color:{COLORS['text_main']};">{val}</div>
            </div>
            """, unsafe_allow_html=True)

    # Threat type breakdown pie chart
    if len(threats) > 0:
        st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
        col_pie, col_table = st.columns([1, 2])
        with col_pie:
            st.markdown("#### Threat Type Breakdown")
            type_counts = threats['ml_prediction'].value_counts()
            fig = px.pie(
                values=type_counts.values, names=type_counts.index, hole=0.55,
                color_discrete_sequence=[COLORS['danger'], COLORS['warning'], COLORS['accent'], COLORS['primary'], COLORS['success']]
            )
            fig.update_traces(textfont=dict(color=COLORS['text_main']))
            apply_chart_theme(fig)
            fig.update_layout(height=320)
            st.plotly_chart(fig, use_container_width=True)

        with col_table:
            st.markdown("#### Detected Threats")
            threat_display = threats[['src_ip', 'dst_ip', 'dst_port', 'ml_prediction', 'ml_confidence']].copy()
            threat_display['ml_confidence'] = (threat_display['ml_confidence'] * 100).round(1).astype(str) + '%'
            threat_display.columns = ['Source IP', 'Dest IP', 'Port', 'Verdict', 'Confidence']
            st.dataframe(threat_display.head(50), use_container_width=True, hide_index=True)

    # Push anomalies to shared detection log
    anomaly_dets = []
    for _, row in threats.iterrows():
        anomaly_dets.append({
            'prediction': row['ml_prediction'],
            'confidence': row['ml_confidence'],
            'is_anomaly': True,
            'src_ip': row.get('src_ip', 'N/A'),
            'dst_ip': row.get('dst_ip', 'N/A'),
            'dst_port': row.get('dst_port', ''),
            'timestamp': datetime.now(),
        })
    if anomaly_dets:
        append_detections(anomaly_dets, source="PCAP Analysis")

    st.session_state.pcap_results = df
    return df


# ── File Upload ─────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Upload PCAP/PCAPNG file",
    type=['pcap', 'pcapng', 'cap'],
    help="Drag and drop or click to upload network capture files",
    label_visibility="hidden"
)

if uploaded_file:
    st.success(f"Loaded: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pcap') as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    if st.button("🔍 Begin Deep Analysis", type="primary", use_container_width=True):
        with st.spinner("Decoding packets and extracting flow features..."):
            try:
                from src.capture import PcapAnalyzer

                analyzer = PcapAnalyzer()
                df = analyzer.analyze(tmp_path)
                summary = analyzer.get_summary()

                if df.empty:
                    st.warning("No IP packets found in the uploaded file.")
                else:
                    st.markdown("### 📊 Dataset Overview")
                    c1, c2, c3, c4 = st.columns(4)
                    border_colors = [COLORS['primary'], COLORS['accent'], COLORS['success'], COLORS['warning']]
                    labels = ["Total Flows", "Total Packets", "Unique IPs", "Protocols"]
                    values = [
                        f"{summary['total_flows']:,}",
                        f"{summary['total_packets']:,}",
                        f"{summary['unique_ips']}",
                        str(len(summary['protocols'])),
                    ]
                    for col, lbl, val, bc in zip([c1, c2, c3, c4], labels, values, border_colors):
                        with col:
                            st.markdown(f"""
                            <div class="result-card" style="border-top-color:{bc};">
                                <div style="color:{COLORS['text_muted']}; font-size:0.8rem; text-transform:uppercase;
                                     letter-spacing:0.04em; margin-bottom:0.5rem;">{lbl}</div>
                                <div style="font-size:1.75rem; font-weight:700; font-family:'JetBrains Mono',monospace;
                                     color:{COLORS['text_main']};">{val}</div>
                            </div>
                            """, unsafe_allow_html=True)

                    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("#### 📡 Protocol Breakdown")
                        protocols = summary['protocols']
                        fig = px.pie(
                            values=list(protocols.values()),
                            names=list(protocols.keys()),
                            hole=0.5,
                            color_discrete_sequence=[COLORS['primary'], COLORS['accent'], COLORS['success'], COLORS['warning']]
                        )
                        fig.update_traces(textfont=dict(color=COLORS['text_main']))
                        apply_chart_theme(fig)
                        fig.update_layout(height=320)
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        st.markdown("#### 📈 Target Ports")
                        port_counts = df['dst_port'].value_counts().head(8)
                        fig = px.bar(
                            x=port_counts.index.astype(str),
                            y=port_counts.values,
                            color_discrete_sequence=[COLORS['primary']]
                        )
                        apply_chart_theme(fig)
                        fig.update_layout(height=320, xaxis_title="Port", yaxis_title="Flows")
                        st.plotly_chart(fig, use_container_width=True)

                    # ── ML Classification ────────────────────────────────────────
                    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
                    df = _run_ml_classification(df)

                    # ── Flow Signatures Table ────────────────────────────────────
                    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
                    st.markdown("### 📋 Flow Signatures")
                    display_cols = ['src_ip', 'dst_ip', 'src_port', 'dst_port', 'protocol',
                                    'total_fwd_packets', 'total_bwd_packets', 'flow_bytes_per_s',
                                    'ml_prediction', 'ml_confidence', 'ml_is_anomaly']
                    show_df = df[display_cols].copy()
                    show_df['ml_confidence'] = (show_df['ml_confidence'] * 100).round(1).astype(str) + '%'
                    show_df.columns = ['Src IP', 'Dst IP', 'Src Port', 'Dst Port', 'Proto',
                                       'Fwd Pkts', 'Bwd Pkts', 'Bytes/s',
                                       'ML Verdict', 'Confidence', 'Threat']
                    st.dataframe(show_df.head(100), use_container_width=True, hide_index=True)

                    st.download_button(
                        "📥 Download Extracted Features (CSV)",
                        df.to_csv(index=False),
                        file_name=f"pcap_features_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        type="primary"
                    )

            except ImportError:
                st.error("The 'scapy' library is not installed. Please run: `pip install scapy`")
            except Exception as e:
                st.error(f"Failed to process capture file: {str(e)}")
            finally:
                os.unlink(tmp_path)
else:
    # ── Empty state ─────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="upload-box">
        <div style="font-size: 4rem; margin-bottom: 1rem; opacity:0.8;">🗂️</div>
        <h3 style="margin-bottom:0.5rem;">Select a Capture File</h3>
        <p style="color: {COLORS['text_muted']}; max-width: 420px; margin: 0 auto; line-height: 1.7; font-size:0.95rem;">
            We support standard <strong>.pcap</strong> and <strong>.pcapng</strong> files generated by
            Wireshark, tcpdump, or other capture tools.
        </p>
        <div style="display:flex; gap:1rem; justify-content:center; margin-top:1.25rem;">
            <span style="color:{COLORS['text_muted']}; font-size:0.8rem; padding:4px 12px;
                  border:1px solid rgba(148,163,184,0.15); border-radius:8px;">Max 200 MB</span>
            <span style="color:{COLORS['text_muted']}; font-size:0.8rem; padding:4px 12px;
                  border:1px solid rgba(148,163,184,0.15); border-radius:8px;">Local Processing Only</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    if st.button("Generate Synthetic Demo Capture", use_container_width=True):
        n = 100
        demo_df = pd.DataFrame({
            'src_ip': [f"192.168.1.{np.random.randint(1,255)}" for _ in range(n)],
            'dst_ip': [f"10.0.0.{np.random.randint(1,255)}" for _ in range(n)],
            'src_port': np.random.randint(1024, 65535, n),
            'dst_port': np.random.choice([80, 443, 22, 3389, 53], n),
            'protocol': np.random.choice(['TCP', 'UDP'], n, p=[0.85, 0.15]),
            'total_fwd_packets': np.random.poisson(12, n),
            'total_bwd_packets': np.random.poisson(18, n),
            'total_fwd_bytes': np.random.randint(500, 50000, n),
            'total_bwd_bytes': np.random.randint(500, 50000, n),
            'flow_duration': np.random.exponential(5000, n),
            'flow_bytes_per_s': np.random.exponential(8000, n),
            'flow_packets_per_s': np.random.exponential(50, n),
        })

        st.markdown("### 📊 Demo Processing Complete")
        cols = st.columns(4)
        cols[0].metric("Total Flows", n)
        cols[1].metric("Total Packets", int(demo_df['total_fwd_packets'].sum() + demo_df['total_bwd_packets'].sum()))
        cols[2].metric("Unique Source IPs", demo_df['src_ip'].nunique())
        cols[3].metric("Protocols", 2)

        # Run ML on demo data
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        demo_df = _run_ml_classification(demo_df)

        st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
        st.dataframe(demo_df, use_container_width=True, hide_index=True)

st.markdown(f"""
<div style="text-align:center; margin-top:3rem; padding-top:1.5rem; border-top:1px solid {COLORS['border']};">
    <p style="color:{COLORS['text_muted']}; font-size:0.85rem;">Network Anomaly Analyzer v2.0</p>
</div>
""", unsafe_allow_html=True)
