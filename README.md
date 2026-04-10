# BirdNET-Pi Remix

A self-contained, handheld birdsong identification device. It listens continuously
for bird calls, identifies them locally using the [BirdNET-Go](https://github.com/tphakala/birdnet-go)
machine-learning engine, and displays results on a 1.8" colour TFT screen.
Runs offline by default, optionally syncing detections to [BirdWeather](https://app.birdweather.com)
when Wi-Fi is available.

Built using [Claude](https://claude.ai) and [Kiro](https://kiro.dev).
Full design documentation is in [`initial_design/`](initial_design/00-README.md).
Kiro implementation specs are in [`specifications/`](specifications/).

---

## UI Prototype

A browser-based React prototype simulates the device display and buttons at 4× scale
(640×512px) for design review. It covers all five screens (Boot, Config, Idle,
Detection, History), all button interactions, auto-cycling detections, and the dim
timer.

See [`prototype/README.md`](prototype/README.md) for setup and running instructions.

---

### Button interactions

| Button | Click | Hold 2s |
|--------|-------|---------|
| A | Cycle brightness · Scroll up (History) | Enter Config (Boot screen only) |
| B | Toggle History / Back · Advance Config step | — |
| C | Scroll down (History) | Shutdown |

Auto-behaviours (prototype timings, shortened for review):
- New detection auto-cycles every **12 seconds**
- Display dims after **15 seconds** of no button interaction (real device: 60s)
- Detection screen auto-returns to Idle after **30 seconds**

---

## Project status

| Phase | Status |
|-------|--------|
| Design & planning | ✅ Complete |
| UI prototype | ✅ Complete |
| Kiro specifications | ✅ Complete |
| Kiro implementation | 🔲 Not started |
| Hardware build | 🔲 Not started |
| Documentation & release | 🔲 Not started |

---

## Credits

Built on top of:
- [BirdNET-Go](https://github.com/tphakala/birdnet-go) — analysis engine
- [BirdNET-Pi](https://github.com/Nachtzuster/BirdNET-Pi) — architecture reference
- [BirdNetDisplay](https://github.com/ThomDyson/BirdNetDisplay) — display integration reference
