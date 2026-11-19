#!/usr/bin/env python3
"""
Controller - Native CoreGraphics Mouse & Window Controller for macOS
Provides pixel-accurate mouse movement, left click, scroll wheel events,
screen capture, and Chrome window focus without third-party dependencies.
"""

import ctypes
import time
import subprocess
import os
import sys

CG = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics')

class CGPoint(ctypes.Structure):
    _fields_ = [('x', ctypes.c_double), ('y', ctypes.c_double)]

CG.CGEventCreateMouseEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint32, CGPoint, ctypes.c_uint32]
CG.CGEventCreateMouseEvent.restype = ctypes.c_void_p

CG.CGEventCreateScrollWheelEvent2.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int32]
CG.CGEventCreateScrollWheelEvent2.restype = ctypes.c_void_p

CG.CGEventPost.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
CG.CGEventPost.restype = None

def activate_chrome():
    """Activate Google Chrome and raise the front window."""
    subprocess.run(['osascript', '-e', '''
        tell application "Google Chrome"
            activate
        end tell
    '''], check=False)
    time.sleep(0.2)

def move(x: float, y: float):
    """Move mouse pointer to global screen coordinates (x, y)."""
    pt = CGPoint(x, y)
    move_ev = CG.CGEventCreateMouseEvent(None, 5, pt, 0)
    CG.CGEventPost(0, move_ev)

def click(x: float, y: float):
    """Perform a mouse click at global screen coordinates (x, y)."""
    activate_chrome()
    move(x, y)
    pt = CGPoint(x, y)
    down = CG.CGEventCreateMouseEvent(None, 1, pt, 0)
    up = CG.CGEventCreateMouseEvent(None, 2, pt, 0)
    CG.CGEventPost(0, down)
    time.sleep(0.05)
    CG.CGEventPost(0, up)
    time.sleep(0.3)

def scroll_down(clicks: int = 5, x: float = 500, y: float = 500):
    """Send scroll wheel down events at (x, y)."""
    activate_chrome()
    move(x, y)
    time.sleep(0.1)
    event = CG.CGEventCreateScrollWheelEvent2(None, 0, 1, -clicks)
    CG.CGEventPost(0, event)
    time.sleep(0.5)

def scroll_up(clicks: int = 5, x: float = 500, y: float = 500):
    """Send scroll wheel up events at (x, y)."""
    activate_chrome()
    move(x, y)
    time.sleep(0.1)
    event = CG.CGEventCreateScrollWheelEvent2(None, 0, 1, clicks)
    CG.CGEventPost(0, event)
    time.sleep(0.5)

def capture(output_path: str = "/tmp/chrome_capture.png") -> str:
    """Capture screen bounds using macOS screencapture utility."""
    subprocess.run(['screencapture', '-x', output_path], check=True)
    return output_path

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: controller.py [click x y | scroll_down n [x y] | scroll_up n [x y] | capture [path]]")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == 'click':
        click(float(sys.argv[2]), float(sys.argv[3]))
    elif cmd == 'scroll_down':
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        x = float(sys.argv[3]) if len(sys.argv) > 4 else 500
        y = float(sys.argv[4]) if len(sys.argv) > 4 else 500
        scroll_down(n, x, y)
    elif cmd == 'scroll_up':
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        x = float(sys.argv[3]) if len(sys.argv) > 4 else 500
        y = float(sys.argv[4]) if len(sys.argv) > 4 else 500
        scroll_up(n, x, y)
    elif cmd == 'capture':
        path = sys.argv[2] if len(sys.argv) > 2 else "/tmp/chrome_capture.png"
        capture(path)
