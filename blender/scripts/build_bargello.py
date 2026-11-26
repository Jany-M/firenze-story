"""Bargello (Palazzo del Capitano del Popolo, then del Podestà) – measured, dated model (v1).

Run:  blender -b --python blender/scripts/build_bargello.py  →  web/public/models/landmarks/bargello.glb
Frame: origin = axis of the Torre Volognana at ground level (scene x 226.6 / z 136.0), X east, Y north, no rotation.
Ground 8.5 (DTM 48.5 m a.s.l.). Outline: OSM way 43837065, the whole block between Via del Proconsolo (west),
Via della Vigna Vecchia (north), Via dell'Acqua (east) and Via Ghibellina (south), ≈67 × 40 m.
Measured (LiDAR 2023 DSM 0.5 m): front wing on Via del Proconsolo x 223–242 to ≈28.5 m (top of the battlements);
courtyard open x 242–260 / z 142–163; a ≈12 m roof along its north side (the Verone); the other wings ≈23.5–24.5 m;
tower ≈8 m square at the north-west corner, top 54.9 m above the street.
Dates (docs/landmarks/BARGELLO.md): begun 1255 for the Capitano del Popolo on the Proconsolo side, taking in the
Boscoli tower (later called the Volognana); courtyard 1280–85; Via Ghibellina and Via dell'Acqua sides raised
1316–20, Vigna Vecchia side 1320, Verone 1317–20; Neri di Fioravante raises and vaults the palace 1340–45 (council hall);
courtyard staircase 1345–67. Early heights and the shape of the Boscoli tower are *conjectural*.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
K.reset()
MAT["stone"] = material("pietra_forte", "pietra_forte", (0.62, 0.5, 0.36), 0.85, 0.32, tint=(3.0, 2.85, 2.55))
MAT["serena"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)

OX, OZ = 226.6, 136.0
def M(sx, sz): return (sx - OX, -(sz - OZ))           # scene x/z → model X/Y

FRONT = [M(*p) for p in [(223.2, 129.7), (230.9, 130.0), (242.0, 131.0), (242.0, 142.0), (242.0, 163.0), (242.0, 171.1), (236.6, 171.1), (217.5, 168.5), (222.9, 136.3)]]
NORTH = [M(*p) for p in [(242.0, 131.0), (244.4, 131.2), (286.2, 134.9), (286.0, 142.0), (260.0, 142.0), (242.0, 142.0)]]
SOUTH = [M(*p) for p in [(242.0, 163.0), (260.0, 163.0), (285.4, 163.0), (285.3, 171.0), (242.0, 171.1)]]
BLOCK = [M(*p) for p in [(223.2, 129.7), (222.9, 136.3), (217.5, 168.5), (236.6, 171.1), (285.3, 171.0), (286.2, 134.9), (244.4, 131.2), (230.9, 130.0)]]   # OSM way 43837065
EAST = [M(*p) for p in [(260.0, 142.0), (286.0, 142.0), (285.4, 163.0), (260.0, 163.0)]]
COURT = (M(242.0, 163.0), M(260.0, 142.0))           # (x0, y0), (x1, y1) in model coords: open courtyard
TW = 4.1                                               # tower half-width

def ccw(pts):
    a = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    return pts if a > 0 else pts[::-1]
def edges(outline):
    """Wall frames for each edge of a polygon: u along the edge, n outward."""
    p = ccw(outline)
    for i in range(len(p)):
        a, b = Vector((*p[i], 0)), Vector((*p[(i + 1) % len(p)], 0)); d = b - a; L = d.length
        if L < 1.5: continue
        u = d / L; yield Frame(a, u, Vector((u.y, -u.x, 0))), L
def prism(part, outline, z0, z1, mat):
    bm = bm_for(part, mat); p = ccw(outline)
    bot = [bm.verts.new((x, y, z0)) for x, y in p]; top = [bm.verts.new((x, y, z1)) for x, y in p]
    bm.faces.new(top); bm.faces.new(bot[::-1])
    for i in range(len(p)):
        j = (i + 1) % len(p); bm.faces.new((bot[i], bot[j], top[j], top[i]))
def hip_roof(part, outline, z0, rise, mat="roof"):
    p = ccw(outline); cx = sum(x for x, _ in p) / len(p); cy = sum(y for _, y in p) / len(p)
    hi = [(cx + (x - cx) * 0.3, cy + (y - cy) * 0.3) for x, y in p]; bm = bm_for(part, mat)
    for i in range(len(p)):
        j = (i + 1) % len(p); poly(bm, [(*p[i], z0), (*p[j], z0), (*hi[j], z0 + rise), (*hi[i], z0 + rise)])
    poly(bm, [(*q, z0 + rise) for q in hi])
def seg_dist(p, a, b):
    a, b = Vector((*a, 0)), Vector((*b, 0)); d = b - a; t = max(0, min(1, (p - a).dot(d) / max(d.length_squared, 1e-9)))
    return (p - a - d * t).length
def kind_of(F, L):
    """'out' on the street (midpoint on the OSM outline), 'court' on the courtyard, 'shared' between two wings."""
    m = F.p(L / 2, 0); m.z = 0
    if min(seg_dist(m, BLOCK[i], BLOCK[(i + 1) % len(BLOCK)]) for i in range(len(BLOCK))) < 0.8: return "out"
    (x0, y0), (x1, y1) = COURT
    if (min(x0, x1) - 0.5 <= m.x <= max(x0, x1) + 0.5) and (min(y0, y1) - 0.5 <= m.y <= max(y0, y1) + 0.5): return "court"
    return "shared"
def is_inner(F, L): return kind_of(F, L) == "court"

def bifora(part, F, u, v0, v1, w=2.4):
    """Gothic two-light window: round outer arch, central colonnette, pietra forte frame."""
    opening(part, F, u - w / 2, u + w / 2, v0, v1, frame=0.35, pointed=False, fill="glass", frame_mat="stone")
    pbox(bm_for(part, "stone"), F, u - 0.09, u + 0.09, v0, v1 - w * 0.5, 0.0, 0.14)
def gallery(part, F, L, v0, crown, proj=1.0, merlon=(1.0, 0.8, 1.9)):
    """Battlements on corbels (beccatelli) with small arches, square Guelph merlons."""
    n = max(2, int(L / 1.6)); du = L / n
    for i in range(n + 1):
        u = i * du; box(bm_for(part, "stone"), F, u - 0.28, u + 0.28, v0, v0 + 2.0, 0, proj)
        for k in range(3): box(bm_for(part, "stone"), F, u - 0.32, u + 0.32, v0 + 0.3 + k * 0.55, v0 + 0.42 + k * 0.55, 0, proj * (0.4 + k * 0.25) + 0.05)
    for i in range(n):
        a, b = i * du + 0.28, (i + 1) * du - 0.28
        poly(bm_for(part, "dark"), [F.p(a + 0.05, v0 + 1.95, proj - 0.02), F.p(b - 0.05, v0 + 1.95, proj - 0.02), F.p(b - 0.05, v0 + 1.5, proj - 0.02), F.p(a + 0.05, v0 + 1.5, proj - 0.02)])
    box(bm_for(part, "stone"), F, -proj, L + proj, v0 + 2.0, crown, proj - 0.5, proj)
    mw, gap, mh = merlon; k = max(1, int((L + 2 * proj) / (mw + gap))); step = (L + 2 * proj) / k
    for i in range(k):
        u = -proj + i * step + (step - mw) / 2
        box(bm_for(part, "stone"), F, u, u + mw, crown, crown + mh, proj - 0.5, proj)

def facades(part, outline, z0, z1, kind):
    """Walls of one wing between z0 and z1. kind: 'front_low' | 'front_high' | 'wing_low' | 'wing_high'."""
    for F, L in edges(outline):
        k = kind_of(F, L)
        if k == "shared": continue                                             # wall between two wings: inside the block
        inner = k == "court"
        wall(part, F, 0, L, z0, z1, 1.6, "stone")
        if kind.endswith("low"):
            if inner:                                                            # courtyard portico (1280–85): round arches
                n = max(1, round(L / 4.6)); du = L / n
                for i in range(n):
                    opening(part, F, i * du + 0.55, (i + 1) * du - 0.55, 0.0, 6.2, depth=1.4, frame=0.3, pointed=False, fill="dark", frame_mat="serena")
                continue
            pbox(bm_for(part, "stone"), F, 0, L, 0, 0.9, 0, 0.3)                  # bench
            n = max(1, int(L / 8.5))
            for i in range(n):
                u = L * (i + 0.5) / n
                pbox(bm_for(part, "dark"), F, u - 0.55, u + 0.55, 5.6, 7.0, 0, 0.06)   # small barred windows
                pbox(bm_for(part, "stone"), F, u - 0.75, u + 0.75, 5.4, 5.6, 0, 0.18)
                opening(part, F, u - 0.8, u + 0.8, 10.0, 13.4, depth=0.4, frame=0.3, pointed=False, fill="glass", frame_mat="stone")
            pbox(bm_for(part, "stone"), F, -0.2, L + 0.2, 9.4, 9.75, 0, 0.25)       # string course
        else:
            n = max(1, int(L / (9.0 if kind == "front_high" else 7.5)))
            for i in range(n):
                u = L * (i + 0.5) / n
                if inner: opening(part, F, u - 0.9, u + 0.9, z0 + 1.2, z0 + 4.4, depth=0.4, frame=0.3, pointed=True, fill="glass", frame_mat="stone")
                else: bifora(part, F, u, z0 + 1.0, z0 + 5.4 if kind == "wing_high" else z0 + 5.0)
            pbox(bm_for(part, "stone"), F, -0.2, L + 0.2, z0 + 0.2, z0 + 0.55, 0, 0.25)

# ---- the Boscoli tower before the palace, then the Volognana ----
def tower(part, z0, z1, crown):
    T = [(-TW, -TW), (TW, -TW), (TW, TW), (-TW, TW)]
    prism(part, T, z0, z1, "stone")
    for F, L in edges(T):
        for v in range(int(z0) + 8, int(z1) - 3, 7):
            pbox(bm_for(part, "dark"), F, L / 2 - 0.25, L / 2 + 0.25, v, v + 1.4, 0, 0.05)        # slit windows
    if crown:                                                                     # corbelled crown with merlons
        for F, L in edges(T): gallery(part, F, L, z1, z1 + 2.6, proj=0.9, merlon=(0.9, 0.7, 1.6))
        prism(part, [(-1.6, -1.6), (1.6, -1.6), (1.6, 1.6), (-1.6, 1.6)], z1, z1 + 4.2, "stone")   # bell cell
        for F, L in edges([(-1.6, -1.6), (1.6, -1.6), (1.6, 1.6), (-1.6, 1.6)]):
            opening(part, F, 0.7, L - 0.7, z1 + 0.6, z1 + 3.3, depth=0.4, frame=0.2, pointed=False, fill="dark", frame_mat="stone")
        hip_roof(part, [(-1.9, -1.9), (1.9, -1.9), (1.9, 1.9), (-1.9, 1.9)], z1 + 4.2, 1.5)
    else:
        hip_roof(part, T, z1, 2.0)
tower("torre_boscoli@1180-1255", 0, 30.0, False)
tower(f"torre_volognana@1255-{NOW}", 0, 48.5, True)

# ---- front wing on Via del Proconsolo: two storeys from 1255, raised by Neri di Fioravante 1340–45 ----
facades(f"front_low@1255-{NOW}", FRONT, 0, 17.0, "front_low")
hip_roof("front_roof_early@1255-1340", FRONT, 17.0, 3.0)
# main portal on Via del Proconsolo (west face, middle of the long edge)
for F, L in edges(FRONT):
    if F.n.x < -0.9 and L > 25:
        opening(f"front_low@1255-{NOW}", F, L * 0.55 - 1.8, L * 0.55 + 1.8, 0, 6.0, depth=1.2, frame=0.6, pointed=False, fill="dark", frame_mat="stone")
facades(f"front_raise@1340-{NOW}", FRONT, 17.0, 24.5, "front_high")
for F, L in edges(FRONT):
    if kind_of(F, L) == "out": gallery(f"front_raise@1340-{NOW}", F, L, 24.5, 26.6)
hip_roof(f"front_raise@1340-{NOW}", FRONT, 24.6, 2.0)

# ---- the other wings: raised 1316–20 (Verone 1317–20), heightened 1340–45 ----
for nm, O in (("north", NORTH), ("south", SOUTH), ("east", EAST)):
    facades(f"{nm}_low@1316-{NOW}", O, 0, 15.0, "wing_low")
    hip_roof(f"{nm}_roof_early@1316-1340", O, 15.0, 2.6)
    facades(f"{nm}_raise@1340-{NOW}", O, 15.0, 20.5, "wing_high")
    for F, L in edges(O):
        if kind_of(F, L) == "out": gallery(f"{nm}_raise@1340-{NOW}", F, L, 20.5, 22.4, proj=0.8)
    hip_roof(f"{nm}_raise@1340-{NOW}", O, 20.6, 2.0)

# ---- courtyard: paving, well, the Verone (first-floor loggia on the north side) and the open staircase ----
(cx0, cy0), (cx1, cy1) = COURT                      # cy0 south (lower Y), cy1 north
pbox(bm_for(f"court@1280-{NOW}", "stone"), Frame((0, 0, 0), (1, 0, 0), (0, 1, 0)), cx0, cx1, 0, 0.12, cy0, cy1)
for a in range(10):                                  # the well in the middle
    c = Vector(((cx0 + cx1) / 2, (cy0 + cy1) / 2, 0)); ang = a / 10 * 2 * math.pi
    box(bm_for(f"court@1280-{NOW}", "stone"), Frame(c, (math.cos(ang + math.pi / 2), math.sin(ang + math.pi / 2), 0), (math.cos(ang), math.sin(ang), 0)), -0.4, 0.4, 0, 0.95, 0.75, 1.0)
yv = cy1 - 4.5                                       # Verone: 4.5 m deep loggia on piers over the north portico
Fv = Frame((cx0, yv, 0), (1, 0, 0), (0, -1, 0))
for i in range(5):
    u = (cx1 - cx0) * i / 4
    box(bm_for(f"verone@1317-{NOW}", "serena"), Fv, u - 0.35, u + 0.35, 0, 12.0, -0.35, 0.35)                 # piers
for i in range(4):
    u0, u1 = (cx1 - cx0) * i / 4 + 0.35, (cx1 - cx0) * (i + 1) / 4 - 0.35
    opening(f"verone@1317-{NOW}", Fv, u0, u1, 7.6, 11.4, depth=0.3, frame=0.25, pointed=False, fill="dark", frame_mat="serena")
    box(bm_for(f"verone@1317-{NOW}", "stone"), Fv, u0, u1, 7.2, 8.3, -0.1, 0.12)                              # parapet
box(bm_for(f"verone@1317-{NOW}", "stone"), Fv, -0.3, cx1 - cx0 + 0.3, 7.0, 7.4, -4.5, 0.3)                 # floor slab (towards the north wing)
lean_to(f"verone@1317-{NOW}", cx0, cx1, yv - 0.6, cy1, 12.0, 13.2)
# staircase (Neri di Fioravante, 1345–67): one straight flight along the west side of the courtyard, rising north
# to the Verone, low parapet with a lion on the newel post
n = 22; xs0, xs1 = cx0 + 0.1, cx0 + 2.6; y_start, y_end = cy0 + 1.0, yv - 0.2
for i in range(n):
    y0 = y_start + (y_end - y_start) * i / n; y1 = y_start + (y_end - y_start) * (i + 1) / n; z = 7.2 * (i + 1) / n
    wbox(bm_for(f"scalone@1367-{NOW}", "stone"), xs0, xs1, y0, y1, max(0, z - 0.9), z)
for i in range(n):
    y0 = y_start + (y_end - y_start) * i / n; y1 = y_start + (y_end - y_start) * (i + 1) / n; z = 7.2 * (i + 1) / n
    wbox(bm_for(f"scalone@1367-{NOW}", "stone"), xs1 - 0.25, xs1, y0, y1, z, z + 1.0)                         # parapet
wbox(bm_for(f"scalone@1367-{NOW}", "stone"), xs1 - 0.5, xs1 + 0.1, y_start - 0.6, y_start, 0, 1.6)              # newel post
wbox(bm_for(f"scalone@1367-{NOW}", "stone"), xs1 - 0.4, xs1, y_start - 0.5, y_start - 0.1, 1.6, 2.3)           # the lion (block)

K.export("bargello")
