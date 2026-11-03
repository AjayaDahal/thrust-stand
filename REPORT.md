# Thrust stand — Design Review Report

This is the record of the audit of the pendulum thrust stand as received (v0, kept unchanged in
`v0_archive/`) and of the redesign that fixes it (v1). "Fixed" means the CAD, the gate and the
documents no longer contain the defect. It does not mean the stand has been built: the checks that
only a build can close are listed under "Open".

**Method.** `scripts/audit_v0.py` rebuilds every v0 part from v0's own source, places it where
v0's render script put it, adds the tubes, the 2807 motor and the bolts the v0 README calls for,
and intersects everything pairwise with build123d; the overlaps are written as red solids for the
viewer's v0 mode (`v0_archive/audit/`). The mechanics were checked by hand (moment balance about
the pivot, cantilever bending, momentum theory for the prop wash), and the README's claims and
pass marks were checked against the CAD and against the VTOL project (`vtol-plane/DESIGN.md`,
`scripts/params.py`, `scripts/mass_balance.py`).

## Current status (v1, Nov 3, 2026)

**Ready to print.** Start with `pivot_head`, `arm_hub` and `motor_clamp`: they take the tubes and
the bolts, so they confirm the 25.8 mm and 15.0 mm bores on your printer before the rest.

- Gate: `scripts/check_stand.py` passes **9/9**: valid solids that fit the Kobra S1 bed; no
  collision between any two of the 19 placed printed parts, 3 tubes, 22 bolts (head, washers, nut),
  the bought parts and the board (91 touching or near pairs tested); every bolt 1–8 mm out of its
  nut or with the right thread engagement; every M4 nut behind ≥ 3 mm of wall; the motor plate takes
  the 19×19, 16×16 and both 16/19-cross patterns; both links on the thrust line and the centre plane
  (ratio 1.0000); the crank's arms equal (188.00 / 188.00 mm) with its nose on the anvil at the
  pivot's height (32.00) and the anvil on the scale (17.00); the swing stop at 3.9° both ways with
  the prop still clear; 7, 8 and 10 in prop discs clear of the board, post, masts and crank; no flat
  ceiling wider than 16 mm in any print.
- 18 print files sliced for the Kobra S1 (PETG, 4 walls, 30 % gyroid, 0.2 mm; `gcode/`):
  every build 494 g / 21.2 h; plus the pocket-scale option 209 g / 9.0 h or the load-cell
  option 178 g / 7.4 h; the calibration rig 203 g / 8.7 h.
- 3-D viewer with the v0 audit mode (`viewer/`), renders and animations (`renders/`), a dimensioned
  diagram (`diagram.png`), `BOM.md` (including the measuring scale), `README.md` (build and test).

**Open, can only be closed by building** (in order):

1. Measure the tubes: the post must be ≥ 728 mm and the arm ≥ 500 mm, or lower the pivot
   (`README.md`, "Tube cut list"). Measure the walls too: the cross-bolts are drilled through them.
2. Measure the pocket scale: platform height (17 mm assumed; the listing's text says ¾ in) and
   outline. More than 2 mm off: set `BENCH` and reprint the anvil.
3. Hold the motor plate against your 2212 motor before trusting the 16/19 slots: the 22xx
   pattern was not measured (the 2807's 19×19 was, in the VTOL project).
4. The load cell's real hole positions and thread (55–80 mm cells fit the mast's slot; the clevis
   assumes holes 5 and 20 mm from the end).
5. Pivot friction: with the link off, the arm must swing and settle within its ±4° stop.
6. Calibration with known weights over the pulley (`README.md`, "Calibrate"), and the pocket
   scale's own error against a calibration mass.
7. The prop-wash bias (finding 1.10): with the load cell, run the same prop tractor and pusher.

## Round 2 — one scale for the stand and the VTOL (Nov 3, 2026)

Request: one scale that measures thrust on the stand and also weighs the VTOL's parts. Chosen:
the **YONCON 3000 g / 0.1 g pocket kitchen scale** (~105 × 127 × 17 mm, 96 mm stainless platform,
0.5–3000 g). The luggage-scale option is gone.

| # | Topic | Finding | Change | Status |
|---|---|---|---|---|
| 2.1 | resolution | For thrust, 1 g is already 0.08 % of the 1235 g mark, below the vibration flicker, the ±0.5 % link geometry and the 4–8 % prop-wash bias: 0.1 g adds nothing there. It helps for the VTOL's small parts (a 9 g servo to 1 %) and costs no more. A 10 g luggage scale (0.8 %) could do neither job well. | 3000 g × 0.1 g; 3 kg covers the 2807's 1810 g data-sheet maximum, the crank's preload and, on a cradle, the whole ~2.0 kg plane. | chosen |
| 2.2 | geometry | A kitchen scale reads only a push on its platform; the stand's link pulls horizontally. A lever on the pendulum itself would bend the arm and change the 1:1 ratio. | `crank`: a bell crank on two 608 bearings, both arms 188 mm, pin straight above the pivot at shaft height, nose straight north of it level with the pivot. Its nose presses with the link's pull. | fixed, gated (6) |
| 2.3 | friction | A contact above or below the pivot scrubs as the scale flexes, and a plain bore would add stick-slip. | The nose touches level with the pivot, so it moves straight down; ball bearings: ≤ 0.09 g at 2 kg (μ 0.0015 at the 8 mm bore, axle load √2 × thrust). | fixed, gated (6), info |
| 2.4 | height | The pocket scale is only 17 mm tall, too low for the crank's hub and base under a pivot at the platform's height. | `scale_anvil` (15 mm, 14 g) stands on the platform and lifts the contact to 32 mm. Any 0.1 g scale up to 30 mm tall fits by changing only the anvil. | fixed, gated (6) |
| 2.5 | reuse | The scale has to come off for weighing parts and go back in the same place. | Two `scale_corner` stops; the anvil just sits on the platform; nose position, not anvil position, sets the lever arm. | fixed |
| 2.6 | link | The crank's pin is 293 mm south of the clamp's, beyond a 130 mm link. | `crank_link` 293 mm (prints diagonally); `cell_link` 130 mm for the load cell (no more 10 mm hook hole or bushing). | fixed, gated (2, 9) |
| 2.7 | limits | Tractor props only (the link must be in tension); the crank preloads ~28 g; a pocket scale switches itself off and zeroes at switch-on; a push on the arm goes 1:1 onto a 3 kg scale. | Tare before each run; switch on with the motor stopped; pusher runs and logging stay with the load cell; warnings in `README.md`. | documented |

## Round 1 — audit of v0 (as received) and the v1 fixes

Severity: **P0** cannot be built or reads wrong, **P1** wrong result or fails in use, **P2** print
or assembly problem, **P3** documentation.

| # | Severity | Finding | Fix (v1) | Status |
|---|---|---|---|---|
| 1.1 | P0 build | **The arm and the post occupy the same space.** Both stand at x = y = 0: the arm hangs from the pivot on top of the post, straight down along the post. They overlap from z 182 to 635 (229 538 mm³), and the arm also runs into the clevis's socket block above the post (5 067 mm³). The motor clamp and the brace clamp, both centred on x = y = 0, would have gripped the post as well, so there was no pendulum. The v0 diagram hid it by drawing the arm 28 mm aside ("in reality it hangs in line with the post"); the render drew post and arm as two identical white cylinders in the same place. | The post stands 70 mm beside the arm (y = −70). A new `pivot_head` caps the post and carries the axle over the arm: two cheeks either side of the hub and a bridge above it (an inverted U), with the post's socket beside it. It prints upside down with no supports. | fixed, gated (2) |
| 1.2 | P0 build | **The motor clamp's cross-bolt runs into the motor.** It ran along x through y = 0, z = 220, out of the face the motor plate sits on, on the motor's axis: with its nut, the M5×70 ends 6 mm inside the motor (118 mm³). No length fits: the nut needs 4 mm past the face, where the plate's centre hole and the motor's shaft end are. | The cross-bolt runs along y (M5×60), clear of the motor and of the plate bolts. | fixed, gated (2, 3) |
| 1.3 | P0 build | **The 2807 plate's holes do not match the motor.** They sit on a 19 mm circle (a 13.4 mm square); the Emax ECOII 2807 is 19×19 mm (as in the VTOL's `params.py`), so its screws miss (113 mm³). The 2212 plate's 16×19 *rectangle* does not match the usual 22xx pattern either, a cross with 16 mm on one axis and 19 mm on the other. | One `motor_plate` with slots: four on the diagonals (16×16 and 19×19 squares) and four on the cross (16 and 19 mm, either way round). | fixed, gated (5) |
| 1.4 | P0 build | **The motor screws' heads have nowhere to go.** The plate sits flat on the clamp and the M3 screws go in from the clamp side, so their heads must sit between the plate and the clamp (285 mm³ of overlap). | The plate is 8 mm thick with 4 mm counterbores on its back: the heads sit inside it, and an M3×8 gives 4 mm of thread in the motor, as in the VTOL. | fixed, gated (2, 3) |
| 1.5 | P0 build | **The M4 "nut traps" do not trap.** On the clamp's motor face and on the mast's flange the pocket opens onto the face the plate or platform sits on. Tightening pulls the nut out of its pocket against the plate, so the plate is clamped to its own nut and the clamp is not in the joint: the thrust pulls the motor plate off its clamp, and the platform can lift. | Side-entry slots behind a wall: the nut slides in from the side and bears on 6.0 mm of solid (clamp) or 3.2 mm (flange). | fixed, gated (4) |
| 1.6 | P1 accuracy | **The link pulls 4 mm above the thrust line.** It lay on top of a 4 mm tab whose mid-plane was the shaft height, so the scale read +0.84 %. The README's "hook ±10 mm is < 1 % error" is wrong: with that pin, a hook 10 mm low reads +1.8 %, 10 mm high +0.5 %. | A fork on the clamp's back holds the link on edge between two tines, pinned on an axis parallel to the pivot, exactly on the thrust line. Ratio 1.0000; hook 5 mm low +0.40 %, 5 mm high −0.25 %, 10 mm low +0.94 %. | fixed, gated (6) |
| 1.7 | P1 accuracy | **The brace is not needed, and it cost accuracy.** In a pendulum the thrust and the link's pull act almost on one line, so the pivot carries only the arm's weight plus ~0.8 % of the thrust: 0.44 mm of post bending at 1.5 kg, not the "~60 mm" the README warned of (that figure, 53 mm by calculation, assumes the whole thrust on the post top). Keeping the brace forced the scale line 30 mm sideways, which twists the pendulum (0.45 N·m at 1.5 kg) and loads the pivot bores sideways: up to ~6 g (0.4 %) of extra friction, growing with thrust. | Brace removed; the scale line runs on the centre plane (no twist). The guy cord stays as an option, for a stiffer post only. | fixed, gated (6) |
| 1.8 | P1 build | **The brace rule did not fit.** "Foot distance = clamp height" puts the foot's 45° socket axis 17.7 mm off the clamp socket's axis, so a straight tube cannot enter both (11 644 mm³ into the foot). The brace also needed 605 mm of thin tube (110 axle + 495); in the photos the thin tube looks about 400 mm long. | Brace removed (1.7); the thin tube only gives the 80 mm axle. | fixed |
| 1.9 | P1 test | **The pass marks are stale.** The README's 1155 g / 880 g belong to an older 3S study. The VTOL is now 4S with the ECOII 2807 1700KV on 7×4.5: each front motor carries 741 g in hover and must stay under 60 % of its near-empty thrust, so it needs **≥ 1235 g near empty** (`mass_balance.py` assumes 1250 g near empty, 1550 g on a full pack). | `README.md` "VTOL pass marks" uses the current numbers and where they come from. | fixed |
| 1.10 | P1 accuracy | **The prop-wash bias is larger than stated.** Pulling (tractor), the prop blows straight onto the motor plate, the clamp, the fork and the bottom of the arm. Momentum theory at 1.5 kg on a 7 in prop gives ~16 m/s through the disc and ~27 m/s a radius behind it; the parts in the jet then cost roughly 4–8 % of the reading (estimate), not 2–5 %. | Documented as installed thrust (conservative for a pass/fail). The load cell reads both ways, so the same prop can be run as a pusher (flip the prop, reverse the motor): the wash then blows away from the stand and the difference is the bias. | documented; to measure (open 6) |
| 1.11 | P2 print | **Three overhangs needed support:** the mast's flange stuck out 15 mm all round the 30 mm post (a 2700 mm² flat ceiling 198 mm up); the clamp's link tab stuck out 18 mm at mid-height; the hub's blind 25.8 mm arm bore ended in a flat 26 mm ceiling. | The flange flares out at 45°; the fork's tines run the clamp's full height; the hub's bore ends in a 45° cone. The gate rejects any flat ceiling wider than 16 mm (the widest left: 8 mm). | fixed, gated (9) |
| 1.12 | P2 build | **Bolt lengths.** M6×35 through the 8 mm foot, the 18 mm board, two washers and a nut leaves 0.8 mm: less than one thread. Nuts under the board also make it rock. | Wood screws (#10 × 1 in) hold the feet down. The gate checks every bolt: 1–8 mm out of its nut, or 4 mm of thread in the motor, 6–10 mm in the load cell. | fixed, gated (3) |
| 1.13 | P2 build | **Axle end pins.** The README said to cross-drill both ends of the axle and pin them with M5 bolts, which are not in its hardware list and not needed: the hub's cross-bolt pins the axle, and the cheeks hold the hub. | Dropped; the axle is 80 mm and ends 3 mm short of its blind bore. | fixed |
| 1.14 | P2 use | **The luggage scale was held by zip ties.** Only friction carried the pull, and the platform bolts' heads stood up under the scale. | A cord from the scale's handle to a slot at the platform's south end took the pull. Superseded in Round 2: the luggage scale and its platform are gone (2.2). | superseded |
| 1.15 | P2 print | **The link's 10 mm hook hole left 1 mm of plastic each side.** | A 20 mm round end: 5 mm each side. Superseded in Round 2: both links now have 3.5 mm pin holes at each end (2.6). | superseded |
| 1.16 | P1 test | **No calibration.** The 1:1 geometry was trusted, and so was the scale's own calibration; a load cell has none until you give it one. | A pulley rig (`cal_pulley_bracket`, `cal_wheel` on a 608 bearing, on `cal_mast` at the north edge): known weights pull along the thrust line, through the whole stand. Procedure in `README.md`. | fixed (open 6) |
| 1.17 | P3 docs | **The pictures could not show 1.1.** See 1.1: the diagram displaced the arm and the render overlaid two identical cylinders. | `diagram.png` is drawn from the CAD numbers with nothing displaced, and the three.js viewer has a v0 mode that shows the clashes in red. | fixed |
| 1.18 | P3 docs | **Hidden swing stop.** The hub's corner hit the clevis block 2 mm below it after 4.1°, so the README's "flick the arm, it should swing and settle" could not happen as described. | Kept on purpose and documented: the bridge, 2 mm above the hub, stops the swing at 3.9°. If the link breaks at full throttle, the prop end moves 33 mm and a 10 in disc still clears the post by 12 mm. | fixed, gated (7, 8) |
| 1.19 | P3 docs | **Unrunnable paths and an unchecked print time.** The scripts pointed at `/home/hatch/...`, and "~15 h across both printers" was not from a slicer. | Scripts run from `scripts/` with relative paths in the local `vtol-venv`; times come from the sliced G-code. | fixed |

### The v1 numbers behind the fixes

| Item | Value | Source |
|---|---|---|
| Scale force / thrust | 1.0000 (link pins on the thrust line, y = 0; crank arms 188.00 / 188.00 mm) | gate 6 |
| Link end height error | ±5 mm → +0.40 % / −0.25 %; −10 mm → +0.94 % | gate 6 |
| Crank bearings | ≤ 0.09 g at 2 kg (two 608s, μ ≈ 0.0015 at the bore) | gate info |
| Crank preload on the scale | ~28 g (crank's weight, CG 47 mm north of its pivot) + the 14 g anvil: tared | CAD + slicer |
| Sideways load on the post | ~0 (pivot carries the ~420 g pendulum) | moment balance |
| Pivot friction | ≤ 1.9 g at the thrust line (PETG on PVC, μ ≈ 0.3) | gate info |
| Gravity stiffness | 5.9 N/m: 0.6 g per mm the scale stretches (a load cell moves < 0.5 mm) | gate info |
| Swing stop | 3.9° either way; prop end moves 33 mm | gate 7 |
| Prop clearance to the board | 131 mm (7 in), 118 mm (8 in), 93 mm (10 in) | gate 8 |
| Prop clearance to the post at the stop | 15 mm (7 in), 14 mm (8 in), 12 mm (10 in) | gate 8 |
| Link buckling (pusher, load cell) | ~146 N for the 5 × 12 mm link pinned over 130 mm: 7× a 2 kg thrust | hand calc. |
