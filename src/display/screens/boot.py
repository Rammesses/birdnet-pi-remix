"""Boot splash screen renderer."""

import math
import time

from PIL import ImageDraw, ImageFont

from display.config import (
    COL_BG, COL_TEXT_PRIMARY, COL_TEXT_SECONDARY, COL_ACCENT,
    DISPLAY_WIDTH, DISPLAY_HEIGHT,
)


def render_boot(draw: ImageDraw.ImageDraw,
                font_bold: ImageFont.FreeTypeFont,
                font_small: ImageFont.FreeTypeFont) -> None:
    """Render the boot splash screen with an indeterminate progress bar."""
    draw.rectangle([0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT], fill=COL_BG)

    # Bird glyph
    bird = "\U0001F426"
    try:
        bbox = draw.textbbox((0, 0), bird, font=font_bold)
        bw = bbox[2] - bbox[0]
        draw.text(((DISPLAY_WIDTH - bw) // 2, 28), bird, font=font_bold, fill=COL_ACCENT)
    except Exception:
        pass  # emoji may not render on all fonts; skip gracefully

    # Title
    title = "BirdNET Remix"
    bbox = draw.textbbox((0, 0), title, font=font_bold)
    tw = bbox[2] - bbox[0]
    draw.text(((DISPLAY_WIDTH - tw) // 2, 52), title, font=font_bold, fill=COL_TEXT_PRIMARY)

    # Subtitle
    sub = "Starting up..."
    bbox = draw.textbbox((0, 0), sub, font=font_small)
    sw = bbox[2] - bbox[0]
    draw.text(((DISPLAY_WIDTH - sw) // 2, 72), sub, font=font_small, fill=COL_TEXT_SECONDARY)

    # Indeterminate progress bar (120px wide, centred)
    bar_x = (DISPLAY_WIDTH - 120) // 2
    bar_y = 90
    draw.rectangle([bar_x, bar_y, bar_x + 120, bar_y + 6], outline=COL_TEXT_SECONDARY)

    # Animated fill: 40px wide chunk cycling left-to-right
    chunk = 40
    period = 1.5  # seconds
    pos = int(((time.monotonic() % period) / period) * (120 + chunk)) - chunk
    fill_x1 = max(bar_x + 1, bar_x + pos)
    fill_x2 = min(bar_x + 119, bar_x + pos + chunk)
    if fill_x1 < fill_x2:
        draw.rectangle([fill_x1, bar_y + 1, fill_x2, bar_y + 5], fill=COL_ACCENT)
