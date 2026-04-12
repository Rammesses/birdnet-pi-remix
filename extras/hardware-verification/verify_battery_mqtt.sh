#!/usr/bin/env bash
# Verify battery MQTT messages are being published by the power daemon.
# Waits up to 35 seconds for a message on birdnet/battery.
set -euo pipefail

echo "=== Battery MQTT Verification ==="
echo "Waiting for birdnet/battery message (up to 35s)..."

MSG=$(mosquitto_sub -h localhost -t birdnet/battery -C 1 -W 35 2>&1) || {
    echo "✗ No message received within 35 seconds"
    echo "  Check: systemctl status birdnet-power"
    echo "  Check: journalctl -u birdnet-power -n 20"
    exit 1
}

echo "Received: $MSG"

# Basic sanity checks
if echo "$MSG" | grep -q '"voltage"' && echo "$MSG" | grep -q '"percent"'; then
    echo "✓ Battery MQTT OK"
else
    echo "✗ Message missing expected fields (voltage, percent)"
    exit 1
fi
