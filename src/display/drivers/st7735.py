"""ST7735 display driver wrapper using luma.lcd."""

import RPi.GPIO as GPIO
from luma.core.interface.serial import spi
from luma.lcd.device import st7735
from PIL import Image

from display.config import (
    DISPLAY_CS, DISPLAY_DC, DISPLAY_RST, DISPLAY_BL,
    DISPLAY_WIDTH, DISPLAY_HEIGHT,
)


class ST7735Display:
    """Thin wrapper around luma.lcd st7735 device with backlight PWM control."""

    def __init__(self):
        """Initialise SPI interface, luma device, and backlight PWM."""
        serial = spi(port=0, device=0, gpio_DC=DISPLAY_DC, gpio_RST=DISPLAY_RST)
        self._device = st7735(
            serial,
            width=DISPLAY_WIDTH,
            height=DISPLAY_HEIGHT,
            bgr=False,
            h_offset=0,
            v_offset=0,
        )
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(DISPLAY_BL, GPIO.OUT)
        self._pwm = GPIO.PWM(DISPLAY_BL, 1000)
        self._pwm.start(100)

    def show(self, image: Image.Image) -> None:
        """Push a Pillow image to the display."""
        self._device.display(image)

    def set_backlight(self, percent: int) -> None:
        """Set backlight brightness (0–100)."""
        self._pwm.ChangeDutyCycle(max(0, min(100, percent)))

    def clear(self) -> None:
        """Fill display with black."""
        self._device.display(Image.new("RGB", (DISPLAY_WIDTH, DISPLAY_HEIGHT), (0, 0, 0)))

    def cleanup(self) -> None:
        """Release GPIO and PWM resources."""
        self._pwm.stop()
        self._device.cleanup()
