"""
Real-Time PPE Compliance & Safety Monitoring System
Author: Kishanth m _ 3rd year AI/DS Student
Description:
    Real-time shop floor and construction site safety gear monitoring
    using Ultralytics YOLOv8 for object detection and YOLOv8-Pose for
    anatomical keypoint tracking.
"""

import os
import time
from datetime import datetime
import cv2
import numpy as np
from ultralytics import YOLO


class PPEDetector:
    """
    Main detection pipeline combining human pose estimation and object detection
    to verify PPE compliance (helmets, masks, gloves, safety shoes) in real-time.
    """

    def __init__(self, model_name='yolov8n.pt', confidence_threshold=0.5):
        print("[INFO] Initializing PPE Safety Monitor...")
        print(f"[INFO] Loading object detection model ({model_name})...")
        self.model = YOLO(model_name)

        print("[INFO] Loading pose estimation model (yolov8n-pose.pt)...")
        self.pose_model = YOLO('yolov8n-pose.pt')
        self.confidence_threshold = confidence_threshold

        # List of mandatory PPE items to monitor
        self.required_ppe = ['helmet', 'mask', 'gloves', 'shoes']

        # Manual override toggles (useful for live demonstration/testing)
        self.manual_overrides = {
            'helmet': False,
            'mask': False,
            'gloves': False,
            'shoes': False
        }
        # Backward-compatible alias
        self.demo_overrides = self.manual_overrides

        # Violation tracking & snapshot rate limiting
        self.violation_count = 0
        self.last_violation_time = 0
        self.violation_cooldown = 3  # minimum seconds between violation snapshots

        # Directories for persistence
        self.log_dir = 'logs'
        self.violation_dir = 'violations'
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.violation_dir, exist_ok=True)

        # Create session log file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = os.path.join(self.log_dir, f'violations_{timestamp}.txt')

        print("[INFO] PPE Safety Monitor initialized successfully!")
        print(f"[INFO] Monitoring for: {', '.join(self.required_ppe)}")
        print(f"[INFO] Violation logs will be saved to: {self.log_file}")

    def _overlap(self, part_bbox, detections, keywords):
        """
        Check if any detected object matching the target keywords overlaps
        with the specified anatomical bounding box.
        """
        px1, py1, px2, py2 = part_bbox
        for cls_name, (dx1, dy1, dx2, dy2), _ in detections:
            if not any(k in cls_name.lower() for k in keywords):
                continue
            # Intersection test
            if min(px2, dx2) > max(px1, dx1) and min(py2, dy2) > max(py1, dy1):
                return True
        return False

    def check_compliance(self, detections, pose_results):
        """
        Match detected objects with anatomical keypoint locations.
        Keypoint mapping (COCO 17 keypoints):
          - 0 to 4: Nose, Eyes, Ears (Head region)
          - 9, 10: Left & Right Wrists (Hands region)
          - 15, 16: Left & Right Ankles (Feet region)
        """
        detected_ppe = set()
        body_parts = {'heads': [], 'hands': [], 'feet': []}

        if pose_results and len(pose_results) > 0:
            for result in pose_results:
                if not result.keypoints:
                    continue

                for kps in result.keypoints.data:
                    if kps.shape[0] == 0:
                        continue
                    kps = kps.cpu().numpy()

                    # 1. Head Region (Keypoints 0-4: nose, eyes, ears)
                    head_pts = kps[0:5]
                    if np.any(head_pts[:, 2] > 0.5):
                        valid_pts = head_pts[head_pts[:, 2] > 0.5]
                        x_min, y_min = np.min(valid_pts[:, 0]), np.min(valid_pts[:, 1])
                        x_max, y_max = np.max(valid_pts[:, 0]), np.max(valid_pts[:, 1])
                        pad = int((x_max - x_min) * 0.5)
                        head_bbox = (
                            int(x_min - pad),
                            int(y_min - pad),
                            int(x_max + pad),
                            int(y_max + pad * 1.5)
                        )

                        has_helmet = (
                            self._overlap(head_bbox, detections, ['helmet', 'hat', 'hardhat'])
                            or self.manual_overrides['helmet']
                        )
                        has_mask = (
                            self._overlap(head_bbox, detections, ['mask', 'face_mask'])
                            or self.manual_overrides['mask']
                        )

                        if has_helmet:
                            detected_ppe.add('helmet')
                        if has_mask:
                            detected_ppe.add('mask')

                        body_parts['heads'].append({
                            'bbox': head_bbox,
                            'has_helmet': has_helmet,
                            'has_mask': has_mask
                        })

                    # 2. Hands Region (Keypoints 9 & 10: wrists)
                    for idx in [9, 10]:
                        if kps[idx][2] > 0.5:
                            x, y = kps[idx][0], kps[idx][1]
                            box_radius = 40
                            hand_bbox = (
                                int(x - box_radius),
                                int(y - box_radius),
                                int(x + box_radius),
                                int(y + box_radius)
                            )
                            has_glove = (
                                self._overlap(hand_bbox, detections, ['glove'])
                                or self.manual_overrides['gloves']
                            )
                            if has_glove:
                                detected_ppe.add('gloves')
                            body_parts['hands'].append({
                                'bbox': hand_bbox,
                                'has_glove': has_glove
                            })

                    # 3. Feet Region (Keypoints 15 & 16: ankles)
                    for idx in [15, 16]:
                        if kps[idx][2] > 0.5:
                            x, y = kps[idx][0], kps[idx][1]
                            box_radius = 40
                            foot_bbox = (
                                int(x - box_radius),
                                int(y - box_radius),
                                int(x + box_radius),
                                int(y + box_radius)
                            )
                            has_shoe = (
                                self._overlap(foot_bbox, detections, ['shoe', 'boot', 'safety'])
                                or self.manual_overrides['shoes']
                            )
                            if has_shoe:
                                detected_ppe.add('shoes')
                            body_parts['feet'].append({
                                'bbox': foot_bbox,
                                'has_shoe': has_shoe
                            })

        missing = [item for item in self.required_ppe if item not in detected_ppe]
        is_compliant = (len(missing) == 0)
        return is_compliant, missing, body_parts

    def _draw_label(self, frame, text, x, y, color):
        """Helper to draw text label with a filled colored background box."""
        (w, h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
        cv2.rectangle(frame, (x, y - h - 10), (x + w + 10, y), color, -1)
        cv2.putText(frame, text, (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    def draw(self, frame, parts, missing):
        """Draw bounding boxes and status labels on detected body parts."""
        # Annotate Head
        for head in parts.get('heads', []):
            x1, y1, x2, y2 = head['bbox']
            missing_head = []
            if 'helmet' in self.required_ppe and not head['has_helmet']:
                missing_head.append('HELMET')
            if 'mask' in self.required_ppe and not head['has_mask']:
                missing_head.append('MASK')

            color = (0, 255, 0) if not missing_head else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
            status_text = "HEAD: OK" if not missing_head else f"Missing: {','.join(missing_head)}"
            self._draw_label(frame, status_text, x1, y1, color)

        # Annotate Hands / Gloves
        if 'gloves' in self.required_ppe:
            for hand in parts.get('hands', []):
                x1, y1, x2, y2 = hand['bbox']
                color = (0, 255, 0) if hand['has_glove'] else (0, 0, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                status_text = "GLOVE: OK" if hand['has_glove'] else "Missing: GLOVE"
                self._draw_label(frame, status_text, x1, y1, color)

        # Annotate Feet / Shoes
        if 'shoes' in self.required_ppe:
            for foot in parts.get('feet', []):
                x1, y1, x2, y2 = foot['bbox']
                color = (0, 255, 0) if foot['has_shoe'] else (0, 0, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                status_text = "SHOE: OK" if foot['has_shoe'] else "Missing: SHOE"
                self._draw_label(frame, status_text, x1, y1, color)

        return frame

    def run(self):
        """Main real-time video capture and detection loop."""
        print("\n" + "=" * 60)
        print(" Starting webcam feed...")
        print(" Controls: Press 'Q' to quit | 'H': Helmet | 'M': Mask | 'G': Gloves | 'S': Shoes")
        print("=" * 60 + "\n")

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[ERROR] Cannot access webcam. Please verify camera connection.")
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        window_name = 'PPE Safety Monitor'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 800, 600)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

        frame_count = 0
        skip_frames = 2  # Process every 3rd frame for smooth CPU performance
        last_results = ([], None)  # (detections, pose_results)

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("[ERROR] Failed to read frame from webcam.")
                    break

                # Frame skipping for real-time CPU performance
                if frame_count % (skip_frames + 1) == 0:
                    det = self.model(frame, verbose=False, conf=self.confidence_threshold)[0]
                    pose = self.pose_model(frame, verbose=False, conf=0.5)[0]

                    detections = []
                    for box in det.boxes:
                        cls_name = self.model.names[int(box.cls[0])]
                        coords = tuple(map(int, box.xyxy[0]))
                        conf = float(box.conf[0])
                        detections.append((cls_name, coords, conf))

                    last_results = (detections, [pose])

                detections, pose_results = last_results

                person_detected = False
                if pose_results:
                    person_detected = any(
                        r.keypoints and r.keypoints.data.shape[0] > 0
                        for r in pose_results
                    )

                annotated = frame.copy()
                is_compliant = True

                if person_detected:
                    is_compliant, missing, parts = self.check_compliance(detections, pose_results)
                    annotated = self.draw(annotated, parts, missing)

                    # Handle safety violations
                    if not is_compliant:
                        current_time = time.time()
                        if current_time - self.last_violation_time > self.violation_cooldown:
                            self.violation_count += 1
                            timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            entry = f"[{timestamp_str}] VIOLATION #{self.violation_count}: Missing {', '.join(missing)}\n"

                            with open(self.log_file, 'a') as f:
                                f.write(entry)
                            print(f"[VIOLATION] {entry.strip()}")

                            snapshot_filename = f'violations/violation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
                            cv2.imwrite(snapshot_filename, annotated)
                            print(f"[EVIDENCE] Screenshot saved: {snapshot_filename}")

                            self.last_violation_time = current_time

                cv2.imshow(window_name, annotated)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    print("[INFO] Quitting application...")
                    break
                elif key == ord('h') or key == ord('H'):
                    self.manual_overrides['helmet'] = not self.manual_overrides['helmet']
                    print(f"[TEST OVERRIDE] Helmet: {self.manual_overrides['helmet']}")
                elif key == ord('m') or key == ord('M'):
                    self.manual_overrides['mask'] = not self.manual_overrides['mask']
                    print(f"[TEST OVERRIDE] Mask: {self.manual_overrides['mask']}")
                elif key == ord('g') or key == ord('G'):
                    self.manual_overrides['gloves'] = not self.manual_overrides['gloves']
                    print(f"[TEST OVERRIDE] Gloves: {self.manual_overrides['gloves']}")
                elif key == ord('s') or key == ord('S'):
                    self.manual_overrides['shoes'] = not self.manual_overrides['shoes']
                    print(f"[TEST OVERRIDE] Shoes: {self.manual_overrides['shoes']}")

                frame_count += 1

        except KeyboardInterrupt:
            print("\n[INFO] Interrupted by user.")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            with open(self.log_file, 'a') as f:
                f.write(f"\nSession Ended: {datetime.now()}\nTotal Violations: {self.violation_count}\n")
            print(f"\n[INFO] Session complete. Total violations recorded: {self.violation_count}")


def main():
    """Entry point for the PPE detection application."""
    detector = PPEDetector()
    detector.run()


if __name__ == "__main__":
    main()
