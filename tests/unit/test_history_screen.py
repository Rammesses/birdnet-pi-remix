"""Unit tests for the history screen renderer."""

import pytest
from PIL import Image, ImageDraw, ImageFont

from display.config import COL_BG, COL_ACCENT, DISPLAY_WIDTH, DISPLAY_HEIGHT
from display.screens.history import render_history

DETECTIONS = [
    {"common_name": "Great Tit",   "confidence": 0.87, "timestamp": "2026-04-10T14:23:00Z"},
    {"common_name": "Blue Tit",    "confidence": 0.92, "timestamp": "2026-04-10T14:18:00Z"},
    {"common_name": "Robin",       "confidence": 0.78, "timestamp": "2026-04-10T13:55:00Z"},
    {"common_name": "Song Thrush", "confidence": 0.83, "timestamp": "2026-04-10T13:41:00Z"},
    {"common_name": "Chaffinch",   "confidence": 0.71, "timestamp": "2026-04-10T13:30:00Z"},
    {"common_name": "Blackbird",   "confidence": 0.95, "timestamp": "2026-04-10T13:12:00Z"},
]


def _fonts():
    return ImageFont.load_default(), ImageFont.load_default()


def _render(detections, scroll=0):
    img = Image.new("RGB", (DISPLAY_WIDTH, DISPLAY_HEIGHT), COL_BG)
    draw = ImageDraw.Draw(img)
    small, tiny = _fonts()
    render_history(draw, small, tiny, detections, scroll, battery_pct=80)
    return img


def test_history_renders_without_error():
    _render(DETECTIONS)


def test_empty_history_renders_without_error():
    _render([])


def test_history_non_blank():
    img = _render(DETECTIONS)
    blank = Image.new("RGB", (DISPLAY_WIDTH, DISPLAY_HEIGHT), COL_BG)
    assert list(img.getdata()) != list(blank.getdata())


def test_scroll_changes_output():
    img0 = _render(DETECTIONS, scroll=0)
    img1 = _render(DETECTIONS, scroll=1)
    assert list(img0.getdata()) != list(img1.getdata())
