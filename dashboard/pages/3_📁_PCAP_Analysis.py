"""
📁 PCAP Analysis Page - Import and analyze network capture files
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path
from datetime import datetime
import tempfile
import os

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from dashboard.theme import inject_theme, inject_sidebar_brand, COLORS, apply_chart_theme
from dashboard.components import page_header

st.set_page_config(page_title="PCAP Analysis", page_icon="📁", layout="wide")
inject_theme()
inject_sidebar_brand()

page_header("📁", "File Analysis", "Upload & inspect packet captures")

st.markdown(f"""
<style>
    .upload-box {{
        border: 2px dashed rgba(99,102,241,0.35);
        border-radius: 16px;
        padding: 4rem 2rem;
        text-align: center;
        background: rgba(30,41,59,0.3);
        backdrop-filter: blur(8px);
        margin: 2rem 0;
        transition: all 0.3s ease;
    }}
    .upload-box:hover {{
        border-color: {COLORS['accent']};
        background: rgba(99, 102, 241, 0.06);
        box-shadow: 0 0 30px rgba(99,102,241,0.08);
    }}
    .result-card {{
        background: rgba(30,41,59,0.45);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(99,102,241,0.15);
        border-radius: 14px;
        padding: 1.5rem;
        border-top: 3px solid;
    }}
</style>
""", unsafe_allow_html=True)

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

                    st.markdown("### 📋 Flow Signatures")
                    display_cols = ['src_ip', 'dst_ip', 'src_port', 'dst_port', 'protocol',
                                    'total_fwd_packets', 'total_bwd_packets', 'flow_bytes_per_s']
                    st.dataframe(
                        df[display_cols].head(100),
                        use_container_width=True,
                        hide_index=True
                    )

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
    # ── Better empty state ───────────────────────────────────────────────────
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
        import numpy as np
        n = 100
        demo_df = pd.DataFrame({
            'src_ip': [f"192.168.1.{np.random.randint(1,255)}" for _ in range(n)],
            'dst_ip': [f"10.0.0.{np.random.randint(1,255)}" for _ in range(n)],
            'src_port': np.random.randint(1024, 65535, n),
            'dst_port': np.random.choice([80, 443, 22, 3389, 53], n),
            'protocol': np.random.choice(['TCP', 'UDP'], n, p=[0.85, 0.15]),
            'total_fwd_packets': np.random.poisson(12, n),
            'total_bwd_packets': np.random.poisson(18, n),
            'flow_bytes_per_s': np.random.exponential(8000, n),
        })

        st.markdown("### 📊 Demo Processing Complete")
        cols = st.columns(4)
        cols[0].metric("Total Flows", n)
        cols[1].metric("Total Packets", demo_df['total_fwd_packets'].sum() + demo_df['total_bwd_packets'].sum())
        cols[2].metric("Unique Source IPs", demo_df['src_ip'].nunique())
        cols[3].metric("Protocols", 2)

        st.dataframe(demo_df, use_container_width=True, hide_index=True)

st.markdown(f"""
<div style="text-align:center; margin-top:3rem; padding-top:1.5rem; border-top:1px solid {COLORS['border']};">
    <p style="color:{COLORS['text_muted']}; font-size:0.85rem;">Network Anomaly Analyzer v2.0</p>
</div>
""", unsafe_allow_html=True)
