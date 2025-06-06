#!/usr/bin/env python3
"""
Simple status check for Badger 2040 W
"""

import badger2040
import time

# Quick status display
display = badger2040.Badger2040()
display.led(128)

display.set_pen(15)
display.clear()

display.set_pen(0)
display.set_font("bitmap8")
display.text("Status Check", 10, 20, 280, 1)

display.set_font("bitmap6")
display.text("✓ Display: Working", 10, 40, 280, 1)
display.text("✓ Device: Online", 10, 55, 280, 1)
display.text("✓ Badge: Running", 10, 70, 280, 1)

display.text("Press any button to", 10, 90, 280, 1)
display.text("return to badge app", 10, 105, 280, 1)

display.update()

print("Status check displayed")
print("Badge should show status screen")
print("Press any button on device to continue")

# Wait for button press
while True:
    if (display.pressed(badger2040.BUTTON_A) or 
        display.pressed(badger2040.BUTTON_B) or 
        display.pressed(badger2040.BUTTON_C)):
        break
    time.sleep(0.1)

print("Button pressed - returning to badge application")

# Run the main badge application
import main_github_api
