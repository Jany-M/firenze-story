"""Piazza Santa Maria Novella: the two obelisks of the Corsa dei Cocchi, the lawns and the benches (absolute scene coordinates).

Obelisks (Wikipedia "Obelisks of the Corsa dei Cocchi"; photographs: Francesco Bini 2021, Zairon 2023, Txllxt 2010, Sommer
c. 1870): designed by Ammannati 1570, brought from the quarry 1572, set up in 1608 for the wedding of Cosimo II; until then
(from 1563) two wooden pyramids marked the turning posts of the chariot race on the eve of San Giovanni. Each: a low base of
two steps, a pedestal of pietra forte with polished breccia panels (renewed in the 1790s, now red Levanto), four bronze
tortoises at the corners carrying the veined marble shaft, a bronze Florentine lily on top (added in the 1790s).
Height ≈10 m (LiDAR 2023: north obelisk 10.0 m over the ground).
Lawns: eight beds in two point-symmetric ovals, traced from the 2017 orthophoto (pipeline/48_piazza_smn.py), with a low
clipped hedge along the edge; not in the 19th-century photographs (bare square) – laid out in the 20th century, year *inferred*.
Benches: pietra serena benches on the paving round the lawns (*inferred*).
Run: blender -b --factory-startup --python blender/scripts/build_piazza_smn.py
"""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from mathutils import Vector
from landmark_detail import *
from landmark_church import extra_materials, bed, bench, Vs
K.reset()
MAT["serena"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)
MAT["forte"] = material("pietra_forte", "pietra_forte", (0.66, 0.56, 0.42), 0.85, 0.32, tint=(3.0, 2.85, 2.55))
MAT["levanto"] = material("marble_levanto_red", None, (0.42, 0.22, 0.2), 0.35)
MAT["veined"] = material("marble_veined", None, (0.86, 0.84, 0.8), 0.45)
MAT["hedge"] = material("box_hedge", None, (0.13, 0.26, 0.11), 0.95)
MAT["wood"] = material("wood_painted", None, (0.55, 0.43, 0.3), 0.85)
extra_materials()
NOW = K.NOW
D = json.load(open(os.path.join(ROOT, "blender", "data", "piazza_smn.json"), encoding="utf-8"))
ux, uz = D["axis"]; AXIS = Vector((ux, -uz, 0)).normalized(); NRM = Vector((-AXIS.y, AXIS.x, 0))
LAWNS = "1930"                                            # 20th century, year inferred

def frustum(part, mat, F, w0, w1, z0, z1):
    """Square frustum in frame F (u, n centred on 0), from half-width w0 at z0 to w1 at z1."""
    bm = bm_for(part, mat)
    lo = [F.p(a * w0, z0, b * w0) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    hi = [F.p(a * w1, z1, b * w1) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    for i in range(4): poly(bm, [lo[i], lo[(i + 1) % 4], hi[(i + 1) % 4], hi[i]])
    poly(bm, hi); poly(bm, lo[::-1])

def sq(part, mat, F, w, z0, z1): box(bm_for(part, mat), F, -w, w, z0, z1, -w, w)

def obelisk(c, g):
    P = f"obelischi@1608-{NOW}"
    F = Frame(Vs(*c) - Vector((0, 0, 0)), AXIS, NRM)
    sq(P, "serena", F, 1.85, g - 0.1, g + 0.16); sq(P, "serena", F, 1.45, g + 0.16, g + 0.32)        # two steps
    sq(P, "forte", F, 0.9, g + 0.32, g + 0.58)                                                       # base moulding
    sq(P, "forte", F, 0.76, g + 0.58, g + 2.05)                                                      # pedestal
    sq(P, "forte", F, 0.88, g + 2.05, g + 2.25)                                                      # cap
    for k in range(4):                                                                               # breccia / Levanto panels
        a = k * math.pi / 2; d = AXIS * math.cos(a) + NRM * math.sin(a); t = Vector((-d.y, d.x, 0))
        Fp = Frame(Vs(*c) + d * 0.76, t, d); box(bm_for(P, "levanto"), Fp, -0.42, 0.42, g + 0.85, g + 1.85, 0, 0.03, back=False)
    for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1)):                                                # the four tortoises
        tc = F.p(a * 0.52, 0, b * 0.52); tc.z = 0
        cone(P.replace("obelischi", "tartarughe"), "bronze", tc, 0.3, 0.12, g + 2.25, g + 2.47, seg=10)
        dd = (AXIS * a + NRM * b).normalized()
        cylinder(P.replace("obelischi", "tartarughe"), "bronze", tc + dd * 0.3, 0.07, g + 2.27, g + 2.37, seg=6)   # head
    frustum(P, "veined", F, 0.5, 0.17, g + 2.47, g + 9.0)                                            # the shaft
    frustum(P, "veined", F, 0.19, 0.01, g + 9.0, g + 9.28)                                           # pyramidion
    L = f"giglio@1792-{NOW}"                                                                         # the bronze lily
    cylinder(L, "bronze", Vs(*c), 0.04, g + 9.28, g + 9.62, seg=6)
    for k in (-1, 1):
        Fl = Frame(Vs(*c), AXIS, NRM)
        box(bm_for(L, "bronze"), Fl, k * 0.08, k * 0.24, g + 9.45, g + 9.8, -0.03, 0.03)            # side petals
    cone(L, "bronze", Vs(*c), 0.08, 0.0, g + 9.6, g + 10.0, seg=4)                                   # middle petal
    box(bm_for(L, "bronze"), Frame(Vs(*c), AXIS, NRM), -0.2, 0.2, g + 9.42, g + 9.48, -0.05, 0.05)  # the band

def wooden_post(c, g):                                                                              # 1563–1608: the race's turning posts
    P = "mete_di_legno@1563-1607"; F = Frame(Vs(*c), AXIS, NRM)
    sq(P, "wood", F, 1.2, g - 0.1, g + 0.8); frustum(P, "wood", F, 0.9, 0.05, g + 0.8, g + 8.0)

for o in D["obelisks"]:
    obelisk(o["c"], o["ground"]); wooden_post(o["c"], o["ground"])

def hedge(part, pts, g, w=0.35, h=0.45):
    P = pts[:-1] if pts[0] == pts[-1] else pts
    if sum(P[i - 1][0] * P[i][1] - P[i][0] * P[i - 1][1] for i in range(len(P))) < 0: P = P[::-1]
    cx = sum(p[0] for p in P) / len(P); cz = sum(p[1] for p in P) / len(P)
    for (x0, z0), (x1, z1) in zip(P, P[1:] + P[:1]):
        L = math.hypot(x1 - x0, z1 - z0)
        if L < 0.2: continue
        ux_, uz_ = (x1 - x0) / L, (z1 - z0) / L
        n = Vector((uz_, ux_, 0))                                   # one of the two sides; turn it to the inside
        mid = Vs((x0 + x1) / 2, (z0 + z1) / 2)
        if (Vs(cx, cz) - mid).dot(n) < 0: n = -n
        F = Frame(Vs(x0, z0), Vector((ux_, -uz_, 0)), n)
        box(bm_for(part, "hedge"), F, 0, L, g + 0.12, g + 0.12 + h, 0.05, 0.05 + w)

for L in D["lawns"]:
    bed(f"prati@{LAWNS}-{NOW}", L["pts"], L["ground"] + 0.02, curb=0.12, rail=False)
    hedge(f"prati@{LAWNS}-{NOW}", L["pts"], L["ground"] + 0.02)
for b in D["benches"]:
    bench(f"panchine@{LAWNS}-{NOW}", b["c"], b["ang"], b["ground"], L=3.0)
K.export("piazza_smn")
