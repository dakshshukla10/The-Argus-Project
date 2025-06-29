"""
Streamlit dashboard for The Argus Protocol.
Displays live video stream and real-time analytics data from the FastAPI backend.
This is a client-only interface - no CV/AI processing is performed here.
"""

import streamlit as st
import requests
import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import time
import websocket
import threading
import queue
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Argus Protocol Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
WEBSOCKET_URL = "ws://127.0.0.1:8000/ws/analytics"
VIDEO_STREAM_URL = f"{BACKEND_URL}/analytics_stream"

# Initialize session state
if 'analytics_data' not in st.session_state:
    st.session_state.analytics_data = []
if 'websocket_connected' not in st.session_state:
    st.session_state.websocket_connected = False
if 'data_queue' not in st.session_state:
    st.session_state.data_queue = queue.Queue()

def get_status_color(status):
    """Get color for status indicator."""
    colors = {
        'NORMAL': '#28a745',    # Green
        'WARNING': '#ffc107',   # Yellow
        'CRITICAL': '#dc3545'   # Red
    }
    return colors.get(status, '#6c757d')  # Default gray

def get_status_emoji(status):
    """Get emoji for status."""
    emojis = {
        'NORMAL': '✅',
        'WARNING': '⚠️',
        'CRITICAL': '🚨'
    }
    return emojis.get(status, '❓')

def websocket_listener():
    """WebSocket listener running in background thread."""
    def on_message(ws, message):
        try:
            data = json.loads(message)
            data['timestamp'] = datetime.now()
            st.session_state.data_queue.put(data)
        except Exception as e:
            print(f"Error processing WebSocket message: {e}")
    
    def on_error(ws, error):
        print(f"WebSocket error: {error}")
        st.session_state.websocket_connected = False
    
    def on_close(ws, close_status_code, close_msg):
        print("WebSocket connection closed")
        st.session_state.websocket_connected = False
    
    def on_open(ws):
        print("WebSocket connection opened")
        st.session_state.websocket_connected = True
    
    try:
        ws = websocket.WebSocketApp(WEBSOCKET_URL,
                                  on_open=on_open,
                                  on_message=on_message,
                                  on_error=on_error,
                                  on_close=on_close)
        ws.run_forever()
    except Exception as e:
        print(f"WebSocket connection failed: {e}")
        st.session_state.websocket_connected = False

def check_backend_status():
    """Check if the backend is running."""
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=3)
        return response.status_code == 200
    except:
        return False

def main():
    """Main dashboard application."""
    
    # Header
    st.title("🎯 Argus Protocol Dashboard")
    st.markdown("**Real-time Crowd Analytics & Stampede Risk Assessment**")
    
    # Check backend status
    backend_online = check_backend_status()
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 System Status")
        
        # Backend status
        if backend_online:
            st.success("✅ Backend Online")
        else:
            st.error("❌ Backend Offline")
            st.warning("Please start the FastAPI backend:")
            st.code("cd src && python main.py")
            return
        
        # WebSocket status
        if st.session_state.websocket_connected:
            st.success("✅ WebSocket Connected")
        else:
            st.warning("🔄 Connecting to WebSocket...")
            # Start WebSocket listener if not already running
            if 'websocket_thread' not in st.session_state:
                st.session_state.websocket_thread = threading.Thread(
                    target=websocket_listener, daemon=True
                )
                st.session_state.websocket_thread.start()
        
        st.markdown("---")
        
        # Configuration
        st.header("⚙️ Configuration")
        max_data_points = st.slider("Max Data Points", 50, 500, 200)
        refresh_rate = st.slider("Refresh Rate (seconds)", 0.5, 5.0, 1.0)
        
        st.markdown("---")
        
        # Thresholds display
        st.header("🎯 Alert Thresholds")
        st.markdown("**Density (persons/cell)**")
        st.markdown("⚠️ Warning: 4.0")
        st.markdown("🚨 Critical: 6.0")
        
        st.markdown("**Motion Coherence (std dev)**")
        st.markdown("⚠️ Warning: 40.0°")
        st.markdown("🚨 Critical: 65.0°")
        
        st.markdown("**Kinetic Energy**")
        st.markdown("⚠️ Spike Factor: 2.0x")
    
    # Process incoming WebSocket data
    while not st.session_state.data_queue.empty():
        try:
            new_data = st.session_state.data_queue.get_nowait()
            st.session_state.analytics_data.append(new_data)
            
            # Keep only recent data points
            if len(st.session_state.analytics_data) > max_data_points:
                st.session_state.analytics_data = st.session_state.analytics_data[-max_data_points:]
        except queue.Empty:
            break
    
    # Main content
    if not st.session_state.analytics_data:
        st.info("🔄 Waiting for analytics data from backend...")
        st.markdown("Make sure the backend is running and processing video.")
        return
    
    # Get latest data
    latest_data = st.session_state.analytics_data[-1]
    
    # Status indicator (prominent)
    status = latest_data.get('status', 'UNKNOWN')
    status_color = get_status_color(status)
    status_emoji = get_status_emoji(status)
    
    st.markdown(f"""
    <div style="
        background-color: {status_color}; 
        color: white; 
        padding: 20px; 
        border-radius: 10px; 
        text-align: center; 
        font-size: 24px; 
        font-weight: bold; 
        margin-bottom: 20px;
    ">
        {status_emoji} SYSTEM STATUS: {status}
    </div>
    """, unsafe_allow_html=True)
    
    # Video stream and current metrics
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📹 Live Video Stream")
        try:
            st.image(VIDEO_STREAM_URL, use_column_width=True)
        except Exception as e:
            st.error(f"Failed to load video stream: {e}")
            st.markdown(f"Video URL: {VIDEO_STREAM_URL}")
    
    with col2:
        st.subheader("📊 Current Metrics")
        
        # Person count
        person_count = latest_data.get('person_count', 0)
        st.metric("👥 Person Count", person_count)
        
        # Density
        density_data = latest_data.get('density', {})
        max_density = density_data.get('max_density', 0)
        st.metric("🏘️ Max Density", f"{max_density:.1f} persons/cell")
        
        # Motion Coherence
        coherence_data = latest_data.get('motion_coherence', {})
        std_deviation = coherence_data.get('std_deviation', 0)
        st.metric("🌊 Motion Coherence", f"{std_deviation:.1f}° std dev")
        
        # Kinetic Energy
        ke_data = latest_data.get('kinetic_energy', {})
        current_ke = ke_data.get('current', 0)
        moving_avg = ke_data.get('moving_average', 0)
        spike_detected = ke_data.get('spike_detected', False)
        
        ke_label = "⚡ Kinetic Energy"
        if spike_detected:
            ke_label += " 🔥"
        
        st.metric(ke_label, f"{current_ke:.2f}", 
                 delta=f"Avg: {moving_avg:.2f}")
        
        # Frame info
        frame_count = latest_data.get('frame_count', 0)
        st.metric("🎬 Frame Count", frame_count)
    
    # Historical charts
    if len(st.session_state.analytics_data) > 1:
        st.subheader("📈 Historical Analytics")
        
        # Prepare data for plotting
        df_data = []
        for data in st.session_state.analytics_data:
            row = {
                'timestamp': data.get('timestamp', datetime.now()),
                'person_count': data.get('person_count', 0),
                'max_density': data.get('density', {}).get('max_density', 0),
                'motion_coherence': data.get('motion_coherence', {}).get('std_deviation', 0),
                'kinetic_energy': data.get('kinetic_energy', {}).get('current', 0),
                'ke_moving_avg': data.get('kinetic_energy', {}).get('moving_average', 0),
                'status': data.get('status', 'UNKNOWN')
            }
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Person Count', 'Density', 'Motion Coherence', 'Kinetic Energy'),
            vertical_spacing=0.12
        )
        
        # Person count
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['person_count'], 
                      name='Person Count', line=dict(color='blue')),
            row=1, col=1
        )
        
        # Density with thresholds
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['max_density'], 
                      name='Max Density', line=dict(color='green')),
            row=1, col=2
        )
        fig.add_hline(y=4.0, line_dash="dash", line_color="orange", 
                     annotation_text="Warning", row=1, col=2)
        fig.add_hline(y=6.0, line_dash="dash", line_color="red", 
                     annotation_text="Critical", row=1, col=2)
        
        # Motion coherence with thresholds
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['motion_coherence'], 
                      name='Motion Coherence', line=dict(color='purple')),
            row=2, col=1
        )
        fig.add_hline(y=40.0, line_dash="dash", line_color="orange", 
                     annotation_text="Warning", row=2, col=1)
        fig.add_hline(y=65.0, line_dash="dash", line_color="red", 
                     annotation_text="Critical", row=2, col=1)
        
        # Kinetic energy
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['kinetic_energy'], 
                      name='Current KE', line=dict(color='red')),
            row=2, col=2
        )
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['ke_moving_avg'], 
                      name='Moving Avg', line=dict(color='orange', dash='dash')),
            row=2, col=2
        )
        
        fig.update_layout(height=600, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
        
        # Status timeline
        st.subheader("🚨 Status Timeline")
        status_colors = {'NORMAL': 'green', 'WARNING': 'orange', 'CRITICAL': 'red'}
        status_fig = px.scatter(df, x='timestamp', y='status', 
                               color='status', color_discrete_map=status_colors,
                               title="System Status Over Time")
        status_fig.update_traces(marker_size=10)
        st.plotly_chart(status_fig, use_container_width=True)
    
    # Data table
    with st.expander("📋 Raw Data (Latest 10 entries)"):
        if st.session_state.analytics_data:
            recent_data = st.session_state.analytics_data[-10:]
            display_data = []
            for data in recent_data:
                display_row = {
                    'Timestamp': data.get('timestamp', 'N/A'),
                    'Frame': data.get('frame_count', 0),
                    'Persons': data.get('person_count', 0),
                    'Max Density': data.get('density', {}).get('max_density', 0),
                    'Motion Coherence': data.get('motion_coherence', {}).get('std_deviation', 0),
                    'Kinetic Energy': data.get('kinetic_energy', {}).get('current', 0),
                    'Status': data.get('status', 'UNKNOWN')
                }
                display_data.append(display_row)
            
            st.dataframe(pd.DataFrame(display_data), use_container_width=True)
    
    # Auto-refresh
    time.sleep(refresh_rate)
    st.rerun()

if __name__ == "__main__":
    main()