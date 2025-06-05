#!/usr/bin/env python3
"""
Simple script to run the main application on Badger 2040 W
"""

import serial
import time
import glob
from typing import Optional

def find_device() -> Optional[str]:
    """Find the Pico device"""
    patterns = ['/dev/tty.usbmodem*', '/dev/ttyACM*', '/dev/ttyUSB*']
    
    for pattern in patterns:
        devices = glob.glob(pattern)
        if devices:
            return devices[0]
    return None

def run_main():
    """Run the main application"""
    device = find_device()
    if not device:
        print("❌ Device not found")
        return False
    
    try:
        print(f"🚀 Running main application on {device}...")
        
        ser = serial.Serial(device, 115200, timeout=3)
        
        # Send Ctrl+C to interrupt
        ser.write(b'\x03')
        time.sleep(0.5)
        
        # Send import command
        ser.write(b'import main\r\n')
        time.sleep(1)
        
        # Read response
        response = ser.read(200).decode('utf-8', errors='ignore')
        print(f"Response: {response}")
        
        ser.close()
        print("✅ Application started")
        return True
        
    except Exception as e:
        print(f"❌ Error running application: {e}")
        return False

if __name__ == '__main__':
    run_main()
