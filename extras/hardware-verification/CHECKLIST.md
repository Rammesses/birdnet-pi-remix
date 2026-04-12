# BirdNET-Pi Remix — Hardware Readiness Checklist

Complete all items before final enclosure assembly.
Verification scripts are in `extras/hardware-verification/`.

## SD Card & OS

- [ ] SD card written with Raspberry Pi OS Lite 64-bit (Bookworm)
- [ ] Hostname set to `birdnet-remix`, SSH enabled
- [ ] Pi boots and is reachable via `ssh birdnet-admin@birdnet-remix.local`
- [ ] `uname -a` shows `aarch64`

## Installation

- [ ] `src/install/install.sh` ran without errors
- [ ] `~/install.log` shows clean completion
- [ ] All 4 services active: `systemctl status birdnet-remix.target`

## Peripheral Verification

- [ ] INA219 at `0x40`: `sudo bash extras/hardware-verification/verify_i2c.sh`
- [ ] Display smoke test passes: `sudo python3 extras/hardware-verification/verify_display.py`
- [ ] I²S mic visible to ALSA: `sudo bash extras/hardware-verification/verify_audio.sh`
- [ ] All 3 buttons respond: `sudo python3 extras/hardware-verification/verify_buttons.py`

## System Behaviour

- [ ] Boot splash → Idle transition on service start
- [ ] Synthetic detection triggers Detection screen:
  ```bash
  mosquitto_pub -h localhost -t birdnet/detection -m '{"common_name":"Great Tit","scientific_name":"Parus major","confidence":0.87,"timestamp":"2026-04-08T14:23:11Z"}'
  ```
- [ ] Button A cycles backlight (100% → 50% → 10% → 100%)
- [ ] Button B toggles History screen and back
- [ ] Button C hold (3s) initiates shutdown screen

## Battery & Power

- [ ] Battery MQTT messages published every 30s: `sudo bash extras/hardware-verification/verify_battery_mqtt.sh`
- [ ] Voltage and percent values are plausible for current charge level

## Live Audio

- [ ] BirdNET-Go produces at least one live detection from real audio
  (monitor with `mosquitto_sub -h localhost -t birdnet/detection -v`)

## Graceful Shutdown

- [ ] Shutdown sequence completes cleanly: `sudo bash extras/hardware-verification/verify_shutdown.sh`
- [ ] After reboot: `journalctl --boot=-1 | grep -E "(Stopped BirdNET-Go|sync|poweroff)"` shows expected entries
- [ ] SQLite integrity check passes: `sqlite3 /var/lib/birdnet-go/detections.db "PRAGMA integrity_check;"`
