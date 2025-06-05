# GitHub Badge for Badger 2040 W - GitHub Actions Version
# Downloads pre-generated badge data from GitHub Pages
# Features smart caching for offline viewing and efficient button navigation

import badger2040
from badger2040 import WIDTH, HEIGHT
import urequests
import time
import json
import gc
import badger_os

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
    USERNAME = "Julian-Elliott"
    REPO_NAME = "badger-github-badge"

BASE_URL = f"https://{USERNAME}.github.io/{REPO_NAME}/api"

# Data URLs
COMPACT_DATA_URL = f"{BASE_URL}/badge_compact.json"
SIMPLE_DATA_URL = f"{BASE_URL}/badge_simple.txt"

# Page configuration
PAGES = ["overview", "stats", "activity", "qr"]
CURRENT_PAGE = 0

# Smart cache system - stores data for each page
CACHE = {
    "data": None,
    "pages": {},
    "last_update": 0,
    "update_count": 0
}

UPDATE_INTERVAL = 1800  # 30 minutes

# Initialize display
display = badger2040.Badger2040()
display.led(128)
display.set_update_speed(badger2040.UPDATE_FAST)
display.connect()

# QR code setup
if HAS_QRCODE:
    qr_code = qrcode.QRCode()


def cache_page_data(page_name, data):
    """Cache data for specific page"""
    CACHE["pages"][page_name] = {
        "data": data,
        "timestamp": time.time()
    }
    print(f"Cached data for page: {page_name}")


def get_cached_page_data(page_name):
    """Get cached data for specific page"""
    if page_name in CACHE["pages"]:
        cached = CACHE["pages"][page_name]
        age = time.time() - cached["timestamp"]
        print(f"Using cached data for {page_name} (age: {age:.0f}s)")
        return cached["data"]
    return None


def fetch_badge_data():
    """Fetch badge data from GitHub Pages with fallback"""
    global CACHE
    
    try:
        print("Fetching data from GitHub Pages...")
        response = urequests.get(COMPACT_DATA_URL, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            CACHE["data"] = data
            CACHE["last_update"] = time.time()
            CACHE["update_count"] += 1
            
            # Cache data for each page
            cache_page_data("overview", data.get("profile", {}))
            cache_page_data("stats", data.get("stats", {}))
            cache_page_data("activity", data.get("activity", []))
            cache_page_data("qr", {"url": data.get("profile", {}).get("html_url", "")})
            
            print("✓ Data updated and cached")
            response.close()
            return True
        
        response.close()
        
    except Exception as e:
        print(f"Fetch error: {e}")
    
    # Try simple text fallback
    try:
        print("Trying simple text fallback...")
        response = urequests.get(SIMPLE_DATA_URL, timeout=10)
        
        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            if len(lines) >= 8:
                simple_data = {
                    'profile': {
                        'username': lines[0],
                        'name': lines[1],
                        'public_repos': int(lines[2]),
                        'followers': int(lines[3]),
                        'html_url': f'https://github.com/{lines[0]}'
                    },
                    'stats': {
                        'total_stars': int(lines[4]),
                        'total_forks': int(lines[5]),
                        'top_language': lines[6]
                    },
                    'activity': [],
                    'meta': {'source': 'simple_text'}
                }
                CACHE["data"] = simple_data
                CACHE["last_update"] = time.time()
                print("✓ Simple data loaded")
                response.close()
                return True
        
        response.close()
        
    except Exception as e:
        print(f"Simple fallback error: {e}")
    
    return False


def update_data():
    """Update data with visual feedback"""
    display.set_pen(15)
    display.clear()
    display.set_pen(0)
    display.set_font("bitmap8")
    display.text("Updating...", 5, 40, WIDTH, 1)
    display.set_font("bitmap6")
    display.text("Downloading from GitHub Pages", 5, 55, WIDTH, 1)
    display.update()
    
    success = fetch_badge_data()
    
    # Show result
    display.set_pen(15)
    display.clear()
    display.set_pen(0)
    display.set_font("bitmap8")
    
    if success:
        display.text("✓ Updated", 5, 45, WIDTH, 1)
        display.set_font("bitmap6")
        display.text(f"Cache: {len(CACHE['pages'])} pages", 5, 60, WIDTH, 1)
    else:
        display.text("✗ Failed", 5, 45, WIDTH, 1)
        display.set_font("bitmap6")
        display.text("Using cached data", 5, 60, WIDTH, 1)
    
    display.update()
    time.sleep(1.5)
    gc.collect()
    return success


def draw_header(title):
    """Draw professional header"""
    display.set_pen(0)
    display.rectangle(0, 0, WIDTH, 22)
    display.set_pen(15)
    
    # GitHub branding
    display.set_font("bitmap8")
    display.text("GitHub", 4, 7, WIDTH, 1)
    
    # Page indicator
    page_indicator = f"{CURRENT_PAGE + 1}/{len(PAGES)}"
    nav_width = display.measure_text(page_indicator, 1)
    display.text(page_indicator, WIDTH - nav_width - 4, 7, WIDTH, 1)
    
    # Title centered
    display.set_font("bitmap6")
    title_width = display.measure_text(title, 1)
    display.text(title, (WIDTH - title_width) // 2, 7, WIDTH, 1)


def draw_footer():
    """Draw status footer"""
    display.set_pen(0)
    display.set_font("bitmap6")
    
    # Cache status
    if CACHE["last_update"] > 0:
        age = int((time.time() - CACHE["last_update"]) / 60)
        if age < 60:
            status = f"Updated: {age}m ago"
        else:
            status = f"Updated: {age//60}h ago"
    else:
        status = "Data: cached"
    
    display.text(status, 5, HEIGHT - 12, WIDTH, 1)
    
    # Controls hint
    display.text("↑↓:Nav A:Update B:Cache C:View", 5, HEIGHT - 2, WIDTH, 1)


def draw_overview_page():
    """Draw overview page"""
    display.set_pen(15)
    display.clear()
    draw_header("Overview")
    
    # Get data from cache or main cache
    profile = get_cached_page_data("overview") or CACHE.get("data", {}).get("profile", {})
    stats = CACHE.get("data", {}).get("stats", {})
    
    if not profile:
        display.set_pen(0)
        display.set_font("bitmap8")
        display.text("No data available", 5, 50, WIDTH, 1)
        display.set_font("bitmap6")
        display.text("Press A to update", 5, 65, WIDTH, 1)
        draw_footer()
        display.update()
        return
    
    display.set_pen(0)
    y = 28
    
    # User info
    display.set_font("bitmap8")
    name = profile.get('name', profile.get('username', USERNAME))
    if len(name) > 20:
        name = name[:17] + "..."
    display.text(name, 5, y, WIDTH - 10, 1)
    y += 16
    
    display.set_font("bitmap6")
    display.text(f"@{profile.get('username', USERNAME)}", 5, y, WIDTH - 10, 1)
    y += 14
    
    # Stats in columns
    col1_x = 5
    col2_x = WIDTH // 2 + 10
    
    display.text(f"Repos: {profile.get('public_repos', 0)}", col1_x, y, WIDTH//2, 1)
    display.text(f"Stars: {stats.get('total_stars', 0)}", col2_x, y, WIDTH//2, 1)
    y += 12
    
    display.text(f"Followers: {profile.get('followers', 0)}", col1_x, y, WIDTH//2, 1)
    display.text(f"Forks: {stats.get('total_forks', 0)}", col2_x, y, WIDTH//2, 1)
    y += 12
    
    # Top language
    top_lang = stats.get('top_language')
    if top_lang and top_lang != 'None':
        display.text(f"Top Language: {top_lang}", 5, y, WIDTH, 1)
    
    draw_footer()
    display.update()


def draw_stats_page():
    """Draw statistics page"""
    display.set_pen(15)
    display.clear()
    draw_header("Statistics")
    
    stats = get_cached_page_data("stats") or CACHE.get("data", {}).get("stats", {})
    profile = CACHE.get("data", {}).get("profile", {})
    
    if not stats:
        display.set_pen(0)
        display.text("No stats available", 5, 50, WIDTH, 1)
        draw_footer()
        display.update()
        return
    
    display.set_pen(0)
    y = 28
    
    # Repository statistics
    display.set_font("bitmap8")
    display.text("Repository Stats", 5, y, WIDTH, 1)
    y += 16
    
    display.set_font("bitmap6")
    display.text(f"Total Repos: {profile.get('public_repos', 0)}", 5, y, WIDTH, 1)
    y += 12
    display.text(f"Total Stars: {stats.get('total_stars', 0)}", 5, y, WIDTH, 1)
    y += 12
    display.text(f"Total Forks: {stats.get('total_forks', 0)}", 5, y, WIDTH, 1)
    y += 14
    
    # Most starred repo
    most_starred = stats.get('most_starred', {})
    if most_starred:
        display.text("Most Starred:", 5, y, WIDTH, 1)
        y += 12
        repo_name = most_starred.get('name', 'Unknown')
        if len(repo_name) > 30:
            repo_name = repo_name[:27] + "..."
        display.text(f"• {repo_name}", 5, y, WIDTH, 1)
        y += 12
        stars = most_starred.get('stargazers_count', 0)
        display.text(f"  {stars} stars", 5, y, WIDTH, 1)
    
    draw_footer()
    display.update()


def draw_activity_page():
    """Draw activity page"""
    display.set_pen(15)
    display.clear()
    draw_header("Activity")
    
    activity = get_cached_page_data("activity") or CACHE.get("data", {}).get("activity", [])
    
    if not activity:
        display.set_pen(0)
        display.text("No activity data", 5, 50, WIDTH, 1)
        draw_footer()
        display.update()
        return
    
    display.set_pen(0)
    y = 28
    
    display.set_font("bitmap8")
    display.text("Recent Events", 5, y, WIDTH, 1)
    y += 16
    
    display.set_font("bitmap6")
    
    # Show recent events
    for i, event in enumerate(activity[:5]):  # Show up to 5 events
        if y > HEIGHT - 25:  # Leave space for footer
            break
        
        text = event.get('display', f"{event.get('action', '')} {event.get('repo_short', '')}")
        if len(text) > 40:
            text = text[:37] + "..."
        
        display.text(f"• {text}", 5, y, WIDTH, 1)
        y += 12
    
    draw_footer()
    display.update()


def draw_qr_page():
    """Draw QR code page"""
    display.set_pen(15)
    display.clear()
    draw_header("QR Code")
    
    if not HAS_QRCODE:
        display.set_pen(0)
        display.text("QR module not available", 5, 50, WIDTH, 1)
        display.text("Install qrcode library", 5, 65, WIDTH, 1)
        draw_footer()
        display.update()
        return
    
    # Get GitHub URL
    profile = CACHE.get("data", {}).get("profile", {})
    github_url = profile.get('html_url', f'https://github.com/{USERNAME}')
    
    # Generate QR code
    qr_code.set_text(github_url)
    
    # Draw QR code
    display.set_pen(15)
    w, h = qr_code.get_size()
    qr_size = min(80, (HEIGHT - 50) // h * h)  # Fit in available space
    module_size = qr_size // w
    qr_x = (WIDTH - qr_size) // 2
    qr_y = 30
    
    # White background
    display.rectangle(qr_x - 2, qr_y - 2, qr_size + 4, qr_size + 4)
    
    # Draw QR modules
    display.set_pen(0)
    for y in range(h):
        for x in range(w):
            if qr_code.get_module(x, y):
                px = qr_x + x * module_size
                py = qr_y + y * module_size
                display.rectangle(px, py, module_size, module_size)
    
    # GitHub URL text
    display.set_font("bitmap6")
    url_text = github_url.replace('https://', '')
    url_width = display.measure_text(url_text, 1)
    display.text(url_text, (WIDTH - url_width) // 2, HEIGHT - 25, WIDTH, 1)
    
    draw_footer()
    display.update()


def draw_current_page():
    """Draw the current page"""
    page_name = PAGES[CURRENT_PAGE]
    
    if page_name == "overview":
        draw_overview_page()
    elif page_name == "stats":
        draw_stats_page()
    elif page_name == "activity":
        draw_activity_page()
    elif page_name == "qr":
        draw_qr_page()


def handle_buttons():
    """Handle button presses with proper debouncing"""
    global CURRENT_PAGE
    
    if display.pressed(badger2040.BUTTON_UP):
        CURRENT_PAGE = (CURRENT_PAGE - 1) % len(PAGES)
        print(f"Page up: {PAGES[CURRENT_PAGE]}")
        draw_current_page()
        time.sleep(0.2)  # Debounce
        
    elif display.pressed(badger2040.BUTTON_DOWN):
        CURRENT_PAGE = (CURRENT_PAGE + 1) % len(PAGES)
        print(f"Page down: {PAGES[CURRENT_PAGE]}")
        draw_current_page()
        time.sleep(0.2)  # Debounce
        
    elif display.pressed(badger2040.BUTTON_A):
        print("Manual update requested")
        update_data()
        draw_current_page()
        time.sleep(0.3)  # Longer debounce for update
        
    elif display.pressed(badger2040.BUTTON_B):
        print(f"Reloading page from cache: {PAGES[CURRENT_PAGE]}")
        draw_current_page()
        time.sleep(0.2)  # Debounce
        
    elif display.pressed(badger2040.BUTTON_C):
        # Show cache info
        display.set_pen(15)
        display.clear()
        display.set_pen(0)
        display.set_font("bitmap8")
        display.text("Cache Status", 5, 30, WIDTH, 1)
        display.set_font("bitmap6")
        display.text(f"Pages cached: {len(CACHE['pages'])}", 5, 50, WIDTH, 1)
        display.text(f"Updates: {CACHE['update_count']}", 5, 65, WIDTH, 1)
        if CACHE["last_update"]:
            age = int((time.time() - CACHE["last_update"]) / 60)
            display.text(f"Last update: {age}m ago", 5, 80, WIDTH, 1)
        display.text("Press any button to return", 5, HEIGHT - 15, WIDTH, 1)
        display.update()
        
        # Wait for button release and press
        while display.pressed(badger2040.BUTTON_C):
            time.sleep(0.1)
        while not (display.pressed(badger2040.BUTTON_A) or display.pressed(badger2040.BUTTON_B) or 
                  display.pressed(badger2040.BUTTON_C) or display.pressed(badger2040.BUTTON_UP) or 
                  display.pressed(badger2040.BUTTON_DOWN)):
            time.sleep(0.1)
        
        draw_current_page()
        time.sleep(0.2)


def main():
    """Main application loop"""
    print("Starting GitHub Actions Badge...")
    
    # Show startup screen
    display.set_pen(15)
    display.clear()
    display.set_pen(0)
    display.set_font("bitmap8")
    display.text("GitHub Badge", 5, 30, WIDTH, 1)
    display.set_font("bitmap6")
    display.text("GitHub Actions Version", 5, 50, WIDTH, 1)
    display.text("Loading...", 5, 65, WIDTH, 1)
    display.update()
    
    # Initial data fetch
    if not CACHE["data"]:
        print("Initial data fetch...")
        if not fetch_badge_data():
            print("Using demo data for first run")
            CACHE["data"] = {
                "profile": {"username": USERNAME, "public_repos": 0, "followers": 0},
                "stats": {"total_stars": 0, "total_forks": 0},
                "activity": [],
                "meta": {"source": "demo"}
            }
    
    # Draw initial page
    draw_current_page()
    
    # Main loop
    try:
        while True:
            # Auto-update check
            if time.time() - CACHE["last_update"] > UPDATE_INTERVAL:
                print("Auto-update triggered")
                update_data()
                draw_current_page()
            
            # Handle button input
            handle_buttons()
            
            # Small delay to prevent excessive CPU usage
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("Shutting down...")
    except Exception as e:
        print(f"Error in main loop: {e}")
        # Show error screen
        display.set_pen(15)
        display.clear()
        display.set_pen(0)
        display.text("Error occurred", 5, 40, WIDTH, 1)
        display.text("Power cycle to restart", 5, 55, WIDTH, 1)
        display.update()
    finally:
        display.halt()


if __name__ == "__main__":
    main()
