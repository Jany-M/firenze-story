"""Basilica di Santa Maria del Carmine with the Corsini chapel, the first cloister and the convent (v1).

Run:  python pipeline/45_chiese.py   (once: outlines, ground, DSM raster → blender/data/chiese.json)
      blender -b --python blender/scripts/build_carmine.py  →  web/public/models/landmarks/carmine.glb
Frame: a along the front (OSM way 118425485) from its west corner, o inwards (south) along the church's axis.
Measured (LiDAR 2023 DSM, ground 6.0 m scene): the nave a 0.7–20.8, eaves ≈26.5, ridge ≈30.3 above the square, to o 60;
the transept a −9.5…31, o 60–76, eaves ≈24, ridge ≈27.6; over the crossing an octagon ≈16 m across (apothem 8) with its
roof's top ≈37.7; the choir a 5–17 to o 86, ridge ≈27.3; the Corsini chapel at the east end of the transept: a square
base ≈15.5 high, an octagonal drum to ≈21.5 (apothem ≈4.6), the lantern's top ≈26.5 at a 36.8, o 68.2; a thin wall
1 m deep and 4.5 m wide at a −4, o 45–49.5 standing 22 m high (the bell gable); the side chapels ≈10–12 m.
Details from photographs (docs/materials):
- front (Sailko 2009, Pufui PcPifpef 2018): the unfinished front in rough rubble and brick, a gable with a small oculus and a
  cross, a tall round-headed window under a ghost of a larger arch, the portal in a frame of pale stone blocks laid long
  and short, the lower part of the front a little wider;
- flanks (Yair Haklai 2019 from the Duomo, Pufui PcPifpef 2018 from the west): rubble walls with big round-headed windows,
  a row of small arches, a plastered band with small square windows under the eaves; over the crossing a plastered
  octagon with framed panels under a low tiled roof with a weathervane (Francesco Bini 2021); the bell gable with two
  bells facing west;
- Corsini chapel (Sailko 2013): plastered base with a lunette window, the octagonal drum with rectangular windows in grey
  stone frames, a low tiled roof and a lantern with a small cupola, gilded ball and cross;
- the first cloister (Oursana 2013, Sailko 2009): round arches on pietra serena columns, an open upper loggia with a
  parapet and columns under a timber roof, a lawn with a well-head and an iron frame.
Dates (docs/landmarks/CARMINE.md): founded 1268, finished 1476 (shown from 1300, *inferred*); the Corsini chapel
1675–83; the fire of 1771 and Ruggieri's rebuilding 1775–82 (the octagon over the crossing shown from 1782, *inferred*);
the first cloister's south loggia 1597–1600, the other three 1612; the convent from 1300 (*inferred*).
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from mathutils import Vector
from landmark_detail import *
from landmark_church import Site, slab, extra_materials
import numpy as np
K.reset()
MAT["plaster"] = material("plaster_cream_cm", None, (0.9, 0.86, 0.76), 0.9)
MAT["rough"] = material("rubble_stone", "pietra_forte", (0.6, 0.5, 0.38), 0.9, 0.5, tint=(2.6, 2.4, 2.1))
MAT["forte"] = material("pietra_forte", "pietra_forte", (0.62, 0.5, 0.36), 0.85, 0.32, tint=(3.0, 2.85, 2.55))
MAT["pale"] = material("pale_stone_blocks", None, (0.82, 0.76, 0.62), 0.8)
MAT["serena"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)
MAT["iron"] = material("wrought_iron", None, (0.08, 0.08, 0.08), 0.6, metal=0.6)
extra_materials()
MAT["conv"] = material("plaster_convent", None, (0.9, 0.85, 0.74), 0.9)
NOW = K.NOW
S = Site("carmine"); G = S.G; L = S.L
F = S.front()
NAVE = (0.7, 20.8); NAVE_END = 60.0; EAVE, RIDGE = G + 26.5, G + 30.3
TR = (-9.5, 31.0, 60.0, 76.0); TR_EAVE, TR_RIDGE = G + 24.0, G + 27.6
CH = (5.0, 17.0, 76.0, 86.0); CH_EAVE, CH_RIDGE = G + 25.3, G + 27.3
CX = (10.75, 68.0)                                     # the crossing's centre
CO = (36.8, 67.6); CO_BASE = (31.0, 42.5, 60.5, 74.5)  # the Corsini chapel
VELA = (-3.8, 44.8, 49.6)                              # bell gable: a, o0, o1
B = f"chiesa@1300-{NOW}"
ROT = math.atan2(S.TA.y, S.TA.x)

def face_a(a, o0, o1, out):
    return (Frame(S.W(a, o1), -S.NO, -S.TA), o1 - o0) if out < 0 else (Frame(S.W(a, o0), S.NO, S.TA), o1 - o0)
def face_o(o, a0, a1, out):
    return (Frame(S.W(a0, o), S.TA, -S.NO), a1 - a0) if out < 0 else (Frame(S.W(a1, o), -S.TA, S.NO), a1 - a0)
def big_window(part, Fr, u, sill, h, w):
    """Round-headed window deep in the rubble wall, with a stone frame."""
    r = w / 2; spring = sill + h - r
    arch_fill(part, "glass", Fr, u - r, u + r, sill, spring, n=0.03)
    ring(part, "forte", Fr, u, spring, r, r + 0.35, 0, 0.12, seg=10, soffit=False)
    for s_ in (-1, 1): pbox(bm_for(part, "forte"), Fr, u + s_ * (r + 0.175) - 0.175, u + s_ * (r + 0.175) + 0.175, sill, spring, 0, 0.12)
    pbox(bm_for(part, "forte"), Fr, u - r - 0.4, u + r + 0.4, sill - 0.2, sill, 0, 0.2)
def archetti(part, Fr, Lf, v, step=1.1):
    """A corbel table: a row of small round arches on little brackets, proud of the wall."""
    n = max(1, int(Lf / step)); st = Lf / n; r = st / 2 - 0.08
    for k in range(n):
        uc = (k + 0.5) * st
        ring(part, "rough", Fr, uc, v, r, r + 0.14, 0, 0.14, seg=6, soffit=True)
        pbox(bm_for(part, "rough"), Fr, k * st - 0.1, k * st + 0.1, v - 0.35, v, 0, 0.18)
    pbox(bm_for(part, "rough"), Fr, -0.1, Lf + 0.1, v + r + 0.14, v + r + 0.34, 0, 0.18)
def flank(part, Fr, Lf, n_win, top_band=True):
    """A nave flank: big windows in the rubble, the corbel table, the plastered band with small square windows, the eaves."""
    for k in range(n_win): big_window(part, Fr, (k + 0.5) * Lf / n_win, G + 12.4, 6.6, 2.3)
    if top_band:
        archetti(part, Fr, Lf, G + 19.6)
        pbox(bm_for(part, "plaster"), Fr, 0, Lf, G + 20.4, EAVE - 0.2, 0, 0.05)
        for k in range(n_win): win_rect(part, Fr, (k + 0.5) * Lf / n_win, G + 22.6, G + 23.3, 0.7, frame="plaster", fill="dark", fw=0.1)
    pbox(bm_for(part, "forte"), Fr, -0.1, Lf + 0.1, EAVE - 0.25, EAVE, 0, 0.45)
def quoins(part, Fr, Lf, v0, v1):
    """Ashlar corner stones, laid long and short, at both ends of a rubble face."""
    z = v0; k = 0
    while z < v1 - 0.3:
        w = 1.1 if k % 2 == 0 else 0.65
        for (u0, u1) in ((0, w), (Lf - w, Lf)): pbox(bm_for(part, "forte"), Fr, u0, u1, z, min(v1, z + 0.5), 0, 0.06)
        z += 0.5; k += 1
def gable(part, mat, Fr, Lf, eave, ridge):
    poly(bm_for(part, mat), [Fr.p(0, eave), Fr.p(Lf, eave), Fr.p(Lf / 2, ridge)])
    bm = bm_for(part, "forte")
    for (u0, v0), (u1, v1) in (((-0.3, eave), (Lf / 2, ridge + 0.15)), ((Lf / 2, ridge + 0.15), (Lf + 0.3, eave))):
        poly(bm, [Fr.p(u0, v0, 0.02), Fr.p(u1, v1, 0.02), Fr.p(u1, v1 + 0.3, 0.35), Fr.p(u0, v0 + 0.3, 0.35)])
def oct_roof(part, c, apothem, z0, z1, eave=0.5, mat="roof"):
    """Low octagonal pyramid roof over an octagon turned like octagon_prism(rot=ROT)."""
    Rr = (apothem + eave) / math.cos(math.pi / 8)
    pts = [c + Vector((Rr * math.cos(ROT + math.pi / 8 + k * math.pi / 4), Rr * math.sin(ROT + math.pi / 8 + k * math.pi / 4), z0)) for k in range(8)]
    ap = c + Vector((0, 0, z1))
    for k in range(8): poly(bm_for(part, mat), [pts[k], pts[(k + 1) % 8], ap])

# ---------------------------------------------------------------- the church: nave, transept, choir (rough stone walls)
S.hall(B, NAVE[0], NAVE[1], 0.0, NAVE_END, G - 0.5, EAVE, RIDGE, mat="rough", gables=(False, False))
S.hall(B, TR[0], TR[1], TR[2], TR[3], G - 0.5, TR_EAVE, TR_RIDGE, along="a", mat="rough", gables=(True, True))
S.hall(B, CH[0], CH[1], CH[2], CH[3], G - 0.5, CH_EAVE, CH_RIDGE, mat="rough", gables=(False, True))
for a, out in ((NAVE[0], -1), (NAVE[1], 1)):                                     # the flanks: five bays each
    Fr, Lf = face_a(a, 0.0, NAVE_END, out); flank(B, Fr, Lf, 5)
for o, out in ((TR[2], -1), (TR[3], 1)):                                         # transept arms: a window each, quoins
    for (a0, a1) in ((TR[0], NAVE[0]), (NAVE[1], TR[1])):
        Fr, Lf = face_o(o, a0, a1, out); quoins(B, Fr, Lf, G, TR_EAVE)
        big_window(B, Fr, Lf / 2, G + 13.0, 6.2, 2.1)
        pbox(bm_for(B, "forte"), Fr, -0.1, Lf + 0.1, TR_EAVE - 0.25, TR_EAVE, 0, 0.4)
for a, out in ((TR[0], -1), (TR[1], 1)):                                         # transept ends
    Fr, Lf = face_a(a, TR[2], TR[3], out); quoins(B, Fr, Lf, G, TR_EAVE)
    oculus(B, Fr, Lf / 2, TR_EAVE + 1.2, 0.5, frame="forte", fill="dark", fw=0.15)
for a, out in ((CH[0], -1), (CH[1], 1)):
    Fr, Lf = face_a(a, CH[2], CH[3], out); pbox(bm_for(B, "forte"), Fr, -0.1, Lf + 0.1, CH_EAVE - 0.25, CH_EAVE, 0, 0.4)
Fr, Lf = face_o(CH[3], CH[0], CH[1], 1); quoins(B, Fr, Lf, G, CH_EAVE)            # the choir end: a tall window, an oculus
big_window(B, Fr, Lf / 2, G + 11.0, 8.6, 2.4)
oculus(B, Fr, Lf / 2, CH_EAVE + 0.9, 0.45, frame="forte", fill="dark", fw=0.15)

# ---------------------------------------------------------------- the front: rough rubble, never faced
APEX = G + 31.2
outline = [(0, G - 0.6), (L, G - 0.6), (L, G + 26.9), (L / 2, APEX), (0, G + 26.9)]
slab(B, "rough", F, outline, -1.2, 0.0)
base = [(-0.35, G - 0.6), (L + 0.35, G - 0.6), (L + 0.35, G + 9.4), (L - 0.6, G + 10.0), (0.6, G + 10.0), (-0.35, G + 9.4)]
slab(B, "rough", F, base, 0.0, 0.3)                                              # the wider lower part
fp = f"facciata_dettagli@1300-{NOW}"
DW, DH = 3.3, 6.6; uc = L / 2
poly(bm_for(fp, "wood"), [F.p(uc - DW / 2, G, 0.33), F.p(uc + DW / 2, G, 0.33), F.p(uc + DW / 2, G + DH, 0.33), F.p(uc - DW / 2, G + DH, 0.33)])
for k in range(1, 4): pbox(bm_for(fp, "wood"), F, uc - DW / 2 + 0.2, uc + DW / 2 - 0.2, G + DH * k / 4 - 0.06, G + DH * k / 4 + 0.06, 0.33, 0.38)
for (u0, u1, v0, v1) in ((uc - DW / 2 - 0.45, uc - DW / 2, G, G + DH + 0.45), (uc + DW / 2, uc + DW / 2 + 0.45, G, G + DH + 0.45), (uc - DW / 2 - 0.45, uc + DW / 2 + 0.45, G + DH, G + DH + 0.45)):
    pbox(bm_for(fp, "forte"), F, u0, u1, v0, v1, 0.3, 0.5)                    # the moulded frame
z = G; k = 0
while z < G + DH + 1.6:                                                         # the pale blocks laid long and short
    w = 1.55 if k % 2 == 0 else 1.0
    for (u0, u1) in ((uc - DW / 2 - 0.45 - w, uc - DW / 2 - 0.45), (uc + DW / 2 + 0.45, uc + DW / 2 + 0.45 + w)):
        pbox(bm_for(fp, "pale"), F, u0, u1, z + 0.03, z + 0.52, 0.3, 0.42)
    z += 0.55; k += 1
pbox(bm_for(fp, "pale"), F, uc - DW / 2 - 1.6, uc + DW / 2 + 1.6, G + DH + 0.45, G + DH + 1.1, 0.3, 0.45)
big_window(fp, F, uc, G + 13.6, 7.6, 2.2)
ring(fp, "forte", F, uc, G + 19.0, 2.6, 3.0, 0, 0.05, seg=12, soffit=False)   # the ghost of a larger arch
oculus(fp, F, uc, APEX - 3.4, 0.45, frame="forte", fill="dark", fw=0.12)
cross(fp, F.p(uc, APEX, -0.6), 1.6)
for k in range(3): box(bm_for(fp, "serena"), F, uc - 3.5 - k * 0.6, uc + 3.5 + k * 0.6, G - 0.9 + k * 0.15, G - 0.6 + k * 0.15, 0.3, 2.2 - k * 0.7)

# ---------------------------------------------------------------- the bell gable on the west chapels, facing west
V = f"campanile_a_vela@1300-{NOW}"
Fv = Frame(S.W(VELA[0] - 0.5, VELA[2]), -S.NO, -S.TA); Lv = VELA[2] - VELA[1]
box(bm_for(V, "rough"), Fv, 0, Lv, G + 10.2, G + 21.4, -1.0, 0.0)
slab(V, "rough", Fv, [(0, G + 21.4), (Lv, G + 21.4), (Lv / 2, G + 22.9)], -1.0, 0.0)
pbox(bm_for(V, "forte"), Fv, -0.15, Lv + 0.15, G + 21.2, G + 21.45, -1.1, 0.12)
for k in (0, 1):
    u = Lv * (0.27 + 0.46 * k); r = 0.68
    arch_fill(V, "dark", Fv, u - r, u + r, G + 16.6, G + 19.6, n=0.01)
    ring(V, "forte", Fv, u, G + 19.6, r, r + 0.25, 0, 0.08, seg=10, soffit=False)
    cone(V, "bronze", Fv.p(u, 0, 0.3), 0.5, 0.25, G + 17.5, G + 18.7, seg=10)
    cylinder(V, "iron", Fv.p(u, 0, 0.3), 0.06, G + 18.7, G + 19.4, seg=5)
cross(V, Fv.p(Lv / 2, G + 22.9, -0.5), 1.1)

# ---------------------------------------------------------------- the octagon over the crossing (Ruggieri's rebuilding)
T = f"tiburio@1782-{NOW}"; c = S.W(*CX)
box(bm_for(T, "plaster"), Frame(S.W(NAVE[0], TR[2]), S.TA, S.NO), 0, NAVE[1] - NAVE[0], G - 0.5, G + 28.7, 0, TR[3] - TR[2])
for Fr, Lf in (face_o(TR[2], NAVE[0], NAVE[1], -1), face_o(TR[3], NAVE[0], NAVE[1], 1), face_a(NAVE[0], TR[2], TR[3], -1), face_a(NAVE[1], TR[2], TR[3], 1)):
    pbox(bm_for(T, "plaster"), Fr, -0.1, Lf + 0.1, G + 28.4, G + 28.7, 0, 0.3)
# the square base's tiled roof slopes up to the octagon
P4 = [S.W(NAVE[0] - 0.4, TR[2] - 0.4, G + 28.7), S.W(NAVE[1] + 0.4, TR[2] - 0.4, G + 28.7), S.W(NAVE[1] + 0.4, TR[3] + 0.4, G + 28.7), S.W(NAVE[0] - 0.4, TR[3] + 0.4, G + 28.7)]
Q4 = [S.W(CX[0] - 6.5, CX[1] - 6.5, G + 29.9), S.W(CX[0] + 6.5, CX[1] - 6.5, G + 29.9), S.W(CX[0] + 6.5, CX[1] + 6.5, G + 29.9), S.W(CX[0] - 6.5, CX[1] + 6.5, G + 29.9)]
for i in range(4): poly(bm_for(T, "roof"), [P4[i], P4[(i + 1) % 4], Q4[(i + 1) % 4], Q4[i]])
AP = 8.0; z0, z1 = G + 28.7, G + 33.7
octagon_prism(T, "plaster", c, AP, z0, z1, rot=ROT)
for Fr, w, k in oct_faces(c, AP, rot=ROT):                                     # framed panels, corner strips, small holes
    pbox(bm_for(T, "plaster"), Fr, 0, 0.45, z0, z1 - 0.5, 0, 0.12); pbox(bm_for(T, "plaster"), Fr, w - 0.45, w, z0, z1 - 0.5, 0, 0.12)
    for (u0, u1, v0, v1) in ((0.9, w - 0.9, z0 + 0.6, z0 + 0.8), (0.9, w - 0.9, z1 - 1.5, z1 - 1.3), (0.9, 1.1, z0 + 0.6, z1 - 1.3), (w - 1.1, w - 0.9, z0 + 0.6, z1 - 1.3)):
        pbox(bm_for(T, "plaster"), Fr, u0, u1, v0, v1, 0, 0.06)
    for u in (w * 0.35, w * 0.65): poly(bm_for(T, "dark"), [Fr.p(u - 0.15, z1 - 0.95, 0.02), Fr.p(u + 0.15, z1 - 0.95, 0.02), Fr.p(u + 0.15, z1 - 0.65, 0.02), Fr.p(u - 0.15, z1 - 0.65, 0.02)])
octagon_prism(T, "serena", c, AP + 0.3, z1 - 0.5, z1, rot=ROT)
oct_roof(T, c, AP + 0.3, z1, G + 36.9, eave=0.6)
cylinder(T, "lead", c, 0.35, G + 36.7, G + 37.4, seg=8); sphere(T, "lead", c + Vector((0, 0, G + 37.6)), 0.25)
box(bm_for(T, "iron"), Frame(c, S.TA, -S.NO), -0.04, 0.04, G + 37.6, G + 39.0, -0.04, 0.04)
box(bm_for(T, "iron"), Frame(c, S.TA, -S.NO), 0.0, 0.7, G + 38.3, G + 38.7, -0.02, 0.02)   # the weathervane

# ---------------------------------------------------------------- the Corsini chapel (Pier Francesco Silvani, 1675–83)
P = f"cappella_corsini@1683-{NOW}"; cc = S.W(*CO)
a0, a1, o0, o1 = CO_BASE; zb = G + 15.5
box(bm_for(P, "plaster"), Frame(S.W(a0, o0), S.TA, S.NO), 0, a1 - a0, G - 0.5, zb, 0, o1 - o0)
for Fr, Lf in (face_o(o0, a0, a1, -1), face_o(o1, a0, a1, 1), face_a(a1, o0, o1, 1)):
    pbox(bm_for(P, "serena"), Fr, -0.1, Lf + 0.1, zb - 0.4, zb, 0, 0.4)
Fr, Lf = face_a(a1, o0, o1, 1)                                                  # the lunette window over the garden
r = 2.6; arch_fill(P, "glass", Fr, Lf / 2 - r, Lf / 2 + r, zb - 5.2, zb - 5.2, n=0.03)
ring(P, "plaster", Fr, Lf / 2, zb - 5.2, r, r + 0.6, 0, 0.1, seg=12, soffit=False)
for Fr, Lf in (face_o(o0, a0, a1, -1), face_o(o1, a0, a1, 1)):                  # low roofs round the drum
    poly(bm_for(P, "roof"), [Fr.p(-0.3, zb, 0.5), Fr.p(Lf + 0.3, zb, 0.5), Fr.p(Lf - 1.0, zb + 1.2, -1.5), Fr.p(1.0, zb + 1.2, -1.5)])
AC = 4.6; d0, d1 = zb, G + 21.4
octagon_prism(P, "plaster", cc, AC, d0, d1, rot=ROT)
for Fr, w, k in oct_faces(cc, AC, rot=ROT):
    win_rect(P, Fr, w / 2, d0 + 2.0, d0 + 3.6, 1.3, frame="serena", fill="glass", fw=0.18)
    pbox(bm_for(P, "plaster"), Fr, 0, 0.3, d0, d1 - 0.4, 0, 0.1); pbox(bm_for(P, "plaster"), Fr, w - 0.3, w, d0, d1 - 0.4, 0, 0.1)
octagon_prism(P, "serena", cc, AC + 0.3, d1 - 0.4, d1, rot=ROT)
oct_roof(P, cc, AC + 0.3, d1, G + 23.3, eave=0.5)
column_lantern(P, cc, G + 23.0, 1.0, 3.2, n=8, mat="serena")

# ---------------------------------------------------------------- the first cloister (south loggia 1597–1600, the others 1612)
def hole_box(k):
    h = S.D["polys"][3][1][k]
    A = [(p[0] - S.A[0]) * S.t[0] + (p[1] - S.A[1]) * S.t[1] for p in h]; O = [(p[0] - S.A[0]) * S.n[0] + (p[1] - S.A[1]) * S.n[1] for p in h]
    return min(A), max(A), min(O), max(O)
holes = sorted((hole_box(k) for k in range(len(S.D["polys"][3][1]))), key=lambda b: -(b[1] - b[0]) * (b[3] - b[2]))
print("convent courts", [tuple(round(x, 1) for x in b) for b in holes[:3]])
C0 = holes[0]
gr = S.D["grid"]
gC = gr["g"][int((C0[2] + C0[3]) / 2 - gr["o0"])][int((C0[0] + C0[1]) / 2 - gr["a0"])] or G
gC += 0.05
CL = f"chiostro@1612-{NOW}"
S.cloister(CL, C0[0], C0[1], C0[2], C0[3], gC, gC + 3.7, (max(3, round((C0[1] - C0[0]) / 3.9)), max(3, round((C0[3] - C0[2]) / 3.9))), 4.0,
           gC + 9.2, kind="loggia", upper=(1.0, 0, 0, "colonnade"), garth="lawn", well="well", wall="conv")
def in_cloister(a, o, d=4.6):
    return C0[0] - d <= a <= C0[1] + d and C0[2] - d <= o <= C0[3] + d

# ---------------------------------------------------------------- everything else from the DSM
def hand(a, o, m=0.3):
    """Inside the hand-built church, octagon or chapel."""
    if NAVE[0] - m <= a <= NAVE[1] + m and -1.0 <= o <= NAVE_END + m: return True
    if TR[0] - m <= a <= TR[1] + m and TR[2] - m <= o <= TR[3] + m: return True
    if CH[0] - m <= a <= CH[1] + m and CH[2] - m <= o <= CH[3] + m: return True
    if CO_BASE[0] - m <= a <= CO_BASE[1] + m and CO_BASE[2] - m <= o <= CO_BASE[3] + m: return True
    return False
for j in range(gr["no"]):                                    # the bell gable is built by hand: the chapel roof under it
    for i in range(gr["na"]):
        a, o = gr["a0"] + i + 0.5, gr["o0"] + j + 0.5
        if VELA[0] - 1.6 <= a <= VELA[0] + 1.6 and VELA[1] - 1.0 <= o <= VELA[2] + 1.0 and gr["h"][j][i] is not None:
            gr["h"][j][i] = min(gr["h"][j][i], G + 10.6)
def phase(a, o, k):
    if hand(a, o): return None
    if k == 3 and in_cloister(a, o): return None
    if k == 0: return ("cappelle", 1300)
    return {1: ("annessi_est", 1500), 2: ("annessi_sud", 1500), 3: ("convento", 1300)}[k]
def detail(part):
    if part in ("convento", "annessi_est", "annessi_sud"): return {"roof": "hip", "windows": True, "mat": "conv"}
    return {"roof": "hip", "windows": False, "mat": "rough"}
def solid(a, o): return hand(a, o, 0.0)
print("massing", S.raster(phase, detail=detail, solid=solid))
K.export("carmine")
