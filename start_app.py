#!/usr/bin/env python3
"""
College Buddy Application Launcher
Starts both backend and frontend with a single command
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def main():
    print("=" * 50)
    print("  College Buddy - Starting Application")
    print("=" * 50)
    print()
    
    # Get the script directory
    script_dir = Path(__file__).parent.absolute()
    
    # Start backend server
    print("[1/2] Starting Backend Server...")
    print("Opening backend in new window...")
    
    if sys.platform == "win32":
        # Windows
        backend_cmd = f'start "College Buddy - Backend" cmd /k "cd /d {script_dir} && python main.py"'
        subprocess.run(backend_cmd, shell=True)
    else:
        # Linux/Mac
        backend_cmd = ["python3", "main.py"]
        subprocess.Popen(backend_cmd, cwd=script_dir)
    
    # Wait a bit for backend to start
    print("Waiting for backend to initialize...")
    time.sleep(3)
    
    # Open frontend in browser
    print()
    print("[2/2] Starting Frontend...")
    print("Opening frontend in default browser...")
    
    frontend_path = script_dir / "static" / "index.html"
    webbrowser.open(f"file:///{frontend_path}")
    
    print()
    print("=" * 50)
    print("  Application Started Successfully!")
    print("=" * 50)
    print()
    print("Backend: Running on http://localhost:8001")
    print("Frontend: Opened in your default browser")
    print()
    print("To stop the backend:")
    print("  - Windows: Close the backend command window")
    print("  - Linux/Mac: Press Ctrl+C in the terminal")
    print()

if __name__ == "__main__":
    main()
