# Kiro Specification: BirdNET-Pi Remix — Hardware Provisioning

## Overview

This document specifies how to prepare, configure, and verify a physical
Raspberry Pi Zero 2W for the BirdNET-Pi Remix software. It covers:

1. SD card preparation and first-boot OS configuration
2. Running the installation script
3. Breadboard bring-up and hardware verification procedure
4. Per-peripheral smoke tests (audio, display, power monitor, buttons)
5. End-to-end functional verification before enclosure assembly

---

## Bill of Materials (Breadboard Prototype)

The following parts are needed for breadboard bring-up. Refer to `03-bill-of-materials.md`
for full sourcing details.

| Part | Qty | Notes |
|------|-----|-------|
| Raspberry Pi Zero 2W | 1 | With soldered GPIO header |
| MicroSD card ≥32GB (A1/A2) | 1 | SanDisk MAX Endurance preferred |
| ST7735 1.8" TFT breakout | 1 | With SPI pins broken out |
| Adafruit SPH0645 I²S mic breakout | 1 | With header pins soldered |
| INA219 I²C breakout module | 1 | Standard eBay/Amazon module with 0.1Ω shunt |
| TP4056 USB-C charger module (with protection) | 1 | DW01A variant |
| MT3608 boost converter module | 1 | Adjustable output |
| LiPo cell 3.7V 3000mAh | 1 | JST-PH 2mm connector |
| Tactile push buttons | 3 | 6mm × 6mm |
| 1N5819 Schottky diode | 1 | Back-feed protection |
| 100µF 10V electrolytic capacitor | 1 | Boost output filter |
| 47Ω resistor | 1 | Display backlight |
| 10kΩ resistors | 3 | Button pull-ups (if not using software pull-ups) |
| Breadboard (830 tie-point) | 1 | |
| Dupont jumper wires (F-F, M-F, M-M) | 40+ | Assorted |
| USB-C cable | 1 | For charging |
| USB-A to Micro-USB cable | 1 | For initial Pi power during setup |
| Multimeter | 1 | Essential for power circuit verification |

---

## Step 1: SD Card Preparation

### 1.1 Flash the OS

1. Download **Raspberry Pi Imager** from https://www.raspberrypi.com/software/
2. Select OS: **Raspberry Pi OS Lite (64-bit)** — Bookworm
3. Select your SD card
4. Click the ⚙️ gear icon before writing to pre-configure:

   | Setting | Value |
   |---------|-------|
   | Hostname | `birdnet-remix` |
   | Enable SSH | Yes — password authentication |
   | Username | `birdnet-admin` |
   | Password | (your choice — note it down) |
   | Wi-Fi SSID | Your home network |
   | Wi-Fi password | Your home network password |
   | Locale | Europe/London, keyboard gb |

5. Write the image. Wait for verification to complete.

### 1.2 Verify the SD card

Before inserting into the Pi, mount the SD card on your computer and confirm:
- `/boot/firmware/` exists and contains `config.txt`
- `/boot/firmware/ssh` file is present (SSH enabled)

---

## Step 2: Power Circuit Assembly (Do This Before Connecting the Pi)

**Important:** Assemble and verify the power circuit on the breadboard before
connecting the Pi Zero 2W. An incorrectly adjusted boost converter will destroy
the Pi.

### 2.1 Boost converter adjustment

1. Connect the TP4056 module to a bench USB-C supply (or phone charger)
2. Connect the LiPo cell to TP4056 BAT+/BAT-
3. Connect TP4056 BAT+/BAT- output to MT3608 VIN+/VIN-
4. Do **not** connect the Pi yet
5. Power on the USB-C supply — TP4056 CHRG LED should illuminate
6. Measure MT3608 VOUT with multimeter
7. Adjust MT3608 trim potentiometer until VOUT reads **5.10V ± 0.05V**
   - Clockwise increases voltage on most MT3608 modules
   - Do not exceed 5.25V
8. Note this voltage and proceed

### 2.2 Power circuit wiring

```
USB-C (5V) → TP4056 IN+ / IN-
TP4056 BAT+ → INA219 VIN+
TP4056 BAT- → GND rail
LiPo JST → TP4056 BAT connector
INA219 VIN- → MT3608 VIN+
MT3608 VIN- → GND rail
MT3608 VOUT → 1N5819 Anode
1N5819 Cathode → 100µF cap (+) → Pi 5V (Pin 2)
100µF cap (-) → GND rail
Pi GND (Pin 6) → GND rail
```

### 2.3 Power circuit verification (before connecting Pi)

With LiPo connected and USB-C power applied:
- Multimeter across Pi Pin 2 and Pin 6: should read **4.9–5.1V**
- Multimeter across INA219 VIN+ and VIN-: should read **< 0.05V** (shunt drop)
- TP4056 CHRG LED: on (charging), STBY LED: on when full

If voltage is outside 4.75–5.25V: **stop and recheck before connecting Pi.**

---

## Step 3: First Boot and SSH Access

### 3.1 Initial connection

1. Insert the prepared SD card into the Pi Zero 2W
2. Connect the Pi to the power circuit (5V to Pin 2, GND to Pin 6)
3. Alternatively, for initial setup, power via Micro-USB power port on the Pi
4. Wait ~60 seconds for first boot
5. Find the Pi's IP address: check your router's DHCP list, or use:
   ```bash
   ping birdnet-remix.local
   ```
6. SSH in:
   ```bash
   ssh birdnet-admin@birdnet-remix.local
   ```

### 3.2 Verify base system

```bash
uname -a          # Should show: aarch64 GNU/Linux ... aarch64
cat /etc/os-release | grep VERSION   # Should show: Bookworm
df -h /           # Verify ~28GB available on 32GB card
```

---

## Step 4: Repository Deployment and Installation

### 4.1 Clone the repository

```bash
sudo apt-get install -y git
git clone https://github.com/Rammesses/birdnet-pi-remix.git
cd birdnet-pi-remix
```

### 4.2 Run the installation script

```bash
chmod +x install/install.sh
sudo bash install/install.sh 2>&1 | tee ~/install.log
```

The script will:
- Apply `config.txt` changes (I²S, SPI, I²C)
- Install all system packages and Python dependencies
- Download BirdNET-Go binary
- Prompt for BirdWeather token and Wi-Fi credentials
- Enable all services
- Reboot automatically

**Expected duration:** 5–10 minutes depending on network speed.

### 4.3 Post-reboot verification

After reboot, SSH back in and check:

```bash
systemctl status birdnet-remix.target
systemctl status mosquitto
systemctl status birdnet-go
systemctl status birdnet-display
systemctl status birdnet-power
```

All should show `active (running)`. If any service failed:
```bash
journalctl -u birdnet-<service> -n 50
```

---

## Step 5: Peripheral Wiring (Breadboard)

Wire peripherals one at a time, verifying each before adding the next.
Power off the Pi between wiring changes.

### 5.1 I²C Power Monitor (INA219)

Wire per `04-hardware-design.md`:

```
INA219 VCC  → Pin 1  (3.3V)
INA219 GND  → Pin 6  (GND)
INA219 SDA  → Pin 3  (GPIO 2)
INA219 SCL  → Pin 5  (GPIO 3)
```

**Verify:**
```bash
sudo i2cdetect -y 1
```
Expected output: `0x40` visible in the grid.

If not visible:
- Check `dtparam=i2c_arm=on` is in `/boot/firmware/config.txt`
- Check wiring continuity with multimeter
- Verify 3.3V present on INA219 VCC pin

### 5.2 ST7735 Display

Wire per `04-hardware-design.md`:

```
ST7735 VCC   → Pin 1  (3.3V)
ST7735 GND   → Pin 6  (GND)
ST7735 CS    → Pin 24 (GPIO 8)
ST7735 RESET → Pin 22 (GPIO 25)
ST7735 DC    → Pin 18 (GPIO 24)
ST7735 MOSI  → Pin 19 (GPIO 10)
ST7735 SCK   → Pin 23 (GPIO 11)
ST7735 LED   → 47Ω → Pin 1 (3.3V)
              (or GPIO 12 for PWM backlight control)
```

**Verify:**
```bash
ls /dev/spidev0.*   # Should show /dev/spidev0.0
```

Run the display smoke test:
```bash
cd /opt/birdnet-remix
sudo venv/bin/python3 -c "
from display.drivers.st7735 import ST7735Display
from PIL import Image, ImageDraw
d = ST7735Display()
img = Image.new('RGB', (160, 128), (13, 27, 14))
draw = ImageDraw.Draw(img)
draw.text((10, 50), 'Hello Bird!', fill=(240, 236, 216))
d.show(img)
print('Display OK')
"
```

Expected: "Hello Bird!" appears on the TFT in white on dark green.

### 5.3 SPH0645 I²S Microphone

Wire per `04-hardware-design.md`:

```
SPH0645 3V    → Pin 1  (3.3V)
SPH0645 GND   → Pin 6  (GND)
SPH0645 BCLK  → Pin 12 (GPIO 18)
SPH0645 LRCLK → Pin 35 (GPIO 19)
SPH0645 DOUT  → Pin 38 (GPIO 20)
SPH0645 SEL   → GND    (left channel)
```

**Verify:**
```bash
arecord -l    # Should list: card 0, device 0: I2S [...]
```

Record 5 seconds of audio and check for non-zero data:
```bash
arecord -D hw:0,0 -f S32_LE -r 48000 -c 2 -d 5 /tmp/test.wav
aplay /tmp/test.wav     # Should play back ambient sound (may be quiet)
# OR check file is non-trivially sized:
ls -lh /tmp/test.wav    # Should be ~1.8MB for 5s at 48kHz stereo 32-bit
```

If `arecord -l` shows no cards:
- Check `dtparam=i2s=on` and `dtoverlay=i2s-mmap` in `/boot/firmware/config.txt`
- Verify BCLK, LRCLK, DOUT continuity
- Check `dtparam=audio=off` is set (conflicts with I²S if on)

### 5.4 Buttons

Wire per `04-hardware-design.md`:

```
Button A → GPIO 16 (Pin 36) + GND
Button B → GPIO 26 (Pin 37) + GND
Button C → GPIO 21 (Pin 40) + GND
```

**Verify:**
```bash
sudo venv/bin/python3 -c "
import RPi.GPIO as GPIO, time
GPIO.setmode(GPIO.BCM)
for pin in [16, 26, 21]:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
print('Press each button in sequence: A, B, C')
for label, pin in [('A',16),('B',26),('C',21)]:
    while GPIO.input(pin) == 1:
        pass
    print(f'Button {label} OK')
    time.sleep(0.3)
GPIO.cleanup()
"
```

---

## Step 6: Full System Bring-Up

With all peripherals wired:

### 6.1 Start all services

```bash
sudo systemctl restart birdnet-remix.target
```

Watch the display: boot splash should appear within 10 seconds, then transition
to the Idle (clock) screen once BirdNET-Go and MQTT are ready.

### 6.2 Trigger a synthetic detection

On the Pi (or from another machine on the same network):

```bash
mosquitto_pub -h localhost -t birdnet/detection -m '{
  "common_name": "Great Tit",
  "scientific_name": "Parus major",
  "confidence": 0.87,
  "timestamp": "2026-04-08T14:23:11Z"
}'
```

Expected: Detection screen appears on the TFT within 1 second of command.

### 6.3 Verify button interactions

| Action | Expected result |
|--------|-----------------|
| Press Button A once | Backlight dims to 50% |
| Press Button A again | Backlight dims to 10% |
| Press Button A again | Backlight returns to 100% |
| Press Button B | History screen shown |
| Press Button B again | Returns to previous screen |
| Hold Button C for 3 seconds | Shutdown screen; system powers off |

### 6.4 Verify battery monitoring

```bash
mosquitto_sub -h localhost -t birdnet/battery -v
```

Expected output every 30 seconds:
```
birdnet/battery {"voltage": 3.87, "percent": 75, "current_ma": 215.3, "warning": false, "critical": false}
```

Battery % and voltage must correspond to the LiPo discharge curve.

---

## Step 7: BirdNET-Go Live Audio Test

With microphone wired and all services running:

1. Place the device near a window or play a bird call recording
   (test WAV files available at https://xeno-canto.org)
2. Watch the display and/or monitor MQTT:
   ```bash
   mosquitto_sub -h localhost -t birdnet/detection -v
   ```
3. A detection should appear within a few seconds of a clear bird call

**If no detections appear after 2 minutes of clear audio:**
- Check BirdNET-Go is running: `systemctl status birdnet-go`
- Check ALSA device is correct in `/etc/birdnet-go/config.yaml` (`input.device`)
- Check BirdNET-Go logs: `journalctl -u birdnet-go -n 50`
- Lower the detection threshold temporarily in config: `threshold: 0.5`

---

## Step 8: Graceful Shutdown Verification

```bash
# Simulate power-critical condition
mosquitto_pub -h localhost -t birdnet/battery -m '{
  "voltage": 3.2, "percent": 0, "critical": true
}'
```

Expected sequence:
1. Shutdown screen appears on display
2. ~5 seconds later, `birdnet-go.service` stops
3. `sync` runs
4. System powers off

After power-on, verify:
```bash
journalctl --boot=-1 | grep -E "(Stopped BirdNET-Go|sync|poweroff)"
sqlite3 /var/lib/birdnet-go/detections.db "PRAGMA integrity_check;"
# Expected: ok
```

---

## Troubleshooting Reference

| Symptom | First checks |
|---------|-------------|
| Display blank after wiring | `ls /dev/spidev0.0`; check CS/DC/RST wiring; verify 3.3V on VCC |
| No audio device | `arecord -l`; check `config.txt` overlays; check `dtparam=audio=off` |
| INA219 not on I²C bus | `i2cdetect -y 1`; check SDA/SCL; check 3.3V on VCC |
| birdnet-go fails to start | `journalctl -u birdnet-go`; check ALSA device name; check config.yaml |
| Display daemon crashes | `journalctl -u birdnet-display`; check SPI device; check GPIO pin conflicts |
| No MQTT messages | `systemctl status mosquitto`; check mosquitto.conf; `mosquitto_sub -t '#'` |
| Pi won't boot from power circuit | Measure 5V on Pin 2/6; recheck boost converter adjustment |

---

## Readiness Checklist

Before final enclosure assembly, all items must be checked:

- [ ] SD card written with Bookworm Lite 64-bit
- [ ] `install.sh` ran without errors, install.log shows clean completion
- [ ] All 4 services active and running
- [ ] INA219 visible at `0x40` on I²C bus
- [ ] Display smoke test: "Hello Bird!" rendered correctly
- [ ] `arecord -l` shows I²S capture device
- [ ] All 3 buttons verified via GPIO test
- [ ] Boot splash → Idle transition on service start
- [ ] Synthetic detection triggers Detection screen
- [ ] Button A cycles backlight (3 levels)
- [ ] Button B toggles History screen
- [ ] Button C hold initiates shutdown
- [ ] Battery MQTT messages published every 30s with plausible values
- [ ] BirdNET-Go produces at least one live detection from real audio
- [ ] Graceful shutdown leaves filesystem clean (SQLite integrity check passes)
