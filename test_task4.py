#!/usr/bin/env python3
"""
Test script for Task 4 milestone: WebSocket & Dashboard Integration
"""

import sys
import os
import time
import json
import requests
import websocket
import threading
import subprocess
from datetime import datetime

def test_task4_milestone():
    """Test Task 4: WebSocket & Dashboard Integration milestone"""
    print("=" * 60)
    print("TESTING TASK 4 MILESTONE: WebSocket & Dashboard Integration")
    print("=" * 60)
    
    # Test 1: Backend API Status
    print("1. Testing backend API status...")
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend API is running")
        else:
            print("   ❌ Backend API returned non-200 status")
            return False
    except Exception as e:
        print(f"   ❌ Backend API not accessible: {e}")
        print("   💡 Make sure to run: cd src && python main.py")
        return False
    
    # Test 2: WebSocket Endpoint
    print("2. Testing WebSocket endpoint...")
    websocket_data = []
    websocket_connected = False
    websocket_error = None
    
    def on_message(ws, message):
        try:
            data = json.loads(message)
            websocket_data.append(data)
            print(f"   📡 Received WebSocket data: Frame {data.get('frame_count', 'N/A')}")
        except Exception as e:
            print(f"   ❌ Error parsing WebSocket message: {e}")
    
    def on_error(ws, error):
        nonlocal websocket_error
        websocket_error = error
        print(f"   ❌ WebSocket error: {error}")
    
    def on_close(ws, close_status_code, close_msg):
        print("   🔌 WebSocket connection closed")
    
    def on_open(ws):
        nonlocal websocket_connected
        websocket_connected = True
        print("   ✅ WebSocket connection opened")
    
    try:
        ws = websocket.WebSocketApp("ws://127.0.0.1:8000/ws/analytics",
                                  on_open=on_open,
                                  on_message=on_message,
                                  on_error=on_error,
                                  on_close=on_close)
        
        # Run WebSocket in background thread
        ws_thread = threading.Thread(target=ws.run_forever, daemon=True)
        ws_thread.start()
        
        # Wait for connection and data
        timeout = 10
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if websocket_connected and len(websocket_data) > 0:
                break
            time.sleep(0.5)
        
        ws.close()
        
        if not websocket_connected:
            print("   ❌ WebSocket connection failed")
            if websocket_error:
                print(f"      Error: {websocket_error}")
            return False
        
        if len(websocket_data) == 0:
            print("   ❌ No data received from WebSocket")
            return False
        
        print(f"   ✅ WebSocket working - received {len(websocket_data)} data packets")
        
        # Validate data structure
        sample_data = websocket_data[0]
        required_keys = ['frame_count', 'person_count', 'density', 'motion_coherence', 'kinetic_energy', 'status']
        missing_keys = [key for key in required_keys if key not in sample_data]
        
        if missing_keys:
            print(f"   ❌ WebSocket data missing keys: {missing_keys}")
            return False
        
        print("   ✅ WebSocket data structure validated")
        
    except Exception as e:
        print(f"   ❌ WebSocket test failed: {e}")
        return False
    
    # Test 3: Dashboard Dependencies
    print("3. Testing dashboard dependencies...")
    try:
        import streamlit
        import plotly
        import pandas
        import websocket as ws_client
        print("   ✅ All dashboard dependencies available")
    except ImportError as e:
        print(f"   ❌ Missing dashboard dependency: {e}")
        print("   💡 Run: pip install streamlit plotly pandas websocket-client")
        return False
    
    # Test 4: Dashboard File Exists
    print("4. Testing dashboard file...")
    dashboard_path = "src/dashboard.py"
    if os.path.exists(dashboard_path):
        print("   ✅ Dashboard file exists")
        
        # Check if dashboard can be imported
        try:
            sys.path.append('src')
            # Just check if the file can be read and has main components
            with open(dashboard_path, 'r') as f:
                content = f.read()
                
            required_components = [
                'streamlit',
                'websocket',
                'WEBSOCKET_URL',
                'VIDEO_STREAM_URL',
                'def main',
                'st.title'
            ]
            
            missing_components = [comp for comp in required_components if comp not in content]
            if missing_components:
                print(f"   ❌ Dashboard missing components: {missing_components}")
                return False
            
            print("   ✅ Dashboard file structure validated")
            
        except Exception as e:
            print(f"   ❌ Dashboard file validation failed: {e}")
            return False
    else:
        print("   ❌ Dashboard file not found")
        return False
    
    # Test 5: Video Stream Endpoint
    print("5. Testing video stream endpoint...")
    try:
        response = requests.get("http://127.0.0.1:8000/analytics_stream", timeout=5, stream=True)
        if response.status_code == 200:
            print("   ✅ Video stream endpoint accessible")
        else:
            print(f"   ❌ Video stream returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Video stream test failed: {e}")
        return False
    
    # Test 6: Sample Analytics Data Validation
    print("6. Validating analytics data format...")
    if websocket_data:
        sample = websocket_data[0]
        
        # Check data types and ranges
        validations = [
            ('frame_count', int, lambda x: x >= 0),
            ('person_count', int, lambda x: x >= 0),
            ('status', str, lambda x: x in ['NORMAL', 'WARNING', 'CRITICAL'])
        ]
        
        for key, expected_type, validator in validations:
            if key in sample:
                value = sample[key]
                if not isinstance(value, expected_type):
                    print(f"   ❌ {key} has wrong type: {type(value)} (expected {expected_type})")
                    return False
                if not validator(value):
                    print(f"   ❌ {key} has invalid value: {value}")
                    return False
        
        print("   ✅ Analytics data format validated")
        
        # Display sample data
        print("   📋 Sample analytics data:")
        print(f"      - Frame: {sample.get('frame_count', 'N/A')}")
        print(f"      - Persons: {sample.get('person_count', 'N/A')}")
        print(f"      - Status: {sample.get('status', 'N/A')}")
        print(f"      - Density: {sample.get('density', {}).get('max_density', 'N/A')}")
        print(f"      - Coherence: {sample.get('motion_coherence', {}).get('std_deviation', 'N/A')}")
        print(f"      - Kinetic Energy: {sample.get('kinetic_energy', {}).get('current', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("✅ TASK 4 MILESTONE ACHIEVED!")
    print("✅ WebSocket endpoint broadcasting analytics JSON")
    print("✅ Dashboard file created with all required components")
    print("✅ Video stream endpoint accessible for dashboard")
    print("✅ Real-time data streaming working")
    print("=" * 60)
    return True

def test_dashboard_launch():
    """Test if dashboard can be launched (optional - requires manual verification)"""
    print("\n" + "=" * 60)
    print("OPTIONAL: Dashboard Launch Test")
    print("=" * 60)
    
    print("To complete Task 4 testing, manually verify the dashboard:")
    print("")
    print("1. 🚀 Start the backend (if not already running):")
    print("   cd src && python main.py")
    print("")
    print("2. 🎨 Start the dashboard:")
    print("   cd src && streamlit run dashboard.py --server.port 8501")
    print("")
    print("3. 🌐 Open dashboard in browser:")
    print("   http://127.0.0.1:8501")
    print("")
    print("4. ✅ Verify the dashboard shows:")
    print("   - Live video stream with detections")
    print("   - Real-time updating graphs")
    print("   - System status indicator (NORMAL/WARNING/CRITICAL)")
    print("   - Current metrics (person count, density, coherence, kinetic energy)")
    print("   - Historical charts")
    print("")
    print("5. 🔄 Verify real-time updates:")
    print("   - Graphs should update automatically")
    print("   - Status should change based on analytics")
    print("   - Video stream should show live processing")
    print("")
    print("=" * 60)

if __name__ == "__main__":
    success = test_task4_milestone()
    
    if success:
        print("\n🎉 Task 4 milestone achieved!")
        test_dashboard_launch()
        print("\n📋 Next steps:")
        print("   1. Test the complete system manually")
        print("   2. Proceed to Task 5: Refinement & Demo Polish")
    else:
        print("\n❌ Task 4 milestone not met. Please fix issues before proceeding.")
    
    sys.exit(0 if success else 1)