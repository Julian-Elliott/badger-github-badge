#!/usr/bin/env python3
"""
Test GitHub Pages URLs for the badge application
"""

import network
import urequests
import time

def test_github_pages():
    """Test GitHub Pages URLs"""
    print("=== GitHub Pages URL Test ===")
    
    username = "Julian-Elliott"
    repo = "badger-github-badge"
    
    urls_to_test = [
        f"https://{username}.github.io/{repo}/api/badge_compact.json",
        f"https://{username}.github.io/{repo}/api/badge_simple.txt",
        f"https://{username}.github.io/{repo}/",
        "https://api.github.com/rate_limit",
        "https://api.github.com/users/Julian-Elliott"
    ]
    
    sta = network.WLAN(network.STA_IF)
    if not sta.isconnected():
        print("❌ WiFi not connected")
        return
    
    print(f"📡 IP: {sta.ifconfig()[0]}")
    
    headers = {
        'User-Agent': 'BadgerGitHubBadge/1.0',
        'Accept': 'application/json'
    }
    
    for url in urls_to_test:
        print(f"\n🔗 Testing: {url}")
        try:
            response = urequests.get(url, headers=headers, timeout=15)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text
                if len(content) > 200:
                    content = content[:200] + "..."
                print(f"   Content preview: {content}")
            elif response.status_code == 404:
                print("   ❌ Not found - URL may not exist")
            elif response.status_code == 403:
                print("   ❌ Forbidden - possible rate limit")
            else:
                print(f"   ⚠️  Unexpected status: {response.text[:100]}")
            
            response.close()
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(1)  # Be nice to servers

if __name__ == "__main__":
    test_github_pages()
