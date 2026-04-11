"""Listening animation component."""

import time

from PIL import ImageDraw, ImageFont

from display.config import COL_TEXT_SECONDARY, COL_TEXT_PRIMARY, DISPLAY_WIDTH


def draw_listening(draw: ImageDraw.ImageDraw, y: int, font: ImageFont.FreeTypeFont) -> None:
    """Draw '≋  Listening...  ≋' with three cycling dots centred at y.

    Dots cycle Sage→Bone White at 0.4s per dot (period 1.2s).
    """
    label = "\u2248  Listening...  \u2248"
    bbox = draw.textbbox((0, 0), label, font=font)
    lw = bbox[2] - bbox[0]
    draw.text(((DISPLAY_WIDTH - lw) // 2, y), label, font=font, fill=COL_TEXT_SECONDARY)

    # Three dots below
    dot_y = y + 14
    phase = (time.monotonic() % 1.2) / 0.4  # 0.0–3.0
    dots = ["·", "·", "·"]
    colours = [COL_TEXT_SECONDARY, COL_TEXT_SECONDARY, COL_TEXT_SECONDARY]
    colours[int(phase) % 3] = COL_TEXT_PRIMARY

    dot_str = "  ".join(dots)
    # Render each dot individually with its colour
    x = (DISPLAY_WIDTH - 16) // 2
    for i, (dot, col) in enumerate(zip(dots, colours)):
        draw.text((x + i * 8, dot_y), dot, font=font, fill=col)
