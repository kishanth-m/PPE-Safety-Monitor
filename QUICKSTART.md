# Quick Start Guide

## Installation (One-time setup)

1. Open terminal/command prompt
2. Navigate to project folder:
   ```
   cd ppe-safety-monitor
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the System

```
python ppe_detector.py
```

## Controls

- Press **Q** to quit

## What to Expect

- ✅ Green "COMPLIANT" when PPE is detected
- ⚠️ Red warning when PPE is missing
- Screenshots saved in `violations/` folder
- Logs saved in `logs/` folder

## Troubleshooting

**Webcam not working?**
- Close other apps using camera
- Check camera permissions

**Slow performance?**
- Close other applications
- System is optimized for CPU

**Model downloading?**
- First run downloads YOLOv8 (~6MB)
- Needs internet connection

---

That's it! You're ready to demo! 🚀
