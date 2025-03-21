#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Hotkey Launcher for TalkStream

This script listens for a specific hotkey combination and toggles (launches/closes)
the gemini_liveapi.py script in default mode when triggered.
It runs silently in the background and displays toast notifications.

Usage:
    Simply run this script in the background:
    python hotkey_launcher.py

    Press Ctrl+Alt+G to toggle (start/stop) TalkStream.
"""

import os
import sys
import subprocess
import threading
import time
import keyboard
from plyer import notification
import argparse
import psutil
import win32gui
import win32con

# Default hotkey combination (can be customized)
DEFAULT_HOTKEY = "ctrl+alt+g"

# Global variable to track the running process
talkstream_process = None

def show_notification(title, message):
    """
    Display a toast notification with the given title and message.
    
    Args:
        title (str): The notification title
        message (str): The notification message
    """
    try:
        # Force toast notification style on Windows
        notification.notify(
            title=title,
            message=message,
            app_name="TalkStream",
            timeout=5,  # seconds
            toast=True  # Ensure toast notification on Windows
        )
    except Exception as e:
        print(f"Failed to show notification: {e}")

def is_process_running(process):
    """
    Check if a process is still running.
    
    Args:
        process: The process object to check
        
    Returns:
        bool: True if the process is running, False otherwise
    """
    if process is None:
        return False
        
    try:
        return process.poll() is None
    except:
        return False

def terminate_process(process):
    """
    Terminate a process and all its children.
    
    Args:
        process: The process object to terminate
    """
    if process is None:
        return
        
    try:
        # Get the process ID
        pid = process.pid
        
        # Create a psutil process from the pid
        parent = psutil.Process(pid)
        
        # Terminate all child processes
        for child in parent.children(recursive=True):
            try:
                child.terminate()
            except:
                pass
                
        # Terminate the parent process
        parent.terminate()
        
        # Wait for processes to terminate
        gone, still_alive = psutil.wait_procs([parent], timeout=3)
        
        # Force kill any remaining processes
        for p in still_alive:
            try:
                p.kill()
            except:
                pass
    except Exception as e:
        print(f"Error terminating process: {e}")

def launch_gemini_liveapi(mode="screen"):
    """
    Launch the gemini_liveapi.py script in the specified mode silently.
    
    Args:
        mode (str): The video mode to use (camera, screen, or none)
    
    Returns:
        subprocess.Popen: The process object if launched successfully, None otherwise
    """
    global talkstream_process
    
    # If already running, terminate it
    if is_process_running(talkstream_process):
        terminate_process(talkstream_process)
        show_notification(
            "TalkStream Stopped", 
            "TalkStream has been closed"
        )
        talkstream_process = None
        return None
    
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    gemini_script = os.path.join(script_dir, "gemini_liveapi.py")
    
    # Ensure the script exists
    if not os.path.exists(gemini_script):
        print(f"Error: Could not find {gemini_script}")
        show_notification("TalkStream Error", f"Could not find {gemini_script}")
        return None
    
    # Launch the script in a new process
    try:
        # Use Python executable from current environment
        python_exe = sys.executable
        cmd = [python_exe, gemini_script, "--mode", mode]
        
        # Launch silently in the background
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        
        process = subprocess.Popen(
            cmd,
            startupinfo=startupinfo,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        # Show notification
        show_notification(
            "TalkStream Launched", 
            f"TalkStream is now running in {mode} mode"
        )
        
        print(f"Launched TalkStream in {mode} mode (PID: {process.pid})")
        return process
        
    except Exception as e:
        error_msg = f"Failed to launch TalkStream: {e}"
        print(error_msg)
        show_notification("TalkStream Error", error_msg)
        return None

def toggle_talkstream(mode):
    """
    Toggle TalkStream on/off.
    
    Args:
        mode (str): The video mode to use when launching
    """
    global talkstream_process
    
    if is_process_running(talkstream_process):
        # TalkStream is running, stop it
        terminate_process(talkstream_process)
        show_notification(
            "TalkStream Stopped", 
            "TalkStream has been closed"
        )
        talkstream_process = None
    else:
        # TalkStream is not running, start it
        talkstream_process = launch_gemini_liveapi(mode)

def register_hotkey(hotkey, mode):
    """
    Register a hotkey to toggle TalkStream.
    
    Args:
        hotkey (str): The hotkey combination to listen for
        mode (str): The video mode to use when launching
    """
    keyboard.add_hotkey(hotkey, lambda: toggle_talkstream(mode))
    print(f"Listening for hotkey: {hotkey} to toggle TalkStream in {mode} mode")

def hide_console_window():
    """Hide the console window on Windows."""
    try:
        # Get the handle to the console window
        console_window = win32gui.GetForegroundWindow()
        
        # Hide the window
        win32gui.ShowWindow(console_window, win32con.SW_HIDE)
    except Exception as e:
        print(f"Failed to hide console window: {e}")

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="TalkStream Hotkey Launcher")
    parser.add_argument(
        "--hotkey", 
        type=str, 
        default=DEFAULT_HOTKEY,
        help=f"Hotkey combination to toggle TalkStream (default: {DEFAULT_HOTKEY})"
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="screen",
        choices=["camera", "screen", "none"],
        help="Video mode to use when launching TalkStream (default: screen)"
    )
    parser.add_argument(
        "--hide-console",
        action="store_true",
        help="Hide the console window when running"
    )
    
    args = parser.parse_args()
    
    # Hide console window if requested
    if args.hide_console:
        hide_console_window()
    
    # Show startup notification
    show_notification(
        "TalkStream Hotkey Launcher", 
        f"Press {args.hotkey} to toggle TalkStream"
    )
    
    # Register the hotkey
    register_hotkey(args.hotkey, args.mode)
    
    # Keep the script running
    print("TalkStream Hotkey Launcher is running. Press Ctrl+C to exit.")
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting TalkStream Hotkey Launcher...")
        keyboard.unhook_all()
        
        # Ensure TalkStream is terminated when exiting
        if is_process_running(talkstream_process):
            terminate_process(talkstream_process)

if __name__ == "__main__":
    main()
