# The Argus Protocol

🎯 **Real-time Crowd Analytics for CCTV Surveillance**

[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)](https://github.com/dakshshukla10/The-Argus-Protocol)
[![Hackathon](https://img.shields.io/badge/Hackathon-CCTV%20Surveillance%202.0-blue)](https://github.com/dakshshukla10/The-Argus-Protocol)

## 🏛️ **Hackathon Submission**

**Event**: CCTV Surveillance Security & Forensics Hackathon 2.0  
**Organized by**: Bureau of Police Research & Development (BPR&D), Ministry of Home Affairs, Government of India  
**Partners**: CyberPeace and National Crime Records Bureau (NCRB)

---

## 🎯 **Overview**

Real-time crowd analytics system for CCTV surveillance networks that predicts stampede risk and crowd safety threats using computer vision and machine learning.

**Mission**: Enhance public safety through intelligent crowd monitoring and early warning systems for law enforcement.

## ✨ **Key Features**

- 🎯 **Real-time Threat Detection** with sub-second response
- 📹 **CCTV Integration** compatible with existing surveillance infrastructure  
- 📊 **Command Center Dashboard** for security operations
- 🚨 **Automated Alerts** with NORMAL/WARNING/CRITICAL status
- 📈 **Forensic Analysis** for post-incident investigation
- 🌐 **Scalable Architecture** for multi-location deployment

## 📊 **Core Metrics**

### 1. Crowd Density
- **Purpose**: Identifies overcrowding in public spaces
- **Method**: Grid-based person counting analysis
- **Thresholds**: WARNING at 4.0, CRITICAL at 6.0 persons/zone

### 2. Motion Coherence  
- **Purpose**: Detects chaotic crowd movement patterns
- **Method**: Statistical analysis of movement direction variance
- **Thresholds**: WARNING at 40.0°, CRITICAL at 65.0° deviation

### 3. Kinetic Energy
- **Purpose**: Detects sudden crowd acceleration
- **Method**: Real-time speed and momentum analysis
- **Thresholds**: WARNING when 2x spike over baseline

## 🏗️ **System Architecture**

### Backend Engine (Python + FastAPI)
- **Video Processing**: YOLOv8 person detection + SORT tracking
- **Analytics**: Real-time calculation of safety metrics
- **Communication**: WebSocket streaming + HTTP endpoints

### Command Dashboard (Streamlit)
- **Live Monitoring**: Real-time video feeds with detection overlays
- **Alert System**: Immediate threat notifications
- **Data Visualization**: Historical charts and forensic analysis

## 🚀 **Quick Start**

### Installation
```bash
git clone https://github.com/dakshshukla10/The-Argus-Protocol.git
cd The-Argus-Protocol
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running the System
```bash
# Terminal 1: Start Backend
cd src && python main.py

# Terminal 2: Start Dashboard
cd src && streamlit run dashboard.py --server.port 8501

# Open: http://127.0.0.1:8501
```

## 🛠️ **Technology Stack**

- **Backend**: FastAPI, WebSockets
- **Computer Vision**: YOLOv8, OpenCV, SORT tracking
- **Frontend**: Streamlit, Plotly
- **Analytics**: NumPy, SciPy, Pandas
- **Security**: Input validation, environment configuration

## 🏛️ **Government Applications**

### Target Deployments
- **Public Events**: Festivals, rallies, gatherings
- **Transportation**: Railway stations, airports, metro
- **Infrastructure**: Government buildings, sensitive areas
- **Urban Surveillance**: City-wide CCTV networks

### Law Enforcement Benefits
- Proactive threat detection before incidents
- Real-time situational awareness for command centers
- Forensic analysis for post-incident investigation
- Efficient security resource deployment

## 🧪 **Testing**

```bash
# Run system tests
python test_task1.py  # Detection engine
python test_task2.py  # Video streaming
python test_task3.py  # Analytics pipeline
python test_task4.py  # Dashboard integration
python test_task5.py  # Complete system
```

## 📊 **Project Status**

- ✅ **Detection Engine**: YOLOv8 person detection
- ✅ **Video Processing**: Real-time streaming pipeline
- ✅ **Analytics**: Multi-object tracking with safety metrics
- ✅ **Dashboard**: Command center interface with alerts
- ✅ **Production Ready**: Security hardened and optimized

## 📚 **Documentation**

- **[Technical Issues](issues.md)**: Comprehensive bug analysis and fixes
- **[Implementation Discussion](Suggestions.md)**: Security and performance analysis

## 📝 **License & Usage**

Developed for CCTV Surveillance Security & Forensics Hackathon 2.0 under BPR&D, Ministry of Home Affairs, Government of India.

**Intended Use**: Law enforcement, public safety, and authorized security applications.

---

**⚠️ Notice**: System requires proper calibration and testing before real-world deployment.