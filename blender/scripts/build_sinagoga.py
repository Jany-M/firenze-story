"""Tempio Maggiore Israelitico – the Synagogue of Florence (v1).

Run:  python pipeline/47_moderni.py   (once: outlines, ground, DSM raster → blender/data/moderni.json)
      blender -b --python blender/scripts/build_sinagoga.py  →  web/public/models/landmarks/sinagoga.glb
Frame: a along the west front (towards Via Farini) from its south corner (OSM way 102979678), o inwards (east).
Measured (LiDAR 2023 DSM; ground 9.5 m scene): the front ≈23 m; the hall's roof ≈24 m above the ground; the central dome's
top ≈45.7 m at o ≈28 (≈17 m across where it rises from the roof); the two towers on the front ≈27 m.
From photographs and descriptions: a Moorish-revival front in bands of white travertine and pink stone, a portico of
horseshoe arches, two towers with small domes, the great dome in green copper (gilded at first) (La Nazione; meer.com).
Dates: built 1874–1882 to the design of Marco Treves, Mariano Falcini and Vincenzo Micheli, inaugurated 24 October 1882
(shown from 1882; the works 1874–82 not drawn) – docs/landmarks/SINAGOGA.md.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from mathutils import Vector
from landmark_detail import *
from landmark_church import Site, extra_materials
K.reset()
MAT["plaster"] = material("travertine", None, (0.9, 0.86, 0.78), 0.8)
MAT["pink"] = material("pink_stone", None, (0.86, 0.66, 0.6), 0.8)
MAT["copper"] = material("copper_verdigris", None, (0.36, 0.62, 0.52), 0.5, metal=0.3)
MAT["serena"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)
MAT["gold"] = material("gilt", None, (0.85, 0.68, 0.3), 0.35, metal=0.8)
extra_materials()
NOW = K.NOW
S = Site("sinagoga", "moderni"); G = S.G; L = S.L
F = S.front()
Y = 1882; P = f"tempio@{Y}-{NOW}"
DOME_O, DOME_R, ROOF = 28.0, 8.6, G + 24.0
TOW = 3.2                                                                   # half size of the towers on the front
DEPTH = 46.0                                                                # the hall's length (DSM: the roof ends ≈46 m in)
c = S.W(L / 2, DOME_O)
# the hall: one block with a flat roof, walls in bands of travertine and pink stone, tall horseshoe windows on the sides
Fb = Frame(S.W(0, 0), S.TA, S.NO)
box(bm_for(P, "plaster"), Fb, 0, L, G - 0.3, ROOF, 0, DEPTH)
sides = [(Frame(S.W(0, DEPTH), -S.NO, -S.TA), DEPTH), (Frame(S.W(L, 0), S.NO, S.TA), DEPTH), (Frame(S.W(L, DEPTH), -S.TA, S.NO), L)]
for Fs, Ls in sides:
    for k in range(int((ROOF - G) / 1.2)):
        if k % 2: pbox(bm_for(P, "pink"), Fs, 0, Ls, G + k * 1.2, G + (k + 1) * 1.2, 0, 0.06)
    nwin = max(1, int(Ls / 6.0))
    for i in range(nwin):
        uc = (i + 0.5) * Ls / nwin
        arch_fill(P, "dark", Fs, uc - 0.9, uc + 0.9, G + 8.0, G + 15.0, n=0.08)
    pbox(bm_for(P, "serena"), Fs, -0.2, Ls + 0.2, ROOF - 0.6, ROOF, 0, 0.45)
cylinder(P, "pink", c, DOME_R + 0.4, ROOF, ROOF + 4.5, seg=16)
for k in range(16):                                                          # windows round the drum
    t = 2 * math.pi * (k + 0.5) / 16; d = Vector((math.cos(t), math.sin(t), 0)); Fd = Frame(c + d * (DOME_R + 0.4), Vector((-d.y, d.x, 0)), d)
    poly(bm_for(P, "dark"), [Fd.p(-0.5, ROOF + 1.0, 0.03), Fd.p(0.5, ROOF + 1.0, 0.03), Fd.p(0.5, ROOF + 3.4, 0.03), Fd.p(-0.5, ROOF + 3.4, 0.03)])
top = dome(P, c, DOME_R + 0.5, ROOF + 4.5, 16.0, ribs=16, mat="copper", seg=32, rib_mat="copper")   # slightly pointed by its height
cone(P, "copper", c, 1.2, 0.2, top - 0.3, top + 1.6, seg=12); sphere(P, "gold", c + Vector((0, 0, top + 1.9)), 0.45)
# the two towers on the front, banded, with small copper domes
for ac in (TOW, L - TOW):
    tc = S.W(ac, TOW)
    for z in [G - 0.3 + 1.2 * k for k in range(int(27.0 / 1.2))]:                      # towers rise above the hall (DSM ≈27 m)
        Fb = Frame(S.W(ac - TOW, 0, 0), S.TA, S.NO)
        box(bm_for(P, "pink" if int((z - G) / 1.2) % 2 else "plaster"), Fb, -0.25, 2 * TOW + 0.25, z, z + 1.2, -0.25, 2 * TOW + 0.25)
    cylinder(P, "plaster", tc, TOW * 0.8, G + 26.6, G + 28.6, seg=8)
    t2 = dome(P, tc, TOW * 0.85, G + 28.6, 3.6, ribs=8, mat="copper", seg=16, rib_mat="copper")
    sphere(P, "gold", tc + Vector((0, 0, t2 + 0.5)), 0.25)
# the front between the towers: bands of travertine and pink stone, the portico of horseshoe arches, a rose window
for k in range(int(18.0 / 1.2)):
    pbox(bm_for(P, "pink" if k % 2 else "plaster"), F, 2 * TOW, L - 2 * TOW, G + k * 1.2, G + (k + 1) * 1.2, 0, 0.15)
n = 3; w = (L - 4 * TOW) / n
for i in range(n):
    uc = 2 * TOW + (i + 0.5) * w; r = w * 0.36
    pts = [F.p(uc - r, G + 0.2, 0.17), F.p(uc + r, G + 0.2, 0.17)] + [F.p(uc + r * math.cos(t), G + 5.2 + r * math.sin(t), 0.17) for t in [-0.35 + (math.pi + 0.7) * j / 16 for j in range(17)]]
    poly(bm_for(P, "dark"), pts[:2] + pts[2:])
    ring(P, "serena", F, uc, G + 5.2, r, r + 0.35, 0.17, 0.3, seg=12)
poly(bm_for(P, "dark"), [F.p(L / 2 + 2.0 * math.cos(2 * math.pi * k / 20), G + 12.5 + 2.0 * math.sin(2 * math.pi * k / 20), 0.2) for k in range(20)])
pbox(bm_for(P, "serena"), F, 2 * TOW - 0.2, L - 2 * TOW + 0.2, G + 18.0, G + 18.6, 0, 0.5)
K.export("sinagoga")
