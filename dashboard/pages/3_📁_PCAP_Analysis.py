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

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

st.set_page_config(page_title="PCAP Analysis", page_icon="📁", layout="wide")

# Theme CSS
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0a0f1a 0%, #111827 100%); }
    .upload-box {
        border: 2px dashed #6366f1;
        border-radius: 16px;
        padding: 3rem;
        text-align: center;
        background: rgba(99, 102, 241, 0.05);
        margin: 2rem 0;
    }
    .result-card {
        background: rgba(31, 41, 55, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    h1, h2, h3 { color: #f8fafc !important; }
</style>
""", unsafe_allow_html=True)

st.title("📁 PCAP File Analysis")
st.markdown("Upload network capture files to analyze traffic patterns and detect anomalies")

# File upload
uploaded_file = st.file_uploader(
    "Upload PCAP/PCAPNG file",
    type=['pcap', 'pcapng', 'cap'],
    help="Drag and drop or click to upload network capture files"
)

if uploaded_file:
    st.success(f"✅ File uploaded: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pcap') as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name
    
    # Analyze button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_btn = st.button("🔍 Analyze PCAP", width='stretch')
    
    if analyze_btn:
        with st.spinner("Analyzing packets..."):
            try:
                from src.capture import PcapAnalyzer
                
                analyzer = PcapAnalyzer()
                df = analyzer.analyze(tmp_path)
                summary = analyzer.get_summary()
                
                if df.empty:
                    st.warning("No IP packets found in file")
                else:
                    # Summary metrics
                    st.markdown("### 📊 Analysis Results")
                    cols = st.columns(4)
                    cols[0].metric("Total Flows", f"{summary['total_flows']:,}")
                    cols[1].metric("Total Packets", f"{summary['total_packets']:,}")
                    cols[2].metric("Unique IPs", f"{summary['unique_ips']}")
                    cols[3].metric("Protocols", len(summary['protocols']))
                    
                    st.markdown("---")
                    
                    # Protocol distribution
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 📡 Protocol Distribution")
                        protocols = summary['protocols']
                        fig = px.pie(
                            values=list(protocols.values()),
                            names=list(protocols.keys()),
                            hole=0.4
                        )
                        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
                        st.plotly_chart(fig, width='stretch')
                    
                    with col2:
                        st.markdown("#### 📈 Traffic by Port")
                        port_counts = df['dst_port'].value_counts().head(10)
                        fig = px.bar(x=port_counts.index.astype(str), y=port_counts.values)
                        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
                        st.plotly_chart(fig, width='stretch')
                    
                    st.markdown("---")
                    
                    # Flow table
                    st.markdown("#### 📋 Flow Details")
                    display_cols = ['src_ip', 'dst_ip', 'src_port', 'dst_port', 'protocol', 
                                   'total_fwd_packets', 'total_bwd_packets', 'flow_bytes_per_s']
                    st.dataframe(
                        df[display_cols].head(100),
                        width='stretch',
                        hide_index=True
                    )
                    
                    # Download results
                    st.download_button(
                        "📥 Download as CSV",
                        df.to_csv(index=False),
                        file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                    
            except ImportError:
                st.error("⚠️ scapy not installed. Run: `pip install scapy`")
            except Exception as e:
                st.error(f"Analysis error: {str(e)}")
            finally:
                os.unlink(tmp_path)
else:
    # Upload instructions
    st.markdown("""
    <div class="upload-box">
        <h3>📂 Drop your PCAP file here</h3>
        <p style="color: #94a3b8;">Supported formats: .pcap, .pcapng, .cap</p>
        <p style="color: #64748b; font-size: 0.875rem;">
            Maximum file size: 200MB • Files are processed locally
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Demo option
    st.markdown("---")
    st.markdown("### 🎮 No PCAP file? Try demo data")
    if st.button("Generate Demo Analysis"):
        import numpy as np
        
        # Generate demo flows
        n = 50
        demo_df = pd.DataFrame({
            'src_ip': [f"192.168.1.{np.random.randint(1,255)}" for _ in range(n)],
            'dst_ip': [f"10.0.0.{np.random.randint(1,255)}" for _ in range(n)],
            'src_port': np.random.randint(1024, 65535, n),
            'dst_port': np.random.choice([80, 443, 22, 3389], n),
            'protocol': np.random.choice(['TCP', 'UDP'], n, p=[0.8, 0.2]),
            'total_fwd_packets': np.random.poisson(10, n),
            'total_bwd_packets': np.random.poisson(15, n),
            'flow_bytes_per_s': np.random.exponential(5000, n),
        })
        
        st.markdown("### 📊 Demo Analysis Results")
        cols = st.columns(4)
        cols[0].metric("Total Flows", n)
        cols[1].metric("Total Packets", demo_df['total_fwd_packets'].sum() + demo_df['total_bwd_packets'].sum())
        cols[2].metric("Unique IPs", demo_df['src_ip'].nunique())
        cols[3].metric("Protocols", 2)
        
        st.dataframe(demo_df, width='stretch', hide_index=True)

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center; color:#64748b;'>Yhlas Network Analyzer v2.0</p>", unsafe_allow_html=True)
