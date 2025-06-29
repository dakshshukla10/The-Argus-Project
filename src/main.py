"""
FastAPI backend for The Argus Protocol.
Handles video processing, person detection, tracking, and analytics.
Provides HTTP endpoints for video streaming and WebSocket for real-time data.
"""

import cv2
import numpy as np
from fastapi import FastAPI, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import io
import os
import sys
import time
import math
import asyncio

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.detection import PersonDetector
from engine.core_pipeline import ArgusCorePipeline
from config import VIDEO_RESOLUTION, PROCESSING_FPS
import json

app = FastAPI(title="Argus Protocol Backend", description="Real-time crowd analytics system")

# Initialize components
detector = PersonDetector()
core_pipeline = ArgusCorePipeline()

@app.get("/")
async def root():
    """Root endpoint to check if the API is running."""
    return {"message": "Argus Protocol Backend is running", "status": "active"}

@app.get("/test_frame")
async def get_test_frame():
    """
    Test endpoint that returns a single processed frame with YOLO detections.
    This satisfies Task 1 milestone: A single image is returned via HTTP request.
    """
    try:
        # Create a test frame (black image for now)
        # In a real scenario, this would be from a video file or camera
        test_frame = np.zeros((VIDEO_RESOLUTION[1], VIDEO_RESOLUTION[0], 3), dtype=np.uint8)
        
        # Add some text to make it visible
        cv2.putText(test_frame, "Argus Protocol - Test Frame", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(test_frame, f"Resolution: {VIDEO_RESOLUTION[0]}x{VIDEO_RESOLUTION[1]}", (50, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Perform person detection
        detections = detector.detect_persons(test_frame)
        
        # Draw detections on frame
        processed_frame = detector.draw_detections(test_frame, detections)
        
        # Add detection count to frame
        cv2.putText(processed_frame, f"Persons detected: {len(detections)}", (50, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Convert frame to JPEG
        _, buffer = cv2.imencode('.jpg', processed_frame)
        
        # Return as image response
        return Response(content=buffer.tobytes(), media_type="image/jpeg")
        
    except Exception as e:
        # Log detailed error for debugging
        print(f"Frame processing error: {str(e)}")
        return {"error": "Frame processing failed. Please check server logs."}

@app.get("/test_frame_with_video")
async def get_test_frame_with_video():
    """
    Test endpoint that processes a frame from webcam or test pattern if available.
    """
    try:
        # Try to open webcam, fallback to test pattern
        cap = cv2.VideoCapture(0)
        
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # Resize frame to target resolution
                frame = cv2.resize(frame, VIDEO_RESOLUTION)
            else:
                # Fallback to test pattern
                frame = create_test_pattern()
        else:
            # Fallback to test pattern
            frame = create_test_pattern()
        
        # Perform person detection
        detections = detector.detect_persons(frame)
        
        # Draw detections on frame
        processed_frame = detector.draw_detections(frame, detections)
        
        # Add detection info to frame
        cv2.putText(processed_frame, f"Persons detected: {len(detections)}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(processed_frame, "Argus Protocol - Live Detection", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Convert frame to JPEG
        _, buffer = cv2.imencode('.jpg', processed_frame)
        
        # Return as image response
        return Response(content=buffer.tobytes(), media_type="image/jpeg")
        
    except Exception as e:
        # Log detailed error for debugging  
        print(f"Video frame processing error: {str(e)}")
        return {"error": "Video frame processing failed. Please check server logs."}

@app.get("/video_stream")
async def video_stream():
    """
    Basic video streaming endpoint with YOLO detections.
    This satisfies Task 2 milestone: A live video stream with YOLO detections.
    """
    def generate_frames():
        # Try to open webcam first, fallback to test pattern generation
        cap = cv2.VideoCapture(0)
        frame_count = 0
        
        # If webcam is not available, we'll generate test patterns
        use_webcam = cap.isOpened()
        
        try:
            while True:
                if use_webcam:
                    ret, frame = cap.read()
                    if not ret:
                        # If webcam fails, switch to test pattern
                        use_webcam = False
                        cap.release()
                        frame = create_test_pattern()
                    else:
                        # Resize webcam frame to target resolution
                        frame = cv2.resize(frame, VIDEO_RESOLUTION)
                else:
                    # Generate test pattern
                    frame = create_test_pattern()
                
                # Perform person detection only (no tracking/analytics for basic stream)
                detections = detector.detect_persons(frame)
                processed_frame = detector.draw_detections(frame, detections)
                
                # Add detection info to frame
                cv2.putText(processed_frame, f"Persons detected: {len(detections)}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(processed_frame, "Argus Protocol - Basic Stream", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(processed_frame, f"Source: {'Webcam' if use_webcam else 'Test Pattern'}", 
                           (10, VIDEO_RESOLUTION[1] - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Encode frame as JPEG
                _, buffer = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                
                # Yield frame in multipart format
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                
                frame_count += 1
                
                # Control frame rate
                time.sleep(1.0 / PROCESSING_FPS)
                
        except Exception as e:
            print(f"Error in video stream: {e}")
        finally:
            if cap.isOpened():
                cap.release()
    
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/analytics_stream")
async def analytics_stream():
    """
    Advanced video streaming with full analytics pipeline.
    This satisfies Task 3 milestone: SORT tracking + 3 core metrics calculation with console output.
    """
    def generate_analytics_frames():
        # Try to open webcam first, fallback to test pattern generation
        cap = cv2.VideoCapture(0)
        frame_count = 0
        
        # If webcam is not available, we'll generate test patterns
        use_webcam = cap.isOpened()
        
        try:
            while True:
                if use_webcam:
                    ret, frame = cap.read()
                    if not ret:
                        # If webcam fails, switch to test pattern
                        use_webcam = False
                        cap.release()
                        frame = create_test_pattern_with_motion(frame_count)
                    else:
                        # Resize webcam frame to target resolution
                        frame = cv2.resize(frame, VIDEO_RESOLUTION)
                else:
                    # Generate test pattern with simulated motion
                    frame = create_test_pattern_with_motion(frame_count)
                
                # Process frame through complete pipeline
                processed_frame, analytics_data = core_pipeline.process_frame(frame)
                
                # Print analytics to console (Task 3 milestone requirement)
                if frame_count % 15 == 0:  # Print every second (15 FPS)
                    print("\n" + "="*60)
                    print(f"🎯 ARGUS ANALYTICS - Frame {analytics_data['frame_count']}")
                    print("="*60)
                    print(f"📊 Person Count: {analytics_data['person_count']}")
                    print(f"🏘️  Max Density: {analytics_data['density']['max_density']:.1f} persons/cell")
                    print(f"🌊 Motion Coherence: {analytics_data['motion_coherence']['std_deviation']:.1f}° std dev")
                    print(f"⚡ Kinetic Energy: {analytics_data['kinetic_energy']['current']:.2f}")
                    print(f"📈 KE Moving Avg: {analytics_data['kinetic_energy']['moving_average']:.2f}")
                    print(f"🚨 Status: {analytics_data['status']}")
                    if analytics_data['kinetic_energy']['spike_detected']:
                        print("⚠️  KINETIC ENERGY SPIKE DETECTED!")
                    print("="*60)
                
                # Add source info
                cv2.putText(processed_frame, f"Source: {'Webcam' if use_webcam else 'Test Pattern'}", 
                           (10, VIDEO_RESOLUTION[1] - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Encode frame as JPEG
                _, buffer = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                
                # Yield frame in multipart format
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                
                frame_count += 1
                
                # Control frame rate
                time.sleep(1.0 / PROCESSING_FPS)
                
        except Exception as e:
            print(f"Error in analytics stream: {e}")
        finally:
            if cap.isOpened():
                cap.release()
    
    return StreamingResponse(generate_analytics_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected clients
                self.active_connections.remove(connection)

manager = ConnectionManager()

@app.websocket("/ws/analytics")
async def websocket_analytics(websocket: WebSocket):
    """
    WebSocket endpoint for real-time analytics data streaming.
    This satisfies Task 4 milestone: WebSocket endpoint broadcasting analytics JSON.
    """
    await manager.connect(websocket)
    print(f"🔌 WebSocket client connected. Total connections: {len(manager.active_connections)}")
    
    try:
        # Start analytics processing in background
        cap = cv2.VideoCapture(0)
        frame_count = 0
        use_webcam = cap.isOpened()
        
        while True:
            try:
                if use_webcam:
                    ret, frame = cap.read()
                    if not ret:
                        use_webcam = False
                        cap.release()
                        frame = create_test_pattern_with_motion(frame_count)
                    else:
                        frame = cv2.resize(frame, VIDEO_RESOLUTION)
                else:
                    frame = create_test_pattern_with_motion(frame_count)
                
                # Process frame through complete pipeline
                processed_frame, analytics_data = core_pipeline.process_frame(frame)
                
                # Send analytics data via WebSocket
                analytics_json = json.dumps(analytics_data)
                await websocket.send_text(analytics_json)
                
                frame_count += 1
                
                # Control frame rate
                await asyncio.sleep(1.0 / PROCESSING_FPS)
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"Error in WebSocket analytics: {e}")
                break
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"🔌 WebSocket client disconnected. Total connections: {len(manager.active_connections)}")
    finally:
        if cap.isOpened():
            cap.release()

def create_test_pattern_with_motion(frame_count: int) -> np.ndarray:
    """Create a test pattern frame with animated elements to simulate motion."""
    frame = np.zeros((VIDEO_RESOLUTION[1], VIDEO_RESOLUTION[0], 3), dtype=np.uint8)
    
    # Add gradient background
    for i in range(VIDEO_RESOLUTION[1]):
        intensity = int(255 * i / VIDEO_RESOLUTION[1])
        frame[i, :] = [intensity // 3, intensity // 2, intensity]
    
    # Add moving objects to simulate people
    time_factor = frame_count * 0.1
    
    # Moving circle 1 (horizontal movement)
    x1 = int(160 + 100 * math.sin(time_factor))
    y1 = 120
    cv2.circle(frame, (x1, y1), 30, (255, 255, 255), -1)
    
    # Moving rectangle (vertical movement)
    y2 = int(250 + 50 * math.sin(time_factor * 0.7))
    cv2.rectangle(frame, (300, y2), (400, y2 + 100), (255, 255, 255), -1)
    
    # Moving circle 2 (diagonal movement)
    x3 = int(500 + 80 * math.cos(time_factor * 1.2))
    y3 = int(150 + 60 * math.sin(time_factor * 1.2))
    cv2.circle(frame, (x3, y3), 25, (255, 255, 255), -1)
    
    # Add more moving objects to create crowd-like scenario
    for i in range(3):
        x = int(100 + i * 150 + 50 * math.sin(time_factor + i))
        y = int(350 + 30 * math.cos(time_factor * 0.8 + i))
        cv2.circle(frame, (x, y), 20, (200, 200, 200), -1)
    
    # Add title
    cv2.putText(frame, "Argus Protocol - Animated Test", (50, 50), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(frame, f"Frame: {frame_count}", (50, 80), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    return frame

def create_test_pattern() -> np.ndarray:
    """Create a test pattern frame with some visual elements."""
    frame = np.zeros((VIDEO_RESOLUTION[1], VIDEO_RESOLUTION[0], 3), dtype=np.uint8)
    
    # Add gradient background
    for i in range(VIDEO_RESOLUTION[1]):
        intensity = int(255 * i / VIDEO_RESOLUTION[1])
        frame[i, :] = [intensity // 3, intensity // 2, intensity]
    
    # Add some geometric shapes to simulate objects
    cv2.circle(frame, (160, 120), 30, (255, 255, 255), -1)
    cv2.rectangle(frame, (300, 200), (400, 300), (255, 255, 255), -1)
    cv2.circle(frame, (500, 150), 25, (255, 255, 255), -1)
    
    # Add title
    cv2.putText(frame, "Argus Protocol Test Pattern", (50, 50), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    return frame

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Argus Protocol Backend...")
    print("✅ Task 1: Single frame processing with YOLO detections")
    print("✅ Task 2: Video streaming with YOLO detections")
    print("✅ Task 3: SORT tracking + 3 core metrics calculation")
    print("")
    print("📡 Available endpoints:")
    print("  - http://127.0.0.1:8000/ (API status)")
    print("  - http://127.0.0.1:8000/test_frame (single frame with detections)")
    print("  - http://127.0.0.1:8000/video_stream (basic video stream)")
    print("  - http://127.0.0.1:8000/analytics_stream (FULL ANALYTICS PIPELINE)")
    print("  - http://127.0.0.1:8000/test_frame_with_video (webcam or test pattern)")
    print("  - ws://127.0.0.1:8000/ws/analytics (WebSocket for real-time analytics)")
    print("")
    print("🎯 For LIVE ANALYTICS with console output:")
    print("   👉 Open: http://127.0.0.1:8000/analytics_stream")
    print("   👀 Watch this console for real-time metrics!")
    print("")
    print("📊 For DASHBOARD (Task 4):")
    print("   👉 Run: streamlit run dashboard.py --server.port 8501")
    print("   👉 Open: http://127.0.0.1:8501")
    print("   📡 Dashboard connects to WebSocket for real-time data")
    print("")
    print("=" * 60)
    
    uvicorn.run(app, host="127.0.0.1", port=8000)