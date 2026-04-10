"""Unit tests for DisplayStateMachine."""

import pytest
from display.state_machine import (
    DisplayStateMachine,
    BOOT, IDLE, DETECTION, HISTORY, DIM, SHUTDOWN,
)

SAMPLE_DETECTION = {
    "common_name": "Great Tit",
    "scientific_name": "Parus major",
    "confidence": 0.87,
    "timestamp": "2026-04-10T14:23:00Z",
}


@pytest.fixture
def sm():
    return DisplayStateMachine()


@pytest.fixture
def sm_idle(sm):
    sm.on_mqtt_connected()
    assert sm.state == IDLE
    return sm


@pytest.fixture
def sm_detection(sm_idle):
    sm_idle.on_detection(SAMPLE_DETECTION)
    assert sm_idle.state == DETECTION
    return sm_idle


def test_boot_to_idle(sm):
    sm.on_mqtt_connected()
    assert sm.state == IDLE


def test_idle_to_detection(sm_idle):
    sm_idle.on_detection(SAMPLE_DETECTION)
    assert sm_idle.state == DETECTION


def test_detection_timeout_to_idle(sm_detection):
    sm_detection.on_detection_timeout()
    assert sm_detection.state == IDLE


def test_new_detection_resets_timer(sm_detection):
    sm_detection.on_detection({"common_name": "Blue Tit", "confidence": 0.9})
    assert sm_detection.state == DETECTION


def test_button_b_idle_to_history(sm_idle):
    sm_idle.on_button_b()
    assert sm_idle.state == HISTORY


def test_button_b_detection_to_history(sm_detection):
    sm_detection.on_button_b()
    assert sm_detection.state == HISTORY


def test_button_b_history_returns_to_idle(sm_idle):
    sm_idle.on_button_b()
    sm_idle.on_button_b()
    assert sm_idle.state == IDLE


def test_button_b_history_returns_to_detection(sm_detection):
    sm_detection.on_button_b()
    sm_detection.on_button_b()
    assert sm_detection.state == DETECTION


def test_button_a_cycles_backlight(sm_idle):
    from display.config import BACKLIGHT_LEVELS
    assert sm_idle.backlight_percent == BACKLIGHT_LEVELS[0]
    sm_idle.on_button_a()
    assert sm_idle.backlight_percent == BACKLIGHT_LEVELS[1]
    sm_idle.on_button_a()
    assert sm_idle.backlight_percent == BACKLIGHT_LEVELS[2]
    sm_idle.on_button_a()
    assert sm_idle.backlight_percent == BACKLIGHT_LEVELS[0]


def test_button_c_hold_triggers_shutdown(sm_idle):
    sm_idle.on_button_c_hold()
    assert sm_idle.state == SHUTDOWN


def test_dim_timeout_any_state(sm_idle):
    sm_idle.on_dim_timeout()
    assert sm_idle.state == DIM


def test_button_wake_from_dim(sm_idle):
    sm_idle.on_dim_timeout()
    sm_idle.on_button_a()
    assert sm_idle.state == IDLE


def test_power_critical_triggers_shutdown(sm_idle):
    sm_idle.on_power_critical()
    assert sm_idle.state == SHUTDOWN


def test_history_stores_last_20(sm_idle):
    for i in range(25):
        sm_idle.on_detection({"common_name": f"Bird {i}", "confidence": 0.8})
    assert len(sm_idle.history) == 20


def test_history_is_most_recent_first(sm_idle):
    for name in ("Bird A", "Bird B", "Bird C"):
        sm_idle.on_detection({"common_name": name, "confidence": 0.8})
    assert sm_idle.history[0]["common_name"] == "Bird C"
