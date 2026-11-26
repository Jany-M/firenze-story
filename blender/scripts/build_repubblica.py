"""Piazza della Repubblica – the Palazzo dell'Arcone block on the west side of the square (v1).

Run:  python pipeline/43_centro.py   (once: outline, ground, LiDAR → blender/data/centro.json)
      blender -b --python blender/scripts/build_repubblica.py  →  web/public/models/landmarks/repubblica.glb
Frame: absolute scene coordinates (Blender X = scene x, Blender Y = −scene z, Z = scene y); placed at [0, 0], rot 0, ground 0.
Measured: OSM relation 1593627 – the whole block between the square, Via Pellicceria, Via de' Brunelleschi and Via degli
Anselmi, 113 m along the square; Via degli Strozzi passes under it between z 32 and 43 (11 m); LiDAR eaves ≈26.4 m above
the street (DSM median 35.1 m scene, ground 8.7 m), roofs to ≈28.5 m.
Details from photographs (docs/materials): an arcaded portico along the whole square front; three storeys of pedimented
windows over it; in the middle the central body with the great arch over Via degli Strozzi, giant paired columns, the
entablature, the attic with the inscription in real letters (Blender's default font, not the carved face) and four statues of the arts; until 1904 the group of Italy with Art and
Science on top. Storey heights, bay width (4.6 m), the portico depth (5.2 m) and the column order are *inferred*.
Dates (docs/landmarks/REPUBBLICA.md): square laid out from 1885 on the ground of the Mercato Vecchio and the Ghetto; the
Arcone building by Vincenzo Micheli, begun 1895 (the city data dates the block 1890 – conflict noted); crowning group
removed 1904; Piacentini's 1931 plan to pull the arch down never carried out.
"""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from mathutils import Vector
from landmark_detail import *
from landmark_text import lettering
K.reset()
MAT["plaster"] = material("plaster_ochre", None, (0.78, 0.64, 0.4), 0.9)
MAT["serena"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)
MAT["dress"] = material("artificial_stone", None, (0.8, 0.71, 0.5), 0.8)
MAT["letters"] = material("inscription_letters", None, (0.12, 0.11, 0.1), 0.7)
MAT["marble"] = material("marble_white", None, (0.9, 0.89, 0.86), 0.5)
MAT["panel"] = material("inscription_panel", None, (0.9, 0.89, 0.86), 0.5)
NOW = K.NOW
D = json.load(open(os.path.join(ROOT, "blender", "data", "centro.json"), encoding="utf-8"))["arcone"]
P = [tuple(p) for p in (D["pts"][:-1] if D["pts"][0] == D["pts"][-1] else D["pts"])]
G = max(D["ground"]) + 0.05
EAVE = G + 25.2
FROM = 1895
B = f"arcone@{FROM}-{NOW}"
def V(x, z, h=0.0): return Vector((x, -z, h))

# ---- the block as prisms, with the portico and the Via degli Strozzi passage cut out ----
def clip(poly_, keep):
    """Sutherland–Hodgman against one half-plane; keep(p) -> signed value, >= 0 kept."""
    out = []
    for i in range(len(poly_)):
        a, b = poly_[i - 1], poly_[i]; fa, fb = keep(a), keep(b)
        if fb >= 0:
            if fa < 0: t = fa / (fa - fb); out.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
            out.append(b)
        elif fa >= 0: t = fa / (fa - fb); out.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    ded = []
    for p in out:
        if not ded or math.dist(p, ded[-1]) > 0.05: ded.append(p)
    if len(ded) > 2 and math.dist(ded[0], ded[-1]) < 0.05: ded.pop()
    return ded
def area(Q): return sum(Q[i - 1][0] * Q[i][1] - Q[i][0] * Q[i - 1][1] for i in range(len(Q))) / 2
def prism(part, Q, z0, z1, wall="plaster", top="roof", bottom=True):
    if len(Q) < 3: return
    if area(Q) < 0: Q = Q[::-1]
    bw, bt = bm_for(part, wall), bm_for(part, top)
    for a, b in zip(Q, Q[1:] + Q[:1]): poly(bw, [V(*a, z0), V(*b, z0), V(*b, z1), V(*a, z1)])
    poly(bt, [V(*p, z1) for p in Q[::-1]])
    if bottom: poly(bw, [V(*p, z0) for p in Q])
Z_N, Z_S = 32.0, 43.0                       # the passage (Via degli Strozzi)
X_PORT = -137.0                             # back wall of the portico
SOUTH, NORTH = clip(P, lambda p: Z_N - p[1]), clip(P, lambda p: p[1] - Z_S)
PORT_TOP, ARCH_SPRING, ARCH_R = G + 7.8, G + 13.5, (Z_S - Z_N) / 2
CROWN = ARCH_SPRING + ARCH_R
for Q in (SOUTH, NORTH):
    prism(B, clip(Q, lambda p: X_PORT - p[0]), G - 1.0, PORT_TOP)
    prism(B, Q, PORT_TOP, CROWN, top="plaster")
prism(B, P, CROWN, EAVE, bottom=True)

# ---- the square front ----
A0, A1 = (-132.4, -17.9), (-131.2, 94.9)
L = math.dist(A0, A1); tu = ((A1[0] - A0[0]) / L, (A1[1] - A0[1]) / L)
F = Frame(V(*A0), Vector((tu[0], -tu[1], 0)), Vector((1, 0, 0)))
UC = ((Z_N + Z_S) / 2 - A0[1]) / tu[1]                    # the arch's axis along the front
HALF = 10.0                                               # the central body: 20 m wide
BAY = 4.6
def spandrel(part, mat, Fr, uc, spring, r, top, n):
    """Fill between a semicircular arch and its rectangle [uc−r, uc+r] × [spring, top] on the face n."""
    bm = bm_for(part, mat); seg = 10
    for side in (-1, 1):
        pts = [Fr.p(uc + side * r * math.cos(math.pi / 2 * k / seg), spring + r * math.sin(math.pi / 2 * k / seg), n) for k in range(seg + 1)]
        corner = Fr.p(uc + side * r, top, n)
        for k in range(seg): poly(bm, [pts[k], pts[k + 1], corner] if side > 0 else [pts[k + 1], pts[k], corner])
        poly(bm, [Fr.p(uc + side * r, spring, n), pts[0], corner] if side < 0 else [pts[0], Fr.p(uc + side * r, spring, n), corner])
def bays(u0, u1):
    n = max(1, round((u1 - u0) / BAY)); w = (u1 - u0) / n
    return [u0 + (k + 0.5) * w for k in range(n)], w
def side_body(u0, u1):
    cs, w = bays(u0, u1); r = w / 2 - 0.65; spring = PORT_TOP - 0.6 - r
    for uc in cs:
        for s_ in (-1, 1):
            pbox(bm_for(B, "dress"), F, uc + s_ * (w / 2) - 0.65, uc + s_ * (w / 2) + 0.65, G - 0.5, spring, -0.6, 0.15)     # piers
        spandrel(B, "plaster", F, uc, spring, r, PORT_TOP, 0.0)
        ring(B, "dress", F, uc, spring, r, r + 0.35, 0, 0.15, seg=12, soffit=True)
        for v0, h, ped in ((G + 9.4, 3.1, "cornice"), (G + 14.6, 2.8, "cornice"), (G + 19.8, 2.5, None)):
            win_rect(B, F, uc, v0, v0 + h, 1.3, frame="dress", fill="dark", fw=0.2, pediment=ped)
    pbox(bm_for(B, "dress"), F, u0, u1, PORT_TOP - 0.6, PORT_TOP + 0.2, 0, 0.3)
    for v in (G + 13.9, G + 19.1): pbox(bm_for(B, "dress"), F, u0, u1, v - 0.25, v, 0, 0.2)
    entablature(B, F, u0, u1, EAVE - 1.4, mat="dress", h=1.4, proj=0.9)
    for u in (u0, u1): pbox(bm_for(B, "dress"), F, u - 0.5, u + 0.5, PORT_TOP + 0.2, EAVE - 1.4, 0, 0.12)                   # quoins
side_body(0.0, UC - HALF)
side_body(UC + HALF, L)

# ---- the central body and the arch ----
P1 = 0.8                                                   # how far the central body stands out
bm = bm_for(B, "plaster")
for (a, b) in ((UC - HALF, UC - ARCH_R), (UC + ARCH_R, UC + HALF)):
    box(bm, F, a, b, G - 0.5, G + 21.5, -0.6, P1)
box(bm, F, UC - ARCH_R, UC + ARCH_R, CROWN, G + 21.5, -0.6, P1)
spandrel(B, "plaster", F, UC, ARCH_SPRING, ARCH_R, CROWN, P1)
voussoirs(B, "dress", F, UC, ARCH_SPRING, ARCH_R, ARCH_R + 1.1, n=19, proud=P1 + 0.25)
ring(B, "dress", F, UC, ARCH_SPRING, ARCH_R - 0.01, ARCH_R + 0.01, -0.6, P1, seg=18, soffit=True)
for s_ in (-1, 1):                                       # imposts
    pbox(bm_for(B, "dress"), F, UC + s_ * ARCH_R - 0.6, UC + s_ * ARCH_R + 0.6, ARCH_SPRING - 0.6, ARCH_SPRING, P1, P1 + 0.35)
# giant paired columns on pedestals
COLS = [UC + s_ * d for s_ in (-1, 1) for d in (ARCH_R + 1.0, HALF - 1.0)]
for u in COLS:
    pbox(bm_for(B, "dress"), F, u - 0.95, u + 0.95, PORT_TOP - 0.6, PORT_TOP + 1.6, P1, P1 + 1.9)     # on the rusticated ground storey
    cylinder(B, "dress", F.p(u, 0, P1 + 0.95), 0.58, PORT_TOP + 1.6, G + 20.6, seg=16)
    pbox(bm_for(B, "dress"), F, u - 0.85, u + 0.85, G + 20.6, G + 21.5, P1, P1 + 1.8)
entablature(B, F, UC - HALF - 0.3, UC + HALF + 0.3, G + 21.5, mat="dress", h=1.8, proj=P1 + 2.0)
for s_ in (-1, 1):
    u = UC + s_ * (ARCH_R + HALF) / 2
    for v0, h in ((PORT_TOP + 2.4, 3.0), (G + 15.6, 2.6)):
        win_rect(B, F, u, v0, v0 + h, 1.2, frame="dress", fill="dark", fw=0.2, pediment="cornice")
    for k in range(int((ARCH_SPRING - 0.6 - G) / 0.9)):                                     # banded rustication on the ground storey
        v = G + k * 0.9
        for (a0, a1) in ((UC - HALF, UC - ARCH_R - 0.6), (UC + ARCH_R + 0.6, UC + HALF)):
            pbox(bm_for(B, "dress"), F, a0, a1, v + 0.08, v + 0.82, P1, P1 + 0.12)
pbox(bm_for(B, "dress"), F, UC - HALF - 0.2, UC + HALF + 0.2, G + 21.5, G + 22.95, P1, P1 + 1.6)   # architrave and frieze over the columns
pbox(bm_for(B, "panel"), F, UC - 1.7, UC + 1.7, G + 22.1, G + 22.95, P1 + 1.6, P1 + 1.7)      # the date in the frieze
lettering(B, "letters", F, UC, G + 22.3, P1 + 1.7, "MDCCCXCV", 0.55, width=3.1)
# the attic with the inscription (L'ANTICO CENTRO DELLA CITTÀ / DA SECOLARE SQUALLORE / A VITA NUOVA RESTITUITO)
box(bm_for(B, "plaster"), F, UC - HALF + 1.0, UC + HALF - 1.0, G + 23.3, G + 29.6, -0.6, P1)
pbox(bm_for(B, "panel"), F, UC - ARCH_R - 0.8, UC + ARCH_R + 0.8, G + 24.4, G + 28.0, P1, P1 + 0.12)
for k, line in enumerate(("L'ANTICO CENTRO DELLA CITTÀ", "DA SECOLARE SQUALLORE", "A VITA NUOVA RESTITUITO")):
    lettering(B, "letters", F, UC, G + 27.05 - k * 1.08, P1 + 0.12, line, 0.78, width=2 * ARCH_R + 0.6)
entablature(B, F, UC - HALF + 0.8, UC + HALF - 0.8, G + 29.6, mat="dress", h=0.9, proj=P1 + 0.6)
for k in range(int((2 * HALF - 2.0) / 0.45)):                                               # balustrade on the attic
    u = UC - HALF + 1.2 + k * 0.45
    box(bm_for(B, "dress"), F, u - 0.1, u + 0.1, G + 30.5, G + 31.3, P1 - 0.3, P1 - 0.1)
pbox(bm_for(B, "dress"), F, UC - HALF + 1.0, UC + HALF - 1.0, G + 31.3, G + 31.55, P1 - 0.4, P1)
# statues: the four arts over the columns, and the crowning group (1895–1904)
def figure(part, u, n, z, h, group=1):
    for g in range(group):
        du = (g - (group - 1) / 2) * 0.9; hh = h * (1 - 0.15 * abs(g - (group - 1) / 2))
        box(bm_for(part, "marble"), F, u + du - 0.32, u + du + 0.32, z, z + hh * 0.82, n - 0.25, n + 0.25)
        box(bm_for(part, "marble"), F, u + du - 0.15, u + du + 0.15, z + hh * 0.82, z + hh, n - 0.15, n + 0.15)
for u in COLS:
    pbox(bm_for(B, "dress"), F, u - 0.6, u + 0.6, G + 23.3, G + 24.1, P1 + 0.4, P1 + 1.6)
    figure(f"arti@{FROM}-{NOW}", u, P1 + 1.0, G + 24.1, 2.6)
box(bm_for(f"gruppo_italia@{FROM}-1904", "marble"), F, UC - 2.0, UC + 2.0, G + 31.55, G + 32.6, -0.4, 0.8)
figure(f"gruppo_italia@{FROM}-1904", UC, 0.2, G + 32.6, 3.4, group=3)
# the back of the arch, on Via degli Strozzi
xb = -144.0
Fb = Frame(V(xb, Z_S), Vector((0, 1, 0)), Vector((-1, 0, 0)))          # u northwards (scene −z), n westwards
spandrel(B, "plaster", Fb, ARCH_R, ARCH_SPRING, ARCH_R, CROWN, 0.0)
ring(B, "dress", Fb, ARCH_R, ARCH_SPRING, ARCH_R, ARCH_R + 0.6, 0, 0.15, seg=18, soffit=False)
# the passage vault: a barrel under the bridge, from the square to Via degli Strozzi
bmv = bm_for(B, "plaster"); seg = 18; x0, x1 = xb, A0[0] + (37.5 - A0[1]) * tu[0] / tu[1]
for k in range(seg):
    a0, a1 = math.pi * k / seg, math.pi * (k + 1) / seg
    def q(x, a): return V(x, (Z_N + Z_S) / 2 - ARCH_R * math.cos(a), ARCH_SPRING + ARCH_R * math.sin(a))
    poly(bmv, [q(x0, a0), q(x1, a0), q(x1, a1), q(x0, a1)])
K.export("repubblica")
