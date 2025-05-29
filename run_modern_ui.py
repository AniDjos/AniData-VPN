#!/usr/bin/env python3

import os
import sys
import subprocess

def ensure_venv():
    """Ensure we're running in the virtual environment"""
    # Get the project root directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check for possible virtual environment paths
    venv_paths = [
        '/home/anicet/vpn-venv/bin/python3',  # Original path
        os.path.join(current_dir, 'venv_pyside6', 'bin', 'python'),  # PySide6 venv
        os.path.join(current_dir, 'venv', 'bin', 'python')  # Default venv name
    ]
    
    # Find first existing venv
    venv_python = None
    for path in venv_paths:
        if os.path.exists(path):
            venv_python = path
            break
    
    if not venv_python:
        print("Virtual environment not found. Please run setup.sh or migrate_to_pyside6.sh first.")
        sys.exit(1)
    
    # If we're not running in the venv, restart script with venv python
    if sys.executable != venv_python:
        os.execv(venv_python, [venv_python] + sys.argv)

# Ensure we're running in the virtual environment
ensure_venv()

# Add the project root directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Check if PySide6 is installed
try:
    import PySide6
except ImportError:
    print("ERROR: PySide6 is required. Install with:")
    print("pip install PySide6")
    print("\nOR use the provided script:")
    print("./migrate_to_pyside6.sh")
    print("\nOR run with the launcher:")
    print("./run_with_pyside6.sh")
    sys.exit(1)

from ui.desktop.modern_bridge import run_modern_ui

if __name__ == '__main__':
    run_modern_ui()