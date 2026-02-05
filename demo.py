"""
Demo Helper Script for PPE Safety Monitor
==========================================
This script provides a simplified demo mode for testing and presentations.
It includes helpful tips and a more user-friendly startup experience.
"""

import sys
import os

def print_banner():
    """Display a welcome banner."""
    print("\n" + "=" * 70)
    print("   AI-BASED PPE COMPLIANCE & SAFETY MONITORING SYSTEM 🏭")
    print("=" * 70)
    print("  Hackathon 2026 - Real-time Safety Monitoring Demo")
    print("=" * 70 + "\n")

def check_dependencies():
    """Check if required packages are installed."""
    print(" Checking dependencies...")
    
    required_packages = {
        'cv2': 'opencv-python',
        'ultralytics': 'ultralytics',
        'numpy': 'numpy',
        'PIL': 'Pillow'
    }
    
    missing = []
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print("\n Missing dependencies detected!")
        print(f"   Please run: pip install {' '.join(missing)}")
        print("   Or: pip install -r requirements.txt\n")
        return False
    
    print(" All dependencies installed!\n")
    return True

def check_camera():
    """Check if camera is available."""
    print(" Checking camera availability...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, _ = cap.read()
            cap.release()
            if ret:
                print(" Camera is working!\n")
                return True
        print("  Camera might not be available")
        print("   Make sure no other app is using it\n")
        return False
    except Exception as e:
        print(f"  Camera check failed: {e}\n")
        return False

def show_demo_tips():
    """Display helpful demo tips."""
    print(" DEMO TIPS:")
    print("=" * 70)
    print("1. Position yourself clearly in front of the camera")
    print("2. Ensure good lighting for better detection")
    print("3. Use props (toy helmet, mask) or printed images for demo")
    print("4. The system detects objects in real-time at ~20-30 FPS")
    print("5. Violations are logged with 3-second cooldown")
    print("6. Press 'Q' to quit anytime")
    print("=" * 70 + "\n")

def show_controls():
    """Display control information."""
    print(" CONTROLS:")
    print("=" * 70)
    print("  Q or q  →  Quit the application")
    print("=" * 70 + "\n")

def show_features():
    """Display system features."""
    print(" FEATURES:")
    print("=" * 70)
    print("  ✓ Real-time PPE detection using YOLOv8")
    print("  ✓ Visual violation warnings on screen")
    print("  ✓ Automatic violation logging with timestamps")
    print("  ✓ Screenshot capture on violations")
    print("  ✓ FPS counter and compliance status display")
    print("  ✓ CPU-optimized for laptop use (no GPU needed)")
    print("=" * 70 + "\n")

def main():
    """Main demo launcher."""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check camera
    check_camera()
    
    # Show information
    show_features()
    show_demo_tips()
    show_controls()
    
    # Prompt to start
    print(" Ready to start the PPE Safety Monitor!")
    input("   Press ENTER to begin... ")
    print("\n")
    
    # Import and run the main detector
    try:
        from ppe_detector import main as run_detector
        run_detector()
    except KeyboardInterrupt:
        print("\n\n👋 Demo cancelled by user. Goodbye!")
    except Exception as e:
        print(f"\n\n Error running detector: {e}")
        print("   Check the error message above for details.\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
