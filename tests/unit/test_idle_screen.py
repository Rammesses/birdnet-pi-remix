"""Unit tests for the idle screen renderer."""

import pytest
from PIL import Image, ImageDraw, ImageFont

from display.config import COL_BG, DISPLAY_WIDTH, DISPLAY_HEIGHT
from display.screens.idle import render_idle


def _fonts():
    f = ImageFont.load_default()
    return f, f, f, f, f  # large, bold, small, tiny (×2 for render_idle signature)


def _render():
    img = Image.new("RGB", (DISPLAY_WIDTH, DISPLAY_HEIGHT), COL_BG)
    draw = ImageDraw.Draw(img)
    large, bold, small, tiny, _ = _fonts()
    render_idle(draw, large, bold, small, tiny,
                battery_pct=80, wifi_connected=False, wifi_configured=False)
    return img


def test_idle_renders_without_error():
    _render()


def test_idle_non_blank():
    img = _render()
    blank = Image.new("RGB", (DISPLAY_WIDTH, DISPLAY_HEIGHT), COL_BG)
    assert list(img.getdata()) != list(blank.getdata())
