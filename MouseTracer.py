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
refRate = 10
trackerRad = 5
lastTime = time.perf_counter()

# tkinter window init
tracker = tk.Tk()
tracker.title("Mouse Tracker 1000")
tracker.attributes("-topmost", True)
tracker.attributes("-alpha",0.75)
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
    canvas.delete("dot")  # Only delete dot, not labels
    canvas.create_oval(x-5, y-5, x+5, y+5, fill='lime', outline='white', tags="dot")

    tracker.after(refRate, update_display)

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
