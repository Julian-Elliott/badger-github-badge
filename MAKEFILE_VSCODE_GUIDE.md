# Makefile and VS Code Integration Guide for Badger 2040 W Development

This guide explains how Makefiles and VS Code extensions should communicate with the Badger 2040 W (Pico W) for effective development workflow.

## Table of Contents
- [Overview](#overview)
- [VS Code Extensions](#vs-code-extensions)
- [Makefile Best Practices](#makefile-best-practices)
- [Integration Workflow](#integration-workflow)
- [Project Structure](#project-structure)
- [Example Implementation](#example-implementation)
- [Troubleshooting](#troubleshooting)

## Overview

The Badger 2040 W runs MicroPython on the Raspberry Pi Pico W platform. Development involves:
- **Source Code**: Python files for the badge application
- **Firmware**: Custom Pimoroni Badger 2040 W MicroPython firmware
- **File Transfer**: Moving files to/from the device via USB serial
- **Build Automation**: Using Makefiles to automate common tasks

## VS Code Extensions

### Essential Extensions

```vscode-extensions
paulober.pico-w-go,raspberry-pi.raspberry-pi-pico
```

#### MicroPico (paulober.pico-w-go)
- **Auto-completion**: IntelliSense for MicroPython modules
- **Remote workspace**: Direct file management on Pico
- **REPL console**: Interactive Python shell
- **File synchronization**: Upload/download files seamlessly

#### Raspberry Pi Pico (raspberry-pi.raspberry-pi-pico)
- **Official support**: Created by Raspberry Pi Foundation
- **Project templates**: Quick project setup
- **SDK integration**: For C/C++ development (not needed for MicroPython)
- **Debugging support**: Hardware debugging capabilities

### Additional Helpful Extensions

```vscode-extensions
ms-python.python,platformio.platformio-ide,daleka.mpytools
```

## Makefile Best Practices

### Core Principles

1. **Device Detection**: Automatically find connected Pico devices
2. **Firmware Management**: Install/update firmware as needed
3. **File Transfer**: Reliable upload/download of Python files
4. **Error Handling**: Graceful failure with informative messages
5. **Cross-Platform**: Work on macOS, Linux, and Windows

### Key Variables

```makefile
# Device detection (adjust patterns for your OS)
DEVICE_PATTERNS := /dev/tty.usbmodem* /dev/ttyACM*
DEVICE := $(shell ls $(DEVICE_PATTERNS) 2>/dev/null | head -1)
BAUD_RATE := 115200

# Project structure
SRC_DIR := .
MAIN_FILE := main.py
CONFIG_FILE := badge_config.py
FIRMWARE_DIR := firmware
```

### Essential Targets

```makefile
.PHONY: help check-device upload run clean flash-firmware

help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

check-device: ## Check if Pico device is connected
	@if [ -z "$(DEVICE)" ]; then \
		echo "Error: No Pico device found"; \
		echo "Expected device patterns: $(DEVICE_PATTERNS)"; \
		exit 1; \
	fi
	@echo "Found device: $(DEVICE)"

upload: check-device ## Upload main files to Pico
	@echo "Uploading files to $(DEVICE)..."
	# Implementation depends on chosen tool (ampy, rshell, etc.)

run: upload ## Upload and run the application
	@echo "Running application..."
	# Send commands to execute main.py

clean: check-device ## Clean files from Pico
	@echo "Cleaning Pico filesystem..."
	# Remove uploaded files

flash-firmware: ## Flash Pimoroni Badger 2040 W firmware
	@echo "Put device in bootloader mode and run this target"
	# Copy .uf2 file to mounted drive
```

## Integration Workflow

### 1. VS Code Integration

VS Code extensions communicate with the Pico through:
- **Serial Communication**: Direct REPL access via USB
- **File Transfer Protocols**: Using tools like `ampy`, `rshell`, or `mpremote`
- **Debugging Interface**: Real-time code execution and inspection

### 2. Makefile Communication

Makefiles should integrate with VS Code by:
- **Task Integration**: Define VS Code tasks that call Makefile targets
- **Terminal Integration**: Use VS Code's integrated terminal
- **Problem Matchers**: Parse build output for error highlighting

### 3. File Transfer Methods

#### Option A: ampy (Adafruit MicroPython Tool)
```makefile
upload-ampy: check-device
	ampy --port $(DEVICE) --baud $(BAUD_RATE) put $(MAIN_FILE)
	ampy --port $(DEVICE) --baud $(BAUD_RATE) put $(CONFIG_FILE)
```

#### Option B: rshell (Remote Shell)
```makefile
upload-rshell: check-device
	rshell --port $(DEVICE) --baud $(BAUD_RATE) \
		cp $(MAIN_FILE) /pyboard/ \
		cp $(CONFIG_FILE) /pyboard/
```

#### Option C: mpremote (Official MicroPython Tool)
```makefile
upload-mpremote: check-device
	mpremote connect $(DEVICE) fs cp $(MAIN_FILE) :
	mpremote connect $(DEVICE) fs cp $(CONFIG_FILE) :
```

### 4. VS Code Tasks Configuration

Create `.vscode/tasks.json`:
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Upload to Badger",
            "type": "shell",
            "command": "make",
            "args": ["upload"],
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            },
            "problemMatcher": []
        },
        {
            "label": "Flash Firmware",
            "type": "shell",
            "command": "make",
            "args": ["flash-firmware"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": true,
                "panel": "dedicated"
            }
        },
        {
            "label": "Run Application",
            "type": "shell",
            "command": "make",
            "args": ["run"],
            "group": "test",
            "dependsOn": "Upload to Badger"
        }
    ]
}
```

## Project Structure

```
badger-project/
├── Makefile                 # Build automation
├── main.py                  # Main application
├── badge_config.py          # Configuration
├── install_qrcode.py        # Module installer
├── firmware/                # Firmware files
│   └── pimoroni-badger2040w-*.uf2
├── .vscode/
│   ├── tasks.json          # VS Code tasks
│   ├── launch.json         # Debug configuration
│   └── settings.json       # Workspace settings
├── scripts/                # Helper scripts
│   ├── upload_files.py     # File transfer script
│   └── device_reset.py     # Device management
└── README.md               # Project documentation
```

## Example Implementation

### Complete Makefile

```makefile
# Badger 2040 W Development Makefile

# Configuration
SHELL := /bin/bash
.DEFAULT_GOAL := help

# Device detection (macOS/Linux)
DEVICE_PATTERNS := /dev/tty.usbmodem* /dev/ttyACM* /dev/ttyUSB*
DEVICE := $(shell ls $(DEVICE_PATTERNS) 2>/dev/null | head -1)
BAUD_RATE := 115200

# Project files
MAIN_FILE := main.py
CONFIG_FILE := badge_config.py
QR_INSTALLER := install_qrcode.py
FIRMWARE_FILE := firmware/pimoroni-badger2040w-*.uf2

# Tools
UPLOAD_TOOL := mpremote
# Alternative: ampy, rshell

.PHONY: help check-device install-tools upload run clean flash-firmware test

help: ## Show available targets
	@echo "Badger 2040 W Development Makefile"
	@echo "=================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

check-device: ## Check if Pico device is connected
	@if [ -z "$(DEVICE)" ]; then \
		echo "❌ Error: No Pico device found"; \
		echo "   Expected patterns: $(DEVICE_PATTERNS)"; \
		echo "   Make sure device is connected and not in bootloader mode"; \
		exit 1; \
	fi
	@echo "✅ Found device: $(DEVICE)"

install-tools: ## Install required Python tools
	@echo "Installing MicroPython tools..."
	pip install mpremote adafruit-ampy rshell
	@echo "✅ Tools installed"

upload: check-device ## Upload main files to Pico
	@echo "📤 Uploading files to $(DEVICE)..."
	@if command -v $(UPLOAD_TOOL) >/dev/null 2>&1; then \
		$(UPLOAD_TOOL) connect $(DEVICE) fs cp $(MAIN_FILE) : && \
		$(UPLOAD_TOOL) connect $(DEVICE) fs cp $(CONFIG_FILE) : && \
		echo "✅ Files uploaded successfully"; \
	else \
		echo "❌ Error: $(UPLOAD_TOOL) not found. Run 'make install-tools'"; \
		exit 1; \
	fi

upload-qr: check-device ## Upload QR code installer
	@echo "📤 Uploading QR code installer..."
	$(UPLOAD_TOOL) connect $(DEVICE) fs cp $(QR_INSTALLER) :

run: upload ## Upload and run the application
	@echo "🚀 Running application..."
	$(UPLOAD_TOOL) connect $(DEVICE) exec "import main"

soft-reset: check-device ## Soft reset the device
	@echo "🔄 Soft resetting device..."
	$(UPLOAD_TOOL) connect $(DEVICE) exec "import machine; machine.soft_reset()"

clean: check-device ## Remove files from Pico
	@echo "🧹 Cleaning Pico filesystem..."
	$(UPLOAD_TOOL) connect $(DEVICE) fs rm main.py || true
	$(UPLOAD_TOOL) connect $(DEVICE) fs rm $(CONFIG_FILE) || true
	@echo "✅ Cleanup complete"

list-files: check-device ## List files on Pico
	@echo "📋 Files on device:"
	$(UPLOAD_TOOL) connect $(DEVICE) fs ls

repl: check-device ## Open REPL console
	@echo "🔗 Opening REPL console (Ctrl+C to exit)..."
	$(UPLOAD_TOOL) connect $(DEVICE) repl

flash-firmware: ## Flash Pimoroni Badger 2040 W firmware
	@echo "⚠️  Put device in bootloader mode:"
	@echo "   1. Hold BOOTSEL button on Pico W"
	@echo "   2. Press RESET button on Badger"
	@echo "   3. Release BOOTSEL when RPI-RP2 drive appears"
	@echo ""
	@read -p "Press Enter when device is in bootloader mode..."
	@if [ -d "/Volumes/RPI-RP2" ]; then \
		cp $(FIRMWARE_FILE) "/Volumes/RPI-RP2/" && \
		echo "✅ Firmware flashed successfully"; \
	elif [ -d "/media/$(USER)/RPI-RP2" ]; then \
		cp $(FIRMWARE_FILE) "/media/$(USER)/RPI-RP2/" && \
		echo "✅ Firmware flashed successfully"; \
	else \
		echo "❌ Error: RPI-RP2 drive not found"; \
		exit 1; \
	fi

test: check-device ## Run basic device tests
	@echo "🧪 Testing device communication..."
	$(UPLOAD_TOOL) connect $(DEVICE) exec "print('Hello from Badger 2040 W')"
	@echo "✅ Device communication OK"

monitor: check-device ## Monitor device output
	@echo "👀 Monitoring device output (Ctrl+C to exit)..."
	$(UPLOAD_TOOL) connect $(DEVICE) exec "exec(open('main.py').read())"

# Development workflow targets
dev-setup: install-tools upload upload-qr ## Complete development setup
	@echo "🎉 Development environment ready!"

dev-cycle: upload run ## Quick development cycle (upload + run)

# Error handling
check-firmware: check-device ## Verify firmware version
	@echo "🔍 Checking firmware version..."
	$(UPLOAD_TOOL) connect $(DEVICE) exec "import sys; print(sys.implementation)"
```

### VS Code Workspace Settings

Create `.vscode/settings.json`:
```json
{
    "micropico.syncFolder": "",
    "micropico.openOnStart": true,
    "python.defaultInterpreterPath": "/usr/bin/python3",
    "files.associations": {
        "*.py": "python"
    },
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true
}
```

## Troubleshooting

### Common Issues

1. **Device Not Found**
   ```bash
   make check-device
   # Check USB connections and device mode
   ```

2. **Permission Denied (Linux)**
   ```bash
   sudo usermod -a -G dialout $USER
   # Logout and login again
   ```

3. **Tool Installation Issues**
   ```bash
   make install-tools
   # Ensure pip is up to date
   ```

4. **File Transfer Failures**
   ```bash
   make soft-reset
   make upload
   # Try different upload tools
   ```

### VS Code Extension Issues

1. **MicroPico Not Connecting**
   - Check device path in extension settings
   - Verify baud rate (115200)
   - Restart VS Code

2. **IntelliSense Not Working**
   - Install MicroPython stubs: `pip install micropython-stubs`
   - Configure Python interpreter path

3. **REPL Console Problems**
   - Ensure no other programs are using the serial port
   - Check device permissions
   - Try different baud rates

## Best Practices

1. **Version Control**: Include Makefile and VS Code configuration in git
2. **Documentation**: Keep README updated with project-specific instructions
3. **Error Handling**: Make targets fail gracefully with helpful messages
4. **Cross-Platform**: Test Makefile on different operating systems
5. **Tool Dependencies**: Document required tools and installation methods

This guide provides a comprehensive foundation for integrating Makefiles with VS Code for Badger 2040 W development, ensuring a smooth and efficient workflow.
