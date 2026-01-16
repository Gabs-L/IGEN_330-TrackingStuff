import mouse
import pyautogui
import pynput
import time
import keyboard
import os
import math
import sys
import tkinter
from colorama import init

init()
refRate = 0.1
lastTime = time.perf_counter()
print("tracking started, esc to stop")

while True:
    if keyboard.is_pressed('esc'):
        break
    if time.perf_counter() - lastTime >= refRate:
        activeWin = pyautogui.getActiveWindow()
        activeWinCenter = (activeWin.left+activeWin.width/2,activeWin.top+activeWin.height/2)
        dist = math.dist(activeWinCenter, pyautogui.position())
        globalCoord = pyautogui.position()
        rel_x = globalCoord.x - activeWin.left
        rel_y = globalCoord.y - activeWin.top

        print(f"active window: \"{activeWin.title}\"")
        print(f"window size: X={activeWin.width}, Y={activeWin.height}")
        print(f"window centre: {activeWinCenter}, ({activeWin.width/2}, {activeWin.height/2})")
        print(f"coords X={rel_x}, Y={rel_y}")
        print(f"dist.: {dist:.3f}\033[5A]")
        lastTime = time.perf_counter()
