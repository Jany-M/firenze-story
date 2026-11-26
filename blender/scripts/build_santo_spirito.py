"""Basilica di Santo Spirito with its sacristy, Cenacolo and convent (v1).

Run:  python pipeline/45_chiese.py   (once: outlines, ground, DSM raster → blender/data/chiese.json)
      blender -b --python blender/scripts/build_santo_spirito.py  →  web/public/models/landmarks/santo_spirito.glb
Frame: absolute scene coordinates; inside the script a along the front (OSM way 24881563) from its south-west corner, o
inwards along the church's axis. The axis is at a 12.5 (the nave's ridge and the dome's lantern in the DSM), 2.8 m off the
middle of the OSM front segment, so the front (30.6 m) is centred on the axis.
Measured (LiDAR 2023 DSM, ground 8.1 m scene): heights above the square – nave a 6–19, eaves ≈24.7, ridge ≈28; aisles
a 0–6 and 19–25 under lean-to roofs ≈16–18; the outer chapels ≈13–14; transept a −7…33, o 59.5–75.5, as high as the nave;
choir to o 87; the dome's drum ≈7 m radius on the crossing, the lantern's ball ≈44.8 m (DSM peak 52.9 scene); the bell
tower at a −27.6, o 47.5, its cross ≈65 m (DSM peak 73.4 scene).
Details from photographs (docs/materials):
- front (Giaccai 2014): plain plastered front, stone plinth and steps, central portal in a pietra serena frame and two smaller
  doors, the curved gable with two volutes, the ledge and small pediment, a big oculus in a moulded ring and a small one;
- body seen from Giotto's tower and the Duomo (Zairon 2023, Luca Aless 2014): ochre plaster, pietra serena corner pilasters
  and cornices, tall round-headed windows along the nave's clerestory and the transept, the transept and choir ends gabled as
  pediments with an oculus, two tall windows and a blind arch below; the dome on a low drum ringed with small oculi, its
  lantern with columns, a little cap and a gilded ball;
- bell tower (Pufui PcPifpef 2018): pietra forte; two tiers with a great arched opening a face between cornices; the belfry
  with a balustrade, scroll buttresses on the corner pedestals and a pillared arch; the frieze "AVSPICIIS COSMI"; a small bell
  stage and a tall stone spire with a ball and a cross. Heights from the photograph scaled to the DSM peak.
Dates (docs/landmarks/SANTO-SPIRITO.md): the Augustinians' church begun 1269 (stands until 1481); Brunelleschi's church begun
1444, dome 1479–81, consecrated 1481; the outside in bare stone until it was plastered in the 18th century (shown 1750,
*inferred*); sacristy begun 1489 (shown 1495, *inferred*); bell tower 1503–70; Cenacolo c. 1350 and convent 1300 (*inferred*).
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from mathutils import Vector
from landmark_detail import *
from landmark_church import Site, slab, extra_materials, bed, fountain_spirito, statue
import numpy as np
from landmark_text import lettering
K.reset()
MAT["plaster"] = material("plaster_ochre_sp", None, (0.88, 0.74, 0.48), 0.9)
MAT["rough"] = material("rubble_stone", "pietra_forte", (0.6, 0.5, 0.38), 0.9, 0.5, tint=(2.6, 2.4, 2.1))
MAT["forte"] = material("pietra_forte", "pietra_forte", (0.62, 0.5, 0.36), 0.85, 0.32, tint=(3.0, 2.85, 2.55))
MAT["serena"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)
MAT["letters"] = material("inscription_letters", None, (0.2, 0.17, 0.14), 0.7)
MAT["iron"] = material("wrought_iron", None, (0.08, 0.08, 0.08), 0.6, metal=0.6)
extra_materials()
MAT["conv"] = material("plaster_convent", None, (0.9, 0.85, 0.74), 0.9)
NOW = K.NOW
S = Site("spirito"); G = S.G; L = S.L
AX = 12.5; OFF = AX - L / 2
F = Frame(S.W(OFF, 0), S.TA, -S.NO)                       # the front, centred on the axis
NAVE = (6.0, 19.0); EAVE, RIDGE = G + 24.7, G + 28.0
TR = (-7.0, 33.0, 59.5, 75.5)                              # transept a0, a1, o0, o1
CHOIR_END = 87.0
TOWER_A, TOWER_O = -27.6, 47.5
B = f"chiesa@1481-{NOW}"

def face_a(a, o0, o1, out):
    """Wall face at constant a over o0..o1; out = −1 faces smaller a. Returns (frame, length): u along the wall."""
    return (Frame(S.W(a, o1), -S.NO, -S.TA), o1 - o0) if out < 0 else (Frame(S.W(a, o0), S.NO, S.TA), o1 - o0)
def face_o(o, a0, a1, out):
    """Wall face at constant o over a0..a1; out = −1 faces the front."""
    return (Frame(S.W(a0, o), S.TA, -S.NO), a1 - a0) if out < 0 else (Frame(S.W(a1, o), -S.TA, S.NO), a1 - a0)
def tall_window(part, Fr, u, sill, h, w=1.25):
    """Round-headed window in a pietra serena frame."""
    r = w / 2; spring = sill + h - r
    arch_fill(part, "dark", Fr, u - r, u + r, sill, spring, n=0.03)
    ring(part, "serena", Fr, u, spring, r, r + 0.22, 0, 0.1, seg=10, soffit=False)
    pbox(bm_for(part, "serena"), Fr, u - r - 0.22, u - r, sill, spring, 0, 0.1)
    pbox(bm_for(part, "serena"), Fr, u + r, u + r + 0.22, sill, spring, 0, 0.1)
    pbox(bm_for(part, "serena"), Fr, u - r - 0.3, u + r + 0.3, sill - 0.18, sill, 0, 0.16)
def trim(part, Fr, Lf, v0, eave, corners=True):
    """Pietra serena corner pilasters and the cornice under the eaves."""
    if corners:
        pbox(bm_for(part, "serena"), Fr, 0, 0.7, v0, eave - 0.6, 0, 0.12)
        pbox(bm_for(part, "serena"), Fr, Lf - 0.7, Lf, v0, eave - 0.6, 0, 0.12)
    pbox(bm_for(part, "serena"), Fr, -0.1, Lf + 0.1, eave - 0.6, eave - 0.3, 0, 0.25)
    pbox(bm_for(part, "serena"), Fr, -0.2, Lf + 0.2, eave - 0.3, eave, 0, 0.5)
def gable_end(part, Fr, Lf, eave, ridge, windows=True):
    """A pediment end: the triangle with its raking cornice and an oculus; below, two tall windows and a blind arch."""
    poly(bm_for(part, "plaster"), [Fr.p(0, eave), Fr.p(Lf, eave), Fr.p(Lf / 2, ridge)])
    bm = bm_for(part, "serena")
    for (u0, v0), (u1, v1) in (((-0.3, eave), (Lf / 2, ridge + 0.15)), ((Lf / 2, ridge + 0.15), (Lf + 0.3, eave))):
        poly(bm, [Fr.p(u0, v0, 0.02), Fr.p(u1, v1, 0.02), Fr.p(u1, v1 + 0.4, 0.45), Fr.p(u0, v0 + 0.4, 0.45)])
    oculus(part, Fr, Lf / 2, eave + (ridge - eave) * 0.42, 0.55, frame="serena", fill="dark", fw=0.16)
    if windows:
        for u in (Lf * 0.25, Lf * 0.75): tall_window(part, Fr, u, G + 19.6, 4.2, w=1.1)

# ---------------------------------------------------------------- the medieval church (1269–1481): a lower hall (size *inferred*)
S.hall("chiesa_medievale@1269-1481", 5.0, 20.0, 2.0, 62.0, G - 0.5, G + 14.0, G + 18.0)

# ---------------------------------------------------------------- Brunelleschi's church (1481)
S.hall(B, NAVE[0], NAVE[1], 0.6, CHOIR_END, G - 0.5, EAVE, RIDGE, gables=(False, False))
S.hall(B, TR[0], TR[1], TR[2], TR[3], G - 0.5, EAVE, RIDGE, along="a", gables=(False, False))
# nave walls above the aisles: clerestory windows one a bay (Brunelleschi's bay of 11 braccia, ≈6.4 m)
for a, out in ((NAVE[0], -1), (NAVE[1], 1)):
    for (o0, o1) in ((0.6, TR[2]), (TR[3], CHOIR_END)):
        Fr, Lf = face_a(a, o0, o1, out)
        trim(B, Fr, Lf, G + 18.2, EAVE, corners=False)
        n = max(1, int(Lf / 6.4))
        for k in range(n): tall_window(B, Fr, (k + 0.5) * Lf / n, G + 19.3, 4.0, w=1.1)
# transept: long faces with two windows an arm, the two pediment ends; the choir end
for o, out in ((TR[2], -1), (TR[3], 1)):
    for (a0, a1) in ((TR[0], NAVE[0]), (NAVE[1], TR[1])):
        Fr, Lf = face_o(o, a0, a1, out); trim(B, Fr, Lf, G + 16.0, EAVE)
        for u in (Lf * 0.3, Lf * 0.72): tall_window(B, Fr, u, G + 19.6, 4.2, w=1.1)
for a, out in ((TR[0], -1), (TR[1], 1)):
    Fr, Lf = face_a(a, TR[2], TR[3], out); trim(B, Fr, Lf, G - 0.5, EAVE); gable_end(B, Fr, Lf, EAVE, RIDGE)
Fr, Lf = face_o(CHOIR_END, NAVE[0], NAVE[1], 1); trim(B, Fr, Lf, G + 16.0, EAVE); gable_end(B, Fr, Lf, EAVE, RIDGE, windows=False)
tall_window(B, Fr, Lf / 2, G + 19.6, 4.2, w=1.1)

# aisles under lean-to roofs, the outer chapels lower (the curved chapels are hidden inside a straight wall)
def lean_to(part, a_in, a_out, o0, o1, h_in, h_out):
    lo, hi = min(a_in, a_out), max(a_in, a_out)
    box(bm_for(part, "plaster"), Frame(S.W(lo, o0), S.TA, S.NO), 0, hi - lo, G - 0.5, min(h_in, h_out), 0, o1 - o0)
    e = 0.4 if a_out > a_in else -0.4
    quad = [S.W(a_in, o0, h_in), S.W(a_out + e, o0, h_out), S.W(a_out + e, o1, h_out), S.W(a_in, o1, h_in)]
    poly(bm_for(part, "roof"), quad if a_out > a_in else quad[::-1])
    for o in (o0, o1): poly(bm_for(part, "plaster"), [S.W(a_in, o, min(h_in, h_out)), S.W(a_out, o, min(h_in, h_out)), S.W(a_in, o, h_in)])
    Fs, Ls = face_a(a_out, o0, o1, 1 if a_out > a_in else -1)
    pbox(bm_for(part, "serena"), Fs, -0.1, Ls + 0.1, h_out - 0.35, h_out, 0, 0.35)
for (a_in, a_mid, a_out) in ((NAVE[0], 0.0, -5.5), (NAVE[1], 25.0, 30.5)):
    lean_to(B, a_in, a_mid, 1.2, 41.0, G + 18.2, G + 15.8)
    lean_to(B, a_mid, a_out, 1.2, 41.0, G + 14.4, G + 13.6)
# the aisles and chapels carry on round the transept arms and the choir (DSM: aisles ≈16.5–17.5 m above the square, the outer
# chapel band ≈12–13 m – Brunelleschi's plan with the chapels all round the church, hidden outside in a straight wall)
def hipped(part, a0, a1, o0, o1, z, rise, mat="plaster", corn=True):
    box(bm_for(part, mat), Frame(S.W(a0, o0), S.TA, S.NO), 0, a1 - a0, G - 0.5, z, 0, o1 - o0)
    e = 0.4; hm = min(a1 - a0, o1 - o0) / 2; z1 = z + rise
    A_, B_, C_, D_ = S.W(a0 - e, o0 - e, z), S.W(a1 + e, o0 - e, z), S.W(a1 + e, o1 + e, z), S.W(a0 - e, o1 + e, z)
    rb = bm_for(part, "roof")
    if a1 - a0 >= o1 - o0:
        R0, R1 = S.W(a0 + hm, (o0 + o1) / 2, z1), S.W(a1 - hm, (o0 + o1) / 2, z1)
        poly(rb, [A_, B_, R1, R0]); poly(rb, [C_, D_, R0, R1]); poly(rb, [B_, C_, R1]); poly(rb, [D_, A_, R0])
    else:
        R0, R1 = S.W((a0 + a1) / 2, o0 + hm, z1), S.W((a0 + a1) / 2, o1 - hm, z1)
        poly(rb, [B_, C_, R1, R0]); poly(rb, [D_, A_, R0, R1]); poly(rb, [A_, B_, R0]); poly(rb, [C_, D_, R1])
    if corn:
        for (o_, u_, n_, Lf) in ((S.W(a0, o0), S.TA, -S.NO, a1 - a0), (S.W(a1, o1), -S.TA, S.NO, a1 - a0), (S.W(a0, o1), -S.NO, -S.TA, o1 - o0), (S.W(a1, o0), S.NO, S.TA, o1 - o0)):
            pbox(bm_for(part, "serena"), Frame(o_, u_, n_), -0.1, Lf + 0.1, z - 0.35, z, 0, 0.35)
hipped(B, -16.5, 42.5, 41.0, 83.5, G + 12.6, 1.2)                      # chapel band round the transept
hipped(B, -4.0, 30.0, 83.0, 96.5, G + 12.6, 1.2)                       # and round the choir
hipped(B, -14.0, 40.0, 41.0, 82.0, G + 16.8, 2.2, corn=False)          # the aisles round the transept
hipped(B, -2.0, 28.0, 80.0, 93.5, G + 16.8, 2.2, corn=False)           # and round the choir

# the dome: low drum ringed with oculi, the tiled dome, a lantern with columns, a little cap and the gilded ball
c = S.W(AX, (TR[2] + TR[3]) / 2); R = 7.0; d0, d1 = G + 27.5, G + 32.0
P = f"cupola@1481-{NOW}"
cylinder(P, "plaster", c, R, d0, d1, seg=32)
cylinder(P, "serena", c, R + 0.25, d1 - 0.35, d1, seg=32)
for k in range(14):
    t = 2 * math.pi * (k + 0.5) / 14; dv = Vector((math.cos(t), math.sin(t), 0))
    oculus(P, Frame(c + dv * R, Vector((-dv.y, dv.x, 0)), dv), 0, (d0 + d1) / 2 + 0.6, 0.42, frame="serena", fill="dark", fw=0.12)
dome(P, c, R + 0.1, d1, 7.0, ribs=8, mat="tile", seg=32, rib_mat="serena")
lt0 = d1 + 6.7
cylinder(P, "plaster", c, 1.45, lt0 - 0.3, lt0 + 0.4, seg=12)
for k in range(8):
    t = 2 * math.pi * k / 8
    cylinder(P, "serena", c + Vector((math.cos(t), math.sin(t), 0)) * 1.25, 0.14, lt0 + 0.4, lt0 + 2.6, seg=6)
cylinder(P, "plaster", c, 1.0, lt0 + 0.4, lt0 + 2.6, seg=12)
cylinder(P, "serena", c, 1.5, lt0 + 2.6, lt0 + 3.0, seg=12)
cone(P, "lead", c, 1.25, 0.25, lt0 + 3.0, lt0 + 4.1, seg=12)
sphere(P, "gold", c + Vector((0, 0, G + 44.2)), 0.42)
box(bm_for(P, "iron"), Frame(c, S.TA, -S.NO), -0.05, 0.05, G + 44.6, G + 45.6, -0.05, 0.05)

# ---------------------------------------------------------------- the front: curved gable, bare stone until 1750, then plastered
H_SIDE, H_LEDGE, H_TOP = 14.6, 24.7, 28.9                   # the ledge at the nave's eaves, the pediment over its ridge
mid0, mid1 = NAVE[0] - OFF, NAVE[1] - OFF                  # as wide as the nave (8.8 … 21.8)
def volute():
    """The left flank, from the ledge at mid0 down to the aisle cornice: a concave sweep ending in a round scroll."""
    bc, br = (3.0, H_SIDE + 1.6), 1.7
    a_join = math.radians(40)
    j = (bc[0] + br * math.cos(a_join), bc[1] + br * math.sin(a_join))
    sweep = [(mid0 + (j[0] - mid0) * t, H_LEDGE + (j[1] - H_LEDGE) * (1 - (1 - t) ** 2.4)) for t in [k / 12 for k in range(13)]]
    bulb = [(bc[0] + br * math.cos(a), bc[1] + br * math.sin(a)) for a in [a_join + (math.pi - a_join) * k / 10 for k in range(1, 11)]]
    return sweep + bulb + [(bc[0] - br, H_SIDE)]
P_left = volute()
outline = [(0, -0.6), (L, -0.6), (L, H_SIDE)] + [(L - u, v) for u, v in P_left[::-1]][:-1] + \
          [(mid1, H_LEDGE), (mid1 - 0.6, H_LEDGE), (L / 2, H_TOP), (mid0 + 0.6, H_LEDGE), (mid0, H_LEDGE)] + P_left[1:] + [(0, H_SIDE)]
outline = [(u, G + v) for u, v in outline]
for part, mat in (("facciata_pietra@1481-1750", "rough"), (f"facciata@1750-{NOW}", "plaster")):
    slab(part, mat, F, outline, -1.2, 0.0)
fp = f"facciata_dettagli@1481-{NOW}"
pbox(bm_for(fp, "serena"), F, 0, L, G - 0.6, G + 0.9, 0, 0.12)                                  # plinth
for (u0, u1) in ((0, 1.6), (L - 1.6, L)):                                                      # aisle cornices
    pbox(bm_for(fp, "serena"), F, u0 - 0.2, u1 + 0.2, G + H_SIDE - 0.25, G + H_SIDE, 0, 0.35)
pbox(bm_for(fp, "serena"), F, mid0 - 0.5, mid1 + 0.5, G + H_LEDGE - 0.3, G + H_LEDGE, 0, 0.45)  # the ledge under the pediment
bm = bm_for(fp, "serena")
for (u0, v0), (u1, v1) in (((mid0 + 0.3, H_LEDGE), (L / 2, H_TOP + 0.3)), ((L / 2, H_TOP + 0.3), (mid1 - 0.3, H_LEDGE))):
    poly(bm, [F.p(u0, G + v0, 0.02), F.p(u1, G + v1, 0.02), F.p(u1, G + v1 + 0.4, 0.4), F.p(u0, G + v0 + 0.4, 0.4)])
cylinder(fp, "serena", F.p(L / 2, 0, -0.6), 0.35, G + H_TOP, G + H_TOP + 1.0, seg=8)
box(bm_for(fp, "iron"), F, L / 2 - 0.06, L / 2 + 0.06, G + H_TOP + 1.0, G + H_TOP + 3.0, -0.66, -0.54)
box(bm_for(fp, "iron"), F, L / 2 - 0.5, L / 2 + 0.5, G + H_TOP + 2.2, G + H_TOP + 2.32, -0.66, -0.54)
for (uc, w, h, fw) in ((L / 2, 3.3, 7.9, 0.55), (7.1, 2.3, 5.6, 0.35), (L - 7.1, 2.3, 5.6, 0.35)):
    poly(bm_for(fp, "wood"), [F.p(uc - w / 2, G, 0.03), F.p(uc + w / 2, G, 0.03), F.p(uc + w / 2, G + h, 0.03), F.p(uc - w / 2, G + h, 0.03)])
    for (u0, u1, v0, v1) in ((uc - w / 2 - fw, uc - w / 2, G, G + h + fw), (uc + w / 2, uc + w / 2 + fw, G, G + h + fw), (uc - w / 2, uc + w / 2, G + h, G + h + fw)):
        pbox(bm_for(fp, "serena"), F, u0, u1, v0, v1, 0, 0.12)
oculus(fp, F, L / 2, G + 19.0, 1.5, frame="serena", fill="glass", fw=0.9)
oculus(fp, F, L / 2, G + 26.4, 0.5, frame="serena", fill="dark", fw=0.12)
for k in range(3): box(bm_for(fp, "serena"), F, -1.0, L + 1.0, G - 0.9 + k * 0.15, G - 0.6 + k * 0.15, 0.0, 2.4 - k * 0.8)

# ---------------------------------------------------------------- bell tower (Baccio d'Agnolo, 1503–70), pietra forte
T = f"campanile@1570-{NOW}"; TS = 6.8
CT = S.W(TOWER_A, TOWER_O)
def tfaces(side):
    """The four faces of a square of side `side` centred on the tower: (frame, length), u along, n outwards."""
    h = side / 2
    return [(Frame(CT - u * h + n * h, u, n), side) for (u, n) in ((S.TA, -S.NO), (S.NO, S.TA), (-S.TA, S.NO), (-S.NO, -S.TA))]
def tbox(z0, z1, side, mat="forte"):
    h = side / 2; box(bm_for(T, mat), Frame(S.W(TOWER_A - h, TOWER_O - h), S.TA, S.NO), 0, side, z0, z1, 0, side)
def tcornice(z, side, proj, h=0.5):
    tbox(z, z + h * 0.5, side + proj); tbox(z + h * 0.5, z + h, side + proj * 1.8)
tbox(G - 0.5, G + 44.6, TS)
for (z0, spring, r) in ((G + 27.9, G + 33.4, 1.2), (G + 36.8, G + 42.6, 1.35)):        # two tiers, a great arch a face
    for Fr, Lf in tfaces(TS):
        arch_fill(T, "dark", Fr, Lf / 2 - r, Lf / 2 + r, z0, spring, n=0.03)
        ring(T, "forte", Fr, Lf / 2, spring, r, r + 0.45, 0, 0.12, seg=12, soffit=False)
        for s_ in (-1, 1): pbox(bm_for(T, "forte"), Fr, Lf / 2 + s_ * (r + 0.05) - 0.25, Lf / 2 + s_ * (r + 0.05) + 0.25, z0, spring, 0, 0.15)
tcornice(G + 35.4, TS, 0.25); tcornice(G + 44.6, TS, 0.45, h=1.4)
# the belfry: inset core with a pillared arch a face, a balustrade, corner pedestals with scroll buttresses
CS = 4.8; zb0, zb1 = G + 46.0, G + 52.6
tbox(zb0, zb1, CS)
for Fr, Lf in tfaces(CS):
    r = 0.85; spring = zb1 - 2.3
    arch_fill(T, "dark", Fr, Lf / 2 - r, Lf / 2 + r, zb0 + 0.9, spring, n=0.03)
    for s_ in (-1, 1): cylinder(T, "forte", Fr.p(Lf / 2 + s_ * (r + 0.2), 0, 0.2), 0.18, zb0 + 0.9, spring, seg=8)
    ring(T, "forte", Fr, Lf / 2, spring, r, r + 0.6, 0, 0.15, seg=12, soffit=False)
    for k in range(5):                                                               # the little round holes in the archivolt
        t = math.pi * (k + 0.5) / 5
        poly(bm_for(T, "dark"), [Fr.p(Lf / 2 + (r + 0.3) * math.cos(t) + 0.13 * math.cos(q), spring + (r + 0.3) * math.sin(t) + 0.13 * math.sin(q), 0.16) for q in [2 * math.pi * i / 8 for i in range(8)]])
for Fr, Lf in tfaces(TS + 0.5):                                                    # balustrade on the cornice
    pbox(bm_for(T, "forte"), Fr, 0.9, Lf - 0.9, zb0 + 0.85, zb0 + 1.0, -0.25, 0)
    for k in range(int((Lf - 1.8) / 0.3)):
        u = 1.0 + k * 0.3; box(bm_for(T, "forte"), Fr, u, u + 0.12, zb0, zb0 + 0.85, -0.18, -0.06)
h2 = (TS + 0.5) / 2
for (sa, so) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):                              # corner pedestals and scrolls
    pc = S.W(TOWER_A + sa * (h2 - 0.45), TOWER_O + so * (h2 - 0.45))
    box(bm_for(T, "forte"), Frame(pc - S.TA * 0.45 - S.NO * 0.45, S.TA, S.NO), 0, 0.9, zb0, zb0 + 2.2, 0, 0.9)
    toward = (CT - pc).normalized(); side_v = Vector((-toward.y, toward.x, 0))
    Fv = Frame(pc - side_v * 0.15, side_v, toward)
    for k in range(10):
        t0, t1 = k / 10, (k + 1) / 10
        poly(bm_for(T, "forte"), [Fv.p(0, zb0 + 2.2 + 2.4 * t0, 0.1 + 0.9 * t0 * t0), Fv.p(0.3, zb0 + 2.2 + 2.4 * t0, 0.1 + 0.9 * t0 * t0),
                                  Fv.p(0.3, zb0 + 2.2 + 2.4 * t1, 0.1 + 0.9 * t1 * t1), Fv.p(0, zb0 + 2.2 + 2.4 * t1, 0.1 + 0.9 * t1 * t1)])
    sphere(T, "forte", Fv.p(0.15, zb0 + 4.7, 1.05), 0.32)
# the frieze with the inscription, the bell stage, the spire with ball and cross
tcornice(zb1, CS, 0.3, h=0.9)
Fr0, Lf0 = tfaces(CS + 0.3)[0]
lettering(T, "letters", Fr0, Lf0 / 2, zb1 + 0.2, 0.02, "AVSPICIIS COSMI", 0.42, width=Lf0 - 0.5)
zs0, zs1 = zb1 + 0.9, zb1 + 3.2; BS = 3.9
tbox(zs0, zs1, BS)
for Fr, Lf in tfaces(BS):
    arch_fill(T, "dark", Fr, Lf / 2 - 0.65, Lf / 2 + 0.65, zs0 + 0.2, zs1 - 0.85, n=0.03)
    ring(T, "forte", Fr, Lf / 2, zs1 - 0.85, 0.65, 0.95, 0, 0.12, seg=10, soffit=False)
tcornice(zs1, BS, 0.2, h=0.4)
for (sa, so) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
    cone(T, "forte", S.W(TOWER_A + sa * (BS / 2 - 0.2), TOWER_O + so * (BS / 2 - 0.2)), 0.22, 0.03, zs1 + 0.4, zs1 + 1.2, seg=6)
top = G + 62.6; hs = BS / 2 - 0.1
pts = [S.W(TOWER_A - hs, TOWER_O - hs, zs1 + 0.4), S.W(TOWER_A + hs, TOWER_O - hs, zs1 + 0.4), S.W(TOWER_A + hs, TOWER_O + hs, zs1 + 0.4), S.W(TOWER_A - hs, TOWER_O + hs, zs1 + 0.4)]
for p0, p1 in zip(pts, pts[1:] + pts[:1]): poly(bm_for(T, "forte"), [p0, p1, S.W(TOWER_A, TOWER_O, top)])
sphere(T, "lead", S.W(TOWER_A, TOWER_O, top + 0.4), 0.45)
box(bm_for(T, "iron"), Frame(CT, S.TA, -S.NO), -0.05, 0.05, top + 0.8, G + 65.0, -0.05, 0.05)
box(bm_for(T, "iron"), Frame(CT, S.TA, -S.NO), -0.4, 0.4, G + 64.2, G + 64.32, -0.05, 0.05)

# ---------------------------------------------------------------- the convent's two cloisters (OSM relation 1631265, its two courts)
def hole_box(k):
    """Bounding box (a0, a1, o0, o1) of the OSM court k of the convent, and the DSM height of the wings round it."""
    h = S.D["polys"][3][1][k]
    A = [(p[0] - S.A[0]) * S.t[0] + (p[1] - S.A[1]) * S.t[1] for p in h]; O = [(p[0] - S.A[0]) * S.n[0] + (p[1] - S.A[1]) * S.n[1] for p in h]
    a0, a1, o0, o1 = min(A), max(A), min(O), max(O)
    gr = S.D["grid"]; ring = []
    for j in range(gr["no"]):
        for i in range(gr["na"]):
            a_, o_ = gr["a0"] + i + 0.5, gr["o0"] + j + 0.5; hv = gr["h"][j][i]
            if hv is None: continue
            d = max(a0 - a_, a_ - a1, o0 - o_, o_ - o1)
            if 6 <= d <= 12: ring.append(hv)
    return a0, a1, o0, o1, float(np.median(ring)) if ring else S.G + 14
CL = {}
for k in range(len(S.D["polys"][3][1])):
    a0, a1, o0, o1, rt = hole_box(k)
    if (a1 - a0) * (o1 - o0) > 300: CL[k] = (a0, a1, o0, o1, rt)
near = max(CL, key=lambda k: CL[k][1]); far = min(CL, key=lambda k: CL[k][1])
gc = lambda b: S.D["grid"]["g"][int((b[2] + b[3]) / 2 - S.D["grid"]["o0"])][int((b[0] + b[1]) / 2 - S.D["grid"]["a0"])] or G
# the Chiostro dei Morti beside the church (Giulio and Alfonso Parigi, c. 1620; photograph Sailko 2017): arches on columns,
# the upper floor with pilaster strips and plain windows, a paved path and a round basin in the garth
a0, a1, o0, o1, rt = CL[near]; g0 = gc(CL[near]) + 0.05
S.cloister(f"chiostro_morti@1620-{NOW}", a0, a1, o0, o1, g0, g0 + 3.4, (max(3, round((a1 - a0) / 2.9)), max(3, round((o1 - o0) / 2.9))), 3.8,
           min(rt, g0 + 11.0), kind="loggia", upper=(1.4, 1.8, 0.95, "plain"), garth="lawn", well="basin", wall="conv")
# the Chiostro Grande (Bartolomeo Ammannati, 1564–69; photograph Sailko 2009): wide arches on Tuscan columns, the upper floor
# with arched windows between pilaster strips, a well with an iron frame in the middle
a0, a1, o0, o1, rt = CL[far]; g1 = gc(CL[far]) + 0.05
S.cloister(f"chiostro_grande@1569-{NOW}", a0, a1, o0, o1, g1, g1 + 4.6, (max(3, round((a1 - a0) / 4.9)), max(3, round((o1 - o0) / 4.9))), 4.6,
           min(rt, g1 + 13.0), kind="loggia", upper=(1.4, 2.8, 1.5, "arched"), garth="lawn", well="well", wall="conv")
def in_cloister(a, o):
    for (b0, b1, c0, c1, _), d in ((CL[near], 4.4), (CL[far], 5.2)):
        if b0 - d <= a <= b1 + d and c0 - d <= o <= c1 + d: return True
    return False

# ---------------------------------------------------------------- Giuliano da Sangallo's sacristy: an octagon under a ribbed dome
# with a lantern (shown 1495; the dome's place and size from the DSM: the sacristy's highest cells)
gr = S.D["grid"]; hi = [(gr["a0"] + i + 0.5, gr["o0"] + j + 0.5, gr["h"][j][i]) for j in range(gr["no"]) for i in range(gr["na"])
                       if gr["k"][j][i] == 2 and gr["h"][j][i] is not None]
top_h = max(h for _, _, h in hi); core = [(a, o) for a, o, h in hi if h > top_h - 5.0]
SA = sum(a for a, _ in core) / len(core); SO = sum(o for _, o in core) / len(core)
SR = max(4.0, min(6.5, (len(core) / math.pi) ** 0.5))
SAG = f"sagrestia_cupola@1495-{NOW}"; cs = S.W(SA, SO)
octagon_prism(SAG, "plaster", cs, SR, G - 0.5, top_h - 6.2, rot=0.0)
for k in range(8):                                                              # serena corner pilasters and the cornice
    t = 2 * math.pi * k / 8 + math.pi / 8; d = Vector((math.cos(t), math.sin(t), 0)) * (SR / math.cos(math.pi / 8))
    cylinder(SAG, "serena", cs + d, 0.25, G + 10.0, top_h - 6.4, seg=6)
octagon_prism(SAG, "serena", cs, SR + 0.3, top_h - 6.6, top_h - 6.2, rot=0.0)
dome(SAG, cs, SR * 0.95, top_h - 6.2, 4.4, ribs=8, mat="tile", seg=24, rib_mat="serena")
cylinder(SAG, "plaster", cs, 0.9, top_h - 1.9, top_h - 0.6, seg=8); cone(SAG, "lead", cs, 1.0, 0.1, top_h - 0.6, top_h + 0.4, seg=8)

# ---------------------------------------------------------------- Piazza Santo Spirito (OSM relation 1631844)
SQ = S.D["square"]
fc = SQ["fountain"]["c"]
for b in SQ["beds"]:                                    # the garden beds of 1869 (Luigi Del Sarto, Attilio Pucci), as they are today
    if math.dist(fc, (sum(p[0] for p in b["pts"]) / len(b["pts"]), sum(p[1] for p in b["pts"]) / len(b["pts"]))) < 3: continue
    bed(f"piazza_aiuole@1869-{NOW}", b["pts"], b["ground"])
fountain_spirito(f"fontana@1812-{NOW}", fc, SQ["fountain"]["r"], SQ["fountain"]["ground"] + 0.05)        # brought from the convent in 1812
R_ = SQ["ridolfi"]
statue(f"monumento_ridolfi@1898-{NOW}", R_["c"], R_["face"], R_["ground"] + 0.05, base=(1.8, 3.0), fig=2.7, ped="granite", body="marble")

# ---------------------------------------------------------------- everything else from the DSM
def phase(a, o, k):
    if k == 0: return None                                                                 # the whole church is built by hand
    if abs(a - TOWER_A) < TS / 2 + 1.8 and abs(o - TOWER_O) < TS / 2 + 1.8: return None
    if k == 2 and (a - SA) ** 2 + (o - SO) ** 2 < (SR + 1.0) ** 2: return None
    return {1: ("cenacolo", 1350), 2: ("sagrestia", 1495), 3: ("convento", 1300)}[k]
def detail(part):
    if part == "convento": return {"roof": "hip", "windows": True, "mat": "conv"}
    return {"roof": "hip", "windows": False}
def phase2(a, o, k):
    if k == 3 and in_cloister(a, o): return None
    return phase(a, o, k)
def solid(a, o):                                     # the church, the bell tower and the sacristy are built by hand
    if abs(a - TOWER_A) < TS / 2 + 0.6 and abs(o - TOWER_O) < TS / 2 + 0.6: return True
    if (a - SA) ** 2 + (o - SO) ** 2 < (SR + 1.0) ** 2: return True
    gr_ = S.D["grid"]; i, j = int(math.floor(a - gr_["a0"])), int(math.floor(o - gr_["o0"]))
    return 0 <= i < gr_["na"] and 0 <= j < gr_["no"] and gr_["k"][j][i] == 0
print("massing", S.raster(phase2, detail=detail, solid=solid))
K.export("santo_spirito")
