"""History screen renderer."""

from PIL import ImageDraw, ImageFont

from display.config import (
    COL_BG, COL_TEXT_PRIMARY, COL_TEXT_SECONDARY,
    COL_ACCENT, COL_CONF_FILL, COL_DIVIDER, COL_HINT,
    DISPLAY_WIDTH, DISPLAY_HEIGHT,
)
from display.components.battery import draw_battery

ROWS_VISIBLE = 5
ROW_HEIGHT   = 14


def render_history(draw: ImageDraw.ImageDraw,
                   font_small: ImageFont.FreeTypeFont,
                   font_tiny: ImageFont.FreeTypeFont,
                   detections: list,
                   scroll_offset: int,
                   battery_pct: int) -> None:
    """Render the history screen showing 5 detection rows.

    Args:
        detections:    List of detection dicts (newest first).
        scroll_offset: Index of the first visible row.
    """
    draw.rectangle([0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT], fill=COL_BG)

    # Header
    draw.text((4, 2), "Recent Detections", font=font_small, fill=COL_TEXT_PRIMARY)
    draw_battery(draw, DISPLAY_WIDTH - 44, 2, battery_pct, font_tiny)
    draw.line([0, 13, DISPLAY_WIDTH, 13], fill=COL_DIVIDER)

    # Rows
    visible = detections[scroll_offset: scroll_offset + ROWS_VISIBLE]
    for i, det in enumerate(visible):
        y = 14 + i * ROW_HEIGHT
        colour = COL_ACCENT if i == 0 else COL_TEXT_PRIMARY

        # Time
        ts = det.get("timestamp", "")
        time_str = ts[11:16] if len(ts) >= 16 else "--:--"
        draw.text((4, y), time_str, font=font_tiny, fill=colour)

        # Name (truncated)
        name = det.get("common_name", "Unknown")[:16]
        draw.text((38, y), name, font=font_tiny, fill=colour)

        # Mini confidence bar (30px)
        conf = float(det.get("confidence", 0.0))
        bar_x = DISPLAY_WIDTH - 44
        draw.rectangle([bar_x, y + 2, bar_x + 29, y + 10], fill=COL_DIVIDER)
        draw.rectangle([bar_x, y + 2, bar_x + int(29 * conf), y + 10], fill=COL_CONF_FILL)

        # Percent
        draw.text((DISPLAY_WIDTH - 14, y), f"{int(conf * 100)}%", font=font_tiny, fill=colour)

    # Divider
    draw.line([0, 84, DISPLAY_WIDTH, 84], fill=COL_DIVIDER)

    # Button hints
    hint = "[A]\u2191  [B]Back  [C]\u2193"
    bbox = draw.textbbox((0, 0), hint, font=font_tiny)
    hw = bbox[2] - bbox[0]
    draw.text(((DISPLAY_WIDTH - hw) // 2, 116), hint, font=font_tiny, fill=COL_HINT)
