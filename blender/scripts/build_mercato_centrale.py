"""Mercato Centrale (Mercato di San Lorenzo) – dated model (v1).

Run:  python pipeline/43_centro.py   (once: outline, ground, LiDAR → blender/data/centro.json)
      blender -b --python blender/scripts/build_mercato_centrale.py  →  web/public/models/landmarks/mercato_centrale.glb
Frame: absolute scene coordinates (Blender X = scene x, Blender Y = −scene z, Z = scene y); placed at [0, 0], rot 0, ground 0.
Measured: OSM way 480015428 – 82.7 × 70.3 m, long sides along Via dell'Ariento and Via Sant'Antonino; the street slopes by
≈2.7 m round the building (app terrain 4.2–7.0 m); OSM height 14.5 m (the side halls), LiDAR roof median ≈19.4 m over the
floor (the central hall).
Details from photographs (docs/materials): a tall ground storey in rusticated stone, round arches on piers with a
panelled base, green louvred shutters and red iron fans in the arch heads, a heavy cornice and a low attic hiding the side
roofs; above it the central hall of red cast iron and glass on deep eaves, gabled on the short ends, with a walkway and
railing along the top. Bay counts (10 on the long sides, 8 on the short ones), storey heights and the hall width are
*inferred*.
Dates (docs/landmarks/MERCATO-CENTRALE.md): Giuseppe Mengoni, built 1870–74, opened 1874; the mezzanine floor 1979 and the
food hall 2014 are inside and not shown. Before 1874 the city data's block (record 9177, dated 1320 there) stands in.
"""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from mathutils import Vector
from landmark_detail import *
K.reset()
MAT["stone"] = material("pietra_forte", "pietra_forte", (0.62, 0.5, 0.36), 0.85, 0.32, tint=(3.0, 2.85, 2.55))
MAT["serena"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)
MAT["iron"] = material("cast_iron_painted", None, (0.16, 0.19, 0.18), 0.55, metal=0.5)
MAT["glazing"] = material("market_glazing", None, (0.3, 0.38, 0.36), 0.12, metal=0.2)
MAT["shutter"] = material("louvres_green", None, (0.13, 0.3, 0.2), 0.7)
MAT["red"] = material("iron_red", None, (0.5, 0.1, 0.12), 0.5, metal=0.4)
MAT["lead"] = material("roof_green", None, (0.24, 0.4, 0.3), 0.6, metal=0.2)
NOW = K.NOW
D = json.load(open(os.path.join(ROOT, "blender", "data", "centro.json"), encoding="utf-8"))["mercato"]
G = max(D["ground"]) + 0.05                  # floor level; the plinth goes down to the lowest street
G0 = min(D["ground"]) - 0.5
FROM = 1874
M = f"mercato@{FROM}-{NOW}"
O = Vector((-226.18, 541.61, 0))             # west corner (Blender coordinates)
def vb(x, z): return Vector((x, -z, 0))
A = (vb(-178.44, -474.12) - O).normalized(); LA = (vb(-178.44, -474.12) - O).length      # long axis
Bv = (vb(-168.66, -582.0) - O).normalized(); LB = (vb(-168.66, -582.0) - O).length        # short axis
Z = Vector((0, 0, 1))
def Q(a, b, h=0.0): return O + A * a + Bv * b + Z * h
GF = G + 12.6                                # top of the stone storey (cornice), a low attic above it
SIDE_LOW, SIDE_HIGH, CLER, RIDGE = GF + 0.9, GF + 2.6, G + 21.0, G + 24.6
B1, B2 = LB * 0.3, LB * 0.7                  # the central nave

# the four fronts: frame with u along the side and n outwards
CEN = Q(LA / 2, LB / 2)
def side_frame(p0, p1):
    u = (p1 - p0).normalized(); n = Vector((u.y, -u.x, 0))
    if (p0 - CEN).dot(n) < 0: n = -n
    return Frame(p0, u, n), (p1 - p0).length
SIDES = [(Q(0, 0), Q(LA, 0), 10), (Q(LA, 0), Q(LA, LB), 8), (Q(LA, LB), Q(0, LB), 10), (Q(0, LB), Q(0, 0), 8)]

def stone_storey():
    for p0, p1, nb in SIDES:
        F, L = side_frame(p0, p1); w = L / nb
        box(bm_for(M, "stone"), F, 0, L, G0, G + 0.4, -0.8, 0.4)                                   # plinth over the slope
        for k in range(nb):
            u0, u1 = k * w, (k + 1) * w; uc = (u0 + u1) / 2
            pw = 1.6 if k in (0, nb - 1) else 1.1
            r = w / 2 - pw / 2 - 0.5; spring = GF - 2.4 - r; SILL = G + 2.2
            for (a, b) in ((u0, u0 + pw / 2), (u1 - pw / 2, u1)):
                box(bm_for(M, "stone"), F, a, b, G + 0.4, GF, -0.8, 0)
            voussoirs(M, "stone", F, uc, spring, r, r + 0.9, n=13, proud=0.22)
            box(bm_for(M, "stone"), F, uc - r - 0.5, uc + r + 0.5, G + 0.4, SILL, -0.8, -0.2)          # panelled base under the arch
            for (a, b) in ((uc - r - 0.5, uc - r), (uc + r, uc + r + 0.5)): box(bm_for(M, "stone"), F, a, b, SILL, GF, -0.8, 0)
            poly(bm_for(M, "shutter"), [F.p(uc - r, SILL, -0.4), F.p(uc + r, SILL, -0.4), F.p(uc + r, spring, -0.4), F.p(uc - r, spring, -0.4)])
            for q in range(int((spring - SILL) / 0.35)):                                                  # louvres
                v = SILL + 0.2 + q * 0.35; pbox(bm_for(M, "shutter"), F, uc - r, uc + r, v, v + 0.06, -0.4, -0.3)
            arch_fill(M, "red", F, uc - r, uc + r, spring, spring, n=-0.42)                               # the iron fan in the arch head
            for q in range(1, 8):
                t = math.pi * q / 8
                pbox(bm_for(M, "red"), F, uc + (r - 0.1) * math.cos(t) - 0.05, uc + (r - 0.1) * math.cos(t) + 0.05, spring, spring + (r - 0.1) * math.sin(t), -0.4, -0.34)
            bm = bm_for(M, "stone")                                                                  # spandrels up to the cornice
            seg = 10
            for s_ in (-1, 1):
                pts = [F.p(uc + s_ * r * math.cos(math.pi / 2 * i / seg), spring + r * math.sin(math.pi / 2 * i / seg), 0) for i in range(seg + 1)]
                corner = F.p(uc + s_ * r, GF, 0)
                for i in range(seg): poly(bm, [pts[i], pts[i + 1], corner] if s_ > 0 else [pts[i + 1], pts[i], corner])
            pbox(bm_for(M, "stone"), F, uc - r, uc + r, spring + r, GF, -0.8, 0)
        entablature(M, F, 0, L, GF - 1.1, mat="stone", h=1.1, proj=0.7)
        box(bm_for(M, "stone"), F, 0, L, GF, GF + 1.2, -0.6, 0.1)                                          # attic hiding the side roofs
stone_storey()

# the iron halls
H = f"mercato_padiglioni@{FROM}-{NOW}"
def glazed_wall(Fr, u0, u1, v0, v1, step=1.6, frame="iron"):
    poly(bm_for(H, "glazing"), [Fr.p(u0, v0), Fr.p(u1, v0), Fr.p(u1, v1), Fr.p(u0, v1)])
    u = u0
    while u <= u1 + 0.01:
        pbox(bm_for(H, frame), Fr, u - 0.07, u + 0.07, v0, v1, 0, 0.12); u += step
    for v in (v0, (v0 + v1) / 2, v1): pbox(bm_for(H, frame), Fr, u0, u1, v - 0.08, v + 0.08, 0, 0.14)
def roof(p, mat="lead"):
    poly(bm_for(H, mat), p)
# side naves: a glazed band over the stone storey, then a lean-to up to the central nave
for (b0, b1, outer) in ((0.0, B1, 0.0), (B2, LB, LB)):
    inner = B1 if outer == 0.0 else B2
    for a in (0.0, LA):                                                                           # glazed band on the ends
        F, _ = side_frame(Q(a, b0), Q(a, b1))
        glazed_wall(F, 0, b1 - b0, GF, SIDE_LOW)
    F, L = side_frame(Q(0, outer), Q(LA, outer)); glazed_wall(F, 0, L, GF, SIDE_LOW)
    roof([Q(0, outer, SIDE_LOW), Q(LA, outer, SIDE_LOW), Q(LA, inner, SIDE_HIGH), Q(0, inner, SIDE_HIGH)])
    for a in (0.0, LA):                                                                           # the lean-to's triangular end
        roof([Q(a, outer, SIDE_LOW), Q(a, inner, SIDE_LOW), Q(a, inner, SIDE_HIGH)], "glazing")
# central nave: red cast-iron and glass walls, a roof on deep eaves with a flat walkway along the top
for b in (B1, B2):
    F, L = side_frame(Q(0, b), Q(LA, b)); glazed_wall(F, 0, L, SIDE_HIGH, CLER, step=LA / 20, frame="red")
    for k in range(21): pbox(bm_for(H, "red"), F, k * LA / 20 - 0.2, k * LA / 20 + 0.2, SIDE_HIGH, CLER, 0, 0.35)   # piers
bm_ = (B1 + B2) / 2; flat = 2.0; ov = 1.6
for (b, bo, bs) in ((B1, B1 - ov, bm_ - flat), (B2, B2 + ov, bm_ + flat)):
    roof([Q(-ov, bo, CLER - 0.3), Q(LA + ov, bo, CLER - 0.3), Q(LA + ov, bs, RIDGE), Q(-ov, bs, RIDGE)])
roof([Q(-ov, bm_ - flat, RIDGE), Q(LA + ov, bm_ - flat, RIDGE), Q(LA + ov, bm_ + flat, RIDGE), Q(-ov, bm_ + flat, RIDGE)])
for bb in (bm_ - flat, bm_ + flat):                                                               # railing along the walkway
    for k in range(int(LA / 1.5) + 1):
        p = Q(k * LA / int(LA / 1.5), bb, RIDGE); poly(bm_for(H, "iron"), [p, p + A * 0.05, p + A * 0.05 + Z, p + Z])
    poly(bm_for(H, "iron"), [Q(0, bb, RIDGE + 0.95), Q(LA, bb, RIDGE + 0.95), Q(LA, bb, RIDGE + 1.05), Q(0, bb, RIDGE + 1.05)])
for k in range(int(LA / 4.0) + 1):                                                               # iron ribs over the side roofs
    a = k * LA / int(LA / 4.0)
    for (b0, h0, b1, h1) in ((0, SIDE_LOW, B1, SIDE_HIGH), (LB, SIDE_LOW, B2, SIDE_HIGH)):
        p0, p1 = Q(a, b0, h0 + 0.05), Q(a, b1, h1 + 0.05); sv = A * 0.08
        poly(bm_for(H, "iron"), [p0 - sv, p0 + sv, p1 + sv, p1 - sv])
# the gable ends: glazed, framed in red iron
for a in (0.0, LA):
    F, _ = side_frame(Q(a, B1), Q(a, B2)); W = B2 - B1
    glazed_wall(F, 0, W, SIDE_HIGH, CLER, step=W / 8, frame="red")
    rise = RIDGE - CLER; run = W / 2 - flat
    poly(bm_for(H, "glazing"), [F.p(0, CLER), F.p(W, CLER), F.p(W - run, RIDGE), F.p(run, RIDGE)])
    for k in range(1, 8):
        u = W * k / 8; top = CLER + rise * min(1.0, min(u, W - u) / run)
        pbox(bm_for(H, "red"), F, u - 0.08, u + 0.08, CLER, top, 0, 0.12)
    for (u0, u1) in ((0, run), (W, W - run)):                                                    # raking frames
        p0, p1 = F.p(u0, CLER, 0.15), F.p(u1, RIDGE, 0.15); d = Vector((0, 0, 0.18))
        poly(bm_for(H, "red"), [p0 - d, p1 - d, p1 + d, p0 + d])
    pbox(bm_for(H, "red"), F, 0, W, CLER - 0.2, CLER + 0.2, 0, 0.3)
K.export("mercato_centrale")
