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

#update loop
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

    # canvas stuff
    def on_motion(event):
        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        canvas.delete("dot")
        dot = canvas.create_oval(x+trackerRad,y+trackerRad,x-trackerRad,y-trackerRad, fill='lime', outline='white', tags="trail")
        trail.append((dot, time.time() * 1000))
    canvas.bind("<Motion>", on_motion)

    def fade_trail():
        current_time = time.time() * 1000
        to_delete = [item[0] for item in trail if current_time - item[1] > FADE_TIME]
        for dot_id in to_delete:
            canvas.delete(dot_id)
            trail[:] = [item for item in trail if item[0] != dot_id]
    
         # Limit total trail length
        while len(trail) > MAX_TRAIL:
            canvas.delete(trail[0][0])
            trail.pop(0)

        canvas.after(refRate, fade_trail)

    tracker.after(refRate, update_display)
    fade_trail()

canvas = Canvas(tracker, bg='black', highlightthickness=0)

canvas.pack(fill=tk.BOTH, expand=True)

# Labels:
screenCentre = tk.Label(tracker, text="Screen Centre: --, --", font=("Arial", 8))
mouseCoord = tk.Label(tracker, text="Mouse: --, --", font=("Arial", 8))
screenSize = tk.Label(tracker, text="Screen Size: --, --", font=("Arial", 8))
distance = tk.Label(tracker, text="Distance: --, --", font=("Arial", 8))

# placing labels manually
screenCentre.place(x=5, y=5)
mouseCoord.place(x=5, y=20)
screenSize.place(x=5, y=35)
distance.place(x=5, y=50)

update_display()
tracker.mainloop()
