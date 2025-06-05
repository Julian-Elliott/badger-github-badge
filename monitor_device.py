#!/usr/bin/env python3
"""
Simple diagnostic script to check current device status
"""

import time
import serial
import glob

def find_device():
    """Find the Pico device"""
    patterns = ['/dev/tty.usbmodem*', '/dev/ttyACM*']
    for pattern in patterns:
        devices = glob.glob(pattern)
        if devices:
            return devices[0]
    return None

def monitor_device():
    """Monitor device output for debugging"""
    device = find_device()
    if not device:
        print("❌ No device found")
        return
    
    print(f"📱 Monitoring device: {device}")
    print("Press Ctrl+C to stop monitoring")
    
    try:
        ser = serial.Serial(device, 115200, timeout=1)
        
        # Send interrupt to see current status
        ser.write(b'\x03\r\n')
        time.sleep(0.5)
        
        # Send a simple status check
        ser.write(b'print("Device Status Check")\r\n')
        ser.write(b'import network\r\n')
        ser.write(b'sta = network.WLAN(network.STA_IF)\r\n')
        ser.write(b'print("WiFi connected:", sta.isconnected())\r\n')
        ser.write(b'print("Current time:", time.time())\r\n')
        
        # Monitor output
        start_time = time.time()
        while time.time() - start_time < 10:
            data = ser.read(ser.in_waiting or 1)
            if data:
                try:
                    text = data.decode('utf-8', errors='ignore')
                    print(text, end='')
                except:
                    pass
            time.sleep(0.1)
        
        ser.close()
        
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    monitor_device()
