# BirdNET-Pi Remix

A self-contained, handheld birdsong identification device. It listens continuously
for bird calls, identifies them locally using the [BirdNET-Go](https://github.com/tphakala/birdnet-go)
machine-learning engine, and displays results on a 1.8" colour TFT screen.
Runs offline by default, optionally syncing detections to [BirdWeather](https://app.birdweather.com)
when Wi-Fi is available.

Built using [Claude](https://claude.ai) and [Kiro](https://kiro.dev).
Full design documentation is in [`initial_design/`](initial_design/00-README.md).

---

## UI Prototype

A browser-based React prototype simulates the device display and buttons at 4× scale
(640×512px) for design review. It covers all five screens (Boot, Config, Idle,
Detection, History), all button interactions, auto-cycling detections, and the dim
timer.

### Prerequisites

The prototype requires **Node.js** (v18+) and runs via [Vite](https://vitejs.dev).

#### Linux / WSL (Debian/Ubuntu)

```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### macOS

```bash
brew install node
```

#### Windows (native)

Download and install from [nodejs.org](https://nodejs.org).

---

### Running the prototype

```bash
cd prototype
./run.sh
```

On first run, `run.sh` will:
1. Scaffold a Vite + React project in the `prototype/` directory
2. Install npm dependencies (~30s, requires internet)
3. Start the dev server at **http://localhost:5173**

Subsequent runs skip the scaffold and start immediately.

> **Windows native:** `run.sh` is a bash script. Run it from WSL, Git Bash, or
> adapt the commands manually.

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
| Kiro implementation | 🔲 Not started |
| Hardware build | 🔲 Not started |
| Documentation & release | 🔲 Not started |

---

## Credits

Built on top of:
- [BirdNET-Go](https://github.com/tphakala/birdnet-go) — analysis engine
- [BirdNET-Pi](https://github.com/Nachtzuster/BirdNET-Pi) — architecture reference
- [BirdNetDisplay](https://github.com/ThomDyson/BirdNetDisplay) — display integration reference
