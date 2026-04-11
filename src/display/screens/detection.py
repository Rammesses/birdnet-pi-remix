"""Detection screen renderer."""

from PIL import ImageDraw, ImageFont

from display.config import (
    COL_BG, COL_TEXT_PRIMARY, COL_TEXT_SECONDARY,
    COL_CONF_BG, COL_CONF_FILL, COL_HINT,
    DISPLAY_WIDTH, DISPLAY_HEIGHT,
)
from display.components.spectrogram import draw_visualiser
from display.screens._status_bar import render_status_bar


def render_detection(draw: ImageDraw.ImageDraw,
                     font_bold: ImageFont.FreeTypeFont,
                     font_italic: ImageFont.FreeTypeFont,
                     font_small: ImageFont.FreeTypeFont,
                     font_tiny: ImageFont.FreeTypeFont,
                     detection: dict,
                     slide_offset: int,
                     battery_pct: int,
                     wifi_connected: bool,
                     wifi_configured: bool) -> None:
    """Render the detection screen.

    Args:
        detection:    Dict with keys common_name, scientific_name, confidence.
        slide_offset: Horizontal pixel offset for slide-in animation (0 = settled).
    """
    draw.rectangle([0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT], fill=COL_BG)
    render_status_bar(draw, font_small, font_tiny, battery_pct, wifi_connected, wifi_configured)

    common = detection.get("common_name", "Unknown")[:20]
    sci    = detection.get("scientific_name", "")
    conf   = float(detection.get("confidence", 0.0))

    x = 4 + slide_offset

    # Common name (16px bold)
    draw.text((x, 14), common, font=font_bold, fill=COL_TEXT_PRIMARY)

    # Scientific name (11px italic)
    draw.text((x, 33), sci, font=font_italic, fill=COL_TEXT_SECONDARY)

    # Confidence bar
    bar_x1, bar_y1, bar_x2, bar_y2 = 4, 47, 156, 60
    draw.rectangle([bar_x1, bar_y1, bar_x2, bar_y2], fill=COL_CONF_BG)
    fill_w = int(152 * conf)
    if fill_w > 0:
        draw.rectangle([bar_x1, bar_y1, bar_x1 + fill_w, bar_y2], fill=COL_CONF_FILL)
    pct_str = f"{int(conf * 100)}%"
    bbox = draw.textbbox((0, 0), pct_str, font=font_small)
    pw = bbox[2] - bbox[0]
    draw.text((bar_x2 - pw - 2, bar_y1), pct_str, font=font_small, fill=COL_TEXT_PRIMARY)

    # Visualiser
    draw_visualiser(draw, 4, 103, conf)

    # Button hints
    hint = "[A]Bright  [B]History  [C\u25BA]Off"
    bbox = draw.textbbox((0, 0), hint, font=font_tiny)
    hw = bbox[2] - bbox[0]
    draw.text(((DISPLAY_WIDTH - hw) // 2, 116), hint, font=font_tiny, fill=COL_HINT)
