"""Shared status bar renderer used by all screens."""

from PIL import ImageDraw, ImageFont

from display.config import COL_BG, COL_DIVIDER, DISPLAY_WIDTH
from display.components.battery import draw_battery, draw_wifi
from display.components.clock import draw_time_hhmm


def render_status_bar(draw: ImageDraw.ImageDraw,
                      font_small: ImageFont.FreeTypeFont,
                      font_tiny: ImageFont.FreeTypeFont,
                      battery_pct: int,
                      wifi_connected: bool,
                      wifi_configured: bool) -> None:
    """Render the 14px status bar at the top of the screen."""
    draw.rectangle([0, 0, DISPLAY_WIDTH, 13], fill=COL_BG)

    x = 2
    draw_wifi(draw, x, 3, wifi_connected, wifi_configured)
    if wifi_configured:
        x += 12

    draw_battery(draw, x, 2, battery_pct, font_tiny)
    x += 40

    # Time (right-aligned)
    from datetime import datetime
    time_str = datetime.now().strftime("%H:%M")
    bbox = draw.textbbox((0, 0), time_str, font=font_small)
    tw = bbox[2] - bbox[0]
    draw_time_hhmm(draw, DISPLAY_WIDTH - tw - 2, 2, font_small)

    draw.line([0, 13, DISPLAY_WIDTH, 13], fill=COL_DIVIDER)
