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

if __name__ == "__main__":
    import uvicorn
    print("Starting Argus Protocol Backend...")
    print("Task 1 Milestone: Single frame processing with YOLO detections")
    print("Test endpoints:")
    print("  - http://127.0.0.1:8000/ (API status)")
    print("  - http://127.0.0.1:8000/test_frame (test frame with detections)")
    print("  - http://127.0.0.1:8000/test_frame_with_video (webcam or test pattern)")
    
    uvicorn.run(app, host="127.0.0.1", port=8000)