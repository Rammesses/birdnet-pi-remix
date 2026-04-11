# 03 — Bill of Materials

All prices are approximate GBP as of early 2026. UK suppliers preferred where available.
Alternatives listed where the primary source has stock risk.

---

## Core Electronics

| # | Component | Spec | Supplier | Part / Link | Est. £ |
|---|-----------|------|----------|-------------|--------|
| 1 | **Raspberry Pi Zero 2W** | 512MB RAM, 64-bit quad-core, Wi-Fi/BT | Raspberry Pi / Pimoroni / The Pi Hut | [pi.hut](https://thepihut.com/products/raspberry-pi-zero-2) | £15 |
| 2 | **MicroSD card** | 32GB+ A1/A2 class, e.g. SanDisk Endurance | Amazon | SanDisk MAX Endurance 32GB | £8 |
| 3 | **ST7735 1.8" TFT display** | 160×128, SPI, with 3 onboard buttons | AliExpress / Amazon | Waveshare 1.8" ST7735S HAT *or* bare breakout with buttons | £8–12 |
| 4 | **I²S MEMS microphone HAT** | Leaves GPIO SPI pins free; use **Adafruit I2S MEMS Mic Breakout (SPH0645)** or **ReSpeaker Mic Hat** — see note below | Pimoroni / Adafruit | [Adafruit SPH0645](https://www.adafruit.com/product/3421) | £6–10 |

> **Mic HAT note:** The ReSpeaker 2-Mic HAT uses the full GPIO header (HAT form factor)
> which would conflict with the ST7735 on SPI. Instead, use the **Adafruit SPH0645 I²S
> MEMS Microphone Breakout** — it's a small breakout board that connects via just 5 wires
> (3.3V, GND, BCLK, LRCLK, DOUT), leaving all SPI and other GPIO pins free for the
> display and buttons. Alternatively, the **Waveshare WM8960 Audio HAT** is higher
> quality but occupies the full header — only viable if the ST7735 connects via a
> dedicated SPI breakout rather than a HAT.
>
> **Recommended: Adafruit SPH0645** for pin compatibility simplicity.

---

## Power System

| # | Component | Spec | Supplier | Part / Link | Est. £ |
|---|-----------|------|----------|-------------|--------|
| 5 | **LiPo battery** | 3.7V, 2000mAh, JST-PH 2mm connector | Pimoroni / Amazon | e.g. [Pimoroni LiPo 2000mAh](https://shop.pimoroni.com/products/lipo-battery-pack) | £10 |
| 6 | **TP4056 LiPo charger module** | USB-C input, 1A charge, with protection circuit (DW01A) | Amazon / AliExpress | TP4056 Type-C with protection | £2 |
| 7 | **MT3608 boost converter** | 3.7V→5V, 2A output, adjustable | Amazon / AliExpress | MT3608 DC-DC step-up module | £1.50 |
| 8 | **Voltage divider resistors** | 100kΩ + 100kΩ (for VBAT sensing to 3.3V GPIO) | Any | 0805 or through-hole | <£1 |
| 9 | **100µF electrolytic capacitor** | Boost converter output filter | Any | 100µF 10V | <£1 |
| 10 | **Schottky diode** | 1N5819 — prevent back-feed from 5V to charger | Any | 1N5819 | <£1 |

> **Power budget estimate:**
> - Pi Zero 2W: ~120mA idle, ~300mA peak
> - ST7735 display: ~30mA
> - SPH0645 mic: ~600µA
> - Total worst-case: ~350mA @ 5V = 1.75W
> - 2000mAh LiPo @ 3.7V = 7.4Wh
> - Estimated runtime: **~4 hours** under continuous load (BirdNET-Go active)
> - For 6+ hours target: consider 3000mAh cell (increases housing depth by ~3mm)

---

## Housing & Mechanical

| # | Component | Spec | Supplier | Part / Link | Est. £ |
|---|-----------|------|----------|-------------|--------|
| 11 | **PETG filament** | 1.75mm, weather-resistant, ~100g needed | Amazon / Prusament | Any quality PETG | £3 (portion) |
| 12 | **O-ring cord / gasket** | 2mm dia. silicone cord, ~200mm for lid seal | Amazon | Silicone O-ring cord 2mm | £3 |
| 13 | **M2.5 × 6mm screws** | 4× for Pi Zero mounting | Amazon | M2.5 brass inserts + screws | £3 |
| 14 | **M3 × 10mm screws** | 4× for housing lid | Amazon | Stainless M3 | £2 |
| 15 | **M3 brass heat-set inserts** | 4× for housing lid threads | Amazon | M3 × 4mm × 5mm | £3 |
| 16 | **Cable gland** | PG7, waterproof, for USB-C cable entry | Amazon | PG7 nylon cable gland | £2 |
| 17 | **Display window** | 2mm clear acrylic, laser-cut or cut from sheet | Local / Amazon | 2mm clear acrylic sheet | £3 |
| 18 | **Microphone mesh** | Fine stainless steel mesh, ~10mm dia. | Amazon | Microphone protective mesh | £2 |
| 19 | **Waterproof sealant** | Clear silicone RTV, for acrylic window bond | B&Q / Amazon | Dow Corning 732 or similar | £5 |
| 20 | **Kickstand hinge pin** | 2mm steel rod, 20mm length | Amazon / hardware | 2mm steel rod | £1 |
| 21 | **Kickstand spring** | Small torsion spring or flat spring steel | Amazon | Assorted spring set | £3 |

---

## Consumables & Misc

| # | Component | Spec | Supplier | Est. £ |
|---|-----------|------|----------|--------|
| 22 | Dupont / JST cables | Female-female jumper wires, 20cm | Amazon | £2 |
| 23 | Header pins | 2.54mm male, for soldering to SPH0645 breakout | Amazon | £1 |
| 24 | Kapton tape | Electrical insulation inside housing | Amazon | £2 |
| 25 | Thermal pad | 0.5mm, for Pi Zero to housing heat transfer | Amazon | £2 |

---

## Tools Required (assumed available)

- Soldering iron + solder
- 3D printer capable of PETG (0.4mm nozzle, 250°C+ hotend)
- Multimeter
- Small flat/Phillips screwdrivers
- Tweezers
- Heat-set insert tool or soldering iron tip

---

## Total Estimated Cost

| Category | £ |
|----------|---|
| Core electronics | ~£41–47 |
| Power system | ~£18 |
| Housing & mechanical | ~£31 |
| Consumables | ~£7 |
| **Total** | **~£97–103** |

> This excludes tools and assumes the Pi Zero 2W is purchased new at RRP.
> With parts already on hand (Pi, filament, misc hardware), cost drops to ~£50–60.
