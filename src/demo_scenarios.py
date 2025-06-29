#!/usr/bin/env python3
"""
Demo scenarios for The Argus Protocol - Task 5 refinement
Creates realistic test scenarios to tune thresholds and demonstrate capabilities
"""

import cv2
import numpy as np
import math
import time
from typing import Tuple, List

class DemoScenarioGenerator:
    """Generate realistic crowd scenarios for testing and demo purposes"""
    
    def __init__(self, resolution: Tuple[int, int] = (640, 480)):
        self.width, self.height = resolution
        self.frame_count = 0

    
    def _draw_realistic_person(self, frame: np.ndarray, x: int, y: int, w: int, h: int):
        """Draw a more realistic person shape that YOLO can detect"""
        # Body (torso)
        torso_w = int(w * 0.8)
        torso_h = int(h * 0.6)
        torso_x = x + (w - torso_w) // 2
        torso_y = y + int(h * 0.25)
        
        cv2.rectangle(frame, (torso_x, torso_y), (torso_x + torso_w, torso_y + torso_h), 
                     (180, 180, 180), -1)
        
        # Head
        head_radius = int(w * 0.25)
        head_x = x + w // 2
        head_y = y + head_radius
        cv2.circle(frame, (head_x, head_y), head_radius, (200, 200, 200), -1)
        
        # Arms
        arm_w = int(w * 0.15)
        arm_h = int(h * 0.4)
        # Left arm
        cv2.rectangle(frame, (torso_x - arm_w, torso_y), 
                     (torso_x, torso_y + arm_h), (160, 160, 160), -1)
        # Right arm  
        cv2.rectangle(frame, (torso_x + torso_w, torso_y), 
                     (torso_x + torso_w + arm_w, torso_y + arm_h), (160, 160, 160), -1)
        
        # Legs
        leg_w = int(w * 0.2)
        leg_h = int(h * 0.4)
        leg_y = torso_y + torso_h
        # Left leg
        cv2.rectangle(frame, (torso_x + int(torso_w * 0.2), leg_y), 
                     (torso_x + int(torso_w * 0.2) + leg_w, leg_y + leg_h), (140, 140, 140), -1)
        # Right leg
        cv2.rectangle(frame, (torso_x + int(torso_w * 0.6), leg_y), 
                     (torso_x + int(torso_w * 0.6) + leg_w, leg_y + leg_h), (140, 140, 140), -1)
        
    def create_normal_crowd_scenario(self) -> np.ndarray:
        """Create a normal, safe crowd scenario"""
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Add gradient background
        for i in range(self.height):
            intensity = int(50 + 100 * i / self.height)
            frame[i, :] = [intensity//3, intensity//2, intensity//4]
        
        # Add 3-5 people spread out (safe density)
        people_positions = [
            (120, 150, 40, 80),   # (x, y, width, height)
            (300, 200, 35, 75),
            (480, 180, 38, 82),
            (200, 320, 42, 85),
        ]
        
        for x, y, w, h in people_positions:
            # Draw person with slight movement
            offset_x = int(5 * math.sin(self.frame_count * 0.1 + x * 0.01))
            offset_y = int(3 * math.cos(self.frame_count * 0.1 + y * 0.01))
            
            self._draw_realistic_person(frame, x + offset_x, y + offset_y, w, h)
        
        # Add title
        cv2.putText(frame, "NORMAL CROWD - Safe Density", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Frame: {self.frame_count}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        self.frame_count += 1
        return frame
    
    def create_warning_crowd_scenario(self) -> np.ndarray:
        """Create a warning-level crowd scenario"""
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Add gradient background
        for i in range(self.height):
            intensity = int(60 + 120 * i / self.height)
            frame[i, :] = [intensity//4, intensity//2, intensity//3]
        
        # Add 8-10 people with moderate density
        people_positions = [
            (80, 120, 35, 70),
            (140, 140, 38, 75),
            (200, 130, 36, 72),
            (260, 150, 40, 78),
            (320, 135, 37, 74),
            (380, 145, 39, 76),
            (100, 250, 38, 75),
            (180, 270, 36, 73),
            (280, 260, 40, 77),
        ]
        
        for i, (x, y, w, h) in enumerate(people_positions):
            # Add more chaotic movement for warning scenario
            offset_x = int(8 * math.sin(self.frame_count * 0.15 + i * 0.5))
            offset_y = int(6 * math.cos(self.frame_count * 0.12 + i * 0.3))
            
            self._draw_realistic_person(frame, x + offset_x, y + offset_y, w, h)
        
        # Add title
        cv2.putText(frame, "WARNING CROWD - Moderate Density", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
        cv2.putText(frame, f"Frame: {self.frame_count}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        self.frame_count += 1
        return frame
    
    def create_critical_crowd_scenario(self) -> np.ndarray:
        """Create a critical/dangerous crowd scenario"""
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Add darker background for critical scenario
        for i in range(self.height):
            intensity = int(40 + 80 * i / self.height)
            frame[i, :] = [intensity//2, intensity//4, intensity//3]
        
        # Add 15+ people with high density and chaotic movement
        people_positions = []
        
        # Dense cluster in center
        for row in range(3):
            for col in range(5):
                x = 150 + col * 45 + np.random.randint(-10, 10)
                y = 150 + row * 50 + np.random.randint(-10, 10)
                w = 30 + np.random.randint(-5, 5)
                h = 65 + np.random.randint(-10, 10)
                people_positions.append((x, y, w, h))
        
        # Additional scattered people
        additional_positions = [
            (50, 100, 32, 68),
            (550, 120, 35, 70),
            (80, 300, 33, 67),
            (500, 280, 36, 72),
        ]
        people_positions.extend(additional_positions)
        
        for i, (x, y, w, h) in enumerate(people_positions):
            # Very chaotic movement for critical scenario
            offset_x = int(15 * math.sin(self.frame_count * 0.2 + i * 0.8))
            offset_y = int(12 * math.cos(self.frame_count * 0.18 + i * 0.6))
            
            self._draw_realistic_person(frame, x + offset_x, y + offset_y, w, h)
        
        # Add title
        cv2.putText(frame, "CRITICAL CROWD - High Density & Chaos", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, f"Frame: {self.frame_count}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        self.frame_count += 1
        return frame
    
    def create_stampede_scenario(self) -> np.ndarray:
        """Create a stampede scenario with rapid directional movement"""
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Red-tinted background for danger
        for i in range(self.height):
            intensity = int(30 + 60 * i / self.height)
            frame[i, :] = [intensity//4, intensity//4, intensity]
        
        # People moving rapidly in same direction (stampede behavior)
        people_positions = []
        
        # Create crowd moving from left to right
        for row in range(4):
            for col in range(6):
                base_x = 50 + col * 40
                base_y = 100 + row * 60
                
                # Add rapid movement in same direction
                movement_speed = 3
                x = base_x + (self.frame_count * movement_speed) % (self.width + 100)
                y = base_y + int(5 * math.sin(self.frame_count * 0.1 + col))
                
                if x < self.width:  # Only show if still in frame
                    people_positions.append((x, y, 25, 55))
        
        for i, (x, y, w, h) in enumerate(people_positions):
            # Draw realistic person with motion trail
            self._draw_realistic_person(frame, x, y, w, h)
            # Add motion trail
            cv2.rectangle(frame, (x - 5, y), (x, y + h), (100, 100, 100), -1)
        
        # Add title
        cv2.putText(frame, "STAMPEDE - Rapid Directional Movement", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, f"Frame: {self.frame_count}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        self.frame_count += 1
        return frame
    
    def reset_frame_count(self):
        """Reset frame counter for new scenario"""
        self.frame_count = 0

def test_demo_scenarios():
    """Test all demo scenarios"""
    print("🎬 Testing Demo Scenarios...")
    
    generator = DemoScenarioGenerator()
    
    scenarios = [
        ("Normal", generator.create_normal_crowd_scenario),
        ("Warning", generator.create_warning_crowd_scenario),
        ("Critical", generator.create_critical_crowd_scenario),
        ("Stampede", generator.create_stampede_scenario),
    ]
    
    for name, scenario_func in scenarios:
        print(f"Testing {name} scenario...")
        generator.reset_frame_count()
        
        # Generate a few frames
        for i in range(3):
            frame = scenario_func()
            print(f"  Frame {i+1}: {frame.shape} - {name}")
    
    print("✅ All demo scenarios working!")

if __name__ == "__main__":
    test_demo_scenarios()