#!/usr/bin/env python3
"""
Test script for Task 1 milestone: Single frame processing with YOLO detections
"""

import sys
import os
sys.path.append('src')

from src.engine.detection import PersonDetector
from src.config import VIDEO_RESOLUTION
import cv2
import numpy as np

def test_task1_milestone():
    """Test Task 1: Setup & Detection milestone"""
    print("=" * 60)
    print("TESTING TASK 1 MILESTONE: Setup & Detection")
    print("=" * 60)
    
    # Test 1: PersonDetector initialization
    print("1. Testing PersonDetector initialization...")
    try:
        detector = PersonDetector()
        print("   ✅ PersonDetector initialized successfully")
    except Exception as e:
        print(f"   ❌ PersonDetector initialization failed: {e}")
        return False
    
    # Test 2: Create test frame
    print("2. Creating test frame...")
    try:
        test_frame = np.zeros((VIDEO_RESOLUTION[1], VIDEO_RESOLUTION[0], 3), dtype=np.uint8)
        # Add some visual elements
        cv2.putText(test_frame, "Argus Protocol Test", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        print(f"   ✅ Test frame created: {VIDEO_RESOLUTION[0]}x{VIDEO_RESOLUTION[1]}")
    except Exception as e:
        print(f"   ❌ Test frame creation failed: {e}")
        return False
    
    # Test 3: Person detection
    print("3. Testing person detection...")
    try:
        detections = detector.detect_persons(test_frame)
        print(f"   ✅ Detection completed: {len(detections)} persons detected")
    except Exception as e:
        print(f"   ❌ Person detection failed: {e}")
        return False
    
    # Test 4: Draw detections
    print("4. Testing detection visualization...")
    try:
        processed_frame = detector.draw_detections(test_frame, detections)
        print("   ✅ Detection visualization completed")
    except Exception as e:
        print(f"   ❌ Detection visualization failed: {e}")
        return False
    
    # Test 5: Save test result
    print("5. Saving test result...")
    try:
        cv2.imwrite("task1_test_result.jpg", processed_frame)
        print("   ✅ Test result saved as 'task1_test_result.jpg'")
    except Exception as e:
        print(f"   ❌ Failed to save test result: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ TASK 1 MILESTONE ACHIEVED!")
    print("✅ Single frame processing with YOLO detections working")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_task1_milestone()
    if success:
        print("\n🎉 Ready to proceed to Task 2: Video Streaming")
    else:
        print("\n❌ Task 1 milestone not met. Please fix issues before proceeding.")
    sys.exit(0 if success else 1)