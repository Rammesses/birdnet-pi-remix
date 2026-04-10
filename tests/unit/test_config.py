"""Unit tests for display/config.py."""

import display.config as cfg


def test_all_gpio_constants_defined():
    for name in ("DISPLAY_CS", "DISPLAY_DC", "DISPLAY_RST", "DISPLAY_BL",
                 "BUTTON_A", "BUTTON_B", "BUTTON_C"):
        assert isinstance(getattr(cfg, name), int), f"{name} must be an int"


def test_all_colour_constants_are_rgb_tuples():
    colour_names = [k for k in dir(cfg) if k.startswith("COL_")]
    assert colour_names, "No COL_* constants found"
    for name in colour_names:
        val = getattr(cfg, name)
        assert isinstance(val, tuple) and len(val) == 3, f"{name} must be a 3-tuple"
        assert all(isinstance(c, int) and 0 <= c <= 255 for c in val), \
            f"{name} values must be ints in 0–255"


def test_display_dimensions():
    assert cfg.DISPLAY_WIDTH  == 160
    assert cfg.DISPLAY_HEIGHT == 128


def test_voltage_thresholds_ordered():
    assert cfg.VOLTAGE_SHUTDOWN < cfg.VOLTAGE_WARNING
