#!/usr/bin/env python3
"""
Script to install QR code module on Badger 2040 W
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

def install_qr_module():
    """Install QR code module by running install_qrcode.py"""
    device = find_device()
    if not device:
        print("❌ Device not found")
        return False
    
    try:
        print(f"📦 Installing QR code module on {device}...")
        
        ser = serial.Serial(device, 115200, timeout=10)
        
        # Send Ctrl+C to interrupt
        ser.write(b'\x03')
        time.sleep(0.5)
        
        # Clear input buffer
        ser.reset_input_buffer()
        
        # Send command to run install script
        command = "exec(open('install_qrcode.py').read())\r\n"
        ser.write(command.encode())
        
        print("⏳ Installing QR code module (this may take a while)...")
        time.sleep(5)  # Give time for installation
        
        # Read response
        response = ser.read(1000).decode('utf-8', errors='ignore')
        print(f"Installation output: {response}")
        
        ser.close()
        
        if 'error' in response.lower() or 'failed' in response.lower():
            print("❌ QR module installation may have failed")
            return False
        else:
            print("✅ QR module installation completed")
            return True
        
    except Exception as e:
        print(f"❌ Error installing QR module: {e}")
        return False

if __name__ == '__main__':
    install_qr_module()
