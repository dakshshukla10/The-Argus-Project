"""
Analytics module for calculating the three core metrics:
1. Crowd Density: Number of persons per unit area
2. Motion Coherence: Standard deviation of motion vector angles
3. Kinetic Energy: Average magnitude of motion vectors
"""

import numpy as np
import math
from typing import List, Dict, Tuple, Optional
from collections import deque
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    DENSITY_GRID_SIZE, VIDEO_RESOLUTION,
    DENSITY_THRESHOLD_WARNING, DENSITY_THRESHOLD_CRITICAL,
    COHERENCE_THRESHOLD_WARNING, COHERENCE_THRESHOLD_CRITICAL,
    KE_SPIKE_FACTOR, KE_MOVING_AVG_WINDOW,
    STATUS_NORMAL, STATUS_WARNING, STATUS_CRITICAL
)


class CrowdAnalytics:
    """
    Main analytics class for calculating crowd safety metrics
    """
    
    def __init__(self):
        """Initialize the analytics engine"""
        self.kinetic_energy_history = deque(maxlen=KE_MOVING_AVG_WINDOW)
        self.frame_count = 0
        
    def calculate_crowd_density(self, tracker_info: List[Dict]) -> Tuple[float, np.ndarray]:
        """
        Calculate crowd density as number of persons per grid cell
        
        Args:
            tracker_info: List of tracker dictionaries with bbox information
            
        Returns:
            Tuple of (max_density, density_grid)
        """
        # Create density grid
        grid_height, grid_width = DENSITY_GRID_SIZE
        density_grid = np.zeros((grid_height, grid_width))
        
        # Calculate grid cell dimensions
        cell_width = VIDEO_RESOLUTION[0] / grid_width
        cell_height = VIDEO_RESOLUTION[1] / grid_height
        
        # Count persons in each grid cell
        for tracker in tracker_info:
            bbox = tracker['bbox']
            # Use center of bounding box
            center_x = (bbox[0] + bbox[2]) / 2
            center_y = (bbox[1] + bbox[3]) / 2
            
            # Convert to grid coordinates
            grid_x = int(center_x / cell_width)
            grid_y = int(center_y / cell_height)
            
            # Ensure within bounds
            grid_x = max(0, min(grid_width - 1, grid_x))
            grid_y = max(0, min(grid_height - 1, grid_y))
            
            density_grid[grid_y, grid_x] += 1
        
        # Return maximum density and the grid
        max_density = np.max(density_grid)
        return float(max_density), density_grid
    
    def calculate_motion_coherence(self, tracker_info: List[Dict]) -> float:
        """
        Calculate motion coherence as standard deviation of motion vector angles
        
        Args:
            tracker_info: List of tracker dictionaries with velocity information
            
        Returns:
            Standard deviation of motion angles in degrees
        """
        if len(tracker_info) < 2:
            return 0.0
        
        angles = []
        for tracker in tracker_info:
            velocity = tracker['velocity']
            vx, vy = velocity[0], velocity[1]
            
            # Calculate angle only if there's significant movement
            speed = math.sqrt(vx*vx + vy*vy)
            if speed > 0.1:  # Minimum speed threshold
                angle = math.atan2(vy, vx)
                angles.append(angle)
        
        if len(angles) < 2:
            return 0.0
        
        # Convert to degrees and calculate standard deviation
        angles_deg = [math.degrees(angle) for angle in angles]
        
        # Handle angle wraparound (circular statistics)
        # Convert to unit vectors and calculate circular standard deviation
        x_components = [math.cos(angle) for angle in angles]
        y_components = [math.sin(angle) for angle in angles]
        
        mean_x = np.mean(x_components)
        mean_y = np.mean(y_components)
        
        # Calculate circular variance
        R = math.sqrt(mean_x*mean_x + mean_y*mean_y)
        circular_variance = 1 - R
        
        # Convert to standard deviation in degrees
        if circular_variance <= 0:
            return 0.0
        
        # Approximate conversion to degrees
        coherence_std = math.degrees(math.sqrt(2 * circular_variance))
        
        return float(coherence_std)
    
    def calculate_kinetic_energy(self, tracker_info: List[Dict]) -> Tuple[float, float, bool]:
        """
        Calculate kinetic energy as average magnitude of motion vectors
        
        Args:
            tracker_info: List of tracker dictionaries with velocity information
            
        Returns:
            Tuple of (current_ke, moving_average_ke, is_spike)
        """
        if len(tracker_info) == 0:
            current_ke = 0.0
        else:
            # Calculate average kinetic energy (proportional to velocity squared)
            total_ke = 0.0
            for tracker in tracker_info:
                velocity = tracker['velocity']
                vx, vy = velocity[0], velocity[1]
                ke = (vx*vx + vy*vy) / 2.0  # Simplified kinetic energy
                total_ke += ke
            
            current_ke = total_ke / len(tracker_info)
        
        # Add to history
        self.kinetic_energy_history.append(current_ke)
        
        # Calculate moving average
        if len(self.kinetic_energy_history) > 0:
            moving_avg = np.mean(self.kinetic_energy_history)
        else:
            moving_avg = current_ke
        
        # Check for spike
        is_spike = False
        if moving_avg > 0 and len(self.kinetic_energy_history) >= 10:
            spike_threshold = moving_avg * KE_SPIKE_FACTOR
            is_spike = current_ke > spike_threshold
        
        return float(current_ke), float(moving_avg), is_spike
    
    def determine_status(self, density: float, coherence: float, ke_spike: bool) -> str:
        """
        Determine overall system status based on the three metrics
        
        Args:
            density: Maximum crowd density
            coherence: Motion coherence standard deviation
            ke_spike: Whether there's a kinetic energy spike
            
        Returns:
            Status string: NORMAL, WARNING, or CRITICAL
        """
        # Check for critical conditions
        if (density >= DENSITY_THRESHOLD_CRITICAL or 
            coherence >= COHERENCE_THRESHOLD_CRITICAL or
            ke_spike):
            return STATUS_CRITICAL
        
        # Check for warning conditions
        if (density >= DENSITY_THRESHOLD_WARNING or 
            coherence >= COHERENCE_THRESHOLD_WARNING):
            return STATUS_WARNING
        
        return STATUS_NORMAL
    
    def analyze_frame(self, tracker_info: List[Dict]) -> Dict:
        """
        Perform complete analysis of a frame
        
        Args:
            tracker_info: List of tracker dictionaries
            
        Returns:
            Dictionary containing all analytics results
        """
        self.frame_count += 1
        
        # Calculate all metrics
        density, density_grid = self.calculate_crowd_density(tracker_info)
        coherence = self.calculate_motion_coherence(tracker_info)
        ke_current, ke_avg, ke_spike = self.calculate_kinetic_energy(tracker_info)
        
        # Determine status
        status = self.determine_status(density, coherence, ke_spike)
        
        # Prepare results
        results = {
            'frame_count': self.frame_count,
            'timestamp': self.frame_count / 15.0,  # Assuming 15 FPS
            'person_count': len(tracker_info),
            'density': {
                'max_density': density,
                'grid': density_grid.tolist(),
                'threshold_warning': DENSITY_THRESHOLD_WARNING,
                'threshold_critical': DENSITY_THRESHOLD_CRITICAL
            },
            'motion_coherence': {
                'std_deviation': coherence,
                'threshold_warning': COHERENCE_THRESHOLD_WARNING,
                'threshold_critical': COHERENCE_THRESHOLD_CRITICAL
            },
            'kinetic_energy': {
                'current': ke_current,
                'moving_average': ke_avg,
                'spike_detected': ke_spike,
                'spike_factor': KE_SPIKE_FACTOR
            },
            'status': status,
            'trackers': tracker_info
        }
        
        return results
    
    def get_summary_stats(self) -> Dict:
        """
        Get summary statistics for the analytics session
        
        Returns:
            Dictionary with summary statistics
        """
        return {
            'total_frames': self.frame_count,
            'ke_history_length': len(self.kinetic_energy_history),
            'ke_history': list(self.kinetic_energy_history) if self.kinetic_energy_history else []
        }


def test_analytics():
    """Test function for the analytics module."""
    analytics = CrowdAnalytics()
    
    # Create test tracker data
    test_trackers = [
        {
            'id': 1,
            'bbox': [100, 100, 150, 200],
            'velocity': [2.0, 1.0],
            'age': 5,
            'hits': 5
        },
        {
            'id': 2,
            'bbox': [300, 150, 350, 250],
            'velocity': [1.5, -0.5],
            'age': 3,
            'hits': 3
        },
        {
            'id': 3,
            'bbox': [200, 200, 250, 300],
            'velocity': [-1.0, 2.0],
            'age': 7,
            'hits': 7
        }
    ]
    
    # Test analytics
    results = analytics.analyze_frame(test_trackers)
    
    print("Analytics Test Results:")
    print(f"Person Count: {results['person_count']}")
    print(f"Max Density: {results['density']['max_density']}")
    print(f"Motion Coherence: {results['motion_coherence']['std_deviation']:.2f}°")
    print(f"Kinetic Energy: {results['kinetic_energy']['current']:.2f}")
    print(f"Status: {results['status']}")
    
    print("Analytics test completed successfully")


if __name__ == "__main__":
    test_analytics()