# Kiro Specification: BirdNET-Pi Remix — Verification & Testing

## Overview

This document specifies how to verify that the BirdNET-Pi Remix software stack
is correct, before any real hardware is available. Tests are structured in three
tiers:

1. **Unit tests** — individual components tested in isolation on any machine
2. **Integration tests** — services tested together on a Pi Zero 2W (or Pi OS VM)
3. **Acceptance criteria** — end-to-end checks that map directly to the project's
   success criteria from `01-project-overview.md`

All unit and most integration tests must be able to run on a development machine
(x86-64 Linux or macOS) without hardware attached.

---

## Test Framework

Use `pytest` with the following plugins:

```
pytest>=7.0
pytest-mock>=3.10
pytest-timeout>=2.1
```

Add to `requirements-dev.txt` (separate from `requirements.txt`).

Test directory layout:

```
tests/
├── conftest.py
├── unit/
│   ├── test_config.py
│   ├── test_state_machine.py
│   ├── test_battery_component.py
│   ├── test_detection_screen.py
│   ├── test_history_screen.py
│   ├── test_idle_screen.py
│   ├── test_power_daemon.py
│   └── test_mqtt_schema.py
└── integration/
    ├── test_service_startup.py
    ├── test_mqtt_flow.py
    └── test_display_smoke.py
```

---

## Hardware Mocking Strategy

Because tests run without hardware, all hardware-dependent libraries must be
mockable. The following mocks must be provided in `tests/conftest.py`:

### RPi.GPIO mock

```python
@pytest.fixture(autouse=True)
def mock_gpio(monkeypatch):
    """Replace RPi.GPIO with a no-op mock for all tests."""
    mock = MagicMock()
    monkeypatch.setitem(sys.modules, 'RPi', mock)
    monkeypatch.setitem(sys.modules, 'RPi.GPIO', mock.GPIO)
    return mock
```

### luma.lcd mock

```python
@pytest.fixture
def mock_display(monkeypatch):
    """Replace ST7735Display with a mock that captures rendered frames."""
    frames = []
    mock = MagicMock()
    mock.show.side_effect = lambda img: frames.append(img.copy())
    monkeypatch.setattr('display.drivers.st7735.ST7735Display', lambda: mock)
    return mock, frames
```

### smbus2 / INA219 mock

```python
@pytest.fixture
def mock_ina219(monkeypatch):
    """Return controllable voltage/current readings."""
    readings = {'voltage': 3.85, 'current': 210.0}
    mock_bus = MagicMock()
    mock_bus.read_i2c_block_data.return_value = encode_ina219(readings)
    monkeypatch.setitem(sys.modules, 'smbus2', MagicMock(SMBus=lambda _: mock_bus))
    return readings
```

### paho-mqtt mock

```python
@pytest.fixture
def mqtt_harness():
    """In-process MQTT harness using a dict of topic→[payloads]."""
    # Uses paho.mqtt.client loopback mode, or a simple dict-based mock
    ...
```

---

## Unit Tests

### `test_config.py`

| Test | Assertion |
|------|-----------|
| `test_all_gpio_constants_defined` | All pin constants in `config.py` are integers |
| `test_all_colour_constants_are_rgb_tuples` | All `COL_*` constants are 3-tuples of ints in range 0–255 |
| `test_display_dimensions` | `DISPLAY_WIDTH == 160`, `DISPLAY_HEIGHT == 128` |
| `test_voltage_thresholds_ordered` | `VOLTAGE_SHUTDOWN < VOLTAGE_WARNING` |

---

### `test_state_machine.py`

The state machine must be testable independently of the display hardware.
Extract state-machine logic into a class `DisplayStateMachine` in
`display/state_machine.py` with no I/O dependencies.

```python
class DisplayStateMachine:
    def __init__(self): ...
    def on_mqtt_connected(self): ...
    def on_detection(self, payload: dict): ...
    def on_button_a(self): ...
    def on_button_b(self): ...
    def on_button_c_hold(self): ...
    def on_dim_timeout(self): ...
    def on_detection_timeout(self): ...
    def on_power_critical(self): ...
    @property
    def state(self) -> str: ...
    @property
    def backlight_percent(self) -> int: ...
    @property
    def last_detection(self) -> dict | None: ...
    @property
    def history(self) -> list[dict]: ...
```

| Test | Precondition | Event | Expected state |
|------|-------------|-------|---------------|
| `test_boot_to_idle` | state=BOOT | `on_mqtt_connected()` | IDLE |
| `test_idle_to_detection` | state=IDLE | `on_detection({...})` | DETECTION |
| `test_detection_timeout_to_idle` | state=DETECTION | `on_detection_timeout()` | IDLE |
| `test_new_detection_resets_timer` | state=DETECTION | `on_detection({...})` | DETECTION |
| `test_button_b_idle_to_history` | state=IDLE | `on_button_b()` | HISTORY |
| `test_button_b_detection_to_history` | state=DETECTION | `on_button_b()` | HISTORY |
| `test_button_b_history_returns_to_idle` | state=HISTORY (from IDLE) | `on_button_b()` | IDLE |
| `test_button_b_history_returns_to_detection` | state=HISTORY (from DETECTION) | `on_button_b()` | DETECTION |
| `test_button_a_cycles_backlight` | backlight=100 | `on_button_a()` × 3 | 100→50→10→100 |
| `test_button_c_hold_triggers_shutdown` | any state | `on_button_c_hold()` | SHUTDOWN |
| `test_dim_timeout_any_state` | state=IDLE | `on_dim_timeout()` | DIM |
| `test_button_wake_from_dim` | state=DIM | `on_button_a()` | IDLE |
| `test_power_critical_triggers_shutdown` | state=IDLE | `on_power_critical()` | SHUTDOWN |
| `test_history_stores_last_20` | 25 detections received | — | `len(history) == 20` |
| `test_history_is_most_recent_first` | 3 detections A, B, C | — | `history[0]` is C |

---

### `test_power_daemon.py`

| Test | Setup | Assertion |
|------|-------|-----------|
| `test_voltage_to_percent_full` | voltage=4.1 | returns 100 |
| `test_voltage_to_percent_half` | voltage=3.7 | returns 50 |
| `test_voltage_to_percent_empty` | voltage=3.3 | returns 0 |
| `test_voltage_to_percent_interpolates` | voltage=3.9 | between 50 and 100 |
| `test_voltage_below_shutdown_triggers_critical` | voltage=3.2, mock MQTT | publishes `critical: true` |
| `test_voltage_in_warning_range` | voltage=3.4 | publishes `warning: true`, `critical: false` |
| `test_graceful_shutdown_calls_systemctl` | critical condition | `systemctl stop birdnet-go` called |

---

### `test_mqtt_schema.py`

| Test | Payload | Assertion |
|------|---------|-----------|
| `test_full_payload_parsed` | All fields present | All fields extracted correctly |
| `test_missing_common_name` | No `common_name` key | Defaults to `"Unknown"` |
| `test_missing_confidence` | No `confidence` key | Defaults to `0.0` |
| `test_confidence_clamped` | `confidence: 1.5` | Stored as `1.0` |
| `test_invalid_json_ignored` | `"not json"` | No exception raised, detection ignored |

---

### `test_detection_screen.py`

Using `mock_display` fixture:

| Test | Assertion |
|------|-----------|
| `test_common_name_rendered` | Pixel region y=14–32 is non-background |
| `test_confidence_bar_full` | Bar width at 100% confidence spans full width |
| `test_confidence_bar_empty` | Bar width at 0% confidence is background colour only |
| `test_slide_animation_produces_frames` | First 8 frames differ in x-position of name |
| `test_same_species_no_slide` | Second detection of same species: frames 1 and 2 have same x |

---

### `test_battery_component.py`

| Test | Input | Assertion |
|------|-------|-----------|
| `test_battery_icon_good_colour` | percent=80 | Uses `COL_BATT_GOOD` |
| `test_battery_icon_low_colour` | percent=30 | Uses `COL_BATT_LOW` |
| `test_battery_icon_critical_colour` | percent=10 | Uses `COL_BATT_CRIT` |
| `test_battery_renders_percentage_text` | percent=73 | Rendered image contains "73%" text region |

---

## Integration Tests

These tests require either a real Pi Zero 2W or a Pi OS arm64 QEMU VM.
They are tagged `@pytest.mark.integration` and skipped by default on non-Pi hosts.

Add skip logic in `conftest.py`:
```python
import platform
running_on_pi = platform.machine() == "aarch64" and Path("/proc/device-tree/model").exists()
pi_only = pytest.mark.skipif(not running_on_pi, reason="Requires Raspberry Pi hardware")
```

### `test_service_startup.py`

| Test | Method | Pass criterion |
|------|--------|---------------|
| `test_mosquitto_starts` | `systemctl is-active mosquitto` | Returns `active` |
| `test_birdnet_go_starts` | `systemctl is-active birdnet-go` | Returns `active` within 30s |
| `test_display_daemon_starts` | `systemctl is-active birdnet-display` | Returns `active` within 15s |
| `test_power_daemon_starts` | `systemctl is-active birdnet-power` | Returns `active` within 10s |
| `test_all_services_running` | Check all 4 services | All return `active` |

Timeout: each test has a 60-second timeout via `@pytest.mark.timeout(60)`.

---

### `test_mqtt_flow.py`

Publish a synthetic detection message to `birdnet/detection` using
`mosquitto_pub` and verify the display daemon receives it.

```python
def test_synthetic_detection_received():
    payload = json.dumps({
        "common_name": "Test Sparrow",
        "scientific_name": "Passer test",
        "confidence": 0.91,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })
    result = subprocess.run(
        ["mosquitto_pub", "-t", "birdnet/detection", "-m", payload],
        timeout=5
    )
    assert result.returncode == 0
    # Verify display daemon log shows receipt
    time.sleep(1)
    journal = subprocess.run(
        ["journalctl", "-u", "birdnet-display", "-n", "20", "--no-pager"],
        capture_output=True, text=True
    )
    assert "Test Sparrow" in journal.stdout
```

---

### `test_display_smoke.py`

Verify the physical display is working by commanding the display daemon to
show each screen in sequence and checking no service crash occurs.

```python
def test_display_stays_running_through_states():
    # Trigger each state via MQTT
    for payload in [BOOT_TRIGGER, DETECTION_PAYLOAD, HISTORY_TRIGGER, IDLE_TRIGGER]:
        subprocess.run(["mosquitto_pub", "-t", payload["topic"], "-m", payload["msg"]])
        time.sleep(2)
    # Service must still be active after all transitions
    result = subprocess.run(["systemctl", "is-active", "birdnet-display"],
                            capture_output=True, text=True)
    assert result.stdout.strip() == "active"
```

---

## Acceptance Criteria Verification

These map directly to the success criteria in `01-project-overview.md`.

### AC-1: Detection latency ≤ 5 seconds

**Method:** Play a 3-second WAV file of a known bird call through the ALSA loopback
device on the Pi. Measure time from playback start to detection MQTT message appearing
on `birdnet/detection`.

```bash
# Setup: configure ALSA loopback module
modprobe snd-aloop
# Route test audio into BirdNET-Go's capture device
aplay -D hw:Loopback,0,0 test_audio/great_tit_call.wav &
# Timestamp MQTT message arrival
mosquitto_sub -t birdnet/detection -C 1 | python3 -c "
import sys, time, json
line = sys.stdin.readline()
print(f'Detection received at: {time.time()}')"
```

Pass: detection message received within 5 seconds of audio playback start.

### AC-2: Battery life ≥ 6 hours

**Method (pre-hardware):** Calculate from power budget.
- Pi Zero 2W: 300mA @ 5V worst case
- ST7735: 30mA @ 3.3V
- SPH0645: 0.6mA
- Boost converter efficiency: ~85%
- Total draw from LiPo: ~(330mA × 5V) / (3.7V × 0.85) ≈ 524mA
- 2000mAh / 524mA ≈ 3.8 hours on 2000mAh cell
- 3000mAh / 524mA ≈ 5.7 hours

**Action:** Flag this as a known gap — the 2000mAh cell does not meet the 6-hour
target under worst-case load. Update BoM to specify **3000mAh minimum** and note
this in `09-open-questions.md`. The power daemon's battery % readings will allow
real-world runtime to be measured once hardware is available.

**Hardware test (when available):** Run device from full charge with BirdNET-Go
active and periodic audio input, log timestamps of first boot and power-critical
shutdown. Verify ≥ 6 hours elapsed.

### AC-3: Bootup time ≤ 60 seconds

**Method:** Log timestamp at systemd `default.target` completion and at
`birdnet-remix.target` active state. Difference must be ≤ 60 seconds.

```bash
systemd-analyze blame | head -20
systemd-analyze critical-chain birdnet-remix.target
```

Pass: `birdnet-display.service` reaches active state within 60 seconds of power-on.

### AC-4: Graceful shutdown completes cleanly

**Method:** Trigger Button C hold (or publish `{"critical": true}` to
`birdnet/battery`) and verify:

```bash
# After shutdown sequence completes, inspect journal
journalctl --boot=-1 | grep -E "(birdnet-go|sync|poweroff)"
```

Pass criteria:
- `systemctl stop birdnet-go` appears in journal before poweroff
- No filesystem errors on next boot (`journalctl -b -p err` is clean)
- SQLite database at `/var/lib/birdnet-go/detections.db` is not corrupted
  (check with `sqlite3 /var/lib/birdnet-go/detections.db "PRAGMA integrity_check;"`)

### AC-5: Identification accuracy not degraded

**Method:** Run BirdNET-Go's own built-in test suite (if available) against a
set of reference WAV files. Compare detection confidence scores to known baseline.

This is a BirdNET-Go integration concern, not a display daemon concern. Our
responsibility is to pass through the confidence value from MQTT without rounding
or modification. Verify via unit test `test_confidence_not_modified`:

```python
def test_confidence_not_modified():
    payload = {"confidence": 0.873456}
    detection = parse_detection_payload(json.dumps(payload))
    assert detection["confidence"] == pytest.approx(0.873456, rel=1e-4)
```

---

## Running the Test Suite

```bash
# Development machine (unit tests only)
pip install -r requirements-dev.txt
pytest tests/unit/ -v

# On Pi (unit + integration)
pytest tests/ -v --timeout=120

# Run with coverage report
pytest tests/unit/ --cov=display --cov=power --cov-report=term-missing
```

Target: **unit test coverage ≥ 80%** for `display/` and `power/` modules.
