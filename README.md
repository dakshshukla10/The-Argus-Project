# The Argus Protocol

🎯 **A real-time crowd analytics system that predicts stampede risk using AI-powered computer vision**

[![Status](https://img.shields.io/badge/Status-Feature%20Complete-brightgreen)](https://github.com/dakshshukla10/The-Argus-Protocol)
[![Tasks](https://img.shields.io/badge/Tasks%20Completed-4%2F5-blue)](https://github.com/dakshshukla10/The-Argus-Protocol)
[![Security](https://img.shields.io/badge/Security-Enhanced-green)](https://github.com/dakshshukla10/The-Argus-Protocol)

**Live Demo**: Real-time crowd analytics with WebSocket streaming and interactive dashboard

Quantifies three core safety metrics: **Crowd Density**, **Motion Coherence**, and **Kinetic Energy** to predict stampede risk in real-time.

## ✨ Key Features

🎯 **Real-time Analytics**: Live crowd safety assessment with sub-second latency  
📹 **Video Processing**: YOLOv8 person detection + SORT multi-object tracking  
📊 **Interactive Dashboard**: Streamlit UI with live graphs and status monitoring  
⚡ **WebSocket Streaming**: Real-time data broadcasting to multiple clients  
🚨 **Smart Alerts**: Automatic NORMAL/WARNING/CRITICAL status determination  
🔒 **Production Ready**: Security hardened with pinned dependencies and input validation  
🎨 **Visualization**: Historical charts, real-time metrics, and data export  
🔧 **Configurable**: Environment variables and threshold customization

## 🎯 Primary Objective

Build a real-time crowd analytics system that predicts stampede risk by quantifying three core metrics:

- **Crowd Density**: Number of persons per unit area
- **Motion Coherence**: Standard deviation of motion vector angles (Low deviation is safe; high deviation is dangerous)
- **Kinetic Energy**: Average magnitude of motion vectors

## 🏗️ System Architecture

The system consists of two distinct, decoupled services:

### 🚀 Backend Engine (Python + FastAPI)
- **Responsibility**: All AI/CV processing (the "heavy-lifting" engine)
- **Pipeline**: 
  - 📹 Ingest video stream (webcam or test patterns)
  - 🔍 **Detection**: YOLOv8 (ultralytics) for person detection
  - 🎯 **Tracking**: SORT algorithm for multi-object tracking with unique IDs
  - 📊 **Analytics**: Real-time calculation of three core safety metrics
- **Output**: 
  - 🌐 HTTP video streaming with live visualizations
  - ⚡ WebSocket real-time analytics data broadcasting
  - 📝 Console logging of live metrics

### 🎨 Frontend Dashboard (Python + Streamlit)
- **Responsibility**: Interactive UI and data visualization (client-only)
- **Features**:
  - 🔌 Real-time WebSocket connection to backend analytics
  - 📺 Live video stream display with detection overlays
  - 📈 Interactive Plotly charts with historical data
  - 🚨 Prominent system status indicator (NORMAL/WARNING/CRITICAL)
  - 📊 Current metrics display and threshold monitoring
  - 📋 Data tables and export capabilities

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

**🌐 Available Endpoints:**
- 📊 API Status: http://127.0.0.1:8000/
- 🖼️ Single Frame Test: http://127.0.0.1:8000/test_frame
- 📹 Basic Video Stream: http://127.0.0.1:8000/video_stream
- 🎯 **Full Analytics Stream**: http://127.0.0.1:8000/analytics_stream
- ⚡ **WebSocket Analytics**: ws://127.0.0.1:8000/ws/analytics

### 3. Start the Dashboard
```bash
# In a new terminal
cd src
streamlit run dashboard.py --server.port 8501
```

**🎨 Dashboard URL**: http://127.0.0.1:8501

### 4. Complete System Demo
1. **Backend**: Processes video and streams analytics
2. **Dashboard**: Displays live video + real-time graphs
3. **WebSocket**: Connects dashboard to backend for live data
4. **Status Monitoring**: Watch for NORMAL/WARNING/CRITICAL alerts

## 🛠️ Tech Stack

- **🔧 Backend**: FastAPI, uvicorn, WebSockets
- **🤖 AI/CV**: ultralytics (YOLOv8), OpenCV, custom SORT tracking
- **🎨 Frontend**: Streamlit, Plotly, interactive dashboards
- **📊 Data Processing**: NumPy, SciPy, Pandas
- **⚡ Communication**: Real-time WebSocket streaming, HTTP video streaming
- **🔒 Security**: Pinned dependencies, input validation, environment variables

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

- ✅ **Task 1**: Setup & Detection - Single frame processing with YOLO detections
- ✅ **Task 2**: Video Streaming - Live video stream with YOLO detections viewable in browser
- ✅ **Task 3**: Tracking & Analytics - SORT tracking + 3 core metrics calculation with console output
- ✅ **Task 4**: WebSocket & Dashboard Integration - Real-time data streaming + Streamlit UI
- 🔄 **Task 5**: Refinement & Demo Polish - Threshold tuning + visualization improvements

### 🎉 **Current Status: FEATURE COMPLETE**
The system is fully functional with real-time crowd analytics, WebSocket streaming, and interactive dashboard!

## 🔒 Security & Performance

### 🛡️ **Security Enhancements**
- **Pinned Dependencies**: All package versions locked to prevent supply chain attacks
- **Input Validation**: Comprehensive video frame validation to prevent crashes
- **Error Handling**: Secure error messages that don't leak internal details
- **Environment Variables**: Configurable host/port settings for deployment flexibility

### ⚡ **Performance Optimizations**
- **Efficient Data Structures**: Using `collections.deque` for O(1) operations
- **Real-time Processing**: 15 FPS video processing with sub-second WebSocket latency
- **Concurrent Connections**: Multiple dashboard clients supported simultaneously
- **Memory Management**: Automatic data cleanup and bounded memory usage

### 📊 **System Monitoring**
- **Live Metrics**: Real-time console output of all analytics
- **Status Indicators**: Automatic NORMAL/WARNING/CRITICAL status determination
- **Performance Tracking**: Frame processing rates and connection monitoring

## 🔧 Configuration

All configuration constants are defined in `src/config.py` with environment variable support:

```python
# Model & Video Config
YOLO_MODEL_PATH = "data/models/yolov8n.pt"
VIDEO_RESOLUTION = (640, 480)  # W, H
PROCESSING_FPS = 15

# Server Config (Environment Variable Support)
BACKEND_HOST = os.getenv('ARGUS_HOST', '127.0.0.1')
BACKEND_PORT = int(os.getenv('ARGUS_PORT', '8000'))

# Prediction Thresholds
DENSITY_THRESHOLD_WARNING = 4.0
DENSITY_THRESHOLD_CRITICAL = 6.0
COHERENCE_THRESHOLD_WARNING = 40.0
COHERENCE_THRESHOLD_CRITICAL = 65.0
KE_SPIKE_FACTOR = 2.0
KE_MOVING_AVG_WINDOW = 45
```

### 🌍 **Environment Variables**
```bash
# Optional: Customize host and port
export ARGUS_HOST="0.0.0.0"  # For network access
export ARGUS_PORT="8080"     # Custom port
```

## 🧪 Testing

Run the test scripts to verify functionality:

```bash
# Test Task 1: Single frame detection
python test_task1.py

# Test Task 2: Video streaming
python test_task2.py

# Test Task 3: Tracking & Analytics
python test_task3.py

# Test Task 4: WebSocket & Dashboard Integration
python test_task4.py

# Complete system test (all components)
python test_complete_system.py  # Available in project root
```

### 🎯 **Test Results**
All tests pass with ✅ **6/6 components verified**:
- Backend API ✅
- Video Endpoints ✅  
- WebSocket Streaming ✅
- Analytics Data ✅
- Dashboard Components ✅
- System Integration ✅

## 📚 Documentation & Discussions

### 💬 **Technical Discussions**
- **[Discussion #1](Suggestions.md)**: External LLM suggestions analysis and implementation
  - Security improvements and performance optimizations
  - Critical analysis of 13 suggestions with implementation decisions
  - Documented by Claude (Sonnet 3.5)

### 📖 **Additional Resources**
- **Test Scripts**: Comprehensive testing for each development milestone
- **Configuration Guide**: Environment variables and deployment options
- **Security Audit**: Vulnerability assessment and mitigation strategies

## 🏆 **Recent Improvements**

### ✅ **Security Enhancements (Latest)**
- 🔒 **Dependency Pinning**: Fixed critical supply chain vulnerability
- 🛡️ **Input Validation**: Added comprehensive frame validation
- 🔐 **Error Handling**: Secure error messages without information leakage
- ⚙️ **Environment Variables**: Flexible deployment configuration

### ⚡ **Performance Optimizations (Latest)**
- 🚀 **Deque Implementation**: O(1) data operations for dashboard
- 📊 **Real-time Analytics**: Sub-second WebSocket streaming
- 💾 **Memory Management**: Bounded memory usage with automatic cleanup

## 📝 License

This project is developed for crowd safety analytics and stampede prevention research.

## 🤝 Contributing

This project follows a strict milestone-driven development approach. All major tasks (1-4) are complete, with the system now feature-ready for production use.

---

**⚠️ Safety Notice**: This system is designed for crowd safety analytics. Proper calibration and testing are essential before deployment in real-world scenarios.