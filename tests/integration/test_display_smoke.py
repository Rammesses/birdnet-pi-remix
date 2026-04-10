"""Integration tests: display smoke test — cycle through states and verify no crash.

Skipped on non-Pi hardware.
"""

import json
import subprocess
import time
from datetime import datetime, timezone

import pytest
from tests.conftest import pi_only

_DETECTION = json.dumps({
    "common_name": "Smoke Test Bird",
    "scientific_name": "Testus avius",
    "confidence": 0.85,
    "timestamp": datetime.now(timezone.utc).isoformat(),
})


def _pub(topic: str, msg: str) -> None:
    subprocess.run(["mosquitto_pub", "-t", topic, "-m", msg], timeout=5, check=True)


@pi_only
@pytest.mark.timeout(60)
def test_display_stays_running_through_states():
    # Trigger detection → display should move to DETECTION state
    _pub("birdnet/detection", _DETECTION)
    time.sleep(2)

    # Trigger another detection (same species — no slide)
    _pub("birdnet/detection", _DETECTION)
    time.sleep(2)

    # Trigger a different detection
    _pub("birdnet/detection", json.dumps({
        "common_name": "Another Bird",
        "confidence": 0.70,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }))
    time.sleep(2)

    # Service must still be active after all transitions
    result = subprocess.run(
        ["systemctl", "is-active", "birdnet-display"],
        capture_output=True, text=True,
    )
    assert result.stdout.strip() == "active"
