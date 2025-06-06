#!/usr/bin/env python3
"""
Monitor the Badger 2040 W device output to see badge operation
"""

import serial
import time
import glob

def find_device():
    """Find connected Pico device"""
    patterns = ['/dev/tty.usbmodem*', '/dev/ttyACM*']
    for pattern in patterns:
        devices = glob.glob(pattern)
        if devices:
            return devices[0]
    return None

def monitor_badge():
    """Monitor badge application output"""
    device = find_device()
    if not device:
        print("❌ Device not found")
        return
    
    print(f"🦡 Monitoring Badger 2040 W: {device}")
    print("Press Ctrl+C to stop monitoring")
    print("=" * 50)
    
    try:
        ser = serial.Serial(device, 115200, timeout=1)
        
        while True:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                try:
                    text = data.decode('utf-8', errors='ignore')
                    if text.strip():
                        # Add timestamp
                        timestamp = time.strftime("%H:%M:%S")
                        for line in text.strip().split('\n'):
                            if line.strip():
                                print(f"[{timestamp}] {line}")
                except:
                    pass
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped")
        ser.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    monitor_badge()
