"""Clock rendering component."""

from datetime import datetime

from PIL import ImageDraw, ImageFont

from display.config import COL_TEXT_PRIMARY, COL_TEXT_SECONDARY


def draw_time_hhmm(draw: ImageDraw.ImageDraw, x: int, y: int, font: ImageFont.FreeTypeFont) -> None:
    """Draw current time as HH:MM at (x, y)."""
    draw.text((x, y), datetime.now().strftime("%H:%M"), font=font, fill=COL_TEXT_PRIMARY)


def draw_clock_full(draw: ImageDraw.ImageDraw, width: int, y_start: int,
                    font_large: ImageFont.FreeTypeFont,
                    font_small: ImageFont.FreeTypeFont) -> None:
    """Draw centred HH:MM:SS, day name, and date starting at y_start."""
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")
    day_str  = now.strftime("%A")
    date_str = now.strftime("%-d %B %Y")

    for text, font, y in (
        (time_str, font_large, y_start),
        (day_str,  font_small, y_start + 39),
        (date_str, font_small, y_start + 51),
    ):
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((width - tw) // 2, y), text, font=font, fill=COL_TEXT_PRIMARY)
