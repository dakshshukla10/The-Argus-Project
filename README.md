# The Argus Protocol

🎯 **AI-Powered Real-time Crowd Analytics for CCTV Surveillance**

[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)](https://github.com/dakshshukla10/The-Argus-Protocol)
[![Hackathon](https://img.shields.io/badge/Hackathon-CCTV%20Surveillance%202.0-blue)](https://github.com/dakshshukla10/The-Argus-Protocol)

## 🏛️ **Hackathon Submission**

**Event**: CCTV Surveillance Security & Forensics Hackathon 2.0  
**Organized by**: Bureau of Police Research & Development (BPR&D), Ministry of Home Affairs, Government of India  
**Partners**: CyberPeace and National Crime Records Bureau (NCRB)

**Team Name**: SOSityAI  
**Team Members**: Daksh Shukla, Sayam Jain  
**College**: Manipal Institute Of Technology

### **AI Innovation Focus**
- Develop cutting-edge **AI and Machine Learning solutions** for CCTV surveillance enhancement
- Address public safety challenges through **advanced AI computer vision and deep learning**
- Create **AI-powered intelligent systems** for law enforcement agencies
- Strengthen India's security infrastructure with **next-generation AI technology**

---

## 🎯 **Overview**

AI-powered real-time crowd analytics system for CCTV surveillance networks that predicts stampede risk and crowd safety threats using advanced computer vision, machine learning, and artificial intelligence algorithms.

**Mission**: Enhance public safety through AI-driven intelligent crowd monitoring and machine learning-based early warning systems for law enforcement.

## ✨ **Key Features**

- 🎯 **AI-Powered Threat Detection** with sub-second response using deep learning
- 📹 **Smart CCTV Integration** with AI-enhanced video analysis capabilities  
- 📊 **Intelligent Command Dashboard** powered by real-time AI analytics
- 🚨 **Automated Alerts** with machine learning-based risk assessment
- 📈 **AI-Enhanced Forensic Analysis** for post-incident investigation
- 🌐 **Scalable AI Architecture** for multi-location intelligent deployment

## 📊 **Core Metrics**

### 1. AI-Powered Crowd Density Analysis
- **Purpose**: The AI identifies overcrowding patterns in public spaces using machine learning
- **Method**: Deep learning grid-based person counting with intelligent spatial analysis
- **AI Thresholds**: Smart WARNING at 4.0, CRITICAL at 6.0 persons/zone with ML optimization

### 2. Intelligent Motion Coherence Detection  
- **Purpose**: AI detects chaotic crowd movement patterns indicating panic using neural networks
- **Method**: Machine learning statistical analysis of movement direction variance
- **Smart Thresholds**: AI-calibrated WARNING at 40.0°, CRITICAL at 65.0° deviation

### 3. AI-Enhanced Kinetic Energy Monitoring
- **Purpose**: Deep learning detects sudden crowd acceleration indicating emergency situations
- **Method**: Real-time analysis of speed and momentum with predictive algorithms
- **Intelligent Thresholds**: ML-based WARNING when 2x spike over the calculated baseline

## 🏗️ **System Architecture**

### AI Processing Engine (Python + FastAPI)
- **Video Processing**: YOLOv8 deep learning person detection + SORT AI tracking
- **Machine Learning Analytics**: Real-time AI-powered safety metrics calculation
- **Smart Communication**: WebSocket streaming + HTTP endpoints with data

### AI Command Dashboard (Streamlit)
- **AI-Enhanced Live Monitoring**: Real-time video feeds with intelligent detection overlays
- **Smart Alert System**: AI-driven immediate threat notifications
- **Intelligent Data Visualization**: ML-powered historical charts and AI forensic analysis

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

- **Backend**: FastAPI with machine learning integration, WebSockets
- **Computer Vision**: YOLOv8 deep learning, OpenCV, SORT AI tracking
- **Smart Frontend**: Streamlit with AI-powered visualizations, Plotly
- **ML Analytics**: NumPy, SciPy, Pandas for AI data processing
- **Security**: Intelligent input validation, ML-aware configuration

## 🏛️ **Government Applications**

### Target Deployments
- **Public Events**: Festivals, rallies, gatherings
- **Transportation**: Railway stations, airports, metro
- **Infrastructure**: Government buildings, sensitive areas
- **Urban Surveillance**: City-wide CCTV networks

### AI-Enhanced Law Enforcement Benefits
- **AI-Powered Proactive Detection**: Machine learning predicts threats before incidents
- **Intelligent Situational Awareness**: Real-time AI analytics for command centers
- **AI-Driven Forensic Analysis**: Deep learning for post-incident investigation
- **Smart Resource Deployment**: AI-optimized security personnel allocation

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

- ✅ **Detection Engine**: YOLOv8 deep learning person detection
- ✅ **Smart Video Processing**: Real-time AI-powered streaming pipeline
- ✅ **ML Analytics**: AI multi-object tracking with intelligent safety metrics
- ✅ **Dashboard**: Intelligent command center interface with smart alerts
- ✅ **AI Production Ready**: ML-optimized, security hardened with AI validation

## 📚 **Documentation**

- **[Technical Issues](issues.md)**: Comprehensive bug analysis and fixes
- **[Implementation Discussion](Suggestions.md)**: Security and performance analysis

## 📝 **License & Usage**

Developed for CCTV Surveillance Security & Forensics Hackathon 2.0 under BPR&D, Ministry of Home Affairs, Government of India.

**Intended Use**: AI-powered law enforcement, intelligent public safety systems, and authorized AI security applications.

---

**⚠️ Notice**: System requires proper calibration and testing before real-world deployment.