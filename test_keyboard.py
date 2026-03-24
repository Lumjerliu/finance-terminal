#!/usr/bin/env python3
"""
Test keyboard input for Bloomberg Terminal
Run with: python3 test_keyboard.py
"""

import sys
import tty
import termios
import threading
import queue
import time

def test_keyboard():
    """Test that keyboard input works"""
    print("=" * 60)
    print("KEYBOARD INPUT TEST")
    print("=" * 60)
    print("\nThis test will check if keyboard input is working.")
    print("Type some characters and press Enter to see them.")
    print("Press Ctrl+C to exit.\n")
    
    key_queue = queue.Queue()
    running = True
    
    def read_keys():
        nonlocal running
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while running:
                ch = sys.stdin.read(1)
                if ch:
                    key_queue.put(ch)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
    
    # Start keyboard thread
    key_thread = threading.Thread(target=read_keys, daemon=True)
    key_thread.start()
    
    buffer = ""
    print("READY> ", end="", flush=True)
    
    try:
        while running:
            try:
                ch = key_queue.get(timeout=0.1)
                
                if ch == '\x03':  # Ctrl+C
                    print("\n\n[EXIT] Ctrl+C pressed")
                    running = False
                    break
                elif ch == '\r' or ch == '\n':  # Enter
                    print(f"\n[OK] You typed: '{buffer}'")
                    buffer = ""
                    print("READY> ", end="", flush=True)
                elif ch == '\x1b':  # ESC
                    buffer = ""
                    print("\n[CLEAR] Buffer cleared")
                    print("READY> ", end="", flush=True)
                elif ch == '\x7f' or ch == '\x08':  # Backspace
                    buffer = buffer[:-1]
                    print(f"\rREADY> {buffer}_", end="", flush=True)
                elif ch.isprintable():
                    buffer += ch
                    print(f"\rREADY> {buffer}_", end="", flush=True)
            except queue.Empty:
                pass
    except KeyboardInterrupt:
        running = False
    
    print("\n\n[PASS] Keyboard test completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_keyboard()
