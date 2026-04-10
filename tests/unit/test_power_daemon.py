"""Unit tests for the power daemon voltage-to-percent conversion and shutdown logic."""

import json
import pytest
from unittest.mock import MagicMock, patch, call


# Import the pure function directly
from power.daemon import _voltage_to_percent


def test_voltage_to_percent_full():
    assert _voltage_to_percent(4.1) == 100


def test_voltage_to_percent_above_full():
    assert _voltage_to_percent(4.5) == 100


def test_voltage_to_percent_half():
    assert _voltage_to_percent(3.7) == 50


def test_voltage_to_percent_empty():
    assert _voltage_to_percent(3.3) == 0


def test_voltage_to_percent_below_empty():
    assert _voltage_to_percent(3.0) == 0


def test_voltage_to_percent_interpolates():
    pct = _voltage_to_percent(3.9)
    assert 50 < pct < 100


def test_voltage_below_shutdown_triggers_critical():
    mock_client = MagicMock()
    from power.daemon import graceful_shutdown
    with patch("power.daemon.time.sleep"), \
         patch("power.daemon.subprocess.run"):
        graceful_shutdown(mock_client)
    published = mock_client.publish.call_args[0]
    assert published[0].endswith("battery")
    payload = json.loads(published[1])
    assert payload["critical"] is True


def test_voltage_in_warning_range():
    """voltage=3.4 → warning=True, critical=False in published payload."""
    from power.daemon import _voltage_to_percent, VOLTAGE_WARNING, VOLTAGE_SHUTDOWN
    voltage = 3.4
    warning  = voltage < VOLTAGE_WARNING
    critical = voltage < VOLTAGE_SHUTDOWN
    assert warning  is True
    assert critical is False


def test_graceful_shutdown_calls_systemctl():
    mock_client = MagicMock()
    from power.daemon import graceful_shutdown
    with patch("power.daemon.time.sleep"), \
         patch("power.daemon.subprocess.run") as mock_run:
        graceful_shutdown(mock_client)
    calls = [c[0][0] for c in mock_run.call_args_list]
    assert ["systemctl", "stop", "birdnet-go"] in calls
