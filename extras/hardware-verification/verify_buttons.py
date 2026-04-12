#!/usr/bin/env python3
"""Interactive button verification — press each button in sequence."""

import sys
import time
import RPi.GPIO as GPIO

BUTTONS = [("A", 16), ("B", 26), ("C", 21)]

GPIO.setmode(GPIO.BCM)
for _, pin in BUTTONS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("=== Button Verification ===")
print("Press each button when prompted. Ctrl-C to abort.\n")

try:
    for label, pin in BUTTONS:
        print(f"Press Button {label} (GPIO {pin})...", end=" ", flush=True)
        while GPIO.input(pin) == 1:
            time.sleep(0.01)
        print(f"✓")
        time.sleep(0.3)  # debounce
    print("\n✓ All buttons OK")
except KeyboardInterrupt:
    print("\nAborted.")
    sys.exit(1)
finally:
    GPIO.cleanup()
