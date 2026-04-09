# BirdNET Remix — UI Prototype

A browser-based React prototype simulating the device display at 4× scale (640×512px).

## Prerequisites

Requires **Node.js** (v18+), run via [Vite](https://vitejs.dev).

### Linux / WSL (Debian/Ubuntu)

```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### macOS

```bash
brew install node
```

### Windows (native)

Download and install from [nodejs.org](https://nodejs.org).

## Running

```bash
./run.sh
```

On first run, `run.sh` will:
1. Scaffold a Vite + React project in this directory
2. Install npm dependencies (~30s, requires internet)
3. Start the dev server at **http://localhost:5173**

Subsequent runs skip the scaffold and start immediately.

> **Windows native:** run from WSL or Git Bash.
