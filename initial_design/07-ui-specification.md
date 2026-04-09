# 07 — UI Specification

## Display Parameters

| Parameter | Value |
|-----------|-------|
| Display | ST7735S 1.8" TFT |
| Resolution | 160 × 128 pixels |
| Orientation | Landscape (160px wide, 128px tall) |
| Colour depth | 16-bit RGB565 |
| Refresh target | 15fps (sufficient for this UI) |

---

## Colour Palette

A nature-inspired dark theme. Dark background reduces power draw and looks sharp
on the ST7735 in outdoor light.

| Role | Name | Hex | RGB |
|------|------|-----|-----|
| Background | Forest Night | `#0D1B0E` | 13, 27, 14 |
| Primary text | Bone White | `#F0ECD8` | 240, 236, 216 |
| Secondary text | Sage | `#8BA888` | 139, 168, 136 |
| Accent / highlight | Birch Yellow | `#E8C84A` | 232, 200, 74 |
| Confidence bar fill | Moss Green | `#4CAF50` | 76, 175, 80 |
| Confidence bar bg | Dark Moss | `#1E3320` | 30, 51, 32 |
| Spectrogram low | Deep Blue | `#1A3A5C` | 26, 58, 92 |
| Spectrogram high | Sky Amber | `#F0A030` | 240, 160, 48 |
| Battery good | Leaf Green | `#66BB6A` | 102, 187, 106 |
| Battery low | Amber | `#FFA726` | 255, 167, 38 |
| Battery critical | Red | `#EF5350` | 239, 83, 80 |
| Divider line | Dark Sage | `#2A4A2A` | 42, 74, 42 |
| Button hint text | Dim Sage | `#567856` | 86, 120, 86 |

---

## Typography

Pillow's default fonts are limited. We will use pre-rendered bitmap fonts or
embed a small TTF:

| Role | Font | Size | Notes |
|------|------|------|-------|
| Common name | **DejaVu Sans Bold** (TTF) | 16px | Hero text |
| Scientific name | DejaVu Sans Oblique | 11px | Italic, secondary |
| Confidence % | DejaVu Sans Bold | 13px | |
| Clock time | **DejaVu Sans Bold** | 28px | Large, centred |
| Clock date | DejaVu Sans | 11px | |
| History list | DejaVu Sans | 11px | |
| Button hints | DejaVu Sans | 9px | Bottom strip |
| Status icons | Custom 8×8 bitmap glyphs | 8px | Battery, Wi-Fi |

> DejaVu Sans is open source (Bitstream Vera licence) and well-legible at small
> sizes. Include the subset TTFs in the repository under `display/fonts/`.

---

## Layout Zones (Detection Screen)

```
 0         40        80       120       160
 ┌──────────────────────────────────────────┐ 0
 │  STATUS BAR                              │
 │  [wifi icon] [battery icon] [time 14:23] │ 14
 ├──────────────────────────────────────────┤
 │  COMMON NAME (large)                     │ 15
 │  Great Tit                               │ 33
 ├──────────────────────────────────────────┤
 │  SCIENTIFIC NAME (small italic)          │ 34
 │  Parus major                             │ 46
 ├──────────────────────────────────────────┤
 │  CONFIDENCE BAR                          │ 47
 │  [██████████████████░░] 87%              │ 62
 ├──────────────────────────────────────────┤
 │  SPECTROGRAM / VISUALISER AREA           │ 63
 │  ▁▂▄▆█▇▅▃▂▁▂▄▅▆▄▃▂▁▂▄                  │ 103
 ├──────────────────────────────────────────┤
 │  BUTTON HINT BAR                         │ 104
 │  [A]Bright  [B]History  [C▶]Off          │ 114
 └──────────────────────────────────────────┘ 128
```

Margins: 4px left/right, 2px top/bottom.

---

## Layout Zones (Idle Screen)

```
 ┌──────────────────────────────────────────┐ 0
 │  STATUS BAR (as above)                   │ 14
 ├──────────────────────────────────────────┤
 │                                          │ 15
 │            14:23:45                      │ 50
 │          Wednesday                       │ 63
 │         8 April 2026                     │ 76
 │                                          │
 │       ≋  Listening...  ≋                │ 95
 │       (animated pulse dots)              │
 │                                          │ 114
 ├──────────────────────────────────────────┤
 │  BUTTON HINT BAR                         │
 │  [A]Bright  [B]History  [C▶]Off          │ 128
 └──────────────────────────────────────────┘
```

---

## Layout Zones (History Screen)

```
 ┌──────────────────────────────────────────┐ 0
 │  "Recent Detections"       🔋[████░]     │ 14
 ├──────────────────────────────────────────┤
 │  14:23  Great Tit         ██████ 87%     │ 28
 │  14:18  Blue Tit          ███████92%     │ 42
 │  13:55  Robin             █████  78%     │ 56
 │  13:41  Song Thrush       ██████ 83%     │ 70
 │  13:30  Chaffinch         █████  71%     │ 84
 ├──────────────────────────────────────────┤
 │  [A]↑ Scroll  [B] Back  [C]↓ Scroll     │ 114
 └──────────────────────────────────────────┘
```

5 entries visible at once. Scroll by 1 row per button press.
Selected/top row highlighted with Birch Yellow text.

---

## Animations

### Listening Animation (Idle Screen)
- Three dots `· · ·` below "Listening..." text
- Dots pulse in sequence: `·̈  · ·` → `· ·̈ ·` → `· · ·̈` → repeat
- Period: 1.2 seconds total (0.4s per dot)
- Colour: cycles between Sage and Bone White

### Detection Transition
- New detection: common name slides in from right over 200ms (8 frames at 15fps)
- If same species detected again: confidence bar updates in-place, no slide

### Clock (Idle)
- Time updates every second
- No animation — just static update

### Battery Icon
- 5-segment icon: `[████░]` = 80%
- Segments: 0–20% = 1 seg (red), 20–40% = 2 seg (amber), 40%+ = green
- Charging: animated fill cycling upward while USB-C connected

---

## Status Bar Elements

The 14px status bar at the top of every screen contains (left to right):

```
[Wi-Fi icon]  [Battery icon + %]  [spacer]  [HH:MM time]
```

- Wi-Fi icon: solid when connected, outline when not, hidden when no SSID configured
- Battery icon: 5-bar glyph + numeric % (e.g. "87%")
- Time: HH:MM, 24-hour, updated every minute in non-idle screens
  (idle screen shows seconds in the main clock)

---

## Button Behaviour Summary

| Button | Short press | Long press (≥ 3s) |
|--------|-------------|-------------------|
| A (left) | Cycle backlight: 100% → 50% → 10% → 100% | — |
| B (middle) | Toggle History / back to previous screen | — |
| C (right) | — | Initiate graceful shutdown |

Button A also wakes the display from DIM state (returns to current screen at 100%).
Any button press resets the 60-second dim timer.

---

## Boot Splash Screen

Duration: displayed until MQTT broker is reachable (typically 10–20s after boot).

```
 ┌──────────────────────────────────────────┐
 │                                          │
 │                                          │
 │           🐦  BirdNET Remix              │
 │                                          │
 │         Starting up...                   │
 │         [░░░░░░░░░░░░░░░]                │
 │         (animated progress bar)          │
 │                                          │
 │                                          │
 └──────────────────────────────────────────┘
```

Progress bar pulses (indeterminate) until services are ready.

---

## Shutdown Screen

```
 ┌──────────────────────────────────────────┐
 │                                          │
 │                                          │
 │         Shutting down...                 │
 │                                          │
 │     Saving detections database           │
 │          Please wait                     │
 │                                          │
 │                                          │
 └──────────────────────────────────────────┘
```

Displayed for ~3 seconds during graceful shutdown sequence. Screen then goes black.

---

## Prototype Notes

Before Kiro implementation, a UI prototype will be built as an HTML/React artifact
in Claude to validate:
- Colour palette readability
- Layout proportions at 160×128
- Spectrogram/confidence bar design
- Typography sizing
- Animation concepts

The prototype will simulate all three screens and button interactions.
