#!/usr/bin/env python3
"""The gate: checks the v1 assembly before anything is printed. Exit code 1 if any check fails.

  1  every part is a valid solid and fits the Kobra S1 bed (250 mm) in its print orientation
  2  nothing collides: placed parts, tubes, bolts (head, washers, nut) and bought parts, pairwise
     (bolts through the tubes they are drilled through, and screws into their tapped holes, allowed)
  3  every bolt's length: 1-8 mm out of its nut, or the right thread engagement
  4  every M4 nut sits behind at least 3 mm of solid wall (v0's pockets opened on the mating face)
  5  the motor plate takes the 2807's 19x19 pattern and 16/19 cross patterns either way round
  6  measurement: link pins on the thrust line and the centre plane; the crank's arms equal, its
     nose on the anvil at the pivot's height, the anvil on the scale; reads 1:1, within 0.5 % for
     a link end 5 mm off
  7  the swing stop: the hub meets the bridge at 3-6 deg, and at the stop the prop still clears
  8  prop discs (7, 8 and 10 in) clear the board, the post and the scale masts
  9  print orientation: no flat ceiling wider than 16 mm needs bridging or support

Run: C:/Users/ajayad/venvs/vtol-venv/Scripts/python.exe scripts/check_stand.py
"""
import math
import os
import sys

import numpy as np
from build123d import Box, Cone, Cylinder, Pos, Rot

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_thrust_stand as B  # noqa: E402
import geom as G  # noqa: E402

BED = 250.0
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{': ' + detail if detail else ''}")


def cyl_between(a, b, r):
    a, b = np.asarray(a, float), np.asarray(b, float)
    v = b - a
    L = float(np.linalg.norm(v))
    d = v / L
    c = (a + b) / 2
    # rotate z onto d: about y by theta, then about z by phi
    theta = math.degrees(math.acos(max(-1.0, min(1.0, d[2]))))
    phi = math.degrees(math.atan2(d[1], d[0]))
    return Pos(*c) * Rot(0, 0, phi) * Rot(0, theta, 0) * Cylinder(r, L)


WASHER_OD = {"M3": 7.0, "M4": 9.0, "M5": 10.0, "M8": 16.0}


def bolt_solids(b):
    """Shank, head, washers and nut of one bolt, as solids (nut as its inscribed cylinder)."""
    p0, u = np.array(b["p0"]), np.array(b["u"])
    wh, wn = b["washers"]
    hd, hh = b["head"]
    s = cyl_between(p0, p0 + u * b["length"], b["d"] / 2 * 0.98)
    if b["csk"]:                                                # flat head inside its countersink
        c = p0 + u * hh / 2
        s += Pos(*c) * Rot(0, 180 if u[2] > 0 else 0, 0) * Cone(b["d"] / 2 * 0.98, hd / 2 * 0.97, hh * 0.98)
    else:
        s += cyl_between(p0 - u * hh, p0, hd / 2)
    if wh:
        s += cyl_between(p0, p0 + u * wh, WASHER_OD[b["size"]] / 2)
    if b["nut"]:
        a0 = wh + b["stack"]
        if wn:
            s += cyl_between(p0 + u * a0, p0 + u * (a0 + wn), WASHER_OD[b["size"]] / 2)
        af, t = b["nut_dims"]
        s += cyl_between(p0 + u * (a0 + wn), p0 + u * (a0 + wn + t), af / 2)
    return s


def bought_solids(e):
    if e["kind"] == "motor":
        x, y, z = e["base"]
        (rs, hs), (rb, hb) = e["stator"], e["bell"]
        s = B.cyl_x(rs, x, x + hs, y, z) + B.cyl_x(rb, x + hs, x + hs + hb, y, z)
        s += B.cyl_x(e["shaft"], x + hs + hb, x + e["prop_at"] + 4, y, z) + B.cyl_x(6.0, x + e["prop_at"] - 4,
                                                                                  x + e["prop_at"] + 4, y, z)
        return s + B.cyl_x(2.5, x - 1.5, x, y, z)                  # shaft end and circlip under the base
    if e["kind"] == "box":
        return Pos(*e["pos"]) * Box(*e["size"])
    if e["kind"] == "cyl":
        a = np.array(e["pos"]) - np.array(e["axis"]) * e["h"] / 2
        bb = np.array(e["pos"]) + np.array(e["axis"]) * e["h"] / 2
        return cyl_between(a, bb, e["r"]) - cyl_between(a - np.array(e["axis"]), bb + np.array(e["axis"]), 4.0)
    raise ValueError(e)


def assemble(parts):
    """Every object: name -> dict(solid, option, kind)."""
    objs = {}
    for name, spec in B.PARTS.items():
        for k, at in enumerate(spec["at"]):
            inst = name if len(spec["at"]) == 1 else f"{name}_{k + 1}"
            turn = at[3] if len(at) > 3 else 0.0
            objs[inst] = dict(solid=Pos(*at[:3]) * Rot(0, 0, turn) * parts[name], option=spec["option"], kind="part",
                              part=name)
    for t in B.tubes():
        objs[t["name"]] = dict(solid=cyl_between(t["a"], t["b"], t["od"] / 2), option=t["option"], kind="tube")
    for b in B.hardware():
        objs[b["name"]] = dict(solid=bolt_solids(b), option=b["option"], kind="bolt", spec=b)
    for e in B.bought():
        objs[e["name"]] = dict(solid=bought_solids(e), option=e["option"], kind="bought")
    bd = B.BOARD
    objs["board"] = dict(solid=B.box(bd["x0"], bd["x1"], bd["y0"], bd["y1"], -bd["t"], 0), option="core", kind="board")
    return objs


ALLOWED = {("foot_bolt", "post"), ("head_post_bolt", "post"), ("hub_axle_bolt", "axle"), ("hub_arm_bolt", "arm"),
           ("clamp_bolt", "arm")}
INTO = {"motor", "load_cell"}


def compatible(a, b):
    return not ({a, b} == {"bench", "cell"} or (a in ("cal",) and b in ("bench", "cell", "guy"))
                or (b in ("cal",) and a in ("bench", "cell", "guy")))


def allowed(n1, o1, n2, o2):
    if (n1, n2) in ALLOWED or (n2, n1) in ALLOWED:
        return True
    for x, y in ((o1, o2), (o2, o1)):
        if x["kind"] == "bolt" and x["spec"]["into"] and x["spec"]["into"] == y.get("name"):
            return True
    return False


def bbox_overlap(a, b, tol=0.0):
    A, Bb = a.bounding_box(), b.bounding_box()
    return (A.min.X - tol <= Bb.max.X and Bb.min.X - tol <= A.max.X and A.min.Y - tol <= Bb.max.Y
            and Bb.min.Y - tol <= A.max.Y and A.min.Z - tol <= Bb.max.Z and Bb.min.Z - tol <= A.max.Z)


def check_clashes(objs):
    names = list(objs)
    for n in names:
        objs[n]["name"] = n
    worst, n_pairs = [], 0
    for i, n1 in enumerate(names):
        for n2 in names[i + 1:]:
            o1, o2 = objs[n1], objs[n2]
            if not compatible(o1["option"], o2["option"]) or allowed(n1, o1, n2, o2):
                continue
            if not bbox_overlap(o1["solid"], o2["solid"]):
                continue
            n_pairs += 1
            v = (o1["solid"] & o2["solid"]).volume
            if v > 0.5:
                worst.append((v, n1, n2))
    worst.sort(reverse=True)
    check("2 no collisions", not worst,
          f"{n_pairs} touching or near pairs tested" if not worst else
          "; ".join(f"{a} x {b} {v:.0f} mm3" for v, a, b in worst[:8]))


def check_bolts():
    bad, lines = [], []
    for b in B.hardware():
        wh, wn = b["washers"]
        if b["nut"]:
            out = b["length"] - (wh + b["stack"] + wn + b["nut_dims"][1])
            ok = 1.0 <= out <= 8.0
            lines.append(f"{b['name']} {b['size']}x{b['length']} +{out:.1f}")
        else:
            eng = b["length"] - wh - b["stack"]
            lo, hi = (3.0, 4.5) if b["into"] == "motor" else (6.0, 10.0)
            ok = lo <= eng <= hi
            lines.append(f"{b['name']} {b['size']}x{b['length']} thread {eng:.1f}")
        if not ok:
            bad.append(lines[-1])
    check("3 bolt lengths", not bad, f"{len(lines)} bolts" if not bad else "; ".join(bad))


def check_nut_walls(parts):
    """Ring of solid around each M4 bolt between the mating face and its nut: must be full."""
    probes = []
    for sz in (-B.PLATE_BOLT_Z, B.PLATE_BOLT_Z):
        probes.append(("motor_clamp", B.cyl_x(3.4, B.NUT_X[1], B.CLAMP["x"], z=sz) - B.cyl_x(2.4, 0, 40, z=sz),
                       B.CLAMP["x"] - B.NUT_X[1]))
    for sx in (-20, 20):
        z1, z0 = B.MAST_FLANGE, B.MAST_FLANGE - 3.2
        probes.append(("cal_mast", B.cyl_z(3.4, z0, z1, x=sx) - B.cyl_z(2.4, 0, 300, x=sx), 3.2))
    bad = []
    for part, ring, wall in probes:
        full = ring.volume
        got = (parts[part] & ring).volume
        if got < 0.97 * full or wall < 3.0:
            bad.append(f"{part}: {got / full:.0%} solid, wall {wall:.1f} mm")
    check("4 M4 nuts captured behind a wall", not bad,
          f"walls {B.CLAMP['x'] - B.NUT_X[1]:.1f} mm (clamp), 3.2 mm (mast flange)" if not bad else "; ".join(bad))


def check_motor_patterns():
    pats = {"2807 19x19": [(9.5, 9.5), (-9.5, 9.5), (-9.5, -9.5), (9.5, -9.5)],
            "16x16 square": [(8, 8), (-8, 8), (-8, -8), (8, -8)],
            "2212 cross 16/19": [(0, 8), (0, -8), (9.5, 0), (-9.5, 0)],
            "2212 cross 19/16": [(0, 9.5), (0, -9.5), (8, 0), (-8, 0)]}
    bad = []
    for pname, holes in pats.items():
        for y, z in holes:
            best = 9e9
            for a, r0, r1 in B.MOTOR_SLOTS:
                u = np.array([math.cos(math.radians(a)), math.sin(math.radians(a))])
                t = np.clip(np.dot([y, z], u), r0, r1)
                best = min(best, float(np.linalg.norm(np.array([y, z]) - t * u)))
            if best > (3.4 - 3.0) / 2 + 1e-6:
                bad.append(f"{pname} hole ({y}, {z}) {best:.2f} mm off")
    check("5 motor plate fits 19x19, 16x16 and 16/19 crosses", not bad, "; ".join(bad))


def ratio(e, x_hook=B.X_HOOK):
    """Scale force / thrust, for a hook e mm above the link pin (moment balance about the pivot)."""
    px, pz = B.PIN_X, B.Z_SHAFT
    dx, dz = x_hook - px, e
    arm = abs((0 - px) * dz - (B.Z_PIVOT - pz) * dx) / math.hypot(dx, dz)
    return (B.Z_PIVOT - B.Z_SHAFT) / arm


def check_measurement(objs):
    ok = True
    for name in ("crank_link", "cell_link"):
        at = B.PARTS[name]["at"][0]
        ok &= abs(at[2] - B.Z_SHAFT) < 1e-9 and abs(at[1]) < 1e-9
    ok &= abs(B.PARTS["cell_clevis"]["at"][0][2] - B.Z_SHAFT) < 1e-9
    # The crank: link pin straight above the pivot at shaft height; the nose's lowest point on the
    # anvil, level with the pivot and as far north of it as the pin is above it; the anvil on the scale.
    r = B.CRANK["r"]
    pin_up = B.Z_SHAFT - B.Z_NOSE
    crank = objs["crank"]["solid"]
    nose = crank & B.box(B.X_PAN - 8, B.X_PAN + 8, -20, 20, 0, B.Z_NOSE + 6)
    nb = nose.bounding_box()
    ab = objs["scale_anvil"]["solid"].bounding_box()
    scale_top = objs["scale_pan"]["solid"].bounding_box().max.Z
    reach = B.X_PAN - B.X_CRANK
    ok &= abs(nb.min.Z - ab.max.Z) < 0.01 and abs(ab.max.Z - B.Z_NOSE) < 0.01 and abs(ab.min.Z - scale_top) < 0.01
    ok &= abs(pin_up - r) < 1e-9 and abs(reach - r) < 1e-9
    r0, rm, rp = ratio(0), ratio(-5), ratio(5)
    ok &= abs(r0 - 1) < 1e-9 and max(abs(rm - 1), abs(rp - 1)) < 0.005
    check("6 links on the thrust line and the centre plane; crank 1:1; reads 1:1", ok,
          f"crank arms {pin_up:.2f} / {reach:.2f} mm, nose {nb.min.Z:.2f} on the anvil at {ab.max.Z:.2f}, "
          f"anvil on the scale at {scale_top:.2f}; link end 5 mm low {rm:.4f}, 5 mm high {rp:.4f}")


def pendulum(objs, deg):
    """The swinging objects turned about the pivot axle by deg (positive = prop end swings south)."""
    names = ["arm_hub", "arm", "axle", "motor_clamp", "motor_plate", "motor", "hub_axle_bolt", "hub_arm_bolt",
             "clamp_bolt", "plate_bolt_upper", "plate_bolt_lower", "esc"]
    T = Pos(0, 0, B.Z_PIVOT) * Rot(0, deg, 0) * Pos(0, 0, -B.Z_PIVOT)
    return {n: T * objs[n]["solid"] for n in names}


def prop_disc(d_in, deg=0.0, half=10.0):
    r = d_in * 25.4 / 2
    x = B.X_PLATE_FRONT + 37.0
    disc = B.cyl_x(r, x - half, x + half, z=B.Z_SHAFT)
    return Pos(0, 0, B.Z_PIVOT) * Rot(0, deg, 0) * Pos(0, 0, -B.Z_PIVOT) * disc


def stop_angle(objs, sign):
    head = objs["pivot_head"]["solid"]
    lo, hi = 0.0, 12.0
    for _ in range(14):
        mid = (lo + hi) / 2
        hub = Pos(0, 0, B.Z_PIVOT) * Rot(0, sign * mid, 0) * Pos(0, 0, -B.Z_PIVOT) * objs["arm_hub"]["solid"]
        if (hub & head).volume > 0.05:
            hi = mid
        else:
            lo = mid
    return hi


def check_swing_and_props(objs):
    stops = [stop_angle(objs, s) for s in (1, -1)]
    fixed = ["post", "post_foot", "pivot_head", "board", "crank", "crank_base", "bench_scale", "crank_link",
             "cell_mast", "load_cell", "cell_clevis", "guy_anchor"]
    lines, bad = [], []
    for d_in in (7, 8, 10):
        for deg in (0.0, stops[0], -stops[1]):
            disc = prop_disc(d_in, deg)
            for n in fixed:
                gap = disc.distance_to(objs[n]["solid"])
                need = 40.0 if n == "board" else 10.0
                if gap < need:
                    bad.append(f"{d_in} in at {deg:+.1f} deg: {n} {gap:.0f} mm")
        lines.append(f"{d_in} in: board {B.Z_SHAFT - d_in * 12.7:.0f} mm, post "
                     f"{prop_disc(d_in, stops[0]).distance_to(objs['post']['solid']):.0f} mm at the south stop")
    cal = prop_disc(7).distance_to(objs["cal_mast"]["solid"])
    ok_stop = all(3.0 <= s <= 6.0 for s in stops)
    check("7 swing stop at 3-6 deg either way", ok_stop, f"{stops[0]:.1f} / {stops[1]:.1f} deg "
          f"(prop end moves {math.radians(max(stops)) * (B.Z_PIVOT - B.Z_SHAFT):.0f} mm)")
    check("8 prop discs clear board, post and masts (also at the stops)", not bad,
          "; ".join(lines) + f"; calibration mast {cal:.0f} mm in front of a 7 in disc: remove it before running"
          if not bad else "; ".join(bad))


def patches(tris, sel):
    """Connected groups (shared vertices) of the selected triangles, as boolean masks."""
    idx = np.flatnonzero(sel)
    if not len(idx):
        return []
    keys = {}
    parent = list(range(len(idx)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for k, t in enumerate(idx):
        for v in tris[t]:
            key = tuple(np.round(v, 2))
            if key in keys:
                a, b = find(k), find(keys[key])
                if a != b:
                    parent[a] = b
            else:
                keys[key] = k
    groups = {}
    for k, t in enumerate(idx):
        groups.setdefault(find(k), []).append(t)
    out = []
    for members in groups.values():
        m = np.zeros(len(tris), bool)
        m[members] = True
        out.append(m)
    return out


def perimeter(tris):
    """Length of the boundary of a triangle patch (edges used by one triangle only)."""
    count = {}
    for t in tris:
        for i in range(3):
            a, b = tuple(np.round(t[i], 2)), tuple(np.round(t[(i + 1) % 3], 2))
            k = (a, b) if a < b else (b, a)
            count[k] = count.get(k, 0) + 1
    return sum(np.linalg.norm(np.subtract(a, b)) for (a, b), n in count.items() if n == 1)


def check_print():
    bad, notes = [], []
    for name in B.FILES:
        tris = G.read_stl(os.path.join(G.STL, name + ".stl"))
        lo, hi = tris.reshape(-1, 3).min(0), tris.reshape(-1, 3).max(0)
        size = hi - lo
        if abs(lo[2]) > 1e-3 or max(size[0], size[1]) > BED - 10 or size[2] > BED:
            bad.append(f"{name}: {size.round(1)} mm, min z {lo[2]:.2f}")
        n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
        area = np.linalg.norm(n, axis=1) / 2
        nz = n[:, 2] / np.maximum(2 * area, 1e-12)
        zc = tris[:, :, 2].mean(1)
        sel = (nz < -0.98) & (zc > 0.3) & (area > 1e-6)
        for g in patches(tris, sel):
            pts = tris[g][:, :, :2].reshape(-1, 2)
            # narrowest extent: the bounding box for strips and plates, 4 area / perimeter for rings
            w = min(np.ptp(pts[:, 0]), np.ptp(pts[:, 1]), 4 * area[g].sum() / max(perimeter(tris[g]), 1e-9))
            if w > 16.0 and area[g].sum() > 60.0:
                bad.append(f"{name}: flat ceiling at z {zc[g].mean():.1f}, {area[g].sum():.0f} mm2, {w:.0f} mm wide")
            elif area[g].sum() > 20.0:
                notes.append(f"{name} {w:.1f} mm")
    check("1+9 parts fit the bed and print without supports", not bad,
          f"{len(B.FILES)} files; bridges: {', '.join(sorted(set(notes)))}" if not bad else "; ".join(bad))


def info(parts):
    """Numbers for REPORT.md: the pendulum's gravity stiffness and pivot friction, worst case."""
    m = 0.050 + 0.008 + 0.030                                   # motor, prop, ESC
    pet = 1.27e-3 * 0.55                                        # g/mm3 of PETG at ~55 % effective fill
    for n in ("arm_hub", "motor_clamp", "motor_plate"):
        m += parts[n].volume * pet / 1000
    m += math.pi / 4 * (25.4 ** 2 - 22.4 ** 2) * 500 * 1.4e-6   # PVC arm, ~1.5 mm wall
    d = 0.33                                                    # CG below the pivot, m (estimate)
    L = (B.Z_PIVOT - B.Z_SHAFT) / 1000
    k_g = m * 9.81 * d / L ** 2                                 # N/m at the thrust line
    fric = 0.3 * m * 9.81 * (B.THIN_OD / 2000) / L              # N, PETG on PVC, mu 0.3
    # crank: the axle carries the link's pull and the anvil's push, at right angles (sqrt 2 x thrust);
    # ball bearings, mu ~0.0015 at the 8 mm bore. Worst case at 2 kg of thrust, in g of reading.
    crank = 0.0015 * math.sqrt(2) * 20.0 * 0.004 / (B.CRANK["r"] / 1000)
    print(f"[info] pendulum ~{m * 1000:.0f} g; gravity stiffness {k_g:.1f} N/m at the thrust line "
          f"(1 mm of scale travel = {k_g * 1e-3 / 9.81 * 1000:.2f} g); pivot friction <= {fric / 9.81 * 1000:.1f} g; "
          f"crank bearings <= {crank / 9.81 * 1000:.2f} g at 2 kg")


def main():
    parts = B.build(verbose=False)
    check("1 all parts valid solids", all(p.is_valid for p in parts.values()), f"{len(parts)} parts")
    objs = assemble(parts)
    check_clashes(objs)
    check_bolts()
    check_nut_walls(parts)
    check_motor_patterns()
    check_measurement(objs)
    check_swing_and_props(objs)
    check_print()
    info(parts)
    n_bad = sum(1 for _, ok, _ in RESULTS if not ok)
    print(f"\n{len(RESULTS) - n_bad}/{len(RESULTS)} checks pass")
    sys.exit(1 if n_bad else 0)


if __name__ == "__main__":
    main()
