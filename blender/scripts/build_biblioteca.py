"""Biblioteca Nazionale Centrale di Firenze, Piazza dei Cavalleggeri (v1).

Run:  python pipeline/47_moderni.py biblioteca   (outline, ground, DSM raster → blender/data/moderni.json)
      blender -b --python blender/scripts/build_biblioteca.py  →  web/public/models/landmarks/biblioteca.glb
Frame: a along the front on Piazza dei Cavalleggeri from the west corner of OSM way 102979687 (by the rotunda on Via
Magliabechi) to the east corner on Via Tripoli (132 m), o inwards (north).
Measured (LiDAR 2023 DSM, height over the ground, read in this frame): the central block a 58..98 stands 8.5 m forward
of the line (o -8.5..2) at 20 m; its two towers a 59..67 and 88.5..96.5 reach 33 m; the wings 21–22 m, their front at
o -3 (west) and o -1.7 (east); the rotunda at the west corner a half circle of r ≈ 9.6 m (centre a 1.6, o 17.5), 27–28 m;
the distribution hall behind the portico 18 m; the rear blocks 13–20 m round light wells.
From photographs (Commons: Sailko, Gryffindor, Zairon, Giovanni Dall'Orto, Jebulon; credited on the library page): walls
in pietra forte, three storeys of windows with stone frames, paired windows on the main floor, a band of reddish panels
under the cornice; the portico of three round arches on Corinthian columns, white marble arms of Florence and of Savoy at
its corners, the dark panel BIBLIOTECA NAZIONALE CENTRALE over it; the two square towers ("the architect's ears") with an
arched opening on each face and a bronze statue in the front one – Dante and Galileo –, a deep cornice and a low tiled
roof; the rotunda ("Tribuna dantesca e galileiana") with arched windows and a low drum.
History: competition 1904–06, won by Cesare Bazzani; first stone 8 May 1911, works stopped by the war; the rotunda (the
Tribuna) first, 1929–30; the library moved from the Uffizi and opened on 30 October 1935; a west wing towards the Santa
Croce cloisters by Vincenzo Mazzei 1962 (which block it is: *inferred*, the north-west one); flooded on 4 November 1966.
Sources: bncf.cultura.gov.it ("La nuova sede"), risorgimentofirenze.it, cultura.gov.it.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from landmark_detail import *
from landmark_church import Site, extra_materials
from landmark_volume import Vol, punched, arched_row
from mathutils import Vector
K.reset()
MAT["forte"] = material("pietra_forte_bncf", None, (0.74, 0.58, 0.36), 0.85)          # smooth dressed ashlar, ochre
MAT["fortedk"] = material("pietra_forte_frames", None, (0.62, 0.48, 0.3), 0.85)
MAT["shade"] = material("portico_shade", None, (0.3, 0.25, 0.19), 0.9)
MAT["pinkband"] = material("red_panels", None, (0.72, 0.45, 0.38), 0.85)
MAT["marble"] = material("white_marble", None, (0.92, 0.91, 0.88), 0.5)
MAT["slate"] = material("name_panel", None, (0.18, 0.19, 0.19), 0.6)
MAT["bronze"] = material("bronze_statues", None, (0.2, 0.22, 0.17), 0.45, metal=0.7)
MAT["glass"] = material("window_glass", None, (0.08, 0.09, 0.11), 0.15)
extra_materials()
NOW = K.NOW
S = Site("biblioteca", "moderni"); G = S.G; V = Vol(S)
B0 = G - 2.8                                          # walls start below the lowest ground round the block (5.8)
P = f"biblioteca@1935-{NOW}"; TR = f"tribuna@1929-{NOW}"; MZ = f"ala_mazzei@1962-{NOW}"
CW = f"cantiere@1911-1934"                            # the works: the shell rising
def H(z): return G + z
WING = 20.0

# ------------------------------------------------------------------ masses
blocks = [  # (part, a0, a1, o0, o1, height over G)
    (P, 23.4, 58.0, -3.0, 12.0, WING), (P, 98.0, 132.0, -1.7, 14.0, WING),        # the front wings
    (P, 0.0, 23.4, 0.0, 27.0, WING),                                               # the west end, behind the rotunda
    (P, 23.4, 66.0, 12.0, 33.0, 18.0), (P, 66.0, 88.0, 2.0, 34.0, 18.0),          # the rear wing, the distribution hall
    (P, 88.0, 126.0, 14.0, 38.0, 14.0), (P, 66.3, 85.8, 34.0, 42.0, 15.0),         # rear storehouses
    (MZ, -1.4, 23.4, 27.0, 35.5, 17.0),                                            # Mazzei's wing (1962)
]
for part, a0, a1, o0, o1, h in blocks:
    V.prism(part, "forte", V.rect(a0, a1, o0, o1), B0, H(h), top_mat="roof")
    V.hip(part, "roof", a0, a1, o0, o1, H(h), H(h) + min(2.2, (min(a1 - a0, o1 - o0)) / 6), over=0.6)
# the central block before the line, with its towers
CB = (58.0, 98.0, -8.5, 2.0)
V.prism(P, "forte", V.rect(*CB), B0, H(20.0), top_mat="roof")
TOW = [(59.0, 67.0), (88.5, 96.5)]
# the rotunda: a half cylinder on the west end, drum and low dome over it
rc = V.W(1.6, 17.5); RR = 9.6
def rdir(t): return S.TA * math.cos(t) + S.NO * math.sin(t)
seg = 18
for k in range(seg):
    t0, t1 = math.pi / 2 + math.pi * k / seg, math.pi / 2 + math.pi * (k + 1) / seg     # the west half (towards -a)
    d0, d1 = rdir(t0), rdir(t1)
    poly(bm_for(TR, "forte"), [rc + d0 * RR + Vector((0, 0, B0)), rc + d1 * RR + Vector((0, 0, B0)), rc + d1 * RR + Vector((0, 0, H(21.0))), rc + d0 * RR + Vector((0, 0, H(21.0)))])
    poly(bm_for(TR, "roof"), [rc + Vector((0, 0, H(21.0))), rc + d1 * RR + Vector((0, 0, H(21.0))), rc + d0 * RR + Vector((0, 0, H(21.0)))])
    dm = rdir((t0 + t1) / 2); Fr = Frame(rc + dm * (RR + 0.02), (d1 - d0).normalized(), dm); w = RR * math.pi / seg
    if k % 2 == 0 or True:
        arch_fill(TR, "glass", Fr, -w * 0.28, w * 0.28, H(11.5), H(15.5), n=0.03)
        poly(bm_for(TR, "glass"), [Fr.p(-w * 0.25, H(6.5), 0.03), Fr.p(w * 0.25, H(6.5), 0.03), Fr.p(w * 0.25, H(9.5), 0.03), Fr.p(-w * 0.25, H(9.5), 0.03)])
        poly(bm_for(TR, "dark"), [Fr.p(-w * 0.18, H(1.2), 0.03), Fr.p(w * 0.18, H(1.2), 0.03), Fr.p(w * 0.18, H(2.6), 0.03), Fr.p(-w * 0.18, H(2.6), 0.03)])
    pbox(bm_for(TR, "forte"), Fr, -w / 2 - 0.02, w / 2 + 0.02, H(19.6), H(21.0), 0, 0.7)          # cornice
    pbox(bm_for(TR, "forte"), Fr, -w / 2 - 0.02, w / 2 + 0.02, H(10.6), H(11.0), 0, 0.3)          # string courses
    pbox(bm_for(TR, "forte"), Fr, -w / 2 - 0.02, w / 2 + 0.02, H(4.8), H(5.2), 0, 0.3)
    pbox(bm_for(TR, "pinkband"), Fr, -w / 2, w / 2, H(17.6), H(18.8), 0, 0.02)
cylinder(TR, "forte", rc, 7.2, H(21.0), H(24.6), seg=28)                                             # the drum
for k in range(16):
    t = 2 * math.pi * k / 16; d = rdir(t); Fd = Frame(rc + d * 7.22, Vector((-d.y, d.x, 0)), d)
    arch_fill(TR, "glass", Fd, -0.7, 0.7, H(21.8), H(23.4), n=0.02)
cylinder(TR, "forte", rc, 7.6, H(24.3), H(24.9), seg=28)
dome(TR, rc, 7.3, H(24.9), 3.2, ribs=16, mat="roof", seg=28, rib_mat="forte")

# ------------------------------------------------------------------ the walls of the wings: three storeys of windows
def wing_face(part, F, L, top=WING, bays=3.9, first=True):
    pbox(bm_for(part, "forte"), F, -0.3, L + 0.3, H(top - 0.9), H(top), 0, 0.85)                    # cornice
    pbox(bm_for(part, "pinkband"), F, 0.3, L - 0.3, H(top - 2.4), H(top - 1.2), 0, 0.02)             # the red panels
    for v in (H(5.6), H(11.6)): pbox(bm_for(part, "forte"), F, 0, L, v - 0.35, v, 0, 0.3)              # string courses
    pbox(bm_for(part, "fortedk"), F, 0, L, B0, H(1.2), 0, 0.25)                                        # plinth
    us = punched(part, F, 0.8, L - 0.8, H(2.0), H(4.3), 1.2, bays, fill="glass", frame="fortedk", fw=0.18)
    for u in us:                                                                                       # paired windows, main floor
        for du in (-0.62, 0.62):
            poly(bm_for(part, "glass"), [F.p(u + du - 0.48, H(6.6), 0.04), F.p(u + du + 0.48, H(6.6), 0.04), F.p(u + du + 0.48, H(10.4), 0.04), F.p(u + du - 0.48, H(10.4), 0.04)])
        pbox(bm_for(part, "fortedk"), F, u - 1.3, u + 1.3, H(6.3), H(6.6), 0, 0.2)
        pbox(bm_for(part, "fortedk"), F, u - 1.3, u + 1.3, H(10.4), H(11.0), 0, 0.22)
        for du in (-1.25, 0, 1.25): pbox(bm_for(part, "fortedk"), F, u + du - 0.1, u + du + 0.1, H(6.6), H(10.4), 0, 0.16)
        poly(bm_for(part, "glass"), [F.p(u - 0.9, H(12.6), 0.04), F.p(u + 0.9, H(12.6), 0.04), F.p(u + 0.9, H(16.2), 0.04), F.p(u - 0.9, H(16.2), 0.04)])
        for (a_, b_, c_, d_) in ((u - 1.1, u - 0.9, H(12.6), H(16.2)), (u + 0.9, u + 1.1, H(12.6), H(16.2)), (u - 1.1, u + 1.1, H(16.2), H(16.6)), (u - 1.2, u + 1.2, H(12.3), H(12.6))):
            pbox(bm_for(part, "fortedk"), F, a_, b_, c_, d_, 0, 0.16)
for part, a0, a1, o0, o1, h in blocks:
    for F, L, p0, p1 in V.edges(V.rect(a0, a1, o0, o1)):
        wing_face(part, F, L, top=h, bays=3.9 if h >= 18 else 4.6)
# ------------------------------------------------------------------ the central block: portico, name panel, arms, towers
Ff, Lf = V.frame(CB[0], CB[2], CB[1], CB[2], inside=(78, 0))       # u from the west tower's corner, 40 m
pbox(bm_for(P, "fortedk"), Ff, 0, Lf, B0, H(1.4), 0, 0.3)
# the portico: three arches between the towers' feet, ≈ 4 m deep, dark behind, steps before it
PU0, PU1 = 10.0, 30.0; pw = (PU1 - PU0) / 3
for i in range(3):
    u = PU0 + pw * (i + 0.5)
    arch_fill(P, "shade", Ff, u - pw / 2 + 0.55, u + pw / 2 - 0.55, H(1.4), H(8.6), n=0.02)
    ring(P, "forte", Ff, u, H(8.6), pw / 2 - 0.55, pw / 2 - 0.05, 0, 0.35, seg=14)
for u in (PU0 + 0.3, PU0 + pw, PU0 + 2 * pw, PU1 - 0.3):           # columns, capitals, bases
    cylinder(P, "forte", Ff.p(u, 0, 0.45), 0.36, H(1.4), H(7.6), seg=12)
    pbox(bm_for(P, "forte"), Ff, u - 0.55, u + 0.55, H(7.6), H(8.6), -0.05, 1.0)
    pbox(bm_for(P, "forte"), Ff, u - 0.5, u + 0.5, H(1.4), H(1.9), -0.05, 0.95)
poly(bm_for(P, "glass"), [Ff.p(PU0 + 2.5, H(1.4), 0.05), Ff.p(PU1 - 2.5, H(1.4), 0.05), Ff.p(PU1 - 2.5, H(5.2), 0.05), Ff.p(PU0 + 2.5, H(5.2), 0.05)])   # the doors and windows under the portico
poly(bm_for(P, "dark"), [Ff.p(PU0, H(1.4), -4.0), Ff.p(PU1, H(1.4), -4.0), Ff.p(PU1, H(9), -4.0), Ff.p(PU0, H(9), -4.0)])
pbox(bm_for(P, "forte"), Ff, PU0 - 1.0, PU1 + 1.0, H(11.6), H(12.2), 0, 0.45)                     # over the arches
pbox(bm_for(P, "pinkband"), Ff, PU0, PU1, H(9.8), H(11.2), 0, 0.02)                               # the spandrels' red panels
pbox(bm_for(P, "slate"), Ff, PU0 + 1.2, PU1 - 1.2, H(13.4), H(15.4), 0, 0.08)                     # BIBLIOTECA NAZIONALE CENTRALE
pbox(bm_for(P, "forte"), Ff, PU0 + 0.9, PU1 - 0.9, H(13.1), H(15.7), 0, 0.04)
pbox(bm_for(P, "forte"), Ff, -0.4, Lf + 0.4, H(18.8), H(20.0), 0, 1.0)                            # the main cornice
for u in (PU0 - 0.2, PU1 + 0.2):                                                                   # arms of Florence and Savoy
    pbox(bm_for(P, "marble"), Ff, u - 0.9, u + 0.9, H(9.6), H(11.6), 0, 0.35)
# the towers' feet on the front: two storeys of paired windows each side of the portico
for (u0, u1) in ((0.0, PU0), (PU1, Lf)):
    uc = (u0 + u1) / 2
    for (v0, v1) in ((H(2.4), H(4.8)), (H(6.6), H(10.4)), (H(12.8), H(16.0))):
        for du in (-0.9, 0.9):
            poly(bm_for(P, "glass"), [Ff.p(uc + du - 0.6, v0, 0.04), Ff.p(uc + du + 0.6, v0, 0.04), Ff.p(uc + du + 0.6, v1, 0.04), Ff.p(uc + du - 0.6, v1, 0.04)])
        pbox(bm_for(P, "fortedk"), Ff, uc - 1.8, uc + 1.8, v0 - 0.3, v0, 0, 0.22); pbox(bm_for(P, "fortedk"), Ff, uc - 1.8, uc + 1.8, v1, v1 + 0.45, 0, 0.25)
        for du in (-1.6, 0, 1.6): pbox(bm_for(P, "fortedk"), Ff, uc + du - 0.12, uc + du + 0.12, v0, v1, 0, 0.18)
    for v in (H(5.6), H(11.9)): pbox(bm_for(P, "forte"), Ff, u0, u1, v - 0.35, v, 0, 0.3)
# the sides of the central block
for (a, ins) in ((CB[0], (78, -3)), (CB[1], (78, -3))):
    F, L = V.frame(a, CB[2], a, CB[3], inside=ins); wing_face(P, F, L, top=20.0, bays=3.6)
# the towers: shaft from the cornice, an arch on each face, a statue in the front one, cornice and a low roof
for (t0, t1), who in zip(TOW, ("Dante", "Galileo")):
    TW = V.rect(t0, t1, -8.5, -0.5)
    V.prism(P, "forte", TW, H(20.0), H(29.6), top_mat="roof")
    V.hip(P, "roof", t0, t1, -8.5, -0.5, H(30.4), H(33.0), over=0.9)
    for F, L, p0, p1 in V.edges(TW):
        arch_fill(P, "dark", F, L / 2 - 1.7, L / 2 + 1.7, H(21.6), H(26.6), n=0.03)
        ring(P, "forte", F, L / 2, H(26.6), 1.7, 2.1, 0, 0.3, seg=12)
        pbox(bm_for(P, "forte"), F, -0.6, L + 0.6, H(29.6), H(30.5), 0, 1.0)                    # the deep cornice
        pbox(bm_for(P, "forte"), F, -0.2, L + 0.2, H(20.0), H(20.6), 0, 0.4)
        pbox(bm_for(P, "slate"), F, L / 2 - 1.4, L / 2 + 1.4, H(20.8), H(21.4), 0, 0.06)      # the verse under the niche
        for s_ in (-1, 1): cylinder(P, "forte", F.p(L / 2 + s_ * 1.25, 0, 0.25), 0.16, H(21.6), H(25.4), seg=8)
    Fs, Ls = V.frame(t0, -8.5, t1, -8.5, inside=((t0 + t1) / 2, -4))
    c = Fs.p(Ls / 2, 0, -0.7)                                                                          # the bronze statue in the niche
    cone(P, "bronze", c, 0.55, 0.32, H(21.7), H(24.6), seg=10); sphere(P, "bronze", c + Vector((0, 0, H(24.95))), 0.24)
    pbox(bm_for(P, "forte"), Fs, Ls / 2 - 0.8, Ls / 2 + 0.8, H(21.3), H(21.7), -1.4, 0)
# the steps and the paving before the portico
for k in range(6):
    pbox(bm_for(P, "fortedk"), Ff, PU0 - 2.0, PU1 + 2.0, G - 0.6 + k * 0.17, G - 0.43 + k * 0.17, 0.0, 3.4 - k * 0.5)
# ------------------------------------------------------------------ the works (1911–1934): the shell under scaffolding, *inferred* look
V.prism(CW, "forte", V.rect(23.4, 132.0, -3.0, 14.0), B0, H(12.0), top_mat="dark")
V.prism(CW, "forte", V.rect(58.0, 98.0, -8.5, 2.0), B0, H(14.0), top_mat="dark")
K.export("biblioteca")
