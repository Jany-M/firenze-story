"""Orsanmichele – measured, dated model (v1).

Run:  blender -b --python blender/scripts/build_orsanmichele.py → web/public/models/landmarks/orsanmichele.glb
Frame: origin = centre of the block at ground (scene x −9.0 / z 121.6), X east, Y north, no rotation. Ground 10.0 m (datum).
Measured (LiDAR 2023 DSM 0.5 m; OSM way 442508011): 34.5 m (E–W) × 24.4 m (N–S), cornice ≈41 m, low roof to ≈43 m;
the passage to the Palazzo dell'Arte della Lana crosses Via dell'Arte della Lana on the west at ≈15–18 m.
Three bays on the long sides, two on the short ones: 14 pier faces = the 14 guild tabernacles.
Dates (docs/landmarks/ORSANMICHELE.md): Arnolfo's grain loggia 1290, burnt 1304 (*conjectural* form); new loggia from 1337;
first granary floor c. 1357, second floor and roof by 1404 (*inferred* split); arches walled with Gothic tracery c. 1380
(Simone Talenti); guild statues in the tabernacles from 1399 to the 1600s (one group, shown from 1416); Buontalenti's
passage to the Arte della Lana 1569.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
K.reset()
MAT["stone"] = material("pietra_forte", "pietra_forte", (0.62, 0.5, 0.36), 0.85, 0.32, tint=(3.0, 2.85, 2.55))

HX, HY = 17.25, 12.2

def hip(bm, x0, x1, y0, y1, z, rise):
    """Hip roof over a rectangle: ridge along the longer side."""
    if x1 - x0 >= y1 - y0:
        d = (y1 - y0) / 2; ym = (y0 + y1) / 2; a, b = (x0 + d, ym, z + rise), (x1 - d, ym, z + rise)
        poly(bm, [(x0, y0, z), (x1, y0, z), b, a]); poly(bm, [(x1, y1, z), (x0, y1, z), a, b])
        poly(bm, [(x1, y0, z), (x1, y1, z), b]); poly(bm, [(x0, y1, z), (x0, y0, z), a])
    else:
        d = (x1 - x0) / 2; xm = (x0 + x1) / 2; a, b = (xm, y0 + d, z + rise), (xm, y1 - d, z + rise)
        poly(bm, [(x1, y0, z), (x1, y1, z), b, a]); poly(bm, [(x0, y1, z), (x0, y0, z), a, b])
        poly(bm, [(x0, y0, z), (x1, y0, z), a]); poly(bm, [(x1, y1, z), (x0, y1, z), b])
FACES = [(Vector((0, -1, 0)), HY, HX), (Vector((1, 0, 0)), HX, HY), (Vector((0, 1, 0)), HY, HX), (Vector((-1, 0, 0)), HX, HY)]
def face_frame(n, dn, du):
    u = Vector((-n.y, n.x, 0)); return Frame(n * dn - u * du, u, n), 2 * du

def piers(L):
    k = 3 if L > 30 else 2; w = 3.2; step = (L - w) / k
    return [i * step for i in range(k + 1)], w, step

def loggia(part, tracery_part):
    """Ground floor: piers with tabernacle niches, round arches; tracery infill in its own (later) part."""
    for n, dn, du in FACES:
        F, L = face_frame(n, dn, du); P, w, step = piers(L)
        for u in P:
            box(bm_for(part, "stone"), F, u, u + w, -1.5, 13.0, -1.2, 0.0)
            # tabernacle: marble frame, pointed top, dark recess
            pbox(bm_for(part, "white"), F, u + 0.35, u + w - 0.35, 2.4, 7.6, 0.0, 0.35)
            poly(bm_for(part, "white"), [F.p(u + 0.35, 7.6, 0.36), F.p(u + w - 0.35, 7.6, 0.36), F.p(u + w / 2, 9.2, 0.36)])
            box(bm_for(part, "dark"), F, u + 0.7, u + w - 0.7, 2.8, 7.2, 0.36, 0.38)
        for a, b in zip(P[:-1], P[1:]):
            a0, b0 = a + w, b; r = (b0 - a0) / 2; spring = 13.0 - r - 0.4
            box(bm_for(part, "stone"), F, a0, b0, spring + r + 0.4, 13.0, -1.2, 0.0)            # spandrels
            for k in range(8):                                                                     # arch ring
                t0, t1 = k / 8 * math.pi, (k + 1) / 8 * math.pi
                poly(bm_for(part, "stone"), [F.p(a0 + r - r * math.cos(t0), spring + r * math.sin(t0), 0.02), F.p(a0 + r - r * math.cos(t1), spring + r * math.sin(t1), 0.02),
                                             F.p(a0 + r - r * math.cos(t1), 13.0, 0.02), F.p(a0 + r - r * math.cos(t0), 13.0, 0.02)])
            poly(bm_for(part, "dark"), [F.p(a0, -1.5, -1.0), F.p(b0, -1.5, -1.0), F.p(b0, spring, -1.0)] +
                 [F.p(a0 + r - r * math.cos(t), spring + r * math.sin(t), -1.0) for t in [k / 12 * math.pi for k in range(12, -1, -1)]] + [F.p(a0, spring, -1.0)])
            # c. 1380: the arches are walled, with tall Gothic tracery windows above a solid base
            box(bm_for(tracery_part, "stone"), F, a0, b0, -1.5, 4.2, -0.6, -0.2)
            opening(tracery_part, F, a0 + 0.6, b0 - 0.6, 4.2, spring + r * 0.9, depth=0.25, frame=0.35, pointed=True, fill="glass", frame_mat="white", mullion=True)
            poly(bm_for(tracery_part, "stone"), [F.p(a0, spring, -0.45)] + [F.p(a0 + r - r * math.cos(t), spring + r * math.sin(t), -0.45) for t in [k / 12 * math.pi for k in range(13)]] + [F.p(b0, spring, -0.45)])
        cornice(part, F, 0, L, 13.0, h=0.7, proj=0.45, mat="stone", arches=False)

def upper(part, v0, v1, top=False):
    """A granary floor: plain pietra forte walls, one large round-arched two-light window per bay."""
    for n, dn, du in FACES:
        F, L = face_frame(n, dn, du); P, w, step = piers(L)
        box(bm_for(part, "stone"), F, 0, L, v0, v1, -1.2, 0.0)
        for a, b in zip(P[:-1], P[1:]):
            m = (a + w + b) / 2
            opening(part, F, m - 1.6, m + 1.6, v0 + 3.0, v1 - 2.5, frame=0.4, pointed=False, fill="glass", frame_mat="stone", mullion=True)
        cornice(part, F, 0, L, v1, h=0.6 if not top else 1.0, proj=0.4 if not top else 0.9, mat="stone", arches=top)

def roof(part, z, rise):
    hip(bm_for(part, "roof"), -HX - 0.9, HX + 0.9, -HY - 0.9, HY + 0.9, z, rise)

def statues(part):
    """The guild statues in the 14 tabernacles (bronze and marble; originals now in the museum upstairs, copies outside)."""
    for n, dn, du in FACES:
        F, L = face_frame(n, dn, du); P, w, step = piers(L)
        for i, u in enumerate(P):
            mat = "bronze" if (i + int(n.x * 3 + n.y * 5)) % 3 == 0 else "white"
            box(bm_for(part, mat), F, u + w / 2 - 0.42, u + w / 2 + 0.42, 2.9, 6.1, 0.2, 0.55)
            box(bm_for(part, mat), F, u + w / 2 - 0.2, u + w / 2 + 0.2, 6.1, 6.7, 0.25, 0.5)

def passage(part):
    """Buontalenti's covered passage (1569) from the upper floor to the Palazzo dell'Arte della Lana across the street."""
    F = Frame(Vector((-HX, -3.0, 0)), Vector((-1, 0, 0)), Vector((0, -1, 0)))
    box(bm_for(part, "stone"), F, 0, 8.5, 14.5, 18.4, -3.2, 0.0)
    for k in range(9):
        t0, t1 = k / 9 * math.pi, (k + 1) / 9 * math.pi; r = 4.25
        poly(bm_for(part, "stone"), [F.p(r - r * math.cos(t0), 11.0 + r * 0.8 * math.sin(t0), 0.02), F.p(r - r * math.cos(t1), 11.0 + r * 0.8 * math.sin(t1), 0.02),
                                     F.p(r - r * math.cos(t1), 14.5, 0.02), F.p(r - r * math.cos(t0), 14.5, 0.02)])
    box(bm_for(part, "roof"), F, -0.2, 8.7, 18.4, 18.8, -3.5, 0.3)

# Arnolfo's open grain loggia of 1290 (burnt 1304): brick piers under a timber roof – conjectural form on the same plan
for n, dn, du in FACES:
    F, L = face_frame(n, dn, du); P, w, step = piers(L)
    for u in P: box(bm_for("loggia_arnolfo@1290-1304", "brick"), F, u + 0.4, u + w - 0.4, -1.5, 9.0, -1.0, 0.0)
    box(bm_for("loggia_arnolfo@1290-1304", "wood"), F, 0, L, 9.0, 10.0, -1.0, 0.0)
hip(bm_for("loggia_arnolfo@1290-1304", "roof"), -HX - 0.6, HX + 0.6, -HY - 0.6, HY + 0.6, 10.0, 4.0)

loggia(f"loggia@1337-{NOW}", f"tracery@1380-{NOW}")
upper(f"granary_1@1357-{NOW}", 13.7, 27.2)
roof("roof_temp@1357-1404", 27.8, 2.5)
upper(f"granary_2@1404-{NOW}", 27.8, 40.6, top=True)
roof(f"roof@1404-{NOW}", 41.6, 1.8)
statues(f"statues@1416-{NOW}")
passage(f"passage_lana@1569-{NOW}")
K.export("orsanmichele")
