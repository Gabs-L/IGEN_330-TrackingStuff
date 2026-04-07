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
from pynput import keyboard

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print("PyTorch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
print("CUDA version:", torch.version.cuda)
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))

#Model setup and frame resolutions
model = YOLO('Model1_200_30_best.pt')
model.to(device)
model.fuse()              
model.overrides['verbose'] = False

#Frame resolutions
xRes = 640 #800, 640, 400, 320, 160
yRes = 480 #600, 480, 300, 240, 120
dispX = 1280
dispY = 960

#Manual mode vars
manualSpeed = 200
manual = False
keysPressed = set()
pumpOn = False
solOpen = False

#cv2 capture settings
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, xRes)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, yRes)
#cap.set(cv2.CAP_PROP_FPS, 60)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

#Frame logic/specs and display
xres, yres = xRes, yRes
cx, cy = xres//2, yres//2
frameNum = 0            
frameSkip = 1       # how many frames for yolo to skip
fontScale = 1       #1
fontThicc = 1       #1
dotScale = 3        #2
serialFrameCount = 0
serialFrames = 2    # limit number of frames sent (how many to skip)
confidence = 0.65


#Serial Stuffs:
SERIAL_PORT = 'COM6' #MAKE SURE MATCHES WITH ARDUINO
BAUD_RATE = 9600 # MAKE SURE MATCHING WITH ARDUINO
try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # wait for Arduino to reset after connection
    print(f"Serial connected on {SERIAL_PORT} at {BAUD_RATE} baud")
except serial.SerialException as e: # Fancy Claude.ai error handling
    print(f"WARNING: Serial not available ({e}). Running without Arduino.")
    arduino = None

# Arduino Stuffs (sends move commands to arduino as a string)
def send_to_arduino(moveX, moveY, solenoid=0, pumpVal=0, mode=1): 
    msg = f"{int(mode)},{int(moveX)},{int(moveY)},{int(solenoid)},{int(pumpVal)}\n"
    print(f"[SEND] {msg.strip()}")
    if arduino and arduino.is_open:
        try:
            arduino.write(msg.encode('utf-8'))
        except serial.SerialException as e:
            print(f"Serial write error: {e}")
#Manual mode stuffs
def on_press(key):
    global manual
    if key == keyboard.Key.space:
        manual = not manual
        print(f"[Mode] {'MANUAL' if manual else 'AUTO'}")
    elif hasattr(key, 'char') and key.char in ('w', 'a', 's', 'd', 'o', 'p'):
        keysPressed.add(key.char)
 
def on_release(key):
    if hasattr(key, 'char') and key.char in ('w', 'a', 's', 'd', 'o', 'p'):
        keysPressed.discard(key.char)
 
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.daemon = True
listener.start()

# Capture Stuffs
for _ in range(5):
    if cap.isOpened():
        break
    time.sleep(0.5)
else:
    print("ERROR: Cannot open camera!")
    exit()
time.sleep(1) 

while cap.isOpened():
    if not cap.grab():
        break
    ret, frame = cap.retrieve()
    if not ret:
        break
    
    prevTime = time.time()
    frame = cv2.resize(frame, (xres, yres))
    results = model(frame, conf=confidence, verbose=False)
    annotated_frame = frame.copy()
    # annotated_frame = results[0].plot()
    tealightFound = False
    moveX, moveY = 0, 0 # default to 0 if nothing found
    if manual:
        # WASD → moveX/moveY
        moveX, moveY = 0, 0
        if 'a' in keysPressed: moveX -= manualSpeed
        if 'd' in keysPressed: moveX += manualSpeed
        if 'w' in keysPressed: moveY -= manualSpeed
        if 's' in keysPressed: moveY += manualSpeed
        if 'o' in keysPressed: 
            solOpen = not solOpen 
            keysPressed.discard('o')
        pumpOn = 'p' in keysPressed
        serialFrameCount += 1
        if serialFrameCount >= serialFrames:
            send_to_arduino(moveX, moveY, int(solOpen), 5 if pumpOn else 0, mode=0)
            serialFrameCount = 0
    else: # Auto
        # CV tracking
        for r in results:
            if r.boxes is not None:
                for box in r.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    tealightFound = True
                    center_x = int((x1 + x2) / 2)
                    center_y = int((y1 + y2) / 2)
                    moveX = int(center_x - xres / 2)
                    moveY = int(center_y - yres / 2)
 
                    cv2.circle(annotated_frame, (center_x, center_y), dotScale, (0, 0, 255), -1)
                    cls_idx = int(box.cls[0])
                    class_name = model.names[cls_idx]
                    conf_val = float(box.conf[0])
                    label = f"{class_name} {conf_val:.0%}"
                    label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_PLAIN, fontScale, fontThicc)
                    tx, ty = center_x + 6, center_y - 6
                    cv2.rectangle(annotated_frame, (tx, ty - label_size[1] - 2), (tx + label_size[0] + 4, ty + 2), (0, 0, 255), -1)
                    cv2.putText(annotated_frame, label, (tx + 2, ty), cv2.FONT_HERSHEY_PLAIN, fontScale, (255, 255, 255), fontThicc)
 
        serialFrameCount += 1
        if serialFrameCount >= serialFrames:
            solenoid = 0
            send_to_arduino(moveX if tealightFound else 0, moveY if tealightFound else 0, 0, 0, mode=1)
            serialFrameCount = 0
 
    # HUD
    fps = 1 / (time.time() - prevTime)
    cv2.drawMarker(annotated_frame, (cx, cy), (0, 255, 0), cv2.MARKER_CROSS, 20, 1)
    cv2.putText(annotated_frame, f"FPS: {int(fps)}",      (10, 20),  cv2.FONT_HERSHEY_PLAIN, fontScale, (0, 255, 0), fontThicc)
    cv2.putText(annotated_frame, f"MoveX: {int(moveX)}",  (10, 40),  cv2.FONT_HERSHEY_PLAIN, fontScale, (0, 255, 0), fontThicc)
    cv2.putText(annotated_frame, f"MoveY: {int(moveY)}",  (10, 60), cv2.FONT_HERSHEY_PLAIN, fontScale, (0, 255, 0), fontThicc)
    mode_label = "MODE: MANUAL" if manual else "MODE: AUTO"
    mode_color = (0, 100, 255) if manual else (0, 255, 0)
    cv2.putText(annotated_frame, mode_label, (10, 80), cv2.FONT_HERSHEY_PLAIN, fontScale, mode_color, fontThicc)
    if manual:
            sol_label = "SOLENOID: ON" if solOpen else "SOLENOID: OFF"
            sol_color = (0, 255, 0) if solOpen else (0, 150, 255)
            cv2.putText(annotated_frame, sol_label, (10, 100), cv2.FONT_HERSHEY_PLAIN, fontScale, sol_color, fontThicc)
            pump_label = "PUMP: ON" if pumpOn else "PUMP: OFF"
            pump_color = (0, 255, 0) if pumpOn else (0, 200, 255)
            cv2.putText(annotated_frame, pump_label, (10, 120), cv2.FONT_HERSHEY_PLAIN, fontScale, pump_color, fontThicc)
    
    display_frame = cv2.resize(annotated_frame, (dispX, dispY))
    cv2.imshow('Webcam Detection', display_frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break
 
cap.release()
cv2.destroyAllWindows()
listener.stop()
if arduino and arduino.is_open:
    arduino.close()
    print("Serial port closed.")