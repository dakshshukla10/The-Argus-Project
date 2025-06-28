"""
FastAPI backend for The Argus Protocol.
Handles video processing, person detection, tracking, and analytics.
Provides HTTP endpoints for video streaming and WebSocket for real-time data.
"""

import cv2
import numpy as np
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
import io
import os
import sys
import time
import math

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.detection import PersonDetector
from config import VIDEO_RESOLUTION, PROCESSING_FPS

app = FastAPI(title="Argus Protocol Backend", description="Real-time crowd analytics system")

# Initialize components
detector = PersonDetector()

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
        return {"error": f"Failed to process frame: {str(e)}"}

@app.get("/video_stream")
async def video_stream():
    """
    Video streaming endpoint that returns a continuous stream of processed frames.
    This satisfies Task 2 milestone: Live video stream with YOLO detections viewable in browser.
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
                        frame = create_test_pattern_with_motion(frame_count)
                    else:
                        # Resize webcam frame to target resolution
                        frame = cv2.resize(frame, VIDEO_RESOLUTION)
                else:
                    # Generate test pattern with simulated motion
                    frame = create_test_pattern_with_motion(frame_count)
                
                # Perform person detection
                detections = detector.detect_persons(frame)
                
                # Draw detections on frame
                processed_frame = detector.draw_detections(frame, detections)
                
                # Add overlay information
                cv2.putText(processed_frame, f"Frame: {frame_count}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(processed_frame, f"Persons: {len(detections)}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(processed_frame, "Argus Protocol - Live Stream", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(processed_frame, f"Source: {'Webcam' if use_webcam else 'Test Pattern'}", (10, 120), 
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
        return {"error": f"Failed to process video frame: {str(e)}"}

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

if __name__ == "__main__":
    import uvicorn
    print("Starting Argus Protocol Backend...")
    print("Task 1 ✅: Single frame processing with YOLO detections")
    print("Task 2 🚀: Video streaming with YOLO detections")
    print("Available endpoints:")
    print("  - http://127.0.0.1:8000/ (API status)")
    print("  - http://127.0.0.1:8000/test_frame (single frame with detections)")
    print("  - http://127.0.0.1:8000/video_stream (live video stream)")
    print("  - http://127.0.0.1:8000/test_frame_with_video (webcam or test pattern)")
    
    uvicorn.run(app, host="127.0.0.1", port=8000)
