#!/usr/bin/env python3
"""Dimensioned drawings of the v1 stand, from the same numbers as build_thrust_stand.py:
diagram.png (side and front views), cut_guide.png (each tube laid out like a ruler: cut length, where
each printed part and cross-bolt sits, measured from the tube's ends) and board_layout.png (where each
part stands on the board, measured from the arm axis). Unlike v0's diagram, nothing is drawn displaced:
the arm and the post really are 70 mm apart (front view).

Run: C:/Users/ajayad/venvs/vtol-venv/Scripts/python.exe scripts/make_diagram.py
"""
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Circle, Polygon, Rectangle  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_thrust_stand as B  # noqa: E402
import geom as G  # noqa: E402

PETG, TUBE, BOARD, SCALE = "#2f6db5", "#e9e7df", "#d8c9a3", "#3b3f45"


def rect(ax, x0, x1, z0, z1, fc=PETG, alpha=1.0, **kw):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, facecolor=fc, edgecolor="k", lw=0.8, alpha=alpha, **kw))


def dim_v(ax, x, z0, z1, label, side=1):
    ax.annotate("", (x, z0), (x, z1), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(x + 8 * side, (z0 + z1) / 2, label, fontsize=8, va="center", ha="left" if side > 0 else "right")


def dim_h(ax, z, x0, x1, label):
    ax.annotate("", (x0, z), (x1, z), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text((x0 + x1) / 2, z + 8, label, fontsize=8, ha="center")


def side(ax):
    zs, zp, hz = B.Z_SHAFT, B.Z_PIVOT, B.HUB_Z0
    rect(ax, B.BOARD["x0"], B.BOARD["x1"], -B.BOARD["t"], 0, BOARD)
    rect(ax, -50, 50, 0, 50, alpha=0.35)                                    # post foot (behind)
    rect(ax, -12.7, 12.7, 0, B.POST_TOP, TUBE, alpha=0.6)                   # post (behind the arm)
    rect(ax, -B.HEAD_X, B.HEAD_X, zp + B.HEAD_Z0, zp + B.HEAD_Z1, alpha=0.55)
    rect(ax, -B.HUB["x"], B.HUB["x"], hz, hz + B.HUB["h"])
    rect(ax, -12.7, 12.7, B.ARM_BOT, B.ARM_TOP, TUBE)
    ax.add_patch(Circle((0, zp), B.THIN_OD / 2, facecolor=TUBE, edgecolor="k", lw=0.8))
    rect(ax, -30, 30, zs - 30, zs + 30)                                     # clamp
    rect(ax, -46, -30, zs - 30, zs + 30, alpha=0.7)                         # fork
    rect(ax, 30, 38, zs - 30, zs + 30, "#5d8fd0")                           # motor plate
    rect(ax, 38, 44, zs - 14, zs + 14, "#3b3b3b")
    rect(ax, 44, 68, zs - 17, zs + 17, "#b03030")
    x_prop = B.X_PLATE_FRONT + 37
    for d_in, ls in ((7, "-"), (10, "--")):
        r = d_in * 25.4 / 2
        ax.plot([x_prop, x_prop], [zs - r, zs + r], "k", lw=2.2 if ls == "-" else 1.0, ls=ls)
        ax.text(x_prop + 6, zs + r - 6, f"{d_in} in prop", fontsize=7.5)
    ax.plot([B.PIN_X, B.X_CRANK], [zs, zs], color=PETG, lw=5, solid_capstyle="round")
    for x in (B.PIN_X, B.X_CRANK):
        ax.plot(x, zs, "o", ms=4, mfc="white", mec="k")
    # kitchen scale with the anvil, crank base (cheeks behind the crank) and the bell crank
    xp, zp0, xc, r = B.X_PAN, B.Z_NOSE, B.X_CRANK, B.CRANK["r"]
    w, h = B.BENCH["W"], B.BENCH["H"]
    rect(ax, xp - w / 2, xp + w / 2, 0, h - 1, SCALE)
    rect(ax, xp - w / 2 + 2.5, xp + w / 2 - 2.5, h - 1, h, "#c9ced6")
    ax.text(xp - 5, h / 2, "0.1 g scale", color="white", ha="center", va="center", fontsize=6)
    (bx, _), (tx, _) = B.ANVIL["base"], B.ANVIL["top"]
    ax.add_patch(Polygon([(xp - bx / 2, h), (xp + bx / 2, h), (xp + tx / 2, zp0), (xp - tx / 2, zp0)],
                         closed=True, facecolor=PETG, edgecolor="k", lw=0.8))
    ax.text(xp + bx / 2 + 4, h + 4, "anvil", fontsize=7.5)
    rect(ax, xc - 45, xc + 45, 0, 8)
    rect(ax, xc - 18, xc + 18, 8, zp0 + 14, alpha=0.45)
    rect(ax, xc - 15, xc + 15, zp0, zs - 14)                                # crank: vertical arm
    ax.add_patch(Circle((xc, zs), 9, facecolor=PETG, edgecolor="k", lw=0.8))
    rect(ax, xc - 4.5, xc + 4.5, zs - 14, zs)
    rect(ax, xc, xp, zp0 + 8, zp0 + 36)                                     # horizontal arm
    ax.add_patch(Circle((xc, zp0), 16, facecolor=PETG, edgecolor="k", lw=0.8))
    ax.add_patch(Circle((xc, zp0), 11, facecolor="#9aa3ad", edgecolor="k", lw=0.6))
    ax.add_patch(Circle((xc, zp0), 4, facecolor="white", edgecolor="k", lw=0.6))
    ax.add_patch(Circle((xp, zp0 + 5), 5, facecolor=PETG, edgecolor="k", lw=0.8))
    ax.annotate("", (xp + 22, zp0 + 2), (xp + 22, zp0 + 125), arrowprops=dict(arrowstyle="-|>", color="#1f6fd1", lw=1.5))
    ax.text(xp + 16, zp0 + 85, "press on the anvil\n= thrust", color="#1f6fd1", fontsize=8, ha="right", va="bottom")
    ax.plot([xc, xp], [zp0, zp0], ls=":", color="k", lw=0.9)
    ax.text(xp - 40, -33, f"anvil top {zp0:.0f} = the crank's pivot height (dotted)", fontsize=7.5, ha="center")
    ax.annotate("", (x_prop + 150, zs), (x_prop + 8, zs), arrowprops=dict(arrowstyle="-|>", color="#d62828", lw=2))
    ax.text(x_prop + 80, zs + 10, "thrust", color="#d62828", ha="center", fontsize=9)
    ax.annotate("", (B.PIN_X - 125, zs + 40), (B.PIN_X - 5, zs + 40),
                arrowprops=dict(arrowstyle="-|>", color="#14853f", lw=1.5))
    ax.text(B.PIN_X - 65, zs + 48, "link pull = thrust", color="#14853f", ha="center", fontsize=8)
    dim_v(ax, 130, 0, zs, f"shaft and link {zs:.0f}")
    dim_v(ax, 130, zs, zp, f"arm {zp - zs:.0f} (pivot to shaft)")
    dim_v(ax, 300, 0, zp, f"pivot\naxle {zp:.0f}")
    dim_v(ax, 250, 0, B.POST_TOP, f"post {B.POST_TOP:.0f}", side=-1)
    dim_h(ax, zs - 52, xc, B.PIN_X, f"link {B.PIN_X - xc:.2f} (pin to pin)")
    dim_v(ax, xc - 40, zp0, zs, f"crank {r:.2f}", side=-1)
    dim_h(ax, zp0 + 60, xc, xp, f"crank {r:.2f}")
    ax.text(-200, zp - 20, "pivot head (inverted U) over the hub;\nthe bridge stops the swing at ~4 deg",
            fontsize=8, ha="right")
    ax.text(-465, 470, "link pins on the thrust line: no lever ratio\n(link end +-5 mm: < 0.5 %).\n"
            "The bell crank turns the pull into a press:\nequal arms, pivot level with the anvil,\n"
            "so the scale reads the thrust 1:1.", fontsize=8.5, ha="left", style="italic")
    ax.set_xlim(B.BOARD["x0"] - 20, 400)
    ax.set_ylim(-40, 790)
    ax.set_aspect("equal")
    ax.set_title("Side view (x-z); the post stands 70 mm to the side of the arm", fontsize=10)
    ax.set_xlabel("x: thrust direction (north), mm")
    ax.set_ylabel("z: height above the board, mm")
    ax.grid(True, alpha=0.25)


def front(ax):
    zs, zp = B.Z_SHAFT, B.Z_PIVOT
    rect(ax, B.BOARD["y0"], B.BOARD["y1"], -B.BOARD["t"], 0, BOARD)
    rect(ax, B.SCALE_Y[0], B.SCALE_Y[1], 0, B.BENCH["H"], SCALE, alpha=0.35)  # kitchen scale, behind
    y = B.POST_Y
    rect(ax, y - 50, y + 50, 0, 50)
    rect(ax, y - 12.7, y + 12.7, 0, B.POST_TOP, TUBE)
    yo = B.CHEEK_IN + B.CHEEK_T
    rect(ax, y - 25, -yo, zp + B.HEAD_Z0, zp + B.HEAD_Z1)                   # boss
    rect(ax, -yo, -B.CHEEK_IN, zp + B.HEAD_Z0, zp + B.HEAD_Z1)
    rect(ax, B.CHEEK_IN, yo, zp + B.HEAD_Z0, zp + B.HEAD_Z1)
    rect(ax, -yo, yo, zp + B.BRIDGE_Z0, zp + B.HEAD_Z1)
    rect(ax, -B.HUB["y"], B.HUB["y"], B.HUB_Z0, B.HUB_Z0 + B.HUB["h"], "#5d8fd0")
    rect(ax, B.AXLE_Y[0], B.AXLE_Y[1], zp - B.THIN_OD / 2, zp + B.THIN_OD / 2, TUBE)
    rect(ax, -12.7, 12.7, B.ARM_BOT, B.ARM_TOP, TUBE)
    rect(ax, -25, 25, zs - 30, zs + 30)
    for d_in, ls in ((7, "-"), (10, "--")):
        ax.add_patch(Circle((0, zs), d_in * 12.7, fill=False, ls=ls, lw=1.2))
    dim_h(ax, 470, y, 0, "70")
    ax.text(y - 22, 380, "post", ha="center", va="center", rotation=90, fontsize=8)
    ax.text(22, 380, "arm", ha="center", va="center", rotation=90, fontsize=8)
    ax.set_xlim(B.BOARD["y0"] - 10, B.BOARD["y1"] + 10)
    ax.set_ylim(-40, 790)
    ax.set_aspect("equal")
    ax.set_title("Front view, from the prop end", fontsize=10)
    ax.set_xlabel("y, mm")
    ax.grid(True, alpha=0.25)


def bolt_at(name):
    return next(b for b in B.hardware() if b["name"] == name)


def witness(ax, x, y0, y1):
    ax.plot([x, x], [y0, y1], color="0.55", lw=0.6, ls=(0, (3, 2)))


def hole_inplane(ax, x, half):
    """A cross-bolt that runs up-down in the drawing."""
    ax.plot([x, x], [-half, half], color="#d62828", lw=1.4, ls=(0, (4, 2)))


def hole_endon(ax, x, y=0.0, r=4.0):
    """A cross-bolt seen end-on: it runs into the page."""
    ax.add_patch(Circle((x, y), r, facecolor="white", edgecolor="#d62828", lw=1.4, zorder=5))
    ax.plot([x - r * 0.7, x + r * 0.7], [y - r * 0.7, y + r * 0.7], color="#d62828", lw=1.1, zorder=6)
    ax.plot([x - r * 0.7, x + r * 0.7], [y + r * 0.7, y - r * 0.7], color="#d62828", lw=1.1, zorder=6)


def tube_panel(ax, title, length, r, xlim, ylim):
    rect(ax, 0, length, -r, r, TUBE)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.set_yticks([])
    ax.set_title(title, fontsize=11, loc="left", fontweight="bold")
    ax.grid(True, axis="x", alpha=0.2)
    ax.set_xticks(range(0, int(length) + 1, 50 if length > 200 else 10))
    ax.tick_params(labelsize=7)


def post_panel(ax):
    L, r = B.POST_TOP, B.POST_OD / 2
    foot = B.post_foot().bounding_box()
    z_foot, z_head = bolt_at("foot_bolt")["p0"][2], bolt_at("head_post_bolt")["p0"][2]
    h0, h1 = B.Z_PIVOT + B.HEAD_Z0, B.Z_PIVOT + B.HEAD_Z1
    tube_panel(ax, f"POST: 25.4 mm tube, cut {L:.0f}. Lay it down and measure from the bottom end",
               L, r, (-45, 880), (-128, 100))
    rect(ax, -B.BOARD["t"], 0, -70, 70, BOARD)
    ax.text(-9, 0, "board", rotation=90, ha="center", va="center", fontsize=7.5)
    rect(ax, foot.min.Z, foot.max.Z, -foot.max.X, foot.max.X, alpha=0.4)
    rect(ax, h0, h1, -B.HEAD_X, B.HEAD_X, alpha=0.4)
    hole_endon(ax, z_foot)
    hole_inplane(ax, z_head, B.HEAD_X)
    ax.text(foot.max.Z / 2, foot.max.X + 5, "post_foot", ha="center", fontsize=8.5)
    ax.text(h1 + 8, 0, "pivot_head:\nthe post's top goes\nall the way into\nits socket", va="center", fontsize=8.5)
    ax.text(foot.max.Z + 12, 22, f"foot bolt M5\u00d780 at {z_foot:.0f}, runs east\u2013west (into the page)",
            fontsize=8.5, color="#a51d1d", va="bottom")
    ax.text(h0 - 8, 22, f"head bolt M5\u00d760 at {z_head:.0f} = {L - z_head:.0f} below the top,\n"
            "runs north\u2013south, level with the pivot axle", fontsize=8.5, color="#a51d1d", ha="right",
            va="bottom")
    for x, y, lab in ((z_foot, -60, f"{z_foot:.0f}"), (z_head, -82, f"{z_head:.0f}"), (L, -104, f"{L:.0f} = CUT")):
        witness(ax, x, 0, y)
        dim_h(ax, y, 0, x, lab)
    for x0, y, lab in ((z_head, 50, f"{L - z_head:.0f}"), (h0, 72, f"{L - h0:.0f} inside the head")):
        witness(ax, x0, 0, y)
        witness(ax, L, r, y)
        dim_h(ax, y, x0, L, lab)
    ax.text(0, -124, "0 = bottom end: it stands on the board inside post_foot", fontsize=8.5, va="bottom",
            fontweight="bold")


def arm_panel(ax):
    L, r, a0 = B.ARM_TOP - B.ARM_BOT, B.POST_OD / 2, B.ARM_BOT
    zc, zh, za = (bolt_at(n)["p0"][2] - a0 for n in ("clamp_bolt", "hub_arm_bolt", "hub_axle_bolt"))
    c0, c1 = B.Z_SHAFT - B.CLAMP["z"] - a0, B.Z_SHAFT + B.CLAMP["z"] - a0
    h0, h1 = B.HUB_Z0 - a0, B.HUB_Z0 + B.HUB["h"] - a0
    tube_panel(ax, f"ARM (motor end down): 25.4 mm tube, cut {L:.0f}. Measure from the bottom end",
               L, r, (-60, 640), (-110, 128))
    rect(ax, c0, c1, -B.CLAMP["x"], B.CLAMP["x"], alpha=0.4)
    rect(ax, c0, c1, B.FORK_X[0], B.FORK_X[1], alpha=0.25)
    rect(ax, c0, c1, B.CLAMP["x"], B.X_PLATE_FRONT, "#5d8fd0")
    rect(ax, zc - 17, zc + 17, B.X_PLATE_FRONT, B.X_PLATE_FRONT + 30, "#b03030")
    rect(ax, h0, h1, -B.HUB["x"], B.HUB["x"], alpha=0.4)
    r0, r1 = B.BORE_POST / 2, 4.0
    ax.plot([L, L + r0 - r1, L + r0 - r1, L], [r0, r1, -r1, -r0], color="k", lw=0.7)
    ax.add_patch(Circle((za, 0), B.THIN_OD / 2, facecolor=TUBE, edgecolor="k", lw=0.8))
    hole_endon(ax, zc)
    hole_inplane(ax, zh, B.HUB["x"])
    hole_inplane(ax, za, B.HUB["x"])
    ax.text(c1 + 4, B.X_PLATE_FRONT + 22, "motor (north)", fontsize=8, va="center")
    ax.text(c1 + 4, -24, "motor_clamp", fontsize=8.5, va="center")
    ax.text(c1 + 4, B.FORK_X[0] - 2, "link fork (south)", fontsize=8, va="top")
    ax.text(c1 + 4, 14, f"clamp bolt M5\u00d760 at {zc:.0f}: east\u2013west (into the page),\n"
            f"on the motor shaft's line, {B.Z_SHAFT:.0f} above the board", fontsize=8.5, color="#a51d1d",
            va="bottom")
    ax.text(h1 + 6, 0, "arm_hub: the arm\ngoes in up to the\n45\u00b0 cone; the pivot\naxle passes above it",
            va="center", fontsize=8.5)
    ax.text(h0 - 8, -30, f"hub bolt M5\u00d770 at {zh:.0f} = {L - zh:.0f} below the top, north\u2013south;\n"
            f"the other M5\u00d770 goes through the axle, not the arm", fontsize=8.5, color="#a51d1d", ha="right",
            va="top")
    for x, y, lab in ((zc, -66, f"{zc:.0f}"), (L, -88, f"{L:.0f} = CUT")):
        witness(ax, x, 0, y)
        dim_h(ax, y, 0, x, lab)
    for x0, y, lab in ((zh, 50, f"{L - zh:.0f}"), (h0, 72, f"{L - h0:.0f} inside the hub")):
        witness(ax, x0, 0, y)
        witness(ax, L, r, y)
        dim_h(ax, y, x0, L, lab)
    ax.text(0, -106, f"0 = bottom end: it hangs {B.ARM_BOT:.0f} above the board, {c0:.0f} below the clamp",
            fontsize=8.5, va="bottom", fontweight="bold")


def axle_panel(ax):
    y0, y1 = B.AXLE_Y
    L, r = y1 - y0, B.THIN_OD / 2
    u = lambda y: y - y0                                               # noqa: E731
    ub = bolt_at("hub_axle_bolt")["p0"][1] - y0
    tube_panel(ax, f"AXLE: 14.66 mm tube, cut {L:.0f}", L, r, (-28, 104), (-74, 64))
    rect(ax, u(-B.CHEEK_IN - B.CHEEK_T) - 14, u(-B.CHEEK_IN), -B.HEAD_X, B.HEAD_X, alpha=0.4)
    rect(ax, u(-B.HUB["y"]), u(B.HUB["y"]), -B.HUB["x"], B.HUB["x"], "#5d8fd0", alpha=0.4)
    rect(ax, u(B.CHEEK_IN), u(B.CHEEK_IN + B.CHEEK_T), -B.HEAD_X, B.HEAD_X, alpha=0.4)
    ax.plot([-3, -3], [-B.BORE_PIVOT / 2, B.BORE_PIVOT / 2], color="k", lw=1.2)
    hole_inplane(ax, ub, B.HUB["x"])
    ax.text(u(-B.CHEEK_IN) - 12, B.HEAD_X + 3, "near cheek,\nblind bore", ha="center", fontsize=7.5)
    ax.text(ub, B.HUB["x"] + 3, "arm_hub", ha="center", fontsize=7.5)
    ax.text(u(B.CHEEK_IN + B.CHEEK_T / 2), B.HEAD_X + 3, "far\ncheek", ha="center", fontsize=7.5)
    for x, y, lab in ((ub, -44, f"{ub:.0f}"), (L, -60, f"{L:.0f} = CUT")):
        witness(ax, x, 0, y)
        dim_h(ax, y, 0, x, lab)
    ax.text(ub + 2, -16, f"hub bolt\nM5\u00d770", fontsize=7.5, color="#a51d1d", va="top")
    ax.text(-26, -72, "0 = end in the blind bore (post side)", fontsize=7.5, va="bottom", fontweight="bold")


def cut_guide():
    fig = plt.figure(figsize=(16, 10.5))
    gs = fig.add_gridspec(2, 2, width_ratios=[2.9, 1], height_ratios=[1, 1.08])
    post_panel(fig.add_subplot(gs[0, :]))
    arm_panel(fig.add_subplot(gs[1, 0]))
    axle_panel(fig.add_subplot(gs[1, 1]))
    fig.suptitle("Cut and drill guide (mm). Red: cross-bolts. Drill each one through the printed part's own hole "
                 "once it is in place; these numbers are for checking. North is up in every view.", fontsize=11)
    plt.tight_layout()
    out = os.path.join(G.ROOT, "cut_guide.png")
    plt.savefig(out, dpi=130)
    plt.close(fig)
    print("wrote", out)


def footprint(ax, part, x, y, turn=0.0, fc=PETG, alpha=0.45, ls="-"):
    """A part's bounding-box outline on the board."""
    bb = B.PARTS[part]["fn"]().bounding_box()
    pts = [(bb.min.X, bb.min.Y), (bb.max.X, bb.min.Y), (bb.max.X, bb.max.Y), (bb.min.X, bb.max.Y)]
    c, s = np.cos(np.radians(turn)), np.sin(np.radians(turn))
    ax.add_patch(Polygon([(x + c * px - s * py, y + s * px + c * py) for px, py in pts], closed=True,
                         facecolor=fc, edgecolor="k", lw=0.8, alpha=alpha, ls=ls))


def board_layout():
    fig, ax = plt.subplots(figsize=(15, 9.4))
    bd = B.BOARD
    rect(ax, bd["x0"], bd["x1"], bd["y0"], bd["y1"], BOARD, alpha=0.45)
    ax.plot([bd["x0"], bd["x1"]], [0, 0], color="k", lw=0.8, ls=(0, (8, 4)))
    ax.text(bd["x0"] + 6, 5, "centreline", fontsize=8.5)
    ax.text(bd["x1"] + 8, 0, "NORTH edge (prop end)", rotation=90, va="center", fontsize=9, fontweight="bold")
    ax.text(bd["x0"] - 8, 0, "south edge", rotation=90, va="center", ha="right", fontsize=9)
    footprint(ax, "post_foot", 0, B.POST_Y)
    ax.add_patch(Circle((0, B.POST_Y), B.POST_OD / 2, facecolor=TUBE, edgecolor="k", lw=0.8))
    ax.add_patch(Circle((0, 0), B.POST_OD / 2, facecolor=TUBE, edgecolor="k", lw=0.8, ls="--"))
    ax.plot([-18, 18], [0, 0], "k", lw=1.2)
    ax.plot([0, 0], [-18, 18], "k", lw=1.2)
    ax.text(-16, 16, "arm axis: the arm\nhangs above this mark", ha="right", va="bottom", fontsize=8.5,
            fontweight="bold")
    x_prop, r7 = B.X_PLATE_FRONT + 37, 7 * 12.7
    ax.plot([x_prop, x_prop], [-r7, r7], color="#3b3b3b", lw=3)
    ax.text(x_prop + 5, r7 - 4, "7 in prop\n(overhead)", fontsize=8, va="top")
    w, Ls = B.BENCH["W"], B.SCALE_Y
    rect(ax, B.X_PAN - w / 2, B.X_PAN + w / 2, Ls[0], Ls[1], SCALE, alpha=0.3)
    sw, sl = B.BENCH["steel_w"] / 2, B.BENCH["steel_l"] / 2
    rect(ax, B.X_PAN - sw, B.X_PAN + sw, -sl, sl, "#c9ced6", alpha=0.6)
    (bx, by), _ = B.ANVIL["base"], B.ANVIL["top"]
    rect(ax, B.X_PAN - bx / 2, B.X_PAN + bx / 2, -by / 2, by / 2)
    ax.text(B.X_PAN, Ls[0] + 4, "display end", ha="center", fontsize=7)
    ax.text(B.X_PAN + 8, Ls[1] + 10, "A: pocket scale, anvil on the\nplatform's centre", va="bottom", fontsize=8.5)
    for at in B.PARTS["scale_corner"]["at"]:
        for (x0, x1, y0, y1) in ((-10, 40, -10, 0), (-10, 0, -10, 40)):      # scale_corner's two legs
            t = np.radians(at[3] if len(at) > 3 else 0.0)
            c, s = np.cos(t), np.sin(t)
            pts = [(at[0] + c * px - s * py, at[1] + s * px + c * py) for px, py in
                   ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
            ax.add_patch(Polygon(pts, closed=True, facecolor=PETG, edgecolor="k", lw=0.8, alpha=0.6))
    ax.text(B.X_CORNER - 4, Ls[1] + 16, "scale_corner \u00d72 (A)", ha="right", va="bottom", fontsize=8)
    footprint(ax, "crank_base", B.X_CRANK, 0)
    ax.plot([B.X_CRANK, B.X_CRANK], [-30, 30], "k", lw=1.6)
    ax.text(B.X_CRANK, -52, "A: crank_base\n(axle across, on this line)", ha="center", va="top", fontsize=8.5)
    footprint(ax, "cell_mast", B.X_CELL_MAST, 0, fc="none", alpha=1.0, ls="--")
    ax.text(B.X_CELL_MAST + 4, -122, "B instead of A: cell_mast (dashed)", va="top", fontsize=8.5,
            color="#5b2a86")
    footprint(ax, "cal_mast", B.X_CAL, 0, alpha=0.25, ls="--")
    ax.text(B.X_CAL, 52, "cal_mast\n(calibration only,\nnorth end on the edge)", ha="center", va="bottom",
            fontsize=8)
    footprint(ax, "guy_anchor", B.GUY_X, B.POST_Y, alpha=0.25, ls="--")
    ax.text(B.GUY_X, B.POST_Y + 36, "guy_anchor\n(optional)", ha="center", va="bottom", fontsize=8)
    ax.text(0, B.POST_Y - 56, "post_foot + post", ha="center", va="top", fontsize=8.5, fontweight="bold")
    witness(ax, 0, 18, 190)
    witness(ax, 0, -140, -190)
    for x, y, y0, lab in ((bd["x1"], 182, 0, f"{bd['x1']:.0f}: arm axis from the north edge"),
                          (B.X_CRANK, 158, 40, f"{-B.X_CRANK:.0f}: crank axle (A)"),
                          (B.X_PAN, 134, Ls[1], f"{-B.X_PAN:.0f}: centre of the scale's platform (A)"),
                          (B.X_CELL_MAST, -158, -45, f"{-B.X_CELL_MAST:.0f}: cell mast centre (B)"),
                          (B.GUY_X, -182, B.POST_Y - 30, f"{-B.GUY_X:.0f}: guy anchor (optional)")):
        witness(ax, x, y0, y)
        dim_h(ax, y, x, 0, lab)
    ax.annotate("", (-62, 0), (-62, B.POST_Y), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(-66, B.POST_Y / 2, f"{-B.POST_Y:.0f}", ha="right", va="center", fontsize=8)
    ax.annotate("", (bd["x1"] - 5, 212), (bd["x1"] - 60, 212), arrowprops=dict(arrowstyle="-|>", lw=1.5))
    ax.text(bd["x1"] - 66, 212, "N", ha="right", va="center", fontsize=11, fontweight="bold")
    ax.text(bd["x0"], -214, "Draw the centreline, mark the arm axis 220 mm from the north edge, then measure "
            "every other mark from the arm axis.\nStand each part on its mark and screw it down through its own "
            "holes (in slots, start in the middle).", fontsize=9, va="top")
    ax.set_xlim(bd["x0"] - 40, bd["x1"] + 40)
    ax.set_ylim(-240, 226)
    ax.set_aspect("equal")
    ax.set_title(f"Board layout from above, {bd['x1'] - bd['x0']:.0f} \u00d7 {bd['y1'] - bd['y0']:.0f} mm "
                 "(north to the right; the post is 70 mm east of the arm)", fontsize=11)
    ax.set_xlabel("mm north of the arm axis")
    ax.set_ylabel("mm west of the centreline")
    ax.grid(True, alpha=0.2)
    plt.tight_layout()
    out = os.path.join(G.ROOT, "board_layout.png")
    plt.savefig(out, dpi=130)
    plt.close(fig)
    print("wrote", out)


def main():
    fig, (a, b) = plt.subplots(1, 2, figsize=(15, 7.6), gridspec_kw=dict(width_ratios=[2.25, 1]))
    side(a)
    front(b)
    fig.suptitle("Pendulum thrust stand v1: post beside the arm, link on the thrust line, bell crank onto a "
                 "0.1 g pocket scale (mm)")
    plt.tight_layout()
    out = os.path.join(G.ROOT, "diagram.png")
    plt.savefig(out, dpi=160)
    plt.close(fig)
    print("wrote", out)
    cut_guide()
    board_layout()


if __name__ == "__main__":
    main()
