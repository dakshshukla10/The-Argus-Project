# The Argus Protocol Execution Contract

**Adhere strictly to the architecture, components, and tasks defined herein.**

## 1. Primary Objective

Build a real-time crowd analytics system that predicts stampede risk by quantifying three core metrics:

- **Crowd Density**: Number of persons per unit area
- **Motion Coherence**: Standard deviation of motion vector angles (Low deviation is safe; high deviation is dangerous)
- **Kinetic Energy**: Average magnitude of motion vectors

## 2. Mandatory Architecture

The system will be composed of two distinct, decoupled services:

### Backend Engine (Language: Python, Framework: FastAPI)

**Responsibility**: All AI/CV processing. This is the "heavy-lifting" engine.

**Pipeline**:
- Ingest video stream (from file or camera)
- **Detection**: Use ultralytics/yolov8 (yolov8n.pt model) to detect persons
- **Tracking**: Use the SORT algorithm to assign and maintain a unique ID for each detected person across frames
- **Analytics**: For each frame, calculate the three core metrics (Density, Coherence, Kinetic Energy)

**Output**:
- Stream the processed video (with visualizations) over an HTTP endpoint
- Broadcast the calculated analytics data (JSON payload) in real-time via a WebSocket endpoint

### Frontend Dashboard (Language: Python, Framework: Streamlit)

**Responsibility**: All User Interface and Visualization.
*This is a client only. It must not perform any CV/AI processing.*

**Functionality**:
- Connect to the FastAPI backend's WebSocket to receive the live analytics data
- Display the video stream received from the FastAPI HTTP endpoint
- Visualize the analytics data using plotly graphs
- Display a prominent system status indicator (NORMAL, WARNING, CRITICAL) based on the received data

## 3. Environment and Dependencies

**File: requirements.txt**

```txt
# Core AI/CV & Math
ultralytics
opencv-python
numpy
scipy # For spatial calculations and stats
sort-tracker

# Backend Framework
fastapi
uvicorn[standard]
python-websockets

# Frontend Framework
streamlit
plotly
pandas
```

## 4. Project File Structure (Strict)

**Implement this exact file structure:**

```
```
argus_protocol/
├── data/
│   ├── models/
│   │   └── yolov8n.pt
│   └── videos/
│       ├── normal_flow.mp4
│       └── danger_crush.mp4
│
├── src/
│   ├── main.py             # FastAPI App: Endpoints, WebSocket, orchestrates engine
│   ├── dashboard.py        # Streamlit App: UI code only
│   │
│   ├── engine/
│   │   ├── core_pipeline.py  # Main processing loop called by FastAPI
│   │   ├── detection.py    # Class/function for YOLOv8 inference
│   │   ├── tracking.py     # Class/function for SORT tracking
│   │   └── analytics.py    # Functions for calculating the 3 core metrics
│   │
│   └── config.py           # All constants: thresholds, paths, etc.
│
├── requirements.txt
└── README.md
```

## 5. Core Logic & Constants (src/config.py)

**Define and use these constants for the prediction engine. Do not hardcode values elsewhere.**

```python
# --- Model & Video Config ---
YOLO_MODEL_PATH = "data/models/yolov8n.pt"
VIDEO_RESOLUTION = (640, 480) # W, H
PROCESSING_FPS = 15

# --- Analytics Config ---
# For Density Calculation
# Assuming a fixed camera angle where 1 grid cell ~ 1 sq. meter
DENSITY_GRID_SIZE = (10, 10) # 10x10 grid over the frame

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
KE_SPIKE_FACTOR = 2.0 # A 2x spike over moving average is a warning
KE_MOVING_AVG_WINDOW = 45 # frames (3 seconds @ 15fps)
```

## 6. Task Execution Order

**Execute development in this strict sequence. Do not proceed until the milestone is met.**

### Task 1: Setup & Detection
- Create the environment and file structure
- Implement `src/engine/detection.py`
- In `src/main.py`, create a FastAPI endpoint that returns a single processed frame with YOLO boxes

**Milestone**: A single image is returned via an HTTP request.

### Task 2: Video Streaming
- Modify the FastAPI endpoint to stream a sequence of processed frames (video)

**Milestone**: A live video stream with YOLO detections is viewable in a browser.

### Task 3: Tracking & Analytics
- Implement `src/engine/tracking.py` (SORT)
- Implement `src/engine/analytics.py` (the 3 metric calculations)
- Integrate tracking and analytics into the core_pipeline

**Milestone**: The backend console prints live JSON data for the 3 metrics for every frame.

### Task 4: WebSocket & Dashboard Integration
- Implement the WebSocket endpoint in `src/main.py` to broadcast the analytics JSON
- Implement the Streamlit dashboard (`src/dashboard.py`)
- The dashboard must connect to both the video stream and the WebSocket

**Milestone**: The dashboard displays the video and live-updating graphs/status based on data from the backend. The system is now feature-complete.

### Task 5: Refinement & Demo Polish
- Tune thresholds in config.py
- Improve visualizations
- Prepare the demo story

---