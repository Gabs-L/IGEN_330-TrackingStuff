"""
Created on Fri Nov 21 16:51:34 2025

@author: G
"""
#import libraries
import cv2
from ultralytics import YOLO
import serial
import time

#Load model from root directory
model = YOLO('yolo12n.pt')

#Arduino stuff
serialPort = "COM3"
arduino = serial.Serial(port=serialPort, baudrate=115200, timeout=1)
time.sleep(2)  # wait for Arduino to reset

#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) #Windows only really, change for when using SBC
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
time.sleep(5)

#Capture quality
xres = 640
yres = 480
 
outputX = 90
outputY = 0

#Start feed capture
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.resize(frame, (xres, yres))
    
    #Run the detection model on the frame *** ONLY DETECT BOTTLE ***
    results = model(frame, classes=[39], verbose=False)
    
    #Work on the original frame (not the annotated one)
    annotated_frame = frame.copy()
    
    #Get YOLO's annotated frame FIRST (boxes + confidence labels)
    annotated_frame = results[0].plot()
    cx, cy = xres // 2, yres // 2
    cv2.drawMarker(annotated_frame,(cx, cy),color=(0, 255, 0),markerType=cv2.MARKER_CROSS,markerSize=20,thickness=2)
    bottleFound = False
   
    #Loop through detections
    for r in results:
       boxes = r.boxes
       if boxes is not None:
           for box in boxes:
               #Get bounding box coordinates (x1, y1, x2, y2)
               x1, y1, x2, y2 = box.xyxy[0].tolist()
               bottleFound = True
               
               #Calculate center point
               center_x = int((x1 + x2) / 2)
               center_y = int((y1 + y2) / 2)
               
               #Draw red dot (circle) at center
               cv2.circle(annotated_frame, (center_x, center_y), 5, (0, 0, 255), -1)
               
               #Centering Code:
               moveX = int(center_x-xres/2)
               moveY = int(center_y-yres/2)
               #print(f"MOVE X: {moveX} px")
               #print(f"MOVE Y: {moveY} px")

               if moveX > 0:
                   outputX = 91
                   print(f"moving RIGHT: {outputX}     ", end="\r")
                   arduino.write(f"{outputX}\n".encode()) 
               else: 
                   outputX = 89
                   print(f"moving LEFT: {outputX}     ", end="\r")
                   arduino.write(f"{outputX}\n".encode())
               
               #Print coordinates to terminal
               #print(f"Bottle center: ({center_x}, {center_y})")

    if not bottleFound:
        outputX = 90
        arduino.write(f"{outputX}\n".encode())

    #Display the image
    cv2.imshow('YOLOv12 Webcam Detection', annotated_frame)
    #End capture if "esc" is pressed
    if cv2.waitKey(1) & 0xFF == 27:
        break
#Release the feed capture and close respective windows    
cap.release()
cv2.destroyAllWindows()