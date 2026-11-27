"""Palazzo dell'Antella, Piazza Santa Croce 20–22 – dated model (v1), absolute scene coordinates.

Giulio Parigi joined older houses for Niccolò dell'Antella in 1619; the front over the square was painted in 1619–20 by
Giovanni da San Giovanni with a dozen painters (allegories between the windows, a frieze of framed scenes, putti and
garlands, the attic panels), with Chiarissimo Fancelli's bust of Cosimo II in the middle. The upper floors overhang the
square on stone brackets (a sporto), as the medieval houses here did.
Sources: OSM way 307104291 (front 32.4 m), LiDAR 2023 (eave ≈14.5 m over the square, overhang ≈1.5 m); photographs:
Ricardalovesmonuments 2021 (CC BY-SA 4.0, straightened onto the front as its texture), Jany Martelli 2026 (detail), Sailko,
Txllxt, Chabe01, Albarubescens (Wikimedia Commons). Ground floor openings from the 2021 panorama; roof terraces *inferred* dates.
Run: blender -b --factory-startup --python blender/scripts/build_antella.py
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from mathutils import Vector
from landmark_detail import *
from landmark_church import Vs
K.reset()
MAT["plaster"] = material("plaster_antella", "intonaco", (0.86, 0.77, 0.6), 0.9, 0.6)
MAT["serena"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)
MAT["forte"] = material("pietra_forte", "pietra_forte", (0.66, 0.56, 0.42), 0.85, 0.32, tint=(3.0, 2.85, 2.55))
MAT["fresco"] = material("antella_facade_frescoes", None, (1, 1, 1), 0.85, img="antella_facade.jpg")
MAT["wood"] = material("eaves_wood", "wood", (0.3, 0.21, 0.14), 0.85, 0.8)
MAT["iron"] = material("wrought_iron", None, (0.08, 0.08, 0.08), 0.6, metal=0.6)
MAT["shield"] = material("stemma_red", None, (0.55, 0.12, 0.1), 0.6)
NOW = K.NOW

A, B = (470.7, 322.4), (499.3, 337.7)                    # the front on the square (OSM); B is on the left seen from the square
L = math.dist(A, B); ux, uz = (A[0] - B[0]) / L, (A[1] - B[1]) / L
nx, nz = -uz, ux                                         # outward, towards the square (north)
if nz > 0: nx, nz = -nx, -nz
F = Frame(Vs(*B), Vector((ux, -uz, 0)), Vector((nx, -nz, 0)))
g = 6.85                                                 # the square in front (LiDAR ground 46.8–47.1 m)
TOP, SP, OUT, DEEP = g + 14.5, g + 3.85, 1.5, 13.4       # eave, underside of the overhang, overhang, depth of the house
U = lambda px: (px * 2.4 - 150) / 3550 * L               # x in the 1600-px panorama → metres along the front

BODY, OLD, PAINT = f"palazzo@1300-{NOW}", "facciata_case@1300-1618", f"affreschi@1620-{NOW}"
# the house behind the front and the overhanging upper floors
box(bm_for(BODY, "plaster"), F, 0, L, g - 0.6, TOP, -DEEP, 0)
box(bm_for(BODY, "plaster"), F, 0, L, SP - 0.1, TOP, 0, OUT)
# the front: the frescoes from 1620, plain plaster on the houses before
fr = [F.p(0, SP, OUT + 0.012), F.p(L, SP, OUT + 0.012), F.p(L, TOP, OUT + 0.012), F.p(0, TOP, OUT + 0.012)]
uv_poly(bm_for(PAINT, "fresco"), fr, [(0, 0), (1, 0), (1, 1), (0, 1)])
box(bm_for(OLD, "plaster"), F, 0, L, SP, TOP, OUT, OUT + 0.01)
# string courses in pietra serena under the two rows of windows (from the panorama)
for z in (TOP - 5.17, g + 5.21):
    box(bm_for(BODY, "serena"), F, 0, L, z - 0.12, z, OUT, OUT + 0.08)
# the brackets of the overhang (mensoloni) and the stone sill under it
for px in (70, 175, 268, 350, 462, 553, 770, 905, 1020, 1158, 1262, 1383, 1540):
    u = U(px)
    box(bm_for(BODY, "forte"), F, u - 0.22, u + 0.22, g + 0.9, SP, 0, 0.35)                 # the pier
    for k, (z0, z1, n1) in enumerate(((g + 2.3, g + 2.9, 0.75), (g + 2.9, g + 3.4, 1.1), (g + 3.4, SP, OUT - 0.05))):
        box(bm_for(BODY, "forte"), F, u - 0.2, u + 0.2, z0, z1, 0.3, n1)                    # stepping out to carry the floor
box(bm_for(BODY, "serena"), F, 0, L, SP - 0.18, SP, 0, OUT + 0.05)
# ground floor: shops, barred windows, the portal with the dell'Antella arms
def opening(px0, px1, ztop, z0=0.0, kind="door"):
    u0, u1 = U(px0), U(px1)
    box(bm_for(BODY, "dark"), F, u0, u1, g + z0, g + ztop, 0.0, 0.02)
    for a, b in ((u0 - 0.16, u0), (u1, u1 + 0.16)): box(bm_for(BODY, "serena"), F, a, b, g + z0, g + ztop + 0.16, 0, 0.06)
    box(bm_for(BODY, "serena"), F, u0 - 0.16, u1 + 0.16, g + ztop, g + ztop + 0.16, 0, 0.06)
    if kind == "window":
        for k in range(1, 5): box(bm_for(BODY, "iron"), F, u0 + (u1 - u0) * k / 5 - 0.015, u0 + (u1 - u0) * k / 5 + 0.015, g + z0, g + ztop, 0.02, 0.05)
for px0, px1, top, z0, kind in ((375, 450, 3.0, 0, "door"), (205, 265, 2.75, 1.3, "window"), (475, 530, 2.75, 1.3, "window"), (810, 865, 2.95, 1.45, "window"),
                                (905, 1000, 3.3, 0, "door"), (1045, 1100, 2.9, 0, "door"), (1160, 1222, 2.95, 0, "door"), (1270, 1318, 2.85, 1.4, "window"),
                                (1430, 1500, 2.95, 0, "door"), (60, 105, 2.95, 0, "door")):
    opening(px0, px1, top, z0, kind)
pu = U(712)                                              # the portal
box(bm_for(BODY, "wood"), F, pu - 0.75, pu + 0.75, g, g + 3.0, 0.0, 0.04)
box(bm_for(BODY, "serena"), F, pu - 1.0, pu + 1.0, g + 3.0, g + 3.25, 0, 0.12)
for a in (-1, 1): box(bm_for(BODY, "serena"), F, pu + a * 0.75 - (0.25 if a > 0 else 0), pu + a * 0.75 + (0.25 if a < 0 else 0), g, g + 3.0, 0, 0.1)
box(bm_for(BODY, "shield"), F, pu - 0.28, pu + 0.28, g + 3.3, g + 3.75, 0.05, 0.12)       # the arms
# eaves and roof
box(bm_for(BODY, "wood"), F, -0.2, L + 0.2, TOP, TOP + 0.22, -DEEP - 0.6, OUT + 1.1)
rf = bm_for(BODY, "roof")
poly(rf, [F.p(-0.2, TOP + 0.22, OUT + 1.1), F.p(L + 0.2, TOP + 0.22, OUT + 1.1), F.p(L + 0.2, TOP + 2.6, -6.0), F.p(-0.2, TOP + 2.6, -6.0)])
poly(rf, [F.p(-0.2, TOP + 2.6, -6.0), F.p(L + 0.2, TOP + 2.6, -6.0), F.p(L + 0.2, TOP + 0.22, -DEEP - 0.6), F.p(-0.2, TOP + 0.22, -DEEP - 0.6)])
# on the roof (seen in every photograph since the 19th century; dates inferred): a two-storey altana and two terraces
ALT = f"altane@1850-{NOW}"
ua, ub = U(900), U(1115)
box(bm_for(ALT, "plaster"), F, ua, ub, TOP, TOP + 5.3, -9.0, -3.2)
box(bm_for(ALT, "roof"), F, ua - 0.3, ub + 0.3, TOP + 5.3, TOP + 5.55, -9.3, -2.9)
box(bm_for(ALT, "dark"), F, (ua + ub) / 2 - 0.5, (ua + ub) / 2 + 0.5, TOP + 3.3, TOP + 4.6, -3.2, -3.17)
for p0, p1 in ((640, 885), (1125, 1450)):
    a0, a1 = U(p0), U(p1)
    box(bm_for(ALT, "plaster"), F, a0, a1, TOP, TOP + 3.0, -8.0, -3.0)
    box(bm_for(ALT, "iron"), F, a0, a1, TOP + 3.9, TOP + 3.95, -3.05, -2.98)
    for k in range(int((a1 - a0) / 0.5)): box(bm_for(ALT, "iron"), F, a0 + k * 0.5, a0 + k * 0.5 + 0.03, TOP + 3.0, TOP + 3.95, -3.03, -3.0)
K.export("antella")
