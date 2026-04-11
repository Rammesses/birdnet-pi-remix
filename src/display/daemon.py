"""BirdNET-Pi Remix display daemon.

Implements the rendering loop, MQTT subscription, and button handling.
State logic is delegated to DisplayStateMachine.
Logger name: birdnet.display
"""

import atexit
import json
import logging
import os
import time

import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont

from display.config import (
    DISPLAY_WIDTH, DISPLAY_HEIGHT,
    MQTT_BROKER, MQTT_PORT, MQTT_TOPIC_DETECTION, MQTT_TOPIC_BATTERY, MQTT_TOPIC_WIFI,
    DIM_TIMEOUT_S, DETECTION_TIMEOUT_S, RENDER_FPS,
)
from display.drivers.st7735 import ST7735Display
from display.input.buttons import ButtonHandler
from display.state_machine import DisplayStateMachine, BOOT, IDLE, DETECTION, HISTORY, DIM, SHUTDOWN
from display.screens.boot import render_boot
from display.screens.idle import render_idle
from display.screens.detection import render_detection
from display.screens.history import render_history
from display.screens.shutdown import render_shutdown

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("birdnet.display")

FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
SLIDE_FRAMES = 8  # 200ms at 15fps


class DisplayDaemon:
    """Main display daemon: rendering loop, MQTT, buttons, state machine."""

    def __init__(self):
        self._display = ST7735Display()
        self._sm = DisplayStateMachine()

        self._battery_pct: int = 100
        self._wifi_connected: bool = False
        self._wifi_configured: bool = False

        self._slide_frame: int = 0
        self._history_scroll: int = 0

        self._last_button_time: float = time.monotonic()
        self._detection_time: float = 0.0

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
        }

    # ------------------------------------------------------------------
    # MQTT
    # ------------------------------------------------------------------

    def _setup_mqtt(self) -> mqtt.Client:
        client = mqtt.Client()
        client.on_connect    = self._on_mqtt_connect
        client.on_disconnect = self._on_mqtt_disconnect
        client.on_message    = self._on_mqtt_message
        client.connect_async(MQTT_BROKER, MQTT_PORT)
        client.loop_start()
        return client

    def _on_mqtt_connect(self, client, userdata, flags, rc):
        log.info("MQTT connected (rc=%d)", rc)
        client.subscribe(MQTT_TOPIC_DETECTION)
        client.subscribe(MQTT_TOPIC_BATTERY)
        client.subscribe(MQTT_TOPIC_WIFI)
        self._sm.on_mqtt_connected()

    def _on_mqtt_disconnect(self, client, userdata, rc):
        log.warning("MQTT disconnected (rc=%d), reconnecting...", rc)

    def _on_mqtt_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            log.warning("Bad MQTT payload on %s: %s", msg.topic, exc)
            return

        if msg.topic == MQTT_TOPIC_DETECTION:
            self._sm.on_detection(payload)
            self._detection_time = time.monotonic()
            if self._sm.slide:
                self._slide_frame = SLIDE_FRAMES
                self._sm.clear_slide()
        elif msg.topic == MQTT_TOPIC_BATTERY:
            self._battery_pct = int(payload.get("percent", self._battery_pct))
            if payload.get("critical"):
                self._sm.on_power_critical()
        elif msg.topic == MQTT_TOPIC_WIFI:
            self._wifi_connected  = bool(payload.get("connected", False))
            self._wifi_configured = bool(payload.get("configured", False))

    # ------------------------------------------------------------------
    # Button callbacks
    # ------------------------------------------------------------------

    def _reset_dim_timer(self):
        self._last_button_time = time.monotonic()

    def _on_button_a(self):
        self._sm.on_button_a()
        self._display.set_backlight(self._sm.backlight_percent)

    def _on_button_b(self):
        self._sm.on_button_b()
        self._history_scroll = 0

    def _on_button_c_long(self):
        self._sm.on_button_c_hold()

    # ------------------------------------------------------------------
    # Timeout checks
    # ------------------------------------------------------------------

    def _check_timeouts(self):
        now = time.monotonic()
        if self._sm.state == DETECTION:
            if now - self._detection_time > DETECTION_TIMEOUT_S:
                self._sm.on_detection_timeout()
        if self._sm.state not in (DIM, SHUTDOWN, BOOT):
            if now - self._last_button_time > DIM_TIMEOUT_S:
                self._sm.on_dim_timeout()

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _render_frame(self) -> Image.Image:
        image = Image.new("RGB", (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        draw  = ImageDraw.Draw(image)
        f = self._fonts
        state = self._sm.state

        if state == BOOT:
            render_boot(draw, f["bold"], f["small"])

        elif state == IDLE:
            render_idle(draw, f["large"], f["bold"], f["small"], f["tiny"],
                        self._battery_pct, self._wifi_connected, self._wifi_configured)

        elif state == DETECTION:
            offset = 0
            if self._slide_frame > 0:
                offset = int((self._slide_frame / SLIDE_FRAMES) * DISPLAY_WIDTH)
                self._slide_frame -= 1
            render_detection(draw, f["bold"], f["italic"], f["small"], f["tiny"],
                             self._sm.last_detection or {}, offset,
                             self._battery_pct, self._wifi_connected, self._wifi_configured)

        elif state == HISTORY:
            render_history(draw, f["small"], f["tiny"],
                           self._sm.history, self._history_scroll, self._battery_pct)

        elif state == SHUTDOWN:
            render_shutdown(draw, f["bold"], f["small"])

        # DIM: blank frame, backlight handled separately

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
            self._check_timeouts()
            image = self._render_frame()
            self._display.show(image)

            if self._sm.state == DIM:
                self._display.set_backlight(10)
            elif self._sm.state == SHUTDOWN:
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
