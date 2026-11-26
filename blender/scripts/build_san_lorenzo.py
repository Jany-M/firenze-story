"""San Lorenzo: basilica, Old and New Sacristy, cloister, Laurentian Library, Cappella dei Principi, bell tower – dated model (v1).

Run:  blender -b --python blender/scripts/build_san_lorenzo.py  →  web/public/models/landmarks/san_lorenzo.glb
Frame: absolute scene coordinates (Blender X = scene x, Blender Y = −scene z); the app places it at [0, 0], rot 0, ground 7.8
(Piazza San Lorenzo, 47.8 m a.s.l.). Heights measured on the LiDAR 2023 DSM (0.5 m) and given here above that ground.
Axis: façade centre (−56.0 / −332.1), nave towards the Cappella dei Principi, 12.6° north of west.
Measured: façade 31.6 m wide (OSM way 599900778); nave ridge ≈27.6 m, aisle roofs ≈17.6 m, chapels ≈12 m; crossing tiburio ≈36.4 m;
Old Sacristy ≈26.9 m; New Sacristy ≈33.7 m; bell tower ≈50 m; Cappella dei Principi lantern ≈61 m, octagon apothem ≈19 m.
Details from photographs (docs/landmarks/SAN-LORENZO.md, pictures in docs/materials): rubble façade with the brick relieving arch
and three portals under brick arches, steps along the front and the north flank; chapel wall in ashlar with tall blind arches
and pilaster strips; oculi in the aisle wall; round-headed clerestory windows under a pietra serena entablature; square crossing
tiburio with an arcaded loggia; transept ends with pilasters, a great window and an oculus; New Sacristy drum with Michelangelo's
columned lantern; Cappella dei Principi in pietra forte with white marble frames, half-domed niches on the diagonal faces,
drum windows in scrolled marble frames, ribbed dome and columned lantern; bell tower with belfry, balustrade and cupola;
cloister with arches on columns and a trabeated upper loggia.
Dates (docs/landmarks/SAN-LORENZO.md): church of 393 (conjectural mass) → enlarged 1059 → Brunelleschi from 1421 (Old Sacristy
1421–28), transept and choir shown from 1440 (inferred), nave and crossing 1461 (high altar consecrated, "almost finished");
cloister 1457–60; New Sacristy c. 1521–34 (dome 1524, inferred); Laurentian Library, shown from 1571 (opening year, inferred);
Cappella dei Principi begun 1604, dome 1640 (en.wikipedia; 1743 elsewhere – see the doc); bell tower 1740 (Ferdinando Ruggieri).
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from mathutils import Vector, Matrix
from landmark_detail import *
K.reset()
MAT["stone"] = material("pietra_forte", "pietra_forte", (0.62, 0.5, 0.36), 0.85, 0.32, tint=(3.0, 2.85, 2.55))
MAT["rubble"] = material("rubble_facade", "pietra_forte", (0.58, 0.48, 0.36), 0.95, 0.22, tint=(2.7, 2.5, 2.2))
MAT["shade"] = material("stone_shade", "pietra_forte", (0.48, 0.38, 0.28), 0.9, 0.32, tint=(2.3, 2.1, 1.85))
MAT["serena"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)
MAT["plaster"] = material("plaster_white", None, (0.88, 0.85, 0.78), 0.9)
MAT["ochre"] = material("plaster_ochre", None, (0.78, 0.6, 0.42), 0.9)
MAT["joint"] = material("mortar_joint", None, (0.3, 0.26, 0.22), 0.95)
MAT["iron"] = material("wrought_iron", None, (0.08, 0.08, 0.08), 0.6, metal=0.6)
MAT["lawn"] = material("lawn", None, (0.24, 0.38, 0.17), 0.95)
MAT["hedge"] = material("box_hedge", None, (0.12, 0.26, 0.1), 0.95)
NOW = K.NOW

O = (-56.0, -332.1)                         # façade centre, scene x/z
AX = (-0.975, -0.218)                       # into the church (scene x/z)
LT = (-0.218, 0.975)                        # lateral, positive towards the Old Sacristy / cloister side (south)
def P(a, b, z=0.0):
    """Point a m along the axis from the façade, b m to the south side, z up → Blender coords."""
    return Vector((O[0] + a * AX[0] + b * LT[0], -(O[1] + a * AX[1] + b * LT[1]), z))
def Pxz(x, z, h=0.0): return Vector((x, -z, h))
UB = (P(1, 0) - P(0, 0)); VB = (P(0, 1) - P(0, 0))
Z = Vector((0, 0, 1))

# ---------------------------------------------------------------- frame-specific helpers (shared details: landmark_detail.py)
def blk(part, mat, a0, a1, b0, b1, z0, z1):
    if z0 == 0: z0 = -1.5                                            # walls go into the ground (it falls 1.3 m to the west)
    box(bm_for(part, mat), Frame(P(a0, b0), UB, VB), 0, a1 - a0, z0, z1, 0, b1 - b0)
def gable_ab(part, a0, a1, b0, b1, z0, ridge, along=True, mat="roof", end_mat="rubble"):
    bm = bm_for(part, mat)
    if along:
        bm_ = (b0 + b1) / 2
        poly(bm, [P(a0 - 0.4, b0 - 0.4, z0), P(a1 + 0.4, b0 - 0.4, z0), P(a1 + 0.4, bm_, ridge), P(a0 - 0.4, bm_, ridge)])
        poly(bm, [P(a1 + 0.4, b1 + 0.4, z0), P(a0 - 0.4, b1 + 0.4, z0), P(a0 - 0.4, bm_, ridge), P(a1 + 0.4, bm_, ridge)])
        for a in (a0, a1): poly(bm_for(part, end_mat), [P(a, b0, z0), P(a, b1, z0), P(a, bm_, ridge)])
    else:
        am = (a0 + a1) / 2
        poly(bm, [P(a0 - 0.4, b0, z0), P(a0 - 0.4, b1, z0), P(am, b1, ridge), P(am, b0, ridge)])
        poly(bm, [P(a1 + 0.4, b1, z0), P(a1 + 0.4, b0, z0), P(am, b0, ridge), P(am, b1, ridge)])
        for b in (b0, b1): poly(bm_for(part, end_mat), [P(a0, b, z0), P(a1, b, z0), P(am, b, ridge)])
def lean_ab(part, a0, a1, b_low, b_high, z_low, z_high):
    s = 0.5 if b_low > b_high else -0.5
    poly(bm_for(part, "roof"), [P(a0, b_low + s, z_low - 0.2), P(a1, b_low + s, z_low - 0.2), P(a1, b_high, z_high), P(a0, b_high, z_high)])


# ---------------------------------------------------------------- before Brunelleschi (masses, conjectural)
E = "church_early@393-1059"
blk(E, "rubble", 8, 44, -7, 7, 0, 11); gable_ab(E, 8, 44, -7, 7, 11, 14)
door(E, Frame(P(8, 7), -VB, -UB), 7.0, 2.2, 3.6, arch_mat="rubble", gate=False)
R = "church_1059@1059-1450"
blk(R, "rubble", 2, 56, -9, -4.5, 0, 9.5); blk(R, "rubble", 2, 56, 4.5, 9, 0, 9.5)
blk(R, "rubble", 2, 56, -4.5, 4.5, 0, 15.5)
gable_ab(R, 2, 56, -4.5, 4.5, 15.5, 19.0); lean_ab(R, 2, 56, -9, -4.5, 9.5, 11.5); lean_ab(R, 2, 56, 9, 4.5, 9.5, 11.5)
for s in (-1, 1):
    F = Frame(P(2, s * 4.5), UB, VB * s)
    for i in range(9): win_round(R, F, 4 + i * 6, 11.8, 14.2, 0.7, frame="rubble")
    F = Frame(P(2, s * 9), UB, VB * s)
    for i in range(9): win_round(R, F, 4 + i * 6, 5.5, 7.5, 0.5, frame="rubble")
blk(R, "rubble", 56, 63, -5, 5, 0, 14); cylinder(R, "rubble", P(63, 0), 4.9, -1.5, 13.0, seg=12); cone(R, "roof", P(63, 0), 5.3, 0.3, 13.0, 15.5, seg=12)
Ff = Frame(P(2, 9), -VB, -UB)
rubble(R, Ff, 0, 18, 0.0, lambda u: 9.5 if (u < 4.5 or u > 13.5) else 15.5, seed=1059)
door(R, Ff, 9.0, 2.6, 4.4, arch_mat="rubble", gate=False)
oculus(R, Ff, 9.0, 11.5, 1.2, frame="stone")
blk(R, "rubble", 30, 35, 9, 14, 0, 24); cone(R, "roof", P(32.5, 11.5), 3.6, 0.2, 24, 27, seg=4)

# ---------------------------------------------------------------- Brunelleschi's church
A_CR0, A_CR1 = 61.4, 73.4           # crossing
A_CH1 = 84.0                         # choir end (the Cappella dei Principi starts here)
NAVE_W, AISLE, CHAP, BF = 6.0, 11.0, 15.8, 22.0
NB = 8; BAY = A_CR0 / NB
T = "transept@1440-" + str(NOW)
blk(T, "stone", A_CR0, A_CR1, -BF, BF, 0, 21.0)
gable_ab(T, A_CR0, A_CR1, -BF, -NAVE_W, 21.0, 27.6, along=False, end_mat="stone"); gable_ab(T, A_CR0, A_CR1, NAVE_W, BF, 21.0, 27.6, along=False, end_mat="stone")
blk(T, "stone", A_CR1, A_CH1, -NAVE_W, NAVE_W, 0, 21.0); gable_ab(T, A_CR1, A_CH1, -NAVE_W, NAVE_W, 21.0, 27.3, end_mat="stone")
for s in (-1, 1):
    blk(T, "stone", A_CR1, A_CH1, min(s * AISLE, s * NAVE_W), max(s * AISLE, s * NAVE_W), 0, 12.0)       # choir chapels
    lean_ab(T, A_CR1, A_CH1, s * AISLE, s * NAVE_W, 12.0, 14.2)
    blk(T, "stone", A_CR0 - 6.2, A_CR0, min(s * CHAP, s * BF), max(s * CHAP, s * BF), 0, 10.5)          # chapels on the transept's west side
    poly(bm_for(T, "roof"), [P(A_CR0 - 6.6, s * CHAP, 10.3), P(A_CR0 - 6.6, s * (BF + 0.4), 10.3), P(A_CR0, s * (BF + 0.4), 12.4), P(A_CR0, s * CHAP, 12.4)])
    Fw = Frame(P(A_CR0 - 6.2, s * CHAP), VB * s, -UB)                              # their west face: blind arch and oculus
    blind_arch(T, Fw, 1.0, BF - CHAP - 1.0, 0.0, 6.8); oculus(T, Fw, (BF - CHAP) / 2, 8.6, 0.55)
    entablature(T, Fw, -0.1, BF - CHAP + 0.1, 9.8, mat="stone", h=0.7, proj=0.4)
    # transept end: courses, pilasters, two entablatures, great window, oculus, door
    Fe = Frame(P(A_CR0, s * BF), UB, VB * s)
    L = A_CR1 - A_CR0
    courses(T, Fe, 0, L, 0, 21, 0.6)
    for u in (0.5, L - 0.5): pilaster(T, Fe, u, 1.0, 0, 11.8, 0.35)
    for u in (0.5, L - 0.5): pilaster(T, Fe, u, 0.9, 12.9, 20.2, 0.3)
    entablature(T, Fe, -0.2, L + 0.2, 11.8, mat="stone", h=1.1, proj=0.6); entablature(T, Fe, -0.2, L + 0.2, 20.2, mat="serena", h=1.0, proj=0.7)
    win_round(T, Fe, L / 2, 14.0, 19.4, 2.4, frame="serena")
    oculus(T, Fe, L / 2, 8.6, 1.1); door(T, Fe, L / 2, 1.8, 3.6, arch_mat="stone", gate=False, relieving=False)
    Fc = Frame(P(A_CR1, s * BF), -VB * s, UB)                                      # their east faces (towards the choir)
    for u in (2.0, 6.0, 10.0):
        if u < BF - AISLE - 1: blind_arch(T, Fc, u - 1.5, u + 1.5, 0, 7.0)
    entablature(T, Fc, 0, BF - NAVE_W, 20.2, mat="serena", h=1.0, proj=0.6)
# crossing tiburio: square block over the roofs with an arcaded loggia under a low hip roof (photographs; LiDAR ≈36.4 m)
CR = "crossing@1461-" + str(NOW)
c0 = P((A_CR0 + A_CR1) / 2, 0); HW = 6.4
box(bm_for(CR, "stone"), Frame(c0 - UB * HW - VB * HW, UB, VB), 0, 2 * HW, 21.0, 30.0, 0, 2 * HW)
box(bm_for(CR, "stone"), Frame(c0 - UB * (HW - 0.7) - VB * (HW - 0.7), UB, VB), 0, 2 * HW - 1.4, 30.0, 35.2, 0, 2 * HW - 1.4)
for (o, u, n) in ((c0 - UB * HW - VB * HW, UB, -VB), (c0 + UB * HW - VB * HW, VB, UB), (c0 + UB * HW + VB * HW, -UB, VB), (c0 - UB * HW + VB * HW, -VB, -UB)):
    F = Frame(o, u, n)
    courses(CR, F, 0, 2 * HW, 21.0, 30.0, 0.6)
    entablature(CR, F, -0.1, 2 * HW + 0.1, 29.4, mat="serena", h=0.8, proj=0.45)
    for k in range(4):                                                         # loggia: four arches a side on piers
        uc = 2 * HW / 4 * (k + 0.5)
        arch_fill(CR, "dark", F, uc - 1.05, uc + 1.05, 30.2, 33.4, n=-0.6)
        ring(CR, "serena", F, uc, 33.4, 1.05, 1.3, -0.6, 0.06, seg=10)
        box(bm_for(CR, "serena"), F, uc - 1.3, uc - 1.05, 30.2, 33.4, -0.6, 0.06); box(bm_for(CR, "serena"), F, uc + 1.05, uc + 1.3, 30.2, 33.4, -0.6, 0.06)
    for k in range(5): box(bm_for(CR, "stone"), F, 2 * HW / 4 * k - 0.3 + (0.3 if k == 0 else 0) - (0.3 if k == 4 else 0), 2 * HW / 4 * k + 0.3 + (0.3 if k == 0 else 0) - (0.3 if k == 4 else 0), 30.0, 34.6, -0.6, 0.06)
    entablature(CR, F, -0.2, 2 * HW + 0.2, 34.6, mat="serena", h=0.7, proj=0.6)
tip = c0 + Z * 36.6
crn = [c0 + UB * (x * (HW + 0.7)) + VB * (y * (HW + 0.7)) + Z * 35.3 for x, y in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
for i in range(4): poly(bm_for(CR, "roof"), [crn[i], crn[(i + 1) % 4], tip])
sphere(CR, "gold", tip + Z * 0.4, 0.3); cross(CR, tip + Z * 0.6, 1.2)

N = "nave@1461-" + str(NOW)
blk(N, "rubble", 0, A_CR0, -NAVE_W, NAVE_W, 0, 21.5)
gable_ab(N, 0, A_CR0, -NAVE_W, NAVE_W, 21.5, 27.6, end_mat="rubble")
for s in (-1, 1):
    blk(N, "rubble", 0, A_CR0, min(s * NAVE_W, s * AISLE), max(s * NAVE_W, s * AISLE), 0, 15.0)
    lean_ab(N, 0, A_CR0, s * AISLE, s * NAVE_W, 15.0, 17.6)
    blk(N, "stone", 0, A_CR0, min(s * AISLE, s * (CHAP - 0.6)), max(s * AISLE, s * (CHAP - 0.6)), 0, 10.5)
    lean_ab(N, 0, A_CR0, s * CHAP, s * AISLE, 10.5, 12.3)
    # chapel wall: a tall blind arch per chapel, recessed between piers with pilaster strips, cornice (photographs)
    Fc = Frame(P(0, s * CHAP), UB, VB * s)
    arcade_wall(N, Fc, A_CR0, NB, 9.8, depth=0.6)
    if s < 0: door(N, Frame(P(0, s * (CHAP - 0.6)), UB, VB * s), A_CR0 - BAY / 2, 1.6, 3.4, arch_mat="stone", gate=False, relieving=False)
    # aisle wall above the chapel roofs: brick band and an oculus per bay
    Fa = Frame(P(0, s * AISLE), UB, VB * s)
    pbox(bm_for(N, "brick"), Fa, 0, A_CR0, 12.4, 12.9, 0, 0.04)
    for i in range(NB): oculus(N, Fa, (i + 0.5) * BAY, 13.75, 0.45, fw=0.18)
    entablature(N, Fa, -0.1, A_CR0 + 0.1, 14.5, mat="serena", h=0.5, proj=0.35)
    # clerestory: round-headed windows under the pietra serena entablature, a brick band under them
    Fn = Frame(P(0, s * NAVE_W), UB, VB * s)
    pbox(bm_for(N, "brick"), Fn, 0, A_CR0, 17.7, 18.2, 0, 0.04)
    for i in range(NB): win_round(N, Fn, (i + 0.5) * BAY, 18.3, 20.45, 1.25)
    entablature(N, Fn, -0.1, A_CR0 + 0.1, 20.6, mat="serena", h=0.95, proj=0.6)
# the bare façade: rubble with the brick relieving arch, three portals, a window in the gable
FF = Frame(P(0, CHAP), -VB, -UB)                                          # u across from the south side, n outward (towards the piazza)
W = 2 * CHAP
def ftop(u):
    b = abs(u - CHAP)
    if b <= NAVE_W: return 21.5 + (27.6 - 21.5) * (1 - b / NAVE_W)
    if b <= AISLE: return 17.6
    return 17.6 - (17.6 - 11.6) * (b - AISLE) / (CHAP - AISLE)
box(bm_for(N, "rubble"), FF, 0, W, -1.5, 11.6, -0.6, 0.0)
for (a, b, t0, t1) in ((CHAP - AISLE, CHAP - NAVE_W, 11.6, 17.6), (CHAP + NAVE_W, CHAP + AISLE, 11.6, 17.6), (CHAP - NAVE_W, CHAP + NAVE_W, 11.6, 21.5)):
    box(bm_for(N, "rubble"), FF, a, b, t0, t1, -0.6, 0.0)
for (a, b, ta, tb) in ((0, CHAP - AISLE, 11.6, 17.6), (CHAP + AISLE, W, 17.6, 11.6)):
    poly(bm_for(N, "rubble"), [FF.p(a, 11.6, 0), FF.p(b, 11.6, 0), FF.p(b, tb, 0), FF.p(a, ta, 0)])
poly(bm_for(N, "rubble"), [FF.p(CHAP - NAVE_W, 21.5, 0), FF.p(CHAP + NAVE_W, 21.5, 0), FF.p(CHAP, 27.6, 0)])
HOLES = [(CHAP - 4.9, CHAP + 4.9, 16.6, 25.4), (CHAP - 0.7, CHAP + 0.7, 24.4, 26.1)]
for (u, w, h) in ((CHAP, 3.3, 6.6), (CHAP - 8.4, 2.6, 5.4), (CHAP + 8.4, 2.6, 5.4)):
    HOLES.append((u - w / 2 - 1.0, u + w / 2 + 1.0, -1.0, h + 2.4 + w / 2 + 0.8))
rubble(N, FF, 0, W, 0.0, ftop, seed=1461, holes=HOLES)
ring(N, "brick", FF, CHAP, 20.6, 4.1, 4.8, 0, 0.16, seg=16, soffit=False)                     # relieving arch with brick infill
arch_fill(N, "brick", FF, CHAP - 4.1, CHAP + 4.1, 17.4, 20.6, n=0.08)
win_rect(N, FF, CHAP, 24.6, 25.8, 0.8, frame="stone")
for (u, w, h) in ((CHAP, 3.3, 6.6), (CHAP - 8.4, 2.6, 5.4), (CHAP + 8.4, 2.6, 5.4)):
    door(N, FF, u, w, h)
    ring(N, "brick", FF, u, h + 1.6, w / 2 + 0.2, w / 2 + 0.75, 0, 0.12, seg=12, soffit=False)   # second, higher brick arch
# steps along the front and round the north corner (photographs)
for k in range(7):
    h = 0.2 * (7 - k); d = 0.42 * (k + 1)
    box(bm_for(N, "stone"), Frame(P(-d, -CHAP - d), UB, VB), 0, 0.42, -1.5, h, 0, W + d + 0.6)
    pbox(bm_for(N, "stone"), Frame(P(-d, -CHAP - d), UB, VB), 0, A_CR0 - 6.0 + d, -1.5, h, 0, 0.42)

# Old Sacristy (Brunelleschi 1421–28): square block with pilasters, cylindrical drum with oculi, conical tiled roof, lantern
OS = "old_sacristy@1428-" + str(NOW)
osc = Pxz(-132.9, -320.1)
box(bm_for(OS, "stone"), Frame(osc - UB * 6 - VB * 6, UB, VB), 0, 12, -1.5, 18.5, 0, 12)
for (o, u, n) in ((osc - UB * 6 + VB * 6, UB, VB), (osc + UB * 6 + VB * 6, -VB, UB), (osc - UB * 6 - VB * 6, VB, -UB)):
    F = Frame(o, u, n); courses(OS, F, 0, 12, 0, 18.5, 0.6)
    for uu in (0.5, 11.5): pilaster(OS, F, uu, 1.0, 0, 17.6, 0.45)
    entablature(OS, F, -0.2, 12.2, 17.6, mat="serena", h=0.9, proj=0.55)
    oculus(OS, F, 6, 13.6, 0.9)
cylinder(OS, "stone", osc, 5.0, 18.5, 22.2, seg=24)
for k in range(12):
    t = 2 * math.pi * k / 12; n = Vector((math.cos(t), math.sin(t), 0)); tt = Vector((-n.y, n.x, 0))
    oculus(OS, Frame(osc + n * 5.0, tt, n), 0, 20.3, 0.35, fw=0.14)
cylinder(OS, "serena", osc, 5.3, 22.2, 22.6, seg=24)
cone(OS, "tile", osc, 5.5, 1.1, 22.6, 25.6, seg=24)
column_lantern(OS, osc, 25.6, 0.95, 2.4, n=6)
box(bm_for(OS, "stone"), Frame(osc - UB * 2.5 + VB * 6, UB, VB), 0, 5, -1.5, 12.5, 0, 3.2)                  # scarsella

# cloister (Manetti 1457–60): arches on columns, trabeated upper loggia, ochre walls behind, garth with hedges and an orange tree
CL = "cloister@1460-" + str(NOW)
GX0, GX1, GZ0, GZ1 = -106.0, -79.0, -318.0, -292.0                  # garth (scene x/z)
OUT, GAL = 7.0, 4.0                                                   # depth of the ranges, of the galleries
GARTH = [(Frame(Pxz(GX0, GZ0), Vector((1, 0, 0)), Vector((0, -1, 0))), GX1 - GX0), (Frame(Pxz(GX1, GZ0), Vector((0, -1, 0)), Vector((-1, 0, 0))), GZ1 - GZ0),
         (Frame(Pxz(GX1, GZ1), Vector((-1, 0, 0)), Vector((0, 1, 0))), GX1 - GX0), (Frame(Pxz(GX0, GZ1), Vector((0, 1, 0)), Vector((1, 0, 0))), GZ1 - GZ0)]
I = [(GX0 + 0.6, -(GZ0 + 0.6)), (GX1 - 0.6, -(GZ0 + 0.6)), (GX1 - 0.6, -(GZ1 - 0.6)), (GX0 + 0.6, -(GZ1 - 0.6))]
Oo = [(GX0 - OUT - 0.4, -(GZ0 - OUT - 0.4)), (GX1 + OUT + 0.4, -(GZ0 - OUT - 0.4)), (GX1 + OUT + 0.4, -(GZ1 + OUT + 0.4)), (GX0 - OUT - 0.4, -(GZ1 + OUT + 0.4))]
Mr = [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b in zip(I, Oo)]
for i in range(4):
    j = (i + 1) % 4
    poly(bm_for(CL, "roof"), [(*I[i], 11.4), (*I[j], 11.4), (*Mr[j], 13.4), (*Mr[i], 13.4)])
    poly(bm_for(CL, "roof"), [(*Mr[i], 13.4), (*Mr[j], 13.4), (*Oo[j], 11.4), (*Oo[i], 11.4)])
for G, L in GARTH:
    n = 7; bay = L / n
    box(bm_for(CL, "ochre"), G, -OUT, L + OUT, -1.5, 11.6, -OUT, -GAL)                        # the range behind the gallery
    box(bm_for(CL, "plaster"), G, 0, L, 5.1, 6.6, -GAL, 0.0)                                   # gallery vault / upper floor, parapet
    box(bm_for(CL, "plaster"), G, 0, L, 10.6, 11.0, -GAL, 0.15)                                 # upper loggia ceiling
    Fb = Frame(G.o - G.n * GAL, G.u, G.n)                                                       # back wall of the gallery
    for k in range(n):
        uc = (k + 0.5) * bay
        if k % 2 == 0: win_rect(CL, Fb, uc, 0.0, 2.6, 1.1, frame="serena", fill="wood")
        else: win_rect(CL, Fb, uc, 1.2, 2.8, 1.0, frame="serena", grille=True)
        win_rect(CL, Fb, uc, 7.4, 9.0, 0.9, frame="serena", grille=True)
        r = bay / 2 - 0.3
        poly(bm_for(CL, "plaster"), [G.p(uc - bay / 2, 4.15, 0), G.p(uc - r, 4.15, 0)] +
             [G.p(uc - r * math.cos(math.pi * i / 10), 4.15 + r * math.sin(math.pi * i / 10), 0) for i in range(11)] +
             [G.p(uc + bay / 2, 4.15, 0), G.p(uc + bay / 2, 5.1, 0), G.p(uc - bay / 2, 5.1, 0)])         # spandrel
        ring(CL, "serena", G, uc, 4.15, r, r + 0.22, -0.5, 0.06, seg=10)
        if k % 2 == 0: oculus(CL, G, uc, 6.0, 0.35, fill="serena", frame="serena", fw=0.1)
    for k in range(n + 1):
        cylinder(CL, "serena", G.p(k * bay, 0, -0.25), 0.22, 0.0, 3.9, seg=10)                 # columns with impost blocks
        box(bm_for(CL, "serena"), G, k * bay - 0.32, k * bay + 0.32, 3.9, 4.15, -0.57, 0.07)
        cylinder(CL, "serena", G.p(k * bay, 0, -0.3), 0.15, 6.6, 10.6, seg=8)                   # upper loggia columns
    entablature(CL, G, -0.1, L + 0.1, 5.0, mat="serena", h=0.45, proj=0.25)
    box(bm_for(CL, "serena"), G, -0.1, L + 0.1, 10.6, 11.0, -0.5, 0.15)                         # architrave
    box(bm_for(CL, "wood"), G, -0.3, L + 0.3, 11.0, 11.5, -0.6, 0.7)                            # wooden eaves
poly(bm_for(CL, "lawn"), [Pxz(GX0, GZ0, 0.02), Pxz(GX1, GZ0, 0.02), Pxz(GX1, GZ1, 0.02), Pxz(GX0, GZ1, 0.02)])
cx_, cz_ = (GX0 + GX1) / 2, (GZ0 + GZ1) / 2
for (x0, x1, z0, z1) in ((GX0 + 1, GX1 - 1, GZ0 + 1, GZ0 + 1.6), (GX0 + 1, GX1 - 1, GZ1 - 1.6, GZ1 - 1), (GX0 + 1, GX0 + 1.6, GZ0 + 1, GZ1 - 1),
                         (GX1 - 1.6, GX1 - 1, GZ0 + 1, GZ1 - 1), (cx_ - 1.6, cx_ - 1.0, GZ0 + 1, GZ1 - 1), (cx_ + 1.0, cx_ + 1.6, GZ0 + 1, GZ1 - 1),
                         (GX0 + 1, GX1 - 1, cz_ - 1.6, cz_ - 1.0), (GX0 + 1, GX1 - 1, cz_ + 1.0, cz_ + 1.6)):
    wbox(bm_for(CL, "hedge"), x0, x1, -z1, -z0, 0, 0.75)
tc = Pxz(cx_, cz_)
cylinder(CL, "wood", tc, 0.22, 0, 2.6, seg=8); sphere(CL, "hedge", tc + Z * 4.3, 2.6)

# the rest of the canons' block south and east of the cloister (OSM relation 4101358): ranges with windows
REL = [(-126.2, -295.3), (-120.7, -320.4), (-108.8, -317.8), (-106.8, -326.9), (-99.8, -325.4), (-72.3, -319.2), (-75.4, -305.5),
       (-62.7, -302.6), (-67.8, -278.3), (-70.8, -265.0), (-72.1, -258.7), (-73.5, -252.1), (-78.3, -253.2), (-81.1, -253.9),
       (-81.8, -251.0), (-88.2, -251.8), (-88.5, -246.1), (-96.2, -247.5), (-122.8, -252.6), (-122.5, -254.3), (-122.1, -256.1),
       (-124.8, -257.0), (-126.9, -257.8), (-132.5, -266.5), (-129.5, -280.8), (-128.8, -284.0)]
def clip(poly_, keep, cut):
    out = []
    for i in range(len(poly_)):
        a, b = poly_[i - 1], poly_[i]; ka, kb = keep(a), keep(b)
        if kb:
            if not ka: out.append(cut(a, b))
            out.append(b)
        elif ka: out.append(cut(a, b))
    return out
def extrude(part, pts, z0, z1, mat="ochre", top="roof", floors=(1.6, 5.4, 8.8)):
    """Plain range on an outline: walls, flat-pitched roof, eaves cornice and windows on every side longer than 6 m."""
    bm = bm_for(part, mat); lo = [bm.verts.new((x, -z, z0)) for x, z in pts]; hi = [bm.verts.new((x, -z, z1)) for x, z in pts]
    for i in range(len(pts)):
        j = (i + 1) % len(pts); bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    poly(bm_for(part, top), [(x, -z, z1 + 0.6) for x, z in pts])
    sgn = 1.0
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    if area > 0: sgn = -1.0
    for i in range(len(pts)):
        a, b = Vector((pts[i][0], -pts[i][1], 0)), Vector((pts[(i + 1) % len(pts)][0], -pts[(i + 1) % len(pts)][1], 0))
        L = (b - a).length
        if L < 6: continue
        u = (b - a) / L; n = Vector((u.y, -u.x, 0)) * sgn
        F = Frame(a, u, n)
        pbox(bm_for(part, "stone"), F, 0, L, z1 - 0.5, z1 + 0.15, 0, 0.5)
        m = int(L / 3.2)
        for k in range(m):
            uc = (k + 0.5) * L / m
            for v in floors: win_rect(part, F, uc, v, v + 1.7, 0.9, frame="stone", grille=(v < 3))
cut_s = lambda a, b: (a[0] + (b[0] - a[0]) * (-285.0 - a[1]) / (b[1] - a[1]), -285.0)
extrude(CL, clip(REL, lambda q: q[1] >= -285.0, cut_s), -1.5, 12.0)
extrude(CL, [(-75.4, -305.5), (-62.7, -302.6), (-67.0, -285.0), (-72.0, -285.0)], -1.5, 12.0)

# Laurentian Library (Michelangelo, from 1524; opened 1571) over the west range, with the tall vestibule (ricetto)
LB = "library@1571-" + str(NOW)
wbox(bm_for(LB, "ochre"), -134, -121, 262, 318, -1.5, 20.0)
poly(bm_for(LB, "roof"), [(-134.5, 261.5, 19.8), (-134.5, 318.5, 19.8), (-127.5, 318.5, 21.6), (-127.5, 261.5, 21.6)])
poly(bm_for(LB, "roof"), [(-120.5, 318.5, 19.8), (-120.5, 261.5, 19.8), (-127.5, 261.5, 21.6), (-127.5, 318.5, 21.6)])
poly(bm_for(LB, "ochre"), [(-134, 262, 20.0), (-121, 262, 20.0), (-127.5, 262, 21.6)])
wbox(bm_for(LB, "ochre"), -136, -121, 304, 318, -1.5, 22.5)
gable_roof(LB, -136.4, -120.6, 303.6, 318.4, 22.5, 24.6)
poly(bm_for(LB, "ochre"), [(-136, 304, 22.5), (-136, 318, 22.5), (-136, 311, 24.6)]); poly(bm_for(LB, "ochre"), [(-121, 318, 22.5), (-121, 304, 22.5), (-121, 311, 24.6)])
for side, xw in ((-1, -134), (1, -121)):
    F = Frame(Pxz(xw, -262), Vector((0, 1, 0)), Vector((side, 0, 0)))
    pbox(bm_for(LB, "serena"), F, 0, 42, 12.6, 12.9, 0, 0.25)                                    # string course at the reading-room floor
    for i in range(14):
        u = 1.6 + i * 3.0
        win_rect(LB, F, u, 14.2, 17.4, 1.05, frame="serena", pediment="cornice")              # reading-room windows
        win_rect(LB, F, u, 18.2, 19.2, 0.8, frame="serena")                                    # mezzanine lights
    entablature(LB, F, -0.2, 56.2, 19.4, mat="serena", h=0.6, proj=0.4)
Fr = Frame(Pxz(-136, -318), Vector((0, 1, 0)), Vector((-1, 0, 0)))
for u in (3.0, 7.0, 11.0): win_rect(LB, Fr, u, 15.0, 19.6, 1.3, frame="serena", pediment="cornice")

# New Sacristy (Michelangelo c. 1521–34; dome 1524, inferred): ashlar block, cylindrical drum, tiled dome, columned lantern
NS = "new_sacristy@1524-" + str(NOW)
nsc = Pxz(-120.4, -374.5)
box(bm_for(NS, "stone"), Frame(nsc - UB * 6.5 - VB * 6.5, UB, VB), 0, 13, -1.5, 22.0, 0, 13)
for (o, u, n) in ((nsc - UB * 6.5 - VB * 6.5, UB, -VB), (nsc + UB * 6.5 - VB * 6.5, VB, UB), (nsc - UB * 6.5 + VB * 6.5, -VB, -UB)):
    F = Frame(o, u, n); courses(NS, F, 0, 13, 0, 22, 0.6)
    for uu in (0.6, 12.4): pilaster(NS, F, uu, 1.1, 0, 21.0, 0.45)
    entablature(NS, F, -0.2, 13.2, 21.0, mat="serena", h=1.0, proj=0.6)
    entablature(NS, F, -0.2, 13.2, 11.6, mat="stone", h=0.9, proj=0.5)
    win_round(NS, F, 6.5, 13.4, 19.4, 2.6, frame="serena", fw=0.3)
    oculus(NS, F, 6.5, 8.4, 1.0)
    if u == UB: door(NS, F, 6.5, 1.8, 3.6, arch_mat="stone", gate=False, relieving=False)
    else: win_rect(NS, F, 6.5, 3.0, 5.4, 1.2, frame="serena", grille=True)
cylinder(NS, "stone", nsc, 5.6, 22.0, 26.0, seg=28)
for k in range(8):
    t = 2 * math.pi * k / 8; n = Vector((math.cos(t), math.sin(t), 0)); tt = Vector((-n.y, n.x, 0))
    win_rect(NS, Frame(nsc + n * 5.6, tt, n), 0, 23.0, 25.0, 0.9, frame="serena")
cylinder(NS, "serena", nsc, 5.95, 26.0, 26.5, seg=28)
top = dome(NS, nsc, 5.9, 26.5, 4.6, ribs=8, mat="tile")
column_lantern(NS, nsc, top - 0.2, 1.25, 3.4, n=8)

# Cappella dei Principi (begun 1604 by Nigetti; dome 1640 per en.wikipedia, 1743 elsewhere)
cpc = P(101.8, 1.2)
ROT = math.atan2(UB.y, UB.x)
CW = "principi@1604-" + str(NOW)
octagon_prism(CW, "stone", cpc, 19.0, -1.5, 24.6, rot=ROT)
for F, w, k in oct_faces(cpc, 19.0, rot=ROT):
    if k == 4: continue                                                            # the face against the choir
    courses(CW, F, 0, w, 0, 23.0, 0.65)
    for uu in (0.6, w - 0.6): pbox(bm_for(CW, "white"), F, uu - 0.6, uu + 0.6, 0.6, 23.0, 0, 0.22)      # white marble pilaster panels
    pbox(bm_for(CW, "stone"), F, -0.2, w + 0.2, -1.5, 0.9, 0, 0.35)                                    # plinth
    entablature(CW, F, -0.3, w + 0.3, 23.0, mat="stone", h=1.6, proj=0.9)
    if k % 2 == 1:                                                                 # diagonal faces: half-domed niche (nicchione)
        nc = F.p(w / 2, 0, 0)
        cylinder(CW, "stone", nc, 4.6, -1.5, 15.0, seg=16)
        dome(CW, nc, 4.7, 15.0, 3.0, ribs=0, mat="lead", seg=16)
        win_rect(CW, Frame(nc + F.n * 4.6 - F.u * 0.9, F.u, F.n), 0.9, 5.0, 10.6, 1.4, frame="white", pediment="cornice")
        pbox(bm_for(CW, "white"), Frame(nc + F.n * 4.6 - F.u * 2.2, F.u, F.n), 0, 4.4, 11.8, 13.4, 0, 0.12)
    else:                                                                          # main faces: tall framed window, a panel over it, crypt light
        win_rect(CW, F, w / 2, 5.0, 13.2, 3.0, frame="white", fw=0.45, pediment="cornice")
        pbox(bm_for(CW, "white"), F, w / 2 - 2.2, w / 2 + 2.2, 15.0, 21.2, 0, 0.1)
        pbox(bm_for(CW, "stone"), F, w / 2 - 1.9, w / 2 + 1.9, 15.3, 20.9, 0, 0.14)
        win_rect(CW, F, w / 2, 1.2, 3.6, 1.6, frame="white", grille=True)
CD = "principi_dome@1640-" + str(NOW)
octagon_prism(CD, "stone", cpc, 15.6, 24.6, 33.6, rot=ROT)
for F, w, k in oct_faces(cpc, 15.6, rot=ROT):
    courses(CD, F, 0, w, 24.6, 33.6, 0.65)
    for uu in (0.7, w - 0.7): pilaster(CD, F, uu, 1.1, 24.6, 32.6, 0.4, mat="white", base=False)
    r = 1.7; uc = w / 2                                                            # great drum window in a scrolled white marble frame
    arch_fill(CD, "dark", F, uc - r, uc + r, 26.4, 30.0, n=0.05)
    ring(CD, "white", F, uc, 30.0, r, r + 0.5, 0, 0.18, seg=12)
    pbox(bm_for(CD, "white"), F, uc - r - 0.5, uc - r, 26.0, 30.0, 0, 0.18); pbox(bm_for(CD, "white"), F, uc + r, uc + r + 0.5, 26.0, 30.0, 0, 0.18)
    pbox(bm_for(CD, "white"), F, uc - r - 0.8, uc + r + 0.8, 25.6, 26.1, 0, 0.3)
    for ss in (-1, 1): sphere(CD, "white", F.p(uc + ss * (r + 0.6), 26.3, 0.25), 0.32)          # the scrolls
    pbox(bm_for(CD, "white"), F, uc - 0.3, uc + 0.3, 31.6, 32.4, 0, 0.3)                            # keystone
    entablature(CD, F, -0.3, w + 0.3, 32.6, mat="white", h=1.0, proj=0.7)
top = dome(CD, cpc, 15.4, 33.6, 21.2, ribs=8, mat="tile", rot=ROT + math.pi / 8)
column_lantern(CD, cpc, top - 0.5, 2.4, 7.6, n=8)

# bell tower (Ferdinando Ruggieri, 1740): ashlar shaft with cornices, belfry with balustrade, upper stage, cupola, ball and cross
BT = "campanile@1740-" + str(NOW)
btc = Pxz(-137.2, -357.0); S2 = 2.3
box(bm_for(BT, "stone"), Frame(btc - UB * S2 - VB * S2, UB, VB), 0, 2 * S2, -1.5, 41.0, 0, 2 * S2)
box(bm_for(BT, "stone"), Frame(btc - UB * 1.8 - VB * 1.8, UB, VB), 0, 3.6, 41.0, 45.5, 0, 3.6)
for (o, u, n) in ((btc - UB * S2 - VB * S2, UB, -VB), (btc + UB * S2 - VB * S2, VB, UB), (btc + UB * S2 + VB * S2, -UB, VB), (btc - UB * S2 + VB * S2, -VB, -UB)):
    F = Frame(o, u, n); courses(BT, F, 0, 2 * S2, 0, 34.0, 0.6)
    for v in (22.0, 33.0): entablature(BT, F, -0.1, 2 * S2 + 0.1, v, mat="stone", h=0.7, proj=0.35)
    arch_fill(BT, "dark", F, S2 - 1.0, S2 + 1.0, 34.6, 38.2, n=0.04)                                      # belfry opening
    ring(BT, "stone", F, S2, 38.2, 1.0, 1.35, 0, 0.15, seg=10)
    for kk in range(7): cylinder(BT, "stone", F.p(S2 - 0.9 + kk * 0.3, 0, 0.25), 0.07, 34.2, 35.0, seg=6)   # balustrade
    pbox(bm_for(BT, "stone"), F, S2 - 1.1, S2 + 1.1, 35.0, 35.15, 0, 0.35)
    entablature(BT, F, -0.2, 2 * S2 + 0.2, 40.0, mat="stone", h=1.0, proj=0.5)
    win_round(BT, Frame(btc + (o - btc) * (1.8 / S2), u, n), 1.8, 42.0, 44.4, 1.0, frame="stone")
cone(BT, "lead", btc, 2.1, 0.5, 45.5, 48.3, seg=12)
sphere(BT, "gold", btc + Z * 48.8, 0.35); cross(BT, btc + Z * 49.0, 1.6)

K.export("san_lorenzo")
