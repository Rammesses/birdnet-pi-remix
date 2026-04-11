# 05 — Housing Design

## Form Factor

The housing is a **handheld landscape-oriented enclosure**, sized to comfortably fit
in one hand while also sitting stably on a desk or windowsill via an integrated
rear kickstand.

### Target Dimensions (v1 estimate)

```
Width:   100mm
Height:   65mm
Depth:    28mm  (accommodates Pi + HAT stack + battery)

Display window: 47mm × 35mm (1.8" ST7735 active area + small bezel)
Button spacing: 3× buttons along bottom edge, 8mm spacing
```

---

## Component Layout (front view)

```
┌────────────────────────────────────────────────────┐
│  ┌────────────────────────────────────┐            │
│  │                                    │  [•][•][•] │
│  │         1.8" TFT Display           │   A  B  C  │
│  │          160 × 128 px              │            │
│  │                                    │            │
│  └────────────────────────────────────┘            │
│         ○  mic mesh                                 │
└────────────────────────────────────────────────────┘
```

- Display is left-aligned, centred vertically
- Three buttons are right of display, vertically centred
- Microphone mesh port is bottom-left or bottom-centre
- USB-C port is on the bottom edge (via cable gland or moulded port)

---

## Component Layout (rear view)

```
┌────────────────────────────────────────────────────┐
│                                                    │
│                  [Pi Zero 2W]                      │
│                                                    │
│          [LiPo cell]    [TP4056] [Boost]           │
│                                                    │
│              ╔═══════════════╗                     │
│              ║   kickstand   ║ (hinged, folds flat)│
│              ╚═══════════════╝                     │
└────────────────────────────────────────────────────┘
```

---

## Housing Construction

### Two-Part Shell

The housing consists of:
1. **Front shell** — contains display window, button holes, mic port, all aesthetic
   surfaces. Printed in PETG.
2. **Rear lid** — flat panel with Pi/battery mounting bosses. Attaches with 4×
   M3 screws into heat-set inserts in the front shell. Sealed with a silicone
   O-ring in a channel around the perimeter.

### Assembly Order
1. Install heat-set inserts into front shell lid seats (4 corners)
2. Mount Pi Zero 2W to rear lid on M2.5 standoffs
3. Attach SPH0645 breakout to inner front shell with kapton tape or small bracket
4. Bond display acrylic window with clear RTV silicone (allow 24h cure)
5. Route and dress all wiring
6. Place O-ring in channel
7. Mate front and rear, insert M3 screws
8. Install cable gland for USB-C lead

---

## IP54 Strategy

IP54 = dust protected (no full ingress) + splash proof from all directions.

| Risk point | Mitigation |
|------------|------------|
| Lid join | Silicone O-ring in printed channel, compressed by M3 screws |
| Display window | 2mm acrylic bonded with clear RTV silicone into a rebate |
| Microphone port | Fine stainless mesh + internal foam backing; mesh bonded with RTV |
| Button holes | Buttons protrude through tight-tolerance holes; silicone boot or tolerance seal |
| USB-C entry | PG7 cable gland (fixed cable) *or* moulded USB-C port with silicone seal |
| Rear lid | O-ring channel; no vents |

> **Note on buttons:** Achieving IP54 with exposed tactile buttons is the hardest
> challenge. Two approaches:
> A) **Tight-tolerance printed caps** over internal tactile switches — the cap passes
>    through a close-fitting hole, with a small silicone gasket behind the cap.
>    Effective and clean-looking.
> B) **External rubber membrane** over all three buttons — more robust but adds
>    thickness and less tactile feel.
> v1 will use approach A; v2 may switch to B if field testing shows ingress.

---

## Kickstand Design

The kickstand is a **hinged rear flap** that folds flat against the back of the device
for handheld use, and props open to ~65° for desk/windowsill use.

```
Side view (kickstand deployed):
                ___________
               /           |
              /  display   |
             /             |
            /______________|
           /                \
          / ← 65°            \
         /____________________\ ← kickstand
```

### Kickstand Mechanism
- Printed as a separate PETG part
- Hinges on a 2mm steel rod passing through lugs on the rear lid
- A small leaf spring (thin PETG flex, printed integral) provides two detent positions:
  flat (0°) and deployed (~65°)
- Kickstand surface is textured for grip

---

## Display Window

- 2mm clear acrylic, cut to 52mm × 40mm
- Bonded into a 1.5mm deep rebate in the front shell with clear RTV
- Rebate has a 0.5mm step to retain the acrylic during cure
- Inner surface: no coating (clean acrylic)
- Outer surface: optional anti-glare film (not included in v1)

---

## Printing Specification

| Parameter | Value |
|-----------|-------|
| Material | PETG (weather resistance, slight flex for snap/seal features) |
| Layer height | 0.2mm |
| Infill | 40% gyroid |
| Perimeters/walls | 4 (for strength and water resistance) |
| Top/bottom layers | 5 |
| Supports | Required for display window rebate and button holes (front shell only) |
| Orientation | Front shell: print face-down; rear lid: print outside-down |
| Estimated print time | ~4–5 hours total |
| Estimated filament | ~90–110g |

---

## STL Files to be Created

| File | Description |
|------|-------------|
| `housing_front.stl` | Main front shell with display rebate, button holes, mic port |
| `housing_rear.stl` | Rear lid with Pi mounting bosses, battery bay, O-ring channel |
| `kickstand.stl` | Hinged kickstand with integral spring detents |
| `button_cap_x3.stl` | External button caps (print 3) |
| `mic_shroud.stl` | Internal microphone mount / shroud |

> STL files will be designed in FreeCAD or Fusion 360. Source files (.FCStd / .f3d)
> will be published alongside STLs.

---

## Open Questions for Housing

- [ ] USB-C: fixed attached cable (simpler sealing) or flush IP-rated USB-C port?
      Fixed cable is simpler for v1 but less elegant.
- [ ] Colour: single colour PETG, or two-colour (front shell + rear lid in contrasting
      colours)? Depends on printer capability.
- [ ] Lanyard attachment point? A small lug on the top edge would allow wrist lanyard
      for field use.
- [ ] Charging indicator: should the TP4056 charge/standby LEDs be visible externally
      (small light pipes in housing), or monitored via INA219 only?
