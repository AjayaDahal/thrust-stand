#!/usr/bin/env python3
"""Dimensioned drawing of the v1 stand: side view (x-z) and front view (y-z), from the same numbers
as build_thrust_stand.py. Writes diagram.png. Unlike v0's diagram, nothing is drawn displaced:
the arm and the post really are 70 mm apart (front view).

Run: C:/Users/ajayad/venvs/vtol-venv/Scripts/python.exe scripts/make_diagram.py
"""
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
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


def main():
    fig, (a, b) = plt.subplots(1, 2, figsize=(15, 7.6), gridspec_kw=dict(width_ratios=[2.25, 1]))
    side(a)
    front(b)
    fig.suptitle("Pendulum thrust stand v1: post beside the arm, link on the thrust line, bell crank onto a "
                 "0.1 g pocket scale (mm)")
    plt.tight_layout()
    out = os.path.join(G.ROOT, "diagram.png")
    plt.savefig(out, dpi=160)
    print("wrote", out)


if __name__ == "__main__":
    main()
