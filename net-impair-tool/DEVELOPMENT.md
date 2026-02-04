# Development Notes & Code Walkthrough

## 🎯 Architecture Overview

```
USER LAYER
├── Web Browser / UI
│   ├── HTML (index.html) - Structure
│   ├── CSS (style.css) - Styling
│   └── JavaScript (script.js) - Interactivity
│
APPLICATION LAYER
├── Flask Backend (main.py)
│   ├── HTTP Server (port 5000)
│   ├── API Endpoints
│   └── Route Handlers
│
├── GUI Framework (pywebview)
│   ├── Window Management
│   └── Browser Integration
│
└── System Tray (pystray)
    ├── Icon Management
    └── Context Menu
│
NETWORK LAYER
└── Network Engine (network.py)
    ├── Packet Capture (WinDivert)
    ├── Effect Processing
    ├── Queue Management
    └── Statistics Tracking
│
KERNEL LAYER
└── WinDivert Driver
    ├── Packet Interception
    └── Re-injection
```

## 📋 Code Walkthrough

### 1. main.py (Entry Point - 350 lines)

**Purpose**: Application initialization, Flask server, pywebview, system tray

**Key Classes & Functions**:

```python
# Flask Application
app = Flask(__name__)

# API Endpoints
@app.route('/api/config', methods=['GET', 'POST'])  # Get/set config
@app.route('/api/start', methods=['POST'])          # Start simulation
@app.route('/api/stop', methods=['POST'])           # Stop simulation
@app.route('/api/stats', methods=['GET'])           # Get statistics
@app.route('/api/reset-stats', methods=['POST'])    # Reset stats

# Admin Check
def is_admin()                                       # Check elevated privileges

# System Tray
class TrayIconManager:
    - create_image()                                 # Generate icon
    - create_menu()                                  # Context menu
    - show_window()                                  # Show main window
    - exit_app()                                     # Exit handler
    - perform_self_destruct()                        # Delete app files

# Main App
class NetworkImpairmentApp:
    - start_flask()                                  # Start Flask thread
    - setup_webview()                                # Create browser window
    - setup_tray()                                   # Setup system tray
    - run()                                          # Main entry point
```

**Flow**:
1. Check if running as Administrator
2. Start Flask server in background thread
3. Create pywebview window (loads http://127.0.0.1:5000)
4. Setup system tray icon
5. Block on webview.start() until user closes window

**Key Design Decision**: Flask runs in daemon thread, doesn't block UI

---

### 2. network.py (Packet Engine - 400 lines)

**Purpose**: WinDivert packet interception and effect application

**Key Classes**:

```python
# Configuration Data Class
@dataclass
class NetworkConfig:
    - filter_str: WinDivert filter expression
    - lag_enabled, lag_ms: Latency settings
    - drop_enabled, drop_chance: Loss settings
    - throttle_enabled, throttle_ms, throttle_chance: Bandwidth settings
    - duplicate_enabled, duplicate_count, duplicate_chance: Duplication
    - out_of_order_enabled, out_of_order_chance: Reordering
    - tamper_enabled, tamper_chance: Corruption

# Packet Storage
class PacketQueue:
    - queue: deque of {packet, timestamp, delay, ready_time}
    - lock: threading.Lock for thread-safety
    - stats: counters {processed, dropped, delayed, duplicated, tampered, ooo}
    
    Methods:
    - add(packet, delay_ms, timestamp)      # Add packet to queue
    - get_ready_packets()                   # Get packets due to send
    - get_stats()                           # Get counters
    - reset_stats()                         # Reset counters

# Main Engine
class NetworkImpairmentEngine:
    - config: NetworkConfig instance
    - packet_queue: PacketQueue instance
    - divert_handle: WinDivert handle
    - capture_thread: Packet capture thread
    - process_thread: Packet reinjection thread
    
    Public Methods:
    - start()                               # Begin interception
    - stop()                                # Stop interception
    - update_config(dict)                   # Update configuration
    - get_stats()                           # Get statistics
    - get_config()                          # Get current config
    
    Private Methods:
    - _capture_loop()                       # Capture thread main loop
    - _process_loop()                       # Process thread main loop
    - _apply_effects(packet)                # Apply effects to packet
    - _tamper_packet(packet)                # Corrupt packet data
```

**Effect Application Order** (in _apply_effects):
```
1. DROP CHECK → If dropped, return (stop processing)
2. DUPLICATE CHECK → Count duplicates to create
3. TAMPER CHECK → Corrupt payload
4. OUT-OF-ORDER CHECK → Random delay within range
5. THROTTLE CHECK → Add bandwidth delay
6. LAG CHECK → Add base latency
7. ADD TO QUEUE → Store with calculated delay
8. CREATE DUPLICATES → Add copies to queue with same delay
```

**Threading Model**:
```
Main Thread (Flask)
├─ Spawns Capture Thread
├─ Spawns Process Thread
└─ Waits for shutdown

Capture Thread
├─ Opens WinDivert with filter
├─ Loops: recv packet → apply effects → queue
└─ Runs until is_running = False

Process Thread
├─ Loops: get_ready_packets() → send via divert
└─ Checks every 1ms for ready packets
```

**Key Technical Points**:
- `divert_handle.recv(timeout=100)`: Blocks max 100ms
- `time.time()` for precise timing
- `deque(maxlen=X)` prevents memory bloat
- Lock protection for shared stats
- Non-blocking packet queue (timestamp-based)

---

### 3. templates/index.html (UI Structure - 280 lines)

**Layout**:
```
Header (gradient blue)
│
├─ Left Panel (Control)
│  ├─ Filter input
│  ├─ 6 Effect Cards (Lag, Drop, Throttle, Duplicate, OOO, Tamper)
│  │  Each card has:
│  │  ├─ Checkbox to enable/disable
│  │  └─ Sliders for parameters
│  └─ Control buttons (Start, Stop, Delete)
│
└─ Right Panel (Status)
   ├─ Status display (Engine state, Admin check)
   ├─ Statistics grid (7 counters)
   ├─ Config visualization
   └─ Information card
```

**Key Semantic Elements**:
```html
<div class="container">           <!-- Main wrapper -->
  <header class="header">          <!-- Title & info -->
  <div class="main-content">       <!-- Grid 2-column layout -->
    <div class="panel">            <!-- Left control panel -->
      <div class="effect-card">    <!-- Effect container -->
        <input type="checkbox">     <!-- Toggle -->
        <input type="range">        <!-- Slider -->
      </div>
      <button class="btn">         <!-- Action buttons -->
    </div>
    <div class="panel">            <!-- Right status panel -->
      <div class="status-card">    <!-- Status info -->
      <div class="stats-grid">     <!-- Statistics grid -->
    </div>
  </div>
</div>
```

**Form Elements**:
- `<input type="text">` - WinDivert filter
- `<input type="checkbox">` - Enable/disable effects
- `<input type="range">` - Sliders for values
- `<output>` - Display slider values
- `<button>` - Start/Stop/Delete/Reset buttons

---

### 4. static/style.css (Styling - 600+ lines)

**Design System**:
```css
/* Color Palette */
--bg-primary: #1e1e1e       /* Main background */
--bg-secondary: #2d2d2d     /* Card background */
--bg-tertiary: #3d3d3d      /* Input background */
--text-primary: #e0e0e0     /* Main text */
--text-secondary: #b0b0b0   /* Muted text */
--accent-blue: #0d7377      /* Primary accent */
--accent-light: #14a085     /* Hover/active */
--accent-red: #dc3545       /* Danger button */
--accent-green: #28a745     /* Success status */
--accent-warning: #ffc107   /* Warning color */

/* Layout System */
CSS Grid: main-content (2 columns)
Flexbox: containers, buttons, cards
Responsive: 1200px breakpoint (mobile stacking)
```

**Component Styling**:
```css
/* Sliders */
.slider                         /* Range input */
::-webkit-slider-thumb          /* Thumb styling (Chrome)*/
::-moz-range-thumb              /* Thumb styling (Firefox) */

/* Buttons */
.btn                            /* Base button */
.btn-primary                    /* Primary (blue gradient) */
.btn-secondary                  /* Secondary (dark) */
.btn-danger                     /* Danger (red) */

/* Cards */
.effect-card                    /* Effect container */
.status-card                    /* Status info container */
.stats-grid                     /* Statistics layout */

/* Animations */
@keyframes slideIn              /* Toast entrance */
@keyframes slideOut             /* Toast exit */
@keyframes fade                 /* Fade effects */

/* Scrollbar */
::-webkit-scrollbar             /* Custom scrollbar */
```

**Responsive Design**:
```css
Default: 2-column layout (1200px+)
Tablet: 1 column (max-width: 1200px)
Mobile: Stacked layout, adjusted fonts
```

**Accessibility**:
- Sufficient color contrast (WCAG AA)
- Readable font sizes (14px+ for body)
- Focus states for interactive elements
- Semantic HTML structure

---

### 5. static/script.js (Frontend Logic - 500+ lines)

**Global State Management**:
```javascript
const AppState = {
    isRunning: boolean,              /* Simulation active? */
    updateInterval: number,          /* Stats polling interval ID */
    config: {},                      /* Current configuration */
    previousStats: {}                /* Last stats snapshot */
};

const UI = { /* Element references */
    filterInput,                     /* Filter input field */
    lagCheck, lagSlider, lagValue,  /* Lag controls */
    dropCheck, dropSlider,           /* Drop controls */
    /* ... etc for all controls ... */
    startBtn, stopBtn, deleteBtn,   /* Action buttons */
};

const API_BASE = 'http://127.0.0.1:5000/api';
```

**Core Functions**:

```javascript
/* API Communication */
async apiCall(endpoint, method, data)
    → Fetch wrapper for Flask API
    → Returns JSON response or null on error
    → Shows toast on errors

/* Configuration */
gatherConfigFromUI()
    → Collect all settings from form elements
    → Return config object for backend

loadConfigFromServer()
    → GET /api/config
    → Update UI with server config
    → Sync display with backend state

updateConfigDisplay()
    → Format config for display panel
    → Show active settings
    → Update in real-time

/* Controls */
startSimulation()
    → Gather config from UI
    → POST /api/start
    → Start stats polling
    → Update UI state

stopSimulation()
    → POST /api/stop
    → Stop stats polling
    → Clear counters display

resetStats()
    → POST /api/reset-stats
    → Update display to zero

exitAndDelete()
    → Stop simulation
    → Close window
    → Server handles deletion

/* Statistics */
startStatsPoll()
    → setInterval(/api/stats, 500ms)
    → Updates display every 500ms

stopStatsPoll()
    → Clear polling interval
    → Stop background requests

updateStatsDisplay()
    → GET /api/stats
    → Parse response
    → Update counter displays

/* UI */
updateUIState()
    → Enable/disable buttons based on state
    → Update status displays
    → Update config visualization

setupSliders()
    → Add input listeners to all sliders
    → Update <output> elements on change
    → Real-time value display

showToast(message, type)
    → Create notification element
    → Append to container
    → Auto-remove after 4s
```

**Event Flow**:
```
User Action (click, input)
    ↓
Event Listener (addEventListener)
    ↓
Handler Function (e.g., startSimulation)
    ↓
API Call (apiCall)
    ↓
Flask Backend (main.py route)
    ↓
Network Engine (network.py)
    ↓
Response back to Frontend
    ↓
Update UI (DOM manipulation)
    ↓
Show Toast Notification
```

**Statistics Polling**:
```
Start Simulation
    ↓
startStatsPoll()
    ↓
setInterval(updateStatsDisplay, 500ms)
    ↓
GET /api/stats (every 500ms)
    ↓
updateStats(response)
    ├─ UI.statProcessed.textContent = processed
    ├─ UI.statDropped.textContent = dropped
    └─ ... update other counters
    
Stop Simulation
    ↓
stopStatsPoll()
    ↓
clearInterval (stop background requests)
```

---

## 🔄 Request/Response Flows

### Start Simulation Flow

```
User clicks "Start" button
    ↓
JavaScript: startSimulation()
    ├─ gatherConfigFromUI() → config object
    └─ apiCall('/start', 'POST', config)
    ↓
HTTP POST /api/start {config}
    ↓
Flask: start() endpoint
    ├─ engine.update_config(config)
    └─ success = engine.start()
    ↓
NetworkImpairmentEngine.start()
    ├─ Create WinDivert handle
    ├─ Start capture_thread
    ├─ Start process_thread
    └─ Return success
    ↓
Flask: return {'status': 'running'}
    ↓
JavaScript: startSimulation() continues
    ├─ AppState.isRunning = true
    ├─ updateUIState() (disable Start, enable Stop)
    ├─ startStatsPoll() (begin 500ms updates)
    └─ showToast('✓ Started!', 'success')
    ↓
User sees green status + stats updating
```

### Packet Processing Flow

```
Real Network Layer
    ↓
WinDivert Intercepts Packet (matches filter)
    ↓
capture_thread: divert_handle.recv()
    ├─ Receives packet object from WinDivert
    └─ Calls _apply_effects(packet)
    ↓
_apply_effects(packet)
    ├─ DROP: rand() * 100 < drop_chance? → return (discard)
    ├─ DUPLICATE: for i in duplicate_count → add copy to queue
    ├─ TAMPER: modify packet.payload, recalc checksum
    ├─ OOO: add rand delay (0-100ms)
    ├─ THROTTLE: add rand delay (0-throttle_ms)
    ├─ LAG: add lag_ms
    ├─ QUEUE: packet_queue.add(packet, total_delay)
    └─ stats['processed'] += 1
    ↓
packet_queue (FIFO with timestamps)
    ├─ {packet, timestamp, delay, ready_time}
    └─ Multiple packets stored
    ↓
process_thread: _process_loop()
    ├─ Every 1ms: get_ready_packets()
    ├─ For each ready packet:
    │   └─ divert_handle.send(packet) → back to network
    └─ stats['delayed'] += 1
    ↓
Real Network Layer receives packet
```

### Statistics Update Flow

```
UI: Every 500ms (polling)
    ↓
JavaScript: updateStatsDisplay()
    └─ GET /api/stats
    ↓
Flask: get_stats()
    └─ engine.get_stats()
    ↓
NetworkImpairmentEngine.get_stats()
    ├─ stats = packet_queue.get_stats()
    ├─ stats['running'] = is_running
    ├─ stats['queue_size'] = len(queue)
    └─ return stats dict
    ↓
Flask: return {processed: 123, dropped: 5, ...}
    ↓
JavaScript: updateStats(response)
    ├─ UI.statProcessed.textContent = '123'
    ├─ UI.statDropped.textContent = '5'
    └─ ... update all counters
    ↓
User sees live updating numbers
```

---

## 🎨 Styling Techniques

### Dark Theme Implementation
```css
/* All colors use CSS variables */
color: var(--text-primary);
background: var(--bg-secondary);

/* High contrast for readability */
Normal text:     #e0e0e0 on #2d2d2d (WCAG AA)
Accent text:     #14a085 (teal)
Status success:  #28a745 (green)
Status error:    #dc3545 (red)
```

### Responsive Grid
```css
/* Main layout */
grid-template-columns: 1fr 1fr;         /* 2 equal columns */
@media (max-width: 1200px) {
    grid-template-columns: 1fr;         /* 1 column on small screens */
}

/* Stats grid */
grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
/* Responsive: at least 100px wide, fills available space */
```

### Slider Styling
```css
/* Custom slider appearance */
.slider {
    /* Use gradient background instead of track color */
    background: linear-gradient(to right, blue, teal);
}

::-webkit-slider-thumb {
    /* Completely custom thumb */
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background-color: teal;
}

/* Hover effect */
::-webkit-slider-thumb:hover {
    transform: scale(1.2);
    box-shadow: 0 0 8px rgba(20, 160, 133, 0.5);
}
```

### Animations
```css
/* Toast notifications */
@keyframes slideIn {
    from { transform: translateX(400px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

.toast { animation: slideIn 0.3s ease forwards; }
.toast.fade-out { animation: slideOut 0.3s ease forwards; }
```

---

## ⚡ Performance Optimizations

### 1. Network Engine
- **Non-blocking Queue**: Packets stored with ready_time, not slept
- **Efficient Polling**: 1ms loop (not busy-wait)
- **Lock Minimization**: Only lock when accessing shared queue
- **Memory Bounded**: `deque(maxlen=X)` prevents unbounded growth

### 2. Frontend
- **Event Delegation**: Reuse listeners where possible
- **DOM Caching**: UI elements stored in object reference
- **Debounced Updates**: Stats update every 500ms, not on every change
- **CSS Optimization**: CSS Grid instead of nested divs
- **Smooth Animations**: CSS transitions (GPU-accelerated)

### 3. Flask Server
- **Threaded**: Handle concurrent requests
- **No Debug Mode**: `debug=False` in production
- **No Reloader**: `use_reloader=False` (prevents duplicates)
- **JSON Responses**: Lightweight, fast serialization

### 4. Threading Strategy
- **Main Thread**: Flask WSGI server (can handle multiple requests)
- **Capture Thread**: Packet reception (blocks on recv)
- **Process Thread**: Packet injection (sleeps on idle)
- **No GIL Contention**: I/O-bound threads (not CPU-bound)

---

## 🔍 Debugging Tips

### Enable Console Logging
In network.py:
```python
logging.basicConfig(level=logging.DEBUG)  # Change from INFO
```

### Check Flask Requests
```python
@app.after_request
def log_request(response):
    print(f"{request.method} {request.path} → {response.status_code}")
    return response
```

### Monitor Packet Queue
```python
# In _process_loop:
if len(self.packet_queue.queue) > 10:
    logger.warning(f"Queue building up: {len(self.packet_queue.queue)}")
```

### Browser DevTools
- F12 → Network tab: See API requests
- F12 → Console: JavaScript errors
- F12 → Application: Local storage, cookies

### WinDivert Debugging
```bash
# Command line to test filter:
# (Requires WinDivert tools installed)
windivert-test.exe "tcp.DstPort == 443"
```

---

## 🚀 Deployment Checklist

- [ ] All dependencies listed in requirements.txt
- [ ] No hardcoded paths (use relative paths)
- [ ] Error handling for missing WinDivert
- [ ] Admin privilege check at startup
- [ ] Self-destruct tested
- [ ] Build script (PyInstaller) working
- [ ] Documentation complete and accurate
- [ ] No debugging statements left (or only at DEBUG level)
- [ ] SSL/HTTPS considered (for production)
- [ ] Configuration validation implemented

---

**This document is a developer's companion for understanding the codebase architecture and implementation details.**
