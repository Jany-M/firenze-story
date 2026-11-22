"""Giotto's bell tower (Campanile di Santa Maria del Fiore) – measured, dated model (v1).

Run:  blender -b --python blender/scripts/build_campanile.py   →  web/public/models/landmarks/campanile.glb
Frame: origin = centre of the tower at ground level (LiDAR 2023: scene x 38.3 / z −116.7), X east, Y north, Z up.
Measured (DSM 0.5 m): 15 m square at the crown, top platform 85–86 m above the piazza. Levels and decoration follow
photographs and the standard literature (Giotto 1334–37, Andrea Pisano 1337–48, Francesco Talenti 1350–59):
  0–14 m    two bands of relief panels: hexagons, then lozenges on blue majolica ground
  14–33 m   niches with the statues of prophets and sibyls, then a blind panelled storey
  33–59 m   two storeys with two Gothic bifore per side
  59–77 m   one tall trifora per side
  77–86 m   panelled frieze, crowning cornice on corbels, parapet (the planned spire was never built)
Octagonal corner buttresses run the full height. The tower was clad as it rose: no bare-brick phase.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
K.reset()
MAT["blue"] = material("majolica_blue", None, (0.17, 0.27, 0.52), 0.35)

S = 6.85                     # half side of the wall faces (buttresses reach 7.25)
LEVELS = [                   # (part, from year, z0, z1)
    ("campanile_giotto", 1337, 0.0, 14.0),
    ("campanile_pisano", 1348, 14.0, 33.0),
    ("campanile_talenti_1", 1352, 33.0, 46.0),
    ("campanile_talenti_2", 1355, 46.0, 59.0),
    ("campanile_talenti_3", 1359, 59.0, 82.5),
]
def faces():
    for k in (0, 2, 4, 6):
        n = oct_dir(k); t = Vector((-n.y, n.x, 0))
        yield Frame(n * S - t * S, t, n), 2 * S

def band(part, F, W, z):
    box(bm_for(part, "white"), F, 0, W, z - 0.35, z + 0.35, 0, 0.35)
    box(bm_for(part, "green"), F, 0, W, z - 0.12, z + 0.12, 0, 0.4)

def hexagon(part, F, cu, cv, r):
    poly(bm_for(part, "white"), [F.p(cu + r * math.cos(a), cv + r * math.sin(a), 0.08) for a in [math.pi / 6 + i * math.pi / 3 for i in range(6)]])
    poly(bm_for(part, "red"), [F.p(cu + r * 0.78 * math.cos(a), cv + r * 0.78 * math.sin(a), 0.1) for a in [math.pi / 6 + i * math.pi / 3 for i in range(6)]])
    poly(bm_for(part, "white"), [F.p(cu + r * 0.62 * math.cos(a), cv + r * 0.62 * math.sin(a), 0.12) for a in [math.pi / 6 + i * math.pi / 3 for i in range(6)]])

def lozenge(part, F, cu, cv, w, h):
    poly(bm_for(part, "blue"), [F.p(cu, cv - h, 0.08), F.p(cu + w, cv, 0.08), F.p(cu, cv + h, 0.08), F.p(cu - w, cv, 0.08)])
    poly(bm_for(part, "white"), [F.p(cu, cv - h * 0.6, 0.11), F.p(cu + w * 0.6, cv, 0.11), F.p(cu, cv + h * 0.6, 0.11), F.p(cu - w * 0.6, cv, 0.11)])

def level(part, z0, z1, kind):
    for F, W in faces():
        wall(part, F, 0, W, z0, z1, 1.6)
        if kind == "giotto":
            box(bm_for(part, "white"), F, 0, W, 0, 1.0, 0, 0.5)                                   # plinth
            panels(part, F, 1.2, W - 1.2, 1.0, 7.4, 7, 1, accent=lambda i, j: True)
            for i in range(7): hexagon(part, F, 1.2 + (i + 0.5) * (W - 2.4) / 7, 4.2, 0.78)
            band(part, F, W, 7.6)
            panels(part, F, 1.2, W - 1.2, 7.9, 13.6, 7, 1)
            for i in range(7): lozenge(part, F, 1.2 + (i + 0.5) * (W - 2.4) / 7, 10.75, 0.62, 1.15)
        elif kind == "pisano":
            band(part, F, W, z0 + 0.3)
            for i in range(4):                                                                        # niches with statues
                u = 1.6 + (i + 0.5) * (W - 3.2) / 4
                opening(part, F, u - 0.75, u + 0.75, 16.0, 22.4, depth=0.5, frame=0.3, pointed=True, fill="dark", frame_mat="white")
                box(bm_for(part, "white"), F, u - 0.32, u + 0.32, 16.2, 20.4, 0.08, 0.5)
            panels(part, F, 1.2, W - 1.2, 14.6, 23.6, 8, 2, accent=lambda i, j: j == 0 and i % 2 == 1)
            band(part, F, W, 24.0)
            panels(part, F, 1.2, W - 1.2, 24.4, 32.6, 6, 2, accent=lambda i, j: (i + j) % 2 == 0)
        elif kind == "bifore":
            band(part, F, W, z0 + 0.3)
            panels(part, F, 1.2, W - 1.2, z0 + 0.7, z1 - 0.7, 6, 3, accent=lambda i, j: j == 2 and i in (0, 5))
            for u in (W * 0.3, W * 0.7):
                opening(part, F, u - 1.25, u + 1.25, z0 + 2.2, z1 - 1.8, frame=0.45, mullion=True)
                pinnacle(part, tuple(F.p(u, 0, 0.5)[:2]), z1 - 1.5, 1.6, 0.35)
        elif kind == "trifora":
            band(part, F, W, z0 + 0.3)
            panels(part, F, 1.2, W - 1.2, z0 + 0.7, 76.6, 6, 4, accent=lambda i, j: j == 3 and i in (0, 5))
            u0, u1 = W / 2 - 2.5, W / 2 + 2.5
            opening(part, F, u0, u1, z0 + 2.0, 75.5, frame=0.6)
            for m in (1 / 3, 2 / 3):                                                                   # two mullions
                u = u0 + (u1 - u0) * m; box(bm_for(part, "white"), F, u - 0.13, u + 0.13, z0 + 2.0, 72.6, 0, 0.12)
            for m in (1 / 6, 1 / 2, 5 / 6):
                poly(bm_for(part, "white"), [F.p(u0 + (u1 - u0) * m + 0.45 * math.cos(a), 73.6 + 0.45 * math.sin(a), 0.1) for a in [i / 12 * 2 * math.pi for i in range(12)]])
            band(part, F, W, 77.0)
            panels(part, F, 1.2, W - 1.2, 77.4, 81.8, 8, 1, accent=lambda i, j: i % 2 == 0)
            # crown: corbels, projecting cornice, parapet
            for i in range(14):
                u = 0.4 + i * (W - 0.8) / 13; box(bm_for(part, "white"), F, u - 0.18, u + 0.18, 81.8, 82.6, 0, 0.75)
            box(bm_for(part, "white"), F, -0.75, W + 0.75, 82.6, 83.4, 0, 0.8)
            box(bm_for(part, "green"), F, -0.75, W + 0.75, 83.4, 83.6, 0, 0.75)
            box(bm_for(part, "white"), F, -0.75, W + 0.75, 83.6, 84.4, 0, 0.8)
            box(bm_for(part, "white"), F, -0.55, W + 0.55, 84.4, 85.6, 0.45, 0.75)               # parapet
    # octagonal corner buttresses, banded at the storey lines
    for cx, cy in ((S, S), (-S, S), (-S, -S), (S, -S)):
        bm = bm_for(part, "white")
        bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.85, radius2=0.85, depth=z1 - z0,
                              matrix=Matrix.Translation((cx, cy, (z0 + z1) / 2)) @ Matrix.Rotation(math.pi / 8, 4, "Z"))
        for zb in (z0 + 0.3, z1 - 0.3):
            bmesh.ops.create_cone(bm_for(part, "green"), cap_ends=True, segments=8, radius1=0.9, radius2=0.9, depth=0.25,
                                  matrix=Matrix.Translation((cx, cy, zb)) @ Matrix.Rotation(math.pi / 8, 4, "Z"))
    if kind == "trifora":                                                                               # roof terrace
        wbox(bm_for(part, "lead"), -S, S, -S, S, 84.0, 84.3)

kinds = {"campanile_giotto": "giotto", "campanile_pisano": "pisano", "campanile_talenti_1": "bifore", "campanile_talenti_2": "bifore", "campanile_talenti_3": "trifora"}
for name, yr, z0, z1 in LEVELS:
    level(f"{name}@{yr}-{NOW}", z0, z1, kinds[name])
K.export("campanile")
