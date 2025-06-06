#!/usr/bin/env python3
"""
Upload single file to Badger 2040 W and run it
"""

import sys
import serial
import time
import glob
import os

def find_device():
    """Find connected Pico device"""
    patterns = ['/dev/tty.usbmodem*', '/dev/ttyACM*', '/dev/ttyUSB*']
    
    for pattern in patterns:
        devices = glob.glob(pattern)
        if devices:
            return devices[0]
    return None

def upload_and_run(filename, run_as_main=True):
    """Upload a file and optionally run it"""
    if not os.path.exists(filename):
        print(f"❌ File not found: {filename}")
        return False
    
    device = find_device()
    if not device:
        print("❌ Device not found")
        return False
    
    print(f"📱 Device: {device}")
    print(f"📤 Uploading: {filename}")
    
    try:
        # Read file content
        with open(filename, 'r') as f:
            content = f.read()
        
        # Connect to device
        ser = serial.Serial(device, 115200, timeout=5)
        time.sleep(0.5)
        
        # Send Ctrl+C to interrupt any running program
        ser.write(b'\x03')
        time.sleep(0.5)
        ser.read_all()  # Clear buffer
        
        # Upload file by pasting content
        print("📤 Uploading file content...")
        
        # Send the file content line by line
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if i % 50 == 0:
                print(f"   Progress: {i}/{len(lines)} lines")
            
            ser.write((line + '\r\n').encode())
            time.sleep(0.02)  # Small delay between lines
        
        if run_as_main:
            print("🚀 Running application...")
            # No need to call main() - the script should run automatically
        
        # Monitor output for a few seconds
        print("📊 Monitoring output...")
        start_time = time.time()
        while time.time() - start_time < 5:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                try:
                    text = data.decode('utf-8', errors='ignore')
                    if text.strip():
                        print(f"📱 Device: {text.strip()}")
                except:
                    pass
            time.sleep(0.1)
        
        ser.close()
        print("✅ Upload complete")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 upload_single.py <filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    upload_and_run(filename)
