"""
Configuration constants for The Argus Protocol.
All constants and thresholds are defined here to avoid hardcoding values elsewhere.
"""

# --- Model & Video Config ---
YOLO_MODEL_PATH = "data/models/yolov8n.pt"
VIDEO_RESOLUTION = (640, 480)  # W, H
PROCESSING_FPS = 15

# --- Analytics Config ---
# For Density Calculation
# Assuming a fixed camera angle where 1 grid cell ~ 1 sq. meter
DENSITY_GRID_SIZE = (10, 10)  # 10x10 grid over the frame

# --- Prediction Thresholds ---
# Density (persons/grid_cell)
DENSITY_THRESHOLD_WARNING = 4.0
DENSITY_THRESHOLD_CRITICAL = 6.0

# Motion Coherence (Standard deviation of angles in degrees)
# Higher value means more chaotic movement
COHERENCE_THRESHOLD_WARNING = 40.0
COHERENCE_THRESHOLD_CRITICAL = 65.0

# Kinetic Energy (Average pixel velocity per frame)
# This requires a baseline; we check for spikes
KE_SPIKE_FACTOR = 2.0  # A 2x spike over moving average is a warning
KE_MOVING_AVG_WINDOW = 45  # frames (3 seconds @ 15fps)

# --- Server Config ---
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8000
WEBSOCKET_ENDPOINT = "/ws"
VIDEO_STREAM_ENDPOINT = "/video_stream"

# --- Status Levels ---
STATUS_NORMAL = "NORMAL"
STATUS_WARNING = "WARNING" 
STATUS_CRITICAL = "CRITICAL"