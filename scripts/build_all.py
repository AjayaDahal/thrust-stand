#!/usr/bin/env python3
"""Rebuild everything after a change: parts and assembly, the v0 audit, the gate, slicing and the
slicer projects (3mf/), the viewer manifest and the diagram. Stops at the first failure (the gate
fails on any clash).
Renders: then run serve_viewer.py and open http://127.0.0.1:28766/viewer/?capture=1

Run: C:/Users/ajayad/venvs/vtol-venv/Scripts/python.exe scripts/build_all.py [--no-slice]
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = ["build_thrust_stand.py", "audit_v0.py", "check_stand.py", "slice_all.py", "export_3mf.py", "make_viewer.py",
         "make_diagram.py"]

if __name__ == "__main__":
    for step in STEPS:
        if step in ("slice_all.py", "export_3mf.py") and "--no-slice" in sys.argv:
            continue
        print(f"== {step}", flush=True)
        if subprocess.run([sys.executable, os.path.join(HERE, step)]).returncode:
            sys.exit(f"{step} failed")
    print("all steps done")
