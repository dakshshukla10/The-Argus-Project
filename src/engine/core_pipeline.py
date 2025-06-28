"""
Core processing pipeline for The Argus Protocol.
Integrates detection, tracking, and analytics into a unified processing flow.
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.detection import PersonDetector
from engine.tracking import Sort
from engine.analytics import CrowdAnalytics
from config import VIDEO_RESOLUTION


class ArgusCorePipeline:
    """
    Main processing pipeline that orchestrates detection, tracking, and analytics
    """
    
    def __init__(self):
        """Initialize the core pipeline components"""
        print("Initializing Argus Core Pipeline...")
        
        # Initialize components
        self.detector = PersonDetector()
        self.tracker = Sort(max_age=30, min_hits=3, iou_threshold=0.3)
        self.analytics = CrowdAnalytics()
        
        # Pipeline state
        self.frame_count = 0
        self.is_initialized = True
        
        print("✅ Argus Core Pipeline initialized successfully")
    
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """
        Process a single frame through the complete pipeline
        
        Args:
            frame: Input frame as numpy array
            
        Returns:
            Tuple of (processed_frame, analytics_data)
        """
        self.frame_count += 1
        
        # Step 1: Person Detection
        detections = self.detector.detect_persons(frame)
        
        # Step 2: Convert detections to SORT format
        if len(detections) > 0:
            # Convert from (x1, y1, x2, y2, confidence) to numpy array
            det_array = np.array([[det[0], det[1], det[2], det[3], det[4]] for det in detections])
        else:
            det_array = np.empty((0, 5))
        
        # Step 3: Update tracker
        tracks = self.tracker.update(det_array)
        
        # Step 4: Get tracker information for analytics
        tracker_info = self.tracker.get_trackers()
        
        # Step 5: Perform analytics
        analytics_data = self.analytics.analyze_frame(tracker_info)
        
        # Step 6: Visualize results
        processed_frame = self.visualize_results(frame, tracks, analytics_data)
        
        return processed_frame, analytics_data
    
    def visualize_results(self, frame: np.ndarray, tracks: np.ndarray, analytics_data: Dict) -> np.ndarray:
        """
        Draw visualizations on the frame
        
        Args:
            frame: Input frame
            tracks: Tracking results from SORT
            analytics_data: Analytics results
            
        Returns:
            Frame with visualizations
        """
        vis_frame = frame.copy()
        
        # Draw tracking results
        for track in tracks:
            if len(track) >= 5:
                x1, y1, x2, y2, track_id = track[:5]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                track_id = int(track_id)
                
                # Draw bounding box
                cv2.rectangle(vis_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Draw track ID
                label = f"ID: {track_id}"
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                cv2.rectangle(vis_frame, (x1, y1 - label_size[1] - 10), 
                             (x1 + label_size[0], y1), (0, 255, 0), -1)
                cv2.putText(vis_frame, label, (x1, y1 - 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        # Draw density grid overlay
        self.draw_density_grid(vis_frame, analytics_data['density']['grid'])
        
        # Draw status and metrics overlay
        self.draw_metrics_overlay(vis_frame, analytics_data)
        
        return vis_frame
    
    def draw_density_grid(self, frame: np.ndarray, density_grid: List[List[float]]):
        """
        Draw density grid overlay on frame
        
        Args:
            frame: Frame to draw on
            density_grid: 2D density grid
        """
        grid_height, grid_width = len(density_grid), len(density_grid[0])
        cell_width = VIDEO_RESOLUTION[0] / grid_width
        cell_height = VIDEO_RESOLUTION[1] / grid_height
        
        # Draw grid lines
        for i in range(grid_width + 1):
            x = int(i * cell_width)
            cv2.line(frame, (x, 0), (x, VIDEO_RESOLUTION[1]), (100, 100, 100), 1)
        
        for i in range(grid_height + 1):
            y = int(i * cell_height)
            cv2.line(frame, (0, y), (VIDEO_RESOLUTION[0], y), (100, 100, 100), 1)
        
        # Color cells based on density
        for i in range(grid_height):
            for j in range(grid_width):
                density = density_grid[i][j]
                if density > 0:
                    x1 = int(j * cell_width)
                    y1 = int(i * cell_height)
                    x2 = int((j + 1) * cell_width)
                    y2 = int((i + 1) * cell_height)
                    
                    # Color based on density level
                    if density >= 6.0:  # Critical
                        color = (0, 0, 255, 100)  # Red
                    elif density >= 4.0:  # Warning
                        color = (0, 165, 255, 100)  # Orange
                    else:  # Normal
                        color = (0, 255, 255, 100)  # Yellow
                    
                    # Draw semi-transparent overlay
                    overlay = frame.copy()
                    cv2.rectangle(overlay, (x1, y1), (x2, y2), color[:3], -1)
                    cv2.addWeighted(frame, 0.8, overlay, 0.2, 0, frame)
                    
                    # Draw density value
                    text = f"{density:.0f}"
                    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                    text_x = x1 + (x2 - x1 - text_size[0]) // 2
                    text_y = y1 + (y2 - y1 + text_size[1]) // 2
                    cv2.putText(frame, text, (text_x, text_y), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def draw_metrics_overlay(self, frame: np.ndarray, analytics_data: Dict):
        """
        Draw metrics and status overlay
        
        Args:
            frame: Frame to draw on
            analytics_data: Analytics results
        """
        # Status color
        status = analytics_data['status']
        if status == "CRITICAL":
            status_color = (0, 0, 255)  # Red
        elif status == "WARNING":
            status_color = (0, 165, 255)  # Orange
        else:
            status_color = (0, 255, 0)  # Green
        
        # Draw status box
        cv2.rectangle(frame, (10, 10), (300, 150), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (300, 150), status_color, 2)
        
        # Status text
        cv2.putText(frame, f"STATUS: {status}", (20, 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        # Metrics
        y_offset = 55
        metrics = [
            f"Persons: {analytics_data['person_count']}",
            f"Density: {analytics_data['density']['max_density']:.1f}",
            f"Coherence: {analytics_data['motion_coherence']['std_deviation']:.1f}°",
            f"KE: {analytics_data['kinetic_energy']['current']:.2f}"
        ]
        
        for metric in metrics:
            cv2.putText(frame, metric, (20, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_offset += 20
        
        # Frame info
        cv2.putText(frame, f"Frame: {self.frame_count}", (20, y_offset + 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
    
    def get_pipeline_stats(self) -> Dict:
        """
        Get pipeline statistics
        
        Returns:
            Dictionary with pipeline statistics
        """
        return {
            'frame_count': self.frame_count,
            'is_initialized': self.is_initialized,
            'analytics_stats': self.analytics.get_summary_stats()
        }


def test_core_pipeline():
    """Test function for the core pipeline."""
    print("Testing Argus Core Pipeline...")
    
    # Initialize pipeline
    pipeline = ArgusCorePipeline()
    
    # Create test frame
    test_frame = np.zeros((VIDEO_RESOLUTION[1], VIDEO_RESOLUTION[0], 3), dtype=np.uint8)
    
    # Add some visual elements
    cv2.putText(test_frame, "Core Pipeline Test", (50, 50), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Add some shapes to simulate people
    cv2.rectangle(test_frame, (100, 100), (150, 200), (255, 255, 255), -1)
    cv2.rectangle(test_frame, (300, 150), (350, 250), (255, 255, 255), -1)
    
    # Process frame
    processed_frame, analytics_data = pipeline.process_frame(test_frame)
    
    print("Pipeline Test Results:")
    print(f"✅ Frame processed successfully")
    print(f"✅ Person count: {analytics_data['person_count']}")
    print(f"✅ Status: {analytics_data['status']}")
    print(f"✅ Max density: {analytics_data['density']['max_density']}")
    
    # Save test result
    cv2.imwrite("core_pipeline_test_result.jpg", processed_frame)
    print("✅ Test result saved as 'core_pipeline_test_result.jpg'")
    
    print("Core pipeline test completed successfully!")


if __name__ == "__main__":
    test_core_pipeline()