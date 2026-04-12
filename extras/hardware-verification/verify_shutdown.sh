#!/usr/bin/env bash
# Simulate a power-critical condition and verify graceful shutdown sequence.
# WARNING: This will shut down the Pi. Run only when ready.
set -euo pipefail

echo "=== Graceful Shutdown Verification ==="
echo "WARNING: This will shut down the system in ~8 seconds."
read -rp "Continue? [y/N] " CONFIRM
[[ "$CONFIRM" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 0; }

mosquitto_pub -h localhost -t birdnet/battery -m '{
  "voltage": 3.2, "percent": 0, "critical": true,
  "current_ma": 0.0, "warning": false
}'

echo "Critical battery message published."
echo "Watch the display for the shutdown screen, then system will power off."
echo ""
echo "After next boot, verify with:"
echo "  journalctl --boot=-1 | grep -E '(Stopped BirdNET-Go|sync|poweroff)'"
echo "  sqlite3 /var/lib/birdnet-go/detections.db \"PRAGMA integrity_check;\""
