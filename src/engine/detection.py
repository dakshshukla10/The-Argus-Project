"""
Person detection using YOLOv8.
Handles loading the model and performing inference on video frames.
"""

import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple, Optional
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import YOLO_MODEL_PATH


class PersonDetector:
    """
    YOLOv8-based person detector for crowd analytics.
    """
    
    def __init__(self, model_path: str = YOLO_MODEL_PATH, confidence_threshold: float = 0.5):
        """
        Initialize the person detector.
        
        Args:
            model_path: Path to the YOLOv8 model file
            confidence_threshold: Minimum confidence for detections
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the YOLOv8 model."""
        try:
            self.model = YOLO(self.model_path)
            print(f"YOLOv8 model loaded successfully from {self.model_path}")
        except Exception as e:
            print(f"Error loading YOLOv8 model: {e}")
            # If model file doesn't exist, download it
            if not os.path.exists(self.model_path):
                print("Model file not found. Downloading yolov8n.pt...")
                os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
                self.model = YOLO('yolov8n.pt')  # This will download the model
                # Save the model to the specified path
                self.model.save(self.model_path)
                print(f"Model saved to {self.model_path}")
    
    def detect_persons(self, frame: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """
        Detect persons in a frame.
        
        Args:
            frame: Input frame as numpy array
            
        Returns:
            List of detections as (x1, y1, x2, y2, confidence) tuples
        """
        if self.model is None:
            return []
        
        try:
            # Run inference
            results = self.model(frame, verbose=False)
            
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get class ID (0 is person in COCO dataset)
                        class_id = int(box.cls[0])
                        if class_id == 0:  # Person class
                            confidence = float(box.conf[0])
                            if confidence >= self.confidence_threshold:
                                # Get bounding box coordinates
                                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                                detections.append((int(x1), int(y1), int(x2), int(y2), confidence))
            
            return detections
            
        except Exception as e:
            print(f"Error during detection: {e}")
            return []
    
    def draw_detections(self, frame: np.ndarray, detections: List[Tuple[int, int, int, int, float]]) -> np.ndarray:
        """
        Draw bounding boxes on the frame.
        
        Args:
            frame: Input frame
            detections: List of detections as (x1, y1, x2, y2, confidence) tuples
            
        Returns:
            Frame with drawn bounding boxes
        """
        frame_copy = frame.copy()
        
        for x1, y1, x2, y2, confidence in detections:
            # Draw bounding box
            cv2.rectangle(frame_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw confidence score
            label = f"Person: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(frame_copy, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), (0, 255, 0), -1)
            cv2.putText(frame_copy, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        return frame_copy


def test_detection():
    """Test function for the person detector."""
    detector = PersonDetector()
    
    # Create a test frame (you can replace this with actual video frame)
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Test detection
    detections = detector.detect_persons(test_frame)
    print(f"Detected {len(detections)} persons")
    
    # Test drawing
    result_frame = detector.draw_detections(test_frame, detections)
    print("Detection test completed successfully")


if __name__ == "__main__":
    test_detection()