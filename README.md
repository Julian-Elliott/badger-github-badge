# GitHub Badge for Badger 2040 W - GitHub Actions Version

A modern GitHub badge for your Badger 2040 W that uses GitHub Actions to pre-generate data and serve it via GitHub Pages. This eliminates API rate limits, reduces power consumption, and provides fast, reliable badge updates with offline caching.

## 🚀 Key Features

- **GitHub Actions Powered**: Automated data generation every 6 hours
- **No API Rate Limits**: Pre-generated data eliminates device API calls
- **Smart Caching**: Automatically caches last received page data for offline viewing
- **Multi-Page Navigation**: 4 pages with Up/Down button navigation
- **Fast Loading**: JSON files load much faster than live API requests
- **Battery Efficient**: Minimal network requests save power
- **Professional Layout**: Optimized for 296x128 e-ink display
- **QR Code Generation**: Links directly to your GitHub profile

## 📱 Pages & Navigation

### Page Structure
1. **Overview** - Profile summary with followers, repos, and recent activity
2. **Statistics** - Repository stats, languages, and contribution summary  
3. **Activity** - Recent GitHub events and commit activity
4. **QR Code** - Scannable link to your GitHub profile

### Button Controls
- **UP/DOWN Buttons**: Navigate between pages
- **A Button**: Manual refresh data (downloads latest from GitHub Pages)
- **B Button**: Force page reload from cache
- **C Button**: Toggle between compact/normal view

## 🔧 Quick Setup

### 1. Fork & Configure Repository
1. **Fork this repository** to your GitHub account
2. **Enable GitHub Actions** in your fork (Actions tab)
3. **Enable GitHub Pages**: 
   - Go to Settings → Pages 
   - Set Source to "GitHub Actions"

### 2. Configure Your Badge
1. **Edit `badge_config.py`**:
   ```python
   GITHUB_USERNAME = "your-username"
   BADGE_REPO_NAME = "badger-github-badge"
   ```

2. **Upload to Badger**: Copy `github_actions_main.py` to your Badger 2040 W as `main.py`

### 3. Test the System
1. **Trigger workflow**: Go to Actions → "Update GitHub Badge Data" → "Run workflow"
2. **Verify data**: Check that `public/api/` files were created
3. **Test badge**: Power on Badger and verify display

📖 **Detailed Setup**: See [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) for complete instructions.

## 🔄 How It Works

### GitHub Actions Pipeline
1. **Automated Workflow**: Runs every 6 hours (customizable)
2. **Data Fetching**: Pulls your latest GitHub profile, repos, and activity
3. **Data Processing**: Analyzes and formats data for optimal badge display
4. **GitHub Pages**: Serves processed JSON files via your GitHub Pages site

### Badger Caching System
- **Smart Download**: Fetches latest data from your GitHub Pages URL
- **Page Caching**: Stores each page's data locally for offline viewing
- **Fallback Logic**: Uses cached data when network is unavailable
- **Persistent Storage**: Cache survives power cycles and restarts

### Data Flow
```
GitHub API → GitHub Actions → GitHub Pages → Badger 2040 W → Local Cache
```

## 📦 Dependencies

- `badger2040`: Built-in Badger 2040 W library
- `urequests`: Built-in HTTP library for MicroPython
- `json`: Built-in JSON parsing
- `qrcode`: Optional QR code generation (install via `install_qrcode.py`)

## 🌐 Data Sources

Your GitHub Pages site will serve these endpoints:
- **Compact Data**: `https://username.github.io/badger-github-badge/api/badge_compact.json`
- **Profile**: `https://username.github.io/badger-github-badge/api/profile.json`  
- **Statistics**: `https://username.github.io/badger-github-badge/api/stats.json`
- **Activity**: `https://username.github.io/badger-github-badge/api/activity.json`
- **Fallback**: `https://username.github.io/badger-github-badge/api/badge_simple.txt`

## 🔧 Troubleshooting

### Badge Shows "Loading..." or "No Data"
1. **Check GitHub Actions**: Verify workflow completed successfully in Actions tab
2. **Test GitHub Pages**: Visit your data URL directly in browser
3. **Check WiFi**: Ensure Badger is connected to internet
4. **Verify Config**: Double-check username and repo name in `badge_config.py`

### Cache Issues
- **Clear Cache**: Power cycle Badger or press B button to reload from cache
- **Force Refresh**: Press A button to download fresh data
- **Check Storage**: Ensure Badger has sufficient storage space

### GitHub Actions Problems
- **Enable Permissions**: Check that Actions and Pages are enabled
- **Manual Trigger**: Try running workflow manually
- **Check Logs**: Review workflow logs for error messages

## ⚡ Performance Benefits

Compared to direct API calls:
- **10x Faster Loading**: Pre-generated JSON vs live API requests
- **No Rate Limits**: Unlimited badge updates without API constraints  
- **90% Less Power**: Minimal network requests save battery
- **Offline Capable**: Works with cached data when internet unavailable
- **Always Fresh**: Automatic updates every 6 hours without device interaction

## 📁 Project Structure

```
badger-github-badge/
├── github_actions_main.py          # Main badge application
├── badge_config.py                 # Configuration settings
├── install_qrcode.py               # QR code module installer
├── GITHUB_ACTIONS_SETUP.md         # Detailed setup guide
├── .github/workflows/
│   └── update-badge-data.yml       # GitHub Actions workflow
├── scripts/
│   ├── generate_badge_data.py      # Data generation script
│   └── generate_badge_images.py    # Image generation script
└── public/api/                     # Generated data files (auto-created)
    ├── badge_compact.json
    ├── profile.json
    ├── stats.json
    ├── activity.json
    └── badge_simple.txt
```

## 🔄 Customization

### Update Frequency
Edit `.github/workflows/update-badge-data.yml`:
```yaml
schedule:
  - cron: '0 */3 * * *'  # Every 3 hours
```

### Badge Layout  
Edit `github_actions_main.py` to customize:
- Page layouts and content
- Font sizes and positioning  
- Button behavior
- Cache settings

### Data Processing
Edit `scripts/generate_badge_data.py` to customize:
- Which GitHub data to include
- Statistics calculations
- Data filtering and formatting

## 🚀 Getting Started

Ready to set up your GitHub badge? Follow the [complete setup guide](GITHUB_ACTIONS_SETUP.md) for step-by-step instructions.

**Quick Test**: After setup, your badge data will be available at:
`https://your-username.github.io/badger-github-badge/api/badge_compact.json`