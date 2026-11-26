"""Map of the circles of walls (docs/materials/maps/circles-of-walls.jpg), drawn from blender/data/walls.json (step 40)
on a hillshade of the app's terrain, with the Arno from river.json. Needs matplotlib (not in the base requirements).
"""
import os, json, math
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
D = json.load(open(os.path.join(ROOT, "blender", "data", "walls.json"), encoding="utf-8"))
m = json.load(open(os.path.join(ROOT, "web", "public", "data", "meta.json")))["terrain"]; n, st = m["n"], m["step"]
T = np.fromfile(os.path.join(ROOT, "web", "public", "data", "terrain.f32"), dtype=np.float32).reshape(n, n); half = (n - 1) * st / 2
R = json.load(open(os.path.join(ROOT, "web", "public", "data", "river.json")))["axis"]
X0, X1, Z0, Z1 = -1650, 1550, -1500, 1420

gy, gx = np.gradient(T, st); az, alt = math.radians(315), math.radians(40)
shade = np.sin(alt) + np.cos(alt) * (np.cos(az) * -gx + np.sin(az) * gy) / np.sqrt(1 + gx ** 2 + gy ** 2)
shade = (shade - shade.min()) / (np.ptp(shade) or 1)
fig, ax = plt.subplots(figsize=(13, 12), dpi=110); fig.patch.set_facecolor("#fbf8f2")
ax.imshow(shade, cmap="Greys_r", extent=(-half, half, half, -half), vmin=-0.6, vmax=1.15, alpha=0.55, interpolation="bilinear")
ax.contour(np.linspace(-half, half, n), np.linspace(-half, half, n), T, levels=np.arange(10, 200, 10), colors="#b9ae9c", linewidths=0.35, alpha=0.7)
r = [p for p in R if X0 - 200 < p[0] < X1 + 200]
ax.add_patch(Polygon([(p[0], p[3]) for p in r] + [(p[0], p[4]) for p in r[::-1]], closed=True, fc="#9fc3d6", ec="#6e9bb3", lw=0.8, zorder=2))

STYLE = {  # circle → colour, label
    "roman": ("#7b2d26", "Roman Florentia (1st c. BC → 9th c.)"), "carol": ("#a05a2c", "Carolingian circle (9th c. → 1078)"),
    "matil": ("#c48a1d", "Matildine circle (1078 → 1172)"), "first": ("#3f7f4f", "First communal circle (1172 → 1284)"),
    "ext": ("#58a06a", "its 1260 extension in Oltrarno"), "sixth": ("#c8102e", "Sixth circle (1284–1333): standing today"),
    "gone": ("#c8102e", "Sixth circle: pulled down 1865–70 or earlier"),
}
def circle(w):
    if w["kind"] != "early": return "sixth" if w["to"] > 9000 else "gone"
    f, t = w["from"], w["to"]
    if f < 100: return "roman"
    if f < 1000: return "carol"
    if t <= 1172: return "matil"
    if f == 1260: return "ext"
    return "first"
seen = set()
for w in sorted(D["walls"], key=lambda w: w["kind"] != "early"):
    c = circle(w); col, lab = STYLE[c]; P = np.array([p[:2] for p in w["pts"]])
    ax.plot(P[:, 0], P[:, 1], color=col, lw=3.2 if c in ("sixth", "gone") else 2.2, ls="--" if c == "gone" else "-",
            solid_capstyle="round", zorder=5 if c in ("sixth", "gone") else 4, label=None if c in seen else lab)
    seen.add(c)
    if w["kind"] == "wall":            # towers every 115 m (as in the model), not by the gates
        d, nxt, P2 = 0.0, 57.0, P
        for a, b in zip(P2, P2[1:]):
            l = float(np.hypot(*(b - a)))
            while d + l > nxt:
                q = a + (b - a) * (nxt - d) / l; nxt += 115
                if min(math.dist(q, g["c"]) for g in D["gates"]) > 40: ax.add_patch(Rectangle(q - 9, 18, 18, fc=col, ec="white", lw=0.4, zorder=6))
            d += l
for p in D["polys"]:
    P = [q[:2] for q in p["pts"]]
    ax.add_patch(Polygon(P, closed=True, fc="#c8102e22" if p["id"] != "fortezza" else "#8a5a4433", ec="#8a5a44", lw=1.2, zorder=4,
                         label="Bastions (1531–54) and Fortezza da Basso (1534)" if p["id"] == "fortezza" else None))
LBL = {"romana": "Porta Romana", "frediano": "Porta San Frediano", "croce": "Porta alla Croce", "prato": "Porta al Prato",
       "gallo": "Porta San Gallo", "niccolo": "Torre San Niccolò", "giorgio": "Porta San Giorgio", "zecca": "Torre della Zecca",
       "serpe": "Torre della Serpe", "rosa": "Santa Rosa", "faenza": "Porta a Faenza", "arco": "Arco di Trionfo",
       "pinti": "Porta a Pinti †1866", "giustizia": "Porta alla Giustizia †1530", "miniato": "Porta San Miniato", "verzaia": ""}
OFF = {"zecca": (20, 30), "giustizia": (25, -40), "serpe": (-30, 40), "rosa": (25, 20), "arco": (25, -30), "faenza": (20, 30), "gallo": (25, 25)}
for g in D["gates"]:
    x, z = g["c"]; gone = g["key"] in ("pinti", "giustizia")
    ax.plot(x, z, marker="s", ms=8, mfc="white" if gone else "#c8102e", mec="#7a0a1c", mew=1.4, zorder=8)
    if LBL[g["key"]]:
        dx, dz = OFF.get(g["key"], (22, 0))
        ax.text(x + dx, z + dz, LBL[g["key"]], fontsize=8.5, color="#3a1a14", zorder=9, va="center",
                bbox=dict(boxstyle="round,pad=0.15", fc="#fbf8f2cc", ec="none"))
ax.plot([], [], marker="s", ms=7, ls="", mfc="#c8102e", mec="#7a0a1c", label="Gate or tower standing today")
ax.plot([], [], marker="s", ms=7, ls="", mfc="white", mec="#7a0a1c", label="Gate demolished")
ax.add_patch(Rectangle((-1550, 1300), 500, 22, fc="#3a1a14")); ax.text(-1300, 1270, "500 m", ha="center", fontsize=9)
ax.annotate("N", xy=(1430, -1380), xytext=(1430, -1250), ha="center", fontsize=12, arrowprops=dict(arrowstyle="-|>", color="#3a1a14"))
ax.set_xlim(X0, X1); ax.set_ylim(Z1, Z0); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("The circles of walls of Florence", fontsize=20, family="serif", color="#9e0b23", pad=12)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=3, fontsize=8.5, frameon=False)
fig.text(0.5, 0.01, "Firenze Story · lines: OpenHistoricalMap (CC0) and OpenStreetMap contributors (ODbL) · terrain: LiDAR 2023, Regione Toscana / Comune di Firenze · CC BY-SA 4.0",
         ha="center", fontsize=8, color="#555")
out = os.path.join(ROOT, "docs", "materials", "maps"); os.makedirs(out, exist_ok=True)
fig.savefig(os.path.join(out, "circles-of-walls.jpg"), dpi=110, bbox_inches="tight", facecolor=fig.get_facecolor(), pil_kwargs={"quality": 88})
print("saved", os.path.join(out, "circles-of-walls.jpg"))
