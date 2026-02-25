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
from dashboard.theme import inject_theme, COLORS

st.set_page_config(page_title="PCAP Analysis", page_icon="📁", layout="wide")
inject_theme()

st.title("📁 File Analysis")
st.markdown("Upload packet capture datasets (PCAP/PCAPNG) for offline forensic analysis.")

st.markdown(f"""
<style>
    .upload-box {{
        border: 2px dashed {COLORS['primary']};
        border-radius: 16px;
        padding: 4rem;
        text-align: center;
        background: {COLORS['bg_tertiary']};
        margin: 2rem 0;
        transition: all 0.3s ease;
    }}
    .upload-box:hover {{
        border-color: {COLORS['accent']};
        background: rgba(99, 102, 241, 0.1);
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
    st.success(f"✅ Loaded: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")
    
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
                    cols = st.columns(4)
                    cols[0].metric("Total Flows", f"{summary['total_flows']:,}")
                    cols[1].metric("Total Packets", f"{summary['total_packets']:,}")
                    cols[2].metric("Unique IP Addresses", f"{summary['unique_ips']}")
                    cols[3].metric("Active Protocols", len(summary['protocols']))
                    
                    st.markdown("<br>", unsafe_allow_html=True)
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
                        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', showlegend=True, margin=dict(t=0))
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.markdown("#### 📈 Target Ports")
                        port_counts = df['dst_port'].value_counts().head(8)
                        fig = px.bar(
                            x=port_counts.index.astype(str), 
                            y=port_counts.values,
                            color_discrete_sequence=[COLORS['primary']]
                        )
                        fig.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                            xaxis_title="Port", yaxis_title="Flows", margin=dict(t=0),
                            xaxis=dict(gridcolor=COLORS['bg_tertiary']),
                            yaxis=dict(gridcolor=COLORS['bg_tertiary'])
                        )
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
                st.error("⚠️ The 'scapy' library is not installed. Please run: `pip install scapy`")
            except Exception as e:
                st.error(f"Failed to process capture file: {str(e)}")
            finally:
                os.unlink(tmp_path)
else:
    st.markdown("""
    <div class="upload-box">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🗂️</div>
        <h3>Select a Capture File</h3>
        <p style="color: #94a3b8; max-width: 400px; margin: 0 auto; line-height: 1.6;">
            We support standard .pcap and .pcapng files generated by Wireshark, tcpdump, or other capture tools.
        </p>
        <p style="color: #64748b; font-size: 0.875rem; margin-top: 1rem;">
            Max size: 200MB • Local processing only
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
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

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:{COLORS['text_muted']};font-size:0.875rem;'>Network Anomaly Analyzer v2.0</p>", unsafe_allow_html=True)
