import mouse
import pyautogui
import pynput
import time
import keyboard
import os
import math
import sys
import tkinter
import tkinter as tk
from tkinter import Canvas
from threading import Thread
from colorama import init

init()  # colorama
refRate = 0.001
trackerRad = 5
lastTime = time.perf_counter()

# Create Tkinter window (non-blocking setup)
tracker = tk.Tk()
tracker.title("Mouse Tracker 1000")
canvas = Canvas(tracker, width=800, height=800, bg="black")
canvas.pack()

def tracking_loop():
    global lastTime
    print("tracking started, esc to stop")
    
    while not stop_tracking:
        if keyboard.is_pressed('esc'):
            tracker.destroy()
            break
            
        if time.perf_counter() - lastTime >= refRate:
            try:
                activeWin = pyautogui.getActiveWindow()
                activeWinCenter = (activeWin.left + activeWin.width/2, activeWin.top + activeWin.height/2)
                globalCoord = pyautogui.position()
                rel_x = globalCoord.x - activeWin.left
                rel_y = globalCoord.y - activeWin.top
                
                # Terminal prints (background)
                print(f"active window: \"{activeWin.title}\"")
                print(f"window size: X={activeWin.width}, Y={activeWin.height}")
                print(f"window centre: {activeWinCenter}")
                print(f"coords X={rel_x:.1f}, Y={rel_y:.1f}")
                print(f"\033[5A")  # Clear 4 lines
                
                # Draw on canvas (accessible from any thread)
                # canvas.delete("all")
                canvas.create_oval(rel_x-trackerRad, rel_y-trackerRad, rel_x+trackerRad, rel_y+trackerRad, fill="red", outline="", tags="mouse")
                canvas.create_oval(activeWinCenter[0]-trackerRad, activeWinCenter[1]-trackerRad,activeWinCenter[0]+trackerRad, activeWinCenter[1]+trackerRad, fill="blue", outline="", tags="center")  # Window center
                canvas.update()
                
                lastTime = time.perf_counter()
            except:
                pass  # Handle no active window

# Global flag for clean exit
stop_tracking = False

# Start tracking in background thread
tracker_thread = Thread(target=tracking_loop, daemon=True)
tracker_thread.start()

# Run Tkinter mainloop (foreground, shows window)
tracker.mainloop()
