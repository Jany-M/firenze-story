"""Basilica di San Miniato al Monte with its bell tower, the Bishops' Palace and the monastery (v1).

Run:  python pipeline/45_chiese.py   (once: outlines, ground, DSM raster → blender/data/chiese.json)
      blender -b --python blender/scripts/build_miniato.py  →  web/public/models/landmarks/miniato.glb
Frame: a along the front (OSM way 184781037) from its corner by the Bishops' Palace, o inwards along the church's axis.
Measured (LiDAR 2023 DSM, ground of the terrace 95.1 m scene): the nave's ridge ≈20.3 above the terrace on a 9.4 (1.4 m off
the OSM front's middle: the front is centred on it), the nave a 2.9–15.9 with eaves ≈16.5, the aisles ≈12–13 out to
a −1.1 and 19.9; the church from o 1.5 to 50, the apse to ≈55 with its roof ≈14.5; the bell tower ≈7 m square at a 27.8,
o 42.6, its top ≈32.7; the Bishops' Palace along the front (a −48…−6, o 2–12) ≈16–17, the monastery's wings ≈12–13 round a
court a −35…−8, o 14–34, the back wing ≈16–17 (o 40–50).
Details from photographs (docs/materials): the front in white marble and green serpentine (Elisa Marianini 2018, Txllxt
TxllxT 2010): five round arches on half-columns below, three doors; above, the nave's front between four pilasters, two
panels with wheel roundels, the mosaic of Christ between the Virgin and St Minias over a small window in an aedicule,
the pediment with a frieze of little arches, the copper eagle of the Arte di Calimala on a pinnacle; the aisles' sloping
fronts with a diamond lattice; the apse (Zairon 2023): stone, pilaster strips, windows closed with thin marble slabs,
a half-cone roof; the bell tower: pietra forte, corner pilasters, an arched belfry with the bells, round windows in rings
above, the top never finished.
Dates (docs/landmarks/SAN-MINIATO.md): the church begun 1018; the marble front finished in the early 13th century (shown
from 1207, *inferred*), the mosaic 13th century (shown from 1260, *inferred*), the eagle from 1288 (Calimala); the old bell
tower fell in 1499 (shown 1100–1499, size *inferred*), the new one by Baccio d'Agnolo from 1523, never finished; the
Bishops' Palace 1295; the cloister 1443–c. 1455; the monastery from 1018 (*inferred*).
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from mathutils import Vector
from landmark_detail import *
from landmark_church import Site, slab, extra_materials
K.reset()
MAT["rough"] = material("rubble_stone", "pietra_forte", (0.6, 0.5, 0.38), 0.9, 0.5, tint=(2.6, 2.4, 2.1))
MAT["forte"] = material("pietra_forte", "pietra_forte", (0.62, 0.5, 0.36), 0.85, 0.32, tint=(3.0, 2.85, 2.55))
MAT["marble"] = material("marble_white_sm", None, (0.92, 0.91, 0.88), 0.45)
MAT["verde"] = material("serpentine_green", None, (0.12, 0.17, 0.14), 0.4)
MAT["mosaic"] = material("mosaic_gold", None, (0.85, 0.66, 0.3), 0.35, metal=0.6)
MAT["copper"] = material("copper_eagle", None, (0.28, 0.24, 0.2), 0.5, metal=0.7)
MAT["serena"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)
MAT["iron"] = material("wrought_iron", None, (0.08, 0.08, 0.08), 0.6, metal=0.6)
extra_materials()
MAT["conv"] = material("plaster_convent", None, (0.86, 0.78, 0.62), 0.9)
NOW = K.NOW
S = Site("miniato"); G = S.G
AX = 9.4; HW = 10.8                                      # the axis and the front's half width
NAVE = (AX - 6.5, AX + 6.5); AISLE = (AX - 10.4, AX + 10.4)
O0, O1 = 1.5, 50.0; EAVE, RIDGE = G + 16.5, G + 20.3
F = Frame(S.W(AX - HW, O0), S.TA, -S.NO); FW = 2 * HW     # the front: u 0..FW, n outwards
TW = (27.8, 42.6, 7.0)
B = f"chiesa@1018-{NOW}"

def face_a(a, o0, o1, out):
    return (Frame(S.W(a, o1), -S.NO, -S.TA), o1 - o0) if out < 0 else (Frame(S.W(a, o0), S.NO, S.TA), o1 - o0)
def strip(part, Fr, u0, v0, u1, v1, w=0.12, n=0.05, mat="verde"):
    """A thin inlaid band from (u0, v0) to (u1, v1)."""
    du, dv = u1 - u0, v1 - v0; l = math.hypot(du, dv) or 1; pu, pv = -dv / l * w / 2, du / l * w / 2
    poly(bm_for(part, mat), [Fr.p(u0 - pu, v0 - pv, n), Fr.p(u1 - pu, v1 - pv, n), Fr.p(u1 + pu, v1 + pv, n), Fr.p(u0 + pu, v0 + pv, n)])
def rect_band(part, Fr, u0, u1, v0, v1, w=0.14, n=0.05):
    for (a, b, c, d) in ((u0, v0, u1, v0), (u1, v0, u1, v1), (u1, v1, u0, v1), (u0, v1, u0, v0)): strip(part, Fr, a, b, c, d, w, n)
def roundel(part, Fr, u, v, r, n=0.05):
    ring(part, "verde", Fr, u, v, r - 0.18, r, n - 0.01, n, a0=0, a1=2 * math.pi, seg=20, soffit=False)
    ring(part, "verde", Fr, u, v, r * 0.35, r * 0.35 + 0.14, n - 0.01, n, a0=0, a1=2 * math.pi, seg=12, soffit=False)
    for k in range(4):
        t = math.pi / 4 + k * math.pi / 2
        strip(part, Fr, u + r * 0.42 * math.cos(t), v + r * 0.42 * math.sin(t), u + (r - 0.2) * math.cos(t), v + (r - 0.2) * math.sin(t), 0.12, n)
    oculus(part, Fr, u, v, r * 0.3, frame="marble", fill="dark", fw=0.02)

# ---------------------------------------------------------------- the church body: nave, aisles, apse (stone)
S.hall(B, NAVE[0], NAVE[1], O0, O1, G - 0.5, EAVE, RIDGE, mat="forte", gables=(False, True))
def lean_to(part, a_in, a_out, o0, o1, h_in, h_out):
    lo, hi = min(a_in, a_out), max(a_in, a_out)
    box(bm_for(part, "forte"), Frame(S.W(lo, o0), S.TA, S.NO), 0, hi - lo, G - 0.5, min(h_in, h_out), 0, o1 - o0)
    e = 0.4 if a_out > a_in else -0.4
    quad = [S.W(a_in, o0, h_in), S.W(a_out + e, o0, h_out), S.W(a_out + e, o1, h_out), S.W(a_in, o1, h_in)]
    poly(bm_for(part, "roof"), quad if a_out > a_in else quad[::-1])
    for o in (o0, o1): poly(bm_for(part, "forte"), [S.W(a_in, o, min(h_in, h_out)), S.W(a_out, o, min(h_in, h_out)), S.W(a_in, o, h_in)])
for a_in, a_out in ((NAVE[0], AISLE[0]), (NAVE[1], AISLE[1])):
    lean_to(B, a_in, a_out, O0, O1 - 2.0, G + 13.2, G + 11.0)
for a, out in ((NAVE[0], -1), (NAVE[1], 1)):                                   # small clerestory windows
    Fr, Lf = face_a(a, O0, O1, out)
    for k in range(7): win_round(B, Fr, (k + 0.5) * Lf / 7, G + 13.9, G + 15.6, 0.6, frame="forte", fill="dark", fw=0.12)
for a, out in ((AISLE[0], -1), (AISLE[1], 1)):
    Fr, Lf = face_a(a, O0, O1 - 2.0, out)
    for k in range(6): win_round(B, Fr, (k + 0.5) * Lf / 6, G + 6.0, G + 8.6, 0.8, frame="forte", fill="dark", fw=0.14)
# the apse: a half-cylinder with pilaster strips and windows closed with marble, a half-cone roof
ac = S.W(AX, O1); R_ = 5.6; zA = G + 13.6; n_ = 12
pts = [(AX + R_ * math.cos(math.pi * k / n_), O1 + R_ * math.sin(math.pi * k / n_)) for k in range(n_ + 1)]
for k in range(n_):
    (a0_, o0_), (a1_, o1_) = pts[k], pts[k + 1]
    poly(bm_for(B, "forte"), [S.W(a0_, o0_, G - 0.5), S.W(a1_, o1_, G - 0.5), S.W(a1_, o1_, zA), S.W(a0_, o0_, zA)][::-1])
    e0, e1 = 0.4, 0.4
    poly(bm_for(B, "roof"), [S.W(AX + (a0_ - AX) * (R_ + e0) / R_, O1 + (o0_ - O1) * (R_ + e0) / R_, zA), S.W(AX + (a1_ - AX) * (R_ + e1) / R_, O1 + (o1_ - O1) * (R_ + e1) / R_, zA), S.W(AX, O1, zA + 2.2)][::-1])
for k in (2, 6, 10):                                                           # pilaster strips
    t = math.pi * k / n_; d = Vector((S.TA * math.cos(t) + S.NO * math.sin(t))); d.z = 0
    Fr = Frame(ac + d * R_, Vector((-d.y, d.x, 0)), d)
    pbox(bm_for(B, "forte"), Fr, -0.5, 0.5, G - 0.5, zA - 0.3, 0, 0.3)
for k in (4, 8):                                                               # windows of thin marble
    t = math.pi * k / n_; d = Vector((S.TA * math.cos(t) + S.NO * math.sin(t))); d.z = 0
    Fr = Frame(ac + d * R_, Vector((-d.y, d.x, 0)), d)
    poly(bm_for(B, "marble"), [Fr.p(-0.45, G + 6.0, 0.05), Fr.p(0.45, G + 6.0, 0.05), Fr.p(0.45, G + 9.0, 0.05), Fr.p(-0.45, G + 9.0, 0.05)])

# ---------------------------------------------------------------- the front: rough until the marble facing (early 13th c.)
outline = [(0, G - 0.6), (FW, G - 0.6), (FW, G + 11.0), (HW + 6.5, G + 13.2), (HW + 6.5, EAVE), (HW, RIDGE), (HW - 6.5, EAVE), (HW - 6.5, G + 13.2), (0, G + 11.0)]
slab("facciata_grezza@1018-1207", "forte", F, outline, -1.0, 0.0)
FP = f"facciata@1207-{NOW}"
slab(FP, "marble", F, outline, -1.0, 0.05)
# lower register: five arches on half-columns, three doors
nb = 5; bw = FW / nb; spring = G + 6.0
for k in range(nb + 1):
    u = k * bw
    if 0 < k < nb:
        cylinder(FP, "verde", F.p(u, 0, 0.1), 0.32, G - 0.3, spring - 0.6, seg=10)
        cone(FP, "marble", F.p(u, 0, 0.1), 0.34, 0.5, spring - 0.6, spring, seg=10)
    else:
        pbox(bm_for(FP, "verde"), F, u - 0.35 if k else 0, u if k else 0.35, G - 0.3, G + 8.6, 0.05, 0.25)
for k in range(nb):
    uc = (k + 0.5) * bw; r = bw / 2 - 0.15
    ring(FP, "verde", F, uc, spring, r, r + 0.35, 0.05, 0.12, seg=14, soffit=False)
    rect_band(FP, F, uc - r + 0.3, uc + r - 0.3, G + 0.3, spring - 0.3)
    if k in (1, 2, 3):                                                         # the doors in a frame of green bands
        dw = 2.0 if k == 2 else 1.6; dh = 4.2 if k == 2 else 3.6
        poly(bm_for(FP, "wood"), [F.p(uc - dw / 2, G, 0.07), F.p(uc + dw / 2, G, 0.07), F.p(uc + dw / 2, G + dh, 0.07), F.p(uc - dw / 2, G + dh, 0.07)])
        rect_band(FP, F, uc - dw / 2 - 0.15, uc + dw / 2 + 0.15, G, G + dh + 0.15, w=0.25, n=0.08)
for k in range(1, nb):                                                         # inlaid triangles in the spandrels
    u = k * bw
    for (a, b, c, d) in ((u - 0.7, spring + 1.3, u + 0.7, spring + 1.3), (u + 0.7, spring + 1.3, u, spring + 0.5), (u, spring + 0.5, u - 0.7, spring + 1.3)):
        strip(FP, F, a, b, c, d, 0.1)
for v in (G + 8.6, G + 9.3):                                                   # the bands over the arcade
    pbox(bm_for(FP, "verde"), F, -0.1, FW + 0.1, v, v + 0.25, 0.05, 0.2)
pbox(bm_for(FP, "marble"), F, -0.2, FW + 0.2, G + 9.55, G + 9.9, 0.05, 0.35)
# the aisles' sloping fronts with the diamond lattice
for side in (-1, 1):
    ua, ub = (0.0, HW - 6.5) if side < 0 else (FW, HW + 6.5)
    va, vb = G + 11.0, G + 13.2
    strip(FP, F, ua, va, ub, vb, 0.25, 0.08)
    for k in range(6):
        t = (k + 0.5) / 6; u = ua + (ub - ua) * t; vt = va + (vb - va) * t - 0.25
        strip(FP, F, u - 0.4, G + 10.1, u + 0.4, vt, 0.1); strip(FP, F, u + 0.4, G + 10.1, u - 0.4, vt, 0.1)
# the upper register: four pilasters, wheel roundels, the mosaic over the aedicule window, the pediment
c0 = HW - 6.5; pil = (c0, c0 + 4.3, c0 + 8.7, c0 + 13.0)
for u in pil: pbox(bm_for(FP, "marble"), F, u - 0.35, u + 0.35, G + 9.9, EAVE - 0.4, 0.05, 0.25)
for u in pil: pbox(bm_for(FP, "marble"), F, u - 0.45, u + 0.45, EAVE - 0.8, EAVE - 0.4, 0.05, 0.32)
for (u0, u1) in ((pil[0] + 0.35, pil[1] - 0.35), (pil[2] + 0.35, pil[3] - 0.35)):
    um = (u0 + u1) / 2
    roundel(FP, F, um, G + 14.5, 1.45)
    rect_band(FP, F, u0 + 0.25, u1 - 0.25, G + 10.3, G + 12.9)
    strip(FP, F, um, G + 10.5, um, G + 12.7, 0.12)
um = HW
rect_band(FP, F, um - 1.95, um + 1.95, G + 13.45, G + 15.85, w=0.2)
win_rect(FP, F, um, G + 10.6, G + 12.4, 0.9, frame="marble", fill="dark", fw=0.22, pediment="cornice")
bmp = bm_for(FP, "marble")
poly(bmp, [F.p(um - 1.0, G + 12.85, 0.3), F.p(um + 1.0, G + 12.85, 0.3), F.p(um, G + 13.4, 0.3)])
for k in range(5):                                                             # diamond lattice beside the window
    for s_ in (-1, 1):
        u = um + s_ * 1.4; v = G + 10.4 + k * 0.6
        strip(FP, F, u - 0.3, v, u, v + 0.3, 0.07); strip(FP, F, u, v + 0.3, u + 0.3, v, 0.07)
pbox(bm_for(FP, "marble"), F, pil[0] - 0.5, pil[3] + 0.5, EAVE - 0.4, EAVE, 0.05, 0.45)          # the entablature
pbox(bm_for(FP, "verde"), F, pil[0] - 0.3, pil[3] + 0.3, EAVE - 0.3, EAVE - 0.15, 0.4, 0.47)
for k in range(10):                                                            # the pediment's frieze of little arches
    u = pil[0] + 0.7 + k * (pil[3] - pil[0] - 1.4) / 9
    vtop = EAVE + (RIDGE - EAVE) * (1 - abs(u - HW) / 6.5) - 0.5
    if vtop - (EAVE + 0.4) > 0.9:
        ring(FP, "verde", F, u, EAVE + 1.0, 0.45, 0.6, 0.04, 0.08, seg=8, soffit=False)
        strip(FP, F, u - 0.52, EAVE + 0.3, u - 0.52, EAVE + 1.0, 0.13); strip(FP, F, u + 0.52, EAVE + 0.3, u + 0.52, EAVE + 1.0, 0.13)
for (u0, v0), (u1, v1) in (((pil[0] - 0.6, EAVE), (HW, RIDGE + 0.2)), ((HW, RIDGE + 0.2), (pil[3] + 0.6, EAVE))):
    poly(bm_for(FP, "marble"), [F.p(u0, v0, 0.05), F.p(u1, v1, 0.05), F.p(u1, v1 + 0.4, 0.5), F.p(u0, v0 + 0.4, 0.5)])
EG = f"aquila@1288-{NOW}"; pc = F.p(HW, 0, -0.3)
box(bm_for(EG, "marble"), Frame(pc - S.TA * 0.4 - S.NO * 0.4, S.TA, S.NO), 0, 0.8, RIDGE, RIDGE + 1.3, 0, 0.8)
cone(EG, "marble", pc, 0.5, 0.3, RIDGE + 1.3, RIDGE + 1.6, seg=8)
box(bm_for(EG, "copper"), Frame(pc, S.TA, -S.NO), -0.2, 0.2, RIDGE + 1.6, RIDGE + 2.4, -0.25, 0.25)          # the eagle
box(bm_for(EG, "copper"), Frame(pc, S.TA, -S.NO), -0.75, 0.75, RIDGE + 2.0, RIDGE + 2.35, -0.08, 0.08)       # spread wings
MS = f"mosaico@1260-{NOW}"
poly(bm_for(MS, "mosaic"), [F.p(um - 1.7, G + 13.7, 0.12), F.p(um + 1.7, G + 13.7, 0.12), F.p(um + 1.7, G + 15.6, 0.12), F.p(um - 1.7, G + 15.6, 0.12)])
for x in (-1.1, 0.0, 1.1):
    poly(bm_for(MS, "verde" if x else "dark"), [F.p(um + x - 0.25, G + 13.8, 0.14), F.p(um + x + 0.25, G + 13.8, 0.14), F.p(um + x + 0.25, G + 15.2, 0.14), F.p(um + x - 0.25, G + 15.2, 0.14)])

# ---------------------------------------------------------------- the bell towers: the old one (fell 1499), Baccio d'Agnolo's (1523)
gr = S.D["grid"]
def gnd(a, o):
    v = gr["g"][int(o - gr["o0"])][int(a - gr["a0"])]
    return v if v is not None else G
ta, to, ts = TW; h = ts / 2; gT = min(gnd(ta, to), G) + 0.05
Fb = Frame(S.W(ta - h, to - h), S.TA, S.NO)
faces = [(Frame(o_, u_, n_), ts) for (o_, u_, n_) in ((S.W(ta - h, to - h), S.TA, -S.NO), (S.W(ta + h, to - h), S.NO, S.TA), (S.W(ta + h, to + h), -S.TA, S.NO), (S.W(ta - h, to + h), -S.NO, -S.TA))]
TO = "campanile_medievale@1100-1499"
box(bm_for(TO, "forte"), Fb, 0.6, ts - 0.6, gT - 0.5, G + 26.0, 0.6, ts - 0.6)
rp = [S.W(ta - h + 0.3, to - h + 0.3, G + 26.0), S.W(ta + h - 0.3, to - h + 0.3, G + 26.0), S.W(ta + h - 0.3, to + h - 0.3, G + 26.0), S.W(ta - h + 0.3, to + h - 0.3, G + 26.0)]
for p0, p1 in zip(rp, rp[1:] + rp[:1]): poly(bm_for(TO, "roof"), [p0, p1, S.W(ta, to, G + 28.5)])
T = f"campanile@1523-{NOW}"; TOP = G + 32.6
box(bm_for(T, "forte"), Fb, 0, ts, gT - 0.5, TOP - 0.6, 0, ts)
for Fr, Lf in faces:
    for u0 in (0.0, Lf - 0.8): pbox(bm_for(T, "forte"), Fr, u0, u0 + 0.8, gT, G + 30.6, 0, 0.18)       # corner pilasters
    pbox(bm_for(T, "forte"), Fr, -0.2, Lf + 0.2, G + 21.3, G + 21.9, 0, 0.45)                       # the cornice under the belfry
    pbox(bm_for(T, "forte"), Fr, -0.1, Lf + 0.1, G + 26.6, G + 26.9, 0, 0.25)
    r = 0.9; sp = G + 25.2
    arch_fill(T, "dark", Fr, Lf / 2 - r, Lf / 2 + r, G + 22.3, sp, n=0.03)
    ring(T, "forte", Fr, Lf / 2, sp, r, r + 0.35, 0, 0.15, seg=10, soffit=False)
    cone(T, "bronze", Fr.p(Lf / 2, 0, -0.5), 0.5, 0.22, G + 23.4, G + 24.6, seg=10)
    ring(T, "forte", Fr, Lf / 2, G + 28.8, 0.75, 1.15, 0, 0.12, a0=0, a1=2 * math.pi, seg=16, soffit=False)
    poly(bm_for(T, "dark"), [Fr.p(Lf / 2 + 0.75 * math.cos(q), G + 28.8 + 0.75 * math.sin(q), 0.02) for q in [2 * math.pi * i / 12 for i in range(12)]])
    for k in range(5):                                                         # the unfinished top: ragged courses
        u0 = k * Lf / 5; hh = 0.3 + 0.35 * ((k * 7) % 3)
        box(bm_for(T, "forte"), Fr, u0, u0 + Lf / 5, TOP - 0.6, TOP - 0.6 + hh, -0.6, 0.0)

# ---------------------------------------------------------------- the cloister (1443–c. 1455) in the monastery's court
CA, CO_ = (-32.0, -11.0), (17.0, 31.0)
gC = gnd((CA[0] + CA[1]) / 2, (CO_[0] + CO_[1]) / 2) + 0.05
S.cloister(f"chiostro@1455-{NOW}", CA[0], CA[1], CO_[0], CO_[1], gC, gC + 3.6, (max(3, round((CA[1] - CA[0]) / 3.6)), max(3, round((CO_[1] - CO_[0]) / 3.6))), 3.2,
           gC + 8.5, kind="loggia", upper=(1.2, 1.5, 0.9, "plain"), garth="lawn", well="well", wall="conv")
def in_cloister(a, o, d=3.6):
    return CA[0] - d <= a <= CA[1] + d and CO_[0] - d <= o <= CO_[1] + d

# ---------------------------------------------------------------- everything else from the DSM: the Bishops' Palace, the monastery
def hand(a, o, m=0.3):
    if AISLE[0] - m <= a <= AISLE[1] + m and O0 - 1.0 <= o <= O1 + 6.0: return True
    return abs(a - TW[0]) <= TW[2] / 2 + m and abs(o - TW[1]) <= TW[2] / 2 + m
def phase(a, o, k):
    if hand(a, o) or k != 5 or o > 51.0 or in_cloister(a, o): return None    # the houses at the side stay city records
    if o < 13.0 and a < -5.0: return ("palazzo_vescovi", 1295)
    return ("monastero", 1018)
def detail(part):
    return {"roof": "hip", "windows": True, "mat": "rough" if part == "palazzo_vescovi" else "conv"}
def solid(a, o): return hand(a, o, 0.0)
print("massing", S.raster(phase, detail=detail, solid=solid))
K.export("miniato")
