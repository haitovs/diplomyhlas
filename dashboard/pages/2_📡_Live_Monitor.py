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
from dashboard.theme import inject_theme, COLORS

st.set_page_config(page_title="Live Monitor", page_icon="📡", layout="wide")
inject_theme()

# Initialize session state objects
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataSourceManager()
    st.session_state.predictor = RealtimePredictor()
    st.session_state.history_df = pd.DataFrame()
    st.session_state.total_processed = 0
    st.session_state.is_monitoring = False

def create_sidebar():
    with st.sidebar:
        st.markdown("## ⚙️ Control Panel")
        
        # Monitor Toggle
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
            
        st.markdown("---")
        
        # Source Selection
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
            
        # Attack Simulation (only if using simulation source)
        if 'simulation' in selected_id:
            st.markdown("---")
            st.markdown("### ⚡ Attack Simulation")
            attack_type = st.selectbox("Type", ["DDoS", "PortScan", "BruteForce", "Bot", "SQLi"], label_visibility="collapsed")
            
            col1, col2 = st.columns(2)
            source = st.session_state.data_manager.get_current_source()
            
            # Check attack state directly from the simulator underlying the source
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
                    
        st.markdown("---")
        refresh_rate = st.selectbox("Refresh Rate", ["Manual", "1s", "3s", "5s"], index=1)
        batch_size = st.slider("Flows/batch", 10, 200, 50)
        
        return refresh_rate, batch_size

def process_data(batch_size):
    new_data = st.session_state.data_manager.get_data(n_samples=batch_size)
    if len(new_data) == 0: return pd.DataFrame()
    
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

def render_charts(df):
    if len(df) == 0 or 'ml_is_anomaly' not in df.columns:
        st.info("Waiting for data... Click 'Start Monitoring' in the sidebar.")
        return
        
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Traffic Timeline")
        df_sorted = df.sort_values('timestamp')
        
        # For simplicity, aggregate by seconds
        df_sorted['sec'] = pd.to_datetime(df_sorted['timestamp']).dt.floor('1s')
        agg = df_sorted.groupby('sec').agg({'ml_is_anomaly': 'sum', 'src_ip': 'count'}).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=agg['sec'], y=agg['src_ip'], name="Total", fill='tozeroy', 
            line=dict(color=COLORS['primary']), fillcolor=f"rgba(99,102,241,0.2)"
        ))
        
        anomalies = agg[agg['ml_is_anomaly'] > 0]
        if len(anomalies) > 0:
            fig.add_trace(go.Scatter(
                x=anomalies['sec'], y=anomalies['src_ip'], mode='markers', name='Threats',
                marker=dict(color=COLORS['danger'], size=10, symbol='circle')
            ))
            
        fig.update_layout(
            height=300, margin=dict(l=0, r=0, t=30, b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor=COLORS['bg_tertiary']),
            yaxis=dict(gridcolor=COLORS['bg_tertiary'])
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.markdown("#### Threat Distribution")
        anomalies_df = df[df['ml_is_anomaly']]
        if len(anomalies_df) > 0:
            counts = anomalies_df['ml_prediction'].value_counts()
            fig = go.Figure(data=[go.Pie(
                labels=counts.index, values=counts.values, hole=0.6,
                marker=dict(colors=[COLORS['danger'], COLORS['warning'], COLORS['accent'], COLORS['primary']])
            )])
            fig.update_layout(
                height=300, margin=dict(l=0, r=0, t=30, b=0),
                paper_bgcolor='rgba(0,0,0,0)', showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown(f"""
                <div style="height:250px; display:flex; align-items:center; justify-content:center; 
                     border:1px dashed {COLORS['border']}; border-radius:12px;">
                    <span style="color:{COLORS['success']}">No threats detected</span>
                </div>
            """, unsafe_allow_html=True)

def render_recent_alerts(df):
    st.markdown("#### Recent Threats")
    
    if len(df) == 0 or 'ml_is_anomaly' not in df.columns:
        st.markdown(f"""
            <div style="padding:1rem; border-radius:8px; background:rgba(16,185,129,0.1); color:{COLORS['success']}; border:1px solid rgba(16,185,129,0.3);">
                ✅ System secure. No data processed yet.
            </div>
        """, unsafe_allow_html=True)
        return
    
    anomalies = df[df['ml_is_anomaly']].tail(5)
    
    if len(anomalies) == 0:
        st.markdown(f"""
            <div style="padding:1rem; border-radius:8px; background:rgba(16,185,129,0.1); color:{COLORS['success']}; border:1px solid rgba(16,185,129,0.3);">
                ✅ System secure. No recent threats logged.
            </div>
        """, unsafe_allow_html=True)
        return
        
    for _, row in anomalies.iterrows():
        st.markdown(f"""
            <div style="padding:1rem; border-radius:8px; background:rgba(239,68,68,0.1); border-left:4px solid {COLORS['danger']}; margin-bottom:0.5rem; display:flex; justify-content:space-between;">
                <div>
                    <strong style="color:white">{row['ml_prediction']}</strong>
                    <span style="color:{COLORS['text_muted']}; margin-left:1rem;">{row.get('src_ip','N/A')} → {row.get('dst_ip','N/A')}:{row.get('dst_port','')}</span>
                </div>
                <div>
                    <span style="color:white; font-family:monospace;">{row['ml_confidence']*100:.1f}% Conf</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

def main():
    st.title("Live Network Monitor")
    
    if st.session_state.is_monitoring:
        st.markdown(f"""
            <div class="pulse-container" style="margin-bottom: 2rem;">
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
    st.markdown("<br>", unsafe_allow_html=True)
    
    render_charts(display_df)
    st.markdown("<br>", unsafe_allow_html=True)
    
    render_recent_alerts(display_df)
    
    if st.session_state.is_monitoring and refresh_rate != "Manual":
        seconds = int(refresh_rate.replace('s', ''))
        time.sleep(seconds)
        st.rerun()

if __name__ == "__main__":
    main()
