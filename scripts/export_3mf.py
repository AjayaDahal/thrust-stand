#!/usr/bin/env python3
"""Save every print file as an Anycubic Slicer Next project, 3mf/<part>.3mf: the part in its print
orientation at the centre of the Kobra S1's bed (extra copies arranged on the same plate), with the
printer (Kobra S1 0.4), process (PETG thrust stand: 4 walls, 30 % gyroid, 0.2 mm) and filament
(PETG) settings inside. Open one in the slicer, slice, and send it to the printer.

Each project is checked by slicing it again from the 3MF alone: the filament mass must match the
part's G-code in gcode/ (slice_all.py), so the settings and placement really are in the file.

Run: C:/Users/ajayad/venvs/vtol-venv/Scripts/python.exe scripts/export_3mf.py [part ...]
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_thrust_stand as B  # noqa: E402
import geom as G  # noqa: E402
from slice_all import FILAMENT, MACHINE, PROCESS, PROFILES, SLICER, bed_centre, stats  # noqa: E402

OUT = os.path.join(G.ROOT, "3mf")


def run(cmd, what):
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    return res, f"{what} (exit {res.returncode})\n{(res.stdout + res.stderr)[-1500:]}"


def export(name):
    cx, cy = bed_centre()
    copies = max(1, len(B.PARTS[name]["at"]))
    dst = os.path.join(OUT, name + ".3mf")
    if os.path.exists(dst):
        os.remove(dst)
    with tempfile.TemporaryDirectory() as tmp:
        stl = os.path.join(tmp, name + ".stl")
        G.write_stl(stl, G.apply(G.read_stl(os.path.join(G.STL, name + ".stl")), None, (cx, cy, 0.0)))
        cmd = [SLICER, "--arrange", "1" if copies > 1 else "0", "--orient", "0", "--ensure-on-bed",
               "--datadir", os.path.join(tmp, "cfg"),
               "--load-settings", ";".join(os.path.join(PROFILES, p) for p in (MACHINE, PROCESS)),
               "--load-filaments", os.path.join(PROFILES, FILAMENT),
               "--outputdir", tmp, "--export-3mf", name + ".3mf"] + [stl] * copies   # a path inside --outputdir
        _, msg = run(cmd, f"{name}: export")
        if not os.path.exists(os.path.join(tmp, name + ".3mf")):
            raise RuntimeError(msg)
        shutil.move(os.path.join(tmp, name + ".3mf"), dst)
    return dst, copies


def check(name, dst, copies):
    """Slice the 3MF on its own and compare with the part's G-code; return a one-line summary."""
    with zipfile.ZipFile(dst) as z:
        cfg = json.loads(z.read("Metadata/project_settings.config"))
    want = {"printer_settings_id": "Anycubic Kobra S1 0.4 nozzle", "wall_loops": "4",
            "sparse_infill_density": "30%", "layer_height": "0.2"}
    bad = [f"{k}={cfg.get(k)!r}" for k, v in want.items() if cfg.get(k) != v]
    if cfg.get("filament_type") != ["PETG"]:
        bad.append(f"filament_type={cfg.get('filament_type')!r}")
    with tempfile.TemporaryDirectory() as tmp:
        res, msg = run([SLICER, "--slice", "0", "--datadir", os.path.join(tmp, "cfg"), "--outputdir", tmp, dst],
                       f"{name}: re-slice")
        found = glob.glob(os.path.join(tmp, "*.gcode"))
        if len(found) != 1:
            raise RuntimeError(msg)
        with open(found[0], errors="replace") as f:
            tail = f.read()[-300_000:]
    grams = float(tail.split("; total filament used [g] = ")[1].split()[0])
    ref = (stats(name)[0] or 0.0) * copies
    if abs(grams - ref) > 0.02 * ref + 0.2:
        bad.append(f"re-sliced {grams:.1f} g vs {ref:.1f} g in gcode/")
    if bad:
        raise RuntimeError(f"{name}: " + "; ".join(bad))
    return (f"{name:20s} x{copies}  {os.path.getsize(dst) / 1024:6.0f} KB  re-sliced {grams:6.1f} g "
            f"(gcode/ {ref:6.1f} g), {cfg['print_settings_id']} / {cfg['filament_settings_id'][0]}")


def made_here(path):
    """True for a project this script wrote: every object in it is the file's own STL."""
    stem = os.path.basename(path)[:-4]
    try:
        with zipfile.ZipFile(path) as z:
            names = re.findall(r'<object id="\d+">\s*<metadata key="name" value="([^"]*)"',
                               z.read("Metadata/model_settings.config").decode())
    except (zipfile.BadZipFile, KeyError):
        return False
    return bool(names) and set(names) == {stem + ".stl"}


def main(names=None):
    if not os.path.exists(SLICER):
        sys.exit(f"slicer not found: {SLICER} (set STAND_SLICER)")
    os.makedirs(OUT, exist_ok=True)
    if not names:                                          # stale per-part projects go, nothing else
        for old in glob.glob(os.path.join(OUT, "*.3mf")):
            if os.path.basename(old)[:-4] not in B.FILES and made_here(old):
                os.remove(old)
    for name in names or B.FILES:
        dst, copies = export(name)
        print(check(name, dst, copies))


if __name__ == "__main__":
    main(sys.argv[1:] or None)
