"""Confidence-band visualiser component (v1 pseudo-spectrogram)."""

import math
import time

from PIL import ImageDraw

from display.config import COL_SPEC_LOW, COL_SPEC_HIGH, COL_BG

BAR_COUNT  = 18
BAR_WIDTH  = 7   # px per bar (18 bars × ~7px ≈ 126px, centred in 160px)
BAR_GAP    = 1
MAX_HEIGHT = 40  # px


def _lerp_colour(t: float) -> tuple:
    """Linearly interpolate between COL_SPEC_LOW and COL_SPEC_HIGH."""
    return tuple(int(a + (b - a) * t) for a, b in zip(COL_SPEC_LOW, COL_SPEC_HIGH))


def draw_visualiser(draw: ImageDraw.ImageDraw, x: int, y: int, confidence: float) -> None:
    """Draw 18 animated bars seeded from confidence, cycling slowly.

    Args:
        draw:       Pillow ImageDraw instance.
        x:          Left edge of visualiser area.
        y:          Bottom edge of visualiser area.
        confidence: Detection confidence (0.0–1.0) used as seed.
    """
    t = time.monotonic()
    seed = int(confidence * 1000)
    total_width = BAR_COUNT * (BAR_WIDTH + BAR_GAP) - BAR_GAP
    x_start = x + (152 - total_width) // 2  # centre within 152px content area

    for i in range(BAR_COUNT):
        # Pseudo-random height using sine waves with different frequencies
        phase = (seed + i * 37) % 360
        wave = (math.sin(math.radians(phase) + t * (0.8 + i * 0.05)) + 1) / 2
        height = max(2, int(wave * MAX_HEIGHT * confidence))
        t_colour = height / MAX_HEIGHT
        colour = _lerp_colour(t_colour)

        bx = x_start + i * (BAR_WIDTH + BAR_GAP)
        draw.rectangle([bx, y - height, bx + BAR_WIDTH - 1, y], fill=colour)
