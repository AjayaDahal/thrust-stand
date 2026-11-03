#!/usr/bin/env python3
"""Side-view layout diagram for the pendulum thrust stand.
x = thrust direction (north, +x), z = up. Board top = z 0.
All dimensions in mm. Drawn from the same numbers as build_thrust_stand.py.
Note: the arm is drawn 28 mm offset so it reads separately from the post;
in reality it hangs in line with the post.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

fig, ax = plt.subplots(figsize=(13.5, 7.5))
OX = 28  # diagram-only offset for the hanging arm assembly

# --- board (18 mm plywood/MDF, top at z=0)
ax.add_patch(Rectangle((-500, -18), 700, 18, facecolor="#d8c9a3", edgecolor="k", lw=1))
ax.text(-150, -12, "board 700 x 400 x 18 (plywood / MDF)", ha="center", fontsize=9)

# --- post foot + post
ax.add_patch(Rectangle((-50, 0), 100, 50, facecolor="#9bb8d3", edgecolor="k", lw=1))
ax.text(0, 25, "post_foot", ha="center", fontsize=8)
ax.add_patch(Rectangle((-12.7, 0), 25.4, 635, facecolor="#cfe0ee", edgecolor="k", lw=1))
ax.text(-40, 150, "post\n25.4 mm tube\n(cut ~635)", ha="right", fontsize=8, va="center")

# --- pivot clevis (socket block + cheeks)
ax.add_patch(Rectangle((-35, 595), 70, 55, facecolor="#9bb8d3", edgecolor="k", lw=1))
ax.add_patch(Rectangle((-30, 650), 60, 75, facecolor="#b5cde2", edgecolor="k", lw=1))
ax.text(40, 615, "pivot_clevis (cheeks flank the hub)", ha="left", fontsize=8, va="center")

# --- arm hub + arm tube + motor clamp (offset OX for readability)
ax.add_patch(Rectangle((-30 + OX, 652), 60, 70, facecolor="#f2c879", edgecolor="k", lw=1))
ax.text(OX, 732, "arm_hub", ha="center", fontsize=8)
ax.add_patch(Rectangle((-12.7 + OX, 250), 25.4, 402, facecolor="#fde8b8", edgecolor="k", lw=1))
ax.text(48 + OX, 450, "arm\n25.4 mm tube\n(cut ~500)", ha="left", fontsize=8, va="center")
ax.add_patch(Rectangle((-30 + OX, 190), 60, 60, facecolor="#f2c879", edgecolor="k", lw=1))
ax.text(OX, 258, "motor_clamp", ha="center", fontsize=8)

# --- pivot axle dot + label
ax.plot(OX, 700, "ko", ms=6)
ax.text(60 + OX, 700, "pivot axle, 14.66 mm tube (cut ~110)", ha="left",
        fontsize=8, va="center")

# --- motor + prop (10 in prop shown = worst case for clearance)
ax.add_patch(Rectangle((58 + OX, 200), 32, 40, facecolor="#d98c2b", edgecolor="k", lw=1))
ax.text(74 + OX, 220, "motor", ha="center", fontsize=8)
ax.plot([90 + OX, 103 + OX], [220, 220], "k-", lw=1.5)
ax.plot([103 + OX, 103 + OX], [80, 360], "k-", lw=3)
ax.text(110 + OX, 100, "prop (10 in)", ha="left", fontsize=8)

# --- scale mast + platform + scale + link
ax.add_patch(Rectangle((-290, 0), 105, 8, facecolor="#9bb8d3", edgecolor="k", lw=1))
ax.add_patch(Rectangle((-245, 8), 30, 190, facecolor="#b5cde2", edgecolor="k", lw=1))
ax.add_patch(Rectangle((-290, 8), 47, 132, facecolor="#9bb8d3", edgecolor="k", lw=1, alpha=.45))
ax.add_patch(Rectangle((-260, 198), 60, 6, facecolor="#9bb8d3", edgecolor="k", lw=1))
ax.add_patch(Rectangle((-300, 204), 140, 5, facecolor="#b5cde2", edgecolor="k", lw=1))
ax.text(-230, 100, "scale_mast", fontsize=8, rotation=90, va="center")
ax.text(-302, 206, "scale_platform", fontsize=8, ha="right", va="center")
ax.add_patch(Rectangle((-302, 209), 130, 25, facecolor="#444444", edgecolor="k", lw=1))
ax.text(-237, 221, "luggage scale", color="white", ha="center", fontsize=8)
ax.plot([-172, -172], [221, 221], "ko", ms=4)
ax.text(-172, 242, "hook", ha="center", fontsize=8)
ax.plot([-42, -172], [220, 221], "r-", lw=2)
ax.text(-107, 232, "scale_link", color="r", ha="center", fontsize=8)
ax.text(-230, 260, "scale line offset 30 mm sideways\n(out of this plane) to clear the brace",
        ha="center", fontsize=8, style="italic")

# --- brace (45 deg) + clamp + foot
ax.add_patch(Rectangle((-35, 310), 70, 80, facecolor="#a8c3a0", edgecolor="k", lw=1))
ax.text(-40, 350, "brace_clamp", ha="right", fontsize=8, va="center")
ax.plot([0, -350], [350, 0], "g-", lw=3)
ax.text(-450, 85, "brace: 14.66 mm tube, 45°",
        color="g", ha="center", fontsize=8)
ax.add_patch(Rectangle((-395, 0), 90, 58, facecolor="#a8c3a0", edgecolor="k", lw=1))
ax.text(-350, 29, "brace_foot", ha="center", fontsize=8)

# --- dimension lines
def dim_v(x, z0, z1, label):
    ax.plot([x - 6, x + 6], [z0, z0], "k-", lw=0.8)
    ax.plot([x - 6, x + 6], [z1, z1], "k-", lw=0.8)
    ax.plot([x, x], [z0, z1], "k-", lw=0.8)
    ax.text(x + 10, (z0 + z1) / 2, label, fontsize=8, va="center")

dim_v(170, 220, 700, "arm 480 (pivot to shaft)")
dim_v(200, 0, 220, "shaft 220 above board")
dim_v(260, 0, 700, "pivot 700 above board")
ax.plot([-500, 200], [0, 0], "k--", lw=0.7)
ax.text(-150, -45, "Note: arm drawn 28 mm offset for clarity — in reality it hangs in line with the post.",
        ha="center", fontsize=8, style="italic")

ax.set_xlim(-520, 390)
ax.set_ylim(-60, 780)
ax.set_aspect("equal")
ax.set_xlabel("x  (thrust direction, mm)")
ax.set_ylabel("z  (height above board top, mm)")
ax.set_title("Pendulum thrust stand — side view (part sizes not to scale)")
ax.grid(True, alpha=0.25)
plt.tight_layout()
plt.savefig("diagram.png", dpi=200)
print("wrote diagram.png")
