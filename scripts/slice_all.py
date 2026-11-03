#!/usr/bin/env python3
"""Slice every printed part for the Anycubic Kobra S1 (PETG: 4 walls, 30 % gyroid, 0.2 mm) with
Anycubic Slicer Next's CLI, the same way the VTOL project does: the STL (already in print
orientation) is centred on the bed and sliced with --orient 0 --arrange 0, so nothing turns it.

Out: gcode/<part>.gcode, each ending with a `; stand_stl_sha256 = ...` stamp of the STL it was
sliced from. make_viewer.py reads the sliced mass and time from them.
Set STAND_SLICER if the slicer is not at the default path.

Run: C:/Users/ajayad/venvs/vtol-venv/Scripts/python.exe scripts/slice_all.py [part ...]
"""
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_thrust_stand as B  # noqa: E402
import geom as G  # noqa: E402

SLICER = os.environ.get("STAND_SLICER", r"C:\Program Files\AnycubicSlicerNext\AnycubicSlicerNext.exe")
PROFILES = os.path.join(G.ROOT, "slicer_profiles")
MACHINE, PROCESS, FILAMENT = "machine_kobra_s1.json", "process_petg_stand.json", "filament_petg.json"
GCODE = os.path.join(G.ROOT, "gcode")
STAMP = "; stand_stl_sha256 = "


def stl_hash(name):
    with open(os.path.join(G.STL, name + ".stl"), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def bed_centre():
    with open(os.path.join(PROFILES, MACHINE)) as f:
        corners = [[float(c) for c in corner.split("x")] for corner in json.load(f)["printable_area"]]
    xs, ys = zip(*corners)
    return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2


def slice_part(name):
    cx, cy = bed_centre()
    dst = os.path.join(GCODE, name + ".gcode")
    with tempfile.TemporaryDirectory() as tmp:
        stl = os.path.join(tmp, name + ".stl")
        G.write_stl(stl, G.apply(G.read_stl(os.path.join(G.STL, name + ".stl")), None, (cx, cy, 0.0)))
        cmd = [SLICER, "--slice", "0", "--arrange", "0", "--orient", "0", "--ensure-on-bed",
               "--datadir", os.path.join(tmp, "cfg"),
               "--load-settings", ";".join(os.path.join(PROFILES, p) for p in (MACHINE, PROCESS)),
               "--load-filaments", os.path.join(PROFILES, FILAMENT), "--outputdir", tmp, stl]
        run = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        found = glob.glob(os.path.join(tmp, "*.gcode"))
        if len(found) != 1:
            raise RuntimeError(f"{name}: slicer produced {len(found)} G-code files (exit {run.returncode})\n"
                               f"{(run.stdout + run.stderr)[-1500:]}")
        os.makedirs(GCODE, exist_ok=True)
        shutil.move(found[0], dst)
    with open(dst, "a", newline="\n") as f:
        f.write(f"{STAMP}{stl_hash(name)}\n")
    return dst


def stats(name):
    """(grams, minutes, stamp_ok) from a part's G-code, or (None, None, False) if it is missing."""
    path = os.path.join(GCODE, name + ".gcode")
    if not os.path.exists(path):
        return None, None, False
    with open(path, "r", errors="replace") as f:
        f.seek(max(0, os.path.getsize(path) - 300_000))
        tail = f.read()
    m = re.search(r"; total filament used \[g\] = ([\d.]+)", tail)
    t = re.search(r"; estimated printing time \(normal mode\) = ([^\n]+)", tail)
    s = re.search(re.escape(STAMP) + r"([0-9a-f]{64})", tail)
    minutes = None
    if t:
        unit = dict(d=1440, h=60, m=1, s=1 / 60)
        minutes = sum(float(v) * unit[k] for v, k in re.findall(r"(\d+)([dhms])", t.group(1)))
    return (float(m.group(1)) if m else None), minutes, bool(s and s.group(1) == stl_hash(name))


def main(names=None):
    if not os.path.exists(SLICER):
        sys.exit(f"slicer not found: {SLICER} (set STAND_SLICER)")
    if not names:                                          # G-code of parts that no longer exist goes
        for old in glob.glob(os.path.join(GCODE, "*.gcode")):
            if os.path.basename(old)[:-6] not in B.FILES:
                os.remove(old)
    for name in names or B.FILES:
        dst = slice_part(name)
        g, m, _ = stats(name)
        print(f"sliced {name:20s} {g:7.1f} g {m / 60:5.1f} h  -> {os.path.relpath(dst, G.ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1:] or None)
