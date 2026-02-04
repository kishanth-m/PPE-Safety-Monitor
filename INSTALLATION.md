# Installation & Setup Instructions

## System Requirements

- **Operating System**: Windows 10/11, macOS, or Linux
- **Python**: Version 3.8 or higher
- **RAM**: Minimum 4GB (8GB recommended)
- **Camera**: Built-in webcam or USB camera
- **Internet**: Required for first-time model download (~6MB)

## Step-by-Step Installation

### 1. Verify Python Installation

Open terminal/command prompt and check Python version:

```bash
python --version
```

If Python is not installed, download from [python.org](https://www.python.org/downloads/)

### 2. Navigate to Project Directory

```bash
cd ppe-safety-monitor
```

### 3. Install Dependencies

Install all required packages using pip:

```bash
pip install -r requirements.txt
```

**What gets installed:**
- `opencv-python` (4.8.1.78) - Video capture and processing
- `ultralytics` (8.0.196) - YOLOv8 framework
- `numpy` (1.24.3) - Numerical computations
- `Pillow` (10.0.1) - Image handling

**Installation time:** ~2-5 minutes depending on internet speed

### 4. Verify Installation

Run the demo helper to check everything is set up:

```bash
python demo.py
```

This will:
- Check all dependencies
- Verify camera access
- Show demo tips
- Launch the system when you press ENTER

## Alternative: Direct Run

If you prefer to skip the demo helper:

```bash
python ppe_detector.py
```

## First Run

On the first run, the system will:
1. Download YOLOv8n model (~6MB) from Ultralytics
2. Save it to the `models/` directory
3. Start the detection system

**Note:** This only happens once. Subsequent runs will be instant.

## Troubleshooting Installation

### Issue: "pip not found"

**Solution:**
```bash
python -m pip install -r requirements.txt
```

### Issue: "Permission denied"

**Solution (Windows):**
Run as administrator or use:
```bash
pip install --user -r requirements.txt
```

**Solution (Mac/Linux):**
```bash
pip3 install -r requirements.txt
```

### Issue: "No module named cv2"

**Solution:**
```bash
pip install opencv-python
```

### Issue: Slow installation

**Solution:** Use a faster mirror:
```bash
pip install -r requirements.txt -i https://pypi.org/simple
```

## Running the System

### Option 1: Demo Mode (Recommended for first-time)
```bash
python demo.py
```

### Option 2: Direct Mode
```bash
python ppe_detector.py
```

### Option 3: With Custom Settings
Edit `ppe_detector.py` and modify:
```python
detector = PPEDetector(
    model_name='yolov8n.pt',      # Change to yolov8s.pt for better accuracy
    confidence_threshold=0.5       # Adjust detection sensitivity
)
```

## Camera Setup

### Windows
- Camera permissions are usually automatic
- If issues occur, check Settings → Privacy → Camera

### macOS
- Grant camera permission when prompted
- Or: System Preferences → Security & Privacy → Camera

### Linux
- Ensure user is in `video` group:
  ```bash
  sudo usermod -a -G video $USER
  ```

## Testing the System

1. **Start the system**
2. **Position yourself** in front of camera
3. **Look for**:
   - Green "✓ COMPLIANT" status
   - FPS counter (should be 20-30)
   - Bounding boxes on detected objects
4. **Test violation detection**:
   - Move out of frame
   - Cover face
   - Check if warning appears
5. **Check outputs**:
   - `logs/` folder for violation logs
   - `violations/` folder for screenshots

## Uninstallation

To remove the project:

1. Delete the project folder
2. (Optional) Uninstall packages:
   ```bash
   pip uninstall opencv-python ultralytics numpy Pillow
   ```

## Getting Help

- Check `README.md` for detailed documentation
- Review `HOW_IT_WORKS.md` for technical explanation
- See `QUICKSTART.md` for rapid setup guide

---

**Ready to demo?** Run `python demo.py` and press ENTER! 🚀
