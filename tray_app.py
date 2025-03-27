#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TalkStream Tray Application

This script creates a system tray icon for TalkStream that:
1. Changes color based on whether incoming audio is playing
2. Allows selecting between sharing the whole screen or specific windows
3. Provides easy access to start/stop TalkStream

Usage:
    python tray_app.py
"""

import os
import sys
import subprocess
import threading
import time
import queue
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import win32gui
import psutil
import json
import pyaudio
import keyboard
import win32con


# Constants
ICON_SIZE = (64, 64)
INACTIVE_COLOR = (100, 100, 100)  # Gray when inactive
ACTIVE_COLOR = (0, 200, 0)  # Green when audio is playing
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_HOTKEY = "ctrl+alt+g"  # Default hotkey combination
VOICE_HOTKEY = "ctrl+alt+v"  # Voice-only mode hotkey


# Global variables
talkstream_process = None
audio_active = False
audio_status_queue = queue.Queue()
selected_window = None
window_list = []
tray_icon = None


def create_icon(color):
    """Create a circular icon with the specified color"""
    img = Image.new('RGBA', ICON_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a filled circle
    draw.ellipse((4, 4, ICON_SIZE[0]-4, ICON_SIZE[1]-4), fill=color)
    
    # Add a white border
    draw.ellipse(
        (4, 4, ICON_SIZE[0]-4, ICON_SIZE[1]-4), 
        outline=(255, 255, 255), 
        width=2
    )
    
    return img


def get_window_list():
    """Get a list of all visible windows"""
    global window_list
    window_list = []
    
    def enum_windows_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            # Get window title
            title = win32gui.GetWindowText(hwnd)
            # Skip windows with empty titles or system windows
            if title and title != "Program Manager":
                window_list.append((hwnd, title))
        return True
    
    win32gui.EnumWindows(enum_windows_callback, None)
    return window_list


def get_window_menu_items():
    """Create menu items for each window"""
    windows = get_window_list()
    menu_items = []
    
    for hwnd, title in windows:
        # Truncate long titles
        display_title = title[:40] + "..." if len(title) > 40 else title
        menu_items.append(
            item(display_title, lambda _, hwnd=hwnd: select_window(hwnd))
        )
    
    return menu_items


def select_window(hwnd):
    """Select a specific window for sharing"""
    global selected_window
    selected_window = hwnd
    
    # If TalkStream is running, restart it with the new window
    if is_process_running(talkstream_process):
        stop_talkstream()
        start_talkstream(mode="window")


def create_window_config(hwnd=None):
    """Create a window config file for screen sharing"""
    config = {}
    
    if hwnd is None:
        # Full screen config
        config["type"] = "fullscreen"
    else:
        # Specific window config
        config["type"] = "window"
        config["hwnd"] = hwnd
        config["title"] = win32gui.GetWindowText(hwnd)
    
    # Write config to temporary file
    config_path = os.path.join(SCRIPT_DIR, "window_config.json")
    with open(config_path, "w") as f:
        json.dump(config, f)
    
    return config_path


def is_process_running(process):
    """Check if a process is still running"""
    if process is None:
        return False
    
    try:
        return process.poll() is None
    except Exception:
        return False


def terminate_process(process):
    """Terminate a process and all its children"""
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
            except Exception:
                pass
        
        # Terminate the parent process
        parent.terminate()
        
        # Wait for processes to terminate
        gone, still_alive = psutil.wait_procs([parent], timeout=3)
        
        # Force kill any remaining processes
        for p in still_alive:
            try:
                p.kill()
            except Exception:
                pass
    except Exception as e:
        print(f"Error terminating process: {e}")


def start_talkstream(mode="screen"):
    """Start TalkStream with the specified mode"""
    global talkstream_process
    
    # Get the path to the gemini_liveapi.py script
    gemini_script = os.path.join(SCRIPT_DIR, "gemini_liveapi.py")
    
    # Ensure the script exists
    if not os.path.exists(gemini_script):
        print(f"Error: Could not find {gemini_script}")
        return None
    
    # Create window config if needed
    if mode == "window" and selected_window is not None:
        create_window_config(selected_window)
    elif mode == "screen":
        create_window_config(None)
    elif mode == "none":
        # Create a dummy config for audio-only mode
        config_path = os.path.join(SCRIPT_DIR, "window_config.json")
        with open(config_path, "w") as f:
            json.dump({"type": "none"}, f)
    
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
        
        print(f"Launched TalkStream in {mode} mode (PID: {process.pid})")
        return process
    
    except Exception as e:
        print(f"Failed to launch TalkStream: {e}")
        return None


def stop_talkstream():
    """Stop TalkStream if it's running"""
    global talkstream_process
    
    if is_process_running(talkstream_process):
        terminate_process(talkstream_process)
        talkstream_process = None


def toggle_talkstream(mode="screen"):
    """Toggle TalkStream on/off with the specified mode"""
    global talkstream_process
    
    if is_process_running(talkstream_process):
        stop_talkstream()
    else:
        talkstream_process = start_talkstream(mode)


def monitor_audio_activity():
    """Monitor the audio activity of TalkStream"""
    global audio_active, tray_icon
    
    while True:
        try:
            # Check if there's a new audio status in the queue
            try:
                audio_active = audio_status_queue.get(block=False)
            except queue.Empty:
                pass
            
            # Update the icon if TalkStream is running
            if is_process_running(talkstream_process) and tray_icon:
                if audio_active:
                    tray_icon.icon = create_icon(ACTIVE_COLOR)
                else:
                    tray_icon.icon = create_icon(INACTIVE_COLOR)
            
            time.sleep(0.1)
        except Exception as e:
            print(f"Error in audio monitoring: {e}")
            time.sleep(1)


def patch_audio_play():
    """
    Patch the play_audio method in gemini_liveapi.py to detect audio activity
    This is done by creating a proxy class that will be used in place of the original
    """
    global audio_status_queue
    
    # Create a proxy class for PyAudio.Stream
    original_open = pyaudio.PyAudio.open
    
    def patched_open(self, *args, **kwargs):
        # Call the original open method
        stream = original_open(self, *args, **kwargs)
        
        # If this is an output stream, patch its write method
        if kwargs.get('output', False):
            original_write = stream.write
            
            def patched_write(data, *args, **kwargs):
                # Signal that audio is active
                audio_status_queue.put(True)
                
                # Schedule a task to set audio inactive after a short delay
                def reset_audio_status():
                    time.sleep(0.2)  # Short delay to prevent flickering
                    audio_status_queue.put(False)
                
                threading.Thread(target=reset_audio_status).start()
                
                # Call the original write method
                return original_write(data, *args, **kwargs)
            
            # Replace the write method
            stream.write = patched_write
        
        return stream
    
    # Replace the open method
    pyaudio.PyAudio.open = patched_open


def register_hotkey(hotkey, mode):
    """
    Register a hotkey to toggle TalkStream.
    
    Args:
        hotkey (str): The hotkey combination to register
        mode (str): The video mode to use when launching
    """
    def hotkey_callback():
        toggle_talkstream(mode)
    
    try:
        keyboard.add_hotkey(hotkey, hotkey_callback)
        print(f"Registered hotkey: {hotkey} for {mode} mode")
    except Exception as e:
        print(f"Failed to register hotkey: {e}")


def hide_console_window():
    """Hide the console window on Windows."""
    try:
        # Get the handle to the console window
        console_window = win32gui.GetForegroundWindow()
        
        # Hide the window
        win32gui.ShowWindow(console_window, win32con.SW_HIDE)
    except Exception as e:
        print(f"Failed to hide console window: {e}")


def create_menu():
    """Create the tray icon menu"""
    # Window selection submenu
    window_menu = item("Select Window", pystray.Menu(*get_window_menu_items()))
    
    # Main menu
    menu = pystray.Menu(
        item("Start (Full Screen)", lambda: toggle_talkstream("screen")),
        item("Start (Selected Window)", lambda: toggle_talkstream("window")),
        item("Start (Audio Only)", lambda: toggle_talkstream("none")),
        window_menu,
        item("Refresh Window List", lambda: get_window_list()),
        item("Stop TalkStream", stop_talkstream),
        item("Exit", lambda: tray_icon.stop())
    )
    
    return menu


def setup_tray_icon():
    """Set up the system tray icon"""
    global tray_icon
    
    # Create the initial icon (inactive)
    icon = create_icon(INACTIVE_COLOR)
    
    # Create the tray icon
    tray_icon = pystray.Icon(
        "TalkStream", 
        icon, 
        "TalkStream", 
        menu=create_menu()
    )
    
    # Start the icon
    tray_icon.run()


def main():
    """Main entry point"""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="TalkStream Tray Application")
    parser.add_argument("--hotkey", type=str, default=DEFAULT_HOTKEY, 
                      help=f"Hotkey combination to use (default: {DEFAULT_HOTKEY})")
    parser.add_argument("--mode", type=str, default="screen", 
                      choices=["camera", "screen", "window", "none"],
                      help="Default video mode to use with hotkey (default: screen)")
    parser.add_argument("--disable-voice-hotkey", action="store_true",
                      help="Disable the dedicated voice-only hotkey (Ctrl+Alt+V)")
    args = parser.parse_args()
    
    # Hide console window
    hide_console_window()
    
    # Register main hotkey
    register_hotkey(args.hotkey, args.mode)
    print(f"Press {args.hotkey} to toggle TalkStream in {args.mode} mode")
    
    # Register voice-only hotkey unless disabled
    if not args.disable_voice_hotkey:
        register_hotkey(VOICE_HOTKEY, "none")
        print(f"Press {VOICE_HOTKEY} to toggle TalkStream in voice-only mode")
    
    # Patch the audio play method to detect audio activity
    patch_audio_play()
    
    # Start the audio monitoring thread
    audio_thread = threading.Thread(target=monitor_audio_activity, daemon=True)
    audio_thread.start()
    
    # Set up the tray icon (this will block until the icon is stopped)
    setup_tray_icon()
    
    # Clean up when exiting
    stop_talkstream()
    keyboard.unhook_all()


if __name__ == "__main__":
    main()
