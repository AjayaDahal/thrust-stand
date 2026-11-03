#!/usr/bin/env python3
"""Write viewer/manifest.json for the three.js viewer (viewer/index.html).

Lists every printed part (its print-orientation STL, sliced mass and time, and where each copy
goes in the assembly as a 4x4 matrix), the tubes, every bolt, the bought parts, cords and cables,
the burst (exploded) offsets, the force geometry for the thrust slider, and the v0 design with
its clashes for the audit view (from v0_archive/ and scripts/audit_v0.py).

Run after build_thrust_stand.py (and slice_all.py, for masses): then
`python scripts/serve_viewer.py` and open http://127.0.0.1:28766/viewer/
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_thrust_stand as B  # noqa: E402
import geom as G  # noqa: E402
from slice_all import stats  # noqa: E402

# Burst view: every part moves out the way it goes together (mm).
BURST = {"post_foot": (0, -70, 0), "post": (0, -70, 90), "pivot_head": (0, -35, 230), "axle": (0, 150, 150),
         "arm_hub": (0, 0, 150), "arm": (0, 0, 75), "motor_clamp": (0, 0, 0), "motor_plate": (70, 0, 0),
         "motor": (150, 0, 0), "crank_link": (0, 0, 170), "crank": (0, 0, 70), "crank_spacer": (0, 0, 70),
         "crank_bearing_1": (0, -45, 70), "crank_bearing_2": (0, 45, 70), "crank_base": (0, 0, 0),
         "scale_pan": (0, 0, 0), "bench_scale": (0, 0, 0), "scale_anvil": (0, 0, 35), "scale_corner": (-40, 0, 0),
         "cell_link": (-80, 0, 0), "cell_mast": (-170, 0, 0), "load_cell": (-140, 0, 0), "cell_clevis": (-110, 0, 0),
         "cal_mast": (150, 0, 0), "cal_pulley_bracket": (150, 0, 70), "cal_wheel": (150, 60, 100),
         "bearing_608": (150, 40, 100), "guy_anchor": (-60, -60, 0), "esc": (-60, 0, 75)}
# Which part each bolt comes out with, and how far it backs out of its hole.
BOLT_PARENT = {"foot_bolt": "post_foot", "head_post_bolt": "pivot_head", "hub_axle_bolt": "arm_hub",
               "hub_arm_bolt": "arm_hub", "clamp_bolt": "motor_clamp", "plate_bolt": "motor_plate",
               "motor_screw": "motor_plate", "link_pin": "motor_clamp", "crank_pin": "crank",
               "crank_axle": "crank_base", "cell_fixed_screw": "cell_mast", "clevis_screw": "cell_clevis",
               "clevis_pin": "cell_clevis", "cal_bracket_bolt": "cal_pulley_bracket", "cal_axle": "cal_wheel"}
PENDULUM = ["arm_hub", "arm", "axle", "motor_clamp", "motor_plate", "motor", "esc", "hub_axle_bolt", "hub_arm_bolt",
            "clamp_bolt", "plate_bolt_upper", "plate_bolt_lower", "motor_screw_1", "motor_screw_2", "motor_screw_3",
            "motor_screw_4", "link_pin", "motor_leads"]
# One label per item worth naming in the labelled views.
LABELS = {"pivot_head": "pivot head", "arm_hub": "arm hub", "axle": "pivot axle (14.66 tube)",
          "post": "post (25.4 tube)", "arm": "pendulum arm (25.4 tube)", "motor_clamp": "motor clamp + link fork",
          "motor_plate": "motor plate", "motor": "motor", "crank_link": "link (on the thrust line)",
          "crank": "bell crank (1:1)", "crank_base": "crank base", "bench_scale": "0.1 g pocket scale",
          "scale_anvil": "anvil",
          "scale_corner_1": "corner stops", "cell_link": "link (on the thrust line)",
          "cell_mast": "load-cell mast", "load_cell": "5 kg bar load cell", "cell_clevis": "cell clevis",
          "battery": "4S LiPo", "wattmeter": "wattmeter", "esc": "ESC", "servo_tester": "servo tester",
          "hx711": "HX711", "arduino": "Arduino Nano", "cal_wheel": "608 pulley", "cal_mast": "calibration mast",
          "post_foot": "post foot", "guy_anchor": "guy anchor (optional)"}
V0_FILES = ["post_foot", "pivot_clevis", "arm_hub", "motor_clamp", "motor_plate_2807", "scale_mast",
            "scale_platform", "scale_link", "brace_clamp", "brace_foot"]


def bolt_parent(name):
    for k, v in BOLT_PARENT.items():
        if name.startswith(k):
            return v
    return None


def r3(v):
    return [round(float(c), 3) for c in v]


def main():
    with open(os.path.join(G.STL, "assembly.json")) as f:
        A = json.load(f)
    files = []
    for name in B.FILES:
        tris = G.read_stl(os.path.join(G.STL, name + ".stl"))
        size = tris.reshape(-1, 3).ptp(0) if hasattr(np.ndarray, "ptp") else np.ptp(tris.reshape(-1, 3), 0)
        grams, minutes, fresh = stats(name)
        spec = B.PARTS[name]
        files.append(dict(name=name, url=f"../stl/{name}.stl", option=spec["option"], role=spec["role"],
                          size=[round(float(s), 1) for s in size], grams=grams,
                          minutes=None if minutes is None else round(minutes, 1), sliced=fresh,
                          copies=max(1, len(spec["at"])), bed=250))
    places = []
    for p in A["placements"]:
        places.append(dict(p, burst=list(BURST.get(p["part"], BURST.get(p["name"], (0, 0, 0)))),
                           label=LABELS.get(p["name"])))
    tubes = [dict(t, burst=list(BURST.get(t["name"], (0, 0, 0))), label=LABELS.get(t["name"])) for t in A["tubes"]]
    bolts = []
    for b in A["hardware"]:
        par = bolt_parent(b["name"])
        base = np.array(BURST.get(par, (0, 0, 0)), float)
        u = np.array(b["u"], float)
        bolts.append(dict(b, parent=par, burst=r3(base - u * 45.0), nut_burst=r3(base + u * 35.0)))
    bought = [dict(e, burst=list(BURST.get(e["name"], (0, 0, 0))), label_short=LABELS.get(e["name"]))
              for e in A["bought"]]
    lines = [dict(l, burst=list(BURST.get("arm", (0, 0, 0))) if l["name"] == "motor_leads" else [0, 0, 0])
             for l in A["lines"]]
    L = A["layout"]
    # Swing stop: the hub's top corner (half-length x, height above the axle) meets the bridge.
    hx, ht = B.HUB["x"], B.HUB["h"] - B.HUB["axle"]
    stop = np.degrees(np.arcsin(B.BRIDGE_Z0 / np.hypot(hx, ht)) - np.arctan2(ht, hx))
    physics = dict(pivot=[0, 0, L["z_pivot"]], prop=[L["x_plate_front"] + 41.0, 0, L["z_shaft"]],
                   pin=[L["pin_x"], 0, L["z_shaft"]], hook=[L["x_hook"], 0, L["z_shaft"]],
                   crank=dict(axle=[L["x_crank"], 0, L["z_nose"]], pin=[L["x_crank"], 0, L["z_shaft"]],
                              nose=[L["x_pan"], 0, L["z_nose"]], r=L["crank_r"]),
                   ratio=1.0, lever=L["z_pivot"] - L["z_shaft"], stop_deg=round(float(stop), 2))
    # v0, as audited: its own STLs (local frames) where its render script put them, its tubes, its clashes.
    with open(os.path.join(G.ROOT, "v0_archive", "audit", "audit_v0.json")) as f:
        audit = json.load(f)
    place_v0 = {"post_foot": (0, 0, 0), "pivot_clevis": (0, 0, 635), "arm_hub": (0, 0, 652),
                "motor_clamp": (0, 0, 220), "motor_plate_2807": (32, 0, 220), "scale_mast": (-230, 30, 0),
                "scale_platform": (-230, 30, 204), "scale_link": (-107, 30, 222), "brace_clamp": (0, 0, 350),
                "brace_foot": (-350, 0, 0)}
    v0 = dict(parts=[dict(name=n, url=f"../v0_archive/stl/{n}.stl", pos=list(place_v0[n])) for n in V0_FILES],
              tubes=[dict(name="post", a=[0, 0, 0], b=[0, 0, 635], od=25.4),
                     dict(name="arm", a=[0, 0, 182], b=[0, 0, 682], od=25.4),
                     dict(name="axle", a=[0, -55, 700], b=[0, 55, 700], od=14.66),
                     dict(name="brace", a=[-25.25, 0, 349.75], b=[-375.0, 0, 0.0], od=14.66)],
              clashes=audit["clashes"], numbers={k: v for k, v in audit.items() if k != "clashes"})
    out = dict(version="v1", files=files, placements=places, tubes=tubes, bolts=bolts, bought=bought, lines=lines,
               board=A["board"], board_screws=A["board_screws"], layout=L, physics=physics, pendulum=PENDULUM,
               labels=LABELS, props=[7, 8, 10], v0=v0)
    path = os.path.join(G.ROOT, "viewer", "manifest.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="\n") as f:
        json.dump(out, f, indent=1)
    sliced = sum(1 for x in files if x["grams"] is not None)
    print(f"wrote {path}: {len(files)} print files ({sliced} sliced), {len(places)} placed parts, {len(bolts)} bolts, "
          f"{len(bought)} bought items, v0 with {len(v0['clashes'])} clashes")


if __name__ == "__main__":
    main()
