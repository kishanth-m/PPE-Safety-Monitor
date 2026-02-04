# AI-Based PPE Compliance & Shop Floor Safety Monitoring System

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8-green.svg)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-orange.svg)

A high-performance **real-time PPE (Personal Protective Equipment) compliance monitoring system** that uses **Pose Estimation** and **YOLOv8** to check for safety gear (Helmets, Masks, Gloves, Shoes) on shop floors. Optimized for standard laptops with special Demo features.

## 🚀 Key Features

*   **⚡ Turbo Mode**: Processes every 3rd frame to triple FPS (20-30+ FPS on CPU).
*   **🧙‍♂️ Demo Mode ("Wizard of Oz")**: Manual keyboard overrides to force "Compliant" status during live demos if AI misses an item.
*   **🧠 Hybrid Detection**: Uses Pose Estimation to track body parts (Head, Hands, Feet) + Object Detection for gear.
*   **🤫 Silent Operation**: Zero console spam. Runs quietly in the background.
*   **📸 Automatic Evidence**: Logs violations and captures screenshots automatically.
*   **🔒 Privacy First**: Runs locally offline. No data is sent to the cloud.

## 🔍 What It Detects

The system tracks specific body parts and checks for:
- 🪖 **Head**: Safety Helmet & Face Mask
- 🧤 **Hands**: Safety Gloves
- 👞 **Feet**: Safety Shoes

## 📁 Project Structure

```
ppe-safety-monitor/
├── ppe_detector.py          # Main System (Minified & Optimized)
├── demo.py                  # Demo Helper Script
├── requirements.txt         # Dependencies
├── logs/                    # Timestamped Violation Logs
├── violations/              # Evidence Screenshots
└── models/                  # AI Models (Auto-downloaded)
```

## 🛠️ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the System
```bash
python ppe_detector.py
```
*Note: First run will download the AI models (~12MB total).*

## 🎮 Controls (Demo Mode)

**Standard Controls:**
- `Q`: Quit

**🧙‍♂️ Magic Demo Keys (Wizard of Oz):**
Use these keys to manually toggle an item to **GREEN (Compliant)** if the AI misses it:
- `H`: Toggle **Helmet**
- `M`: Toggle **Mask**
- `G`: Toggle **Gloves**
- `S`: Toggle **Shoes**

## 📊 How It Works

1.  **Pose Estimation**: Finds the person's skeleton (Nose, Wrists, Ankles).
2.  **Object Detection**: Scans for "Helmet", "Mask", "Glove", "Shoe".
3.  **Geometric Matching**: Checks if the detected object overlaps with the correct body part.
4.  **Compliance Check**: 
    - **Green Box**: Item detected OR Manual Override ON.
    - **Red Box**: Item missing AND Person detected.
5.  **Evidence**: If a violation lasts >3 seconds, it saves a photo to `violations/`.

## ⚙️ Customization

Open `ppe_detector.py` to adjust:
- `self.required_ppe`: List of items to check (e.g., remove 'gloves').
- `self.violation_cooldown`: Time between screenshots.

---
**Made for Hackathon 2026** 🚀
*Open source for educational purposes.*
