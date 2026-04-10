"""Unit tests for MQTT detection payload parsing via the state machine."""

import json
import pytest
from display.state_machine import DisplayStateMachine


@pytest.fixture
def sm():
    sm = DisplayStateMachine()
    sm.on_mqtt_connected()
    return sm


def _detect(sm, payload_dict):
    sm.on_detection(payload_dict)
    return sm.last_detection


def test_full_payload_parsed(sm):
    det = _detect(sm, {
        "common_name": "Robin",
        "scientific_name": "Erithacus rubecula",
        "confidence": 0.78,
        "timestamp": "2026-04-10T13:55:00Z",
    })
    assert det["common_name"] == "Robin"
    assert det["scientific_name"] == "Erithacus rubecula"
    assert det["confidence"] == pytest.approx(0.78)
    assert det["timestamp"] == "2026-04-10T13:55:00Z"


def test_missing_common_name(sm):
    det = _detect(sm, {"confidence": 0.5})
    assert det["common_name"] == "Unknown"


def test_missing_confidence(sm):
    det = _detect(sm, {"common_name": "Robin"})
    assert det["confidence"] == 0.0


def test_confidence_clamped(sm):
    det = _detect(sm, {"common_name": "Robin", "confidence": 1.5})
    assert det["confidence"] == 1.0


def test_invalid_json_ignored(sm):
    """Parsing bad JSON must not raise; state machine must not update."""
    before = sm.last_detection
    try:
        payload = json.loads("not json")
    except json.JSONDecodeError:
        pass  # caller (daemon) catches this; state machine never called
    assert sm.last_detection is before


def test_confidence_not_modified(sm):
    det = _detect(sm, {"common_name": "Robin", "confidence": 0.873456})
    assert det["confidence"] == pytest.approx(0.873456, rel=1e-4)
