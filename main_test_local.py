# GitHub Badge for Badger 2040 W - Local Testing Version
# Test version using local HTTP server

import badger2040
from badger2040 import WIDTH, HEIGHT
import urequests
import time
import json
import gc

# Try to import QR code module
try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False

# Configuration for local testing
LOCAL_SERVER_IP = "192.168.4.214"
LOCAL_SERVER_PORT = "8080"

USERNAME = "Julian-Elliott"
REPO_NAME = "badger-github-badge"

# Local test URLs
DATA_URL = f"http://{LOCAL_SERVER_IP}:{LOCAL_SERVER_PORT}/api/badge_compact.json"
FALLBACK_URL = f"http://{LOCAL_SERVER_IP}:{LOCAL_SERVER_PORT}/api/badge_simple.txt"

print(f"🌐 Testing with local server:")
print(f"   Data URL: {DATA_URL}")
print(f"   Fallback URL: {FALLBACK_URL}")

# Pages
PAGES = ["overview", "stats", "activity", "qr"]
current_page = 0

# Cache
cache = {"data": None, "timestamp": 0}

# Display
display = badger2040.Badger2040()
display.led(128)
display.set_update_speed(badger2040.UPDATE_FAST)
display.connect()

if HAS_QRCODE:
    qr_code = qrcode.QRCode()

def fetch_data():
    """Fetch and cache data from local server"""
    global cache
    
    try:
        print("🔄 Fetching data from local server...")
        response = urequests.get(DATA_URL, timeout=10)
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            cache["data"] = response.json()
            cache["timestamp"] = time.time()
            print("✅ Data cached successfully")
            response.close()
            return True
        else:
            print(f"❌ HTTP error: {response.status_code}")
        response.close()
    except Exception as e:
        print(f"❌ Fetch error: {e}")
    
    # Fallback to simple text
    try:
        print("🔄 Trying fallback URL...")
        response = urequests.get(FALLBACK_URL, timeout=10)
        print(f"📡 Fallback response status: {response.status_code}")
        
        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            print(f"📝 Received {len(lines)} lines")
            
            if len(lines) >= 6:
                cache["data"] = {
                    'profile': {
                        'username': lines[0],
                        'name': lines[1], 
                        'public_repos': int(lines[2]),
                        'followers': int(lines[3]),
                        'html_url': f'https://github.com/{lines[0]}'
                    },
                    'stats': {
                        'total_stars': int(lines[4]),
                        'total_forks': int(lines[5])
                    },
                    'activity': []
                }
                cache["timestamp"] = time.time()
                print("✅ Fallback data cached successfully")
                response.close()
                return True
        response.close()
    except Exception as e:
        print(f"❌ Fallback error: {e}")
    
    print("❌ All data fetch attempts failed")
    return False

def draw_header(title):
    """Draw header"""
    display.set_pen(0)
    display.rectangle(0, 0, WIDTH, 20)
    display.set_pen(15)
    display.set_font("bitmap8")
    display.text("GitHub", 4, 6, WIDTH, 1)
    
    # Page indicator
    indicator = f"{current_page + 1}/{len(PAGES)}"
    display.text(indicator, WIDTH - 30, 6, WIDTH, 1)
    
    # Title
    display.set_font("bitmap6")
    title_width = display.measure_text(title, 1)
    display.text(title, (WIDTH - title_width) // 2, 6, WIDTH, 1)

def draw_footer():
    """Draw status footer"""
    display.set_pen(0)
    display.set_font("bitmap6")
    
    if cache["timestamp"] > 0:
        age = int((time.time() - cache["timestamp"]) / 60)
        status = f"Local: {age}m ago" if age < 60 else f"Local: {age//60}h ago"
    else:
        status = "No data"
    
    display.text(status, 4, HEIGHT - 12, WIDTH, 1)

def draw_overview_page():
    """Draw overview page"""
    display.set_pen(15)
    display.clear()
    
    draw_header("Overview")
    
    if not cache["data"]:
        display.set_font("bitmap8")
        display.text("No data available", 20, 50, WIDTH, 1)
        display.text("Check network connection", 20, 70, WIDTH, 1)
        draw_footer()
        return
    
    profile = cache["data"].get("profile", {})
    stats = cache["data"].get("stats", {})
    
    y = 30
    display.set_font("bitmap8")
    
    # Name and username
    name = profile.get("name", "Unknown")
    username = profile.get("username", "unknown")
    display.text(f"{name}", 10, y, WIDTH, 1)
    y += 15
    display.text(f"@{username}", 10, y, WIDTH, 1)
    y += 20
    
    # Stats
    display.set_font("bitmap6")
    repos = profile.get("public_repos", 0)
    followers = profile.get("followers", 0)
    stars = stats.get("total_stars", 0)
    
    display.text(f"Repos: {repos}", 10, y, WIDTH, 1)
    y += 12
    display.text(f"Followers: {followers}", 10, y, WIDTH, 1)
    y += 12
    display.text(f"Stars: {stars}", 10, y, WIDTH, 1)
    
    draw_footer()

def draw_test_page():
    """Draw test results page"""
    display.set_pen(15)
    display.clear()
    
    draw_header("Test Results")
    
    y = 30
    display.set_font("bitmap6")
    
    display.text("Local Server Test:", 10, y, WIDTH, 1)
    y += 15
    
    if cache["data"]:
        display.text("✓ Data loaded successfully", 10, y, WIDTH, 1)
        y += 12
        
        profile = cache["data"].get("profile", {})
        username = profile.get("username", "unknown")
        display.text(f"✓ User: {username}", 10, y, WIDTH, 1)
        y += 12
        
        repos = profile.get("public_repos", 0)
        display.text(f"✓ Repos: {repos}", 10, y, WIDTH, 1)
    else:
        display.text("✗ No data loaded", 10, y, WIDTH, 1)
        y += 12
        display.text("Check server & network", 10, y, WIDTH, 1)
    
    draw_footer()

def main():
    """Main application loop"""
    global current_page
    
    print("🦡 Starting GitHub Badge Test Application")
    print("=========================================")
    
    # Initial data fetch
    print("📡 Initial data fetch...")
    fetch_data()
    
    # Display test results first
    draw_test_page()
    display.update()
    
    last_update = time.time()
    button_states = [False, False, False, False, False]
    
    while True:
        # Check buttons
        buttons = [
            display.pressed(badger2040.BUTTON_A),
            display.pressed(badger2040.BUTTON_B), 
            display.pressed(badger2040.BUTTON_C),
            display.pressed(badger2040.BUTTON_UP),
            display.pressed(badger2040.BUTTON_DOWN)
        ]
        
        # Button A - Previous page
        if buttons[0] and not button_states[0]:
            current_page = (current_page - 1) % len(PAGES)
            print(f"📄 Page: {PAGES[current_page]}")
            
        # Button B - Next page  
        elif buttons[1] and not button_states[1]:
            current_page = (current_page + 1) % len(PAGES)
            print(f"📄 Page: {PAGES[current_page]}")
            
        # Button C - Refresh data
        elif buttons[2] and not button_states[2]:
            print("🔄 Manual refresh...")
            fetch_data()
            
        button_states = buttons
        
        # Auto refresh every 5 minutes
        if time.time() - last_update > 300:
            print("🔄 Auto refresh...")
            fetch_data()
            last_update = time.time()
        
        # Draw current page
        if current_page == 0 or PAGES[current_page] == "overview":
            draw_overview_page()
        else:
            draw_test_page()
            
        display.update()
        time.sleep(0.1)
        gc.collect()

if __name__ == "__main__":
    main()
