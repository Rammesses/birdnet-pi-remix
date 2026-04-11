"""BirdNET-Pi Remix power manager daemon.

Reads INA219 voltage/current via I²C, publishes battery state to MQTT,
and triggers graceful shutdown when voltage drops below threshold.
Logger name: birdnet.power
"""

import json
import logging
import subprocess
import time

import paho.mqtt.client as mqtt
import smbus2

from display.config import (
    INA219_ADDRESS,
    MQTT_BROKER, MQTT_PORT, MQTT_TOPIC_BATTERY,
    VOLTAGE_WARNING, VOLTAGE_SHUTDOWN, POWER_CHECK_INTERVAL,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("birdnet.power")

# INA219 register addresses
_REG_CONFIG    = 0x00
_REG_SHUNT_V   = 0x01
_REG_BUS_V     = 0x02
_REG_POWER     = 0x03
_REG_CURRENT   = 0x04
_REG_CALIBRATE = 0x05

# Calibration for 0.1Ω shunt, 3.2A max
_CALIBRATION = 4096

# LiPo discharge curve: (voltage, percent) breakpoints
_CURVE = [(4.1, 100), (3.7, 50), (3.5, 20), (3.3, 0)]


def _voltage_to_percent(voltage: float) -> int:
    """Linearly interpolate battery percent from voltage using discharge curve."""
    if voltage >= _CURVE[0][0]:
        return 100
    if voltage <= _CURVE[-1][0]:
        return 0
    for i in range(len(_CURVE) - 1):
        v_hi, p_hi = _CURVE[i]
        v_lo, p_lo = _CURVE[i + 1]
        if v_lo <= voltage <= v_hi:
            t = (voltage - v_lo) / (v_hi - v_lo)
            return int(p_lo + t * (p_hi - p_lo))
    return 0


class INA219:
    """Minimal INA219 driver using smbus2."""

    def __init__(self, bus_number: int = 1, address: int = INA219_ADDRESS):
        self._bus = smbus2.SMBus(bus_number)
        self._addr = address
        # Write calibration register
        self._write_register(_REG_CALIBRATE, _CALIBRATION)

    def _write_register(self, register: int, value: int) -> None:
        data = [(value >> 8) & 0xFF, value & 0xFF]
        self._bus.write_i2c_block_data(self._addr, register, data)

    def _read_register(self, register: int) -> int:
        data = self._bus.read_i2c_block_data(self._addr, register, 2)
        return (data[0] << 8) | data[1]

    def read(self) -> tuple[float, float]:
        """Return (voltage_v, current_ma)."""
        bus_raw = self._read_register(_REG_BUS_V)
        voltage = ((bus_raw >> 3) * 4) / 1000.0  # LSB = 4mV

        shunt_raw = self._read_register(_REG_SHUNT_V)
        if shunt_raw > 32767:
            shunt_raw -= 65536
        current_ma = (shunt_raw * 0.01) / 0.1  # LSB=10µV, shunt=0.1Ω → mA

        return voltage, current_ma

    def close(self) -> None:
        self._bus.close()


def graceful_shutdown(mqtt_client: mqtt.Client) -> None:
    """Publish critical battery state then shut down the system."""
    log.warning("Critical battery voltage — initiating graceful shutdown")
    payload = json.dumps({"critical": True, "percent": 0, "voltage": 0.0, "current_ma": 0.0, "warning": False})
    mqtt_client.publish(MQTT_TOPIC_BATTERY, payload)
    time.sleep(5)  # allow display daemon to show shutdown screen
    subprocess.run(["systemctl", "stop", "birdnet-go"], check=False)
    subprocess.run(["sync"], check=False)
    time.sleep(2)
    subprocess.run(["systemctl", "poweroff"], check=False)


def main() -> None:
    """Entry point for the power manager daemon."""
    log.info("Power daemon starting")

    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.loop_start()

    ina = INA219()

    try:
        while True:
            try:
                voltage, current_ma = ina.read()
            except OSError as exc:
                log.error("INA219 read error: %s", exc)
                time.sleep(POWER_CHECK_INTERVAL)
                continue

            percent = _voltage_to_percent(voltage)
            warning  = voltage < VOLTAGE_WARNING
            critical = voltage < VOLTAGE_SHUTDOWN

            payload = json.dumps({
                "voltage":    round(voltage, 3),
                "percent":    percent,
                "current_ma": round(current_ma, 1),
                "warning":    warning,
                "critical":   critical,
            })
            client.publish(MQTT_TOPIC_BATTERY, payload)
            log.info("Battery: %.3fV  %d%%  %.1fmA", voltage, percent, current_ma)

            if critical:
                graceful_shutdown(client)
                break

            time.sleep(POWER_CHECK_INTERVAL)
    finally:
        ina.close()
        client.loop_stop()


if __name__ == "__main__":
    main()
