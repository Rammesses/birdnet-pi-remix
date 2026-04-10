"""Shared pytest fixtures for BirdNET-Pi Remix test suite."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# Hardware mocks (autouse — applied to every test)
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def mock_gpio(monkeypatch):
    """Replace RPi.GPIO with a no-op mock for all tests."""
    mock = MagicMock()
    monkeypatch.setitem(sys.modules, "RPi", mock)
    monkeypatch.setitem(sys.modules, "RPi.GPIO", mock.GPIO)
    return mock


@pytest.fixture(autouse=True)
def mock_luma(monkeypatch):
    """Replace luma.lcd with a no-op mock so imports don't fail."""
    luma_mock = MagicMock()
    monkeypatch.setitem(sys.modules, "luma", luma_mock)
    monkeypatch.setitem(sys.modules, "luma.lcd", luma_mock.lcd)
    monkeypatch.setitem(sys.modules, "luma.lcd.device", luma_mock.lcd.device)
    monkeypatch.setitem(sys.modules, "luma.core", luma_mock.core)
    monkeypatch.setitem(sys.modules, "luma.core.interface", luma_mock.core.interface)
    monkeypatch.setitem(sys.modules, "luma.core.interface.serial", luma_mock.core.interface.serial)
    return luma_mock


@pytest.fixture(autouse=True)
def mock_smbus2(monkeypatch):
    """Replace smbus2 with a no-op mock."""
    mock = MagicMock()
    monkeypatch.setitem(sys.modules, "smbus2", mock)
    return mock


@pytest.fixture(autouse=True)
def mock_paho(monkeypatch):
    """Replace paho.mqtt with a no-op mock."""
    mock = MagicMock()
    monkeypatch.setitem(sys.modules, "paho", mock)
    monkeypatch.setitem(sys.modules, "paho.mqtt", mock.mqtt)
    monkeypatch.setitem(sys.modules, "paho.mqtt.client", mock.mqtt.client)
    return mock


# ---------------------------------------------------------------------------
# Pi-only marker
# ---------------------------------------------------------------------------

running_on_pi = (
    sys.platform == "linux"
    and Path("/proc/device-tree/model").exists()
)
pi_only = pytest.mark.skipif(not running_on_pi, reason="Requires Raspberry Pi hardware")
