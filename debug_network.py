#!/usr/bin/env python3
"""
Debug network connectivity and GitHub API access on Badger 2040 W
"""

import network
import urequests
import time
import gc

def test_network():
    """Test network connectivity and GitHub API access"""
    print("=== Network Debug Test ===")
    
    # Check WiFi status
    sta = network.WLAN(network.STA_IF)
    print(f"WiFi Active: {sta.active()}")
    print(f"WiFi Connected: {sta.isconnected()}")
    
    if sta.isconnected():
        config = sta.ifconfig()
        print(f"IP Address: {config[0]}")
        print(f"Subnet Mask: {config[1]}")
        print(f"Gateway: {config[2]}")
        print(f"DNS: {config[3]}")
        
        # Test basic connectivity
        print("\n=== Testing Basic Connectivity ===")
        try:
            print("Testing httpbin.org...")
            response = urequests.get('http://httpbin.org/ip', timeout=10)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            response.close()
        except Exception as e:
            print(f"Basic HTTP Error: {e}")
        
        # Test HTTPS connectivity
        print("\n=== Testing HTTPS Connectivity ===")
        try:
            print("Testing GitHub API...")
            headers = {
                'User-Agent': 'BadgerGitHubBadge/1.0',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # Test with a simple endpoint first
            response = urequests.get('https://api.github.com/rate_limit', 
                                   headers=headers, timeout=15)
            print(f"GitHub Rate Limit Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Rate limit: {data['rate']['remaining']}/{data['rate']['limit']}")
                print(f"Reset time: {data['rate']['reset']}")
            elif response.status_code == 403:
                print("Rate limited or forbidden")
                print(f"Response headers: {response.headers}")
                print(f"Response text: {response.text}")
            else:
                print(f"Unexpected status: {response.text}")
            
            response.close()
            
        except Exception as e:
            print(f"GitHub API Error: {e}")
            import sys
            sys.print_exception(e)
        
        # Test actual user endpoint
        print("\n=== Testing User Endpoint ===")
        try:
            response = urequests.get('https://api.github.com/users/octocat', 
                                   headers=headers, timeout=15)
            print(f"User API Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"User: {data.get('login')}")
                print(f"Name: {data.get('name')}")
                print(f"Public repos: {data.get('public_repos')}")
            else:
                print(f"User API Response: {response.text[:200]}")
            
            response.close()
            
        except Exception as e:
            print(f"User API Error: {e}")
    
    else:
        print("WiFi not connected!")
        
    # Memory cleanup
    gc.collect()
    print(f"\nFree memory: {gc.mem_free()} bytes")

if __name__ == "__main__":
    test_network()
