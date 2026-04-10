"""Shutdown screen renderer."""

from PIL import ImageDraw, ImageFont

from display.config import (
    COL_BG, COL_TEXT_PRIMARY, COL_TEXT_SECONDARY, DISPLAY_WIDTH, DISPLAY_HEIGHT,
)


def render_shutdown(draw: ImageDraw.ImageDraw,
                    font_bold: ImageFont.FreeTypeFont,
                    font_small: ImageFont.FreeTypeFont) -> None:
    """Render the shutdown screen."""
    draw.rectangle([0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT], fill=COL_BG)

    for text, font, y, colour in (
        ("Shutting down...",          font_bold,  40, COL_TEXT_PRIMARY),
        ("Saving detections database", font_small, 64, COL_TEXT_SECONDARY),
        ("Please wait",               font_small, 78, COL_TEXT_SECONDARY),
    ):
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((DISPLAY_WIDTH - tw) // 2, y), text, font=font, fill=colour)
