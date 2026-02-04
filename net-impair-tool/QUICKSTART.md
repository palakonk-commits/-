# Quick Start Guide - Network Impairment Tool

## Installation (5 minutes)

### 1. Install Python
- Download Python 3.10+ from https://www.python.org
- **Important**: Check "Add Python to PATH" during installation

### 2. Install WinDivert Driver
- Download from: https://www.reqrypt.org/windivert.html
- Extract to `C:\WinDivert\` or add to PATH

### 3. Setup Project
```bash
# Run setup script
setup.bat

# Or manual setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Running the Tool

### Option 1: Simple (Recommended)
```bash
run_as_admin.bat
```

### Option 2: Manual
```bash
# In Command Prompt (Run as Administrator)
python main.py
```

### Option 3: Compiled Executable
```bash
build.bat              # Builds NetworkImpairment.exe
# Then double-click dist\NetworkImpairment.exe
```

## First Launch

1. **Command Prompt Window**: Shows Python debug output
2. **Browser Window**: Opens web interface at http://127.0.0.1:5000/
3. **System Tray**: Icon appears in taskbar

## Basic Usage

### Test Configuration

1. **Set Filter**: Keep default `outbound and udp`
2. **Enable Lag**: Toggle "Lag / Delay" checkbox
3. **Set Delay**: Slide to 100ms
4. **Click Start**: Begin simulation
5. **Open another window**: Visit https://www.google.com (or any site)
6. **Notice**: Network requests will be delayed
7. **Click Stop**: End simulation

### Configuration Tips

- **Filter**: Use `tcp` for HTTP/HTTPS, `udp` for gaming
- **Lag**: 50-150ms feels noticeable
- **Drop**: 2-5% causes visible issues
- **Throttle**: Combined with Lag for congestion effect

## Troubleshooting

### "Admin required" message
- Right-click → Run as Administrator
- Or use `run_as_admin.bat`

### "WinDivert not found" error
- Install from https://www.reqrypt.org/windivert.html
- Add to PATH or copy to `C:\WinDivert\`

### No packets captured
- Try filter `tcp` instead of `udp`
- Ensure application is running as Administrator
- Check System Tray icon exists

### High CPU usage
- Use more specific filter (e.g., `tcp.DstPort == 443`)
- Disable unnecessary effects
- Close other applications

## Feature Overview

| Feature | Purpose | Example |
|---------|---------|---------|
| Lag | Add delay (ms) | 150ms for gaming |
| Drop | Lose packets (%) | 5% for poor WiFi |
| Throttle | Limit bandwidth (ms/%) | 20ms every 50% |
| Duplicate | Copy packets | 1 copy 5% of time |
| Out-of-Order | Reorder packets | 20% chance |
| Tamper | Corrupt data | 5% chance |

## Common Scenarios

### Test Gaming with High Latency
```
Filter: outbound and udp
Lag: 200ms
Drop: 3%
```

### Simulate Congested Network
```
Filter: tcp
Throttle: 50ms (30% chance)
Out-of-Order: 25%
Drop: 2%
```

### Stress Test Application
```
Filter: tcp
Lag: 100ms
Drop: 10%
Duplicate: 2 copies (10%)
Tamper: 5%
```

## Getting Help

1. **Check README.md** - Full documentation
2. **System Tray** - Click icon for options
3. **WinDivert Help** - https://www.reqrypt.org/windivert.html
4. **Filter Syntax** - Read WinDivert documentation

## Important Notes

⚠️ **Required: Administrator Privileges**
- Always run as Administrator
- WinDivert needs kernel-level access

⚠️ **Test Responsibly**
- Only test networks you own or have permission for
- Disable effects when done testing
- Don't use on production networks

✅ **Recommendations**
- Test in isolated environment first
- Start with simple configurations
- Monitor statistics while testing
- Use descriptive filter expressions

## Next Steps

1. Read **README.md** for advanced features
2. Experiment with different filters
3. Combine effects for realistic scenarios
4. Check statistics panel for results
5. Build as executable for easier distribution

---

*For detailed documentation, see README.md*
