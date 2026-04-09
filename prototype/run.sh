#!/usr/bin/env bash
# Runs the BirdNET Remix UI prototype in a local Vite dev server.
# Usage: ./run.sh

set -e
cd "$(dirname "$0")"

NPM="/usr/bin/npm"

# Bootstrap Vite project if not already done
if [ ! -f package.json ]; then
  "$NPM" create vite@latest . -- --template react --yes
  "$NPM" install
fi

# Copy prototype component as the app entry point
cp BirdNETPrototype.jsx src/App.jsx

# Minimal index entry — just mounts App
cat > src/main.jsx << 'EOF'
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
createRoot(document.getElementById("root")).render(<StrictMode><App /></StrictMode>);
EOF

# Plain dark background, no default Vite styles
cat > src/index.css << 'EOF'
body { margin: 0; background: #1a1a1a; }
EOF

# Ensure index.css is imported
sed -i "s|import './index.css'||" src/main.jsx 2>/dev/null || true
echo "import './index.css'" | cat - src/main.jsx > /tmp/_main && mv /tmp/_main src/main.jsx

"$NPM" run dev
