# 02 — System Architecture

## Hardware Layer

```
┌─────────────────────────────────────────────────────────┐
│                  Raspberry Pi Zero 2W                   │
│                                                         │
│  ┌──────────┐  I²S   ┌─────────────────────────────┐   │
│  │  I²S Mic │───────▶│         BirdNET-Go          │   │
│  │   HAT    │        │    (analysis engine,        │   │
│  └──────────┘        │     Go binary, runs as      │   │
│                      │     systemd service)         │   │
│  ┌──────────┐  SPI   └────────────┬────────────────┘   │
│  │ ST7735   │◀───────             │ MQTT (localhost)    │
│  │ 1.8" TFT │        ┌────────────▼────────────────┐   │
│  │ display  │        │      Display Daemon          │   │
│  └──────────┘        │  (Python service, renders    │   │
│                      │   UI to TFT via SPI)         │   │
│  ┌──────────┐  GPIO  └────────────────────────────┬┘   │
│  │ 3 buttons│───────▶  Button handler (part of     │    │
│  └──────────┘          display daemon)             │    │
│                                                    │    │
│  ┌──────────┐  GPIO  ┌────────────────────────────▼┐   │
│  │ Power    │───────▶│     Power Manager Daemon     │   │
│  │ monitor  │        │  (monitors VBAT, triggers    │   │
│  │ (ADC)    │        │   graceful shutdown)         │   │
│  └──────────┘        └─────────────────────────────┘   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │          Wi-Fi (wlan0 — optional)                │   │
│  │    When available: BirdNET-Go syncs to           │   │
│  │    BirdWeather via its built-in integration      │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────┐
│         Power System                │
│                                     │
│  USB-C ──▶ TP4056 ──▶ LiPo cell    │
│                  └──▶ MT3608/boost  │
│                       (3.7V→5V)    │
│                  └──▶ VBAT pin     │
│                       (to ADC)     │
└─────────────────────────────────────┘
```

---

## Software Stack

| Layer | Component | Notes |
|-------|-----------|-------|
| OS | Raspberry Pi OS Lite 64-bit (Bookworm) | Headless, minimal |
| Audio capture | ALSA / I²S kernel driver | Configured for I²S mic HAT |
| Bird analysis engine | **BirdNET-Go** | Go binary, systemd service |
| Message bus | **Mosquitto MQTT** (localhost) | BirdNET-Go publishes detections |
| Display renderer | **Python 3 display daemon** | Custom, subscribes to MQTT |
| TFT driver | **luma.lcd** or **st7735** Python lib | SPI interface to ST7735 |
| Image composition | **Pillow (PIL)** | Renders text, spectrogram, icons |
| Power management | **Python 3 power daemon** | Reads ADC, controls shutdown |
| Button handling | **RPi.GPIO** or **gpiozero** | Part of display daemon |
| Optional cloud sync | BirdNET-Go built-in BirdWeather support | Activated when Wi-Fi present |
| Service management | **systemd** | All daemons as services |
| Wi-Fi management | **wpa_supplicant** | Standard Pi Wi-Fi |

---

## Data Flow

### Detection Flow
```
I²S mic
  └─▶ ALSA audio device
        └─▶ BirdNET-Go (continuous 3-second analysis windows)
              └─▶ Local SQLite DB (detections log)
              └─▶ MQTT publish: birdnet/detection
                    topic payload: {common_name, sci_name, confidence, timestamp, spectrogram_data}
                    └─▶ Display Daemon subscribes
                          └─▶ Renders detection screen on ST7735
              └─▶ (optional) BirdWeather HTTP API sync
```

### Power Flow
```
ADC reads VBAT every 30s
  └─▶ > 3.5V  : normal operation, battery icon shows charge level
  └─▶ 3.5-3.3V: low battery warning shown on display
  └─▶ < 3.3V  : graceful shutdown triggered
        └─▶ systemctl stop birdnet-go
        └─▶ sync filesystem
        └─▶ systemctl poweroff
```

### Button Flow
```
Button A (left)   : cycle display brightness (3 levels) / wake from screensaver
Button B (middle) : toggle between Detection screen and History list
Button C (right)  : [held 3s] initiate safe shutdown
```

---

## Service Architecture

```
systemd target: birdnet-remix.target
  ├── mosquitto.service          (MQTT broker)
  ├── birdnet-go.service         (analysis engine, depends on mosquitto)
  ├── birdnet-display.service    (display daemon, depends on mosquitto)
  └── birdnet-power.service      (power manager, independent)
```

All services start on boot. The display daemon shows a boot splash / "Starting..."
screen while BirdNET-Go initialises.

---

## Key Design Decisions

### Why BirdNET-Go over BirdNET-Pi?
- BirdNET-Pi is a full web server stack (PHP, Caddy, etc.) which is heavy for the
  Pi Zero 2W's 512MB RAM. BirdNET-Go is a single compiled Go binary with a much
  smaller footprint, native MQTT support, and active development.

### Why MQTT as the internal bus?
- BirdNET-Go has native MQTT publishing built in. Using it as the internal bus means
  the display daemon is fully decoupled from the analysis engine — it can be developed,
  restarted, and debugged independently without touching BirdNET-Go.
- It also makes it trivial in future to add other subscribers (e.g. a speaker service,
  a web API, a Home Assistant integration).

### Why a discrete power circuit over a UPS HAT?
- UPS HATs (PiSugar, Waveshare) use the GPIO header, which conflicts with the I²S
  mic HAT. A discrete TP4056 + boost converter circuit avoids this and keeps all
  GPIO pins available for the display and buttons.
- The tradeoff is that we must implement our own battery level sensing via an ADC
  pin (or voltage divider to a GPIO), which is manageable.

### Why Pillow for display rendering?
- Pillow allows composing text, shapes, and image data into a framebuffer in Python,
  which is the most flexible approach for a custom UI. The spectrogram data from
  BirdNET-Go can be rendered as a bar graph directly.
- Alternative: direct C/C++ framebuffer rendering would be faster but far harder
  to iterate on during UI development.

### Why luma.lcd / st7735 Python library?
- These provide a clean abstraction over the SPI interface to the ST7735. luma.lcd
  in particular has good Pillow integration (draw.ImageDraw) and supports the
  ST7735 controller well.
