"""Integration tests: verify all systemd services start correctly.

Skipped on non-Pi hardware.
"""

import subprocess
import pytest
from tests.conftest import pi_only


def _service_active(name: str) -> bool:
    result = subprocess.run(
        ["systemctl", "is-active", name],
        capture_output=True, text=True,
    )
    return result.stdout.strip() == "active"


@pi_only
@pytest.mark.timeout(60)
def test_mosquitto_starts():
    assert _service_active("mosquitto")


@pi_only
@pytest.mark.timeout(60)
def test_birdnet_go_starts():
    assert _service_active("birdnet-go")


@pi_only
@pytest.mark.timeout(60)
def test_display_daemon_starts():
    assert _service_active("birdnet-display")


@pi_only
@pytest.mark.timeout(60)
def test_power_daemon_starts():
    assert _service_active("birdnet-power")


@pi_only
@pytest.mark.timeout(60)
def test_all_services_running():
    for svc in ("mosquitto", "birdnet-go", "birdnet-display", "birdnet-power"):
        assert _service_active(svc), f"{svc} is not active"
