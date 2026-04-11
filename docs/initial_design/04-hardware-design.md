# 04 — Hardware Design

## Pi Zero 2W GPIO Pin Assignment

The Pi Zero 2W uses the standard 40-pin GPIO header.
Constraints:
- I²S mic uses: GPIO 18 (BCLK), GPIO 19 (LRCLK), GPIO 20 (DOUT)
- ST7735 SPI display uses: SPI0 (GPIO 10/11, MOSI/SCLK), plus CE, DC, RST
- Buttons: 3 GPIO inputs with pull-ups
- Battery ADC: 1 GPIO (voltage divider to 3.3V ADC-capable pin — note: Pi has no
  built-in ADC, so we use a 1-bit threshold via GPIO or add a small MCP3008 ADC)

> **ADC Note:** The Pi Zero 2W has no analogue input. Options:
> A) Use a **voltage comparator** (e.g. LM393) with a fixed threshold to give a
>    single "low battery" GPIO signal — simple but coarse.
> B) Add a **MCP3008 SPI ADC** (8-channel, 10-bit) on SPI1 (CE2) — more complex
>    but gives real percentage readings.
> C) Use the **INA219 I²C current/voltage sensor** — clean, uses I²C (GPIO 2/3).
>
> **Recommended: INA219 on I²C** — fewest extra pins, gives both voltage AND
> current (useful for estimating battery %). Add to BoM if accepted.

---

## Pin Assignment Table

| GPIO | Pin # | Function | Connected To |
|------|-------|----------|-------------|
| 2 | 3 | I²C SDA | INA219 SDA |
| 3 | 5 | I²C SCL | INA219 SCL |
| 8 | 24 | SPI0 CE0 | ST7735 CS |
| 9 | 21 | SPI0 MISO | (unused, ST7735 write-only) |
| 10 | 19 | SPI0 MOSI | ST7735 SDA/MOSI |
| 11 | 23 | SPI0 SCLK | ST7735 SCK |
| 18 | 12 | PCM CLK / I²S BCLK | SPH0645 BCLK |
| 19 | 35 | PCM FS / I²S LRCLK | SPH0645 LRCLK |
| 20 | 38 | PCM DIN / I²S DOUT | SPH0645 DOUT |
| 24 | 18 | GPIO output | ST7735 DC (data/command) |
| 25 | 22 | GPIO output | ST7735 RST (reset) |
| 16 | 36 | GPIO input, pull-up | Button A (left) |
| 26 | 37 | GPIO input, pull-up | Button B (middle) |
| 21 | 40 | GPIO input, pull-up | Button C (right) |
| — | 1 | 3.3V | ST7735 VCC, SPH0645 VCC, INA219 VCC |
| — | 2 | 5V | (internal, from boost converter) |
| — | 6 | GND | All component grounds |

---

## I²S Microphone Wiring (SPH0645)

```
SPH0645 Breakout    →    Pi Zero 2W
─────────────────────────────────────
3V                  →    Pin 1  (3.3V)
GND                 →    Pin 6  (GND)
BCLK                →    Pin 12 (GPIO 18)
LRCLK               →    Pin 35 (GPIO 19)
DOUT                →    Pin 38 (GPIO 20)
SEL                 →    GND    (selects left channel; tie low)
```

---

## ST7735 Display Wiring

```
ST7735 Breakout     →    Pi Zero 2W
─────────────────────────────────────
VCC                 →    Pin 1  (3.3V)
GND                 →    Pin 6  (GND)
CS                  →    Pin 24 (GPIO 8, SPI0 CE0)
RESET               →    Pin 22 (GPIO 25)
DC (A0)             →    Pin 18 (GPIO 24)
MOSI (SDA)          →    Pin 19 (GPIO 10)
SCK (SCL)           →    Pin 23 (GPIO 11)
LED (backlight)     →    Pin 1  (3.3V) via 47Ω resistor, or GPIO PWM for brightness control
```

> If brightness control via buttons is required, wire LED backlight to GPIO 12
> (hardware PWM) instead of direct 3.3V. Add this to BoM: 1× 47Ω resistor.

---

## Button Wiring

Buttons are normally-open momentary switches, wired active-low with internal pull-ups
enabled in software.

```
Button A  →  GPIO 16 (Pin 36)  +  GND
Button B  →  GPIO 26 (Pin 37)  +  GND
Button C  →  GPIO 21 (Pin 40)  +  GND
```

---

## INA219 Power Monitor Wiring

The INA219 sits in series with the battery output to measure current and voltage.

```
INA219              →    Circuit
──────────────────────────────────
VCC                 →    3.3V
GND                 →    GND
SDA                 →    Pi GPIO 2 (Pin 3)
SCL                 →    Pi GPIO 3 (Pin 5)
VIN+                →    Battery positive (after TP4056 output)
VIN-                →    Boost converter input positive
Shunt               →    0.1Ω onboard shunt resistor (standard on INA219 module)
```

---

## Power Circuit Schematic (text)

```
USB-C input (5V)
     │
     ▼
TP4056 Module (with DW01A protection)
  CHRG LED ──▶ (optional status LED, mount on housing)
  STBY LED ──▶ (optional status LED)
  BAT+ ──────────────────────────────────┐
  BAT- ──────────────────────────────────┤
     │                                   │
     ▼                                   │
LiPo Cell (3.7V 2000mAh)                │
     │                                   │
     └──▶ INA219 VIN+ ──▶ INA219 VIN- ──┘
                               │
                               ▼
                     MT3608 Boost Converter
                     (set output to 5.1V)
                               │
                      100µF cap to GND
                               │
                               ▼
                     Pi Zero 2W 5V input (Pin 2)
                     (via 1N5819 diode to prevent
                      back-feed when USB-C present)
```

> **Important:** The TP4056 can charge the LiPo while the boost converter simultaneously
> powers the Pi — this is the "charge-and-use" behaviour. Ensure the TP4056 module
> selected includes battery protection (DW01A). The INA219 shunt sits between the
> battery output and boost input, measuring discharge current.

---

## `/boot/config.txt` Entries Required

```ini
# I2S microphone (SPH0645)
dtparam=i2s=on
dtoverlay=i2s-mmap

# SPI for ST7735 display
dtparam=spi=on

# I2C for INA219
dtparam=i2c_arm=on

# Disable audio PWM (conflicts with I2S)
dtparam=audio=off

# Optional: GPU memory minimum (headless)
gpu_mem=16
```

---

## Updated BoM Additions

The following items should be added to the BoM from `03-bill-of-materials.md`:

| # | Component | Spec | Est. £ |
|---|-----------|------|--------|
| 26 | **INA219 I²C current sensor module** | 0.1Ω shunt, 26V/3.2A range | £2 |
| 27 | **47Ω resistor** | For display backlight current limiting | <£1 |
| 28 | **Tactile push buttons** | 6mm×6mm SMD or through-hole, 3× | £1 |

> If using a pre-made ST7735 breakout that already includes buttons (e.g. Waveshare
> 1.8" with joystick/buttons), item 28 is not needed — verify the breakout's button
> GPIO connections against the pin table above and remap if necessary.
