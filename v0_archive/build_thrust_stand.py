#!/usr/bin/env python3
"""
Thrust stand for Ajaya's tubes — pendulum design, 1:1 scale reading.

Measured tube stock (from his caliper photos):
  - 2x long tubes:  OD 25.4 mm  (post + pendulum arm)
  - 1x short tube: OD 14.66 mm (pivot axle + diagonal brace)

Principle: the motor hangs from a pivot at the top of the post. Thrust
pushes the pendulum forward; a luggage scale anchored at motor height
pulls it back through a short link. The link attaches at the motor, so
scale reading = thrust (1:1, no lever ratio). The arm barely moves
(scale spring stretch ~1-3 mm over a 480 mm arm), so the pendulum's
gravity restoring force is ~1-2 g — negligible.

Layout (side view, x = thrust direction, z = up, board top = z 0):
  - post top (pivot assembly base) .... 635 mm above board
  - pivot axle ........................ 700 mm above board
  - motor shaft ....................... 220 mm above board (480 below pivot)
  - scale hook ........................ ~220 mm above board (level w/ shaft)
  - brace: 45 deg, foot distance south = clamp height on post

All printed parts are PETG. Holes are clearance; cross-bolts go through
the printed part AND the tube (drill through the tube using the printed
holes as a guide after setting heights). M4 motor-plate / platform bolts
thread into M4 nuts trapped in pockets on the mounting faces.

Run:  ~/workspace/tools/vtol-venv/bin/python build_thrust_stand.py
Out:  stl/<part>.stl
"""

import os
from build123d import *

# ---------------------------------------------------------------- dims
POST_OD = 25.4          # big tubes (measured 25.38 / 25.39)
THIN_OD = 14.66         # thin tube (measured 14.66)
BORE_POST = 25.8        # slip fit for 25.4 tube (0.4 clearance: real PVC varies)
BORE_THIN = 15.0        # slip fit for 14.66 tube (cross-bolts lock it, so loose is fine)
BORE_PIVOT = 15.0       # pivot bore: 0.34 mm clearance, axle must spin
D_M3, D_M4, D_M5, D_M6 = 3.5, 4.5, 5.5, 6.5   # clearance holes
NUT_M4 = 7.4            # across-flats trap pocket for M4 nut (7 mm nut)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl")


def cyl_z(r, z0, z1, x=0.0, y=0.0):
    """Vertical cylinder (axis z) from z0 to z1, centred at (x, y)."""
    return Pos(x, y, (z0 + z1) / 2) * Cylinder(r, abs(z1 - z0))


def cyl_x(r, x0, x1, y=0.0, z=0.0):
    """Cylinder along x from x0 to x1, centred at (y, z)."""
    return Pos((x0 + x1) / 2, y, z) * Rot(0, 90, 0) * Cylinder(r, abs(x1 - x0))


def cyl_y(r, y0, y1, x=0.0, z=0.0):
    """Cylinder along y from y0 to y1, centred at (x, z)."""
    return Pos(x, (y0 + y1) / 2, z) * Rot(90, 0, 0) * Cylinder(r, abs(y1 - y0))


def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(
        abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


# ---------------------------------------------------------------- parts
def post_foot():
    """Post foot: bolts to the board, post passes through and bottoms on
    the board itself (so the documented heights hold exactly)."""
    p = box(-50, 50, -50, 50, 0, 8)            # base plate
    p += box(-35, 35, -35, 35, 8, 50)          # boss
    p -= cyl_z(BORE_POST / 2, -1, 51)          # post bore, through to board
    p -= cyl_y(D_M5 / 2, -36, 36, z=29)        # cross-bolt through boss+post
    for sx in (-42, 42):
        for sy in (-42, 42):
            p -= cyl_z(D_M6 / 2, -1, 9, sx, sy)  # M6 base bolts (clear of boss)
    return p


def pivot_clevis():
    """Caps the post top. Two cheeks carry the 15 mm pivot bores.
    Local z: post top = 0. Axle height = +65."""
    p = box(-35, 35, -37, 37, -40, 15)         # socket block
    p -= cyl_z(BORE_POST / 2, -41, 5)          # post socket (blind at +5)
    p -= cyl_x(D_M5 / 2, -36, 36, z=-20)       # cross-bolt through block+post
    # cheeks: 10 mm thick, inner gap 54 mm, 75 mm tall, bores at z=+65
    p += box(-30, 30, -37, -27, 15, 90)
    p += box(-30, 30, 27, 37, 15, 90)
    p -= cyl_y(BORE_PIVOT / 2, -38, 38, z=65)   # pivot bores (both cheeks)
    return p


def arm_hub():
    """Between the clevis cheeks. Grips the axle (top) and the arm tube.
    Local z: hub bottom = 0, top = 70. Axle centre z = 48."""
    p = box(-30, 30, -25, 25, 0, 70)
    p -= cyl_y(BORE_THIN / 2, -26, 26, z=48)    # axle bore (through, along y)
    p -= cyl_z(BORE_POST / 2, -1, 30)          # arm bore (blind, 30 deep)
    p -= cyl_x(D_M5 / 2, -31, 31, z=48)        # cross-bolt hub+axle
    p -= cyl_x(D_M5 / 2, -31, 31, z=15)        # cross-bolt hub+arm tube
    return p


def motor_clamp():
    """Clamps the arm tube at its bottom end. Motor plate bolts to the
    +x face (trapped M4 nuts); link tab on the -x face.
    Local z: clamp centre = 0 (this is the motor shaft height)."""
    p = box(-30, 30, -25, 25, -30, 30)
    p -= cyl_z(BORE_POST / 2, -31, 31)         # arm tube through-bore
    p -= cyl_x(D_M5 / 2, -31, 31, z=0)         # cross-bolt clamp+arm tube
    # M4 nut traps opening on the +x face, each with a relief hole behind
    # it so an M4x12 bolt cannot bottom out before the plate clamps.
    for sy in (-20, 20):
        p -= box(26, 30, sy - NUT_M4 / 2, sy + NUT_M4 / 2, -NUT_M4 / 2, NUT_M4 / 2)
        p -= cyl_x(D_M4 / 2, 16, 26, y=sy, z=0)
    # link tab on the -x face, offset to y=+30 so the whole scale line
    # (tab, link, scale, mast) runs 30 mm sideways of the brace plane
    # and cannot collide with the brace tube, mast post, or platform
    p += box(-48, -30, 19, 41, -2, 2)
    p -= cyl_z(D_M3 / 2, -3, 3, x=-42, y=30)
    return p


def motor_plate(pattern):
    """Interchangeable motor plate, 56 x 48 x 4. Bolts to motor_clamp
    with 2x M4 at (y=+-20, z=0). Wire notch on the bottom edge.
    pattern: '2212' -> 16x19 mm rectangle; '2807' -> 19 mm bolt circle."""
    p = box(-2, 2, -28, 28, -24, 24)
    if pattern == "2212":
        holes = [(-8, -9.5), (-8, 9.5), (8, -9.5), (8, 9.5)]
    elif pattern == "2807":
        a = 9.5 / 2 ** 0.5
        holes = [(-a, -a), (-a, a), (a, -a), (a, a)]
    else:
        raise ValueError(pattern)
    for hy, hz in holes:
        p -= cyl_x(D_M3 / 2, -3, 3, y=hy, z=hz)
    p -= cyl_x(10.0 / 2, -3, 3, y=0, z=0)      # centre boss clearance
    for sy in (-20, 20):
        p -= cyl_x(D_M4 / 2, -3, 3, y=sy, z=0)
    p -= box(-3, 3, -5, 5, -25, -16)           # wire notch, bottom edge
    return p


def scale_mast():
    """Scale mast: foot with slotted M6 holes (50 mm travel: covers the
    full link-span range for any scale placement on the platform),
    190 mm post, gusset on the -x side, top flange with trapped M4 nuts.
    Foot extends to x=-60 so the gusset sits fully on it.
    Local z: board top = 0. Flange top = 204."""
    p = box(-60, 45, -45, 45, 0, 8)            # foot
    # slots along x (50 mm travel) for M6 bolts, at y=+-35
    for sy in (-35, 35):
        p -= box(-25, 25, sy - 3.5, sy + 3.5, -1, 9)
        p -= cyl_z(3.5, -1, 9, x=-25, y=sy)
        p -= cyl_z(3.5, -1, 9, x=25, y=sy)
    p += box(-15, 15, -15, 15, 8, 198)         # post 30x30x190
    p += box(-60, -13, -3, 3, 8, 140)         # gusset rib, -x side
    p += box(-30, 30, -30, 30, 198, 204)       # top flange
    for sx in (-20, 20):                       # M4 nut traps on flange top
        p -= box(sx - NUT_M4 / 2, sx + NUT_M4 / 2, -NUT_M4 / 2, NUT_M4 / 2,
                 200, 204)
        p -= cyl_z(D_M4 / 2, 197, 205, x=sx, y=0)  # relief through flange
    return p


def scale_platform():
    """140 x 80 x 5 plate. Scale lies along x, hook pointing +x (north,
    toward the arm). Zip-tie slots hold the scale body. 140 long (not
    160) so its north edge stops at x=-160 in assembly, clearing the
    brace tube by ~4 mm. Place at assembly y=+30 with the rest of the
    scale line."""
    p = box(-70, 70, -40, 40, 0, 5)
    for sx in (-20, 20):
        p -= cyl_z(D_M4 / 2, -1, 6, x=sx, y=0)
    for sx in (-50, 50):
        for sy in (-30, 30):
            p -= box(sx - 2, sx + 2, sy - 7.5, sy + 7.5, -1, 6)
    return p


def scale_link():
    """150 mm link bar. 3.5 mm hole pins to the motor clamp tab;
    10 mm hole takes the luggage-scale hook."""
    p = box(-75, 75, -6, 6, 0, 4)
    p -= cyl_z(D_M3 / 2, -1, 5, x=65)
    p -= cyl_z(10.0 / 2, -1, 5, x=-65)
    return p


def brace_clamp():
    """Grips the post (vertical bore) and the brace tube (45 deg socket
    opening on the -x face). Block 80 tall so the socket's opening ellipse
    stays inside the block. Local: block centre = 0.
    Socket axis: opening (-50, -25), direction (+0.707, +0.707), len 35."""
    p = box(-50, 50, -30, 30, -40, 40)
    p -= cyl_z(BORE_POST / 2, -36, 36)         # post bore
    p -= cyl_y(D_M5 / 2, -31, 31, z=0)         # cross-bolt block+post
    mid = (-50 + 17.5 * 0.7071, -25 + 17.5 * 0.7071)
    p -= Pos(mid[0], 0, mid[1]) * Rot(0, 45, 0) * Cylinder(BORE_THIN / 2, 35)
    p -= cyl_y(D_M5 / 2, -31, 31, x=mid[0], z=mid[1])  # cross-bolt block+brace
    return p


def brace_foot():
    """Bolts to the board; 45 deg socket takes the brace tube from above.
    Socket opening centred at x=8 so the opening ellipse stays inside the
    boss. Local z: board top = 0."""
    p = box(-45, 45, -30, 30, 0, 8)            # base plate
    for sx in (-32, 32):
        for sy in (-20, 20):
            p -= cyl_z(D_M6 / 2, -1, 9, x=sx, y=sy)
    p += box(-25, 25, -25, 25, 8, 58)          # boss
    mid = (8 - 17.5 * 0.7071, 58 - 17.5 * 0.7071)
    p -= Pos(mid[0], 0, mid[1]) * Rot(0, 45, 0) * Cylinder(BORE_THIN / 2, 35)
    p -= cyl_y(D_M5 / 2, -26, 26, x=mid[0], z=mid[1])  # cross-bolt boss+brace
    return p


def guy_anchor():
    """Fallback anchor for a guy-wire brace (use instead of the rigid brace
    tube if the thin tube is too short for a useful brace). Bolt to the
    board ~400 mm south of the post; tie paracord/steel wire from the post
    top (loop under the clevis) through the eyelet and tension it."""
    p = box(-30, 30, -30, 30, 0, 8)            # foot
    for sx in (-20, 20):
        p -= cyl_z(D_M6 / 2, -1, 9, x=sx, y=0)
    p += box(24, 30, -15, 15, 6, 48)           # eyelet plate, north edge
    p -= cyl_x(10.0 / 2, 23, 31, y=0, z=35)    # wire hole
    return p


def shim_plate():
    """60 x 60 x 5 shim for the scale platform (stack as needed so the
    scale hook sits level with the motor shaft)."""
    p = box(-30, 30, -30, 30, 0, 5)
    for sx in (-20, 20):
        p -= cyl_z(D_M4 / 2, -1, 6, x=sx, y=0)
    return p


PARTS = [
    ("post_foot", post_foot),
    ("pivot_clevis", pivot_clevis),
    ("arm_hub", arm_hub),
    ("motor_clamp", motor_clamp),
    ("motor_plate_2212", lambda: motor_plate("2212")),
    ("motor_plate_2807", lambda: motor_plate("2807")),
    ("scale_mast", scale_mast),
    ("scale_platform", scale_platform),
    ("scale_link", scale_link),
    ("brace_clamp", brace_clamp),
    ("brace_foot", brace_foot),
    ("guy_anchor", guy_anchor),
    ("shim_plate", shim_plate),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, fn in PARTS:
        part = fn()
        if not part.is_valid:
            raise RuntimeError(f"{name}: invalid solid")
        bb = part.bounding_box()
        print(f"{name:18s} vol={part.volume:10.0f} mm^3  "
              f"bbox=({bb.max.X - bb.min.X:.1f} x "
              f"{bb.max.Y - bb.min.Y:.1f} x {bb.max.Z - bb.min.Z:.1f}) mm")
        export_stl(part, os.path.join(OUT, f"{name}.stl"))
    print(f"Wrote {len(PARTS)} STLs to {OUT}")


if __name__ == "__main__":
    main()
