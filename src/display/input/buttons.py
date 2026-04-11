"""GPIO button handler for BirdNET-Pi Remix."""

import threading
import time
import RPi.GPIO as GPIO

from display.config import BUTTON_A, BUTTON_B, BUTTON_C

DEBOUNCE_MS = 50
LONG_PRESS_S = 3.0


class ButtonHandler:
    """Registers GPIO callbacks for buttons A, B, and C.

    Callbacks:
        on_a()          — Button A short press
        on_b()          — Button B short press
        on_c_long()     — Button C held ≥ 3 seconds
        on_any()        — Any button press (for dim-timer reset)
    """

    def __init__(self, on_a=None, on_b=None, on_c_long=None, on_any=None):
        """Set up GPIO inputs and edge-detection callbacks."""
        self._on_a = on_a or (lambda: None)
        self._on_b = on_b or (lambda: None)
        self._on_c_long = on_c_long or (lambda: None)
        self._on_any = on_any or (lambda: None)
        self._c_press_time = None
        self._c_timer = None

        GPIO.setmode(GPIO.BCM)
        for pin in (BUTTON_A, BUTTON_B, BUTTON_C):
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(BUTTON_A, GPIO.FALLING, callback=self._handle_a, bouncetime=DEBOUNCE_MS)
        GPIO.add_event_detect(BUTTON_B, GPIO.FALLING, callback=self._handle_b, bouncetime=DEBOUNCE_MS)
        GPIO.add_event_detect(BUTTON_C, GPIO.FALLING, callback=self._handle_c_press, bouncetime=DEBOUNCE_MS)
        GPIO.add_event_detect(BUTTON_C, GPIO.RISING,  callback=self._handle_c_release, bouncetime=DEBOUNCE_MS)

    def _handle_a(self, _channel):
        self._on_any()
        self._on_a()

    def _handle_b(self, _channel):
        self._on_any()
        self._on_b()

    def _handle_c_press(self, _channel):
        self._on_any()
        self._c_press_time = time.monotonic()
        self._c_timer = threading.Timer(LONG_PRESS_S, self._fire_c_long)
        self._c_timer.start()

    def _handle_c_release(self, _channel):
        if self._c_timer:
            self._c_timer.cancel()
            self._c_timer = None

    def _fire_c_long(self):
        if self._c_press_time is not None:
            self._on_c_long()

    def cleanup(self) -> None:
        """Remove GPIO event detection."""
        if self._c_timer:
            self._c_timer.cancel()
        for pin in (BUTTON_A, BUTTON_B, BUTTON_C):
            GPIO.remove_event_detect(pin)
