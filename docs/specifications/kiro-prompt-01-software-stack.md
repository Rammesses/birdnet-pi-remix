# Kiro Specification: BirdNET-Pi Remix — Software Stack

## Context

You are building the software for **BirdNET-Pi Remix**: a self-contained, handheld
birdsong identification device based on a Raspberry Pi Zero 2W. The device listens
continuously for bird calls, identifies them using the BirdNET-Go machine-learning
engine, and displays results on a 1.8" ST7735 colour TFT display (160×128 px).

The UI prototype has already been approved. Your task is to implement the software
stack that runs on the device itself.

---

## Repository Layout

Implement the following directory structure exactly. Do not add top-level directories
that are not listed here.

```
birdnet-pi-remix/
├── display/
│   ├── daemon.py
│   ├── config.py
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── boot.py
│   │   ├── detection.py
│   │   ├── history.py
│   │   ├── idle.py
│   │   └── shutdown.py
│   ├── components/
│   │   ├── __init__.py
│   │   ├── battery.py
│   │   ├── clock.py
│   │   ├── listening.py
│   │   └── spectrogram.py
│   ├── drivers/
│   │   ├── __init__.py
│   │   └── st7735.py
│   ├── fonts/
│   │   ├── DejaVuSans.ttf
│   │   ├── DejaVuSans-Bold.ttf
│   │   └── DejaVuSans-Oblique.ttf
│   └── input/
│       ├── __init__.py
│       └── buttons.py
├── power/
│   ├── __init__.py
│   └── daemon.py
├── config/
│   ├── birdnet-go.yaml
│   ├── mosquitto.conf
│   └── wpa_supplicant.conf.template
├── systemd/
│   ├── birdnet-go.service
│   ├── birdnet-display.service
│   ├── birdnet-power.service
│   └── birdnet-remix.target
└── install/
    ├── install.sh
    ├── setup_audio.sh
    └── setup_display.sh
```

---

## Target Platform

| Item | Value |
|------|-------|
| Hardware | Raspberry Pi Zero 2W |
| OS | Raspberry Pi OS Lite 64-bit, Bookworm (Debian 12) |
| Python | 3.11+ (system Python on Bookworm) |
| Architecture | aarch64 |

---

## Python Dependencies

Use `pip install --break-system-packages` or a venv at `/opt/birdnet-remix/venv`.
A `requirements.txt` must be present in the repository root.

Required packages:

```
luma.lcd>=2.5.0
Pillow>=10.0.0
paho-mqtt>=1.6.1
RPi.GPIO>=0.7.1
smbus2>=0.4.3
```

---

## System Services

### BirdNET-Go (`birdnet-go.service`)

BirdNET-Go is a pre-built Go binary. The install script downloads the latest
`linux/arm64` release from https://github.com/tphakala/birdnet-go/releases.

The systemd service must:
- Run as a dedicated `birdnet` system user (created by install script)
- Start after `mosquitto.service` and `network.target`
- Be part of `birdnet-remix.target`
- Restart on failure with a 5s delay
- Use `/etc/birdnet-go/config.yaml` as its config file

### Display Daemon (`birdnet-display.service`)

- Python service: `python3 /opt/birdnet-remix/display/daemon.py`
- Runs as the `birdnet` user
- Starts after `mosquitto.service`
- Part of `birdnet-remix.target`
- Restart on failure with a 3s delay

### Power Manager (`birdnet-power.service`)

- Python service: `python3 /opt/birdnet-remix/power/daemon.py`
- Runs as root (requires GPIO and I²C access)
- Starts after `multi-user.target`
- Part of `birdnet-remix.target`
- Restart on failure with a 5s delay

### Systemd Target (`birdnet-remix.target`)

```ini
[Unit]
Description=BirdNET Remix Services
Requires=mosquitto.service birdnet-go.service birdnet-display.service birdnet-power.service
After=mosquitto.service birdnet-go.service birdnet-display.service birdnet-power.service

[Install]
WantedBy=multi-user.target
```

---

## BirdNET-Go Configuration (`config/birdnet-go.yaml`)

```yaml
birdnet:
  sensitivity: 1.0
  threshold: 0.7
  overlap: 1.5
  locale: en

input:
  source: alsa
  device: "hw:0,0"
  sample_rate: 48000

realtime:
  enabled: true

mqtt:
  enabled: true
  broker: localhost
  port: 1883
  topic: birdnet/detection

birdweather:
  enabled: false
  token: ""
  locationaccuracy: 500

output:
  sqlite:
    enabled: true
    path: /var/lib/birdnet-go/detections.db
```

---

## Mosquitto Configuration (`config/mosquitto.conf`)

```
listener 1883 127.0.0.1
allow_anonymous true
persistence false
log_type error
```

Mosquitto must bind to localhost only. No external MQTT access.

---

## GPIO and Pin Assignments (`display/config.py`)

Implement `display/config.py` with the following constants. Do not hard-code these
values anywhere else in the codebase — always import from config.

```python
# SPI display
DISPLAY_CS   = 8    # GPIO 8,  Pin 24
DISPLAY_DC   = 24   # GPIO 24, Pin 18
DISPLAY_RST  = 25   # GPIO 25, Pin 22
DISPLAY_BL   = 12   # GPIO 12, Pin 32 (hardware PWM for backlight)

# Display dimensions
DISPLAY_WIDTH  = 160
DISPLAY_HEIGHT = 128

# Buttons (active-low, internal pull-up)
BUTTON_A = 16   # GPIO 16, Pin 36 — brightness / wake
BUTTON_B = 26   # GPIO 26, Pin 37 — history toggle
BUTTON_C = 21   # GPIO 21, Pin 40 — hold=shutdown

# I²C power monitor
INA219_ADDRESS = 0x40

# MQTT
MQTT_BROKER           = "localhost"
MQTT_PORT             = 1883
MQTT_TOPIC_DETECTION  = "birdnet/detection"
MQTT_TOPIC_BATTERY    = "birdnet/battery"
MQTT_TOPIC_WIFI       = "birdnet/wifi_status"

# Timing
DETECTION_TIMEOUT_S   = 30    # Return to IDLE after this many seconds without a new detection
DIM_TIMEOUT_S         = 60    # Dim display after this many seconds without a button press
RENDER_FPS            = 15

# Power thresholds (volts)
VOLTAGE_WARNING       = 3.5
VOLTAGE_SHUTDOWN      = 3.3
POWER_CHECK_INTERVAL  = 30   # seconds
```

---

## Colour Palette

Implement the colour palette in `display/config.py` as named constants.
All colours are RGB tuples for use with Pillow.

```python
# Colours
COL_BG               = (13,  27,  14)   # Forest Night
COL_TEXT_PRIMARY     = (240, 236, 216)  # Bone White
COL_TEXT_SECONDARY   = (139, 168, 136)  # Sage
COL_ACCENT           = (232, 200, 74)   # Birch Yellow
COL_CONF_FILL        = (76,  175, 80)   # Moss Green
COL_CONF_BG          = (30,  51,  32)   # Dark Moss
COL_SPEC_LOW         = (26,  58,  92)   # Deep Blue
COL_SPEC_HIGH        = (240, 160, 48)   # Sky Amber
COL_BATT_GOOD        = (102, 187, 106)  # Leaf Green
COL_BATT_LOW         = (255, 167, 38)   # Amber
COL_BATT_CRIT        = (239, 83,  80)   # Red
COL_DIVIDER          = (42,  74,  42)   # Dark Sage
COL_HINT             = (86,  120, 86)   # Dim Sage
```

---

## Display Driver (`display/drivers/st7735.py`)

Wrap `luma.lcd` to provide a simple interface:

```python
class ST7735Display:
    def __init__(self): ...
    def show(self, image: PIL.Image.Image) -> None: ...
    def set_backlight(self, percent: int) -> None: ...   # 0–100
    def clear(self) -> None: ...
```

Use `luma.lcd.device.st7735` with `bgr=False`, `h_offset=0`, `v_offset=0`.
The backlight must be controlled via hardware PWM on GPIO 12 using RPi.GPIO PWM.

---

## Display Daemon State Machine (`display/daemon.py`)

The daemon must implement the following state machine exactly.

### States

| State | Description |
|-------|-------------|
| `BOOT` | Boot splash; shown until MQTT broker is reachable |
| `IDLE` | Clock + listening animation |
| `DETECTION` | Shows most recent detection |
| `HISTORY` | Scrollable list of recent detections |
| `DIM` | Display dimmed to 10%; any button wakes back to previous state |
| `SHUTDOWN` | Graceful shutdown screen; non-interactive |

### Transitions

```
BOOT        →[mqtt connected]→          IDLE
IDLE        →[detection received]→      DETECTION
DETECTION   →[30s no new detection]→    IDLE
DETECTION   →[new detection]→           DETECTION (reset timer, update content)
IDLE        →[Button B press]→          HISTORY
DETECTION   →[Button B press]→          HISTORY
HISTORY     →[Button B press]→          previous state (IDLE or DETECTION)
any state   →[Button A press]→          cycle backlight: 100→50→10→100%
any state   →[Button C held ≥3s]→       SHUTDOWN
any state   →[60s no button input]→     DIM
DIM         →[any button press]→        IDLE (restore last backlight level)
any state   →[MQTT birdnet/battery critical]→  SHUTDOWN
```

### Button Handling

Button events are handled via `RPi.GPIO` edge-detection callbacks.
- Active-low (pull-up enabled in software)
- Debounce: 50ms
- Button C long-press: timer starts on `FALLING` edge, fires `SHUTDOWN` transition
  if still held at 3 seconds

### Rendering Loop

Run at ~15 fps. Each iteration:
1. Check state and transition conditions
2. Call `render_<state>(image_draw)` for the current state
3. Push frame to display via `ST7735Display.show()`
4. Sleep to maintain target frame rate

### MQTT Detection Payload

The daemon must subscribe to `birdnet/detection`. Parse the JSON payload, using
`.get()` with sensible defaults for all fields:

```python
{
    "common_name":      str  — default "Unknown"
    "scientific_name":  str  — default ""
    "confidence":       float — default 0.0 (range 0.0–1.0)
    "timestamp":        str  — ISO 8601, default current time
}
```

Store the last 20 detections in memory for the History screen.

---

## Screen Implementations

### Boot Screen (`screens/boot.py`)

- Centred bird emoji or simple icon (rendered as a small bitmap glyph)
- "BirdNET Remix" in 16px bold
- "Starting up..." in 11px
- Indeterminate progress bar: 120px wide, animates left-to-right fill cycling

### Idle Screen (`screens/idle.py`)

Layout zones (y pixel ranges):

| Zone | Y range | Content |
|------|---------|---------|
| Status bar | 0–13 | Wi-Fi icon, battery icon+%, HH:MM |
| Clock time | 14–52 | HH:MM:SS, 28px bold, centred |
| Clock day | 53–64 | Day name, 11px, centred |
| Clock date | 65–76 | "8 April 2026", 11px, centred |
| Listening | 77–103 | "≋  Listening...  ≋" + animated dots |
| Button hints | 104–127 | "[A]Bright  [B]History  [C▶]Off" |

Listening animation: three dots cycling Sage→Bone White at 0.4s per dot.

### Detection Screen (`screens/detection.py`)

Layout zones:

| Zone | Y range | Content |
|------|---------|---------|
| Status bar | 0–13 | Wi-Fi icon, battery icon+%, HH:MM |
| Common name | 14–32 | Up to 20 chars, 16px bold, left-aligned |
| Scientific name | 33–45 | Italic 11px, left-aligned |
| Confidence bar | 46–61 | Filled bar + numeric %, 13px bold |
| Visualiser | 62–103 | 18 vertical bars, colour-mapped by amplitude |
| Button hints | 104–127 | "[A]Bright  [B]History  [C▶]Off" |

The visualiser in v1 is **not** a true spectrogram. Render 18 bars of pseudo-random
heights seeded from the detection confidence value, cycling slowly to give a
"listening" feel while the detection is displayed.

The confidence bar is a filled rectangle from x=4 to x=(4 + int(152 * confidence)),
background filled first in `COL_CONF_BG`, then foreground in `COL_CONF_FILL`.

Slide-in animation on new detection: common name translates from x=+160 to x=4
over 8 frames (200ms at 15fps). Same-species update: no slide, bar updates in-place.

### History Screen (`screens/history.py`)

Layout:

| Zone | Y range | Content |
|------|---------|---------|
| Header | 0–13 | "Recent Detections" 11px + battery icon |
| Row 1–5 | 14–83 | HH:MM · name · mini-bar · % (14px per row) |
| Divider | 84–85 | `COL_DIVIDER` line |
| Button hints | 86–127 | "[A]↑  [B]Back  [C]↓" |

Show 5 rows at a time. Scroll offset stored as integer; Button A scrolls up,
Button C scrolls down. Top visible row highlighted in `COL_ACCENT`.

### Shutdown Screen (`screens/shutdown.py`)

- Centred "Shutting down..." 16px bold
- "Saving detections database" 11px
- "Please wait" 11px
- Static; displayed for ~3s then display cleared to black

---

## Power Manager Daemon (`power/daemon.py`)

```python
INA219_ADDRESS    = 0x40
SHUTDOWN_VOLTAGE  = 3.3
WARNING_VOLTAGE   = 3.5
CHECK_INTERVAL    = 30  # seconds
```

Every `CHECK_INTERVAL` seconds:
1. Read voltage and current via INA219 over I²C (use `smbus2`)
2. Convert voltage to battery % using a LiPo discharge curve:
   - ≥4.1V = 100%, 3.7V = 50%, 3.5V = 20%, 3.3V = 0%
   - Linear interpolation between these points
3. Publish to `birdnet/battery` MQTT topic:
   ```json
   {"voltage": 3.85, "percent": 73, "current_ma": 210.5, "warning": false, "critical": false}
   ```
4. If voltage < `SHUTDOWN_VOLTAGE`: publish `critical: true`, then execute graceful
   shutdown after a 5s delay (to allow display to update)

### Graceful Shutdown Sequence

```python
def graceful_shutdown():
    publish_mqtt("birdnet/battery", {"critical": True})
    time.sleep(5)                         # allow display to show shutdown screen
    subprocess.run(["systemctl", "stop", "birdnet-go"])
    subprocess.run(["sync"])
    time.sleep(2)
    subprocess.run(["systemctl", "poweroff"])
```

---

## Status Bar Component (`components/battery.py`, `components/clock.py`)

### Battery icon

Render a 5-segment battery glyph at a given (x, y) position:
- Outer border: 18×10px rectangle
- Inner segments: 5 bars of 2px width with 1px gaps
- Colour: `COL_BATT_GOOD` (≥40%), `COL_BATT_LOW` (20–40%), `COL_BATT_CRIT` (<20%)
- Numeric % appended: "73%" in 9px

### Wi-Fi icon

Render a simple 3-arc glyph (8×8px):
- Solid arcs: Wi-Fi connected
- Outline only: disconnected
- Hidden: no SSID configured

### Clock

Render current time as HH:MM (status bar) or HH:MM:SS (idle screen).
Use `datetime.now()` — no NTP requirement, but if the device has Wi-Fi the system
clock will sync via `systemd-timesyncd`.

---

## Installation Script (`install/install.sh`)

The script must be idempotent (safe to run more than once).

Steps in order:

1. `apt-get update && apt-get upgrade -y`
2. `apt-get install -y python3-pip python3-venv mosquitto mosquitto-clients i2c-tools`
3. Apply `/boot/firmware/config.txt` entries (append if not already present):
   ```ini
   dtparam=i2s=on
   dtoverlay=i2s-mmap
   dtparam=spi=on
   dtparam=i2c_arm=on
   dtparam=audio=off
   gpu_mem=16
   ```
   On Bookworm the config file is at `/boot/firmware/config.txt`, not `/boot/config.txt`.
4. Create system user `birdnet` with no login shell
5. Create directory `/opt/birdnet-remix`, copy repository contents there
6. Create Python venv at `/opt/birdnet-remix/venv`, install `requirements.txt`
7. Download latest BirdNET-Go `linux/arm64` binary from GitHub releases to
   `/usr/local/bin/birdnet-go`, set executable
8. Create `/etc/birdnet-go/` and copy `config/birdnet-go.yaml` there
9. Copy `config/mosquitto.conf` to `/etc/mosquitto/conf.d/birdnet.conf`
10. Copy all `systemd/*.service` and `systemd/*.target` files to
    `/etc/systemd/system/`, reload daemon, enable `birdnet-remix.target`
11. Run `install/setup_audio.sh` (configure ALSA for I²S mic)
12. Run `install/setup_display.sh` (verify SPI device present)
13. Prompt: "Enter BirdWeather station token (leave blank to skip):"
    If provided, update `birdweather.enabled: true` and `token:` in
    `/etc/birdnet-go/config.yaml`
14. Prompt: "Enter Wi-Fi SSID (leave blank to skip):"
    If provided, prompt for password, write `/etc/wpa_supplicant/wpa_supplicant.conf`
15. `systemctl enable birdnet-remix.target && systemctl start birdnet-remix.target`
16. Print "Installation complete. Rebooting in 10 seconds..." and reboot

### ALSA Setup (`install/setup_audio.sh`)

```bash
# Configure ALSA for SPH0645 I²S mic
# /etc/asound.conf
cat > /etc/asound.conf << 'EOF'
pcm.i2smic {
    type hw
    card 0
    device 0
}
pcm.!default {
    type asym
    capture.pcm "i2smic"
}
EOF
```

After writing, run `arecord -l` and print the output for the user to verify
the device is visible.

---

## Coding Standards

- Python: PEP 8 throughout
- All modules must have module-level docstrings
- All public functions and classes must have docstrings
- No bare `except:` clauses — always catch specific exceptions
- Log to `systemd` journal via Python `logging` module (no log files)
  - `logging.basicConfig(level=logging.INFO)`
  - Display daemon: logger name `birdnet.display`
  - Power daemon: logger name `birdnet.power`
- GPIO cleanup: all `RPi.GPIO` resources must be cleaned up in a `finally` block
  or via `atexit`
- MQTT: use `paho.mqtt.client` with `on_connect` and `on_disconnect` callbacks;
  reconnect automatically on disconnect
