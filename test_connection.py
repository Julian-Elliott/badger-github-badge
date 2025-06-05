#!/usr/bin/env python3
"""
Test WiFi connectivity and badge functionality on Badger 2040 W
"""

import serial
import time
import sys
import glob
from typing import Optional

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

def send_command(ser: serial.Serial, command: str, wait_time: float = 2.0) -> str:
    """Send command and return response"""
    # Clear any pending input
    ser.reset_input_buffer()
    
    # Send command
    ser.write((command + '\r\n').encode())
    time.sleep(wait_time)
    
    # Read response
    response = ser.read_all().decode('utf-8', errors='ignore')
    return response

def test_wifi_connection(device_path: str) -> bool:
    """Test WiFi connection on the device"""
    try:
        print("🌐 Testing WiFi Connection...")
        print("============================")
        
        ser = serial.Serial(device_path, 115200, timeout=10)
        
        # Send Ctrl+C to interrupt any running program
        ser.write(b'\x03')
        time.sleep(1)
        
        # Test basic REPL
        response = send_command(ser, "", 0.5)
        if ">>>" not in response:
            print("❌ Failed to get REPL prompt")
            return False
        
        print("✅ REPL connection established")
        
        # Test WiFi configuration
        print("\n📋 Checking WiFi configuration...")
        response = send_command(ser, "import WIFI_CONFIG; print(f'SSID: {WIFI_CONFIG.SSID}, Country: {WIFI_CONFIG.COUNTRY}')")
        if "YOUR_WIFI" in response:
            print("❌ WiFi not configured (still has placeholder values)")
            print("   Run 'make setup-wifi' to configure")
            return False
        elif "SSID:" in response:
            print("✅ WiFi configuration loaded")
            print(f"   {response.strip().split('SSID:')[1] if 'SSID:' in response else 'Config found'}")
        else:
            print("❌ WiFi configuration not found")
            return False
        
        # Test network connection
        print("\n🔗 Testing network connection...")
        response = send_command(ser, "import network; sta=network.WLAN(network.STA_IF); print(f'Connected: {sta.isconnected()}')", 3.0)
        if "Connected: True" in response:
            print("✅ WiFi already connected")
            # Get IP address
            ip_response = send_command(ser, "print(f'IP: {sta.ifconfig()[0]}')")
            if "IP:" in ip_response:
                print(f"   {ip_response.strip().split('IP:')[1] if 'IP:' in ip_response else 'IP found'}")
        else:
            print("⚠️  WiFi not connected, attempting connection...")
            # Try to connect
            connect_response = send_command(ser, "import badger2040; display=badger2040.Badger2040(); display.connect()", 15.0)
            if "error" in connect_response.lower() or "fail" in connect_response.lower():
                print("❌ WiFi connection failed")
                print(f"   Error: {connect_response}")
                return False
            else:
                print("✅ WiFi connection attempted")
                # Check if connected now
                check_response = send_command(ser, "print(f'Connected: {sta.isconnected()}')")
                if "Connected: True" in check_response:
                    print("✅ WiFi connection successful")
                else:
                    print("❌ WiFi connection failed")
                    return False
        
        # Test GitHub API access
        print("\n🐙 Testing GitHub API access...")
        github_test = """
try:
    import urequests
    response = urequests.get('https://api.github.com', timeout=10)
    print(f'GitHub API Status: {response.status_code}')
    response.close()
    print('✅ GitHub API accessible')
except Exception as e:
    print(f'❌ GitHub API error: {e}')
"""
        response = send_command(ser, github_test, 12.0)
        if "GitHub API Status: 200" in response:
            print("✅ GitHub API accessible")
        elif "GitHub API error" in response:
            print("❌ GitHub API not accessible")
            print(f"   Error details in device output")
            return False
        
        print("\n✅ All WiFi tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ WiFi test failed: {e}")
        return False
    finally:
        try:
            ser.close()
        except:
            pass

def test_badge_display(device_path: str) -> bool:
    """Test badge display functionality"""
    try:
        print("\n🦡 Testing Badge Display...")
        print("===========================")
        
        ser = serial.Serial(device_path, 115200, timeout=10)
        
        # Send Ctrl+C to interrupt any running program
        ser.write(b'\x03')
        time.sleep(1)
        
        # Test display initialization
        print("📺 Testing display...")
        display_test = """
try:
    import badger2040
    display = badger2040.Badger2040()
    display.set_update_speed(badger2040.UPDATE_FAST)
    print('✅ Display initialized')
except Exception as e:
    print(f'❌ Display error: {e}')
"""
        response = send_command(ser, display_test, 3.0)
        if "Display initialized" in response:
            print("✅ Display initialization successful")
        else:
            print("❌ Display initialization failed")
            return False
        
        # Test QR code module
        print("\n📱 Testing QR code module...")
        qr_test = """
try:
    import qrcode
    print('✅ QR code module available')
except ImportError:
    print('❌ QR code module not installed')
except Exception as e:
    print(f'❌ QR code error: {e}')
"""
        response = send_command(ser, qr_test, 2.0)
        if "QR code module available" in response:
            print("✅ QR code module ready")
        else:
            print("⚠️  QR code module not available (run 'make install-qr')")
        
        print("\n✅ Badge display tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Badge display test failed: {e}")
        return False
    finally:
        try:
            ser.close()
        except:
            pass

def main():
    """Main function"""
    print("🦡 Badger 2040 W Connection & Badge Tester")
    print("==========================================")
    
    # Find device
    device = find_pico_device()
    if not device:
        print("❌ No Pico device found")
        print("   Make sure device is connected and not in bootloader mode")
        return False
    
    print(f"✅ Found device: {device}")
    print()
    
    # Run tests
    wifi_ok = test_wifi_connection(device)
    display_ok = test_badge_display(device)
    
    print("\n" + "="*50)
    print("🏁 Test Summary")
    print("="*50)
    print(f"WiFi & Network: {'✅ PASS' if wifi_ok else '❌ FAIL'}")
    print(f"Badge Display:  {'✅ PASS' if display_ok else '❌ FAIL'}")
    
    if wifi_ok and display_ok:
        print("\n🎉 All tests passed! Your badge is ready to run.")
        print("   Try: make run")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        if not wifi_ok:
            print("   For WiFi issues: make setup-wifi")
        print("   For display issues: make upload && make install-qr")
    
    return wifi_ok and display_ok

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
