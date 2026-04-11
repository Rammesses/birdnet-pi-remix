#!/usr/bin/env bash
# Configure ALSA for SPH0645 I²S microphone.
set -euo pipefail

cat > /etc/asound.conf << 'EOF'
pcm.i2smic {
    type hw
    card 0
    device 0
}
pcm.!default {
    type asym
    capture.pcm "i2smic"
}
EOF

echo "ALSA config written to /etc/asound.conf"
echo "Detected audio devices:"
arecord -l || true
