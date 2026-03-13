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

#Serial Stuffs:
SERIAL_PORT = 'COM3'
BAUD_RATE = 9600 # MAKE SURE MATCHING WITH ARDUINO
try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # wait for Arduino to reset after connection
    print(f"Serial connected on {SERIAL_PORT} at {BAUD_RATE} baud")
except serial.SerialException as e: # Fancy Claude.ai error handling
    print(f"WARNING: Serial not available ({e}). Running without Arduino.")
    arduino = None

def send_to_arduino(arduino, moveX, moveY): # Sends move commands to arduino as a string
    if arduino and arduino.is_open:
        try:
            msg = f"{moveX},{moveY}\n"
            arduino.write(msg.encode('utf-8'))
        except serial.SerialException as e:
            print(f"Serial write error: {e}")

# Capture Stuffs
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

for _ in range(5):
    if cap.isOpened():
        break
    time.sleep(0.5)
else:
    print("ERROR: Cannot open camera!")
    exit()
time.sleep(1)

xres, yres = 1200, 900 # can also be set to higher (320, 240 / 640, 480 / 1200, 900), 
# outputX, outputY = 90, 90
cx, cy = xres//2, yres//2
frameNum = 0
frameSkip = 0
fontScale = 1.5     #1
fontThicc = 2       #1
dotScale = 3        #2
serialFrames = 3 # limit number of frames sent
serialFrameCount = 0


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
    # annotated_frame = results[0].plot()
    bottleFound = False
    moveX, moveY = 0, 0 # default to 0 if nothing found
    
    if frameNum >= frameSkip:
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

                    cv2.circle(annotated_frame, (center_x, center_y), dotScale, (0, 0, 255), -1)
                    conf_val = float(box.conf[0])
                    label = f"{conf_val:.0%}"
                    offset_x, offset_y = 6, -6  # offset tag up and to the right of the ID dot
                    label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_PLAIN, fontScale, fontThicc)
                    tag_x = center_x + offset_x
                    tag_y = center_y + offset_y
                    cv2.rectangle(annotated_frame,(tag_x, tag_y - label_size[1] - 2), (tag_x + label_size[0] + 4, tag_y + 2), (0, 0, 255), -1)
                    cv2.putText(annotated_frame, label, (tag_x + 2, tag_y), cv2.FONT_HERSHEY_PLAIN, fontScale, (255, 255, 255), fontThicc)

        # Sending Stuffs to Arduino
        serialFrameCount += 1
        if serialFrameCount >= serialFrames:
            send_to_arduino(arduino, moveX if bottleFound else 0, moveY if bottleFound else 0)
            serialFrameCount = 0

        cv2.drawMarker(annotated_frame, (cx, cy), color=(0, 255, 0), markerType = cv2.MARKER_CROSS, markerSize = 20, thickness = 1)
        currTime = time.time()
        fps = 1/(currTime-prevTime)
        cv2.putText(annotated_frame, f"FPS: {int(fps)}", (10, 20),cv2.FONT_HERSHEY_PLAIN, fontScale, (0, 255, 0), fontThicc)
        cv2.putText(annotated_frame, f"MoveX: {int(moveX)}", (10, 40),cv2.FONT_HERSHEY_PLAIN, fontScale, (0, 0, 0), fontThicc)
        cv2.putText(annotated_frame, f"MoveY: {int(moveY)}", (200, 40),cv2.FONT_HERSHEY_PLAIN, fontScale, (0, 0, 0), fontThicc)
        cv2.imshow('Webcam Detection', annotated_frame)
        frameNum = 0
    else:
        cv2.imshow('Webcam Detection', frame) #delete if you prefer low FPS (no spazzing)
        frameNum += 1

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

if arduino and arduino.is_open:
    arduino.close()
    print("Serial port closed.")