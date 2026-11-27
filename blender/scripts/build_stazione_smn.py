"""Stazione di Santa Maria Novella – the passenger building of Michelucci and the Gruppo Toscano (v1).

Run:  python pipeline/47_moderni.py   (once: outlines, ground, DSM raster → blender/data/moderni.json)
      blender -b --python blender/scripts/build_stazione_smn.py  →  web/public/models/landmarks/stazione_smn.glb
Frame: a along the front on Piazza della Stazione from its west corner (OSM relation 3324492), o inwards (north-west).
Measured (LiDAR 2023 DSM; ground 8.3 m scene): a low block along the front ≈6 m high (the entrance gallery), the ticket hall
behind it ≈15 m, the wings along the platforms; front ≈71 m.
From descriptions and photographs: a long, low building of pietra forte, kept horizontal so as not to clash with Santa Maria
Novella; over the entrance the glazed "cascade" that runs from the hall's roof down to the gallery (visittuscany.com,
en.wikipedia). Built 1933–35 after the competition of 1932 won by the Gruppo Toscano (Baroni, Berardi, Gamberini, Guarnieri,
Lusanna, led by Giovanni Michelucci); inaugurated 30 October 1935 (area-arch.it, arttrav.com). Shown from 1935.
The Maria Antonia station of 1848 that stood nearer the church before it, and Michelucci's Palazzina Reale, are not drawn.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from mathutils import Vector
from landmark_detail import *
from landmark_church import Site, extra_materials
K.reset()
MAT["plaster"] = material("pietra_forte_smn", "pietra_forte", (0.6, 0.54, 0.45), 0.85, 0.18, tint=(2.5, 2.45, 2.3))
MAT["glass"] = material("station_glass", None, (0.3, 0.38, 0.42), 0.12, metal=0.2)
MAT["metal"] = material("steel_dark", None, (0.15, 0.15, 0.16), 0.5, metal=0.6)
MAT["roof_m"] = material("flat_roof_smn", None, (0.5, 0.49, 0.46), 0.9)                   # flat roofs, not tiles
MAT["serena"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)
extra_materials()
NOW = K.NOW
S = Site("smn", "moderni"); G = S.G; L = S.L
F = S.front()
Y = 1935; P = f"stazione@{Y}-{NOW}"
def phase(a, o, k): return ("stazione", Y)
def detail(part): return {"roof": "flat", "windows": False, "mat": "plaster"}
print("massing", S.raster(phase, detail=detail, slope=0.0, windows=False))   # flat roofs, no punched windows
# the entrance gallery along the front: a deep canopy on slender piers, glazed doors behind
pbox(bm_for(P, "plaster"), F, 2.0, L - 2.0, G + 5.6, G + 6.3, 0, 4.5)
for k in range(13):
    u = 4.0 + k * (L - 8.0) / 12
    pbox(bm_for(P, "metal"), F, u - 0.18, u + 0.18, G, G + 5.6, 3.9, 4.3)
poly(bm_for(P, "glass"), [F.p(3.0, G + 0.2, 0.05), F.p(L - 3.0, G + 0.2, 0.05), F.p(L - 3.0, G + 5.5, 0.05), F.p(3.0, G + 5.5, 0.05)])
# the glazed cascade over the entrance: steps of glass from the hall's roof down to the gallery
c0, c1 = L / 2 - 11.0, L / 2 + 11.0
for k in range(6):
    o0, o1 = 2.0 + k * 1.7, 2.0 + (k + 1) * 1.7; h0, h1 = G + 6.3 + k * 1.45, G + 6.3 + (k + 1) * 1.45
    q = [S.W(c0, o0, h0), S.W(c1, o0, h0), S.W(c1, o0, h1), S.W(c0, o0, h1)]; poly(bm_for(P, "glass"), q[::-1])
    q = [S.W(c0, o0, h1), S.W(c1, o0, h1), S.W(c1, o1, h1), S.W(c0, o1, h1)]; poly(bm_for(P, "glass"), q[::-1])
    for u in [c0 + (c1 - c0) * j / 10 for j in range(11)]:
        pbox(bm_for(P, "metal"), Frame(S.W(u, o0, 0), S.NO, S.TA), 0, o1 - o0, h0, h1 + 0.05, -0.05, 0.05)
K.export("stazione_smn")
