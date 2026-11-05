# Thrust stand — Bill of materials (v1)

Quantities for one stand. Prices are left out, as in the VTOL project: check them when you buy.
Where each part goes and how it is assembled: `README.md`. Why it is built this way: `REPORT.md`.

The stand is the same whichever scale you use. Build the **core**, then add **one** of the two
measuring options, **A: a 0.1 g pocket kitchen scale under a bell crank** (recommended: the same
scale weighs the VTOL's parts) or **B: a load cell** (logs, reads push and pull), and preferably the
**calibration rig**.

## 1. Printed parts (Kobra S1)

Sliced with `slicer_profiles/` (PETG, 0.2 mm, 4 walls, 30 % gyroid, no supports anywhere) in
Anycubic Slicer Next 2.0.0.3. Mass and time are the slicer's, from `gcode/<part>.gcode`. Print
orientation is baked into `stl/<part>.stl` and `3mf/<part>.3mf` (slicer projects with these
settings): slice as is, do not rotate. `3mf/complete_project.3mf` holds every part on six plates
and prints the ones marked PLA+ in PLA+ at 15 % instead: they only stand or locate.

| Part | Qty | For | Material | Mass | Time | Notes |
|---|---|---|---|---|---|---|
| `post_foot` | 1 | core | PLA+ | 132.3 g | 5 h 25 min | post stands on the board through it |
| `pivot_head` | 1 | core | PETG | 149.8 g | 5 h 56 min | prints upside down; ream the 15 mm bores until the axle turns freely |
| `arm_hub` | 1 | core | PETG | 97.5 g | 3 h 55 min | 15 mm axle bore, 25.8 mm arm bore with a 45° roof |
| `motor_clamp` | 1 | core | PETG | 91.4 g | 3 h 31 min | link fork on the back; M4 nut slots open on the side away from the post |
| `motor_plate` | 1 | core | PETG | 17.4 g | 44 min | fits 19×19 (ECOII 2807), 16×16 and 16/19-cross (22xx) motors |
| **Core total** | | | | **488 g** | **19 h 31 min** | |
| `crank` | 1 | A | PETG | 108.2 g | 4 h 21 min | prints flat; a 608ZZ presses in flush from each face (straight bore since v1.1) |
| `crank_base` | 1 | A | PLA+ | 50.4 g | 1 h 55 min | slotted foot: slide it to set the arm plumb |
| `crank_link` | 1 | A | PETG | 14.9 g | 31 min | 293 mm pin to pin; lies diagonally on the bed |
| `crank_spacer` | 1 | A | PLA+ | 0.1 g | 1 min | 2 mm ring between the bearings' inner races |
| `scale_anvil` | 1 | A | PLA+ | 13.9 g | 31 min | 15 mm tall for a 17 mm scale: lifts the contact to the crank's pivot |
| `scale_corner` | 2 | A | PLA+ | 8.3 g each | 21 min each | corner stops: the scale goes back to the same spot |
| **Option A total** | | | | **204 g** | **8 h 00 min** | |
| `cell_link` | 1 | B | PETG | 7.0 g | 16 min | 130 mm pin to pin |
| `cell_mast` | 1 | B | PLA+ | 158.8 g | 6 h 03 min | slot takes 55–80 mm bar cells |
| `cell_clevis` | 1 | B | PETG | 9.7 g | 28 min | counterbored for the M5 heads |
| **Option B total** | | | | **175 g** | **6 h 47 min** | |
| `cal_mast` | 1 | calibration | PLA+ | 175.8 g | 6 h 58 min | at the board's north edge; remove it before running |
| `cal_pulley_bracket` | 1 | calibration | PLA+ | 20.6 g | 54 min | |
| `cal_wheel` | 1 | calibration | PLA+ | 3.2 g | 7 min | press onto the 608 bearing |
| `guy_anchor` | 1 | optional | PETG | 24.0 g | 1 h 10 min | only for a stiffer post; accuracy does not need it (not in the full project) |

With both printers running, the core and one option is about 14 h each. Print `pivot_head`,
`arm_hub` and `motor_clamp` first: they show whether your printer's 25.8 mm and 15.0 mm bores fit
the tubes before the rest is committed.

## 2. Tubes (your stock)

| Piece | Stock | Cut | Notes |
|---|---|---|---|
| Post | 25.4 mm tube | 728 mm | stands on the board; its top sits in the pivot head's socket |
| Pendulum arm | 25.4 mm tube | 500 mm | 30 mm into the hub, through the clamp, 8 mm out below |
| Pivot axle | 14.66 mm tube | 80 mm | turns in the pivot head's 15 mm bores |

Shorter tubes: `README.md`, "Tube cut list". The rest of the thin tube is spare (v0's brace is gone).

## 3. Hardware

Socket-head screws unless noted; "washer" = plain flat washer. The gate (`scripts/check_stand.py`)
checks each length against what it clamps.

| Item | Core | A | B | Cal. | Guy | Where |
|---|---|---|---|---|---|---|
| M5×80 | 1 | | | | | post_foot, through the post |
| M5×70 | 2 | | | | | arm_hub: through the axle, through the arm |
| M5×60 | 2 | | | | | pivot_head through the post; motor_clamp through the arm (sideways) |
| M5 nut | 5 | | | | | |
| M5 washer | 10 | | 6 | | | B: one under each head and two (2 mm) as the cell's spacer, per screw |
| M5×40 | | | 2 | | | through cell_mast into the cell's fixed end (M4×40 if your cell is M4) |
| M5×12 | | | 2 | | | cell_clevis into the cell's free end (M4×12 if M4) |
| M4×20 | 2 | | | | | motor_plate to motor_clamp |
| M4×16 | | | | 2 | | cal_pulley_bracket to the mast |
| M4 nut | 2 | | | 2 | | slide into the side slots |
| M3×8 | 4 | | | | | motor to plate; heads sit in the counterbores, 4 mm into the motor |
| M3×20 + M3 nyloc + 2 M3 washers | 1 | 1 | 1 | | | link pin in the fork; A: link to the crank's tab; B: link in the clevis. Snug: it must pivot |
| M8×45 + M8 nut + 2 M8 washers | | 1 | | | | crank axle: clamps the bearings' inner races and the spacer between the base's bosses |
| M8×30 + M8 nut + 2 M8 washers | | | | 1 | | pulley axle |
| 608ZZ bearing (8×22×7) | | 2 | | 1 | | A: in the crank; calibration: the pulley |
| Wood screw #10 × 1 in (4.5–5 × 25 mm) | 4 | 6 | 2 | 2 | 2 | holding each foot down; A: crank base 2, corner stops 4 |
| Zip ties | ~6 | | 2 | | | ESC and leads on the arm; B: the cell's wires |
| Cord (paracord or braided line) | | | | | 1.5 m | guy cord |

Board: plywood or MDF, at least 700 × 400 × 18 mm, four rubber feet, and two clamps to hold it to
the bench while running.

## 4. The measuring scale

The scale is the only part that decides accuracy: the stand passes the thrust to it 1:1 (within
0.5 % for a link end ±5 mm off the shaft height, `REPORT.md`). Pick one option.

### Option A — 0.1 g pocket scale and bell crank (recommended: one scale for the stand and the VTOL)

| Item | Qty | Spec |
|---|---|---|
| Pocket kitchen scale, **3000 g × 0.1 g** | 1 | the design is drawn round the **YONCON 3000 g / 0.1 g** "Digital Food Kitchen Scale Upgraded" (Amazon B092W43Q25, ~$10): weighs 0.5–3000 g; about 105 × 127 × 17 mm (the text says 4 × 5 × ¾ in); stainless platform 96 mm long at one end, display and buttons at the other; tare; 2 × AAA (included); 2 plastic trays |
| Calibration mass, 1 kg (or 500 g) | 1 | optional but worth it: checks the scale itself at the thrust you care about (section "Calibrate" in the README) |
| Batteries, AAA | spares | |
| Printed and hardware | | `crank`, `crank_base`, `crank_link`, `crank_spacer`, `scale_anvil`, `scale_corner` ×2; 2 × 608ZZ, M8×45 + nut + 2 washers, M3×20 + nyloc + 2 washers, 6 wood screws (section 3) |

**Measure yours when it arrives:** the height of the platform's top above the bench (the design
assumes 17.0 mm) and its outline. `scale_anvil` stands on the platform and makes up the difference
to the crank's pivot height, 32 mm, so it is 15 mm tall; for another height set `BENCH["H"]` in
`scripts/build_thrust_stand.py`, run `scripts/build_all.py` and print the new anvil (37 min). The
corner stops follow `BENCH["L"]`/`BENCH["W"]` the same way. Within ±2 mm you can leave it and set
the arm plumb with the crank base's slots.

**Other scales.** Any kitchen or pocket scale of **3–5 kg × 0.1 g**, up to 30 mm tall, with tare and
a flat platform at least 60 mm across works the same way: set its size in `BENCH` and rebuild.
Some 5 kg models are dual-range (0.1 g only up to 1–2 kg, 0.5–1 g above): check the specification.
A taller bench scale (e.g. the US-Balance US-SUPER BENCHTOP, 31.75 mm) needs no anvil.

Why this scale: 0.1 g resolves small parts (a 9 g servo to 1 %), and the same scale weighs the
VTOL's printed parts, battery and, on a cradle, the whole plane (about 2.0 kg in hover, from the
motor loads). For thrust, 1 g would have been plenty (1 g is 0.08 % of the 1235 g mark; the
reading flickers by more than that while the motor runs). 3 kg covers the ECOII 2807's 1810 g
data-sheet maximum plus the crank's ~30 g preload. A kitchen scale only reads a push on its
platform, so the bell crank turns the link's pull into one, 1:1 (README, "How it works"). It reads
tractor props (the link in tension); for pusher runs and logging, use option B. Its platform is
small: never lean on the pendulum arm, which would press the scale with your whole push.

### Option B — load cell, HX711 and Arduino (logs; reads push and pull)

| Item | Qty | Spec |
|---|---|---|
| Straight-bar load cell, 5 kg | 1 | aluminium parallel beam, 12.7 mm square, 55–80 mm long, two tapped holes at each end (e.g. SparkFun SEN-14729 TAL220B, or the generic "5 kg load cell + HX711" kit) |
| HX711 load-cell amplifier | 1 | 24-bit; usually bundled with the cell. SparkFun SEN-13879 has a 10/80 samples/s jumper; generic green boards run at 10/s |
| Arduino Nano (or Uno, or an ESP32) | 1 | + USB cable to a laptop for logging |
| Jumper wires | 4 + 4 | cell to HX711 (often pre-soldered), HX711 to Arduino |
| Hardware and printed parts | | M5×40 ×2, M5×12 ×2, M5 washers ×6, M3×20 + nyloc; `cell_link`, `cell_mast`, `cell_clevis` |
| Optional: 0.96 in SSD1306 I2C OLED + a push button | 1 + 1 | stand-alone readout with a tare button |

5 kg is the right range: the VTOL motor's 1.8 kg data-sheet maximum is 37 % of it, overload is
typically rated at 150 %, and with 10 averaged samples the resolution is a few grams. A bar cell
reads push and pull, so it also measures a pusher prop (the prop-wash check in `README.md`).

Wiring (SparkFun colour code; check your cell's sheet): red → E+, black → E−, green → A+,
white → A−; HX711 VCC → 5 V, GND → GND, DT → D3, SCK → D2. If thrust reads negative, swap A+ and
A−. Software: the Arduino "HX711" library (Bogdan Necula), `tare()` with the motor off, then
`set_scale()` with the factor from the calibration below, and print `get_units(10)` to the serial
port.

### Calibration rig (needed for B, a check for A)

| Item | Qty | Spec |
|---|---|---|
| Printed: `cal_mast`, `cal_pulley_bracket`, `cal_wheel` | 1 each | bolts to the board's north edge |
| 608ZZ bearing, M8×30 + nut + 2 washers, M4×16 ×2 + nuts | 1 set | see section 3 |
| Braided line, ≥ 10 kg | 1–2 m | from the prop nut over the pulley |
| Known weights | 0.5–2 kg | water bottles weighed on the pocket scale (to 0.1 g), or calibration weights, in a bag on an S-hook |

## 5. To run a test (mostly the VTOL's own kit)

| Item | Qty | Notes |
|---|---|---|
| Motor | 1 | the VTOL's Emax ECOII 2807 1700KV (or your 22xx motors) |
| ESC, 50 A | 1 | the VTOL's; it takes plain servo PWM from a servo tester |
| Props 7×4.5 | 2+ | the VTOL's size; a spare for the pusher check (load cell) |
| Battery, 4S 5000 mAh | 1 | the VTOL's pack; full and near empty are both test points |
| Wattmeter, inline, XT60, ≥ 100 A | 1 | voltage, current and power for every step |
| Servo tester | 1 | throttle; or the transmitter and receiver, throttle channel straight to the ESC |
| Safety glasses | 1 | |
| Optional: optical tachometer + reflective tape | 1 | adds RPM to thrust, voltage and current |
