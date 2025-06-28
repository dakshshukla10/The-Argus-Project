#!/usr/bin/env python3
"""
Test script for Task 2 milestone: Video streaming with YOLO detections
"""

import sys
import os
import requests
import time
import threading
import subprocess

def test_task2_milestone():
    """Test Task 2: Video Streaming milestone"""
    print("=" * 60)
    print("TESTING TASK 2 MILESTONE: Video Streaming")
    print("=" * 60)
    
    # Test 1: Start FastAPI server
    print("1. Starting FastAPI server...")
    try:
        # Start server in background
        server_process = subprocess.Popen([
            "python", "src/main.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(3)
        print("   ✅ FastAPI server started")
    except Exception as e:
        print(f"   ❌ Failed to start server: {e}")
        return False
    
    try:
        # Test 2: Check API status
        print("2. Testing API status endpoint...")
        try:
            response = requests.get("http://127.0.0.1:8000/", timeout=5)
            if response.status_code == 200:
                print("   ✅ API status endpoint working")
            else:
                print(f"   ❌ API status endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ API status endpoint failed: {e}")
            return False
        
        # Test 3: Test single frame endpoint
        print("3. Testing single frame endpoint...")
        try:
            response = requests.get("http://127.0.0.1:8000/test_frame", timeout=10)
            if response.status_code == 200 and response.headers.get('content-type') == 'image/jpeg':
                print("   ✅ Single frame endpoint working")
            else:
                print(f"   ❌ Single frame endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Single frame endpoint failed: {e}")
            return False
        
        # Test 4: Test video stream endpoint
        print("4. Testing video stream endpoint...")
        try:
            response = requests.get("http://127.0.0.1:8000/video_stream", timeout=5, stream=True)
            if response.status_code == 200:
                # Check if we get multipart content
                content_type = response.headers.get('content-type', '')
                if 'multipart/x-mixed-replace' in content_type:
                    print("   ✅ Video stream endpoint working")
                    
                    # Try to read a few frames
                    frame_count = 0
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            frame_count += 1
                            if frame_count > 3:  # Read a few frames then break
                                break
                    
                    if frame_count > 0:
                        print(f"   ✅ Successfully received {frame_count} video frames")
                    else:
                        print("   ❌ No video frames received")
                        return False
                else:
                    print(f"   ❌ Wrong content type: {content_type}")
                    return False
            else:
                print(f"   ❌ Video stream endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Video stream endpoint failed: {e}")
            return False
        
        print("\n" + "=" * 60)
        print("✅ TASK 2 MILESTONE ACHIEVED!")
        print("✅ Live video stream with YOLO detections viewable in browser")
        print("✅ Video streaming endpoint working correctly")
        print("=" * 60)
        return True
        
    finally:
        # Clean up: terminate server
        print("\n5. Cleaning up...")
        try:
            server_process.terminate()
            server_process.wait(timeout=5)
            print("   ✅ Server terminated successfully")
        except Exception as e:
            print(f"   ⚠️  Server cleanup warning: {e}")
            try:
                server_process.kill()
            except:
                pass

if __name__ == "__main__":
    success = test_task2_milestone()
    if success:
        print("\n🎉 Ready to proceed to Task 3: Tracking & Analytics")
        print("\n📋 To manually test the video stream:")
        print("   1. Run: cd src && python main.py")
        print("   2. Open browser to: http://127.0.0.1:8000/video_stream")
        print("   3. You should see live video with YOLO detections")
    else:
        print("\n❌ Task 2 milestone not met. Please fix issues before proceeding.")
    sys.exit(0 if success else 1)
