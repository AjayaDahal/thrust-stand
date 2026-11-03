#!/usr/bin/env python3
"""Audit of the v0 design (v0_archive/): rebuilds its parts from its own source, places them as
its render script did, adds the tubes, the motor and the bolts the README calls for, and measures
what collides or does not fit. Writes v0_archive/audit/audit_v0.json (the numbers REPORT.md quotes)
and one STL per clash (assembly coordinates) for the viewer's v0 mode.

Run: C:/Users/ajayad/venvs/vtol-venv/Scripts/python.exe scripts/audit_v0.py
"""
import importlib.util
import json
import math
import os
import sys

import numpy as np
from build123d import export_stl, Pos

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom as G  # noqa: E402

V0 = os.path.join(G.ROOT, "v0_archive")
OUT = os.path.join(V0, "audit")

spec = importlib.util.spec_from_file_location("v0", os.path.join(V0, "build_thrust_stand.py"))
v0 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v0)

# Where v0's render script (v0_archive/render_thrust_stand.py) put each part, in mm.
PLACE = {"post_foot": (0, 0, 0), "pivot_clevis": (0, 0, 635), "arm_hub": (0, 0, 652), "motor_clamp": (0, 0, 220),
         "motor_plate_2807": (32, 0, 220), "scale_mast": (-230, 30, 0), "scale_platform": (-230, 30, 204),
         "scale_link": (-107, 30, 222), "brace_clamp": (0, 0, 350), "brace_foot": (-350, 0, 0)}
FUNCS = dict(v0.PARTS)


def placed(name):
    return Pos(*PLACE[name]) * FUNCS[name]()


def main():
    os.makedirs(OUT, exist_ok=True)
    P = {n: placed(n) for n in PLACE}
    T = {"post_tube": v0.cyl_z(12.7, 0, 635), "arm_tube": v0.cyl_z(12.7, 182, 682),
         "axle": v0.cyl_y(7.33, -55, 55, z=700)}
    # The brace tube along the clamp's 45 deg socket axis, from the socket's bottom to the board.
    d = np.array([math.sqrt(0.5), 0, math.sqrt(0.5)])
    top = np.array([-50.0, 0, 350 - 25.0]) + 35 * d
    bot = top - d * (top[2] / d[2])
    T["brace_tube"] = Pos(*((top + bot) / 2)) * v0.Rot(0, 45, 0) * v0.Cylinder(7.33, float(np.linalg.norm(top - bot)))
    # 2807 motor on its plate (front face x = 34) and its four M3 screws at the motor's real 19x19 holes,
    # heads behind the plate as they must be; the clamp's M5 cross-bolt (70 mm, head on the -x face).
    motor = v0.cyl_x(14, 34, 40, z=220) + v0.cyl_x(17, 40, 64, z=220)
    screws = None
    for sy in (-9.5, 9.5):
        for sz in (-9.5, 9.5):
            s = v0.cyl_x(2.75, 27, 30, y=sy, z=220 + sz) + v0.cyl_x(1.5, 30, 38, y=sy, z=220 + sz)
            screws = s if screws is None else screws + s
    bolt = v0.cyl_x(2.5, -30, 40, z=220) + v0.cyl_x(4.0, 30, 34, z=220)      # shank + nut on the +x face

    clashes = []

    def clash(key, a, b, label):
        c = a & b
        vol = c.volume if c is not None else 0.0
        if vol > 1.0:
            path = os.path.join(OUT, f"clash_{key}.stl")
            export_stl(c, path, tolerance=0.05, angular_tolerance=0.2)
            clashes.append(dict(key=key, label=label, volume=round(vol), url=f"../v0_archive/audit/clash_{key}.stl"))
        print(f"{key:24s} {vol:10.0f} mm3  {label}")
        return vol

    clash("arm_post", T["arm_tube"], T["post_tube"],
          "arm and post are the same cylinder from z 182 to 635: the pendulum cannot hang")
    clash("arm_clevis", T["arm_tube"], P["pivot_clevis"], "arm runs into the pivot clevis's socket block")
    clash("bolt_motor", bolt, motor + P["motor_plate_2807"], "motor clamp's M5 cross-bolt and nut end in the motor")
    clash("screws_plate", screws, P["motor_plate_2807"], "2807 screws (19x19) miss the plate's 19 mm-circle holes")
    clash("heads_clamp", screws, P["motor_clamp"], "M3 screw heads have no room between the plate and the clamp")
    clash("brace_foot", T["brace_tube"], P["brace_foot"], "brace tube on the clamp socket's axis misses the foot's socket")

    # Functional findings that are not volume clashes.
    def bore_holds(part, tube_name):
        return P[part].bounding_box().min.Z < 635 and abs(PLACE[part][0]) < 1 and abs(PLACE[part][1]) < 1
    grips_post = [n for n in ("motor_clamp", "brace_clamp") if bore_holds(n, "post_tube")]
    z_pin = PLACE["scale_link"][2] + 2.0          # link 4 mm thick lying on the tab: its mid-plane
    L_T, L_F = 700 - 220, 700 - z_pin

    def ratio(e, pin_x=-42.0, hook_x=-172.0, z_p=z_pin):
        """Scale force / thrust for a hook e mm above the pin (moment balance about the pivot)."""
        dx, dz = hook_x - pin_x, e
        arm = abs((0 - pin_x) * dz - (700 - z_p) * dx) / math.hypot(dx, dz)
        return L_T / arm

    clevis_c = math.sqrt(30 ** 2 + 48 ** 2)
    swing = math.degrees(math.atan2(30, 48) - math.acos(50 / clevis_c))   # hub corner reaches the block 2 mm below
    # Post bending if it carried the full thrust (v0's claim) vs what the pendulum actually puts on it.
    E, Do, Di = 3000.0, 25.4, 22.4                 # PVC, ~1.5 mm wall (assumed)
    I = math.pi / 64 * (Do ** 4 - Di ** 4)
    T15 = 15.0                                      # N, ~1.5 kg of thrust
    flex_claim = T15 * 635 ** 3 / (3 * E * I)
    flex_real = (ratio(0) - 1) * T15 * 635 ** 3 / (3 * E * I)
    yaw = T15 * 0.030                               # N m: thrust on y = 0, link on y = +30
    a = 9.5 / math.sqrt(2)
    out = dict(
        clashes=clashes,
        grips_post=grips_post,
        pin_height=z_pin, ratio=round(ratio(0), 4), ratio_hook_minus10=round(ratio(-10), 4),
        ratio_hook_plus10=round(ratio(10), 4),
        plate_2807_hole_square=round(2 * a, 2), motor_2807_square=19.0,
        plate_2212_holes="rectangle 16 x 19 (+-8, +-9.5)", motor_2212_holes="cross: 16 on one axis, 19 on the other",
        hub_swing_deg=round(swing, 1),
        post_flex_claim_mm=round(flex_claim, 1), post_flex_pendulum_mm=round(flex_real, 2),
        yaw_couple_Nm=round(yaw, 3), brace_axis_offset_mm=round(25 / math.sqrt(2), 1),
        m6x35_left_mm=round(35 - (8 + 18 + 2 * 1.6 + 5.0), 1),
        flange_overhang_mm=15.0, tab_overhang_mm=18.0,
        thin_tube_needed_mm=110 + 495, nut_wall_mm=0.0,
    )
    with open(os.path.join(OUT, "audit_v0.json"), "w", newline="\n") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "clashes"}, indent=1))


if __name__ == "__main__":
    main()
