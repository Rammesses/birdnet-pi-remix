"""Display state machine for BirdNET-Pi Remix.

Pure logic class with no I/O dependencies — fully testable on any machine.
"""

from datetime import datetime

from display.config import (
    BACKLIGHT_LEVELS,
    DETECTION_TIMEOUT_S,
    DIM_TIMEOUT_S,
)

MAX_HISTORY = 20

# State constants
BOOT      = "BOOT"
IDLE      = "IDLE"
DETECTION = "DETECTION"
HISTORY   = "HISTORY"
DIM       = "DIM"
SHUTDOWN  = "SHUTDOWN"


class DisplayStateMachine:
    """State machine for the display daemon.

    All transitions are driven by explicit event methods.
    Time-based transitions (dim, detection timeout) are driven by the caller
    via ``on_dim_timeout()`` and ``on_detection_timeout()``.
    """

    def __init__(self):
        self._state: str = BOOT
        self._prev_state: str = IDLE
        self._backlight_idx: int = 0
        self._last_detection: dict | None = None
        self._history: list[dict] = []
        self._prev_common: str = ""
        self._slide: bool = False  # True when a slide-in animation should start

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def on_mqtt_connected(self) -> None:
        """MQTT broker became reachable — leave BOOT state."""
        if self._state == BOOT:
            self._transition(IDLE)

    def on_detection(self, payload: dict) -> None:
        """A detection MQTT message was received."""
        detection = {
            "common_name":     payload.get("common_name", "Unknown"),
            "scientific_name": payload.get("scientific_name", ""),
            "confidence":      min(1.0, float(payload.get("confidence", 0.0))),
            "timestamp":       payload.get("timestamp", datetime.now().isoformat()),
        }
        same_species = detection["common_name"] == self._prev_common
        self._prev_common = detection["common_name"]
        self._slide = not same_species
        self._last_detection = detection
        self._history.insert(0, detection)
        if len(self._history) > MAX_HISTORY:
            self._history.pop()

        if self._state not in (HISTORY, SHUTDOWN):
            self._transition(DETECTION)

    def on_button_a(self) -> None:
        """Button A pressed — cycle backlight or wake from DIM."""
        if self._state == DIM:
            self._transition(self._prev_state)
            return
        self._backlight_idx = (self._backlight_idx + 1) % len(BACKLIGHT_LEVELS)

    def on_button_b(self) -> None:
        """Button B pressed — toggle History / back."""
        if self._state == HISTORY:
            self._transition(self._prev_state)
        elif self._state in (IDLE, DETECTION):
            self._prev_state = self._state
            self._transition(HISTORY)

    def on_button_c_hold(self) -> None:
        """Button C held ≥ 3 seconds — initiate shutdown."""
        self._transition(SHUTDOWN)

    def on_dim_timeout(self) -> None:
        """60 seconds elapsed with no button press."""
        if self._state not in (DIM, SHUTDOWN):
            self._prev_state = self._state
            self._transition(DIM)

    def on_detection_timeout(self) -> None:
        """30 seconds elapsed with no new detection on DETECTION screen."""
        if self._state == DETECTION:
            self._transition(IDLE)

    def on_power_critical(self) -> None:
        """Battery voltage dropped below shutdown threshold."""
        self._transition(SHUTDOWN)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def state(self) -> str:
        return self._state

    @property
    def backlight_percent(self) -> int:
        return BACKLIGHT_LEVELS[self._backlight_idx]

    @property
    def last_detection(self) -> dict | None:
        return self._last_detection

    @property
    def history(self) -> list[dict]:
        return list(self._history)

    @property
    def slide(self) -> bool:
        """True if the next render should start a slide-in animation."""
        return self._slide

    def clear_slide(self) -> None:
        """Called by the renderer after consuming the slide flag."""
        self._slide = False

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _transition(self, new_state: str) -> None:
        self._state = new_state
