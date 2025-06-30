# Issues & Bug Report - The Argus Protocol

## 🐛 **COMPREHENSIVE BUG ANALYSIS REPORT**

### **🔴 CRITICAL BUGS**

#### **1. WebSocket Connection Manager Race Condition**
**Location**: `src/main.py` - `ConnectionManager.disconnect()` and `broadcast()`
**Issue**: 
```python
def disconnect(self, websocket: WebSocket):
    self.active_connections.remove(websocket)  # Can raise ValueError if not found

async def broadcast(self, message: str):
    for connection in self.active_connections:
        try:
            await connection.send_text(message)
        except:
            self.active_connections.remove(connection)  # Modifying list while iterating
```
**Problem**: 
- `remove()` will raise `ValueError` if websocket not in list
- Modifying list while iterating causes unpredictable behavior
- Race condition between multiple WebSocket disconnections

#### **2. Resource Leak in WebSocket Handler**
**Location**: `src/main.py` - `websocket_analytics()`
**Issue**: Each WebSocket connection creates its own `cv2.VideoCapture(0)` instance
**Problem**: 
- Multiple clients = multiple camera captures
- Camera resource conflicts
- Memory leaks when connections drop unexpectedly
- Only one process can typically access webcam at a time

#### **3. JSON Serialization Failure**
**Location**: `src/engine/analytics.py` - `analyze_frame()`
**Issue**: 
```python
'trackers': tracker_info  # Contains numpy arrays and complex objects
```
**Problem**: 
- `tracker_info` contains numpy arrays that aren't JSON serializable
- Will cause `TypeError: Object of type ndarray is not JSON serializable`
- Crashes WebSocket when trying to send analytics data

### **🟡 MAJOR BUGS**

#### **4. Missing Import Dependencies**
**Location**: `src/main.py`
**Issue**: Missing imports for new functionality
```python
# Missing imports:
import asyncio  # Used in websocket_analytics
from demo_scenarios import DemoScenarioGenerator  # Used in create_demo_scenario
```

#### **5. Infinite Loop Without Proper Exit**
**Location**: `src/main.py` - WebSocket and streaming endpoints
**Issue**: No proper cleanup mechanism for infinite loops
**Problem**: 
- Streams run forever even after client disconnects
- No graceful shutdown mechanism
- Resource accumulation over time

#### **6. Dashboard WebSocket Thread Management**
**Location**: `src/dashboard.py` - `websocket_listener()`
**Issue**: Thread created but never properly managed
**Problem**:
- Thread created every time but not tracked
- No cleanup when dashboard restarts
- Potential memory leaks from orphaned threads

### **🟠 MODERATE BUGS**

#### **7. Hardcoded Configuration Values**
**Location**: `src/dashboard.py`
**Issue**: 
```python
BACKEND_URL = "http://127.0.0.1:8000"  # Should use config.py values
```
**Problem**: Inconsistent with environment variable approach in config.py

#### **8. Exception Handling Too Broad**
**Location**: Multiple files
**Issue**: Bare `except:` clauses hide important errors
```python
except:  # Too broad - hides bugs
    self.active_connections.remove(connection)
```

#### **9. Frame Rate Control Issues**
**Location**: `src/main.py` - streaming functions
**Issue**: `time.sleep()` in async functions blocks event loop
**Problem**: Should use `await asyncio.sleep()` instead

#### **10. Memory Growth in Analytics**
**Location**: `src/engine/analytics.py`
**Issue**: `kinetic_energy_history` uses `deque` but analytics results include full grid arrays
**Problem**: Memory usage grows over time due to large data structures

### **🟢 MINOR BUGS**

#### **11. Type Annotation Compatibility**
**Location**: `src/main.py`
**Issue**: `list[WebSocket]` syntax requires Python 3.9+
**Problem**: May not work on older Python versions

#### **12. Unused Imports and Variables**
**Location**: Various files
**Issue**: Several unused imports and variables throughout codebase

#### **13. Error Message Inconsistency**
**Location**: Various error handlers
**Issue**: Some errors print to console, others return JSON, inconsistent logging

#### **14. Demo Scenarios Not Detected by YOLO**
**Location**: `src/demo_scenarios.py`
**Issue**: Synthetic human shapes not realistic enough for YOLO detection
**Problem**: Demo scenarios show 0 person count, defeating the purpose

### **🔵 POTENTIAL ISSUES**

#### **15. Concurrent Access to Shared State**
**Location**: `src/engine/analytics.py` and `src/engine/tracking.py`
**Issue**: Multiple endpoints might access same pipeline instance simultaneously
**Problem**: Race conditions in frame counting and state management

#### **16. Large Data Transfer**
**Location**: WebSocket analytics streaming
**Issue**: Sending full analytics data including grids and tracker info
**Problem**: High bandwidth usage, potential WebSocket message size limits

#### **17. No Input Validation for Demo Endpoints**
**Location**: `src/main.py` - `demo_scenario_stream()`
**Issue**: Limited validation of scenario parameter
**Problem**: Could be exploited or cause unexpected behavior

#### **18. Dashboard State Management**
**Location**: `src/dashboard.py`
**Issue**: Streamlit session state not properly initialized in all code paths
**Problem**: Potential KeyError exceptions

### **🟣 DESIGN ISSUES**

#### **19. Single Global Pipeline Instance**
**Location**: `src/main.py`
**Issue**: One global `core_pipeline` instance shared across all endpoints
**Problem**: Not scalable, state conflicts between different streams

#### **20. No Graceful Degradation**
**Location**: Throughout system
**Issue**: System fails completely if camera not available
**Problem**: Should fallback gracefully to test patterns

---

## 📊 **SUMMARY**

**Total Issues Found**: 20
- 🔴 **Critical**: 3 (will cause crashes/data loss)
- 🟡 **Major**: 3 (significant functionality problems)  
- 🟠 **Moderate**: 5 (performance/reliability issues)
- 🟢 **Minor**: 4 (cosmetic/compatibility issues)
- 🔵 **Potential**: 3 (edge cases/scalability)
- 🟣 **Design**: 2 (architectural concerns)

**Most Critical Issues to Fix**:
1. **WebSocket Connection Manager** (race conditions, crashes)
2. **JSON Serialization** (will crash WebSocket streaming)
3. **Resource Leaks** (camera capture conflicts)
4. **Missing Imports** (prevents system startup)

---

## ✅ **FIXED ISSUES**

*This section will be updated as issues are resolved*

### **Fixed - [Date]**

*No issues have been fixed yet. Issues will be documented here as they are resolved with:*
- Issue number and description
- Fix implementation details
- Testing verification
- Date fixed
- Fixed by: [Developer name]

---

**Analysis completed**: [Current Date]
**Analyzed by**: Claude (Sonnet 3.5)
**Next steps**: Prioritize and fix Critical and Major bugs first