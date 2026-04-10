"""Unit tests for the detection screen renderer."""

import pytest
from PIL import Image, ImageDraw, ImageFont

from display.config import COL_BG, COL_CONF_FILL, DISPLAY_WIDTH, DISPLAY_HEIGHT
from display.screens.detection import render_detection


def _fonts():
    f = ImageFont.load_default()
    return f, f, f, f  # bold, italic, small, tiny


def _render(detection, slide_offset=0):
    img = Image.new("RGB", (DISPLAY_WIDTH, DISPLAY_HEIGHT), COL_BG)
    draw = ImageDraw.Draw(img)
    bold, italic, small, tiny = _fonts()
    render_detection(draw, bold, italic, small, tiny,
                     detection, slide_offset,
                     battery_pct=80, wifi_connected=False, wifi_configured=False)
    return img


def _row_pixels(img, y1, y2):
    """Return all unique pixel colours in the y range."""
    pixels = set()
    for y in range(y1, y2):
        for x in range(DISPLAY_WIDTH):
            pixels.add(img.getpixel((x, y)))
    return pixels


def test_common_name_rendered():
    img = _render({"common_name": "Great Tit", "confidence": 0.87})
    row = _row_pixels(img, 14, 33)
    assert row != {COL_BG}, "Common name zone should contain non-background pixels"


def test_confidence_bar_full():
    img = _render({"common_name": "Robin", "confidence": 1.0})
    # At 100% confidence the bar fill should be present; check a pixel well within the filled area
    # (avoid the right edge where the % text may overlap)
    assert img.getpixel((80, 53)) == COL_CONF_FILL


def test_confidence_bar_empty():
    img = _render({"common_name": "Robin", "confidence": 0.0})
    # At 0% confidence no fill pixels should appear in the bar row
    bar_pixels = {img.getpixel((x, 53)) for x in range(5, 156)}
    assert COL_CONF_FILL not in bar_pixels


def test_slide_animation_produces_frames():
    """First 8 frames with slide_offset > 0 should differ from settled frame."""
    settled = _render({"common_name": "Great Tit", "confidence": 0.87}, slide_offset=0)
    sliding = _render({"common_name": "Great Tit", "confidence": 0.87}, slide_offset=80)
    assert list(settled.getdata()) != list(sliding.getdata())


def test_same_species_no_slide():
    """Two renders with slide_offset=0 (same species) should have the name at the same x position."""
    det = {"common_name": "Great Tit", "confidence": 0.87}
    frame1 = _render(det, slide_offset=0)
    frame2 = _render(det, slide_offset=0)
    # The name zone (y=14–32) should be identical — same x position, same text
    row1 = [frame1.getpixel((x, 20)) for x in range(DISPLAY_WIDTH)]
    row2 = [frame2.getpixel((x, 20)) for x in range(DISPLAY_WIDTH)]
    assert row1 == row2
