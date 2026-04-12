#!/usr/bin/env python3
"""ST7735 display smoke test — renders 'Hello Bird!' on the TFT."""

import sys
sys.path.insert(0, "/opt/birdnet-remix")

from display.drivers.st7735 import ST7735Display
from PIL import Image, ImageDraw

d = ST7735Display()
img = Image.new("RGB", (160, 128), (13, 27, 14))
draw = ImageDraw.Draw(img)
draw.text((10, 50), "Hello Bird!", fill=(240, 236, 216))
d.show(img)
print("✓ Display OK — 'Hello Bird!' should be visible on the TFT")
