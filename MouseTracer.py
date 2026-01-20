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
trackerRad = 3 # tracker radius
trail = [] # trail storage
MAX_TRAIL = 50  # max dots before clearing
FADE_TIME = 2000  # fade time in ms
lastTime = time.perf_counter()

# tkinter window init
tracker = tk.Tk()
tracker.title("Mouse Tracker 3000")
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
    dot = canvas.create_oval(x-trackerRad, y-trackerRad, x+trackerRad, y+trackerRad, outline = '', fill='red', tags="trail")
    trail.append((dot, time.perf_counter()))

canvas.bind("<Motion>", on_motion)

def fade_trail():
    current_time = time.perf_counter()
    trail[:] = [(dot_id, ts) for dot_id, ts in trail if current_time - ts < FADE_TIME]
    while len(trail) > MAX_TRAIL:
        canvas.delete(trail.pop(0)[0])
    canvas.after(refRate, fade_trail)

fade_trail()

# Labels:
screenCentre = tk.Label(tracker, text="Screen Centre: --, --", font=("Arial", 8))
mouseCoord = tk.Label(tracker, text="Mouse: --, --", font=("Arial", 8))
screenSize = tk.Label(tracker, text="Screen Size: --, --", font=("Arial", 8))
distance = tk.Label(tracker, text="Distance: --, --", font=("Arial", 8))

# placing labels manually
screenCentre.place(x=5, y=5)
mouseCoord.place(x=5, y=30)
screenSize.place(x=5, y=55)
distance.place(x=5, y=80)

def update_display():
    x, y = pyautogui.position()
    activeWin = pyautogui.getActiveWindow()
    xWin = activeWin.left + (activeWin.width // 2)
    yWin = activeWin.top + (activeWin.height // 2)
    mouseDist = math.dist((x, y),(xWin, yWin))

    screenCentre.config(text=f"Screen Center: X: {xWin}, Y: {yWin}", anchor="nw")
    mouseCoord.config(text=f"Mouse Coord: X: {x}, Y: {y}", anchor="nw")
    screenSize.config(text=f"Screen Size: W: {activeWin.width}, H: {activeWin.height}", anchor="nw")
    distance.config(text=f"Dist. from center: {mouseDist:.4f}", anchor="nw")

    canvas_width  = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    xWin = canvas_width // 2
    yWin = canvas_height // 2

    canvas.delete("centreDot")
    centreDot = canvas.create_oval(xWin-trackerRad, yWin-trackerRad-15, xWin+trackerRad, yWin+trackerRad-15, outline = '', fill='lime', tags="centreDot")
    tracker.after(refRate, update_display)
   

update_display()
tracker.mainloop()
