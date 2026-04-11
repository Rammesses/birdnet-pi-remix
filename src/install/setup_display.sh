#!/usr/bin/env bash
# Verify SPI device is present for ST7735 display.
set -euo pipefail

if ls /dev/spidev* &>/dev/null; then
    echo "SPI devices found:"
    ls /dev/spidev*
else
    echo "ERROR: No SPI devices found. Ensure dtparam=spi=on is in /boot/firmware/config.txt and reboot." >&2
    exit 1
fi
