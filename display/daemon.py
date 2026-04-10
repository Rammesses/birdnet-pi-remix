"""BirdNET-Pi Remix display daemon.

Implements the state machine, MQTT subscription, rendering loop, and button handling.
Logger name: birdnet.display
"""

import atexit
import json
import logging
import os
import time
from datetime import datetime
from enum import Enum, auto

import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont

from display.config import (
    DISPLAY_WIDTH, DISPLAY_HEIGHT,
    MQTT_BROKER, MQTT_PORT, MQTT_TOPIC_DETECTION, MQTT_TOPIC_BATTERY, MQTT_TOPIC_WIFI,
    DETECTION_TIMEOUT_S, DIM_TIMEOUT_S, RENDER_FPS,
)
from display.drivers.st7735 import ST7735Display
from display.input.buttons import ButtonHandler
from display.screens.boot import render_boot
from display.screens.idle import render_idle
from display.screens.detection import render_detection
from display.screens.history import render_history
from display.screens.shutdown import render_shutdown

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("birdnet.display")

FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
MAX_HISTORY = 20
BACKLIGHT_LEVELS = [100, 50, 10]
SLIDE_FRAMES = 8  # 200ms at 15fps


class State(Enum):
    BOOT     = auto()
    IDLE     = auto()
    DETECTION = auto()
    HISTORY  = auto()
    DIM      = auto()
    SHUTDOWN = auto()


class DisplayDaemon:
    """Main display daemon: state machine, rendering loop, MQTT, buttons."""

    def __init__(self):
        self._display = ST7735Display()
        self._state = State.BOOT
        self._prev_state = State.IDLE  # state to return to from HISTORY / DIM

        self._detections: list = []
        self._current_detection: dict = {}
        self._detection_time: float = 0.0
        self._last_button_time: float = time.monotonic()
        self._history_scroll: int = 0

        self._backlight_idx: int = 0  # index into BACKLIGHT_LEVELS
        self._display.set_backlight(BACKLIGHT_LEVELS[0])

        self._battery_pct: int = 100
        self._wifi_connected: bool = False
        self._wifi_configured: bool = False

        self._slide_frame: int = 0   # 0 = settled; >0 = animating
        self._prev_common: str = ""  # detect same-species update

        self._fonts = self._load_fonts()
        self._mqtt = self._setup_mqtt()
        self._buttons = ButtonHandler(
            on_a=self._on_button_a,
            on_b=self._on_button_b,
            on_c_long=self._on_button_c_long,
            on_any=self._reset_dim_timer,
        )
        atexit.register(self._cleanup)

    # ------------------------------------------------------------------
    # Font loading
    # ------------------------------------------------------------------

    def _load_fonts(self) -> dict:
        def f(name, size):
            return ImageFont.truetype(os.path.join(FONT_DIR, name), size)

        return {
            "large":  f("DejaVuSans-Bold.ttf", 28),
            "bold":   f("DejaVuSans-Bold.ttf", 16),
            "italic": f("DejaVuSans-Oblique.ttf", 11),
            "small":  f("DejaVuSans.ttf", 11),
            "tiny":   f("DejaVuSans.ttf", 9),
            "conf":   f("DejaVuSans-Bold.ttf", 13),
        }

    # ------------------------------------------------------------------
    # MQTT
    # ------------------------------------------------------------------

    def _setup_mqtt(self) -> mqtt.Client:
        client = mqtt.Client()
        client.on_connect = self._on_mqtt_connect
        client.on_disconnect = self._on_mqtt_disconnect
        client.on_message = self._on_mqtt_message
        client.connect_async(MQTT_BROKER, MQTT_PORT)
        client.loop_start()
        return client

    def _on_mqtt_connect(self, client, userdata, flags, rc):
        log.info("MQTT connected (rc=%d)", rc)
        client.subscribe(MQTT_TOPIC_DETECTION)
        client.subscribe(MQTT_TOPIC_BATTERY)
        client.subscribe(MQTT_TOPIC_WIFI)
        if self._state == State.BOOT:
            self._transition(State.IDLE)

    def _on_mqtt_disconnect(self, client, userdata, rc):
        log.warning("MQTT disconnected (rc=%d), reconnecting...", rc)

    def _on_mqtt_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            log.warning("Bad MQTT payload on %s: %s", msg.topic, exc)
            return

        if msg.topic == MQTT_TOPIC_DETECTION:
            self._handle_detection(payload)
        elif msg.topic == MQTT_TOPIC_BATTERY:
            self._battery_pct = int(payload.get("percent", self._battery_pct))
            if payload.get("critical"):
                self._transition(State.SHUTDOWN)
        elif msg.topic == MQTT_TOPIC_WIFI:
            self._wifi_connected  = bool(payload.get("connected", False))
            self._wifi_configured = bool(payload.get("configured", False))

    def _handle_detection(self, payload: dict):
        detection = {
            "common_name":     payload.get("common_name", "Unknown"),
            "scientific_name": payload.get("scientific_name", ""),
            "confidence":      float(payload.get("confidence", 0.0)),
            "timestamp":       payload.get("timestamp", datetime.now().isoformat()),
        }
        same_species = detection["common_name"] == self._prev_common
        self._prev_common = detection["common_name"]
        self._current_detection = detection
        self._detection_time = time.monotonic()
        self._detections.insert(0, detection)
        if len(self._detections) > MAX_HISTORY:
            self._detections.pop()

        if not same_species:
            self._slide_frame = SLIDE_FRAMES

        if self._state not in (State.HISTORY, State.SHUTDOWN):
            self._transition(State.DETECTION)

    # ------------------------------------------------------------------
    # Button callbacks
    # ------------------------------------------------------------------

    def _reset_dim_timer(self):
        self._last_button_time = time.monotonic()

    def _on_button_a(self):
        if self._state == State.DIM:
            self._transition(self._prev_state)
            return
        self._backlight_idx = (self._backlight_idx + 1) % len(BACKLIGHT_LEVELS)
        self._display.set_backlight(BACKLIGHT_LEVELS[self._backlight_idx])

    def _on_button_b(self):
        if self._state == State.HISTORY:
            self._transition(self._prev_state)
        elif self._state in (State.IDLE, State.DETECTION):
            self._prev_state = self._state
            self._history_scroll = 0
            self._transition(State.HISTORY)

    def _on_button_c_long(self):
        self._transition(State.SHUTDOWN)

    # ------------------------------------------------------------------
    # State machine
    # ------------------------------------------------------------------

    def _transition(self, new_state: State):
        log.info("State: %s → %s", self._state.name, new_state.name)
        self._state = new_state

    def _check_transitions(self):
        now = time.monotonic()

        if self._state == State.DETECTION:
            if now - self._detection_time > DETECTION_TIMEOUT_S:
                self._transition(State.IDLE)

        if self._state not in (State.DIM, State.SHUTDOWN, State.BOOT):
            if now - self._last_button_time > DIM_TIMEOUT_S:
                self._prev_state = self._state
                self._transition(State.DIM)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _render_frame(self) -> Image.Image:
        image = Image.new("RGB", (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        draw  = ImageDraw.Draw(image)
        f = self._fonts

        if self._state == State.BOOT:
            render_boot(draw, f["bold"], f["small"])

        elif self._state == State.IDLE:
            render_idle(draw, f["large"], f["bold"], f["small"], f["tiny"],
                        self._battery_pct, self._wifi_connected, self._wifi_configured)

        elif self._state == State.DETECTION:
            offset = 0
            if self._slide_frame > 0:
                offset = int((self._slide_frame / SLIDE_FRAMES) * DISPLAY_WIDTH)
                self._slide_frame -= 1
            render_detection(draw, f["bold"], f["italic"], f["small"], f["tiny"],
                             self._current_detection, offset,
                             self._battery_pct, self._wifi_connected, self._wifi_configured)

        elif self._state == State.HISTORY:
            render_history(draw, f["small"], f["tiny"],
                           self._detections, self._history_scroll, self._battery_pct)

        elif self._state == State.DIM:
            # Blank frame; backlight already at 10%
            pass

        elif self._state == State.SHUTDOWN:
            render_shutdown(draw, f["bold"], f["small"])

        return image

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self):
        """Start the rendering loop."""
        log.info("Display daemon starting")
        frame_time = 1.0 / RENDER_FPS
        shutdown_shown_at = None

        while True:
            t0 = time.monotonic()

            self._check_transitions()
            image = self._render_frame()
            self._display.show(image)

            if self._state == State.DIM:
                self._display.set_backlight(10)
            elif self._state == State.SHUTDOWN:
                if shutdown_shown_at is None:
                    shutdown_shown_at = time.monotonic()
                elif time.monotonic() - shutdown_shown_at > 3.0:
                    self._display.clear()
                    break

            elapsed = time.monotonic() - t0
            sleep_for = frame_time - elapsed
            if sleep_for > 0:
                time.sleep(sleep_for)

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def _cleanup(self):
        log.info("Display daemon cleaning up")
        self._buttons.cleanup()
        self._display.cleanup()
        self._mqtt.loop_stop()
        GPIO.cleanup()


def main():
    """Entry point."""
    daemon = DisplayDaemon()
    daemon.run()


if __name__ == "__main__":
    main()
