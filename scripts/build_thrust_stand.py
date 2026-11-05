#!/usr/bin/env python3
"""Pendulum thrust stand, v1: the parametric source of every printed part and of the assembly.

What changed from v0 (REPORT.md has the audit): the post stands beside the arm instead of in line
with it (v0's arm and post occupied the same space), a yoke-shaped pivot head carries the axle over
the hub, the motor plate fits 19x19 and 16/19-cross motors with its screw heads recessed, every
M4 nut sits behind a wall in a side slot, the motor clamp's cross-bolt runs sideways (v0's ran into
the motor), the link is pinned on the thrust line in a fork, the scale line runs on the centre
plane, and the brace is gone. The scale is a 0.1 g pocket kitchen scale (3000 g), the same one
that weighs the VTOL's parts: a ball-bearing bell crank with equal arms turns the link's pull into
a press on a printed anvil standing on the scale, 1:1. A load-cell option and a calibration pulley
remain.

Coordinates, mm: x = thrust direction ("north", the prop end), y = sideways, z = up, board top z = 0.
The arm hangs at x = y = 0 from the pivot at Z_PIVOT; the motor shaft is at Z_SHAFT; the post
stands at y = POST_Y. Each part is modelled in assembly orientation around its own origin:
PARTS[name]["at"] lists where its copies go (pure translations), PARTS[name]["print"] the rotation
that lays it on the bed.

Run:  C:/Users/ajayad/venvs/vtol-venv/Scripts/python.exe scripts/build_thrust_stand.py
Out:  stl/<part>.stl (print orientation, ready to slice) and stl/assembly.json (placements, tubes,
      bolts and bought parts, read by check_stand.py and make_viewer.py).
"""
import json
import math
import os
import sys

import numpy as np
from build123d import Axis, Box, Cone, Cylinder, Plane, Polygon, Pos, Rectangle, Rot, export_stl, extrude, loft, revolve

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom as G  # noqa: E402

# ------------------------------------------------------------------ stock and clearances
POST_OD = 25.4          # the two long tubes (measured 25.38 / 25.39): post and arm
THIN_OD = 14.66         # the thin tube (measured 14.66): pivot axle
BORE_POST = 25.8        # slip fit for the 25.4 tubes; the cross-bolts lock them
BORE_PIVOT = 15.0       # the axle turns in these bores (0.34 mm clearance): ream if tight
D_M3, D_M4, D_M5, D_M8 = 3.5, 4.5, 5.5, 8.4           # clearance holes
D_BOARD = 5.0           # board screws: #10 / 4.5-5 mm wood screws
NUT = {"M3": (5.5, 4.0), "M4": (7.0, 3.2), "M5": (8.0, 4.0), "M8": (13.0, 6.5)}   # across flats, thickness (M3 = nyloc)
HEAD = {"M3": (5.5, 3.0), "M4": (7.0, 4.0), "M5": (8.5, 5.0), "M8": (13.0, 8.0)}  # socket head: diameter, height
CSK_M4 = (8.0, 1.85)                                  # M4 flat head (90 deg): diameter, countersink depth
SLOT_W, SLOT_T = 7.3, 3.6                             # M4 nut slot: width (across flats + 0.3), height
SLOT_END = 4.05                                       # slot end to bolt axis: half the nut's across-corners

# ------------------------------------------------------------------ layout
Z_SHAFT = 220.0         # motor shaft = thrust line above the board: 10 in prop clears the board by 93 mm
Z_PIVOT = 700.0         # pivot axle above the board (arm 480 mm, as in v0)
POST_Y = -70.0          # the post stands beside the arm, clear of it and of the scale line
BOARD = dict(x0=-480.0, x1=220.0, y0=-200.0, y1=200.0, t=18.0)

HUB = dict(x=30.0, y=25.0, h=70.0, axle=48.0, arm_depth=30.0)   # arm hub, axle 48 mm above its bottom
HUB_Z0 = Z_PIVOT - HUB["axle"]                                    # 652
CHEEK_IN, CHEEK_T = 27.0, 10.0      # pivot-head cheeks: 2 mm either side of the hub
STOP_GAP = 2.0                      # bridge above the hub's top: stops the swing at ~4 deg either way
HEAD_X = 30.0
HEAD_Z0 = -26.0                     # head bottom, below the axle
BRIDGE_Z0 = HUB["h"] - HUB["axle"] + STOP_GAP                     # 24 above the axle
HEAD_Z1 = BRIDGE_Z0 + 14.0          # head top, 38 above the axle
POST_TOP = Z_PIVOT + HEAD_Z1 - 10.0                               # post top (728): socket blind 10 mm below the roof
AXLE_Y = (-(CHEEK_IN + CHEEK_T) - 5.0, CHEEK_IN + CHEEK_T + 1.0)   # axle ends: 80 mm, 3 mm short of its blind bore
ARM_TOP = HUB_Z0 + HUB["arm_depth"]                               # 682
ARM_BOT = Z_SHAFT - 30.0 - 8.0                                    # 8 mm out of the clamp's bottom

CLAMP = dict(x=30.0, y=25.0, z=30.0)
PLATE_T = 8.0           # motor plate: screw heads sit in 4 mm counterbores, 4 mm under them
PLATE_BOLT_Z = 23.0     # M4 plate bolts above and below the motor, outside the bell
NUT_X = (20.4, 24.0)    # their nuts, 6 mm behind the clamp's face
FORK_GAP, FORK_T, FORK_X = 5.6, 4.0, (-46.0, -30.0)
PIN_X = -40.0           # link pin, on the thrust line (z = Z_SHAFT, y = 0)
LINK = dict(half=65.0, t=5.0, h=12.0)
X_HOOK = PIN_X - 2 * LINK["half"]          # -170: scale hook / load-cell pin
X_PLATE_FRONT = CLAMP["x"] + PLATE_T       # 38: the motor's base sits here

MAST_FLANGE = 204.0                        # top of the scale mast (now the calibration pulley's mast)
# The one scale for the stand and for weighing the VTOL's parts: YONCON 3000 g x 0.1 g pocket kitchen
# scale, 105 x 127 x 17 mm, stainless platform 96 mm long from 3 mm off one end, display at the other
# (listing numbers: measure yours). It lies sideways, display to the east (-y), platform centre under
# the crank's nose.
BENCH = dict(L=127.0, W=105.0, H=17.0, steel_l=96.0, steel_w=100.0, steel_c=51.0)   # steel_c: from the far end
Z_NOSE = 32.0                              # crank pivot = nose contact height; the anvil makes up the rest
CRANK = dict(r=Z_SHAFT - Z_NOSE, t=16.0, w_v=30.0, h_h=28.0, nose=5.0, clear=8.0, hub=16.0)
ANVIL = dict(h=Z_NOSE - BENCH["H"], base=(50.0, 44.0), top=(34.0, 28.0))
BEARING_SEAT = 22.1                        # 608ZZ outer race, push fit
X_PAN = -145.0                             # platform and anvil centre: clear of the post foot
X_CRANK = X_PAN - CRANK["r"]               # crank pivot: equal arms, so the anvil sees the link's pull 1:1
SCALE_Y = (BENCH["steel_c"] - BENCH["L"], BENCH["steel_c"])
CELL = dict(L=75.0, w=12.7, end=5.0, pitch=15.0, spacer=2.0)       # 5 kg bar cell (generic 75 x 12.7 x 12.7)
CLEVIS = dict(x0=-22.0, x1=-12.0, tine=6.0, top=-10.0)             # cell clevis, local to the pin
CELL_TOP = Z_SHAFT + CLEVIS["top"]                                  # 210: the cell's free end tops out here
X_CELL_N = X_HOOK + CLEVIS["x0"]                                    # cell's north face, -192
X_CELL_MAST = X_CELL_N - CELL["w"] - CELL["spacer"] - 15.0         # -221.7
CELL_SLOT = (CELL_TOP - 80.0 + CELL["end"], CELL_TOP - 55.0 + CELL["end"] + CELL["pitch"])   # fits 55-80 mm cells
X_CAL = BOARD["x1"] - 45.0                 # calibration pulley mast at the board's north edge
PULLEY = dict(x=50.0, r_groove=14.0, r_out=17.1, w=7.0, bore=22.05)  # on a 608ZZ (8 x 22 x 7)
Z_PULLEY = Z_SHAFT - PULLEY["r_groove"]    # axle, so the string leaves the groove's top on the thrust line
GUY_X = -420.0


# ------------------------------------------------------------------ primitives (v0's helpers)
def cyl_z(r, z0, z1, x=0.0, y=0.0):
    return Pos(x, y, (z0 + z1) / 2) * Cylinder(r, abs(z1 - z0))


def cyl_x(r, x0, x1, y=0.0, z=0.0):
    return Pos((x0 + x1) / 2, y, z) * Rot(0, 90, 0) * Cylinder(r, abs(x1 - x0))


def cyl_y(r, y0, y1, x=0.0, z=0.0):
    return Pos(x, (y0 + y1) / 2, z) * Rot(90, 0, 0) * Cylinder(r, abs(y1 - y0))


def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def capsule_x(y0, z0, y1, z1, r, x0, x1):
    """Slot along the plate's face (y-z) from (y0, z0) to (y1, z1), width 2r, through x0..x1."""
    ang = math.degrees(math.atan2(z1 - z0, y1 - y0))
    length = math.hypot(y1 - y0, z1 - z0)
    s = cyl_x(r, x0, x1, y=y0, z=z0) + cyl_x(r, x0, x1, y=y1, z=z1)
    if length > 1e-6:
        s += Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Rot(ang, 0, 0) * Box(abs(x1 - x0), length, 2 * r)
    return s


def gusset(x0, x1, z0, z1, y0, y1):
    """Triangular rib in the x-z plane: vertical edge at x1 up to z1, foot from x0 to x1 at z0."""
    tri = Plane.XZ * Polygon((x1, z0), (x0, z0), (x1, z1), align=None)
    return Pos(0, y1, 0) * extrude(tri, amount=y1 - y0)


# ------------------------------------------------------------------ printed parts
def post_foot():
    """Bolts to the board; the post passes through and stands on the board (v0 part, unchanged)."""
    p = box(-50, 50, -50, 50, 0, 8)
    p += box(-35, 35, -35, 35, 8, 50)
    p -= cyl_z(BORE_POST / 2, -1, 51)
    p -= cyl_y(D_M5 / 2, -36, 36, z=29)                       # cross-bolt through boss and post
    for sx in (-42, 42):
        for sy in (-42, 42):
            p -= cyl_z(D_BOARD / 2 + 0.75, -1, 9, sx, sy)     # board screws, clear of the boss
    return p


def pivot_head():
    """Caps the post and carries the pivot axle over the arm: an inverted U (two cheeks and a
    bridge) beside a socket for the post. The hub swings between the cheeks; the bridge, 2 mm above
    the hub, stops the swing at ~4 deg. Prints upside down (top face on the bed), no supports.
    Local origin: the axle centre."""
    yo = CHEEK_IN + CHEEK_T
    p = box(-HEAD_X, HEAD_X, -yo, yo, BRIDGE_Z0, HEAD_Z1)                    # bridge
    p += box(-HEAD_X, HEAD_X, CHEEK_IN, yo, HEAD_Z0, HEAD_Z1)                # far cheek
    p += box(-HEAD_X, HEAD_X, -yo, -CHEEK_IN, HEAD_Z0, HEAD_Z1)              # near cheek
    p += box(-25, 25, POST_Y - 25, -yo + 0.5, HEAD_Z0, HEAD_Z1)              # post boss
    p -= cyl_z(BORE_POST / 2, HEAD_Z0 - 1, POST_TOP - Z_PIVOT, y=POST_Y)     # post socket, blind
    p -= cyl_x(D_M5 / 2, -26, 26, y=POST_Y, z=0)                             # cross-bolt through boss and post
    p -= cyl_y(BORE_PIVOT / 2, AXLE_Y[0] - 3, yo + 1)                        # pivot bores, blind in the boss
    return p


def arm_hub():
    """Between the cheeks; grips the axle (cross-bolted, the axle turns in the cheeks) and the arm.
    Local origin: hub bottom centre; axle 48 mm up (v0 part, unchanged)."""
    p = box(-HUB["x"], HUB["x"], -HUB["y"], HUB["y"], 0, HUB["h"])
    p -= cyl_y(BORE_PIVOT / 2, -HUB["y"] - 1, HUB["y"] + 1, z=HUB["axle"])
    p -= cyl_z(BORE_POST / 2, -1, HUB["arm_depth"])
    r0, r1 = BORE_POST / 2, 4.0                                # 45 deg roof: prints without a 26 mm bridge
    p -= Pos(0, 0, HUB["arm_depth"] + (r0 - r1) / 2 - 0.01) * Cone(r0, r1, r0 - r1)
    p -= cyl_x(D_M5 / 2, -31, 31, z=HUB["axle"])
    p -= cyl_x(D_M5 / 2, -31, 31, z=15)
    return p


def motor_clamp():
    """Clamps the arm's lower end. Motor plate on the +x face (two M4, nuts in side slots behind a
    6 mm wall); the cross-bolt runs along y, clear of the motor; the link pins into the fork on the
    -x face exactly on the thrust line. Local origin: the clamp centre = motor shaft height."""
    p = box(-CLAMP["x"], CLAMP["x"], -CLAMP["y"], CLAMP["y"], -CLAMP["z"], CLAMP["z"])
    p -= cyl_z(BORE_POST / 2, -31, 31)
    p -= cyl_y(D_M5 / 2, -26, 26)                              # cross-bolt through clamp and arm
    for sz in (-PLATE_BOLT_Z, PLATE_BOLT_Z):
        p -= cyl_x(D_M4 / 2, NUT_X[0] - 6.0, CLAMP["x"] + 1, z=sz)          # bolt + relief behind the nut
        p -= box(NUT_X[0], NUT_X[1], -SLOT_END, CLAMP["y"] + 1, sz - SLOT_W / 2, sz + SLOT_W / 2)
    g = FORK_GAP / 2
    for s in (-1, 1):
        y0, y1 = sorted((s * g, s * (g + FORK_T)))
        p += box(FORK_X[0], FORK_X[1] + 0.5, y0, y1, -CLAMP["z"], CLAMP["z"])  # full height: no overhang
    p -= cyl_y(D_M3 / 2, -g - FORK_T - 1, g + FORK_T + 1, x=PIN_X)
    return p


MOTOR_SLOTS = [(a, 8.0, 9.5) for a in (0, 90, 180, 270)] + [(a, 11.31, 13.44) for a in (45, 135, 225, 315)]


def motor_plate():
    """One plate for both motors: four slots on the cross (16 and 19 mm, 22xx) and four on the
    diagonals (16x16 and 19x19 squares; the Emax ECOII 2807 is 19x19). M3 heads sit in 4 mm
    counterbores on the back, so the plate seats flat on the clamp. Local: back face x = 0."""
    p = box(0, PLATE_T, -28, 28, -30, 30)
    p -= cyl_x(5.0, -1, PLATE_T + 1)                           # shaft end and circlip
    for sz in (-PLATE_BOLT_Z, PLATE_BOLT_Z):
        p -= cyl_x(D_M4 / 2, -1, PLATE_T + 1, z=sz)
    for a, r0, r1 in MOTOR_SLOTS:
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        p -= capsule_x(r0 * c, r0 * s, r1 * c, r1 * s, 3.4 / 2, -1, PLATE_T + 1)
        p -= capsule_x(r0 * c, r0 * s, r1 * c, r1 * s, 6.5 / 2, -1, 4.0)
    return p


def _mast_base(top, ribs):
    p = box(-60, 45, -45, 45, 0, 8)                            # foot
    for sy in (-35, 35):                                       # 50 mm slots along x: tension the line
        p -= box(-25, 25, sy - 3.5, sy + 3.5, -1, 9)
        p -= cyl_z(3.5, -1, 9, x=-25, y=sy)
        p -= cyl_z(3.5, -1, 9, x=25, y=sy)
    p += box(-15, 15, -15, 15, 8, top)                         # post 30 x 30
    for y0, y1 in ribs:
        p += gusset(-60, -14, 8, 140, y0, y1)
    return p


def cal_mast():
    """Calibration pulley's mast. The flange flares out at 45 deg (prints without support); its M4
    nuts slide in from the +y side and sit 3.2 mm under the top. Local origin: on the board, at the
    mast centre."""
    p = _mast_base(181, [(-3, 3)])
    p += loft([Plane.XY.offset(179) * Rectangle(30, 30), Plane.XY.offset(194) * Rectangle(60, 60)])
    p += box(-30, 30, -30, 30, 194, MAST_FLANGE)
    for sx in (-20, 20):
        p -= cyl_z(D_M4 / 2, 184, MAST_FLANGE + 1, x=sx)
        p -= box(sx - SLOT_W / 2, sx + SLOT_W / 2, -SLOT_END, 31, MAST_FLANGE - 3.2 - SLOT_T, MAST_FLANGE - 3.2)
    return p


def crank():
    """Scale option: a bell crank with equal arms turns the link's pull into a press on the anvil
    on the scale, 1:1. Its top tab takes the link at shaft height; its nose (a 5 mm cylinder) rests
    on the anvil level with the pivot, so the nose rolls instead of sliding. Two 608 bearings press
    flush into a straight bore, 2 mm apart, the crank_spacer's length. (The first print had a 2 mm
    shoulder between them: over the bed-side seat its hole's walls printed in mid-air, as strands.)
    Prints flat. Local origin: the pivot axis; arms up (+z) and north (+x)."""
    r, t, c = CRANK["r"], CRANK["t"] / 2, CRANK["clear"]
    wv, hh = CRANK["w_v"] / 2, CRANK["h_h"]
    p = cyl_y(CRANK["hub"], -t, t)
    p += box(-wv, wv, -t, t, 0, r - 14)                        # vertical arm
    p += box(-9, 9, -t, -2.5, r - 16, r)                       # tab, beside the link (single shear)
    p += cyl_y(9, -t, -2.5, z=r)
    p += box(0, r, -t, t, c, c + hh)                           # horizontal arm, clear of the anvil
    p += box(r - 5, r + 5, -t, t, CRANK["nose"], c + 1)
    p += cyl_y(CRANK["nose"], -t, t, x=r, z=CRANK["nose"])    # lowest point at the pivot's height
    p += gusset(wv + 70, wv - 0.5, c + hh - 0.5, c + hh + 70, -t, t)
    p -= cyl_y(D_M3 / 2, -t - 1, t, z=r)
    p -= cyl_y(BEARING_SEAT / 2, -t - 1, t + 1)
    return p


def crank_spacer():
    """Between the two bearings' inner races, so the axle clamps only the inner races."""
    return cyl_y(5.75, -1, 1) - cyl_y(D_M8 / 2, -2, 2)


def crank_base():
    """Holds the crank's M8 axle at the nose's height; the bosses touch only the bearings' inner
    races. Slots along x set the crank so the arm hangs plumb. Local origin: on the board,
    under the pivot."""
    t = CRANK["t"] / 2
    p = box(-45, 45, -40, 40, 0, 8)
    for sy in (-30, 30):                                       # 40 mm slots for wood screws
        p -= box(-20, 20, sy - 3, sy + 3, -1, 9)
        p -= cyl_z(3, -1, 9, x=-20, y=sy)
        p -= cyl_z(3, -1, 9, x=20, y=sy)
    for s in (-1, 1):
        y0, y1 = sorted((s * (t + 1), s * (t + 9)))
        p += box(-18, 18, y0, y1, 8, Z_NOSE + 14)
        p += cyl_y(6, *sorted((s * t, s * (t + 1.2))), z=Z_NOSE)
    p -= cyl_y(D_M8 / 2, -t - 10, t + 10, z=Z_NOSE)
    return p


def scale_anvil():
    """Stands on the centre of the scale's platform and lifts the contact to the crank's pivot
    height, so a thin scale works with the same crank. It just sits there: the nose only presses
    down on it. Local origin: its base centre, on the platform."""
    (bx, by), (tx, ty) = ANVIL["base"], ANVIL["top"]
    return loft([Plane.XY * Rectangle(bx, by), Plane.XY.offset(ANVIL["h"]) * Rectangle(tx, ty)])


def scale_corner():
    """Corner stop screwed to the board: push the scale into the two stops and its platform centre
    is back under the crank's nose. Local: the scale occupies x >= 0, y >= 0."""
    p = box(-10, 40, -10, 0, 0, 12) + box(-10, 0, -10, 40, 0, 12)
    for x, y in ((22, -5), (-5, 22)):
        p -= cyl_z(D_BOARD / 2 + 0.25, -1, 13, x=x, y=y)
    return p


def _link(length):
    """Link on edge (5 thick in y, 12 tall), pinned at both ends on axes parallel to the pivot."""
    t, h = LINK["t"] / 2, LINK["h"] / 2
    p = box(-length / 2, length / 2, -t, t, -h, h)
    for x in (-length / 2, length / 2):
        p += cyl_y(h, -t, t, x=x)
        p -= cyl_y(D_M3 / 2, -t - 1, t + 1, x=x)
    return p


def crank_link():
    """Arm fork to the crank's tab, on the thrust line. Prints diagonally on the bed."""
    return _link(PIN_X - X_CRANK)


def cell_link():
    """Arm fork to the load cell's clevis, on the thrust line."""
    return _link(PIN_X - X_HOOK)


def cell_mast():
    """Load-cell option: the bar cell stands on the mast's north face, its fixed end held by two
    screws through the slot (cells 55-80 mm long fit), 2 mm off the face on washers. Side ribs
    leave the screw heads and the hex key clear. Local origin: on the board, at the mast centre."""
    p = _mast_base(CELL_SLOT[1] + 8.0, [(-15, -9), (9, 15)])
    p -= capsule_x(0, CELL_SLOT[0], 0, CELL_SLOT[1], D_M5 / 2, -16, 16)
    return p


def cell_clevis():
    """Bolts to the cell's free end (two M5 into its tapped holes, heads in counterbores) and
    carries a fork whose pin sits on the thrust line, 10 mm above the cell's top. Local origin:
    the pin."""
    x0, x1, top = CLEVIS["x0"], CLEVIS["x1"], CLEVIS["top"]
    holes = (top - CELL["end"], top - CELL["end"] - CELL["pitch"])
    p = box(x0, x1, -10, 10, holes[1] - 8.0, 9.0)
    for z in holes:
        p -= cyl_x(D_M5 / 2, x0 - 1, x1 + 1, z=z)
        p -= cyl_x(9.5 / 2, x1 - 6.0, x1 + 1, z=z)
    g = FORK_GAP / 2
    for s in (-1, 1):
        y0, y1 = sorted((s * g, s * (g + FORK_T)))
        p += box(x1 - 0.5, CLEVIS["tine"], y0, y1, -9, 9)
    p -= cyl_y(D_M3 / 2, -g - FORK_T - 1, g + FORK_T + 1)
    return p


def cal_pulley_bracket():
    """Calibration: bolts onto cal_mast's flange at the board's north edge and holds a 608
    bearing pulley whose groove top is on the thrust line. Local origin: flange top centre."""
    p = box(-30, 30, -30, 30, 0, 6)
    for sx in (-20, 20):
        p -= cyl_z(D_M4 / 2, -1, 7, x=sx)
    p += box(24, 33, 5.5, 11.5, 0, 6)                          # joins the cheek to the base
    p += box(30.5, 66, 5.5, 11.5, -26, 6)                      # cheek, clear of the flange (x <= 30)
    zc = Z_PULLEY - MAST_FLANGE
    p += cyl_y(5.5, 3.5, 6.0, x=PULLEY["x"], z=zc)             # boss on the bearing's inner race
    p -= cyl_y(D_M8 / 2, 2.0, 13.0, x=PULLEY["x"], z=zc)
    return p & box(-40, 80, -40, 40, -40, 6)                   # flat top: it prints on it


def cal_wheel():
    """Grooved tyre pressed onto the 608 bearing's outer race (a drop of CA if loose)."""
    w = PULLEY["w"] / 2
    p = cyl_y(PULLEY["r_out"], -w, w)
    groove = Plane.XY * Polygon((PULLEY["r_out"] + 0.2, -3.2), (PULLEY["r_groove"], 0.0),
                                (PULLEY["r_out"] + 0.2, 3.2), align=None)
    p -= revolve(groove, Axis.Y)
    p -= cyl_y(PULLEY["bore"] / 2, -w - 1, w + 1)
    return p


def guy_anchor():
    """Optional: anchors a tensioned cord from just under the pivot head, for a stiffer post
    (v0 part, unchanged). Not needed for accuracy: the post carries ~1 % of the thrust."""
    p = box(-30, 30, -30, 30, 0, 8)
    for sx in (-20, 20):
        p -= cyl_z(D_BOARD / 2 + 0.75, -1, 9, x=sx)
    p += box(24, 30, -15, 15, 6, 48)
    p -= cyl_x(10.0 / 2, 23, 31, z=35)
    return p


# Print orientation: rotation(s) applied to the part (its local frame) to lay it on the bed.
FLAT_X_DOWN = ("y", 90)      # +x face down
FLAT_MX_DOWN = ("y", -90)    # -x face down
UPSIDE_DOWN = ("x", 180)
ON_EDGE_Y = ("x", 90)        # y thickness becomes z
X_CORNER = X_PAN - BENCH["W"] / 2 - 1.0     # scale corner stops, 1 mm off the scale's south edge
# "at": where each copy goes, (x, y, z) or (x, y, z, turn about z in degrees).
PARTS = {
    "post_foot": dict(fn=post_foot, at=[(0, POST_Y, 0)], option="core", print=None,
                      role="post foot: the post stands on the board through it"),
    "pivot_head": dict(fn=pivot_head, at=[(0, 0, Z_PIVOT)], option="core", print=UPSIDE_DOWN,
                       role="pivot head: caps the post, carries the axle over the arm, stops the swing at ~4 deg"),
    "arm_hub": dict(fn=arm_hub, at=[(0, 0, HUB_Z0)], option="core", print=None,
                    role="arm hub: pinned to the axle and the arm, swings between the cheeks"),
    "motor_clamp": dict(fn=motor_clamp, at=[(0, 0, Z_SHAFT)], option="core", print=None,
                        role="motor clamp: arm end, motor plate on the front, link fork on the back"),
    "motor_plate": dict(fn=motor_plate, at=[(CLAMP["x"], 0, Z_SHAFT)], option="core", print=FLAT_X_DOWN,
                        role="motor plate: 19x19 and 16/19-cross patterns, M3 heads recessed"),
    "crank_link": dict(fn=crank_link, at=[((PIN_X + X_CRANK) / 2, 0, Z_SHAFT)], option="bench",
                       print=[ON_EDGE_Y, ("z", 45)], role="link: arm fork to the crank, on the thrust line"),
    "crank": dict(fn=crank, at=[(X_CRANK, 0, Z_NOSE)], option="bench", print=ON_EDGE_Y,
                  role="bell crank, equal arms: the link's pull presses the anvil on the scale 1:1"),
    "crank_spacer": dict(fn=crank_spacer, at=[(X_CRANK, 0, Z_NOSE)], option="bench", print=ON_EDGE_Y,
                         role="spacer between the crank bearings' inner races"),
    "crank_base": dict(fn=crank_base, at=[(X_CRANK, 0, 0)], option="bench", print=None,
                       role="crank base: holds the crank's axle at the nose's height; slots set the arm plumb"),
    "scale_anvil": dict(fn=scale_anvil, at=[(X_PAN, 0, BENCH["H"])], option="bench", print=None,
                        role="anvil on the platform's centre: lifts the contact to the crank's pivot height"),
    "scale_corner": dict(fn=scale_corner, at=[(X_CORNER, SCALE_Y[0] - 1.0, 0), (X_CORNER, SCALE_Y[1] + 1.0, 0, -90)],
                         option="bench", print=None,
                         role="corner stop: the scale goes back to the same place after weighing parts"),
    "cell_link": dict(fn=cell_link, at=[((PIN_X + X_HOOK) / 2, 0, Z_SHAFT)], option="cell", print=ON_EDGE_Y,
                      role="link: arm fork to the load-cell clevis, on the thrust line"),
    "cell_mast": dict(fn=cell_mast, at=[(X_CELL_MAST, 0, 0)], option="cell", print=None,
                      role="load-cell mast: the bar cell's fixed end on its north face"),
    "cell_clevis": dict(fn=cell_clevis, at=[(X_HOOK, 0, Z_SHAFT)], option="cell", print=FLAT_MX_DOWN,
                        role="load-cell clevis: on the cell's free end, pin on the thrust line"),
    "cal_mast": dict(fn=cal_mast, at=[(X_CAL, 0, 0)], option="cal", print=None,
                     role="calibration mast at the north edge (remove before running)"),
    "cal_pulley_bracket": dict(fn=cal_pulley_bracket, at=[(X_CAL, 0, MAST_FLANGE)], option="cal", print=UPSIDE_DOWN,
                               role="calibration pulley bracket: 608 bearing, groove top on the thrust line"),
    "cal_wheel": dict(fn=cal_wheel, at=[(X_CAL + PULLEY["x"], 0, Z_PULLEY)], option="cal", print=ON_EDGE_Y,
                      role="calibration pulley tyre on the 608 bearing"),
    "guy_anchor": dict(fn=guy_anchor, at=[(GUY_X, POST_Y, 0)], option="guy", print=None,
                       role="optional guy-cord anchor (stiffer post; not needed for accuracy)"),
}
FILES = [n for n, s in PARTS.items() if "file" not in s]       # one STL per distinct part


# ------------------------------------------------------------------ tubes, hardware, bought parts
def tubes():
    return [dict(name="post", a=[0, POST_Y, 0], b=[0, POST_Y, POST_TOP], od=POST_OD, option="core",
                 role=f"post: 25.4 mm tube, cut {POST_TOP:.0f} mm"),
            dict(name="arm", a=[0, 0, ARM_BOT], b=[0, 0, ARM_TOP], od=POST_OD, option="core",
                 role=f"pendulum arm: 25.4 mm tube, cut {ARM_TOP - ARM_BOT:.0f} mm"),
            dict(name="axle", a=[0, AXLE_Y[0], Z_PIVOT], b=[0, AXLE_Y[1], Z_PIVOT], od=THIN_OD, option="core",
                 role=f"pivot axle: 14.66 mm tube, cut {AXLE_Y[1] - AXLE_Y[0]:.0f} mm")]


def _bolt(name, size, length, p0, u, stack, nut=True, into=None, option="core", role="", washers=(0.0, 0.0),
          csk=False):
    """A bolt or screw. p0: where the head bears (on its washer, if any; for a countersunk head, the
    surface it sits flush with); u: unit vector into the work; stack: thickness of material clamped
    (mm); nut: through-bolt with a nut after a washer; into: tapped hole it threads into instead
    (engagement = length - washer - stack)."""
    return dict(name=name, size=size, d=float(size[1:]), length=length, p0=[float(c) for c in p0],
                u=[float(c) for c in u], stack=stack, nut=nut, into=into, option=option, role=role,
                washers=list(washers), head=CSK_M4 if csk else HEAD[size], csk=csk, nut_dims=NUT[size])


def hardware():
    b = []
    yo = POST_Y - 35.0
    b.append(_bolt("foot_bolt", "M5", 80, (0, yo - 1, 29), (0, 1, 0), 70.0, washers=(1, 1),
                   role="M5x80 through post_foot and the post"))
    b.append(_bolt("head_post_bolt", "M5", 60, (-26, POST_Y, Z_PIVOT), (1, 0, 0), 50.0, washers=(1, 1),
                   role="M5x60 through pivot_head and the post"))
    b.append(_bolt("hub_axle_bolt", "M5", 70, (-31, 0, Z_PIVOT), (1, 0, 0), 60.0, washers=(1, 1),
                   role="M5x70 through arm_hub and the axle"))
    b.append(_bolt("hub_arm_bolt", "M5", 70, (-31, 0, HUB_Z0 + 15), (1, 0, 0), 60.0, washers=(1, 1),
                   role="M5x70 through arm_hub and the arm"))
    b.append(_bolt("clamp_bolt", "M5", 60, (0, -26, Z_SHAFT), (0, 1, 0), 50.0, washers=(1, 1),
                   role="M5x60 through motor_clamp and the arm (sideways, clear of the motor)"))
    for s, tag in ((1, "upper"), (-1, "lower")):
        b.append(_bolt(f"plate_bolt_{tag}", "M4", 20, (X_PLATE_FRONT, 0, Z_SHAFT + s * PLATE_BOLT_Z), (-1, 0, 0),
                       PLATE_T + CLAMP["x"] - NUT_X[1], role="M4x20 motor plate to clamp, nut in its side slot"))
    q = 9.5
    for i, (sy, sz) in enumerate(((q, q), (-q, q), (-q, -q), (q, -q))):
        b.append(_bolt(f"motor_screw_{i + 1}", "M3", 8, (CLAMP["x"] + 4.0, sy, Z_SHAFT + sz), (1, 0, 0), 4.0,
                       nut=False, into="motor", role="M3x8 motor screw (19x19), head in its counterbore"))
    gy = FORK_GAP / 2 + FORK_T
    b.append(_bolt("link_pin", "M3", 20, (PIN_X, -gy - 0.5, Z_SHAFT), (0, 1, 0), 2 * gy, washers=(0.5, 0.5),
                   role="M3x20 + nyloc: link pin in the clamp fork"))
    t = CRANK["t"] / 2
    b.append(_bolt("crank_pin", "M3", 20, (X_CRANK, -t - 0.5, Z_SHAFT), (0, 1, 0), t - 2.5 + LINK["t"],
                   washers=(0.5, 0.5), option="bench", role="M3x20 + nyloc: link pin beside the crank's tab"))
    b.append(_bolt("crank_axle", "M8", 45, (X_CRANK, -t - 9 - 1.6, Z_NOSE), (0, 1, 0), 2 * (t + 9),
                   washers=(1.6, 1.6), option="bench",
                   role="M8x45 + nut: crank axle; clamps the bearings' inner races and the spacer"))
    zc = [CELL_TOP - CELL["L"] + CELL["end"], CELL_TOP - CELL["L"] + CELL["end"] + CELL["pitch"]]
    for i, z in enumerate(zc):
        b.append(_bolt(f"cell_fixed_screw_{i + 1}", "M5", 40, (X_CELL_MAST - 15 - 1, 0, z), (1, 0, 0),
                       30.0 + CELL["spacer"], nut=False, into="load_cell", option="cell", washers=(1, 0),
                       role="M5x40 through cell_mast into the cell's fixed end (2 mm of washers as spacer)"))
    for i, z in enumerate((CELL_TOP - CELL["end"], CELL_TOP - CELL["end"] - CELL["pitch"])):
        b.append(_bolt(f"clevis_screw_{i + 1}", "M5", 12, (X_HOOK + CLEVIS["x1"] - 6.0, 0, z), (-1, 0, 0),
                       4.0, nut=False, into="load_cell", option="cell",
                       role="M5x12 cell_clevis into the cell's free end, head in its counterbore"))
    b.append(_bolt("clevis_pin", "M3", 20, (X_HOOK, -gy - 0.5, Z_SHAFT), (0, 1, 0), 2 * gy, washers=(0.5, 0.5),
                   option="cell", role="M3x20 + nyloc: cell_link pin in the clevis"))
    for sx in (-20, 20):
        b.append(_bolt(f"cal_bracket_bolt_{'s' if sx < 0 else 'n'}", "M4", 16, (X_CAL + sx, 0, MAST_FLANGE + 6),
                       (0, 0, -1), 6.0 + 3.2, option="cal", role="M4x16 pulley bracket to mast flange"))
    b.append(_bolt("cal_axle", "M8", 30, (X_CAL + PULLEY["x"], 11.5 + 1, Z_PULLEY), (0, -1, 0), 6.0 + 2.5 + 7.0,
                   washers=(1, 1), option="cal", role="M8x30 + nut: pulley axle through the 608 bearing"))
    return b


def screws_into_board():
    """Wood screws (#10 x 1 in / 4.5-5 x 25 mm) holding each foot down: positions for the viewer."""
    out = []
    for sx in (-42, 42):
        for sy in (-42, 42):
            out.append(dict(at=[sx, POST_Y + sy, 8.0], option="core", part="post_foot"))
    for x0, opt, part in ((X_CELL_MAST, "cell", "cell_mast"), (X_CAL, "cal", "cal_mast")):
        for sy in (-35, 35):
            out.append(dict(at=[x0, sy, 8.0], option=opt, part=part))
    for sy in (-30, 30):
        out.append(dict(at=[X_CRANK, sy, 8.0], option="bench", part="crank_base"))
    for k, c in enumerate(PARTS["scale_corner"]["at"]):
        R = G.rot("z", c[3] if len(c) > 3 else 0.0)
        for p in ((22, -5, 12.0), (-5, 22, 12.0)):
            out.append(dict(at=[float(v) for v in R @ np.array(p) + np.array(c[:3], float)], option="bench",
                            part=f"scale_corner_{k + 1}"))
    for sx in (-20, 20):
        out.append(dict(at=[GUY_X + sx, POST_Y, 8.0], option="guy", part="guy_anchor"))
    return out


def bought():
    """Purchased items as simple envelopes (for the viewer and the clash check)."""
    xm = X_PLATE_FRONT
    e = [dict(name="motor", kind="motor", base=[xm, 0, Z_SHAFT], option="core",
              label="Emax ECOII 2807 1700KV", stator=[14.0, 6.0], bell=[17.0, 24.0], shaft=2.5, prop_at=37.0),
         dict(name="esc", kind="box", size=[8, 22, 45], pos=[-12.7 - 4.2, 0, 422.5], color="#7a3fb0", option="core",
              label="ESC 50 A (zip-tied to the arm, out of the wash)"),
         dict(name="battery", kind="box", size=[155, 48, 37], pos=[-395, 125, 18.5], color="#e8b923", option="core",
              label="4S 5000 mAh LiPo (on the board, never on the arm)"),
         dict(name="wattmeter", kind="box", size=[75, 40, 22], pos=[-265, 135, 11], color="#3a7d44", option="core",
              label="wattmeter (V, A, W)"),
         dict(name="servo_tester", kind="box", size=[50, 30, 15], pos=[-160, 150, 7.5], color="#2f2f2f", option="core",
              label="servo tester (throttle)"),
         dict(name="bench_scale", kind="box", size=[BENCH["W"], BENCH["L"], BENCH["H"] - 1.0],
              pos=[X_PAN, sum(SCALE_Y) / 2, (BENCH["H"] - 1.0) / 2], color="#2b2f36", option="bench",
              label="pocket scale 3000 g x 0.1 g (display at the east end)"),
         dict(name="scale_pan", kind="box", size=[BENCH["steel_w"], BENCH["steel_l"], 1.0],
              pos=[X_PAN, 0, BENCH["H"] - 0.5], color="#c9ced6",
              option="bench", label="the scale's stainless platform: the anvil stands on its centre"),
         dict(name="crank_bearing_1", kind="cyl", r=11.0, h=7.0, pos=[X_CRANK, -4.5, Z_NOSE], axis=[0, 1, 0],
              color="#9aa3ad", option="bench", label="608ZZ bearing (2 in the crank)"),
         dict(name="crank_bearing_2", kind="cyl", r=11.0, h=7.0, pos=[X_CRANK, 4.5, Z_NOSE], axis=[0, 1, 0],
              color="#9aa3ad", option="bench", label="608ZZ bearing (2 in the crank)"),
         dict(name="load_cell", kind="box", size=[CELL["w"], CELL["w"], CELL["L"]],
              pos=[X_CELL_N - CELL["w"] / 2, 0, CELL_TOP - CELL["L"] / 2], color="#b8bec6", option="cell",
              label="5 kg bar load cell"),
         dict(name="hx711", kind="box", size=[34, 21, 4], pos=[-300, -95, 2], color="#1f7a3a", option="cell",
              label="HX711 amplifier"),
         dict(name="arduino", kind="box", size=[45, 18, 8], pos=[-300, -130, 4], color="#1c5fa8", option="cell",
              label="Arduino Nano (USB to laptop)"),
         dict(name="bearing_608", kind="cyl", r=11.0, h=7.0, pos=[X_CAL + PULLEY["x"], 0, Z_PULLEY], axis=[0, 1, 0],
              color="#9aa3ad", option="cal", label="608ZZ bearing"),
         ]
    return e


def lines():
    """Cords, strings and cables as polylines (viewer only)."""
    return [dict(name="cal_string", pts=[[X_PLATE_FRONT + 41, 0, Z_SHAFT], [X_CAL + PULLEY["x"], 0, Z_SHAFT],
                                         [X_CAL + PULLEY["x"] + PULLEY["r_groove"], 0, Z_PULLEY],
                                         [X_CAL + PULLEY["x"] + PULLEY["r_groove"], 0, -150]],
                 d=1.2, color="#e67e22", option="cal", label="string from the prop nut over the pulley to the weights"),
            dict(name="guy_cord", pts=[[0, POST_Y - 12.7, Z_PIVOT - 30], [GUY_X + 27, POST_Y, 35]], d=2.5,
                 color="#566573", option="guy", label="guy cord (optional)"),
            dict(name="battery_lead", pts=[[-318, 125, 20], [-302, 135, 11]], d=5.0, color="#c0392b", option="core"),
            dict(name="esc_lead", pts=[[-228, 135, 11], [-120, 110, 40], [-40, 40, 300], [-14, 8, 400]], d=5.0,
                 color="#c0392b", option="core", label="slack loop: battery lead to the ESC on the arm"),
            dict(name="motor_leads", pts=[[-14, 8, 445], [-12, 14, 300], [10, 24, 240], [38, 18, 226]], d=3.5,
                 color="#2c3e50", option="core"),
            ]


# ------------------------------------------------------------------ export
def print_rotation(name):
    """Rotation that lays the part on the bed: print = R @ local (then centred, see main)."""
    rots = PARTS[name]["print"]
    R = np.eye(3)
    for r in ([] if rots is None else [rots] if isinstance(rots, tuple) else rots):
        R = G.rot(*r) @ R
    return R


def placement(at):
    """(Rz, t) of one copy: assembly = Rz @ local + t."""
    return G.rot("z", at[3] if len(at) > 3 else 0.0), np.asarray(at[:3], float)


def build(names=None, verbose=True):
    """Build every part (local frame). Returns {name: Part}."""
    out = {}
    for name in names or PARTS:
        part = PARTS[name]["fn"]()
        if not part.is_valid:
            raise RuntimeError(f"{name}: invalid solid")
        out[name] = part
        if verbose:
            bb = part.bounding_box()
            print(f"{name:20s} vol={part.volume / 1000:8.1f} cm3  bbox=({bb.max.X - bb.min.X:.1f} x "
                  f"{bb.max.Y - bb.min.Y:.1f} x {bb.max.Z - bb.min.Z:.1f}) mm")
    return out


def main():
    parts = build()
    os.makedirs(G.STL, exist_ok=True)
    for old in os.listdir(G.STL):                              # parts that no longer exist leave no STL
        if old.endswith(".stl") and old[:-4] not in FILES:
            os.remove(os.path.join(G.STL, old))
    placements = []
    for name, part in parts.items():
        spec = PARTS[name]
        R = print_rotation(name)
        tmp = os.path.join(G.STL, f"_{name}_local.stl")
        export_stl(part, tmp, tolerance=0.02, angular_tolerance=0.15)
        tris = G.apply(G.read_stl(tmp), R)
        os.remove(tmp)
        lo, hi = tris.reshape(-1, 3).min(0), tris.reshape(-1, 3).max(0)
        c = np.array([-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]])
        G.write_stl(os.path.join(G.STL, f"{name}.stl"), G.apply(tris, None, c))
        # assembly = Rz R^-1 (print - c) + t
        Ri = R.T
        for k, at in enumerate(spec["at"]):
            Rz, t = placement(at)
            M = G.mat4(Rz @ Ri, t - Rz @ Ri @ c)
            placements.append(dict(name=name if len(spec["at"]) == 1 else f"{name}_{k + 1}", part=name, file=name,
                                   option=spec["option"], role=spec["role"], at=list(map(float, at)),
                                   matrix=[round(float(v), 6) for v in M.T.reshape(-1)]))  # column-major (three.js)
    info = dict(parts={n: dict(file=n, option=PARTS[n]["option"], role=PARTS[n]["role"], qty=max(1, len(PARTS[n]["at"])),
                               volume=round(parts[n].volume / 1000, 2)) for n in parts},
                placements=placements, tubes=tubes(), hardware=hardware(), board_screws=screws_into_board(),
                bought=bought(), lines=lines(), board=BOARD,
                layout=dict(z_shaft=Z_SHAFT, z_pivot=Z_PIVOT, post_y=POST_Y, pin_x=PIN_X, x_hook=X_HOOK,
                            x_plate_front=X_PLATE_FRONT, hub_z0=HUB_Z0, z_pulley=Z_PULLEY, x_cal=X_CAL,
                            x_crank=X_CRANK, x_pan=X_PAN, z_nose=Z_NOSE, crank_r=CRANK["r"],
                            x_cell_mast=X_CELL_MAST, cell_top=CELL_TOP))
    with open(os.path.join(G.STL, "assembly.json"), "w", newline="\n") as f:
        json.dump(info, f, indent=1)
    print(f"wrote {len(FILES)} STLs (print orientation) and stl/assembly.json: {len(placements)} placed parts, "
          f"{len(info['hardware'])} bolts, {len(info['tubes'])} tubes")


if __name__ == "__main__":
    main()
