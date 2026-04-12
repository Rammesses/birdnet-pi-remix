#!/usr/bin/env bash
# Verify SPH0645 I²S microphone is visible to ALSA and can record audio.
set -euo pipefail

echo "=== SPH0645 I²S Microphone Verification ==="

echo "--- ALSA capture devices ---"
if ! arecord -l 2>&1 | grep -q "card"; then
    echo "✗ No ALSA capture devices found"
    echo "  Check: dtparam=i2s=on and dtoverlay=i2s-mmap in /boot/firmware/config.txt"
    echo "  Check: dtparam=audio=off is set"
    echo "  Check: BCLK → Pin 12, LRCLK → Pin 35, DOUT → Pin 38"
    exit 1
fi
arecord -l

echo ""
echo "--- Recording 5 seconds of audio ---"
arecord -D hw:0,0 -f S32_LE -r 48000 -c 2 -d 5 /tmp/birdnet-test.wav
SIZE=$(stat -c%s /tmp/birdnet-test.wav)
echo "Recorded file size: ${SIZE} bytes"

if [ "$SIZE" -gt 1000000 ]; then
    echo "✓ Audio OK — file is ~${SIZE} bytes (expected ~1.8MB for 5s)"
else
    echo "✗ Audio file unexpectedly small (${SIZE} bytes) — check microphone wiring"
    exit 1
fi

rm /tmp/birdnet-test.wav
