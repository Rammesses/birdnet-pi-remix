"""Idle screen renderer."""

from PIL import ImageDraw, ImageFont

from display.config import (
    COL_BG, COL_HINT, DISPLAY_WIDTH, DISPLAY_HEIGHT,
)
from display.components.clock import draw_clock_full
from display.components.listening import draw_listening
from display.screens._status_bar import render_status_bar


def render_idle(draw: ImageDraw.ImageDraw,
                font_large: ImageFont.FreeTypeFont,
                font_bold: ImageFont.FreeTypeFont,
                font_small: ImageFont.FreeTypeFont,
                font_tiny: ImageFont.FreeTypeFont,
                battery_pct: int,
                wifi_connected: bool,
                wifi_configured: bool) -> None:
    """Render the idle screen: clock + listening animation."""
    draw.rectangle([0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT], fill=COL_BG)
    render_status_bar(draw, font_small, font_tiny, battery_pct, wifi_connected, wifi_configured)
    draw_clock_full(draw, DISPLAY_WIDTH, 14, font_large, font_small)
    draw_listening(draw, 77, font_small)

    hint = "[A]Bright  [B]History  [C\u25BA]Off"
    bbox = draw.textbbox((0, 0), hint, font=font_tiny)
    hw = bbox[2] - bbox[0]
    draw.text(((DISPLAY_WIDTH - hw) // 2, 116), hint, font=font_tiny, fill=COL_HINT)
