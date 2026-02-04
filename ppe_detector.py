import cv2
import numpy as np
from ultralytics import YOLO
from datetime import datetime
import os
import time

class PPEDetector:
    def __init__(self, model_name='yolov8n.pt', confidence_threshold=0.5):
        print(" Initializing PPE Safety Monitor...")
        print(f" Loading {model_name} model...")
        self.model = YOLO(model_name)
        print(" Loading yolov8n-pose.pt model...")
        self.pose_model = YOLO('yolov8n-pose.pt')
        self.confidence_threshold = confidence_threshold
        
        self.required_ppe = ['helmet', 'mask', 'gloves', 'shoes']
        self.demo_overrides = {'helmet': False, 'mask': False, 'gloves': False, 'shoes': False}
        
        self.violation_count = 0
        self.last_violation_time = 0
        self.violation_cooldown = 3
        
        self.log_dir = 'logs'
        self.violation_dir = 'violations'
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.violation_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = os.path.join(self.log_dir, f'violations_{timestamp}.txt')
        
        print(" PPE Safety Monitor initialized successfully!")
        print(f" Monitoring for: {', '.join(self.required_ppe)}")
        print(f" Logging violations to: {self.log_file}")
    

    def check_compliance(self, detections, pose_results):
        detected_ppe = set()
        body_parts = {'heads': [], 'hands': [], 'feet': []}
        
        if pose_results and len(pose_results) > 0:
            for result in pose_results:
                if not result.keypoints: continue
                for kps in result.keypoints.data:
                    if kps.shape[0] == 0: continue
                    kps = kps.cpu().numpy()
                    
                    head_pts = kps[0:5]
                    if np.any(head_pts[:, 2] > 0.5):
                        valid_pts = head_pts[head_pts[:, 2] > 0.5]
                        x_min, y_min = np.min(valid_pts[:, 0]), np.min(valid_pts[:, 1])
                        x_max, y_max = np.max(valid_pts[:, 0]), np.max(valid_pts[:, 1])
                        pad = int((x_max - x_min) * 0.5)
                        bbox = (int(x_min - pad), int(y_min - pad), int(x_max + pad), int(y_max + pad * 1.5))
                        
                        has_helmet = self._overlap(bbox, detections, ['helmet', 'hat', 'hardhat']) or self.demo_overrides['helmet']
                        has_mask = self._overlap(bbox, detections, ['mask', 'face_mask']) or self.demo_overrides['mask']
                        
                        if has_helmet: detected_ppe.add('helmet')
                        if has_mask: detected_ppe.add('mask')
                        body_parts['heads'].append({'bbox': bbox, 'has_helmet': has_helmet, 'has_mask': has_mask})

                    for idx in [9, 10]:
                        if kps[idx][2] > 0.5:
                            x, y = kps[idx][0], kps[idx][1]
                            size = 40
                            bbox = (int(x - size), int(y - size), int(x + size), int(y + size))
                            has_glove = self._overlap(bbox, detections, ['glove']) or self.demo_overrides['gloves']
                            if has_glove: detected_ppe.add('gloves')
                            body_parts['hands'].append({'bbox': bbox, 'has_glove': has_glove})

                    for idx in [15, 16]:
                        if kps[idx][2] > 0.5:
                            x, y = kps[idx][0], kps[idx][1]
                            size = 40
                            bbox = (int(x - size), int(y - size), int(x + size), int(y + size))
                            has_shoe = self._overlap(bbox, detections, ['shoe', 'boot', 'safety']) or self.demo_overrides['shoes']
                            if has_shoe: detected_ppe.add('shoes')
                            body_parts['feet'].append({'bbox': bbox, 'has_shoe': has_shoe})

        missing = [i for i in self.required_ppe if i not in detected_ppe]
        return len(missing) == 0, missing, body_parts

    def _overlap(self, part, detections, keywords):
        px1, py1, px2, py2 = part
        for cls, (dx1, dy1, dx2, dy2), _ in detections:
            if not any(k in cls.lower() for k in keywords): continue
            if min(px2, dx2) > max(px1, dx1) and min(py2, dy2) > max(py1, dy1): return True
        return False
    
    def draw(self, frame, parts, missing):
        for head in parts.get('heads', []):
            x1, y1, x2, y2 = head['bbox']
            m = []
            if 'helmet' in self.required_ppe and not head['has_helmet']: m.append('HELMET')
            if 'mask' in self.required_ppe and not head['has_mask']: m.append('MASK')
            color = (0, 255, 0) if not m else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
            self._label(frame, "HEAD: OK" if not m else f"Missing: {','.join(m)}", x1, y1, color)

        if 'gloves' in self.required_ppe:
            for hand in parts.get('hands', []):
                x1, y1, x2, y2 = hand['bbox']
                color = (0, 255, 0) if hand['has_glove'] else (0, 0, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                self._label(frame, "GLOVE: OK" if hand['has_glove'] else "Missing: GLOVE", x1, y1, color)

        if 'shoes' in self.required_ppe:
            for foot in parts.get('feet', []):
                x1, y1, x2, y2 = foot['bbox']
                color = (0, 255, 0) if foot['has_shoe'] else (0, 0, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                self._label(frame, "SHOE: OK" if foot['has_shoe'] else "Missing: SHOE", x1, y1, color)
        return frame

    def _label(self, frame, text, x, y, color):
        (w, h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
        cv2.rectangle(frame, (x, y - h - 10), (x + w + 10, y), color, -1)
        cv2.putText(frame, text, (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    def run(self):
        print("\n" + "=" * 60)
        print(" Starting webcam feed...")
        print("=" * 60)
        print(" Press 'Q' to quit")
        print("=" * 60 + "\n")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened(): return
        cap.set(3, 640); cap.set(4, 480)
        
        window = 'PPE Safety Monitor'
        cv2.namedWindow(window, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window, 800, 600)
        cv2.setWindowProperty(window, cv2.WND_PROP_TOPMOST, 1)
        
        frame_count = 0
        skip_frames = 2 # Process every 3rd frame
        last_results = ([], None) # (detections, pose_results)
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret: break
                
                # Inference skipping for performance
                if frame_count % (skip_frames + 1) == 0:
                    det = self.model(frame, verbose=False, conf=self.confidence_threshold)[0]
                    pose = self.pose_model(frame, verbose=False, conf=0.5)[0]
                    
                    d_info = []
                    for box in det.boxes:
                        d_info.append((self.model.names[int(box.cls[0])], tuple(map(int, box.xyxy[0])), float(box.conf[0])))
                    
                    last_results = (d_info, [pose])
                
                detections, pose_results = last_results
                
                person_detected = any(r.keypoints and r.keypoints.data.shape[0] > 0 for r in pose_results) if pose_results else False
                
                annotated = frame.copy()
                is_compliant = True
                
                if person_detected:
                    is_compliant, missing, parts = self.check_compliance(detections, pose_results)
                    annotated = self.draw(annotated, parts, missing)
                    
                    if not is_compliant:
                        if time.time() - self.last_violation_time > self.violation_cooldown:
                            self.violation_count += 1
                            ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            entry = f"[{ts}] VIOLATION #{self.violation_count}: Missing {', '.join(missing)}\n"
                            with open(self.log_file, 'a') as f: f.write(entry)
                            print(f"log {entry.strip()}")
                            fname = f'violations/violation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
                            cv2.imwrite(fname, annotated)
                            print(f" Screenshot saved: {fname}")
                            self.last_violation_time = time.time()

                cv2.imshow(window, annotated)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'): break
                elif key == ord('h') or key == ord('H'): self.demo_overrides['helmet'] = not self.demo_overrides['helmet']; print(f"🔧 Helmet: {self.demo_overrides['helmet']}")
                elif key == ord('m') or key == ord('M'): self.demo_overrides['mask'] = not self.demo_overrides['mask']; print(f"🔧 Mask: {self.demo_overrides['mask']}")
                elif key == ord('g') or key == ord('G'): self.demo_overrides['gloves'] = not self.demo_overrides['gloves']; print(f"🔧 Gloves: {self.demo_overrides['gloves']}")
                elif key == ord('s') or key == ord('S'): self.demo_overrides['shoes'] = not self.demo_overrides['shoes']; print(f"🔧 Shoes: {self.demo_overrides['shoes']}")
                
                frame_count += 1
                
        except KeyboardInterrupt: pass
        finally:
            cap.release(); cv2.destroyAllWindows()
            with open(self.log_file, 'a') as f:
                f.write(f"\nStopped: {datetime.now()}\nTotal violations: {self.violation_count}\n")
            print(f"\n Session complete! Violations: {self.violation_count}")

if __name__ == "__main__":
    PPEDetector().run()
