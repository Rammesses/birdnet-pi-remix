"""Battery icon and Wi-Fi icon rendering components."""

from PIL import ImageDraw, ImageFont

from display.config import (
    COL_BATT_GOOD, COL_BATT_LOW, COL_BATT_CRIT,
    COL_TEXT_PRIMARY, COL_TEXT_SECONDARY,
)


def _batt_colour(percent: int) -> tuple:
    if percent >= 40:
        return COL_BATT_GOOD
    if percent >= 20:
        return COL_BATT_LOW
    return COL_BATT_CRIT


def draw_battery(draw: ImageDraw.ImageDraw, x: int, y: int, percent: int, font: ImageFont.FreeTypeFont) -> None:
    """Draw a 5-segment battery glyph at (x, y) followed by numeric percent.

    The glyph is 18×10px; text is appended to the right.
    """
    colour = _batt_colour(percent)
    # Outer border
    draw.rectangle([x, y, x + 17, y + 9], outline=colour)
    # Terminal nub
    draw.rectangle([x + 18, y + 3, x + 19, y + 6], fill=colour)
    # Filled segments (5 bars, 2px wide, 1px gap, 1px inner margin)
    filled = round(percent / 20)  # 0–5 segments
    for i in range(5):
        bx = x + 1 + i * 3
        if i < filled:
            draw.rectangle([bx, y + 1, bx + 1, y + 8], fill=colour)
    # Numeric label
    draw.text((x + 22, y), f"{percent}%", font=font, fill=COL_TEXT_SECONDARY)


def draw_wifi(draw: ImageDraw.ImageDraw, x: int, y: int, connected: bool, configured: bool) -> None:
    """Draw a simple 3-arc Wi-Fi glyph at (x, y) in an 8×8px area.

    Hidden if not configured; outline arcs if disconnected; solid if connected.
    """
    if not configured:
        return
    colour = COL_TEXT_PRIMARY if connected else COL_TEXT_SECONDARY
    # Three arcs approximated as partial ellipses
    draw.arc([x,     y + 2, x + 8, y + 10], start=200, end=340, fill=colour)
    draw.arc([x + 2, y + 4, x + 6, y + 8],  start=200, end=340, fill=colour)
    draw.point((x + 4, y + 7), fill=colour)
