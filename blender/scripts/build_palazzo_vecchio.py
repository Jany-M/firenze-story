"""Palazzo Vecchio (Palazzo dei Priori, della Signoria) – measured, dated model (v1).

Run:  blender -b --python blender/scripts/build_palazzo_vecchio.py  →  web/public/models/landmarks/palazzo_vecchio.glb
Frame: origin = axis of the Torre d'Arnolfo at ground level (LiDAR 2023 top 95.0 m at scene x 73.5 / z 276.5),
X east, Y north, Z up; footprints are the OSM outlines (way 361442652 = Arnolfo block, relation 1461712 = complex).
Measured (DSM 0.5 m, piazza at 49.8 m a.s.l.): west façade ≈45 m along the piazza, north side ≈29 m, crenellations
≈41 m, inner roofs 34–43 m, courtyard open; tower shaft ≈7.4 m, tower gallery ≈10.5 m wide at 63–73 m,
belfry 73–84 m, cupola and Marzocco to 95 m. East wings 33–36 m to Via dei Leoni.
Dates (docs/landmarks/PALAZZO-VECCHIO.md): Arnolfo block 1299–1314 (three stages *inferred*), tower on the stump of
the Foraboschi tower (*conjectural* shape), arengario 1323–1812, clock 1353, Salone dei Cinquecento 1495,
Vasari/Buontalenti wings to Via dei Leoni 1588 (*inferred* single date), David 1504 (copy since 1910), Hercules 1534.
Pietra forte throughout: no bare-brick phase.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
K.reset()
MAT["stone"] = material("pietra_forte", "pietra_forte", (0.62, 0.5, 0.36), 0.85, 0.32, tint=(3.0, 2.85, 2.55))
MAT["serena"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)
MAT["plaster"] = material("intonaco_ochre", "intonaco", (0.82, 0.72, 0.55), 0.85, 0.4)
MAT["clock"] = material("clock_dial", None, (0.12, 0.16, 0.3), 0.5)

OX, OZ = 73.5, 276.5
def M(sx, sz): return (sx - OX, -(sz - OZ))           # scene x/z → model X/Y
ARNOLFO = [M(*p) for p in [(75.4, 249.3), (103.8, 254.8), (96.9, 294.2), (95.1, 304.4), (67.5, 293.7)]]
SALONE = [M(*p) for p in [(103.8, 254.8), (127.5, 254.5), (122.0, 315.5), (109.6, 310.8), (98.8, 306.0), (95.1, 304.4), (96.9, 294.2)]]
DUCAL = [M(*p) for p in [(127.5, 254.5), (140.6, 254.4), (192.3, 260.0), (169.3, 313.2), (152.5, 335.9), (128.8, 318.0), (122.0, 315.5)]]
COURT = [M(*p) for p in [(80.5, 278.0), (90.5, 279.5), (89.0, 292.0), (79.0, 290.5)]]
N_DIR = Vector((7.9, 44.4, 0)).normalized()               # along the west façade, towards north (≈10° east of north)
E_DIR = Vector((N_DIR.y, -N_DIR.x, 0))

def ccw(pts):
    a = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    return pts if a > 0 else pts[::-1]
def edges(outline):
    """Wall frames for each edge of a polygon: u along the edge, n outward."""
    p = ccw(outline)
    for i in range(len(p)):
        a, b = Vector((*p[i], 0)), Vector((*p[(i + 1) % len(p)], 0)); d = b - a; L = d.length
        if L < 2: continue
        u = d / L; yield Frame(a, u, Vector((u.y, -u.x, 0))), L

def prism(part, outline, z0, z1, mat):
    bm = bm_for(part, mat); p = ccw(outline)
    bot = [bm.verts.new((x, y, z0)) for x, y in p]; top = [bm.verts.new((x, y, z1)) for x, y in p]
    bm.faces.new(top); bm.faces.new(bot[::-1])
    for i in range(len(p)):
        j = (i + 1) % len(p); bm.faces.new((bot[i], bot[j], top[j], top[i]))

def hip_roof(part, outline, z0, rise, mat="roof", inset=0.0):
    """Roof over a convex-ish polygon: faces from each edge up to a ridge polygon shrunk towards the centroid."""
    p = ccw(outline); cx = sum(x for x, _ in p) / len(p); cy = sum(y for _, y in p) / len(p)
    lo = [(cx + (x - cx) * (1 - inset), cy + (y - cy) * (1 - inset)) for x, y in p]
    hi = [(cx + (x - cx) * 0.25, cy + (y - cy) * 0.25) for x, y in p]
    bm = bm_for(part, mat)
    for i in range(len(p)):
        j = (i + 1) % len(p)
        poly(bm, [(*lo[i], z0), (*lo[j], z0), (*hi[j], z0 + rise), (*hi[i], z0 + rise)])
    poly(bm, [(*q, z0 + rise) for q in hi])

def bifora(part, F, u, v0, v1, w=2.6):
    """Gothic two-light window of the palace: round outer arch, colonnette, trefoil oculus, pietra forte frame."""
    opening(part, F, u - w / 2, u + w / 2, v0, v1, frame=0.4, pointed=False, fill="glass", frame_mat="stone")
    pbox(bm_for(part, "stone"), F, u - 0.1, u + 0.1, v0, v1 - w * 0.55, 0.0, 0.14)
    for s in (-1, 1):                                                          # the two small arches
        c = u + s * w / 4
        poly(bm_for(part, "stone"), [F.p(c + w / 4 * math.cos(a), v1 - w * 0.55 + w / 4 * math.sin(a), 0.1) for a in [i / 10 * math.pi for i in range(11)]]
             + [F.p(c - w / 4, v1 - w * 0.55 - 0.12, 0.1), F.p(c + w / 4, v1 - w * 0.55 - 0.12, 0.1)])
    poly(bm_for(part, "stone"), [F.p(u + 0.32 * math.cos(a), v1 - w * 0.22 + 0.32 * math.sin(a), 0.12) for a in [i / 12 * 2 * math.pi for i in range(12)]])

def string_course(part, F, L, v, h=0.45, proj=0.3, mat="stone"):
    box(bm_for(part, mat), F, -proj, L + proj, v, v + h, 0, proj)

def gallery(part, F, L, v0=31.0, crown=38.4, proj=1.3, merlon=(1.1, 0.75, 2.6), swallow=False, mat="stone"):
    """Ballatoio: corbels (beccatelli) with arches between them, gallery wall on top, crenellation."""
    n = max(2, int(L / 1.7)); du = L / n
    for i in range(n + 1):                                                     # corbels
        u = i * du; box(bm_for(part, mat), F, u - 0.32, u + 0.32, v0, v0 + 2.6, 0, proj)
        for k in range(3): box(bm_for(part, mat), F, u - 0.36, u + 0.36, v0 + 0.5 + k * 0.7, v0 + 0.62 + k * 0.7, 0, proj * (0.45 + k * 0.25) + 0.05)
    for i in range(n):                                                         # arches between corbels
        a, b = i * du + 0.32, (i + 1) * du - 0.32                                # machicolation gaps
        poly(bm_for(part, "dark"), [F.p(a + 0.05, v0 + 2.55, proj - 0.02), F.p(b - 0.05, v0 + 2.55, proj - 0.02), F.p(b - 0.05, v0 + 2.0, proj - 0.02), F.p(a + 0.05, v0 + 2.0, proj - 0.02)])
    box(bm_for(part, mat), F, -proj, L + proj, v0 + 2.6, crown, proj - 0.55, proj)            # gallery wall
    box(bm_for(part, mat), F, -proj, L + proj, crown - 0.3, crown, proj - 0.6, proj + 0.12)    # coping
    mw, gap, mh = merlon; k = max(1, int((L + 2 * proj) / (mw + gap)))
    step = (L + 2 * proj) / k
    for i in range(k):
        u = -proj + i * step + (step - mw) / 2
        if swallow:                                                            # Ghibelline swallowtail: two prongs
            box(bm_for(part, mat), F, u, u + mw, crown, crown + mh * 0.6, proj - 0.5, proj)
            box(bm_for(part, mat), F, u, u + mw * 0.38, crown + mh * 0.6, crown + mh, proj - 0.5, proj)
            box(bm_for(part, mat), F, u + mw * 0.62, u + mw, crown + mh * 0.6, crown + mh, proj - 0.5, proj)
        else:
            box(bm_for(part, mat), F, u, u + mw, crown, crown + mh, proj - 0.5, proj)

def block_facades(part, z0, z1, stage):
    """Arnolfo block, one construction stage: walls between z0 and z1 with that stage's openings."""
    for F, L in edges(ARNOLFO):
        wall(part, F, 0, L, z0, z1, 1.8, "stone")
        west = abs(F.n.x) > 0.9 and F.n.x < 0
        if stage == 0:
            pbox(bm_for(part, "stone"), F, 0, L, 0, 1.2, 0, 0.35)                 # plinth bench
            for u in [L * (i + 0.5) / max(2, int(L / 9)) for i in range(max(2, int(L / 9)))]:
                if west and 20 < u < 31: continue
                pbox(bm_for(part, "dark"), F, u - 0.6, u + 0.6, 7.6, 9.2, 0.0, 0.06)   # small barred windows
                pbox(bm_for(part, "stone"), F, u - 0.8, u + 0.8, 7.4, 7.6, 0, 0.2)
            string_course(part, F, L, 11.0)
        else:
            v0, v1 = (13.4, 19.8) if stage == 1 else (23.4, 29.8)
            n = max(2, int(L / 8.5))
            for i in range(n):
                bifora(part, F, L * (i + 0.5) / n, v0, v1)
            string_course(part, F, L, v0 - 0.6, 0.35, 0.22)
            if stage == 1: string_course(part, F, L, 21.0)
            else: gallery(part, F, L)
    if stage == 0:                                                             # main portal on the piazza
        F, L = next((F, L) for F, L in edges(ARNOLFO) if F.n.x < -0.9)
        opening(part, F, 23.9, 27.1, 0, 7.6, frame=0.55, pointed=False, fill="wood", frame_mat="stone")
        pbox(bm_for(part, "serena"), F, 23.1, 27.9, 9.0, 10.4, 0, 0.35)          # frieze over the door (Medici monogram, 1528)

# ------------------------------------------------------------------ the parts
# Torre dei Foraboschi ("della Vacca"): its stump carries Arnolfo's tower – height and shape conjectural
tf = Frame((0, 0, 0), E_DIR, N_DIR)
box(bm_for(f"torre_foraboschi@1150-1310", "stone"), tf, -3.5, 3.5, 0, 30, -3.5, 3.5)

block_facades(f"arnolfo_ground@1299-{NOW}", 0, 11.6, 0)
prism(f"arnolfo_ground@1299-{NOW}", COURT, 0.0, 0.2, "stone")
block_facades(f"arnolfo_piano_nobile@1304-{NOW}", 11.6, 21.6, 1)
block_facades(f"arnolfo_top@1310-{NOW}", 21.6, 31.2, 2)
# roofs: north range higher (LiDAR 42–43 m), lower ranges around the courtyard
north = [M(*p) for p in [(75.4, 249.3), (103.8, 254.8), (100.5, 273.5), (71.6, 271.2)]]
prism(f"arnolfo_top@1310-{NOW}", north, 31.0, 38.0, "stone")
hip_roof(f"arnolfo_top@1310-{NOW}", north, 38.0, 4.2, inset=0.06)
south = [M(*p) for p in [(71.6, 271.2), (100.5, 273.5), (96.9, 294.2), (95.1, 304.4), (67.5, 293.7)]]
hip_roof(f"arnolfo_top@1310-{NOW}", south, 33.4, 2.4, inset=0.04)
poly(bm_for(f"arnolfo_top@1310-{NOW}", "dark"), [(x, y, 36.0) for x, y in ccw(COURT)])   # light well over the courtyard

# Torre d'Arnolfo, 1310 (built on the Foraboschi stump; shaft above the gallery, its own machicolated gallery,
# swallowtail merlons, open belfry, cupola and the Marzocco on the spire)
T = "torre_arnolfo@1310-" + str(NOW)
h = 3.7
box(bm_for(T, "stone"), tf, -h, h, 20, 63.5, -h, h)
for k, (u, nrm) in enumerate(((E_DIR, N_DIR), (-E_DIR, -N_DIR), (N_DIR, -E_DIR), (-N_DIR, E_DIR))):
    F = Frame(Vector((0, 0, 0)) + nrm * h - u * h, u, nrm)
    for v in (46.0, 54.0):
        opening(T, F, h - 0.45, h + 0.45, v, v + 1.8, frame=0.25, pointed=False, fill="dark", frame_mat="stone")
    gallery(T, F, 2 * h, v0=60.5, crown=70.2, proj=1.55, merlon=(1.0, 0.7, 2.6), swallow=True)
box(bm_for(T, "stone"), tf, -h - 1.55, h + 1.55, 63.1, 63.5, -h - 1.55, h + 1.55)      # gallery floor
box(bm_for(T, "stone"), tf, -3.0, 3.0, 63.5, 72.8, -3.0, 3.0)                         # core under the belfry
# clock on the west face (a public clock from 1353; the present dial and movement are 17th century)
Fw = Frame(-E_DIR * h + N_DIR * h, -N_DIR, -E_DIR)
poly(bm_for(f"tower_clock@1353-{NOW}", "clock"), [Fw.p(h + 1.6 * math.cos(a), 43.0 + 1.6 * math.sin(a), 0.08) for a in [i / 24 * 2 * math.pi for i in range(24)]])
poly(bm_for(f"tower_clock@1353-{NOW}", "gold"), [Fw.p(h + 0.25 * math.cos(a), 43.0 + 0.25 * math.sin(a), 0.12) for a in [i / 8 * 2 * math.pi for i in range(8)]])
box(bm_for(f"tower_clock@1353-{NOW}", "gold"), Fw, h - 0.06, h + 0.06, 43.0, 44.3, 0.1, 0.14)
# belfry: four piers carrying a small crenellated cap, the bell inside
for su in (-1, 1):
    for sn in (-1, 1):
        box(bm_for(T, "stone"), tf, su * 2.9 - 0.45, su * 2.9 + 0.45, 72.8, 80.6, sn * 2.9 - 0.45, sn * 2.9 + 0.45)
box(bm_for(T, "stone"), tf, -3.4, 3.4, 72.8, 73.2, -3.4, 3.4)
box(bm_for(T, "stone"), tf, -3.6, 3.6, 80.6, 81.6, -3.6, 3.6)
for k, (u, nrm) in enumerate(((E_DIR, N_DIR), (-E_DIR, -N_DIR), (N_DIR, -E_DIR), (-N_DIR, E_DIR))):
    F = Frame(nrm * 3.6 - u * 3.6, u, nrm)
    box(bm_for(T, "stone"), F, 0, 7.2, 81.6, 83.0, -0.6, 0)
    for i in range(4):
        uu = 0.35 + i * 1.75
        box(bm_for(T, "stone"), F, uu, uu + 0.35, 83.0, 84.4, -0.6, 0); box(bm_for(T, "stone"), F, uu + 0.75, uu + 1.1, 83.0, 84.4, -0.6, 0)
bm = bm_for(T, "bronze")
bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=1.2, radius2=0.5, depth=1.8, matrix=Matrix.Translation((0, 0, 76.4)))
bm = bm_for(T, "lead")
bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=2.6, radius2=1.0, depth=4.0, matrix=Matrix.Translation((0, 0, 86.0)))
bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=1.0, radius2=0.15, depth=3.4, matrix=Matrix.Translation((0, 0, 89.7)))
bm = bm_for(T, "gold")
bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.08, radius2=0.08, depth=2.4, matrix=Matrix.Translation((0, 0, 92.6)))
wbox(bm, -0.25, 0.25, -0.7, 0.7, 93.6, 94.4); wbox(bm, -0.18, 0.18, 0.4, 0.75, 94.4, 95.0)         # the Marzocco vane

# arengario (speakers' platform along the façade, 1323) → reduced to today's steps in 1812
Fw2, Lw = next((F, L) for F, L in edges(ARNOLFO) if F.n.x < -0.9)
box(bm_for("arengario@1323-1812", "stone"), Fw2, 1.0, Lw - 1.0, 0, 1.6, 0, 4.4)
box(bm_for("arengario@1323-1812", "stone"), Fw2, 1.0, Lw - 1.0, 1.6, 2.6, 4.0, 4.4)
for s in range(3):
    box(bm_for(f"steps@1812-{NOW}", "stone"), Fw2, 14.0, 37.0, 0, 0.9 - s * 0.3, 0, 3.0 - s * 0.9)

# statues flanking the door: David (Michelangelo 1504, copy since 1910) and Hercules and Cacus (Bandinelli 1534)
def statue(part, u, base_h, fig_h):
    box(bm_for(part, "white"), Fw2, u - 0.9, u + 0.9, 0.0, 0.9 + base_h, 3.2, 5.0)
    box(bm_for(part, "white"), Fw2, u - 0.35, u + 0.35, 0.9 + base_h, 0.9 + base_h + fig_h * 0.86, 3.85, 4.35)
    box(bm_for(part, "white"), Fw2, u - 0.18, u + 0.18, 0.9 + base_h + fig_h * 0.86, 0.9 + base_h + fig_h, 3.9, 4.3)
statue("david@1504_159-1873", 21.6, 2.0, 5.2)                 # set on the ringhiera 8 June 1504, to the Accademia 1873
statue(f"david_copy@1910-{NOW}", 21.6, 2.0, 5.2)              # Arrighetti's marble copy
statue(f"hercules@1534-{NOW}", 29.6, 2.0, 5.0)

# east: medieval houses on the lots (conjectural), then Cronaca's Salone dei Cinquecento and the ducal wings
def wing(part, poly_, eaves, rise):
    prism(part, poly_, 0, eaves, "plaster")
    for F, L in edges(poly_):
        pbox(bm_for(part, "stone"), F, 0, L, 0, 4.5, 0, 0.12)                     # rusticated base
        string_course(part, F, L, eaves - 0.6, 0.6, 0.6, "serena")
        floors = [6.5, 14.5, 23.0] if eaves > 25 else [3.5, 8.0]
        n = max(1, int(L / 4.2))
        for v in floors:
            for i in range(n):
                u = L * (i + 0.5) / n
                pbox(bm_for(part, "serena"), F, u - 0.85, u + 0.85, v - 0.2, v + 3.0, 0, 0.1)
                pbox(bm_for(part, "glass"), F, u - 0.6, u + 0.6, v, v + 2.7, 0, 0.13)
    hip_roof(part, poly_, eaves, rise, inset=0.0)
def inside(pt, outline):
    x, y = pt; c = False; p = outline
    for i in range(len(p)):
        (x1, y1), (x2, y2) = p[i], p[i - 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
    return c

def houses(part, outline, seed):
    """Medieval houses on the lot before the palace grew over it (conjectural): narrow plots, 3–5 storeys, gable roofs."""
    import random; rnd = random.Random(seed)
    xs = [x for x, _ in outline]; ys = [y for _, y in outline]; R = max(max(xs) - min(xs), max(ys) - min(ys))
    cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
    for i in range(-int(R / 9) - 1, int(R / 9) + 2):
        for j in range(-int(R / 11) - 1, int(R / 11) + 2):
            c = Vector((cx, cy, 0)) + E_DIR * (i * 9.0) + N_DIR * (j * 11.0)
            if not inside((c.x, c.y), outline) or rnd.random() < 0.12: continue          # a few yards/gardens
            w, d, hgt = 4.0 + rnd.random() * 0.4, 5.2, 9.0 + rnd.choice((0, 3.2, 3.2, 6.4))
            F = Frame(c - E_DIR * w - N_DIR * d, E_DIR, -N_DIR)
            box(bm_for(part, "plaster" if rnd.random() < 0.6 else "stone"), Frame(c, E_DIR, N_DIR), -w, w, 0, hgt, -d, d)
            for k in range(int(hgt / 3.2)):
                for sgn in (-1, 1):
                    Fe = Frame(c + E_DIR * sgn * w - N_DIR * sgn * d, N_DIR * sgn, E_DIR * sgn)
                    for u in (2.5, 5.2, 7.9):
                        pbox(bm_for(part, "dark"), Fe, u - 0.4, u + 0.4, 1.4 + k * 3.2, 2.6 + k * 3.2, 0, 0.05)
            bm = bm_for(part, "roof")
            a = [c + E_DIR * sx * (w + 0.4) + N_DIR * sy * (d + 0.4) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            top0, top1 = c - N_DIR * (d + 0.4), c + N_DIR * (d + 0.4)
            poly(bm, [(*a[0][:2], hgt), (*a[1][:2], hgt), (*top0[:2], hgt + 2.2)])
            poly(bm, [(*a[2][:2], hgt), (*a[3][:2], hgt), (*top1[:2], hgt + 2.2)])
            poly(bm, [(*a[1][:2], hgt), (*a[2][:2], hgt), (*top1[:2], hgt + 2.2), (*top0[:2], hgt + 2.2)])
            poly(bm, [(*a[3][:2], hgt), (*a[0][:2], hgt), (*top0[:2], hgt + 2.2), (*top1[:2], hgt + 2.2)])
houses(f"houses_west@1220-1495", SALONE, 3)
houses(f"houses_east@1220-1588", DUCAL, 7)
wing(f"salone_cinquecento@1495-{NOW}", SALONE, 32.0, 2.8)
wing(f"ducal_wings@1588-{NOW}", DUCAL, 30.0, 2.6)

K.export("palazzo_vecchio")
