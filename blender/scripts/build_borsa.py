"""Palazzo della Borsa (Camera di Commercio), Lungarno Diaz (v1).

Run:  python pipeline/47_moderni.py borsa  (outline, ground, DSM raster → blender/data/moderni.json)
      blender -b --python blender/scripts/build_borsa.py  →  web/public/models/landmarks/borsa.glb
Frame: a along the front on the Lungarno Diaz from the west corner of OSM relation 1602101 (89 m), o inwards (north).
Measured (LiDAR 2023 DSM over the ground, in this frame): the block a 0..89, o 0..30, 16–18 m to the roof; a lower hall
a 60..76, o 9..19 (≈15 m, its glass roof); light wells (the OSM holes) a 36..53, o 5..23 and two small ones.
From photographs (Commons: Sailko 2007 and 2009, credited on the library page): a long neoclassical front of three storeys
in pale yellow plaster, stone window frames, a rusticated ground floor, a pronaos of Doric columns under a pediment in the
middle, a cornice and a low tiled roof.
History: built 1858–60 for Leopold II on the site of a tiratoio of the Arte della Lana, to Michelangelo Maiorfi's design
reworked by Emilio De Fabris, who replaced a rusticated portico with the columned pronaos and pediment; the Borsa's hall
fitted out 1931–33; seat of the Camera di Commercio (fi.camcom.gov.it, borsaitaliana.it, pietredirapolano.com).
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from landmark_detail import *
from landmark_church import Site, extra_materials
from landmark_volume import Vol, punched
from mathutils import Vector
K.reset()
MAT["plaster"] = material("plaster_borsa", None, (0.9, 0.82, 0.6), 0.85)
MAT["trav"] = material("travertine_borsa", None, (0.86, 0.82, 0.72), 0.75)
MAT["glass"] = material("window_glass", None, (0.08, 0.09, 0.11), 0.15)
MAT["skylight"] = material("glass_roof", None, (0.45, 0.55, 0.6), 0.1, metal=0.3)
extra_materials()
NOW = K.NOW
S = Site("borsa", "moderni"); G = S.G; V = Vol(S)
P = f"borsa@1860-{NOW}"
B0, EAVE, L, D = G - 1.5, 16.2, 88.6, 30.0
def H(z): return G + z
V.prism(P, "plaster", V.rect(0, L, 0, D), B0, H(EAVE), top_mat="roof")
V.hip(P, "roof", 0, L, 0, D, H(EAVE), H(EAVE + 2.6), over=0.8)
poly(bm_for(P, "skylight"), [V.W(37, 6, H(EAVE + 1.0)), V.W(52, 6, H(EAVE + 1.0)), V.W(52, 22, H(EAVE + 1.0)), V.W(37, 22, H(EAVE + 1.0))])
poly(bm_for(P, "skylight"), [V.W(60, 9, H(EAVE + 0.4)), V.W(76, 9, H(EAVE + 0.4)), V.W(76, 19, H(EAVE + 0.4)), V.W(60, 19, H(EAVE + 0.4))])
PC = (37.3, 51.3)                                               # the pronaos in the middle of the front
for F, Lf, p0, p1 in V.edges(V.rect(0, L, 0, D)):
    front = abs(p0[1]) < 0.1 and abs(p1[1]) < 0.1
    pbox(bm_for(P, "trav"), F, 0, Lf, B0, H(4.6), 0, 0.08)                                       # rusticated ground floor
    for v in range(1, 6): pbox(bm_for(P, "fortedk" if "fortedk" in MAT else "dark"), F, 0, Lf, H(v * 0.9) - 0.04, H(v * 0.9), 0.08, 0.09)
    pbox(bm_for(P, "trav"), F, -0.2, Lf + 0.2, H(4.6), H(5.0), 0, 0.3)                            # string courses
    pbox(bm_for(P, "trav"), F, -0.2, Lf + 0.2, H(10.3), H(10.6), 0, 0.2)
    pbox(bm_for(P, "trav"), F, -0.5, Lf + 0.5, H(EAVE - 0.9), H(EAVE), 0, 0.9)                  # cornice
    if front:
        segs = [(0.8, PC[0] - 1.2), (PC[1] + 1.2, Lf - 0.8)]
    else:
        segs = [(0.8, Lf - 0.8)]
    for (u0, u1) in segs:
        for (v0, v1, w, fr) in ((H(1.6), H(3.8), 1.3, 0.2), (H(6.0), H(9.2), 1.4, 0.25), (H(11.4), H(14.2), 1.3, 0.2)):
            us = punched(P, F, u0, u1, v0, v1, w, 4.1, fill="glass", frame="trav", fw=fr)
            if v0 > H(5):
                for u in us: pbox(bm_for(P, "trav"), F, u - w / 2 - 0.3, u + w / 2 + 0.3, v1 + fr, v1 + fr + 0.25, 0, 0.3)   # cornices over the windows
# the pronaos: four Doric columns between two antae, a deep porch, entablature and pediment over the cornice
Ff, Lf = V.frame(0, 0, L, 0, inside=(44, 15))
u0, u1 = PC; w = u1 - u0
poly(bm_for(P, "dark"), [Ff.p(u0, H(0.6), 0.02), Ff.p(u1, H(0.6), 0.02), Ff.p(u1, H(11.2), 0.02), Ff.p(u0, H(11.2), 0.02)])
for k in range(6):
    u = u0 + 0.6 + (w - 1.2) * k / 5
    if k in (0, 5): pbox(bm_for(P, "trav"), Ff, u - 0.6, u + 0.6, G, H(11.2), 0, 0.8)                     # antae
    else:
        cylinder(P, "trav", Ff.p(u, 0, 0.8), 0.55, H(0.9), H(10.6), seg=16)
        pbox(bm_for(P, "trav"), Ff, u - 0.75, u + 0.75, H(10.6), H(11.2), 0.05, 1.55)                  # capitals
pbox(bm_for(P, "trav"), Ff, u0 - 0.3, u1 + 0.3, H(11.2), H(13.2), 0, 1.6)                              # entablature
for k in range(int(w / 1.1)):
    u = u0 + 0.4 + k * 1.1; pbox(bm_for(P, "trav"), Ff, u, u + 0.35, H(11.9), H(12.7), 1.6, 1.66)       # triglyphs
pr = bm_for(P, "trav")
poly(pr, [Ff.p(u0 - 0.3, H(13.2), 1.6), Ff.p(u1 + 0.3, H(13.2), 1.6), Ff.p((u0 + u1) / 2, H(16.9), 1.6)])
poly(pr, [Ff.p(u0 - 0.3, H(13.2), -1.0), Ff.p((u0 + u1) / 2, H(16.9), -1.0), Ff.p(u1 + 0.3, H(13.2), -1.0)])
poly(bm_for(P, "roof"), [Ff.p(u0 - 0.6, H(13.15), 1.8), Ff.p((u0 + u1) / 2, H(17.1), 1.8), Ff.p((u0 + u1) / 2, H(17.1), -6.0), Ff.p(u0 - 0.6, H(13.15), -6.0)])
poly(bm_for(P, "roof"), [Ff.p((u0 + u1) / 2, H(17.1), 1.8), Ff.p(u1 + 0.6, H(13.15), 1.8), Ff.p(u1 + 0.6, H(13.15), -6.0), Ff.p((u0 + u1) / 2, H(17.1), -6.0)])
for k in range(4):                                                                                   # the steps up to it
    pbox(bm_for(P, "trav"), Ff, u0 - 0.8, u1 + 0.8, G - 0.4 + k * 0.15, G - 0.25 + k * 0.15, 0.8, 3.4 - k * 0.6)
K.export("borsa")
