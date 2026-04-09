# 01 — Project Overview

## Summary

**BirdNET-Pi Remix** is a self-contained, handheld birdsong identification device.
It listens continuously for bird calls, identifies them locally using the BirdNET-Go
machine-learning engine, and displays results on a colour TFT screen. It is designed
to be placed on a windowsill or desk via a kickstand, carried into the garden, or
mounted outdoors. It runs offline by default and optionally syncs to BirdWeather
when Wi-Fi is available.

---

## Goals

1. **Real-time bird identification** — continuous audio analysis using BirdNET-Go,
   with results appearing on-screen within seconds of a detection.
2. **Rich colour display** — a 1.8" ST7735 TFT showing bird name, scientific name,
   confidence, time, and a live mini-spectrogram.
3. **Standalone / offline-first** — fully functional with no network connectivity.
4. **Optional cloud sync** — when Wi-Fi is present, push detections to BirdWeather.
5. **Battery-powered** — discrete LiPo charge-and-use circuit with graceful shutdown.
6. **IP54-rated housing** — splash-proof and dust-resistant; suitable for outdoor use
   in rain, on a windowsill, or in a garden.
7. **Handheld + desktop** — ergonomic to hold, with an integrated kickstand for
   hands-free desk/windowsill use.
8. **Open-source remix** — all code, housing STLs, and documentation published.

---

## Non-Goals

- Full submersion / IP67 rating (out of scope for v1)
- Solar charging (possible v2 feature)
- Speaker / audio playback of detected calls (possible v2 feature)
- Touchscreen interaction
- Mobile app companion
- Camera / visual bird identification
- Running BirdNET-Pi (replaced by the lighter BirdNET-Go)

---

## Success Criteria

| Criterion | Measure |
|-----------|---------|
| Detection latency | Bird name appears on screen within 5 seconds of a call |
| Battery life | ≥ 6 hours continuous operation on target LiPo cell |
| Housing | Passes a simulated IP54 test (splash from all directions, dusty environment) |
| Identification accuracy | Matches BirdNET-Go baseline accuracy (not degraded by our integration) |
| Bootup time | Device ready to detect within 60 seconds of power-on |
| Graceful shutdown | BirdNET-Go and filesystem cleanly stopped before battery critical cutoff |

---

## Source Projects & Credits

This project remixes and builds on:

- **BirdNET-Go** by tphakala — the analysis engine
  https://github.com/tphakala/birdnet-go
- **BirdNET-Pi** (Nachtzuster fork) — architecture reference
  https://github.com/Nachtzuster/BirdNET-Pi
- **BirdNET-Pi Samson Mic Shroud** by IslePilot — weatherproof mic approach
  https://www.thingiverse.com/thing:6415101
- **BirdNET-Pi Outdoor Mic Capsule Holder** by nullrails — watertight mic mount
  https://www.printables.com/model/540079
- **BirdNetDisplay** by ThomDyson — display integration reference
  https://github.com/ThomDyson/BirdNetDisplay
- **Pi Zero W OLED Case** by timid_possum — Pi Zero + display housing reference
  https://www.thingiverse.com/thing:4320174
- **BirdNET-Pi Laser-Cut Enclosure** by audevuilli — enclosure design reference
  https://github.com/audevuilli/BirdNET-Pi-Enclosure

---

## Project Phases

### Phase 1 — Design & Planning (current)
- Requirements gathering ✅
- Architecture design
- BoM finalisation
- Hardware pin planning
- Housing concept
- UI specification and prototype

### Phase 2 — Kiro Implementation
- BirdNET-Go configuration and setup scripts
- Display daemon (Python service)
- UI renderer (Pillow / luma or direct SPI framebuffer)
- Power management daemon
- Wi-Fi sync service (optional)
- Systemd service definitions

### Phase 3 — Hardware Build
- Prototype wiring on breadboard/jumper wires
- Verify pin assignments and I²S audio
- 3D print housing v1
- Integrate and test

### Phase 4 — Documentation & Release
- Build guide with photos
- Publish STLs to Printables / Thingiverse
- Publish code to GitHub
