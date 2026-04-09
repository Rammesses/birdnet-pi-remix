# 06 — Software Design

## Repository Structure

```
birdnet-pi-remix/
├── display/
│   ├── daemon.py              # Main display daemon entry point
│   ├── screens/
│   │   ├── detection.py       # Detection screen renderer
│   │   ├── history.py         # History list screen renderer
│   │   ├── idle.py            # Idle / clock / listening screen renderer
│   │   ├── boot.py            # Boot splash screen
│   │   └── shutdown.py        # Shutdown screen
│   ├── components/
│   │   ├── spectrogram.py     # Spectrogram bar renderer
│   │   ├── battery.py         # Battery icon renderer
│   │   ├── clock.py           # Clock widget
│   │   └── listening.py       # Listening animation
│   ├── drivers/
│   │   └── st7735.py          # Display driver wrapper (luma.lcd)
│   ├── input/
│   │   └── buttons.py         # Button handler (RPi.GPIO event callbacks)
│   └── config.py              # Pin assignments, display config, colours
├── power/
│   └── daemon.py              # Power manager daemon
├── config/
│   ├── birdnet-go.yaml        # BirdNET-Go configuration
│   ├── mosquitto.conf         # MQTT broker config
│   └── wpa_supplicant.conf    # Wi-Fi template (populated at setup time)
├── systemd/
│   ├── birdnet-go.service
│   ├── birdnet-display.service
│   ├── birdnet-power.service
│   └── birdnet-remix.target
├── install/
│   ├── install.sh             # Full installation script
│   ├── setup_audio.sh         # I²S mic ALSA configuration
│   └── setup_display.sh       # SPI display configuration
└── docs/
    └── (build guide assets)
```

---

## BirdNET-Go Configuration

BirdNET-Go is configured via YAML. Key settings for this device:

```yaml
# config/birdnet-go.yaml

birdnet:
  sensitivity: 1.0
  threshold: 0.7          # Confidence threshold for detections
  overlap: 1.5            # Seconds of overlap between analysis windows
  locale: en              # Common name language

input:
  source: alsa            # Use ALSA for I²S mic input
  device: "hw:0,0"        # ALSA device (adjust after audio setup)
  sample_rate: 48000

realtime:
  enabled: true

mqtt:
  enabled: true
  broker: localhost
  port: 1883
  topic: birdnet/detection

# BirdWeather sync — only active when Wi-Fi connected
birdweather:
  enabled: false          # Set to true + add token to enable sync
  token: ""               # User's BirdWeather station token
  locationaccuracy: 500

output:
  sqlite:
    enabled: true
    path: /var/lib/birdnet-go/detections.db
```

---

## MQTT Message Schema

BirdNET-Go publishes to `birdnet/detection` on each detection event.

Expected payload (JSON):

```json
{
  "common_name": "Great Tit",
  "scientific_name": "Parus major",
  "confidence": 0.87,
  "timestamp": "2026-04-08T14:23:11Z",
  "source_node": "birdnet-remix"
}
```

> **Note:** BirdNET-Go's actual MQTT payload format should be verified against the
> current release when implementing. The display daemon should be robust to missing
> fields (use `.get()` with defaults).
>
> Spectrogram data is NOT natively included in BirdNET-Go's MQTT output. Two options:
> A) The display daemon generates its own mini-spectrogram from the raw audio stream
>    independently (read from ALSA directly in a separate thread).
> B) Use a simple bar visualisation of confidence bands rather than a true spectrogram.
>
> **Recommended for v1:** Option B (confidence-band bars) — simpler, avoids audio
> processing in the display daemon. True spectrogram can be v2.
> Flag in `09-open-questions.md`.

---

## Display Daemon

### State Machine

```
States:
  BOOT        → shows boot splash, transitions to IDLE when MQTT connects
  IDLE        → clock + listening animation; transitions to DETECTION on MQTT message
  DETECTION   → shows detected bird; auto-returns to IDLE after 30s with no new detection
  HISTORY     → compact list of recent detections; Button B toggles in/out
  DIM         → display dimmed (backlight low); any button press → IDLE/DETECTION
  SHUTDOWN    → graceful shutdown screen; non-interactive

Transitions:
  BOOT        →[mqtt connected]→  IDLE
  IDLE        →[detection]→       DETECTION
  DETECTION   →[30s timeout]→     IDLE
  DETECTION   →[new detection]→   DETECTION (reset timeout)
  IDLE        →[Button B]→        HISTORY
  DETECTION   →[Button B]→        HISTORY
  HISTORY     →[Button B]→        previous state (IDLE or DETECTION)
  any         →[Button A]→        cycle brightness (3 levels: full, 50%, off+dim)
  any         →[Button C 3s hold]→ SHUTDOWN
  any         →[60s no button]→   DIM
  DIM         →[any button]→      IDLE
  any         →[power critical]→  SHUTDOWN
```

### Rendering Loop

```python
# Pseudocode — actual implementation by Kiro
while True:
    frame = render_current_state()
    display.display(frame)
    process_button_events()
    sleep(1/15)  # ~15fps — adequate for this UI
```

---

## Screen Specifications

### DETECTION Screen (primary)

```
┌────────────────────────────────────────────────────────────────┐160px
│ Great Tit                              🔋 [████░] 14:23        │
│ Parus major                                                     │
│                                                                 │
│ Confidence: ██████████████████░░  87%                          │
│                                                                 │
│ ▁▂▄▆█▇▅▃▂▁▂▄▅▆▄▃▂▁  (spectrogram / confidence bars)           │
│ ─────────────────────────────────────────────────────          │
│  [A] Bright   [B] History   [C] Hold=Off                       │
└────────────────────────────────────────────────────────────────┘
                                                               128px
```

### IDLE Screen

```
┌────────────────────────────────────────────────────────────────┐
│                                                                 │
│                     14:23:45                                    │
│                   Wednesday                                     │
│                   8 April 2026                                  │
│                                                                 │
│              ≋  Listening...   ≋                               │
│           (animated wave / pulse)                               │
│                                                         🔋[███]│
└────────────────────────────────────────────────────────────────┘
```

### HISTORY Screen

```
┌────────────────────────────────────────────────────────────────┐
│ Recent Detections                                    🔋[███]   │
│ ─────────────────────────────────────────────────────         │
│ 14:23  Great Tit            87%                                │
│ 14:18  Blue Tit             92%                                │
│ 13:55  Robin                78%                                │
│ 13:41  Song Thrush          83%                                │
│ 13:30  Chaffinch            71%                                │
│ ─────────────────────────────────────────────────────         │
│  [A] Scroll up   [B] Back   [C] Scroll down                    │
└────────────────────────────────────────────────────────────────┘
```

---

## Power Manager Daemon

```python
# Pseudocode

INA219_I2C_ADDRESS = 0x40
SHUTDOWN_VOLTAGE   = 3.3   # V
WARNING_VOLTAGE    = 3.5   # V
CHECK_INTERVAL     = 30    # seconds

while True:
    voltage, current = read_ina219()
    battery_pct = voltage_to_percent(voltage)

    publish_battery_state(voltage, battery_pct)  # MQTT: birdnet/battery

    if voltage < SHUTDOWN_VOLTAGE:
        initiate_graceful_shutdown()
        break
    elif voltage < WARNING_VOLTAGE:
        publish_low_battery_warning()

    sleep(CHECK_INTERVAL)
```

### Graceful Shutdown Sequence

```bash
# Initiated by power daemon or Button C hold
1. Display "Shutting down..." screen
2. systemctl stop birdnet-go
3. sync
4. sleep 2
5. systemctl poweroff
```

---

## Wi-Fi / BirdWeather Sync

BirdNET-Go handles BirdWeather sync natively. The install script will:
1. Prompt for BirdWeather station token (optional)
2. Prompt for Wi-Fi credentials (optional)
3. If both provided, set `birdweather.enabled: true` in birdnet-go.yaml
4. A small `wifi-monitor.service` will check connectivity and update a
   `birdnet/wifi_status` MQTT topic — the display daemon shows a Wi-Fi icon
   when connected.

---

## Installation Script Outline

```bash
install.sh:
  1. Update system packages
  2. Configure /boot/config.txt (I²S, SPI, I²C)
  3. Install Mosquitto MQTT broker
  4. Download and install BirdNET-Go binary
  5. Install Python dependencies (luma.lcd, Pillow, paho-mqtt, smbus2, RPi.GPIO)
  6. Copy systemd service files
  7. Configure ALSA for I²S mic
  8. Prompt for Wi-Fi / BirdWeather credentials (optional)
  9. Enable and start all services
  10. Reboot
```
