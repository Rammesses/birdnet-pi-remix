# 08 — Build Guide (Outline)

> This document is a structural outline. The full illustrated build guide will be
> written after the prototype hardware build is complete and photographed.

---

## Prerequisites

### Skills assumed
- Comfortable with Raspberry Pi headless setup (SSH, Raspberry Pi Imager)
- Basic soldering (through-hole components, header pins)
- Familiarity with the Linux command line
- Basic 3D printing experience (PETG settings, supports, post-processing)

### Tools required
- Soldering iron (temperature-controlled preferred)
- Solder (e.g. 0.7mm 60/40 or lead-free)
- Flux
- Multimeter
- Fine-tip tweezers
- M2.5 and M3 hex drivers
- Heat-set insert tool (or soldering iron with flat tip)
- 3D printer (PETG capable: ≥250°C hotend, heated bed)
- Small flat file (for print cleanup)
- Sharp craft knife / scalpel

---

## Section 1 — OS Preparation

1. Download Raspberry Pi OS Lite 64-bit (Bookworm)
2. Flash to microSD with Raspberry Pi Imager
   - Set hostname: `birdnet-remix`
   - Enable SSH, set username/password
   - Configure Wi-Fi (optional)
3. Boot Pi Zero 2W, SSH in
4. Run `sudo apt update && sudo apt upgrade -y`

---

## Section 2 — Enable Hardware Interfaces

1. Edit `/boot/firmware/config.txt` (Bookworm path):
   ```ini
   dtparam=i2s=on
   dtoverlay=i2s-mmap
   dtparam=spi=on
   dtparam=i2c_arm=on
   dtparam=audio=off
   gpu_mem=16
   ```
2. Reboot
3. Verify SPI: `ls /dev/spidev*`
4. Verify I²C: `ls /dev/i2c*`
5. Verify I²S: `arecord -l` (mic won't appear until ALSA config — see Section 4)

---

## Section 3 — Wiring (Prototype Stage)

> Wire on breadboard / with jumper wires before housing assembly.

### 3.1 SPH0645 I²S Microphone
- Wire per pin table in `04-hardware-design.md`
- Tie SEL pin to GND (left channel)

### 3.2 ST7735 Display
- Wire per pin table in `04-hardware-design.md`
- Note: 3.3V only — do NOT connect to 5V

### 3.3 INA219 Power Monitor
- Wire SDA/SCL to GPIO 2/3
- Insert shunt inline with battery output (see power circuit diagram)

### 3.4 Buttons
- Wire three momentary switches between GPIO pins and GND
- No external resistors needed (internal pull-ups used in software)

### 3.5 Power Circuit
- Assemble TP4056 → LiPo → INA219 → MT3608 → Pi 5V
- Set MT3608 output to 5.1V using multimeter before connecting Pi
- Verify with multimeter: 5.1V at Pi input, INA219 reads correct voltage

---

## Section 4 — Audio Configuration

1. Configure ALSA for I²S mic:
   ```bash
   sudo nano /etc/asound.conf
   ```
   Add:
   ```
   pcm.!default {
     type hw
     card 0
     device 0
   }
   ctl.!default {
     type hw
     card 0
   }
   ```
2. Test recording:
   ```bash
   arecord -D hw:0,0 -c 1 -r 48000 -f S16_LE -d 5 test.wav
   aplay test.wav
   ```
3. Verify: clean audio, no distortion, reasonable level

---

## Section 5 — Software Installation

1. Run the install script:
   ```bash
   curl -sSL https://raw.githubusercontent.com/[repo]/install/install.sh | bash
   ```
   Or clone and run manually:
   ```bash
   git clone https://github.com/[repo]/birdnet-pi-remix.git
   cd birdnet-pi-remix
   sudo bash install/install.sh
   ```
2. Follow prompts for optional Wi-Fi / BirdWeather credentials
3. Reboot when prompted

---

## Section 6 — Verification

1. Check all services running:
   ```bash
   systemctl status birdnet-go birdnet-display birdnet-power mosquitto
   ```
2. Check display shows boot splash → idle screen
3. Make a sound near the microphone — check detection appears on screen
4. Press buttons — verify brightness cycle, history screen, hold-to-shutdown
5. Verify battery % shows on status bar
6. (Optional) Connect to Wi-Fi, verify BirdWeather sync in BirdNET-Go logs

---

## Section 7 — 3D Printing the Housing

1. Download STL files from `housing/` directory
2. Slice settings per `05-housing-design.md`
3. Print order:
   a. `housing_front.stl` — with supports (display rebate)
   b. `housing_rear.stl` — no supports needed
   c. `kickstand.stl` — no supports
   d. `button_cap_x3.stl` — print flat, no supports (×3)
   e. `mic_shroud.stl`
4. Post-process:
   - Remove supports carefully from display rebate
   - Test-fit acrylic window, sand rebate if tight
   - Install M3 heat-set inserts in front shell (4 corners, 240°C iron)
   - Test-fit all components before final assembly

---

## Section 8 — Final Assembly

1. Bond acrylic display window with clear RTV; cure 24h
2. Mount Pi Zero 2W in rear lid on M2.5 standoffs
3. Attach SPH0645 mic breakout in housing with Kapton tape / small bracket
4. Route and dress all wiring (minimal bend radius on flex cables)
5. Place power circuit components (TP4056, MT3608, INA219) in battery bay
6. Connect LiPo — verify 5.1V at Pi before proceeding
7. Place O-ring in channel (lightly lubricate with silicone grease)
8. Mate front and rear shell
9. Insert and gently tighten 4× M3 screws (do not overtighten — O-ring compression)
10. Install cable gland for USB-C lead
11. Insert button caps
12. Attach kickstand with hinge pin; verify detent positions

---

## Section 9 — IP54 Verification (Basic)

1. Run device outdoors in light rain for 30 minutes — check for water ingress
2. Inspect O-ring seal for any wet spots after test
3. Verify buttons remain functional when slightly wet

---

## Appendix A — Troubleshooting

| Issue | Check |
|-------|-------|
| Display blank | SPI enabled? Wiring correct? Run `dmesg | grep spi` |
| No audio / no detections | I²S enabled? `arecord` test passes? ALSA device name in birdnet-go.yaml |
| Services not starting | `journalctl -u birdnet-go -u birdnet-display` |
| Battery % wrong | INA219 I²C address: `i2cdetect -y 1` should show `0x40` |
| No BirdWeather sync | Check Wi-Fi: `iwconfig`; check token in birdnet-go.yaml |

---

## Appendix B — BirdNET-Go Log Location

```
journalctl -u birdnet-go -f        # Live logs
/var/lib/birdnet-go/detections.db  # SQLite detections database
```
