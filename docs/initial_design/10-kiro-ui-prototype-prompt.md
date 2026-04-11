# Kiro Prompt: BirdNET Remix — UI Prototype

## Context

You are building an interactive UI prototype for a physical birdsong identification
device. The device has a 1.8" ST7735 TFT display running at **160×128 pixels** in
landscape orientation. The prototype should be a **React artifact** that simulates
the device display and buttons at a scaled-up size for review purposes.

All design decisions, colour palette, typography, layout zones, screen content, and
interaction behaviour are fully specified in the design documents located at:

```
~/Projects/birdnet-pi-remix/initial_design/
  07-ui-specification.md   ← PRIMARY reference for this task
  06-software-design.md    ← State machine and screen logic
```

Read both documents in full before writing any code.

---

## What to Build

A single React component that:

1. **Renders the device display** at 4× scale (640×512px) inside a styled device
   shell, so the layout can be reviewed without squinting. All fonts and elements
   should be sized as they would appear on the real 160×128 display, then scaled up.

2. **Simulates all five screens:**
   - `BOOT` — boot splash with indeterminate progress bar animation
   - `CONFIG` — Wi-Fi setup wizard (4 steps: SSID, Password, BirdWeather token, Timezone)
   - `IDLE` — clock with listening animation
   - `DETECTION` — full detection layout with confidence bar and visualiser
   - `HISTORY` — compact scrollable list of recent detections

3. **Simulates the three buttons** (A, B, C) as clickable elements below the device
   shell, labelled and behaving exactly as specified in the button behaviour table in
   `07-ui-specification.md`. Long-press behaviour (Button C = shutdown, Button A at
   boot = config) should be simulated by holding the mouse button for 2 seconds.

4. **Uses mock data** for detections. Pre-populate with at least 8 realistic UK bird
   detections with varied confidence levels and times, e.g.:
   - Great Tit / Parus major / 87% / 14:23
   - Blue Tit / Cyanistes caeruleus / 92% / 14:18
   - Robin / Erithacus rubecula / 78% / 13:55
   - Song Thrush / Turdus philomelos / 83% / 13:41
   - Chaffinch / Fringilla coelebs / 71% / 13:30
   - Blackbird / Turdus merula / 95% / 13:12
   - Wren / Troglodytes troglodytes / 66% / 12:58
   - Great Spotted Woodpecker / Dendrocopos major / 74% / 12:43

5. **Auto-cycles a new detection** every 12 seconds while in IDLE or DETECTION state,
   cycling through the mock data list, so the transition animation and detection
   screen can be observed without manual interaction.

6. **Implements the 30-second auto-return** from DETECTION to IDLE (with a visible
   countdown in the prototype, e.g. a small fading progress bar under the detection,
   so the reviewer can see the timer — this is prototype-only, not in the real UI spec).

7. **Implements the DIM state** — after 15 seconds of no button interaction in the
   prototype (shortened from the real 60s for review purposes), the display dims
   to 10% brightness.

---

## Colour Palette

Use exactly these values from `07-ui-specification.md`:

```
Background:        #0D1B0E
Primary text:      #F0ECD8
Secondary text:    #8BA888
Accent:            #E8C84A
Confidence fill:   #4CAF50
Confidence bg:     #1E3320
Spectrogram low:   #1A3A5C
Spectrogram high:  #F0A030
Battery good:      #66BB6A
Battery low:       #FFA726
Battery critical:  #EF5350
Divider:           #2A4A2A
Button hint:       #567856
```

---

## Typography

Use **monospace or pixel-style web fonts** that approximate the embedded DejaVu Sans
bitmap rendering. Suggested: `'Courier New'` or import `'Share Tech Mono'` from
Google Fonts for the prototype. Scale all font sizes from the spec by 4× for the
prototype display (e.g. 16px spec → 64px in prototype, then fit within layout zones).

---

## Layout Precision

Implement the exact pixel layout zones from `07-ui-specification.md` for each screen,
scaled 4×. Do not improvise layout — the point of the prototype is to validate the
specified layout. If a layout zone is unclear from the spec, implement your best
interpretation and add a `// REVIEW:` comment in the code flagging the ambiguity.

---

## Device Shell

Render the device in a simple visual shell:
- Dark grey rounded rectangle representing the housing (approximately 750×600px total)
- The 640×512px display area centred in the upper portion
- Three labelled buttons (A, B, C) below the display within the shell
- A small status strip showing: current state name, battery %, simulated Wi-Fi icon
- Optional: a thin bezel around the display area to represent the housing front face

---

## State Persistence

Use React `useState` and `useEffect` for all state. No external libraries beyond
what is available in the Claude artifact environment (React, Tailwind, lucide-react,
recharts if needed for the spectrogram bars).

---

## Deliverable

A single self-contained `.jsx` React artifact that runs without any external
dependencies beyond those available in the Claude artifact sandbox.

Add a comment block at the top of the file:

```jsx
/**
 * BirdNET Remix — UI Prototype
 * Scale: 4× (160×128 → 640×512)
 * Reference: initial_design/07-ui-specification.md
 *
 * REVIEW NOTES:
 * - List any layout ambiguities or design decisions made here
 * - Flag anything that needs designer sign-off before Kiro implementation
 */
```

---

## Out of Scope for This Prototype

- Real MQTT integration
- Real button GPIO
- Actual bird detection
- Config UI character-cycling input (mock it as a static "entering password..." state)
- Actual PWM backlight (simulate with CSS opacity on the display div)
- Animations beyond what CSS transitions can handle simply
