#!/usr/bin/env bash
# BirdNET-Pi Remix — Installation Script
# Idempotent: safe to run more than once.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
INSTALL_DIR="/opt/birdnet-remix"
VENV="$INSTALL_DIR/venv"
CONFIG_DIR="/etc/birdnet-go"
BOOT_CONFIG="/boot/firmware/config.txt"

echo "=== BirdNET-Pi Remix Installer ==="

# 1. System update
apt-get update && apt-get upgrade -y

# 2. System packages
apt-get install -y python3-pip python3-venv mosquitto mosquitto-clients i2c-tools

# 3. /boot/firmware/config.txt entries
add_config() {
    grep -qF "$1" "$BOOT_CONFIG" || echo "$1" >> "$BOOT_CONFIG"
}
add_config "dtparam=i2s=on"
add_config "dtoverlay=i2s-mmap"
add_config "dtparam=spi=on"
add_config "dtparam=i2c_arm=on"
add_config "dtparam=audio=off"
add_config "gpu_mem=16"

# 4. Create birdnet system user
id -u birdnet &>/dev/null || useradd --system --no-create-home --shell /usr/sbin/nologin birdnet

# 5. Copy repository to install dir
mkdir -p "$INSTALL_DIR"
rsync -a --exclude='.git' --exclude='extras' --exclude='docs' --exclude='tests' \
    "$REPO_DIR/" "$INSTALL_DIR/"

# 6. Python venv + dependencies
python3 -m venv "$VENV"
"$VENV/bin/pip" install --upgrade pip
"$VENV/bin/pip" install -r "$INSTALL_DIR/requirements.txt"

# 7. Download BirdNET-Go binary
BIRDNET_GO_VERSION=$(curl -s https://api.github.com/repos/tphakala/birdnet-go/releases/latest \
    | grep '"tag_name"' | cut -d'"' -f4)
BIRDNET_GO_URL="https://github.com/tphakala/birdnet-go/releases/download/${BIRDNET_GO_VERSION}/birdnet-go_linux_arm64"
echo "Downloading BirdNET-Go $BIRDNET_GO_VERSION..."
curl -fsSL "$BIRDNET_GO_URL" -o /usr/local/bin/birdnet-go
chmod +x /usr/local/bin/birdnet-go

# 8. BirdNET-Go config
mkdir -p "$CONFIG_DIR"
cp -n "$INSTALL_DIR/src/config/birdnet-go.yaml" "$CONFIG_DIR/config.yaml" || true

# 9. Mosquitto config
cp "$INSTALL_DIR/src/config/mosquitto.conf" /etc/mosquitto/conf.d/birdnet.conf

# 10. Systemd services
cp "$INSTALL_DIR/src/systemd/"*.service "$INSTALL_DIR/src/systemd/"*.target /etc/systemd/system/
systemctl daemon-reload
systemctl enable birdnet-remix.target

# 11. Audio setup
bash "$INSTALL_DIR/src/install/setup_audio.sh"

# 12. Display setup
bash "$INSTALL_DIR/src/install/setup_display.sh"

# 13. BirdWeather token (optional)
read -rp "Enter BirdWeather station token (leave blank to skip): " BW_TOKEN
if [[ -n "$BW_TOKEN" ]]; then
    sed -i "s/enabled: false/enabled: true/" "$CONFIG_DIR/config.yaml"
    sed -i "s/token: \"\"/token: \"$BW_TOKEN\"/" "$CONFIG_DIR/config.yaml"
    echo "BirdWeather sync enabled."
fi

# 14. Wi-Fi credentials (optional)
read -rp "Enter Wi-Fi SSID (leave blank to skip): " WIFI_SSID
if [[ -n "$WIFI_SSID" ]]; then
    read -rsp "Enter Wi-Fi password: " WIFI_PASS
    echo
    sed -e "s/{{SSID}}/$WIFI_SSID/" \
        -e "s/{{PASSWORD}}/$WIFI_PASS/" \
        "$INSTALL_DIR/config/wpa_supplicant.conf.template" \
        > /etc/wpa_supplicant/wpa_supplicant.conf
    chmod 600 /etc/wpa_supplicant/wpa_supplicant.conf
    echo "Wi-Fi configured."
fi

# 15. Start services
systemctl start birdnet-remix.target

# 16. Done
echo ""
echo "Installation complete. Rebooting in 10 seconds..."
sleep 10
reboot
