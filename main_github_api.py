# GitHub Badge for Badger 2040 W - Working Test Version
# Tests with publicly available GitHub API

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

# Configuration - Using direct GitHub API for testing
USERNAME = "Julian-Elliott"

# Test URLs using public GitHub API
API_BASE = "https://api.github.com"
USER_URL = f"{API_BASE}/users/{USERNAME}"

print(f"🌐 Testing with GitHub API:")
print(f"   User URL: {USER_URL}")

# Pages
PAGES = ["overview", "test", "api", "qr"]
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

def fetch_github_data():
    """Fetch data directly from GitHub API"""
    global cache
    
    try:
        print("🔄 Fetching user data from GitHub API...")
        
        headers = {
            'User-Agent': 'BadgerGitHubBadge/1.0',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = urequests.get(USER_URL, headers=headers, timeout=15)
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            
            # Create simplified badge data structure
            cache["data"] = {
                'profile': {
                    'username': user_data.get('login', 'unknown'),
                    'name': user_data.get('name', 'Unknown'),
                    'public_repos': user_data.get('public_repos', 0),
                    'followers': user_data.get('followers', 0),
                    'following': user_data.get('following', 0),
                    'html_url': user_data.get('html_url', f'https://github.com/{USERNAME}')
                },
                'stats': {
                    'total_stars': 0,  # We'll calculate this separately
                    'total_forks': 0
                }
            }
            
            cache["timestamp"] = time.time()
            print("✅ GitHub API data cached successfully")
            response.close()
            
            # Try to fetch repo data for stars count
            try:
                repos_url = f"{API_BASE}/users/{USERNAME}/repos?per_page=100"
                print("🔄 Fetching repositories...")
                
                repos_response = urequests.get(repos_url, headers=headers, timeout=15)
                if repos_response.status_code == 200:
                    repos = repos_response.json()
                    total_stars = sum(repo.get('stargazers_count', 0) for repo in repos)
                    total_forks = sum(repo.get('forks_count', 0) for repo in repos)
                    
                    cache["data"]["stats"]["total_stars"] = total_stars
                    cache["data"]["stats"]["total_forks"] = total_forks
                    print(f"✅ Repository stats: {total_stars} stars, {total_forks} forks")
                
                repos_response.close()
                
            except Exception as e:
                print(f"⚠️ Repo stats error: {e}")
            
            return True
            
        elif response.status_code == 403:
            print("❌ Rate limited or forbidden")
            response.close()
            return False
            
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"Response: {response.text[:100]}")
            response.close()
            return False
            
    except Exception as e:
        print(f"❌ Fetch error: {e}")
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
        status = f"API: {age}m ago" if age < 60 else f"API: {age//60}h ago"
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
        display.text("Loading...", 20, 50, WIDTH, 1)
        display.text("Fetching GitHub data", 20, 70, WIDTH, 1)
        draw_footer()
        return
    
    profile = cache["data"].get("profile", {})
    stats = cache["data"].get("stats", {})
    
    y = 30
    display.set_font("bitmap8")
    
    # Name and username
    name = profile.get("name", "Unknown")
    username = profile.get("username", "unknown")
    
    # Truncate long names
    if len(name) > 20:
        name = name[:17] + "..."
    
    display.text(f"{name}", 10, y, WIDTH, 1)
    y += 15
    display.text(f"@{username}", 10, y, WIDTH, 1)
    y += 20
    
    # Stats
    display.set_font("bitmap6")
    repos = profile.get("public_repos", 0)
    followers = profile.get("followers", 0)
    following = profile.get("following", 0)
    stars = stats.get("total_stars", 0)
    forks = stats.get("total_forks", 0)
    
    display.text(f"Repos: {repos}", 10, y, WIDTH, 1)
    y += 12
    display.text(f"Followers: {followers}", 10, y, WIDTH, 1)
    y += 12
    display.text(f"Following: {following}", 10, y, WIDTH, 1)
    y += 12
    display.text(f"Stars: {stars}", 10, y, WIDTH, 1)
    
    draw_footer()

def draw_test_page():
    """Draw API test results page"""
    display.set_pen(15)
    display.clear()
    
    draw_header("API Test")
    
    y = 30
    display.set_font("bitmap6")
    
    display.text("GitHub API Test:", 10, y, WIDTH, 1)
    y += 15
    
    if cache["data"]:
        profile = cache["data"].get("profile", {})
        
        display.text("✓ API connection OK", 10, y, WIDTH, 1)
        y += 12
        
        username = profile.get("username", "unknown")
        display.text(f"✓ User: {username}", 10, y, WIDTH, 1)
        y += 12
        
        repos = profile.get("public_repos", 0)
        display.text(f"✓ Repos: {repos}", 10, y, WIDTH, 1)
        y += 12
        
        followers = profile.get("followers", 0)
        display.text(f"✓ Followers: {followers}", 10, y, WIDTH, 1)
        
    else:
        display.text("✗ API connection failed", 10, y, WIDTH, 1)
        y += 12
        display.text("Check network & rate limits", 10, y, WIDTH, 1)
    
    draw_footer()

def draw_api_info_page():
    """Draw API information page"""
    display.set_pen(15)
    display.clear()
    
    draw_header("API Info")
    
    y = 30
    display.set_font("bitmap6")
    
    display.text("Data Source:", 10, y, WIDTH, 1)
    y += 12
    display.text("GitHub REST API v3", 10, y, WIDTH, 1)
    y += 15
    
    display.text("Endpoints:", 10, y, WIDTH, 1)
    y += 12
    display.text("/users/{username}", 10, y, WIDTH, 1)
    y += 12
    display.text("/users/{username}/repos", 10, y, WIDTH, 1)
    y += 15
    
    display.text("Status:", 10, y, WIDTH, 1)
    y += 12
    if cache["data"]:
        display.text("✓ Connected", 10, y, WIDTH, 1)
    else:
        display.text("✗ No data", 10, y, WIDTH, 1)
    
    draw_footer()

def draw_qr_page():
    """Draw QR code page"""
    display.set_pen(15)
    display.clear()
    
    draw_header("QR Code")
    
    if not HAS_QRCODE:
        display.set_font("bitmap8")
        display.text("QR module not", 20, 50, WIDTH, 1)
        display.text("available", 20, 70, WIDTH, 1)
        draw_footer()
        return
    
    if not cache["data"]:
        display.set_font("bitmap8")
        display.text("No profile data", 20, 50, WIDTH, 1)
        draw_footer()
        return
    
    profile = cache["data"].get("profile", {})
    github_url = profile.get("html_url", f"https://github.com/{USERNAME}")
    
    try:
        # Generate QR code
        qr_code.clear()
        qr_code.add_data(github_url)
        qr_code.make()
        
        # Draw QR code
        size = 2
        qr_matrix = qr_code.get_matrix()
        qr_size = len(qr_matrix)
        
        start_x = (WIDTH - qr_size * size) // 2
        start_y = 25
        
        display.set_pen(0)
        for y, row in enumerate(qr_matrix):
            for x, pixel in enumerate(row):
                if pixel:
                    display.rectangle(
                        start_x + x * size,
                        start_y + y * size,
                        size, size
                    )
        
        # Draw URL below QR code
        display.set_font("bitmap6")
        url_text = f"github.com/{USERNAME}"
        url_width = display.measure_text(url_text, 1)
        display.text(url_text, (WIDTH - url_width) // 2, HEIGHT - 25, WIDTH, 1)
        
    except Exception as e:
        display.set_font("bitmap6")
        display.text(f"QR Error: {str(e)[:20]}", 10, 50, WIDTH, 1)
    
    draw_footer()

def main():
    """Main application loop"""
    global current_page
    
    print("🦡 Starting GitHub Badge Application")
    print("====================================")
    
    # Initial data fetch
    print("📡 Initial data fetch...")
    fetch_github_data()
    
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
            fetch_github_data()
            
        button_states = buttons
        
        # Auto refresh every 10 minutes
        if time.time() - last_update > 600:
            print("🔄 Auto refresh...")
            fetch_github_data()
            last_update = time.time()
        
        # Draw current page
        page_name = PAGES[current_page]
        if page_name == "overview":
            draw_overview_page()
        elif page_name == "test":
            draw_test_page()
        elif page_name == "api":
            draw_api_info_page()
        elif page_name == "qr":
            draw_qr_page()
            
        display.update()
        time.sleep(0.1)
        gc.collect()

if __name__ == "__main__":
    main()
