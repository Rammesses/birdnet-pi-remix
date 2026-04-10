"""Unit tests for the battery and Wi-Fi icon components."""

import pytest
from PIL import Image, ImageDraw, ImageFont

from display.config import COL_BATT_GOOD, COL_BATT_LOW, COL_BATT_CRIT, DISPLAY_WIDTH
from display.components.battery import draw_battery, draw_wifi


def _make_draw():
    img = Image.new("RGB", (DISPLAY_WIDTH, 20), (0, 0, 0))
    return img, ImageDraw.Draw(img)


def _tiny_font():
    return ImageFont.load_default()


def _pixels(img):
    return set(img.getdata())


def test_battery_icon_good_colour():
    img, draw = _make_draw()
    draw_battery(draw, 0, 2, 80, _tiny_font())
    assert COL_BATT_GOOD in _pixels(img)


def test_battery_icon_low_colour():
    img, draw = _make_draw()
    draw_battery(draw, 0, 2, 30, _tiny_font())
    assert COL_BATT_LOW in _pixels(img)


def test_battery_icon_critical_colour():
    img, draw = _make_draw()
    draw_battery(draw, 0, 2, 10, _tiny_font())
    assert COL_BATT_CRIT in _pixels(img)


def test_battery_renders_percentage_text():
    """Verify the image is non-trivially different from a blank image after drawing."""
    blank = Image.new("RGB", (DISPLAY_WIDTH, 20), (0, 0, 0))
    img, draw = _make_draw()
    draw_battery(draw, 0, 2, 73, _tiny_font())
    assert list(img.getdata()) != list(blank.getdata())
