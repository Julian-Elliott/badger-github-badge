#!/usr/bin/env python3
"""
Simple network connectivity test for Badger 2040 W
"""

import network
import time
import urequests

def test_network_simple():
    """Test basic network connectivity"""
    print("🌐 Network Connectivity Test")
    print("=" * 30)
    
    # Check WiFi status
    sta = network.WLAN(network.STA_IF)
    print(f"WiFi Active: {sta.active()}")
    print(f"WiFi Connected: {sta.isconnected()}")
    
    if not sta.isconnected():
        print("❌ WiFi not connected!")
        return False
    
    # Get network info
    config = sta.ifconfig()
    ip = config[0]
    gateway = config[2]
    
    print(f"📱 Device IP: {ip}")
    print(f"🌐 Gateway: {gateway}")
    
    # Test basic connectivity
    test_urls = [
        "http://httpbin.org/ip",
        "http://192.168.4.214:8080/api/badge_simple.txt",
        "http://192.168.4.214:8080/api/badge_compact.json"
    ]
    
    for url in test_urls:
        print(f"\n🔗 Testing: {url}")
        try:
            response = urequests.get(url, timeout=10)
            print(f"   ✅ Status: {response.status_code}")
            
            content = response.text
            if len(content) > 100:
                content = content[:100] + "..."
            print(f"   📄 Content: {content}")
            
            response.close()
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(1)
    
    return True

# Run the test
if __name__ == "__main__":
    test_network_simple()
