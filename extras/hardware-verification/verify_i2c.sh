#!/usr/bin/env bash
# Verify INA219 power monitor is visible on I²C bus at 0x40.
set -euo pipefail

echo "=== INA219 I²C Verification ==="
output=$(sudo i2cdetect -y 1)
echo "$output"

if echo "$output" | grep -q "40"; then
    echo "✓ INA219 found at 0x40"
else
    echo "✗ INA219 NOT found at 0x40"
    echo "  Check: dtparam=i2c_arm=on in /boot/firmware/config.txt"
    echo "  Check: SDA → Pin 3 (GPIO 2), SCL → Pin 5 (GPIO 3)"
    echo "  Check: 3.3V on INA219 VCC"
    exit 1
fi
