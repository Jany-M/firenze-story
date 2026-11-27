"""Piazzale Michelangelo, the Loggia and the Rampe del Poggi (v1), absolute scene coordinates.

Run: blender -b --python blender/scripts/build_piazzale.py  →  web/public/models/landmarks/piazzale.glb
Measured (LiDAR 2023, DTM and DSM sampled every 3–5 m and 0.5–1 m round the monument: _dev/tmp/piazzale_probe*.py, values
in scene height = metres a.s.l. − 40):
- the terrace: 63.0–64.0 m; its north wall drops 7.5 m (west) to 9 m (east) to the paths below, its line from
  (745, 927) to (790, 936.5), (845, 939), a step out to (848, 950) and on to (895, 957.5);
- the monument at (818.5, 976.5): a raised platform ≈ 12 m across, 1.1 m over the terrace; the statue's top in the DSM
  at 71.7 (thin bronze: the scan catches little of it);
- the Loggia: a block x 790..814, z 1069..1083, 9–10 m over its ground (67.5), the terrace before it held by a wall at
  z ≈ 1050 (64.1 → 67.2);
- the Rampe: levels at 8.6 (Piazza Poggi), 13.8, then the bends of Viale Poggi at 21.3 and 30.3 (the Comune's carriageway
  polygons), 34–39 above; retaining walls at z ≈ 808, 829, 853 and 869 between them,
  the upper fountain's recess x 795..820 back to z ≈ 881.
From photographs (Commons; credited on the library page): walls of rusticated pietra forte with balustrades; on the
monument a stepped base ringed by posts and chains, a lower pedestal with red marble panels and the arms of Florence,
four bronze allegories (Day, Night, Dawn, Dusk) reclining on volutes at its corners, an upper pedestal with Cesare
Guasti's inscriptions, the bronze David; the Loggia a neoclassical arcade of three round arches on paired columns under
a balustraded roof terrace; the Rampe's grottoes faced with spugne (tufa), with arches, basins and cascades.
History: Giuseppe Poggi for Florence as capital; the piazzale built 1869 (Wikipedia, italia.it; visittuscany gives works
from 1873, opened 1875); the bronze David (Clemente Papi's cast) set up on 25 June 1873; the Loggia, meant as a museum
of Michelangelo's works, a café-restaurant from 1876 (its building date taken as 1873, *inferred*); the Rampe 1872–76,
their fountains dry for most of the 20th century and running again from 2019.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from landmark_detail import *
from landmark_church import Vs, extra_materials
from mathutils import Vector
K.reset()
MAT["forte"] = material("pietra_forte_poggi", None, (0.72, 0.62, 0.47), 0.9)
MAT["fortedk"] = material("pietra_forte_joints", None, (0.55, 0.46, 0.34), 0.9)
MAT["spugne"] = material("spugne_tufa", None, (0.78, 0.76, 0.7), 0.95)
MAT["pinkm"] = material("marble_red_panels", None, (0.78, 0.5, 0.45), 0.5)
MAT["bronzev"] = material("bronze_verdigris", None, (0.25, 0.45, 0.38), 0.45, metal=0.5)
MAT["stucco"] = material("loggia_stucco", None, (0.86, 0.82, 0.72), 0.85)
MAT["asph"] = material("piazzale_paving", None, (0.5, 0.49, 0.47), 0.95)
extra_materials()
NOW = K.NOW
PZ, MO, LG, RA = f"piazzale@1869-{NOW}", f"monumento_david@1873-{NOW}", f"loggia@1873-{NOW}", f"rampe@1876-{NOW}"

def seg(p0, p1, out):
    """Frame on the segment p0 → p1 (scene x, z): u along it, n horizontal towards the point `out`."""
    a, b = Vs(*p0), Vs(*p1); u = (b - a); L = u.length; u.normalize(); n = Vector((u.y, -u.x, 0))
    if (Vs(*out) - (a + b) / 2).dot(n) < 0: n = -n
    return Frame(a, u, n), L
def rusticated(part, F, L, v0, v1, course=0.6, depth=1.4):
    """A retaining wall: the body into the hill, the face in courses of pietra forte with sunk joints."""
    box(bm_for(part, "forte"), F, 0, L, v0, v1, -depth, 0)
    v = v0 + course
    while v < v1 - 0.2:
        pbox(bm_for(part, "fortedk"), F, 0, L, v - 0.05, v, 0, 0.015); v += course
def balustrade(part, F, L, v, h=1.0, step=0.36):
    pbox(bm_for(part, "forte"), F, -0.1, L + 0.1, v, v + 0.16, -0.5, 0.1)
    pbox(bm_for(part, "forte"), F, -0.1, L + 0.1, v + h - 0.16, v + h, -0.5, 0.1)
    for k in range(int(L / step)):
        u = (k + 0.5) * L / int(L / step)
        cylinder(part, "forte", F.p(u, 0, -0.2), 0.1, v + 0.16, v + h - 0.16, seg=6)
    for k in range(int(L / 4.0) + 1):                                   # piers
        u = min(L, k * 4.0); pbox(bm_for(part, "forte"), F, u - 0.25, u + 0.25, v, v + h + 0.08, -0.55, 0.15)
def grotto(part, F, u, v0, w, h, depth=1.6):
    """A round-headed grotto niche faced with spugne, dark inside."""
    arch_fill(part, "dark", F, u - w / 2, u + w / 2, v0, v0 + h - w / 2, n=0.03)
    ring(part, "spugne", F, u, v0 + h - w / 2, w / 2, w / 2 + 0.5, 0, 0.35, seg=12)
    for s in (-1, 1): pbox(bm_for(part, "spugne"), F, u + s * w / 2 - (0.5 if s < 0 else 0), u + s * w / 2 + (0.5 if s > 0 else 0), v0, v0 + h - w / 2, 0, 0.35)
def basin(part, cx, cz, w, d, g, rim=0.5):
    q = [Vs(cx - w / 2, cz - d / 2, g + rim - 0.1), Vs(cx + w / 2, cz - d / 2, g + rim - 0.1), Vs(cx + w / 2, cz + d / 2, g + rim - 0.1), Vs(cx - w / 2, cz + d / 2, g + rim - 0.1)]
    poly(bm_for(part, "water"), q[::-1])
    for (x0, z0, x1, z1) in ((cx - w / 2, cz - d / 2, cx + w / 2, cz - d / 2 + 0.35), (cx - w / 2, cz + d / 2 - 0.35, cx + w / 2, cz + d / 2),
                             (cx - w / 2, cz - d / 2, cx - w / 2 + 0.35, cz + d / 2), (cx + w / 2 - 0.35, cz - d / 2, cx + w / 2, cz + d / 2)):
        F, L = seg((x0, (z0 + z1) / 2), (x1, (z0 + z1) / 2), (x0, z1 + 5)); box(bm_for(part, "spugne"), F, 0, L, g - 0.2, g + rim, -(z1 - z0) / 2, (z1 - z0) / 2)

# ------------------------------------------------------------------ the terrace's north wall and balustrade
NW = [(745, 927), (790, 936.5), (845, 939), (848, 950), (895, 957.5)]
TOP = 63.2
for (p0, p1), low in zip(zip(NW, NW[1:]), (55.2, 55.6, 55.6, 54.4)):
    F, L = seg(p0, p1, ((p0[0] + p1[0]) / 2, min(p0[1], p1[1]) - 20))   # facing north, over the city
    rusticated(PZ, F, L, low - 1.0, TOP)
    pbox(bm_for(PZ, "forte"), F, -0.2, L + 0.2, TOP - 0.45, TOP, 0, 0.35)                   # coping
    balustrade(PZ, F, L, TOP)
# lamp posts along the balustrade
for k in range(9):
    t = (k + 0.5) / 9; i = min(int(t * (len(NW) - 1)), len(NW) - 2); f = t * (len(NW) - 1) - i
    x = NW[i][0] + (NW[i + 1][0] - NW[i][0]) * f; z = NW[i][1] + (NW[i + 1][1] - NW[i][1]) * f + 2.0
    cylinder(PZ, "iron", Vs(x, z), 0.09, TOP, TOP + 4.2, seg=6); sphere(PZ, "marble", Vs(x, z, TOP + 4.4), 0.28)

# ------------------------------------------------------------------ the monument to Michelangelo
C = (818.5, 976.5); G = 63.4
face = Vector((0.35, -1.0, 0)).normalized()                         # David looks south-east, towards the hills (scene +z is south: -y in Blender)
Fm = Frame(Vs(*C), Vector((-face.y, face.x, 0)), face)
for k, (w, h) in enumerate(((13.0, 0.3), (11.6, 0.6), (10.2, 0.9))):  # three steps
    box(bm_for(MO, "marble"), Fm, -w / 2, w / 2, G - 0.2, G + h, -w / 2, w / 2)
for k in range(12):                                                 # posts and chains round the steps
    t = 2 * math.pi * k / 12; p = Vs(*C) + Vector((math.cos(t), math.sin(t), 0)) * 7.4
    cylinder(MO, "marble", p, 0.25, G - 0.1, G + 1.0, seg=8)
    t2 = 2 * math.pi * (k + 1) / 12; p2 = Vs(*C) + Vector((math.cos(t2), math.sin(t2), 0)) * 7.4
    Fc = Frame(p, (p2 - p).normalized(), Vector((0, 0, 0)) + Vector((-(p2 - p).y, (p2 - p).x, 0)).normalized())
    pbox(bm_for(MO, "iron"), Fc, 0, (p2 - p).length, G + 0.72, G + 0.78, -0.03, 0.03)
B = G + 0.9
box(bm_for(MO, "marble"), Fm, -3.6, 3.6, B, B + 0.5, -3.6, 3.6)                         # plinth
box(bm_for(MO, "marble"), Fm, -3.2, 3.2, B + 0.5, B + 2.6, -3.2, 3.2)                   # the lower pedestal
for s in range(4):                                                  # its red marble panels and the arms
    ang = s * math.pi / 2; d = Vector((math.cos(ang), math.sin(ang), 0)); Fs = Frame(Vs(*C) + d * 3.2, Vector((-d.y, d.x, 0)), d)
    for u in (-2.0, 2.0): pbox(bm_for(MO, "pinkm"), Fs, u - 0.9, u + 0.9, B + 0.9, B + 2.2, 0, 0.04)
    pbox(bm_for(MO, "bronze"), Fs, -0.6, 0.6, B + 1.0, B + 2.1, 0, 0.12)
box(bm_for(MO, "marble"), Fm, -3.5, 3.5, B + 2.6, B + 3.0, -3.5, 3.5)                   # its cornice
for (su, sn) in ((-1, -1), (-1, 1), (1, -1), (1, 1)):               # four volutes, a reclining bronze figure on each
    cu, cn = su * 2.4, sn * 2.4
    box(bm_for(MO, "marble"), Fm, cu - 0.9, cu + 0.9, B + 3.0, B + 3.5, cn - 0.9, cn + 0.9)
    along = Vector((su, -sn, 0)).normalized() if su * sn > 0 else Vector((su, sn, 0)).normalized()
    p = Fm.p(cu, 0, cn); body = Frame(p, Fm.u * su, Fm.n * sn)
    box(bm_for(MO, "bronzev"), body, -1.1, 1.1, B + 3.5, B + 4.1, -0.35, 0.35)          # the figure lying along the corner
    box(bm_for(MO, "bronzev"), body, 0.6, 1.1, B + 4.1, B + 4.7, -0.3, 0.3)             # raised shoulders and head
    sphere(MO, "bronzev", body.p(0.9, B + 4.95, 0), 0.22)
box(bm_for(MO, "marble"), Fm, -1.9, 1.9, B + 3.0, B + 5.9, -1.9, 1.9)                   # the upper pedestal (inscriptions)
for s in range(4):
    ang = s * math.pi / 2; d = Vector((math.cos(ang), math.sin(ang), 0)); Fs = Frame(Vs(*C) + d * 1.9, Vector((-d.y, d.x, 0)), d)
    pbox(bm_for(MO, "pinkm"), Fs, -1.1, 1.1, B + 3.7, B + 5.3, 0, 0.03)
box(bm_for(MO, "bronzev"), Fm, -2.1, 2.1, B + 5.9, B + 6.3, -2.1, 2.1)                  # bronze top moulding
D = B + 6.3                                                         # the David, 5.2 m, weight on the right leg
box(bm_for(MO, "bronzev"), Fm, -0.75, 0.75, D, D + 0.35, -0.55, 0.55)                   # rock and base
box(bm_for(MO, "bronzev"), Fm, -0.42, -0.08, D + 0.35, D + 2.55, -0.2, 0.2)             # legs
box(bm_for(MO, "bronzev"), Fm, 0.08, 0.42, D + 0.35, D + 2.5, -0.15, 0.25)
box(bm_for(MO, "bronzev"), Fm, -0.55, 0.55, D + 2.5, D + 4.1, -0.3, 0.3)                # torso
box(bm_for(MO, "bronzev"), Fm, -0.82, -0.58, D + 2.6, D + 4.0, -0.12, 0.12)             # the right arm down
box(bm_for(MO, "bronzev"), Fm, 0.58, 0.82, D + 3.4, D + 4.0, -0.12, 0.12)               # the left arm raised to the shoulder
box(bm_for(MO, "bronzev"), Fm, 0.3, 0.7, D + 3.9, D + 4.2, -0.12, 0.12)
box(bm_for(MO, "bronzev"), Fm, -0.12, 0.12, D + 4.1, D + 4.35, -0.12, 0.12)             # neck
sphere(MO, "bronzev", Fm.p(0, D + 4.62, 0), 0.32)                                        # head and hair

# ------------------------------------------------------------------ the Loggia and the terrace wall below it
GL = 67.5
Ff, Lf = seg((790, 1069), (814, 1069), (802, 1060))                  # its front, towards the piazzale (north)
box(bm_for(LG, "stucco"), Ff, 0, Lf, GL - 0.5, GL + 9.0, -14.0, 0)
box(bm_for(LG, "forte"), Ff, -0.3, Lf + 0.3, GL + 8.4, GL + 9.0, -14.3, 0.4)            # cornice
for F_, L_ in (seg((790, 1069), (790, 1083), (780, 1076)), seg((814, 1069), (814, 1083), (824, 1076)), seg((790, 1083), (814, 1083), (802, 1095)), (Ff, Lf)):
    balustrade(LG, F_, L_, GL + 9.0, h=0.9)
# the arcade: three round arches between paired columns, the back of the loggia in shade
BAY = Lf / 5
for i in range(1, 4):
    u = BAY * (i + 0.5)
    arch_fill(LG, "dark", Ff, u - BAY / 2 + 0.7, u + BAY / 2 - 0.7, GL + 0.6, GL + 5.6, n=0.02)
    ring(LG, "stucco", Ff, u, GL + 5.6, BAY / 2 - 0.7, BAY / 2 - 0.25, 0, 0.3, seg=12)
for i in range(1, 5):
    for du in (-0.45, 0.45):
        cylinder(LG, "stucco", Ff.p(BAY * i + du, 0, 0.5), 0.26, GL + 0.6, GL + 7.4, seg=10)
    pbox(bm_for(LG, "stucco"), Ff, BAY * i - 0.85, BAY * i + 0.85, GL + 7.4, GL + 7.8, 0, 0.85)
for i in (0, 4):                                                    # the closed end bays with a window
    u = BAY * (i + 0.5); poly(bm_for(LG, "glass" if "glass" in MAT else "dark"), [Ff.p(u - 0.8, GL + 2.5, 0.03), Ff.p(u + 0.8, GL + 2.5, 0.03), Ff.p(u + 0.8, GL + 5.0, 0.03), Ff.p(u - 0.8, GL + 5.0, 0.03)])
pbox(bm_for(LG, "stucco"), Ff, 0, Lf, GL + 7.8, GL + 8.4, 0, 0.6)                       # entablature
box(bm_for(LG, "forte"), Ff, -3.0, Lf + 3.0, GL - 0.6, GL + 0.6, 0, 3.5)                 # its podium and steps
Fw, Lw = seg((768, 1050), (836, 1050), (802, 1040))                  # the balcony wall under the loggia (the epigraph)
rusticated(LG, Fw, Lw, 63.8, 67.2)
balustrade(LG, Fw, Lw, 67.2)
pbox(bm_for(LG, "marble"), Fw, Lw / 2 - 3.0, Lw / 2 + 3.0, 64.8, 66.4, 0, 0.06)         # the inscription

# ------------------------------------------------------------------ the Rampe: retaining walls, grottoes, basins, balustrades
def rampe_wall(x0, x1, z, low, top, grottoes=(), w=2.2):
    F, L = seg((x0, z), (x1, z), ((x0 + x1) / 2, z - 10))            # facing north, down to the river
    rusticated(RA, F, L, low - 0.6, top, course=0.55, depth=2.0)
    pbox(bm_for(RA, "forte"), F, -0.2, L + 0.2, top - 0.4, top, 0, 0.3)
    balustrade(RA, F, L, top)
    for gx in grottoes: grotto(RA, F, gx - x0, low, w, min(top - low - 0.8, 3.8))
    return F, L
rampe_wall(783, 818, 808, 8.6, 13.8, grottoes=(790, 800.5, 811))     # the lower fountains, behind the tower
basin(RA, 800.5, 804.5, 30, 4.0, 8.6)
rampe_wall(790, 830, 829, 13.9, 21.2, grottoes=(810,), w=3.0)          # the first level's fountain
basin(RA, 810, 826.0, 9, 3.0, 13.9)
F3, L3 = rampe_wall(748, 852, 853, 21.4, 30.2, grottoes=(760, 840))     # the middle level: the great grotto in its centre
G3 = 800.0
box(bm_for(RA, "spugne"), F3, G3 - 748 - 13, G3 - 748 + 13, 21.0, 30.6, 0, 1.6)        # the rock-faced front, a curved crest
F3f = Frame(F3.p(0, 0, 1.6), F3.u, F3.n)                           # on the rock face's front
for du in (-6.5, 0, 6.5): grotto(RA, F3f, G3 - 748 + du, 21.6, 4.6, 6.6, depth=2.5)
for du in (-3.25, 3.25):                                            # the cascades between the arches
    pbox(bm_for(RA, "water"), F3f, G3 - 748 + du - 0.6, G3 - 748 + du + 0.6, 22.0, 29.6, 0, 0.05)
for k in range(9):
    t = k / 8; pbox(bm_for(RA, "spugne"), F3, G3 - 748 - 13 + t * 26 - 1.6, G3 - 748 - 13 + t * 26 + 1.6, 30.6, 30.6 + 1.6 * math.sin(math.pi * t) + 0.3, 0, 1.6)
basin(RA, G3, 851.2, 26, 3.4, 21.4, rim=0.6)                      # the road (Viale Poggi's bend) runs just below it
rampe_wall(765, 795, 869, 30.4, 35.0); rampe_wall(820, 850, 869, 30.4, 35.0)
for x in (795, 820):                                                # the upper fountain's recess
    F, L = seg((x, 869), (x, 881), (807.5, 875)); rusticated(RA, F, L, 30.4, 37.5, depth=1.5); balustrade(RA, F, L, 37.5)
F4, L4 = rampe_wall(795, 820, 881, 30.4, 39.0, grottoes=(807.5,), w=3.2)
basin(RA, 807.5, 876.0, 18, 5.0, 30.4)
K.export("piazzale")
