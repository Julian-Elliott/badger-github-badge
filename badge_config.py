# Configuration for GitHub Badge
# Edit these values to customize your badge

# Your GitHub username (required)
GITHUB_USERNAME = "Julian-Elliott"

# Repository name where badge data is hosted (required)
# This should be the name of your fork of badger-github-badge
BADGE_REPO_NAME = "badger-github-badge"

# Update intervals (in seconds)
BADGE_UPDATE_INTERVAL = 1800  # 30 minutes
BATTERY_CHECK_INTERVAL = 300  # 5 minutes

# Display options
SHOW_BATTERY_ICON = True
SHOW_WIFI_ICON = True
SHOW_UPDATE_TIME = True

# QR Code settings
QR_CODE_SIZE = 3  # Size multiplier for QR code
QR_CODE_BORDER = 1  # Border size around QR code

# Network settings
REQUEST_TIMEOUT = 10  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds between retries

# Badge layout options
COMPACT_MODE = False  # Use more compact layout for smaller text
DARK_MODE = False     # Invert colors (experimental)

# Debug options
DEBUG_MODE = False    # Enable debug output
VERBOSE_ERRORS = True # Show detailed error messages
