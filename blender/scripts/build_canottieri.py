"""Società Canottieri Firenze: the rowing club's terrace on the Arno under the Uffizi (v1), absolute scene coordinates.

Run: blender -b --python blender/scripts/build_canottieri.py  →  web/public/models/landmarks/canottieri.glb
Measured (LiDAR 2023 DTM; the lungarni's wall line from pipeline/46_lungarni.py): a shelf of bank at 2.6–3.0 m (scene)
between the river wall under the Uffizi's Arno wing and the water, ≈10–12 m wide from x ≈ 5 to 62: the wall from (10, 458.8)
to (30, 463.9), (50, 472.3), (62, 478); the water's edge from (6, 463) to (28, 470.5), (44, 476.5), (62, 482.5).
From photographs (Commons: Francesco Bini 2023, Sailko 2021; credited on the library page): a lawn with green iron chairs and
tables, rose bushes along the wall, a path of stone flags along the wall and brick-edged steps down to the lawn at the
west end, the club's door (a round-headed arch in a white plastered wall, the sign, a clock and memorial tablets) under the
Uffizi's corbelled loggia, a flagpole by the water, the boats kept inside (rowing shells on a floating landing).
History: the club, founded in 1886 (the Federation's list of centenary clubs; another account gives 1911, heir to the
Libertas of 1890), has had its seat under the Uffizi and the Ponte Vecchio since May 1933 (La Nazione).
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from landmark_detail import *
from landmark_church import Vs, extra_materials
from mathutils import Vector
K.reset()
MAT["flags"] = material("stone_flags", None, (0.6, 0.58, 0.54), 0.9)
MAT["brick"] = material("brick_edge", None, (0.62, 0.35, 0.26), 0.9)
MAT["white"] = material("white_plaster", None, (0.9, 0.88, 0.82), 0.85)
MAT["chair"] = material("green_iron_chairs", None, (0.12, 0.3, 0.2), 0.6, metal=0.4)
MAT["rose"] = material("rose_bushes", None, (0.2, 0.36, 0.14), 0.95)
MAT["bloom"] = material("rose_blooms", None, (0.75, 0.15, 0.2), 0.8)
MAT["hull"] = material("rowing_shells", None, (0.92, 0.92, 0.9), 0.4)
MAT["deck"] = material("landing_planks", None, (0.45, 0.36, 0.26), 0.9)
MAT["glass"] = material("window_glass", None, (0.08, 0.09, 0.11), 0.15)
extra_materials()
NOW = K.NOW
P = f"canottieri@1933-{NOW}"
WALL = [(5, 457.5), (10, 458.8), (30, 463.9), (50, 472.3), (62, 478.0)]
EDGE = [(5, 462.0), (6, 463.0), (28, 470.5), (44, 476.5), (62, 482.5)]
GB = 2.8                                                           # the terrace (scene)
def lerp(line, x):
    for (x0, z0), (x1, z1) in zip(line, line[1:]):
        if x0 <= x <= x1: return z0 + (z1 - z0) * (x - x0) / (x1 - x0)
    return line[0][1] if x < line[0][0] else line[-1][1]
# the lawn, the flagstone path along the wall, the brick steps down at the west end
xs = [5 + k * 2.85 for k in range(21)]
for x0, x1 in zip(xs, xs[1:]):
    w0, w1, e0, e1 = lerp(WALL, x0), lerp(WALL, x1), lerp(EDGE, x0), lerp(EDGE, x1)
    poly(bm_for(P, "flags"), [Vs(x0, w0, GB + 0.05), Vs(x1, w1, GB + 0.05), Vs(x1, w1 + 2.4, GB + 0.05), Vs(x0, w0 + 2.4, GB + 0.05)][::-1])
    poly(bm_for(P, "lawn"), [Vs(x0, w0 + 2.4, GB + 0.04), Vs(x1, w1 + 2.4, GB + 0.04), Vs(x1, e1 - 0.4, GB + 0.04), Vs(x0, e0 - 0.4, GB + 0.04)][::-1])
    poly(bm_for(P, "flags"), [Vs(x0, e0 - 0.4, GB + 0.06), Vs(x1, e1 - 0.4, GB + 0.06), Vs(x1, e1, GB - 0.3), Vs(x0, e0, GB - 0.3)][::-1])   # the stone edge to the water
for k in range(4):                                                  # steps from the door's level down to the lawn
    x0 = 7.0 + k * 0.45
    F = Frame(Vs(x0, lerp(WALL, x0)), Vector((0, -1, 0)), Vector((-1, 0, 0)))
    box(bm_for(P, "brick"), F, 0, 4.0, GB, GB + 0.6 - k * 0.15, -0.45, 0)
# the door: a round-headed arch in a white plastered stretch of the wall, sign, clock and tablets
dx = 16.0; F = Frame(Vs(dx - 4, lerp(WALL, dx - 4)), (Vs(dx + 4, lerp(WALL, dx + 4)) - Vs(dx - 4, lerp(WALL, dx - 4))).normalized(), Vector((0, 0, 0)))
F.n = Vector((F.u.y, -F.u.x, 0)) if Vector((F.u.y, -F.u.x, 0)).y < 0 else Vector((-F.u.y, F.u.x, 0))   # towards the river (−y in Blender is +z, south)
box(bm_for(P, "white"), F, 0, 8.0, GB - 0.2, GB + 5.2, -0.2, 0.06)
arch_fill(P, "dark", F, 2.9, 5.1, GB + 0.6, GB + 3.0, n=0.08)
ring(P, "white", F, 4.0, GB + 3.0, 1.1, 1.4, 0, 0.25, seg=10)
pbox(bm_for(P, "white"), F, 2.0, 6.0, GB + 0.45, GB + 0.6, 0.06, 1.2)                             # threshold
pbox(bm_for(P, "slate" if "slate" in MAT else "dark"), F, 6.0, 6.9, GB + 2.2, GB + 2.8, 0.06, 0.1)  # the sign
cylinder(P, "white", F.p(7.3, 0, 0.1), 0.3, GB + 2.9, GB + 2.95, seg=12)                               # clock
for u in (0.8, 1.6): pbox(bm_for(P, "marble"), F, u, u + 0.6, GB + 1.8, GB + 2.7, 0.06, 0.09)        # tablets
# roses along the wall, tables and green chairs on the lawn, a flagpole by the water
import random; rnd = random.Random(1933)
for k in range(12):
    x = 24 + k * 3.0; z = lerp(WALL, x) + 0.6
    sphere(P, "rose", Vs(x, z, GB + 0.55), 0.55); sphere(P, "bloom", Vs(x + 0.2, z + 0.25, GB + 0.95), 0.18)
for k in range(7):
    x = 12 + k * 6.5 + rnd.uniform(-1, 1); z = (lerp(WALL, x) + lerp(EDGE, x)) / 2 + rnd.uniform(-1, 1)
    cylinder(P, "chair", Vs(x, z), 0.05, GB, GB + 0.72, seg=6); cylinder(P, "chair", Vs(x, z), 0.4, GB + 0.72, GB + 0.76, seg=12)
    for a in range(3):
        t = a * 2.1 + rnd.uniform(0, 0.5); c = Vs(x, z) + Vector((math.cos(t), math.sin(t), 0)) * 0.85
        Fc = Frame(c, Vector((-math.sin(t), math.cos(t), 0)), Vector((math.cos(t), math.sin(t), 0)))
        box(bm_for(P, "chair"), Fc, -0.22, 0.22, GB + 0.42, GB + 0.46, -0.22, 0.22); box(bm_for(P, "chair"), Fc, -0.22, 0.22, GB + 0.46, GB + 0.9, 0.18, 0.22)
        for su in (-0.2, 0.2):
            for sn in (-0.2, 0.2): cylinder(P, "chair", Fc.p(su, 0, sn), 0.015, GB, GB + 0.42, seg=4)
fx = 40.0; fz = lerp(EDGE, fx) - 1.2
cylinder(P, "white", Vs(fx, fz), 0.06, GB, GB + 9.0, seg=6)
Ff = Frame(Vs(fx, fz, 0), Vector((1, 0, 0)), Vector((0, -1, 0)))
pbox(bm_for(P, "white"), Ff, 0.05, 1.6, GB + 7.9, GB + 8.9, -0.01, 0.01); pbox(bm_for(P, "bloom"), Ff, 0.05, 1.6, GB + 8.4, GB + 8.6, -0.012, 0.012)   # white and red
# the floating landing at the west end, two rowing shells on it
for k in range(6):
    x = -6 + k * 2.0; z = lerp(EDGE, 6) + 0.5
    box(bm_for(P, "deck"), Frame(Vs(x, z, 0), Vector((1, 0, 0)), Vector((0, -1, 0))), 0, 1.9, 1.85, 2.05, -0.2, 2.6)
for k, off in enumerate((0.6, 1.7)):
    F = Frame(Vs(-6.5, lerp(EDGE, 6) + 0.5 + off, 0), Vector((1, 0, 0)), Vector((0, -1, 0)))
    box(bm_for(P, "hull"), F, 0, 11.5, 2.05, 2.3, -0.18, 0.18)
K.export("canottieri")
