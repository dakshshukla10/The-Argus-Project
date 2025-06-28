# The Argus Protocol

A real-time crowd analytics system that predicts stampede risk by quantifying three core metrics: **Crowd Density**, **Motion Coherence**, and **Kinetic Energy**.

## 🎯 Primary Objective

Build a real-time crowd analytics system that predicts stampede risk by quantifying three core metrics:

- **Crowd Density**: Number of persons per unit area
- **Motion Coherence**: Standard deviation of motion vector angles (Low deviation is safe; high deviation is dangerous)
- **Kinetic Energy**: Average magnitude of motion vectors

## 🏗️ System Architecture

The system consists of two distinct, decoupled services:

### Backend Engine (Python + FastAPI)
- **Responsibility**: All AI/CV processing (the "heavy-lifting" engine)
- **Pipeline**: 
  - Ingest video stream (from file or camera)
  - **Detection**: Use ultralytics/yolov8 (yolov8n.pt model) to detect persons
  - **Tracking**: Use SORT algorithm to assign and maintain unique IDs for each detected person across frames
  - **Analytics**: Calculate the three core metrics for each frame
- **Output**: 
  - Stream processed video (with visualizations) over HTTP endpoint
  - Broadcast analytics data (JSON payload) in real-time via WebSocket endpoint

### Frontend Dashboard (Python + Streamlit)
- **Responsibility**: All User Interface and Visualization (client only - no CV/AI processing)
- **Functionality**:
  - Connect to FastAPI backend's WebSocket to receive live analytics data
  - Display video stream from FastAPI HTTP endpoint
  - Visualize analytics data using plotly graphs
  - Display system status indicator (NORMAL, WARNING, CRITICAL) based on received data

## 📁 Project Structure

```
argus_protocol/
├── data/
│   ├── models/
│   │   └── yolov8n.pt              # YOLOv8 model file
│   └── videos/
│       ├── normal_flow.mp4         # Test video - normal crowd flow
│       └── danger_crush.mp4        # Test video - dangerous crowd scenario
│
├── src/
│   ├── main.py                     # FastAPI App: Endpoints, WebSocket, orchestrates engine
│   ├── dashboard.py                # Streamlit App: UI code only
│   │
│   ├── engine/
│   │   ├── core_pipeline.py        # Main processing loop called by FastAPI
│   │   ├── detection.py            # Class/function for YOLOv8 inference
│   │   ├── tracking.py             # Class/function for SORT tracking
│   │   └── analytics.py            # Functions for calculating the 3 core metrics
│   │
│   └── config.py                   # All constants: thresholds, paths, etc.
│
├── requirements.txt                # Python dependencies
└── README.md                       # Project documentation
```

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/dakshshukla10/The-Argus-Protocol.git
cd The-Argus-Protocol

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Running the Backend
```bash
cd src
python main.py
```

The backend will be available at:
- API Status: http://127.0.0.1:8000/
- Single Frame Test: http://127.0.0.1:8000/test_frame
- Live Video Stream: http://127.0.0.1:8000/video_stream

### 3. Running the Dashboard (Coming Soon)
```bash
cd src
streamlit run dashboard.py --server.port 8501
```

## 🛠️ Tech Stack

- **Backend**: FastAPI, uvicorn
- **AI/CV**: ultralytics (YOLOv8), OpenCV, SORT tracking
- **Frontend**: Streamlit, Plotly
- **Data Processing**: NumPy, SciPy, Pandas
- **Communication**: WebSockets, HTTP streaming

## 📊 Core Metrics

### 1. Crowd Density
- **Definition**: Number of persons per unit area
- **Calculation**: Count persons in each grid cell of 10x10 grid
- **Thresholds**: WARNING at 4.0, CRITICAL at 6.0 persons/grid_cell

### 2. Motion Coherence  
- **Definition**: Standard deviation of motion vector angles
- **Interpretation**: Low deviation = safe, high deviation = dangerous
- **Thresholds**: WARNING at 40.0°, CRITICAL at 65.0° standard deviation

### 3. Kinetic Energy
- **Definition**: Average magnitude of motion vectors
- **Calculation**: Monitor for spikes over moving average
- **Thresholds**: WARNING when 2x spike over 45-frame moving average

## 🎯 Development Milestones

- [x] **Task 1**: Setup & Detection - Single frame processing with YOLO detections
- [x] **Task 2**: Video Streaming - Live video stream with YOLO detections viewable in browser
- [ ] **Task 3**: Tracking & Analytics - SORT tracking + 3 core metrics calculation
- [ ] **Task 4**: WebSocket & Dashboard Integration - Real-time data streaming + Streamlit UI
- [ ] **Task 5**: Refinement & Demo Polish - Threshold tuning + visualization improvements

## 🔧 Configuration

All configuration constants are defined in `src/config.py`:

```python
# Model & Video Config
YOLO_MODEL_PATH = "data/models/yolov8n.pt"
VIDEO_RESOLUTION = (640, 480)  # W, H
PROCESSING_FPS = 15

# Prediction Thresholds
DENSITY_THRESHOLD_WARNING = 4.0
DENSITY_THRESHOLD_CRITICAL = 6.0
COHERENCE_THRESHOLD_WARNING = 40.0
COHERENCE_THRESHOLD_CRITICAL = 65.0
KE_SPIKE_FACTOR = 2.0
KE_MOVING_AVG_WINDOW = 45
```

## 🧪 Testing

Run the test scripts to verify functionality:

```bash
# Test Task 1: Single frame detection
python test_task1.py

# Test Task 2: Video streaming
python test_task2.py
```

## 📝 License

This project is developed for crowd safety analytics and stampede prevention research.

## 🤝 Contributing

This project follows a strict development sequence. Please ensure each milestone is met before proceeding to the next task.

---

**⚠️ Safety Notice**: This system is designed for crowd safety analytics. Proper calibration and testing are essential before deployment in real-world scenarios.