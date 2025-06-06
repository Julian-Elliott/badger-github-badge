# GitHub Badge for Badger 2040 W

A beautiful e-ink badge that displays your GitHub profile stats on a Badger 2040 W device.

## 🎯 Features

- **Real-time GitHub Stats**: Shows your repos, followers, stars, and more
- **Multiple Pages**: Navigate through overview, API info, and QR code pages
- **QR Code**: Display a QR code linking to your GitHub profile
- **Auto-refresh**: Updates data every 10 minutes
- **Button Navigation**: Use A/B buttons to navigate, C to refresh
- **WiFi Enabled**: Connects to your network and fetches live data
- **Rate Limit Friendly**: Handles GitHub API rate limits gracefully

## 📱 Display Pages

1. **Overview**: Your name, username, repos, followers, stars
2. **API Test**: Connection status and data verification  
3. **API Info**: Technical details about data sources
4. **QR Code**: Scannable link to your GitHub profile

## 🛠️ Hardware Required

- [Badger 2040 W](https://shop.pimoroni.com/products/badger-2040-w) (WiFi-enabled version)
- MicroUSB cable for programming
- WiFi network access

## 🚀 Quick Start

### 1. Flash Firmware

Flash the latest Pimoroni MicroPython firmware to your Badger 2040 W.

### 2. Configure WiFi

1. Copy `WIFI_CONFIG.py.template` to `WIFI_CONFIG.py`
2. Edit with your WiFi credentials:
   ```python
   SSID = "YourWiFiNetwork"
   PSK = "YourPassword"
   COUNTRY = "US"  # Your country code
   ```

### 3. Upload Files

Upload the required files to your Badger 2040 W:
- `main.py` - Main badge application
- `badge_config.py` - Configuration file
- `WIFI_CONFIG.py` - Your WiFi credentials
- `install_qrcode.py` - QR code module installer

### 4. Install QR Module

Run the QR code installer:
```python
import install_qrcode
```

### 5. Configure Your Username

Edit `badge_config.py` and set your GitHub username:
```python
GITHUB_USERNAME = "your-username"
```

### 6. Run the Badge

```python
import main
```

## 🔧 Development Workflow

This project includes a complete development environment:

### VS Code Integration

- Predefined tasks for upload, test, and WiFi setup
- MicroPython language support
- Integrated terminal commands

### Makefile Commands

```bash
make upload          # Upload all files
make run             # Run the badge application  
make test-connection # Test WiFi and functionality
make setup-wifi      # Configure WiFi credentials
make install-qr      # Install QR code module
make clean           # Clean temporary files
make help            # Show all available commands
```

### Testing Tools

- `test_connection.py` - Comprehensive connectivity testing
- `monitor_badge.py` - Real-time device monitoring
- `robust_uploader.py` - Reliable file transfer

## 📊 GitHub Pages Integration

For production use, this badge can fetch data from GitHub Pages:

1. Enable GitHub Pages in your repository settings
2. The GitHub Actions workflow will automatically:
   - Fetch your GitHub data every 6 hours
   - Generate optimized badge data files
   - Deploy to GitHub Pages

## 🎛️ Configuration Options

Edit `badge_config.py` to customize:

```python
# Update intervals
BADGE_UPDATE_INTERVAL = 1800  # 30 minutes
BATTERY_CHECK_INTERVAL = 300  # 5 minutes

# Display options
SHOW_BATTERY_ICON = True
SHOW_WIFI_ICON = True
COMPACT_MODE = False

# Network settings
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3
```

## 🔘 Button Controls

- **Button A**: Previous page
- **Button B**: Next page  
- **Button C**: Refresh data manually
- **Up/Down**: (Reserved for future features)

## 🌐 Network Requirements

- WiFi network with internet access
- Access to `api.github.com` (HTTPS)
- Handles rate limiting automatically

## 🔍 Troubleshooting

### WiFi Issues
```bash
make setup-wifi      # Reconfigure WiFi
make test-connection # Test connectivity
```

### Display Issues  
```bash
make upload && make install-qr  # Reinstall everything
```

### API Issues
- Check your GitHub username in `badge_config.py`
- Verify internet connectivity
- GitHub API has rate limits (60 requests/hour without token)

## 📁 Project Structure

```
badger-github-badge/
├── main.py                 # Main badge application
├── badge_config.py         # Configuration
├── WIFI_CONFIG.py          # WiFi credentials (create from template)
├── install_qrcode.py       # QR module installer
├── Makefile               # Build automation
├── .vscode/
│   └── tasks.json         # VS Code integration
├── scripts/
│   └── generate_badge_data.py  # GitHub data generator
└── .github/workflows/
    └── update-badge-data.yml   # Auto-update workflow
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on actual hardware
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- [Pimoroni](https://pimoroni.com) for the excellent Badger 2040 W hardware
- GitHub API for providing comprehensive profile data
- MicroPython community for the fantastic ecosystem

## 📸 Gallery

*Add photos of your badge in action!*

---

**Happy badging! 🦡✨**
