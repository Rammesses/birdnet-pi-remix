# 09 — Open Questions & Deferred Decisions

Items flagged during design that require a decision before or during implementation.
Each item notes where the decision feeds into and what the default assumption is.

---

## Hardware

### OQ-01: USB-C connection style
**Question:** Fixed attached cable (simplest sealing) or flush IP-rated USB-C port?

**Options:**
- A) Fixed cable exits via PG7 cable gland — reliable seal, less convenient
- B) Flush IP-rated USB-C port (e.g. Amphenol waterproof USB-C) — cleaner, ~£3–5 extra
- C) Magnetic charging connector — very clean, but adds complexity and cost

**Default assumption:** Option A (fixed cable) for v1.
**Feeds into:** `05-housing-design.md`, `03-bill-of-materials.md`
**Decision needed by:** Housing CAD design phase

---

### OQ-02: Backlight PWM control
**Question:** Should the ST7735 backlight be on a PWM GPIO for smooth brightness
control, or hardwired to 3.3V (on/off + current limiting resistor only)?

**Default assumption:** GPIO 12 (hardware PWM) for 3-level brightness cycling.
**Feeds into:** `04-hardware-design.md`, display daemon `config.py`
**Decision needed by:** Hardware wiring phase

---

### OQ-03: Charging indicator visibility
**Question:** Should TP4056 charge/standby status LEDs be visible externally
(light pipes through housing) or monitored silently via INA219 only?

**Default assumption:** INA219 only — charging status shown on display via
animated battery icon when USB-C connected.
**Feeds into:** `05-housing-design.md`
**Decision needed by:** Housing CAD design phase

---

### OQ-04: Lanyard attachment point
**Question:** Should the housing include a small lug/eyelet for a wrist lanyard?
Useful for handheld field use.

**Default assumption:** Include a lug on the top-left corner of front shell.
**Feeds into:** `05-housing-design.md`
**Decision needed by:** Housing CAD design phase

---

### OQ-05: Housing colour
**Question:** Single colour PETG, or two-colour (front/rear in contrasting colours)?

**Default assumption:** Single colour. Suggest dark green or dark grey PETG.
**Feeds into:** Print specification
**Decision needed by:** Print phase

---

## Software

### OQ-06: Spectrogram vs confidence bars
**Question:** The original requirement specified a spectrogram. BirdNET-Go does not
natively include spectrogram data in its MQTT output.

**Options:**
- A) **Confidence-band visualiser** — show the per-frequency-band confidence from
     BirdNET-Go's analysis output (if accessible via API/output). Approximates a
     spectrogram.
- B) **True live spectrogram** — display daemon reads raw ALSA audio in a separate
     thread and renders FFT bars independently. More CPU load on Pi Zero 2W.
- C) **Playback spectrogram** — BirdNET-Go saves spectrograms as images; display
     daemon reads these image files and renders them. Adds latency.

**Default assumption:** Option A for v1 — revisit B in v2.
**Feeds into:** `07-ui-specification.md`, `06-software-design.md`
**Decision needed by:** UI prototype phase

---

### OQ-07: Detection auto-return timeout
**Question:** How long should the detection screen persist before returning to idle
if no new detection occurs?

**Default assumption:** 30 seconds.
**Feeds into:** Display daemon state machine
**Decision needed by:** Implementation phase (easy to tune)

---

### OQ-08: History depth
**Question:** How many detections should the history list store in memory?

**Default assumption:** Last 50 detections (well within RAM; SQLite DB stores all).
**Feeds into:** Display daemon data model
**Decision needed by:** Implementation phase

---

### OQ-09: Boot/config UI
**Question:** Should there be any on-device UI for configuration (e.g. Wi-Fi setup,
BirdWeather token entry)? Or is all configuration done via SSH/install script?

**Default assumption:** SSH/install script only for v1. A config screen could be
added in v2 with a text input mechanism (cycling through characters with buttons —
tedious but workable for a one-time setup).
**Feeds into:** Install script design
**Decision needed by:** Before implementation begins

---

### OQ-10: BirdNET-Go MQTT payload verification
**Question:** The MQTT payload schema in `06-software-design.md` is based on
BirdNET-Go documentation. The actual payload format should be verified against the
current BirdNET-Go release before the display daemon is implemented.

**Action:** Check `https://github.com/tphakala/birdnet-go` for current MQTT output
format and update `06-software-design.md` accordingly.
**Feeds into:** Display daemon MQTT subscriber code
**Decision needed by:** Before Kiro implementation starts

---

## Future / v2 Features

These are out of scope for v1 but worth noting for future planning:

| Feature | Notes |
|---------|-------|
| Solar charging | Requires larger housing or external panel |
| Speaker / playback | Replay detected bird call; needs DAC and speaker in housing |
| True spectrogram | FFT from ALSA stream in display daemon (OQ-06 option B) |
| On-device Wi-Fi config | Captive portal or button-driven config UI (OQ-09) |
| Camera module | Visual bird ID; major housing and compute change |
| E-ink variant | E-ink display for ultra-low power; loses animation capability |
| BLE companion app | Push detections to phone via Bluetooth |
| Second Pi integration | Pi Camera for video + BirdNET-Go for audio simultaneously |
