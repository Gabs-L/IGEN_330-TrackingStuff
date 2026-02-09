"""
Created on Fri Nov 21 16:51:34 2025

@author: G
"""
#import libraries
import cv2
from ultralytics import YOLO
import serial
import time
import torch

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print("PyTorch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
print("CUDA version:", torch.version.cuda)
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))

model = YOLO('yolo12n.pt')
model.to(device)
model.fuse()              
model.overrides['verbose'] = False

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
time.sleep(1)

xres, yres = 640, 480
outputX, outputY = 90, 90
cx, cy = xres//2, yres//2

while cap.isOpened():
    if not cap.grab():
        break
    ret, frame = cap.retrieve()
    if not ret:
        break
    prevTime = time.time()
    frame = cv2.resize(frame, (xres, yres))
    results = model(frame, classes=[39], verbose=False)
    annotated_frame = frame.copy()
    annotated_frame = results[0].plot()
    bottleFound = False
    
    for r in results:
        boxes = r.boxes
        if boxes is not None:
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                bottleFound = True
                center_x = int((x1 + x2)/2)
                center_y = int((y1 + y2)/2)
                moveX = int(center_x-xres/2)
                moveY = int(center_y-yres/2)
                cv2.circle(annotated_frame, (center_x, center_y), 2, (0, 0, 255), -1)

    cv2.drawMarker(annotated_frame,(cx, cy),color=(0, 255, 0),markerType=cv2.MARKER_CROSS,markerSize=20,thickness=1)
    currTime = time.time()
    fps = 1/(currTime-prevTime)
    prevTime = currTime
    cv2.putText(annotated_frame, f"FPS: {int(fps)}", (10, 20),cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1)
    cv2.imshow('Webcam Detection', annotated_frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()