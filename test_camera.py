"""
Simple Camera Test Script
This script tests if your webcam and OpenCV window display are working.
"""

import cv2
import sys

print("\n" + "=" * 60)
print("  WEBCAM & WINDOW TEST")
print("=" * 60)
print("\nTesting your camera and OpenCV window display...")
print("Press 'Q' to quit\n")

# Try to open camera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print(" ERROR: Cannot access webcam!")
    print("   Possible reasons:")
    print("   - Camera is being used by another application")
    print("   - Camera permissions not granted")
    print("   - No camera connected")
    sys.exit(1)

print(" Camera opened successfully!")
print(" Creating window...")

# Create window with specific properties
window_name = 'Camera Test - Press Q to Quit'
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 800, 600)

# Try to make window topmost
try:
    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
    print(" Window set to topmost")
except:
    print("  Could not set window to topmost (this is OK)")

print("\n" + "=" * 60)
print("  LOOK FOR THE CAMERA WINDOW!")
print("  It should show your webcam feed")
print("  Press 'Q' on your keyboard to quit")
print("=" * 60 + "\n")

frame_count = 0

while True:
    ret, frame = cap.read()
    
    if not ret:
        print(" ERROR: Failed to read frame from camera!")
        break
    
    frame_count += 1
    
    # Add text to frame
    cv2.putText(frame, f"Frame: {frame_count}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, "Press 'Q' to quit", (10, 70), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, "If you see this, camera works!", (10, 110), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    
    # Display the frame
    cv2.imshow(window_name, frame)
    
    # Check for 'Q' key
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == ord('Q'):
        print(f"\n Test complete! Processed {frame_count} frames.")
        break

# Clean up
cap.release()
cv2.destroyAllWindows()

print("\n" + "=" * 60)
print("  Test finished successfully!")
print("=" * 60 + "\n")
