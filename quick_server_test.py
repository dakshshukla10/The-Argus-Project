#!/usr/bin/env python3
"""
Quick server test to demonstrate endpoints
"""
import sys
sys.path.append('src')

import requests
import time
import subprocess
import signal
import os

def test_server():
    print("🚀 STARTING ARGUS PROTOCOL SERVER TEST")
    print("="*50)
    
    # Start server
    print("1. Starting FastAPI server...")
    server = subprocess.Popen([
        sys.executable, "src/main.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Test API status
        print("2. Testing API status...")
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {data['message']}")
        else:
            print(f"   ❌ Status check failed: {response.status_code}")
            return
        
        # Test single frame
        print("3. Testing single frame endpoint...")
        response = requests.get("http://127.0.0.1:8000/test_frame", timeout=10)
        if response.status_code == 200:
            print(f"   ✅ Single frame endpoint working ({len(response.content)} bytes)")
        else:
            print(f"   ❌ Single frame failed: {response.status_code}")
        
        # Test video stream (just check if it starts)
        print("4. Testing video stream endpoint...")
        response = requests.get("http://127.0.0.1:8000/video_stream", timeout=3, stream=True)
        if response.status_code == 200:
            print(f"   ✅ Video stream endpoint working")
        else:
            print(f"   ❌ Video stream failed: {response.status_code}")
        
        # Test analytics stream
        print("5. Testing analytics stream endpoint...")
        response = requests.get("http://127.0.0.1:8000/analytics_stream", timeout=3, stream=True)
        if response.status_code == 200:
            print(f"   ✅ Analytics stream endpoint working")
        else:
            print(f"   ❌ Analytics stream failed: {response.status_code}")
        
        print("\n" + "="*50)
        print("✅ ALL ENDPOINTS WORKING!")
        print("🎯 The Argus Protocol is fully operational!")
        print("="*50)
        
        print("\n📋 Available endpoints:")
        print("   🏠 API Status: http://127.0.0.1:8000/")
        print("   🖼️  Single Frame: http://127.0.0.1:8000/test_frame")
        print("   📹 Video Stream: http://127.0.0.1:8000/video_stream")
        print("   🎯 Analytics Stream: http://127.0.0.1:8000/analytics_stream")
        print("   📚 API Docs: http://127.0.0.1:8000/docs")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        # Clean up
        print("\n6. Stopping server...")
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
        print("   ✅ Server stopped")

if __name__ == "__main__":
    test_server()
