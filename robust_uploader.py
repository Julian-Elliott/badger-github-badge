#!/usr/bin/env python3
"""
Robust file uploader for Badger 2040 W with better error handling
"""

import serial
import time
import sys
import os
import glob
from typing import Optional, List

def find_pico_device() -> Optional[str]:
    """Find connected Pico device"""
    patterns = [
        '/dev/tty.usbmodem*',
        '/dev/ttyACM*',
        '/dev/ttyUSB*'
    ]
    
    for pattern in patterns:
        devices = glob.glob(pattern)
        if devices:
            return devices[0]
    return None

def wait_for_device(timeout: int = 10) -> Optional[str]:
    """Wait for device to become available"""
    print(f"⏳ Waiting for device (timeout: {timeout}s)...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        device = find_pico_device()
        if device:
            print(f"✅ Found device: {device}")
            return device
        time.sleep(1)
    
    print("❌ Device not found")
    return None

def reset_device_connection(device_path: str) -> bool:
    """Reset device connection by toggling DTR/RTS"""
    try:
        print(f"🔄 Resetting connection to {device_path}...")
        
        # Open and immediately close with DTR/RTS manipulation
        ser = serial.Serial(
            device_path,
            115200,
            timeout=1,
            write_timeout=1
        )
        
        # Toggle DTR and RTS
        ser.dtr = False
        ser.rts = False
        time.sleep(0.1)
        ser.dtr = True
        ser.rts = True
        time.sleep(0.1)
        ser.dtr = False
        ser.rts = False
        
        ser.close()
        time.sleep(2)  # Wait for device to restart
        
        print("✅ Connection reset complete")
        return True
        
    except Exception as e:
        print(f"❌ Reset failed: {e}")
        return False

def send_ctrl_c(device_path: str) -> bool:
    """Send Ctrl+C to interrupt any running program"""
    try:
        print("🛑 Sending Ctrl+C to interrupt any running program...")
        
        ser = serial.Serial(device_path, 115200, timeout=2)
        
        # Send Ctrl+C multiple times
        for _ in range(3):
            ser.write(b'\x03')  # Ctrl+C
            time.sleep(0.1)
        
        # Wait for response
        time.sleep(1)
        
        # Clear any pending data
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        ser.close()
        time.sleep(1)
        
        print("✅ Interrupt sent")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send interrupt: {e}")
        return False

def upload_file_raw(device_path: str, local_file: str, remote_name: str = None) -> bool:
    """Upload file using raw serial communication"""
    if remote_name is None:
        remote_name = os.path.basename(local_file)
    
    if not os.path.exists(local_file):
        print(f"❌ Local file not found: {local_file}")
        return False
    
    try:
        print(f"📤 Uploading {local_file} -> {remote_name}")
        
        # Read file content
        with open(local_file, 'rb') as f:
            content = f.read()
        
        ser = serial.Serial(device_path, 115200, timeout=5, write_timeout=5)
        
        # Send Ctrl+C to get to REPL
        ser.write(b'\x03')
        time.sleep(0.5)
        
        # Enter raw REPL mode
        ser.write(b'\x01')  # Ctrl+A for raw REPL
        time.sleep(0.5)
        
        # Wait for raw REPL prompt
        response = ser.read(100)
        if b'raw REPL' not in response:
            print(f"❌ Failed to enter raw REPL: {response}")
            ser.close()
            return False
        
        # Create file upload command
        upload_cmd = f"""
with open('{remote_name}', 'wb') as f:
    f.write({repr(content)})
print('File uploaded successfully')
""".strip()
        
        # Send command
        ser.write(upload_cmd.encode() + b'\x04')  # Ctrl+D to execute
        
        # Wait for execution
        time.sleep(2)
        
        # Read response
        response = ser.read(1000).decode('utf-8', errors='ignore')
        
        ser.close()
        
        if 'File uploaded successfully' in response:
            print(f"✅ Successfully uploaded {remote_name}")
            return True
        else:
            print(f"❌ Upload failed: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

def upload_files(files: List[str]) -> bool:
    """Upload multiple files with retry logic"""
    device = wait_for_device()
    if not device:
        return False
    
    # Try to reset connection first
    reset_device_connection(device)
    
    # Wait for device to be ready again
    device = wait_for_device(timeout=5)
    if not device:
        return False
    
    # Send interrupt to clear any running programs
    if not send_ctrl_c(device):
        print("⚠️  Warning: Could not send interrupt")
    
    # Upload each file
    success_count = 0
    for file_path in files:
        if upload_file_raw(device, file_path):
            success_count += 1
        else:
            print(f"❌ Failed to upload {file_path}")
    
    print(f"\n📊 Upload Summary: {success_count}/{len(files)} files uploaded successfully")
    return success_count == len(files)

def main():
    """Main function"""
    files_to_upload = [
        'main.py',
        'badge_config.py',
        'install_qrcode.py'
    ]
    
    # Check for WiFi config (only if configured)
    wifi_config = 'WIFI_CONFIG.py'
    if os.path.exists(wifi_config):
        # Only include if it's been configured (doesn't contain placeholder text)
        with open(wifi_config, 'r') as f:
            content = f.read()
            if 'YOUR_WIFI' not in content:
                files_to_upload.append(wifi_config)
                print("📶 WiFi configuration will be uploaded")
            else:
                print("⚠️  WiFi configuration found but not configured (contains placeholders)")
    
    # Check if files exist
    existing_files = []
    for file_path in files_to_upload:
        if os.path.exists(file_path):
            existing_files.append(file_path)
        else:
            print(f"⚠️  Warning: File not found: {file_path}")
    
    if not existing_files:
        print("❌ No files to upload")
        return False
    
    print("🦡 Badger 2040 W File Uploader")
    print("==============================")
    print(f"Files to upload: {', '.join(existing_files)}")
    print()
    
    return upload_files(existing_files)

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
