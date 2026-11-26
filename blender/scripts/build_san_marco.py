"""Basilica di San Marco and the former convent (Museo di San Marco) on Piazza San Marco (v1).

Run:  python pipeline/45_chiese.py   (once: outlines, ground, DSM raster → blender/data/chiese.json)
      blender -b --python blender/scripts/build_san_marco.py  →  web/public/models/landmarks/san_marco.glb
Frame: absolute scene coordinates; inside the script a along the church front (20.9 m, OSM way 225706552) from its
south-west corner, o inwards (north-east) along the nave.
Measured (LiDAR 2023 DSM, ground 10.5 m scene): the front ≈29.5 m to the top of its cross; the nave's roof ridge ≈22.7 m
above the square for 34 m; Silvani's tribune behind it (o 34–48) to ≈26 m; the bell tower at a 17, o 46, ≈35 m. The
convent (OSM relation 1575764): buildings massed from the 1 m DSM raster (landmark_mass.py).
Front from photographs (Sailko 2022, Zairon 2023 – from the square and from Giotto's tower): Paladini's front of 1777–78 –
two orders of fluted Corinthian pilasters (doubled each side of the middle bay) on a stone plinth; the portal between two
columns with a segmental pediment and the sculpted group over it; statues in arched niches under triangular pediments in the
side bays; the upper order with a window between columns under a segmental pediment and garlanded cartouches at the sides;
the attic between the paired pilasters with the relief panel, its flanks sweeping down in concave curves to urns on
pedestals over the outer bays; the triangular pediment with a cartouche and the iron cross. Proportions from the photographs
scaled to the DSM (the cross at ≈31 m) – *inferred*.
Also from Zairon's view: the chapel block with a hipped roof and a small lantern on the left side (Giambologna's chapel of
Sant'Antonino, 1579–89 – identified by its place, *inferred*), the bell tower's tall pointed roof. The convent's front on the
square (Sailko 2022): two storeys of framed windows, a pedimented door near the church.
Dates (docs/landmarks/SAN-MARCO.md): the Silvestrine church (shown from 1300, *inferred*) until Michelozzo's rebuilding for Cosimo
il Vecchio, 1437–43 (consecrated at Epiphany 1443); the convent rebuilt 1439–44 (shown 1444); bell tower 1512 (Baccio d'Agnolo);
Silvani's tribune from 1679; the front 1777–78.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from mathutils import Vector
from landmark_detail import *
from landmark_church import Site, slab, figure, extra_materials, bed, statue, bench
import numpy as np
K.reset()
MAT["plaster"] = material("plaster_cream", "intonaco", (0.88, 0.82, 0.7), 0.9, 0.4, tint=(1.32, 1.2, 1.0))
MAT["serena"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)
MAT["dress"] = material("stucco_stone", None, (0.72, 0.66, 0.55), 0.8)
MAT["wall"] = material("stucco_wall", None, (0.88, 0.83, 0.71), 0.9)
MAT["marble"] = material("marble_white", None, (0.9, 0.89, 0.86), 0.5)
extra_materials()
MAT["conv"] = material("plaster_convent", None, (0.9, 0.85, 0.72), 0.9)
NOW = K.NOW
S = Site("marco"); G = S.G; L = S.L; F = S.front()
NAVE = (3.5, 17.5); RIDGE = 33.2; EAVE = 30.2
TOWER_A, TOWER_O = 16.6, 45.6                    # the tower's square in the 0.5 m DSM (a 15–18, o 44–47)

# the church before Michelozzo (*inferred* size), then his nave
S.hall("chiesa_silvestrini@1300-1443", 4.0, 17.0, 1.0, 34.0, G - 0.5, G + 12.0, G + 15.0)
S.hall(f"navata@1443-{NOW}", NAVE[0], NAVE[1], 0.6, 34.0, G - 0.5, EAVE, RIDGE, gables=(False, True))
# Michelozzo's front (plain gable, *inferred*), 1443–1777
slab("facciata_michelozzo@1443-1778", "plaster", F, [(NAVE[0] - 0.5, G - 0.5), (NAVE[1] + 0.5, G - 0.5), (NAVE[1] + 0.5, EAVE), ((NAVE[0] + NAVE[1]) / 2, RIDGE + 0.4), (NAVE[0] - 0.5, EAVE)], -0.9, 0.0)
pp = "facciata_michelozzo@1443-1778"
poly(bm_for(pp, "wood"), [F.p(L / 2 - 1.3, G, 0.03), F.p(L / 2 + 1.3, G, 0.03), F.p(L / 2 + 1.3, G + 5.0, 0.03), F.p(L / 2 - 1.3, G + 5.0, 0.03)])
oculus(pp, F, L / 2, G + 13.0, 1.3, frame="serena", fill="glass", fw=0.4)

# Paladini's front, 1777–78 (proportions from Sailko 2022 and Zairon 2023, scaled to the DSM: the cross at ≈31 m)
MAT["shade"] = material("niche_shade", None, (0.45, 0.42, 0.37), 0.9)
MAT["iron"] = material("wrought_iron", None, (0.08, 0.08, 0.08), 0.6, metal=0.6)
fp = f"facciata@1778-{NOW}"
H1, H2, HA, H3 = G + 11.9, G + 20.5, G + 25.3, G + 28.3     # lower order, upper order, attic, pediment apex
box(bm_for(fp, "wall"), F, 0, L, G - 0.6, H2, -0.9, 0.0)
mid0, mid1 = L / 2 - 2.6, L / 2 + 2.6
PIL = [0.7, mid0 - 0.55, mid0 + 0.35, mid1 - 0.35, mid1 + 0.55, L - 0.7]
def pilasters(v0, v1, us, w=0.9, n0=0.0):
    for u in us:
        pbox(bm_for(fp, "dress"), F, u - w / 2, u + w / 2, v0, v1, n0, n0 + 0.45)
        for f_ in (-0.25, 0, 0.25): pbox(bm_for(fp, "shade"), F, u + f_ - 0.03, u + f_ + 0.03, v0 + 1.0, v1 - 1.2, n0 + 0.45, n0 + 0.46)
        pbox(bm_for(fp, "dress"), F, u - w / 2 - 0.12, u + w / 2 + 0.12, v1 - 1.0, v1, n0, n0 + 0.62)          # Corinthian capital
        for k in range(3): pbox(bm_for(fp, "dress"), F, u - w / 2 - 0.05, u + w / 2 + 0.05, v1 - 0.9 + k * 0.3, v1 - 0.78 + k * 0.3, n0 + 0.6, n0 + 0.7)
for (u0, u1) in ((-0.2, L / 2 - 1.8), (L / 2 + 1.8, L + 0.2)): pbox(bm_for(fp, "serena"), F, u0, u1, G - 0.6, G + 1.4, 0, 0.6)   # plinth
pilasters(G + 1.4, H1 - 1.3, PIL)
entablature(fp, F, -0.3, L + 0.3, H1 - 1.3, mat="dress", h=1.3, proj=0.9)
pilasters(H1 + 0.2, H2 - 1.1, PIL, w=0.8)
entablature(fp, F, -0.2, L + 0.2, H2 - 1.1, mat="dress", h=1.1, proj=0.8)
# portal: stone frame, segmental pediment, the group of the lion of St Mark with cherubs over it
poly(bm_for(fp, "wood"), [F.p(L / 2 - 1.3, G, 0.6), F.p(L / 2 + 1.3, G, 0.6), F.p(L / 2 + 1.3, G + 5.4, 0.6), F.p(L / 2 - 1.3, G + 5.4, 0.6)])
for (u0, u1, v0, v1) in ((L / 2 - 1.8, L / 2 - 1.3, G, G + 5.9), (L / 2 + 1.3, L / 2 + 1.8, G, G + 5.9), (L / 2 - 1.8, L / 2 + 1.8, G + 5.4, G + 5.9)):
    pbox(bm_for(fp, "serena"), F, u0, u1, v0, v1, 0, 0.75)
for s_ in (-1, 1): cylinder(fp, "dress", F.p(L / 2 + s_ * 2.15, 0, 0.75), 0.22, G + 0.2, G + 5.9, seg=10)
pbox(bm_for(fp, "dress"), F, L / 2 - 2.5, L / 2 + 2.5, G + 5.9, G + 6.4, 0.3, 1.0)
ring(fp, "dress", F, L / 2, G + 6.0, 2.2, 2.55, 0.3, 1.0, a0=0.3, a1=math.pi - 0.3, seg=10, soffit=False)
figure(fp, F, L / 2 - 0.5, G + 6.9, 1.4, n=0.7, mat="marble"); figure(fp, F, L / 2 + 0.5, G + 6.9, 1.2, n=0.7, mat="marble")
box(bm_for(fp, "marble"), F, L / 2 - 0.9, L / 2 + 0.9, G + 6.6, G + 7.3, 0.4, 0.9)
# side bays: statues in arched niches under triangular pediments; upper sides: garlanded cartouches
for uc in ((0.7 + mid0 - 0.55) / 2, (mid1 + 0.55 + L - 0.7) / 2):
    arch_fill(fp, "shade", F, uc - 0.7, uc + 0.7, G + 3.0, G + 5.6, n=0.02)
    figure(fp, F, uc, G + 3.1, 2.2, n=0.1, mat="marble")
    pbox(bm_for(fp, "dress"), F, uc - 1.0, uc + 1.0, G + 2.8, G + 3.05, 0, 0.35)
    for s_ in (-1, 1): pbox(bm_for(fp, "dress"), F, uc + s_ * 0.95 - 0.15, uc + s_ * 0.95 + 0.15, G + 3.0, G + 6.3, 0, 0.18)
    pbox(bm_for(fp, "dress"), F, uc - 1.15, uc + 1.15, G + 6.3, G + 6.5, 0, 0.3)
    poly(bm_for(fp, "dress"), [F.p(uc - 1.2, G + 6.5, 0.3), F.p(uc + 1.2, G + 6.5, 0.3), F.p(uc, G + 7.3, 0.3)])
    ring(fp, "dress", F, uc, H1 + 4.4, 0.8, 1.0, 0, 0.2, a0=0, a1=2 * math.pi, seg=14, soffit=False)          # cartouche
    pbox(bm_for(fp, "dress"), F, uc - 0.5, uc + 0.5, H1 + 3.9, H1 + 4.9, 0, 0.12)
    for k in range(5):                                                                                       # the hanging garland
        t = k / 4; pbox(bm_for(fp, "dress"), F, uc - 0.9 + 1.8 * t - 0.12, uc - 0.9 + 1.8 * t + 0.12, H1 + 3.0 - 0.6 * math.sin(math.pi * t), H1 + 3.3 - 0.6 * math.sin(math.pi * t), 0.05, 0.25)
# the upper middle: a window between two columns under a segmental pediment
win_rect(fp, F, L / 2, H1 + 2.4, H1 + 6.4, 1.6, frame="dress", fill="glass", fw=0.25)
for s_ in (-1, 1): cylinder(fp, "dress", F.p(L / 2 + s_ * 1.3, 0, 0.3), 0.18, H1 + 2.1, H1 + 6.7, seg=10)
pbox(bm_for(fp, "dress"), F, L / 2 - 1.7, L / 2 + 1.7, H1 + 6.7, H1 + 7.1, 0, 0.45)
ring(fp, "dress", F, L / 2, H1 + 6.6, 1.55, 1.85, 0, 0.4, a0=0.25, a1=math.pi - 0.25, seg=10, soffit=False)
pbox(bm_for(fp, "dress"), F, L / 2 - 1.3, L / 2 + 1.3, H1 + 2.0, H1 + 2.4, 0, 0.3)
# the attic: between the paired pilasters, with fluted pilaster pairs and the relief panel; its flanks sweep down in
# concave curves to the outer bays, where urns stand on pedestals; the triangular pediment, its cartouche and the cross
A0, A1 = PIL[1] - 0.5, PIL[4] + 0.5
sweep = [(A0 - (A0 - 1.4) * t, HA - 0.6 - (HA - 0.6 - H2 - 0.9) * math.sin(math.pi / 2 * t) ** 0.7) for t in [k / 10 for k in range(11)]]
outline = [(1.4, H2), (L - 1.4, H2)] + [(L - u, v) for u, v in sweep[::-1]] + [(A1, HA), (A0, HA)] + sweep
from landmark_church import slab as _slab
_slab(fp, "wall", F, outline, -0.6, 0.15)
pilasters(H2, HA - 0.6, [PIL[1], PIL[2], PIL[3], PIL[4]], w=0.7, n0=0.15)
pbox(bm_for(fp, "marble"), F, L / 2 - 1.75, L / 2 + 1.75, H2 + 0.8, H2 + 3.4, 0.15, 0.3)                    # the relief
for k in range(4): box(bm_for(fp, "marble"), F, L / 2 - 1.3 + k * 0.85, L / 2 - 1.0 + k * 0.85, H2 + 1.0, H2 + 2.6 - 0.2 * (k % 2), 0.3, 0.5)
entablature(fp, F, A0 - 0.2, A1 + 0.2, HA - 0.6, mat="dress", h=0.6, proj=0.7)
poly(bm_for(fp, "wall"), [F.p(A0 - 0.2, HA, 0.15), F.p(A1 + 0.2, HA, 0.15), F.p(L / 2, H3, 0.15)])
bm = bm_for(fp, "dress")
for (u0, v0), (u1, v1) in (((A0 - 0.4, HA - 0.05), (L / 2, H3 + 0.15)), ((L / 2, H3 + 0.15), (A1 + 0.4, HA - 0.05))):
    poly(bm, [F.p(u0, v0, 0.15), F.p(u1, v1, 0.15), F.p(u1, v1 + 0.4, 0.8), F.p(u0, v0 + 0.4, 0.8)])
ring(fp, "dress", F, L / 2, H3 + 0.3, 0.35, 0.6, 0, 0.2, a0=0, a1=2 * math.pi, seg=12, soffit=False)
box(bm_for(fp, "iron"), F, L / 2 - 0.06, L / 2 + 0.06, H3 + 0.6, H3 + 2.6, 0.0, 0.12); box(bm_for(fp, "iron"), F, L / 2 - 0.6, L / 2 + 0.6, H3 + 1.8, H3 + 1.92, 0.0, 0.12)
for u in (0.7, L - 0.7):                                                                                     # urns with flames
    box(bm_for(fp, "dress"), F, u - 0.45, u + 0.45, H2, H2 + 1.0, -0.4, 0.5)
    cylinder(fp, "dress", F.p(u, 0, 0.05), 0.32, H2 + 1.0, H2 + 1.9, seg=10); cone(fp, "dress", F.p(u, 0, 0.05), 0.3, 0.04, H2 + 1.9, H2 + 2.8, seg=10)

# the chapel on the left side with its hipped roof and lantern (DSM a −13…−1, o 24…36; seen in Zairon's view from Giotto's
# tower) – Giambologna's chapel of Sant'Antonino, 1579–89 (identification *inferred* from its place on the left side)
CP = f"cappella_salviati@1589-{NOW}"
Fc = Frame(S.W(-13.0, 24.0), S.TA, S.NO)
box(bm_for(CP, "plaster"), Fc, 0, 12.0, G - 0.5, G + 15.5, 0, 12.0)
for (o_, u_, n_, Lf) in ((S.W(-13.0, 24.0), S.TA, -S.NO, 12.0), (S.W(-13.0, 36.0), -S.NO, -S.TA, 12.0)):
    Ff = Frame(o_, u_, n_)
    pbox(bm_for(CP, "serena"), Ff, -0.1, Lf + 0.1, G + 15.0, G + 15.5, 0, 0.4)
    ring(CP, "serena", Ff, Lf / 2, G + 11.0, 1.5, 1.75, 0, 0.12, seg=12, soffit=False)
    arch_fill(CP, "glass", Ff, Lf / 2 - 1.5, Lf / 2 + 1.5, G + 11.0, G + 11.0, n=0.03)
cc = S.W(-7.0, 30.0); bmr = bm_for(CP, "roof")
cs_ = [S.W(-13.4, 23.6, G + 15.5), S.W(-0.6, 23.6, G + 15.5), S.W(-0.6, 36.4, G + 15.5), S.W(-13.4, 36.4, G + 15.5)]
for p0, p1 in zip(cs_, cs_[1:] + cs_[:1]): poly(bmr, [p0, p1, cc + Vector((0, 0, G + 18.4))])
cylinder(CP, "plaster", cc, 0.9, G + 17.6, G + 19.4, seg=8); cone(CP, "lead", cc, 1.05, 0.1, G + 19.4, G + 20.6, seg=8)

# the convent's front on the square (a 20.9–60.3 along the same line): two storeys of framed windows, the museum's door
CV = f"convento_fronte@1444-{NOW}"
Fv = Frame(S.W(20.9, 0.0), S.TA, -S.NO); Lv = 39.4
box(bm_for(CV, "plaster"), Fv, 0, Lv, G - 0.5, G + 13.0, -0.6, 0.0)
pbox(bm_for(CV, "serena"), Fv, 0, Lv, G - 0.5, G + 0.6, 0, 0.1)
pbox(bm_for(CV, "serena"), Fv, 0, Lv, G + 5.6, G + 5.8, 0, 0.12)
pbox(bm_for(CV, "plaster"), Fv, -0.1, Lv + 0.1, G + 12.6, G + 13.0, 0, 0.45)
n = int(Lv / 4.3)
for k in range(n):
    u = (k + 0.5) * Lv / n
    if k == 0:                                                             # the door, with a pediment
        poly(bm_for(CV, "wood"), [Fv.p(u - 0.9, G, 0.05), Fv.p(u + 0.9, G, 0.05), Fv.p(u + 0.9, G + 3.4, 0.05), Fv.p(u - 0.9, G + 3.4, 0.05)])
        for (u0, u1, v0, v1) in ((u - 1.25, u - 0.9, G, G + 3.75), (u + 0.9, u + 1.25, G, G + 3.75), (u - 0.9, u + 0.9, G + 3.4, G + 3.75)):
            pbox(bm_for(CV, "serena"), Fv, u0, u1, v0, v1, 0, 0.14)
        poly(bm_for(CV, "serena"), [Fv.p(u - 1.5, G + 3.9, 0.2), Fv.p(u + 1.5, G + 3.9, 0.2), Fv.p(u, G + 4.7, 0.2)])
    else:
        win_rect(CV, Fv, u, G + 2.2, G + 4.0, 0.9, frame="serena", fill="dark", fw=0.15, grille=True)
    win_rect(CV, Fv, u, G + 7.4, G + 9.6, 1.0, frame="serena", fill="dark", fw=0.15, pediment="cornice")

# bell tower (Baccio d'Agnolo, 1512): plastered shaft, the belfry, a tall pointed pyramid (Zairon 2023; DSM peak ≈34.9 m)
S.campanile(f"campanile@1512-{NOW}", TOWER_A, TOWER_O, 4.4, G, G + 24.6, G + 28.8, G + 34.9, spire="pyramid")

# Silvani's tribune (1679) behind the nave: a hall a 4–19, o 33.5–47.5 under a hipped roof, its ridge ≈25.5 m above the
# square, the eaves ≈22.5 m; a lower apse room behind it (a 6–15, o 47.5–51.5, ≈17.5 m). All from the 0.5 m DSM;
# the windows are *inferred* (two round-headed windows a side, as on the nave)
def hipped(part, a0, a1, o0, o1, z, rise, mat="plaster"):
    box(bm_for(part, mat), Frame(S.W(a0, o0), S.TA, S.NO), 0, a1 - a0, G - 0.5, z, 0, o1 - o0)
    e = 0.45; hm = min(a1 - a0, o1 - o0) / 2; z1 = z + rise
    A_, B_, C_, D_ = S.W(a0 - e, o0 - e, z), S.W(a1 + e, o0 - e, z), S.W(a1 + e, o1 + e, z), S.W(a0 - e, o1 + e, z)
    rb = bm_for(part, "roof")
    if a1 - a0 >= o1 - o0:
        R0, R1 = S.W(a0 + hm, (o0 + o1) / 2, z1), S.W(a1 - hm, (o0 + o1) / 2, z1)
        for q in ([A_, B_, R1, R0], [C_, D_, R0, R1], [B_, C_, R1], [D_, A_, R0]): poly(rb, q)
    else:
        R0, R1 = S.W((a0 + a1) / 2, o0 + hm, z1), S.W((a0 + a1) / 2, o1 - hm, z1)
        for q in ([B_, C_, R1, R0], [D_, A_, R0, R1], [A_, B_, R0], [C_, D_, R1]): poly(rb, q)
    for (o_, u_, n_, Lf) in ((S.W(a0, o0), S.TA, -S.NO, a1 - a0), (S.W(a1, o1), -S.TA, S.NO, a1 - a0), (S.W(a0, o1), -S.NO, -S.TA, o1 - o0), (S.W(a1, o0), S.NO, S.TA, o1 - o0)):
        pbox(bm_for(part, "serena"), Frame(o_, u_, n_), -0.1, Lf + 0.1, z - 0.4, z, 0, 0.35)
TRB = (4.0, 19.0, 33.5, 47.5)
hipped(f"tribuna@1679-{NOW}", *TRB, G + 22.5, 3.0)
hipped(f"tribuna@1679-{NOW}", 6.0, 15.0, 47.5, 51.5, G + 16.0, 1.6)
for (o_, u_, n_) in ((S.W(TRB[0], TRB[3]), -S.NO, -S.TA), (S.W(TRB[1], TRB[2]), S.NO, S.TA)):
    Fw = Frame(o_, u_, n_)
    for uc in (4.5, 9.5):
        arch_fill(f"tribuna@1679-{NOW}", "dark", Fw, uc - 0.75, uc + 0.75, G + 15.5, G + 19.0, n=0.03)
        ring(f"tribuna@1679-{NOW}", "serena", Fw, uc, G + 19.0, 0.75, 0.95, 0, 0.1, seg=10, soffit=False)

# ---------------------------------------------------------------- the convent's cloisters (OSM relation 1575764, its courts)
def hole_box(h):
    A = [(p[0] - S.A[0]) * S.t[0] + (p[1] - S.A[1]) * S.t[1] for p in h]; O = [(p[0] - S.A[0]) * S.n[0] + (p[1] - S.A[1]) * S.n[1] for p in h]
    a0, a1, o0, o1 = min(A), max(A), min(O), max(O)
    gr = S.D["grid"]; ring = []; gg = []
    for j in range(gr["no"]):
        for i in range(gr["na"]):
            a_, o_ = gr["a0"] + i + 0.5, gr["o0"] + j + 0.5; hv = gr["h"][j][i]
            if hv is None: continue
            d = max(a0 - a_, a_ - a1, o0 - o_, o_ - o1)
            if 6 <= d <= 12: ring.append(hv)
            if d < -1: gg.append(gr["g"][j][i])
    return a0, a1, o0, o1, float(np.median(ring)) if ring else G + 12, float(np.median(gg)) if gg else G
courts = sorted((hole_box(h) for h in S.D["polys"][1][1]), key=lambda b: -(b[1] - b[0]) * (b[3] - b[2]))
CA = [b for b in courts[:2]]
ant = min(CA, key=lambda b: b[2]); dom = max(CA, key=lambda b: b[2])            # Sant'Antonino by the church, San Domenico behind
# Sant'Antonino (Michelozzo, before 1440; photograph Vsatinet 2019): arches on columns, a lean-to tiled roof over the walk,
# the wings behind with small windows
a0, a1, o0, o1, rt, gc = ant
S.cloister(f"chiostro_antonino@1444-{NOW}", a0, a1, o0, o1, gc + 0.05, gc + 3.3, (max(3, round((a1 - a0) / 3.0)), max(3, round((o1 - o0) / 3.0))), 3.6,
           rt, kind="lean", ring_top=rt, upper=(2.0, 1.3, 0.7, "plain"), garth="lawn", wall="conv")
# San Domenico (photograph Sailko 2014): arches on columns, two floors above with shuttered windows
a0, a1, o0, o1, rt, gc = dom
S.cloister(f"chiostro_domenico@1444-{NOW}", a0, a1, o0, o1, gc + 0.05, gc + 3.6, (max(3, round((a1 - a0) / 4.2)), max(3, round((o1 - o0) / 4.2))), 3.8,
           min(rt, gc + 12.5), kind="loggia", upper=(1.0, 2.0, 1.1, "shutters"), garth="lawn", wall="conv")
def in_cloister(a, o):
    for (b0, b1, c0, c1, _, _), d in ((ant, 10.2), (dom, 4.4)):
        if b0 - d <= a <= b1 + d and c0 - d <= o <= c1 + d: return True
    return False

# ---------------------------------------------------------------- Piazza San Marco
SQ = S.D["square"]
for b in SQ["beds"]:                                    # the green beds of the square's garden (traced from the 2017 orthophoto)
    bed(f"piazza_giardino@1873-{NOW}", b["pts"], b["ground"], curb=0.2, rail=False)
FA = SQ["fanti"]; fcx = FA["c"]; gf = FA["ground"] + 0.05
statue(f"monumento_fanti@1873-{NOW}", fcx, (S.n[0], S.n[1]), gf, base=(1.7, 3.2), fig=3.0, ped="marble", body="bronze", fence=FA["fence"])
for k in range(4):                                       # benches round the statue (it.wikipedia)
    t = math.pi / 4 + k * math.pi / 2
    from landmark_church import Vs
    bench(f"panchine@1873-{NOW}", (fcx[0] + 5.0 * math.cos(t), fcx[1] + 5.0 * math.sin(t)), t + math.pi / 2, gf)

# the rest from the DSM: chapels and Silvani's tribune with the church, the convent
def phase(a, o, k):
    if abs(a - TOWER_A) < 3.6 and abs(o - TOWER_O) < 3.6: return None
    if (TRB[0] - 0.5 <= a <= TRB[1] + 0.5 and TRB[2] - 0.5 <= o <= TRB[3] + 0.3) or (5.5 <= a <= 15.5 and 47 <= o <= 52): return None   # the tribune, by hand
    if -13.3 <= a <= -0.7 and 23.7 <= o <= 36.3: return None                  # the chapel, by hand
    if 20.9 <= a <= 60.3 and o < 0.8: return None                               # the convent front, by hand
    if k == 0:
        if NAVE[0] - 0.3 <= a <= NAVE[1] + 0.3 and o < 34.3: return None
        if o < 1.0: return None
        return ("cappelle", 1443)
    return ("convento", 1444)
def detail(part):
    if part == "convento": return {"roof": "hip", "windows": True, "mat": "conv"}
    return {"roof": "hip", "windows": False}
def phase2(a, o, k):
    if k == 1 and in_cloister(a, o): return None
    return phase(a, o, k)
def solid(a, o):
    if abs(a - TOWER_A) < 3.6 and abs(o - TOWER_O) < 3.6: return True
    if (TRB[0] - 0.5 <= a <= TRB[1] + 0.5 and TRB[2] - 0.5 <= o <= TRB[3] + 0.3) or (5.5 <= a <= 15.5 and 47 <= o <= 52): return True
    gr_ = S.D["grid"]; i, j = int(math.floor(a - gr_["a0"])), int(math.floor(o - gr_["o0"]))
    return 0 <= i < gr_["na"] and 0 <= j < gr_["no"] and gr_["k"][j][i] == 0 and NAVE[0] - 0.3 <= a <= NAVE[1] + 0.3
print("massing", S.raster(phase2, detail=detail, solid=solid))
K.export("san_marco")
