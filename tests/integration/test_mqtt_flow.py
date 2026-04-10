"""Integration tests: MQTT detection flow.

Skipped on non-Pi hardware.
"""

import json
import subprocess
import time
from datetime import datetime, timezone

import pytest
from tests.conftest import pi_only


@pi_only
@pytest.mark.timeout(30)
def test_synthetic_detection_received():
    payload = json.dumps({
        "common_name": "Test Sparrow",
        "scientific_name": "Passer test",
        "confidence": 0.91,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    result = subprocess.run(
        ["mosquitto_pub", "-t", "birdnet/detection", "-m", payload],
        timeout=5,
    )
    assert result.returncode == 0

    time.sleep(1)
    journal = subprocess.run(
        ["journalctl", "-u", "birdnet-display", "-n", "20", "--no-pager"],
        capture_output=True, text=True,
    )
    assert "Test Sparrow" in journal.stdout
