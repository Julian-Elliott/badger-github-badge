# GitHub Badge for Badger 2040 W - GitHub Actions Caching Version
# Essential offline-capable badge with GitHub Pages data source

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

# Configuration
try:
    from badge_config import GITHUB_USERNAME, BADGE_REPO_NAME
    USERNAME = GITHUB_USERNAME
    REPO_NAME = BADGE_REPO_NAME
except ImportError:
    USERNAME = "Julian-Elliott"  # Change this to your GitHub username
    REPO_NAME = "badger-github-badge"

# Data URL
DATA_URL = f"https://{USERNAME}.github.io/{REPO_NAME}/api/badge_compact.json"
FALLBACK_URL = f"https://{USERNAME}.github.io/{REPO_NAME}/api/badge_simple.txt"

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
    """Fetch and cache data from GitHub Pages"""
    global cache
    
    try:
        print("Fetching data...")
        response = urequests.get(DATA_URL, timeout=10)
        if response.status_code == 200:
            cache["data"] = response.json()
            cache["timestamp"] = time.time()
            print("✓ Data cached")
            response.close()
            return True
        response.close()
    except Exception as e:
        print(f"Fetch error: {e}")
    
    # Fallback to simple text
    try:
        response = urequests.get(FALLBACK_URL, timeout=10)
        if response.status_code == 200:
            lines = response.text.strip().split('\n')
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
                print("✓ Fallback data cached")
                response.close()
                return True
        response.close()
    except Exception as e:
        print(f"Fallback error: {e}")
    
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
        status = f"Cached: {age}m ago" if age < 60 else f"Cached: {age//60}h ago"
    else:
        status = "No data cached"
    
    display.text(status, 5, HEIGHT - 10, WIDTH, 1)


def draw_overview():
    """Draw overview page"""
    display.set_pen(15)
    display.clear()
    draw_header("Overview")
    
    if not cache["data"]:
        display.set_pen(0)
        display.text("No data - Press A to update", 5, 50, WIDTH, 1)
        draw_footer()
        display.update()
        return
    
    profile = cache["data"].get("profile", {})
    stats = cache["data"].get("stats", {})
    
    display.set_pen(0)
    y = 25
    
    # Name and username
    display.set_font("bitmap8")
    name = profile.get('name', profile.get('username', USERNAME))[:20]
    display.text(name, 5, y, WIDTH, 1)
    y += 15
    
    display.set_font("bitmap6")
    display.text(f"@{profile.get('username', USERNAME)}", 5, y, WIDTH, 1)
    y += 15
    
    # Stats
    display.text(f"Repos: {profile.get('public_repos', 0)}", 5, y, WIDTH//2, 1)
    display.text(f"Stars: {stats.get('total_stars', 0)}", WIDTH//2, y, WIDTH//2, 1)
    y += 12
    
    display.text(f"Followers: {profile.get('followers', 0)}", 5, y, WIDTH//2, 1)
    display.text(f"Forks: {stats.get('total_forks', 0)}", WIDTH//2, y, WIDTH//2, 1)
    
    draw_footer()
    display.update()


def draw_stats():
    """Draw stats page"""
    display.set_pen(15)
    display.clear()
    draw_header("Statistics")
    
    if not cache["data"]:
        display.set_pen(0)
        display.text("No stats available", 5, 50, WIDTH, 1)
        draw_footer()
        display.update()
        return
    
    profile = cache["data"].get("profile", {})
    stats = cache["data"].get("stats", {})
    
    display.set_pen(0)
    y = 25
    
    display.set_font("bitmap8")
    display.text("Repository Stats", 5, y, WIDTH, 1)
    y += 15
    
    display.set_font("bitmap6")
    display.text(f"Total Repos: {profile.get('public_repos', 0)}", 5, y, WIDTH, 1)
    y += 12
    display.text(f"Total Stars: {stats.get('total_stars', 0)}", 5, y, WIDTH, 1)
    y += 12
    display.text(f"Total Forks: {stats.get('total_forks', 0)}", 5, y, WIDTH, 1)
    y += 15
    
    # Most starred repo
    most_starred = stats.get('most_starred', {})
    if most_starred:
        display.text("Most Starred:", 5, y, WIDTH, 1)
        y += 12
        repo_name = most_starred.get('name', 'Unknown')[:25]
        display.text(f"• {repo_name}", 5, y, WIDTH, 1)
        y += 12
        stars = most_starred.get('stargazers_count', 0)
        display.text(f"  {stars} stars", 5, y, WIDTH, 1)
    
    draw_footer()
    display.update()


def draw_activity():
    """Draw activity page"""
    display.set_pen(15)
    display.clear()
    draw_header("Activity")
    
    if not cache["data"]:
        display.set_pen(0)
        display.text("No activity data", 5, 50, WIDTH, 1)
        draw_footer()
        display.update()
        return
    
    activity = cache["data"].get("activity", [])
    
    display.set_pen(0)
    y = 25
    
    display.set_font("bitmap8")
    display.text("Recent Events", 5, y, WIDTH, 1)
    y += 15
    
    display.set_font("bitmap6")
    
    if not activity:
        display.text("No recent activity", 5, y, WIDTH, 1)
    else:
        for event in activity[:4]:  # Show up to 4 events
            if y > HEIGHT - 25:
                break
            text = event.get('display', 'Event')[:35]
            display.text(f"• {text}", 5, y, WIDTH, 1)
            y += 12
    
    draw_footer()
    display.update()


def draw_qr():
    """Draw QR code page"""
    display.set_pen(15)
    display.clear()
    draw_header("QR Code")
    
    if not HAS_QRCODE:
        display.set_pen(0)
        display.text("QR module not available", 5, 50, WIDTH, 1)
        draw_footer()
        display.update()
        return
    
    # Get GitHub URL
    if cache["data"]:
        github_url = cache["data"].get("profile", {}).get('html_url', f'https://github.com/{USERNAME}')
    else:
        github_url = f'https://github.com/{USERNAME}'
    
    # Generate and draw QR code
    qr_code.set_text(github_url)
    
    w, h = qr_code.get_size()
    qr_size = 80
    module_size = qr_size // w
    qr_x = (WIDTH - qr_size) // 2
    qr_y = 30
    
    # Background
    display.rectangle(qr_x - 2, qr_y - 2, qr_size + 4, qr_size + 4)
    
    # QR modules
    display.set_pen(0)
    for y in range(h):
        for x in range(w):
            if qr_code.get_module(x, y):
                px = qr_x + x * module_size
                py = qr_y + y * module_size
                display.rectangle(px, py, module_size, module_size)
    
    # URL text
    display.set_font("bitmap6")
    url_text = github_url.replace('https://', '')
    url_width = display.measure_text(url_text, 1)
    display.text(url_text, (WIDTH - url_width) // 2, HEIGHT - 20, WIDTH, 1)
    
    draw_footer()
    display.update()


def draw_page():
    """Draw current page"""
    page = PAGES[current_page]
    if page == "overview":
        draw_overview()
    elif page == "stats":
        draw_stats()
    elif page == "activity":
        draw_activity()
    elif page == "qr":
        draw_qr()


def update_display():
    """Update data and display"""
    display.set_pen(15)
    display.clear()
    display.set_pen(0)
    display.set_font("bitmap8")
    display.text("Updating...", 5, 50, WIDTH, 1)
    display.update()
    
    success = fetch_data()
    
    display.set_pen(15)
    display.clear()
    display.set_pen(0)
    
    if success:
        display.text("✓ Updated", 5, 50, WIDTH, 1)
    else:
        display.text("✗ Update failed", 5, 50, WIDTH, 1)
    
    display.update()
    time.sleep(1)
    draw_page()


def main():
    """Main loop"""
    global current_page
    
    print("Starting GitHub Badge...")
    
    # Show startup
    display.set_pen(15)
    display.clear()
    display.set_pen(0)
    display.set_font("bitmap8")
    display.text("GitHub Badge", 5, 40, WIDTH, 1)
    display.set_font("bitmap6")
    display.text("Loading...", 5, 60, WIDTH, 1)
    display.update()
    
    # Initial fetch
    if not cache["data"]:
        fetch_data()
    
    draw_page()
    
    try:
        while True:
            # Auto-update every 30 minutes
            if cache["timestamp"] > 0 and time.time() - cache["timestamp"] > 1800:
                print("Auto-update...")
                fetch_data()
                draw_page()
            
            # Button handling
            if display.pressed(badger2040.BUTTON_UP):
                current_page = (current_page - 1) % len(PAGES)
                draw_page()
                time.sleep(0.2)
                
            elif display.pressed(badger2040.BUTTON_DOWN):
                current_page = (current_page + 1) % len(PAGES)
                draw_page()
                time.sleep(0.2)
                
            elif display.pressed(badger2040.BUTTON_A):
                update_display()
                time.sleep(0.3)
                
            elif display.pressed(badger2040.BUTTON_B):
                draw_page()  # Reload from cache
                time.sleep(0.2)
                
            elif display.pressed(badger2040.BUTTON_C):
                # Show cache info
                display.set_pen(15)
                display.clear()
                display.set_pen(0)
                display.set_font("bitmap8")
                display.text("Cache Info", 5, 30, WIDTH, 1)
                display.set_font("bitmap6")
                if cache["timestamp"]:
                    age = int((time.time() - cache["timestamp"]) / 60)
                    display.text(f"Age: {age} minutes", 5, 50, WIDTH, 1)
                    display.text("Data cached ✓", 5, 65, WIDTH, 1)
                else:
                    display.text("No cache", 5, 50, WIDTH, 1)
                display.text("Press any button", 5, 85, WIDTH, 1)
                display.update()
                
                # Wait for button
                while not any([display.pressed(badger2040.BUTTON_UP),
                              display.pressed(badger2040.BUTTON_DOWN),
                              display.pressed(badger2040.BUTTON_A),
                              display.pressed(badger2040.BUTTON_B)]):
                    time.sleep(0.1)
                
                draw_page()
                time.sleep(0.2)
            
            time.sleep(0.05)
            gc.collect()
            
    except KeyboardInterrupt:
        print("Shutting down...")
    except Exception as e:
        print(f"Error: {e}")
        display.set_pen(15)
        display.clear()
        display.set_pen(0)
        display.text("Error - restart device", 5, 50, WIDTH, 1)
        display.update()
    finally:
        display.halt()


if __name__ == "__main__":
    main()