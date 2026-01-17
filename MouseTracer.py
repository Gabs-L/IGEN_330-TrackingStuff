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
refRate = 10 # refresh rate in ms
trackerRad = 5 # tracker radius
trail = [] # trail storage
MAX_TRAIL = 50  # max dots before clearing
FADE_TIME = 2000  # fade time in ms
lastTime = time.perf_counter()

# tkinter window init
tracker = tk.Tk()
tracker.title("Mouse Tracker 1000")
tracker.attributes("-topmost", True)
tracker.attributes("-alpha",0.8)
tracker.geometry("800x800")
tracker.resizable(True, True)
tracker.configure(bg='black')

canvas = Canvas(tracker, bg='black', highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True)

# BIND ONCE - BEFORE labels
def on_motion(event):
    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)
    dot = canvas.create_oval(x+trackerRad, y+trackerRad, x-trackerRad, y-trackerRad, 
                            fill='lime', outline='white', tags="trail")
    trail.append((dot, time.time() * 1000))

canvas.bind("<Motion>", on_motion)

def fade_trail():
    current_time = time.time() * 1000
    trail[:] = [(dot_id, ts) for dot_id, ts in trail if current_time - ts < FADE_TIME]
    while len(trail) > MAX_TRAIL:
        canvas.delete(trail.pop(0)[0])
    canvas.after(100, fade_trail)

fade_trail()

# Labels AFTER canvas setup
screenCentre = tk.Label(tracker, text="...", font=("Arial", 8))
# ... place labels ...

# SIMPLIFIED update_display - NO canvas code!
def update_display():
    x, y = pyautogui.position()
    activeWin = pyautogui.getActiveWindow()
    # ... update labels only ...
    tracker.after(100, update_display)  # 100ms not 10ms

update_display()
tracker.mainloop()