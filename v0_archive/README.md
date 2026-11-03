# Pendulum thrust stand — build guide

A thrust stand like the Mech Ninja one, but with the measurement cleaned up.
It uses your tubes: the two long 25.4 mm tubes become the post and the
pendulum arm, and the thin 14.66 mm tube becomes the pivot axle and the
diagonal brace. All other structural parts are 3D-printed PETG.

See `diagram.png` for the side-view layout. All heights are above the
board top.

## How it works (and why it is better than a lever stand)

The motor hangs from a pivot at the top of the post. Thrust pushes the
pendulum forward; a luggage scale anchored at motor height pulls it back
through a short link. The link attaches at the motor clamp, so the scale
reads thrust directly — **1:1, no lever ratio to measure or get wrong**.

The arm barely moves (a luggage scale's spring stretches ~1–3 mm over the
480 mm arm), so the pendulum's gravity restoring force is ~1–2 g and the
pivot friction is a few grams. Accuracy is limited by your scale, not by
the stand. The Mech Ninja style lever stand, by contrast, multiplies any
error in its lever ratio straight into the reading.

## What is in this zip

- `stl/*.stl` — 13 printable parts (list below)
- `diagram.png` — side-view layout with the key dimensions
- `renders/*.png` — 3D renders of the assembled stand (5 angles)
- `build_thrust_stand.py` — the parametric source that generated the STLs
  (edit the numbers at the top and re-run if your tube sizes differ)
- `make_diagram.py` — the script that drew the diagram
- `README.md` — this file

## Tube cut list (your stock)

| Piece | Stock | Length | Notes |
|---|---|---|---|
| Post | 25.4 mm tube | ~635 mm | Top ends up 635 above the board |
| Arm | 25.4 mm tube | ~500 mm | Pivot to motor shaft = 480 |
| Pivot axle | 14.66 mm tube | ~110 mm | Cut this FIRST, then the brace |
| Brace | 14.66 mm tube | remainder | 45°, see the brace rule below |

**Brace rule:** the brace runs at 45°, so the foot's distance south of the
post must equal the clamp's height on the post. Pick a clamp height your
remaining thin tube can reach (e.g. 350 mm up the post → foot 350 mm
south → brace ≈ 495 mm long). Higher clamp = stiffer post. Do not skip
the brace: without it the 25.4 mm post flexes ~60 mm at full thrust.

If your tubes are shorter than the list, scale the stand down, keeping
two rules: motor shaft ≥ 150 mm above the board (prop clearance — a 10 in
prop needs 140 mm + margin), and pivot ≥ shaft + 400 mm.

**If the thin tube is too short for a useful brace** (under ~300 mm after
the axle cut, the brace would sit so low it barely helps): skip the rigid
brace and use a guy wire instead — print `guy_anchor`, bolt it ~400 mm
south of the post, loop paracord or steel wire around the post just under
the clevis, tie it through the anchor's eyelet, and tension it until the
post stops flexing. A tensioned wire is stiffer than the tube brace.

## Bill of materials

**Printed (PETG, 0.2 mm layers, 4 perimeters, 40% infill — ~15 h total
across both printers):**

| Part | Print orientation | Notes |
|---|---|---|
| post_foot | flat, base on bed | post passes through, bottoms on the board |
| pivot_clevis | upright, socket down | ream the 15 mm bores if tight |
| arm_hub | upright | 15 mm axle bore, 25.8 mm arm bore |
| motor_clamp | upright | M4 nut traps on the +x face, relief holes behind; link tab offset to y=+30 (see below) |
| motor_plate_2212 | flat | 16×19 mm pattern, for your 2212 motors |
| motor_plate_2807 | flat | 19 mm bolt circle, for 28xx motors |
| scale_mast | upright, foot on bed | gusset prints without support; 50 mm mast slots; place 30 mm sideways of the post centreline |
| scale_platform | flat | 140 long (north edge clears the brace); zip-tie slots for the scale body |
| scale_link | flat | 10 mm hole = scale hook end; runs at y=+30 with the scale line |
| brace_clamp | flat or upright | 45° socket — clean up with a drill if needed |
| brace_foot | flat | 45° socket |
| guy_anchor | flat | only if using the guy-wire brace (see above) |
| shim_plate | flat | print as many as needed (see setup) |

**Hardware:**

- M5 bolts + nuts: 2× 80 mm (post foot, clevis), 5× 70 mm (arm hub ×2,
  motor clamp, brace clamp ×2), 1× 60 mm (brace foot). These are the
  cross-bolts through the printed parts **and** the tubes.
- M4 × 12 bolts + M4 nuts: 2 for the motor plate, 2 for the scale
  platform. The nuts sit in the pockets on the mounting faces — drop them
  in before bolting the plate/platform on. A relief hole behind each
  pocket keeps the bolt from bottoming out. Add 5 mm of bolt length per
  shim_plate under the platform (M4 × 16 with one shim, × 20 with two).
- M3 × 16 bolt + nut: 1, the link pin at the motor clamp tab.
- M6 × 35 bolts + nuts + washers: 4 (post foot), 2 (scale mast slots),
  4 (brace foot). Or #10 wood screws into the board.
- Motor screws: the M3 screws that came with your motor (or M3 × 8).
- Zip ties: scale body + wire management.
- Board: plywood or MDF, ≥ 700 × 400 × 18 mm.
- Digital luggage scale, 20–50 kg capacity. Any hanging scale works.
- Servo tester (~$5) to drive the ESC — or your FS-i6S + receiver, throttle
  channel straight to the ESC. No flight controller needed.
- Optional but recommended: a wattmeter in series with the battery
  (thrust + current + voltage = efficiency in g/W).

## Assembly

1. **Board layout, south to north:** brace foot (south of post — exact
   spot set by the 45° rule in step 6), scale mast (~230 south **and
   30 mm sideways of the post centreline** — see the offset note in
   step 8), post foot (0), prop clearance north of the post. Mark the
   positions, then bolt the three feet to the board.
2. **Post:** slide the 25.4 mm tube into post_foot (it bottoms on the
   board) and into pivot_clevis (socket on top). Do not drill yet.
3. **Axle:** slide the 110 mm axle through the clevis bores and the
   arm_hub. The hub sits between the cheeks (2 mm clearance each side).
   The axle ends stick out ~18 mm per side — drill a 5 mm cross-hole near
   each end later and pin with an M5 bolt + nut so it cannot slide out.
4. **Arm:** slide the 25.4 mm arm tube into arm_hub from below and into
   motor_clamp at the bottom. Do not drill yet.
5. **Set the heights.** With everything loose, measure: pivot axle
   700 mm above the board, motor shaft 220 mm above the board (clamp
   centre = shaft height). Slide the tubes in their bores until both are
   right, then drill the cross-bolt holes through the printed parts and
   the tubes (use the printed holes as guides, drill slowly) and bolt
   everything. Tighten cross-bolts snug, not gorilla-tight — the tubes
   are hollow and will crush if you over-torque. This order matters — it
   absorbs any error in your tube lengths.
6. **Brace:** clamp brace_clamp on the post, set brace_foot on the board
   at the same distance south as the clamp height (45°), cut the brace
   tube to fit, slide it into both 45° sockets, drill and bolt.
7. **Motor:** bolt the right motor plate to motor_clamp (M4 bolts into
   the trapped nuts), then the motor to the plate (M3). Mount it so the
   prop sits on the **north** side, away from the post — thrust must pull
   the arm north and the scale (south) must resist it. If the scale goes
   slack when you throttle up, the motor is backwards. Route the motor
   wires through the plate's bottom notch and up the arm with zip ties.
   Mount the ESC on the arm with zip ties, as in the reference photo.
   **Battery goes on the board or strapped to the post, never on the
   pendulum arm** — its weight and wire pull would bias the reading.
   Leave a generous slack loop in the battery wires between the fixed
   battery and the moving ESC.
8. **Scale:** bolt scale_platform to the mast flange (M4 into the trapped
   nuts). Lay the scale on the platform, hook pointing north toward the
   arm, zip-tie it through the slots. If your scale's hook is wider than
   the link's 10 mm hole, drill the hole out to fit. Pin scale_link's
   3.5 mm hole to the motor clamp tab (M3 bolt + nut) and hook the scale
   hook through the 10 mm hole. **The whole scale line — tab, link,
   scale, mast — sits 30 mm sideways of the post centreline.** The
   brace tube runs in the centre plane, so a centred scale line would
   collide with it (and the mast post and platform would too). The
   offset does not affect the reading: the link is still straight along
   the thrust direction at shaft height, so the force balance is
   unchanged.
9. **Tension the link.** Slide the mast in its slotted foot holes until
   the link is taut with the arm hanging vertical, then tighten the mast
   bolts. The scale should read ~0 with no throttle.

## Setup checks (do these before the first run)

- **Arm vertical at rest:** hang a small weight or eyeball it against the
  post. If it leans, the link is pulling it — re-tension.
- **Hook level with the shaft:** the scale hook should sit at motor-shaft
  height (±10 mm is <1% error). Shim the platform with shim_plate prints
  if it is low, or lower the mast bolts if high.
- **Pivot spins freely:** flick the arm — it should swing and settle
  vertical. If it sticks, ream the 15 mm clevis bores with a 15 mm drill
  bit or sand them, and add a drop of silicone lubricant.
- **Prop clearance:** spin the prop by hand — it must clear the board
  (≥ 40 mm), the post, and the scale mast. A 10 in prop's bottom edge sits
  at 220 − 140 = 80 mm above the board. Good.
- **Zero:** with the link taut and no throttle, zero/tare the scale. If
  yours has no tare, note the no-load reading and subtract it.

## Running a test

1. Clamp or weigh the board down. Never hold the stand during a run.
2. Stand to the **side**, never in the prop plane. Throttle cut on.
3. Battery → wattmeter (if any) → ESC → motor. Servo tester or
   transmitter throttle to the ESC.
4. Step the throttle (25/50/75/100%), hold each step ~5 s, and note
   thrust + voltage + current. The reading will flicker ±20–50 g from
   prop vibration — note the middle of the range, not the peaks. If your
   scale auto-powers-off, keep each test inside its timeout or tap the
   scale between steps. Let the motor cool between full-throttle runs.
5. Test at full charge and again near empty — voltage changes thrust a
   lot, and that is exactly what the 3S question needs: your 1700KV
   motors on 3S with 7×4.5 and 8×4.5 props, full and near-empty voltage.

**Reading the numbers:** the scale shows *installed* thrust — prop thrust
minus the drag of the motor mount sitting in the prop wash, roughly 2–5%.
For comparing motors or props, use the same mount and the same battery
state; for absolute numbers, add ~2–5%. Pass marks from the VTOL analysis:
1155 g near-empty = the design gate; ~880 g = the practical minimum for
the 3S path.

## Troubleshooting

- **Reading drifts upward during a run:** the arm is binding on the pivot
  or the link is catching — ream the pivot bores, check the link is free.
- **Reading jumps around:** prop vibration — balance the prop, check the
  motor bolts, and make sure the board is not rocking.
- **Arm leans at rest:** link too tight or too loose — re-tension with the
  mast slots, then re-zero.
- **Scale reads with no throttle:** the link is pulling the arm off
  vertical — re-tension, re-zero.
- **Post visibly flexes:** brace clamp too low or brace loose — raise the
  clamp and re-tighten; the brace is not optional. If the thin tube is too
  short for a high clamp, switch to the guy-wire brace (see the tube cut
  list).

## Upgrade paths (later, not needed now)

- **Load cell + HX711 + Arduino** in place of the luggage scale: same
  geometry, continuous logging, thrust curves. The scale_platform bolt
  pattern is the mounting point to adapt.
- **Optical RPM sensor** on the arm: thrust + RPM + current = a full
  motor/prop dataset.
- **Second motor plate** for any other motor: measure its hole pattern,
  edit `motor_plate()` in `build_thrust_stand.py`, re-print.

## Safety

- A spinning prop at full throttle can cause serious injury. Treat every
  run like a flight: clear area, no loose clothing or cables near the
  disc, throttle cut armed, and never reach across the prop plane.
- Bolt-check before each session: motor plate, cross-bolts, mast bolts.
- Do not exceed the motor/ESC ratings. On 3S your 40 A ESCs are fine for
  28xx-class motors (~26 A full throttle scaled); watch motor and ESC
  temperature on long runs.
- Secure the board. A 1.5 kg thrust spike on a light board will walk it.
