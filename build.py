#!/usr/bin/env python3
"""
Build script to compile main.py into an executable.
Run this script to rebuild the mvl_opener.exe with the latest source code.
"""

import subprocess
import sys
import os
import time

def stop_running_process():
    """Stop any running mvl_opener processes."""
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'mvl_opener.exe':
                print(f"Stopping running process (PID: {proc.info['pid']})...")
                proc.kill()
                time.sleep(1)
    except ImportError:
        print("Note: psutil not available, skipping process check")
    except Exception as e:
        print(f"Warning: Could not stop process: {e}")

def clean_old_exe():
    """Remove old executable."""
    exe_path = 'mvl_opener.exe'
    if os.path.exists(exe_path):
        try:
            os.remove(exe_path)
            print(f"Removed old {exe_path}")
        except Exception as e:
            print(f"Warning: Could not remove old exe: {e}")

def build_exe():
    """Run PyInstaller to build the executable."""
    print("Building mvl_opener.exe...")
    cmd = [
        'pyinstaller',
        'main.spec',
        '--distpath', '.',
        '--workpath', 'build',
        '-y'
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        if result.returncode == 0:
            print("\nBuild completed successfully!")
            print(f"Executable: {os.path.abspath('mvl_opener.exe')}")
            return True
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error code {e.returncode}")
        return False
    except Exception as e:
        print(f"\nBuild error: {e}")
        return False

def main():
    print("=" * 60)
    print("MVL Opener - Build Script")
    print("=" * 60)
    
    # Stop any running processes
    stop_running_process()
    
    # Clean old exe
    clean_old_exe()
    
    # Build
    success = build_exe()
    
    print("=" * 60)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
