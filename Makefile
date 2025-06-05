# Badger 2040 W GitHub Badge Development Makefile

# Configuration
SHELL := /bin/bash
.DEFAULT_GOAL := help

# Device detection (macOS/Linux patterns)
DEVICE_PATTERNS := /dev/tty.usbmodem* /dev/ttyACM* /dev/ttyUSB*
DEVICE := $(shell ls $(DEVICE_PATTERNS) 2>/dev/null | head -1)
BAUD_RATE := 115200

# Project files
MAIN_FILE := main.py
CONFIG_FILE := badge_config.py
WIFI_CONFIG := WIFI_CONFIG.py
QR_INSTALLER := install_qrcode.py
UPLOAD_SCRIPT := upload_and_run.py
RESET_SCRIPT := reset_and_upload.py

# Firmware
FIRMWARE_DIR := ../firmware
FIRMWARE_FILE := $(shell ls ../firmware/pimoroni-badger2040w-*.uf2 2>/dev/null | head -1)

# Upload tools (in order of preference)
UPLOAD_TOOLS := mpremote ampy rshell
UPLOAD_TOOL := $(shell for tool in $(UPLOAD_TOOLS); do \
	command -v $$tool >/dev/null 2>&1 && echo $$tool && break; \
done)

.PHONY: help check-device check-tools install-tools setup-wifi upload run clean flash-firmware test test-connection status

help: ## Show available targets
	@echo "🦡 Badger 2040 W GitHub Badge Makefile"
	@echo "====================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'
	@echo ""
	@echo "Workflow:"
	@echo "  1. make install-tools    # Install required Python tools"
	@echo "  2. make flash-firmware   # Flash Badger firmware (if needed)"
	@echo "  3. make setup-wifi       # Configure WiFi credentials"
	@echo "  4. make dev-setup        # Upload all files and QR installer"
	@echo "  5. make test-connection  # Test WiFi and badge functionality"
	@echo "  6. make dev-cycle        # Quick upload + run cycle"

status: ## Show current project status
	@echo "🔍 Project Status"
	@echo "================"
	@echo "Device: $(if $(DEVICE),✅ $(DEVICE),❌ Not found)"
	@echo "Upload tool: $(if $(UPLOAD_TOOL),✅ $(UPLOAD_TOOL),❌ None available)"
	@echo "Firmware: $(if $(FIRMWARE_FILE),✅ $(notdir $(FIRMWARE_FILE)),❌ Not found)"
	@echo ""
	@echo "Files:"
	@echo "  Main: $(if $(wildcard $(MAIN_FILE)),✅,❌) $(MAIN_FILE)"
	@echo "  Config: $(if $(wildcard $(CONFIG_FILE)),✅,❌) $(CONFIG_FILE)"
	@echo "  WiFi Config: $(if $(wildcard $(WIFI_CONFIG)),$(if $(shell grep -q 'YOUR_WIFI' $(WIFI_CONFIG) 2>/dev/null && echo "unconfigured"),⚠️  Needs setup,✅),❌) $(WIFI_CONFIG)"
	@echo "  QR Installer: $(if $(wildcard $(QR_INSTALLER)),✅,❌) $(QR_INSTALLER)"

check-device: ## Check if Pico device is connected
	@if [ -z "$(DEVICE)" ]; then \
		echo "❌ Error: No Pico device found"; \
		echo "   Expected patterns: $(DEVICE_PATTERNS)"; \
		echo "   Make sure:"; \
		echo "   - Device is connected via USB"; \
		echo "   - Device is NOT in bootloader mode"; \
		echo "   - Proper firmware is installed"; \
		exit 1; \
	fi
	@echo "✅ Found device: $(DEVICE)"

check-tools: ## Check if upload tools are available
	@if [ -z "$(UPLOAD_TOOL)" ]; then \
		echo "❌ Error: No upload tools found"; \
		echo "   Available tools: $(UPLOAD_TOOLS)"; \
		echo "   Run 'make install-tools' to install"; \
		exit 1; \
	fi
	@echo "✅ Upload tool: $(UPLOAD_TOOL)"

install-tools: ## Install required Python tools
	@echo "📦 Installing MicroPython tools..."
	pip3 install --upgrade pip
	pip3 install mpremote adafruit-ampy rshell
	@echo "✅ Tools installed successfully"
	@echo ""
	@echo "Available tools:"
	@for tool in $(UPLOAD_TOOLS); do \
		if command -v $$tool >/dev/null 2>&1; then \
			echo "  ✅ $$tool"; \
		else \
			echo "  ❌ $$tool"; \
		fi; \
	done

setup-wifi: ## Configure WiFi credentials
	@echo "📶 WiFi Configuration Setup"
	@echo "==========================="
	@if [ ! -f "$(WIFI_CONFIG)" ]; then \
		echo "❌ $(WIFI_CONFIG) not found"; \
		echo "   Run this target again to create it"; \
		exit 1; \
	fi
	@if grep -q "YOUR_WIFI" $(WIFI_CONFIG); then \
		echo "⚠️  WiFi configuration needs setup"; \
		echo ""; \
		echo "Please edit $(WIFI_CONFIG) and replace:"; \
		echo "  - YOUR_WIFI_NETWORK_NAME with your WiFi SSID"; \
		echo "  - YOUR_WIFI_PASSWORD with your WiFi password"; \
		echo "  - Country code if needed (currently: US)"; \
		echo ""; \
		echo "Example:"; \
		echo "  SSID = \"MyHomeWiFi\""; \
		echo "  PSK = \"mypassword123\""; \
		echo "  COUNTRY = \"US\""; \
		echo ""; \
		$${EDITOR:-nano} $(WIFI_CONFIG); \
	else \
		echo "✅ WiFi configuration appears to be set up"; \
		echo "   SSID: $$(grep '^SSID' $(WIFI_CONFIG) | cut -d'=' -f2 | tr -d ' \"')"; \
		echo "   Country: $$(grep '^COUNTRY' $(WIFI_CONFIG) | cut -d'=' -f2 | tr -d ' \"')"; \
	fi

# Upload using mpremote (preferred)
upload-mpremote: check-device
	@echo "📤 Uploading files using mpremote..."
	mpremote connect $(DEVICE) fs cp $(MAIN_FILE) :
	mpremote connect $(DEVICE) fs cp $(CONFIG_FILE) :
	@if [ -f "$(WIFI_CONFIG)" ] && ! grep -q "YOUR_WIFI" $(WIFI_CONFIG); then \
		echo "📶 Uploading WiFi configuration..."; \
		mpremote connect $(DEVICE) fs cp $(WIFI_CONFIG) :; \
	fi
	@echo "✅ Files uploaded successfully"

# Upload using ampy (fallback)
upload-ampy: check-device
	@echo "📤 Uploading files using ampy..."
	ampy --port $(DEVICE) --baud $(BAUD_RATE) put $(MAIN_FILE)
	ampy --port $(DEVICE) --baud $(BAUD_RATE) put $(CONFIG_FILE)
	@if [ -f "$(WIFI_CONFIG)" ] && ! grep -q "YOUR_WIFI" $(WIFI_CONFIG); then \
		echo "📶 Uploading WiFi configuration..."; \
		ampy --port $(DEVICE) --baud $(BAUD_RATE) put $(WIFI_CONFIG); \
	fi
	@echo "✅ Files uploaded successfully"

# Upload using rshell (fallback)
upload-rshell: check-device
	@echo "📤 Uploading files using rshell..."
	rshell --port $(DEVICE) --baud $(BAUD_RATE) \
		cp $(MAIN_FILE) /pyboard/ \
		cp $(CONFIG_FILE) /pyboard/
	@if [ -f "$(WIFI_CONFIG)" ] && ! grep -q "YOUR_WIFI" $(WIFI_CONFIG); then \
		echo "📶 Uploading WiFi configuration..."; \
		rshell --port $(DEVICE) --baud $(BAUD_RATE) cp $(WIFI_CONFIG) /pyboard/; \
	fi
	@echo "✅ Files uploaded successfully"

# Upload using Python script (last resort)
upload-python: check-device
	@echo "📤 Uploading files using robust Python script..."
	python3 robust_uploader.py

upload: check-device ## Upload main files to Pico
	@echo "📤 Using robust Python uploader (most reliable)..."
	@python3 robust_uploader.py

upload-qr: check-device check-tools ## Upload QR code installer
	@echo "📤 Uploading QR code installer..."
	@case "$(UPLOAD_TOOL)" in \
		mpremote) mpremote connect $(DEVICE) fs cp $(QR_INSTALLER) : ;; \
		ampy) ampy --port $(DEVICE) --baud $(BAUD_RATE) put $(QR_INSTALLER) ;; \
		rshell) rshell --port $(DEVICE) --baud $(BAUD_RATE) cp $(QR_INSTALLER) /pyboard/ ;; \
	esac
	@echo "✅ QR installer uploaded"

run: ## Run the main application
	@echo "🚀 Running GitHub badge application..."
	@python3 run_app.py

install-qr: ## Install QR code module on device
	@echo "📦 Installing QR code module..."
	@python3 install_qr_module.py

soft-reset: check-device ## Soft reset the device
	@echo "🔄 Soft resetting device..."
	@case "$(UPLOAD_TOOL)" in \
		mpremote) mpremote connect $(DEVICE) exec "import machine; machine.soft_reset()" ;; \
		ampy) echo "import machine; machine.soft_reset()" | ampy --port $(DEVICE) --baud $(BAUD_RATE) run - ;; \
		*) echo "⚠️  Manual reset required" ;; \
	esac

hard-reset: check-device ## Hard reset device using Python script
	@echo "🔄 Hard resetting device..."
	@if [ -f "$(RESET_SCRIPT)" ]; then \
		python3 $(RESET_SCRIPT); \
	else \
		echo "⚠️  Reset script not found - manual reset required"; \
	fi

clean: check-device ## Remove uploaded files from Pico
	@echo "🧹 Cleaning Pico filesystem..."
	@case "$(UPLOAD_TOOL)" in \
		mpremote) \
			mpremote connect $(DEVICE) fs rm main.py 2>/dev/null || true; \
			mpremote connect $(DEVICE) fs rm $(CONFIG_FILE) 2>/dev/null || true; \
			mpremote connect $(DEVICE) fs rm $(QR_INSTALLER) 2>/dev/null || true ;; \
		ampy) \
			ampy --port $(DEVICE) --baud $(BAUD_RATE) rm main.py 2>/dev/null || true; \
			ampy --port $(DEVICE) --baud $(BAUD_RATE) rm $(CONFIG_FILE) 2>/dev/null || true; \
			ampy --port $(DEVICE) --baud $(BAUD_RATE) rm $(QR_INSTALLER) 2>/dev/null || true ;; \
		*) echo "⚠️  Manual cleanup required" ;; \
	esac
	@echo "✅ Cleanup complete"

list-files: check-device ## List files on Pico
	@echo "📋 Files on device:"
	@case "$(UPLOAD_TOOL)" in \
		mpremote) mpremote connect $(DEVICE) fs ls ;; \
		ampy) ampy --port $(DEVICE) --baud $(BAUD_RATE) ls ;; \
		rshell) rshell --port $(DEVICE) --baud $(BAUD_RATE) ls /pyboard ;; \
		*) echo "⚠️  Manual file listing required" ;; \
	esac

repl: check-device ## Open REPL console
	@echo "🔗 Opening REPL console (Ctrl+C then Ctrl+X to exit)..."
	@case "$(UPLOAD_TOOL)" in \
		mpremote) mpremote connect $(DEVICE) repl ;; \
		rshell) rshell --port $(DEVICE) --baud $(BAUD_RATE) repl ;; \
		*) echo "⚠️  Use screen $(DEVICE) $(BAUD_RATE) for REPL" ;; \
	esac

flash-firmware: ## Flash Pimoroni Badger 2040 W firmware
	@if [ -z "$(FIRMWARE_FILE)" ]; then \
		echo "❌ Error: No firmware file found"; \
		echo "   Expected: ../pimoroni-badger2040w-*.uf2"; \
		exit 1; \
	fi
	@echo "⚠️  Put device in bootloader mode:"
	@echo "   1. Hold BOOTSEL button on Pico W"
	@echo "   2. Press RESET button on Badger"
	@echo "   3. Release BOOTSEL when RPI-RP2 drive appears"
	@echo ""
	@read -p "Press Enter when device is in bootloader mode..."
	@echo "🔄 Flashing firmware: $(notdir $(FIRMWARE_FILE))"
	@if [ -d "/Volumes/RPI-RP2" ]; then \
		cp "$(FIRMWARE_FILE)" "/Volumes/RPI-RP2/" && \
		echo "✅ Firmware flashed successfully (macOS)"; \
	elif [ -d "/media/$(USER)/RPI-RP2" ]; then \
		cp "$(FIRMWARE_FILE)" "/media/$(USER)/RPI-RP2/" && \
		echo "✅ Firmware flashed successfully (Linux)"; \
	elif [ -d "/mnt/RPI-RP2" ]; then \
		cp "$(FIRMWARE_FILE)" "/mnt/RPI-RP2/" && \
		echo "✅ Firmware flashed successfully (Linux alt)"; \
	else \
		echo "❌ Error: RPI-RP2 drive not found"; \
		echo "   Make sure device is in bootloader mode"; \
		exit 1; \
	fi
	@echo "⏳ Waiting for device to restart..."
	@sleep 3
	@echo "✅ Device should now be ready for development"

test: check-device check-tools ## Run basic device tests
	@echo "🧪 Testing device communication..."
	@case "$(UPLOAD_TOOL)" in \
		mpremote) mpremote connect $(DEVICE) exec "print('Hello from Badger 2040 W!')" ;; \
		ampy) echo "print('Hello from Badger 2040 W!')" | ampy --port $(DEVICE) --baud $(BAUD_RATE) run - ;; \
		*) echo "⚠️  Manual test required" ;; \
	esac
	@echo "✅ Device communication OK"

test-connection: check-device ## Test WiFi connection and badge functionality
	@echo "🌐 Testing WiFi connection and badge functionality..."
	python3 test_connection.py

test-modules: check-device check-tools ## Test required modules
	@echo "🧪 Testing MicroPython modules..."
	@case "$(UPLOAD_TOOL)" in \
		mpremote) \
			mpremote connect $(DEVICE) exec "import badger2040; print('✅ badger2040 module OK')" || echo "❌ badger2040 module missing"; \
			mpremote connect $(DEVICE) exec "import urequests; print('✅ urequests module OK')" || echo "❌ urequests module missing"; \
			mpremote connect $(DEVICE) exec "import network; print('✅ network module OK')" || echo "❌ network module missing" ;; \
		*) echo "⚠️  Manual module testing required" ;; \
	esac

check-firmware: check-device check-tools ## Verify firmware version
	@echo "🔍 Checking firmware version..."
	@case "$(UPLOAD_TOOL)" in \
		mpremote) mpremote connect $(DEVICE) exec "import sys; print('Implementation:', sys.implementation); print('Version:', sys.version)" ;; \
		*) echo "⚠️  Manual firmware check required" ;; \
	esac

monitor: check-device ## Monitor device output
	@echo "👀 Monitoring device output..."
	@case "$(UPLOAD_TOOL)" in \
		mpremote) mpremote connect $(DEVICE) exec "exec(open('main.py').read())" ;; \
		*) echo "⚠️  Manual monitoring required" ;; \
	esac

# Development workflow targets
dev-setup: upload upload-qr install-qr ## Complete development setup
	@echo "🎉 Development environment ready!"
	@echo "   Files uploaded: $(MAIN_FILE), $(CONFIG_FILE), $(QR_INSTALLER)"
	@echo "   QR code module installed"
	@echo "   Ready to run: make run"

dev-cycle: upload run ## Quick development cycle (upload + run)

quick-test: upload test ## Upload and test basic functionality

# Convenience targets for different scenarios
first-time: check-tools flash-firmware dev-setup ## Complete first-time setup
	@echo "🏁 First-time setup complete!"

retry-upload: soft-reset upload ## Retry upload after soft reset

force-upload: hard-reset upload ## Force upload after hard reset

# Help for common issues
troubleshoot: ## Show troubleshooting help
	@echo "🔧 Troubleshooting Guide"
	@echo "======================"
	@echo ""
	@echo "Device not found:"
	@echo "  - Check USB connection"
	@echo "  - Ensure device is not in bootloader mode"
	@echo "  - Try different USB port/cable"
	@echo ""
	@echo "Upload fails:"
	@echo "  - Run: make soft-reset && make upload"
	@echo "  - Try: make hard-reset && make upload"
	@echo "  - Check device permissions (Linux: sudo usermod -a -G dialout $$USER)"
	@echo ""
	@echo "Firmware issues:"
	@echo "  - Ensure Pimoroni Badger 2040 W firmware is installed"
	@echo "  - Run: make flash-firmware"
	@echo "  - Verify with: make check-firmware"
	@echo ""
	@echo "VS Code integration:"
	@echo "  - Install extensions: MicroPico, Raspberry Pi Pico"
	@echo "  - Configure device path in extension settings"
	@echo "  - Use VS Code tasks: Ctrl+Shift+P > Tasks: Run Task"
