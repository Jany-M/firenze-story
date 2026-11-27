"""Stazione Leopolda – Florence's first railway terminus (v1).

Run:  python pipeline/47_moderni.py ; blender -b --python blender/scripts/build_leopolda.py → web/public/models/landmarks/leopolda.glb
Frame: a along the head of the building towards Porta al Prato (OSM way 269666091), o inwards along the train shed.
Measured (LiDAR 2023 DSM; ground 4.2 m scene): a long hall ≈155 × 43 m, its roof ≈10 m above the ground, the head ≈8 m.
History: the terminus of the Leopolda railway to Livorno, by Enrico Presenti for Grand Duke Leopold II, opened 2 June 1848
(Museo Galileo); passenger trains moved to the more central station after the link of 24 April 1860 (en.wikipedia,
Pisa–Florence railway); then the 1861 National Exhibition, workshops, today an events hall (feelflorence.it). Shown from 1848.
The head's arches are drawn plainly (*inferred* from the photograph of 1861 reproduced by getbacklauretta.com).
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from landmark_detail import *
from landmark_church import Site, extra_materials
K.reset()
MAT["plaster"] = material("plaster_leopolda", None, (0.86, 0.8, 0.68), 0.9)
MAT["serena"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)
extra_materials()
NOW = K.NOW
S = Site("leopolda", "moderni"); G = S.G; L = S.L
F = S.front()
Y = 1848; P = f"stazione_leopolda@{Y}-{NOW}"
def phase(a, o, k): return ("stazione_leopolda", Y)
def detail(part): return {"roof": "hip", "windows": True, "mat": "plaster"}
print("massing", S.raster(phase, detail=detail))
n = 7; w = L / n
for i in range(n):                                                          # the head: a row of arched openings
    uc = (i + 0.5) * w
    arch_fill(P, "dark", F, uc - w * 0.3, uc + w * 0.3, G + 0.2, G + 5.2, n=0.04)
    ring(P, "serena", F, uc, G + 5.2 - w * 0.3, w * 0.3, w * 0.3 + 0.3, 0.04, 0.2, seg=10)
pbox(bm_for(P, "serena"), F, -0.2, L + 0.2, G + 6.4, G + 6.8, 0, 0.35)
K.export("leopolda")
