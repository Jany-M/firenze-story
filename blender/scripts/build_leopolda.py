"""Stazione Leopolda – Florence's first railway terminus (v1, rebuilt from the historical views and the DSM).

Run:  python pipeline/47_moderni.py ; blender -b --python blender/scripts/build_leopolda.py → web/public/models/landmarks/leopolda.glb
Frame: a along the head towards Porta al Prato from its north corner (OSM way 269666091; a grows southwards), o inwards
along the train shed (west-north-west). Ground 4.2 m (scene).
Measured (LiDAR 2023 DSM, height above the ground, read in this frame – _dev/tmp/asc_leo.txt): the head o 0..12 across
a -1..45, 8–9 m in front (o 0..6), 11–13 m behind; the shed o 12..110 under three parallel gabled roofs (ridges ≈11 m,
valleys 8–9 m; each ≈15 m wide); along its south side a strip a 43..53, 17–19 m for o 12..56, 8–10 m beyond; the west
end o 110..160 over the whole width, 14–16 m with 17–19 m blocks at both corners and an 18–19 m attic on its end.
From the views: "Veduta prospettica della stazione di Firenze della strada ferrata Leopolda" (c. 1850, public domain):
a tall rusticated end block with three great arches for the tracks and two small gatehouses before it, a long
one-storey arcade with lunette windows along the side of the shed, the shed walls with a row of round windows under the
eaves, a two-storey wing with rectangular windows; the photograph of 1861 (public domain) and the painting of the 1861
Exhibition: the head turned into the Exhibition's entrance, a portico of seven arches under a pediment with statues.
Today (photographs Freepenguin, sailko): the arches of the head stand in ochre plaster behind a forecourt with a steel
pergola on concrete piers.
History: by Enrico Presenti for Leopold II, opened 2 June 1848 (Museo Galileo); last passenger train 1860; the first
Italian National Exhibition 1861 (Giuseppe Martelli's entrance); workshops and stores; events hall today.
Dates *inferred*: the side arcade shown to 1900 (no longer in the DSM); the pediment of 1861 shown to 1900 (gone in
modern photographs); the pergola from 1997.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from landmark_detail import *
from landmark_church import Site, extra_materials
from landmark_volume import Vol, glass_wall, punched, arched_row, tracks
from mathutils import Vector
K.reset()
MAT["plaster"] = material("plaster_leopolda", "intonaco", (0.86, 0.78, 0.62), 0.9, 0.25, tint=(1.0, 0.93, 0.8))
MAT["rustic"] = material("rusticated_stone", "pietra_forte", (0.7, 0.62, 0.5), 0.85, 0.35, tint=(2.2, 2.2, 2.05))
MAT["serena"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)
MAT["steel"] = material("pergola_steel", None, (0.3, 0.36, 0.32), 0.6, metal=0.5)
MAT["concrete"] = material("concrete", None, (0.74, 0.72, 0.68), 0.9)
MAT["ballast"] = material("track_ballast", None, (0.33, 0.3, 0.27), 1.0)
MAT["rail"] = material("rail_steel", None, (0.46, 0.44, 0.42), 0.4, metal=0.7)
extra_materials()
NOW = K.NOW
S = Site("leopolda", "moderni"); G = S.G; V = Vol(S)
ST = f"stazione_leopolda@1848-{NOW}"; ARC = "portico_laterale@1848-1900"; EXPO = "fronte_esposizione@1861-1900"
PORT = f"portico_testata@1861-{NOW}"; HEAD0 = "testata@1848-1861"; PERG = f"pergola@1997-{NOW}"; RAIL = "binari_leopolda@1848-1860"
def H(z): return G + z
def walls(part, pts, h, mat="plaster", cornice=True, top_mat="roof"):
    V.prism(part, mat, pts, G - 0.3, h, top=False)
    E = V.edges(pts)
    if cornice:
        for F, L, p0, p1 in E: pbox(bm_for(part, "serena"), F, -0.2, L + 0.2, h - 0.45, h, 0, 0.4)
    return E

# ------------------------------------------------------------------ the train shed: three gabled roofs side by side
SHED_A = [(-1.0, 13.0), (13.0, 28.0), (28.0, 43.0)]
walls(ST, V.rect(-1.0, 43.0, 12.0, 110.0), H(8.6))
for a0, a1 in SHED_A:
    V.gable(ST, "roof", a0, a1, 12.0, 110.0, H(8.6), H(11.2), along="o", over=0.3, gable_mat="plaster")
Fn, Ln = V.frame(-1.0, 12.0, -1.0, 110.0, inside=(20, 60))       # the north wall: a row of round windows under the eaves
arched_row(ST, Fn, 2, Ln - 2, H(5.4), H(7.0), 1.6, 4.9, fill="dark", frame="serena", fw=0.22)
for o in range(14, 110, 5):                                       # pilaster strips between the bays
    pbox(bm_for(ST, "plaster"), Frame(V.W(-1.0, o), S.NO, -S.TA), -0.3, 0.3, G, H(8.2), 0, 0.2)
# the south wing: two tall storeys for 44 m from the head, one storey beyond (DSM)
for (o0, o1, h) in ((12.0, 56.0, H(17.0)), (56.0, 110.0, H(9.0))):
    walls(ST, V.rect(43.0, 53.0, o0, o1), h)
    V.hip(ST, "roof", 43.0, 53.0, o0, o1, h, h + 1.8, over=0.5)
    Fs, Ls = V.frame(53.0, o0, 53.0, o1, inside=(48, (o0 + o1) / 2))
    punched(ST, Fs, 1.5, Ls - 1.5, H(1.0), H(3.6), 1.3, 3.6, fill="dark", frame="serena")
    if h > H(12):
        pbox(bm_for(ST, "serena"), Fs, 0, Ls, H(8.4), H(8.7), 0, 0.25)
        punched(ST, Fs, 1.5, Ls - 1.5, H(10.0), H(13.0), 1.3, 3.6, fill="dark", frame="serena")
# the west end: the tracks' portal block, rusticated, three great arches, taller corner blocks (DSM; the view of c. 1850)
walls(ST, V.rect(-1.0, 53.0, 110.0, 160.0), H(15.2))
V.hip(ST, "roof", 9.0, 43.0, 110.0, 160.0, H(15.2), H(17.0), over=0.3)
for (a0, a1) in ((-1.0, 9.0), (43.0, 53.0)):
    walls(ST, V.rect(a0, a1, 110.0, 160.0), H(18.2))
    V.hip(ST, "roof", a0, a1, 110.0, 160.0, H(18.2), H(19.4), over=0.4)
Fw, Lw = V.frame(53.0, 160.0, -1.0, 160.0, inside=(26, 130))     # its end towards Livorno
pbox(bm_for(ST, "rustic"), Fw, 0, Lw, G, H(18.2), 0, 0.25)
for k in range(int(18.0 / 0.9)):                                 # rustication courses
    pbox(bm_for(ST, "serena"), Fw, 0, Lw, G + k * 0.9, G + k * 0.9 + 0.06, 0, 0.3)
for u in (Lw / 2 - 12.0, Lw / 2, Lw / 2 + 12.0):                 # the three great arches for the tracks
    arch_fill(ST, "dark", Fw, u - 4.2, u + 4.2, G, H(7.6), n=0.3)
    ring(ST, "rustic", Fw, u, H(7.6), 4.2, 5.4, 0.25, 0.5, seg=14)
pbox(bm_for(ST, "serena"), Fw, -0.2, Lw + 0.2, H(14.6), H(15.4), 0, 0.6)                    # the heavy attic
for (a, ins) in ((-1.0, (20, 130)), (53.0, (20, 130))):          # its sides: arched windows on two storeys
    Fx, Lx = V.frame(a, 110.0, a, 160.0, inside=ins)
    arched_row(ST, Fx, 2, Lx - 2, H(1.0), H(4.2), 1.6, 5.0, fill="dark", frame="serena")
    arched_row(ST, Fx, 2, Lx - 2, H(8.0), H(11.4), 1.5, 5.0, fill="dark", frame="serena")
    pbox(bm_for(ST, "serena"), Fx, 0, Lx, H(6.6), H(6.9), 0, 0.25)
for a in (8.0, 36.0):                                             # the two small gatehouses before it
    gc = V.W(a, 176.0)
    octagon_prism(ST, "plaster", gc, 2.4, G - 0.2, H(4.6), rot=0.0)
    cone(ST, "roof", gc, 2.9, 0.3, H(4.6), H(6.0), seg=8)
# ------------------------------------------------------------------ the head towards Porta al Prato
walls(ST, V.rect(-1.0, 45.0, 6.0, 12.0), H(12.4))
V.hip(ST, "roof", -1.0, 45.0, 6.0, 12.0, H(12.4), H(14.0), over=0.4)
Fh, Lh = V.frame(-1.0, 6.0, 45.0, 6.0, inside=(22, 10))
punched(ST, Fh, 1.5, Lh - 1.5, H(9.4), H(11.6), 1.2, 3.8, fill="dark", frame="serena")    # upper windows above the portico
# 1848–1861: the head as built – a plain two-storey front with a central doorway
V.prism(HEAD0, "plaster", V.rect(-1.0, 45.0, 0.0, 6.0), G - 0.3, H(8.6), top_mat="roof")
F0, L0 = V.frame(-1.0, 0.0, 45.0, 0.0, inside=(22, 3))
arched_row(HEAD0, F0, 1.5, L0 - 1.5, G + 0.1, H(3.4), 1.8, 4.6, fill="dark", frame="serena")
punched(HEAD0, F0, 1.5, L0 - 1.5, H(5.2), H(7.2), 1.2, 4.6, fill="dark", frame="serena")
pbox(bm_for(HEAD0, "serena"), F0, -0.2, L0 + 0.2, H(8.2), H(8.6), 0, 0.4)
# 1861: the Exhibition's entrance – a portico of seven arches (still standing), its pediment and statues (to 1900 *inferred*)
V.prism(PORT, "plaster", V.rect(3.0, 41.0, 0.0, 6.0), G - 0.3, H(8.8), top_mat="roof")
Fp, Lp = V.frame(3.0, 0.0, 41.0, 0.0, inside=(22, 3))
for i in range(7):
    u = (i + 0.5) * Lp / 7
    arch_fill(PORT, "dark", Fp, u - 2.0, u + 2.0, G, H(5.2), n=0.04)
    ring(PORT, "serena", Fp, u, H(5.2), 2.0, 2.35, 0.04, 0.2, seg=12)
for i in range(8):
    pbox(bm_for(PORT, "plaster"), Fp, i * Lp / 7 - 0.5, i * Lp / 7 + 0.5, G, H(7.4), 0, 0.3)   # piers / pilasters
pbox(bm_for(PORT, "serena"), Fp, -0.3, Lp + 0.3, H(7.4), H(8.8), 0, 0.5)
for (a0, a1) in ((-1.0, 3.0), (41.0, 45.0)):                       # the corners beside the portico
    V.prism(PORT, "plaster", V.rect(a0, a1, 0.0, 6.0), G - 0.3, H(8.8), top_mat="roof")
Fe, Le = V.frame(3.0, -0.6, 41.0, -0.6, inside=(22, 3))
poly(bm_for(EXPO, "plaster"), [Fe.p(0, H(8.8), 0), Fe.p(Le, H(8.8), 0), Fe.p(Le / 2, H(13.6), 0)])
pbox(bm_for(EXPO, "serena"), Fe, -0.3, Le + 0.3, H(8.8), H(9.3), 0, 0.5)
for k in range(12):                                               # the raking cornices
    t0, t1 = k / 12, (k + 1) / 12
    for s_ in (-1, 1):
        x0, x1 = Le / 2 + s_ * Le / 2 * (1 - t0), Le / 2 + s_ * Le / 2 * (1 - t1)
        poly(bm_for(EXPO, "serena"), [Fe.p(x0, H(8.8) + 4.8 * t0, 0.45), Fe.p(x1, H(8.8) + 4.8 * t1, 0.45), Fe.p(x1, H(9.2) + 4.8 * t1, 0.45), Fe.p(x0, H(9.2) + 4.8 * t0, 0.45)])
for u in (0.5, Le / 2, Le - 0.5):                                 # statues on the pediment
    vv = H(13.6) if u == Le / 2 else H(9.3)
    pbox(bm_for(EXPO, "marble"), Fe, u - 0.35, u + 0.35, vv, vv + 2.0, -0.3, 0.3)
    sphere(EXPO, "marble", Fe.p(u, vv + 2.3, 0), 0.3)
poly(bm_for(EXPO, "dark"), [Fe.p(6, H(7.6), 0.52), Fe.p(Le - 6, H(7.6), 0.52), Fe.p(Le - 6, H(8.5), 0.52), Fe.p(6, H(8.5), 0.52)])   # the inscription band
# ------------------------------------------------------------------ the arcade along the north side (view of c. 1850; to 1900 *inferred*)
V.prism(ARC, "plaster", V.rect(-6.0, -1.0, 12.0, 108.0), H(5.6), H(6.6), top=True, bottom=True)
V.gable(ARC, "roof", -6.0, -1.0, 12.0, 108.0, H(6.6), H(7.0), along="o", over=0.2)
Fa, La = V.frame(-6.0, 12.0, -6.0, 108.0, inside=(10, 60))
for k in range(int(La / 4.0)):
    u = (k + 0.5) * La / int(La / 4.0)
    arch_fill(ARC, "dark", Fa, u - 1.5, u + 1.5, G, H(4.0), n=0.04)
    ring(ARC, "serena", Fa, u, H(4.0), 1.5, 1.75, 0.04, 0.18, seg=10)
for k in range(int(La / 4.0) + 1):
    pbox(bm_for(ARC, "plaster"), Fa, k * La / int(La / 4.0) - 0.5, k * La / int(La / 4.0) + 0.5, G, H(5.6), 0, 0.05)
pbox(bm_for(ARC, "plaster"), Fa, 0, La, H(5.5), H(6.6), 0, 0.05)
# ------------------------------------------------------------------ the tracks out of the portal (1848–1860)
tracks(V, RAIL, lambda o: 14.0, 160, 300, 3, pitch=12.0, g=G)
# ------------------------------------------------------------------ today: the forecourt's steel pergola on concrete piers
for a in range(2, 44, 8):
    for o in (-20.0, -6.0):
        pbox(bm_for(PERG, "concrete"), Frame(V.W(a, o), S.TA, S.NO), -0.5, 0.5, G, H(7.2), -0.5, 0.5)
    for o in (-16.0, -11.0):
        cylinder(PERG, "steel", V.W(a, o), 0.22, G, H(6.6), seg=8)
    pbox(bm_for(PERG, "steel"), Frame(V.W(a, -20.0), S.NO, -S.TA), 0, 14.0, H(6.6), H(7.2), -0.15, 0.15)
for o in (-16.0, -11.0):
    pbox(bm_for(PERG, "steel"), Frame(V.W(2.0, o), S.TA, S.NO), 0, 40.0, H(7.2), H(7.6), -0.15, 0.15)
K.export("leopolda")
