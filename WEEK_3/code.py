import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ultralytics import YOLO

# =========================
# CONFIG
# =========================
video_path = "input.mp4"
output_video = "output.mp4"

model = YOLO("yolov8n-seg.pt")

# =========================
# VIDEO SETUP
# =========================
cap = cv2.VideoCapture(video_path)

fps = int(cap.get(cv2.CAP_PROP_FPS))
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

out = cv2.VideoWriter(
    output_video,
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps,
    (w, h)
)

# =========================
# STORAGE
# =========================
logs = []

high_conf_boxes = []   # pseudo GT
low_conf_boxes = []    # predictions

frame_id = 0

# =========================
# PROCESS VIDEO
# =========================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)[0]
    annotated = frame.copy()

    if results.boxes is not None:
        for i in range(len(results.boxes)):
            x1, y1, x2, y2 = map(int, results.boxes.xyxy[i])
            conf = float(results.boxes.conf[i])
            cls = int(results.boxes.cls[i])
            label = model.names[cls]

            logs.append([frame_id, label, conf, x1, y1, x2, y2])

            # -------------------------
            # pseudo labeling strategy
            # -------------------------
            if conf >= 0.7:
                high_conf_boxes.append([frame_id, x1, y1, x2, y2, cls])
            else:
                low_conf_boxes.append([frame_id, x1, y1, x2, y2, cls])

            # draw
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                annotated,
                f"{label} {conf:.2f}",
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

    # segmentation masks
    if results.masks is not None:
        masks = results.masks.data.cpu().numpy()

        for mask in masks:
            mask = cv2.resize(mask, (w, h))
            overlay = np.zeros_like(frame, dtype=np.uint8)
            overlay[:, :, 1] = (mask * 255).astype(np.uint8)
            annotated = cv2.addWeighted(annotated, 1, overlay, 0.3, 0)

    out.write(annotated)
    frame_id += 1

cap.release()
out.release()

# =========================
# SAVE LOGS
# =========================
df = pd.DataFrame(logs, columns=["frame","class","conf","x1","y1","x2","y2"])
df.to_csv("detections.csv", index=False)

# =========================
# PSEUDO CONFUSION MATRIX
# =========================
def iou(box1, box2):
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    inter = max(0, x2-x1) * max(0, y2-y1)

    area1 = (box1[2]-box1[0])*(box1[3]-box1[1])
    area2 = (box2[2]-box2[0])*(box2[3]-box2[1])

    union = area1 + area2 - inter
    return inter / union if union > 0 else 0

TP = FP = FN = 0

for h in high_conf_boxes:
    h_box = h[1:5]

    matched = False
    for l in low_conf_boxes:
        if l[0] == h[0]:  # same frame
            l_box = l[1:5]

            if iou(h_box, l_box) > 0.5:
                TP += 1
                matched = True
                break

    if not matched:
        FN += 1

FP = len(low_conf_boxes)

precision = TP / (TP + FP + 1e-6)
recall = TP / (TP + FN + 1e-6)
f1 = 2 * precision * recall / (precision + recall + 1e-6)

# =========================
# PRINT RESULTS
# =========================
print("\n===== PSEUDO METRICS =====")
print("TP:", TP)
print("FP:", FP)
print("FN:", FN)
print("Precision:", precision)
print("Recall:", recall)
print("F1-score:", f1)

# =========================
# GRAPHS
# =========================

# 1. Class distribution
plt.figure()
df["class"].value_counts().plot(kind="bar")
plt.title("Object Class Distribution")
plt.show()

# 2. Confidence histogram
plt.figure()
df["conf"].hist(bins=20)
plt.title("Confidence Distribution")
plt.xlabel("Confidence")
plt.ylabel("Count")
plt.show()

# 3. Detections per frame
plt.figure()
df.groupby("frame").size().plot()
plt.title("Detections per Frame")
plt.xlabel("Frame")
plt.ylabel("Detections")
plt.show()

# 4. Metrics bar chart
plt.figure()
plt.bar(["Precision","Recall","F1"], [precision, recall, f1])
plt.title("Pseudo Evaluation Metrics")
plt.show()

print("\nSaved:")
print("✔ output.mp4")
print("✔ detections.csv")