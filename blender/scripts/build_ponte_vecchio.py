"""Ponte Vecchio, 1345 bridge with its shops and the Vasari Corridor – measured, dated model (v1).

Run:  blender -b --python blender/scripts/build_ponte_vecchio.py  →  web/public/models/landmarks/ponte_vecchio.glb
Frame: world-aligned, origin at the middle of the bridge axis (OSM way 24999532, scene x −151.55 / z 425.45),
X east, Y north; heights are absolute (metres a.s.l. − 40, the scene's datum), so the landmark sits at ground 0.
Measured (DSM/DTM 0.5 m, sections every 4 m): river ≈1.6, street on the bridge 9–10.5 (slight hump), west shops up to
≈17.5, east shops and corridor up to ≈22.4, open terraces at the centre (t 42–58 m), banks at t ≈2 and ≈96 m.
Dates (docs/landmarks/PONTE-VECCHIO.md): bridge 1345 (three segmental arches, 27 + 30 + 27 m, piers 6 m); shops from
1345 (butchers, goldsmiths after 1593 – same buildings); back rooms cantilevered over the river from c. 1600
(*inferred*); Vasari Corridor 1565; Cellini bust 1901. Earlier bridges stay parametric (bridges.ts).
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
K.reset()
MAT["stone"] = material("pietra_forte", "pietra_forte", (0.62, 0.5, 0.36), 0.85, 0.32, tint=(3.0, 2.85, 2.55))
MAT["ochre"] = material("plaster_ochre", "intonaco", (0.8, 0.55, 0.3), 0.9, 0.4, tint=(1.15, 0.5, 0.14))
MAT["rose"] = material("plaster_rose", "intonaco", (0.78, 0.5, 0.42), 0.9, 0.4, tint=(1.1, 0.41, 0.29))
MAT["yellow"] = material("plaster_yellow", "intonaco", (0.88, 0.72, 0.45), 0.9, 0.4, tint=(1.45, 0.92, 0.33))
MAT["rust"] = material("plaster_rust", "intonaco", (0.7, 0.38, 0.25), 0.9, 0.4, tint=(0.87, 0.23, 0.1))
MAT["corr"] = material("plaster_corridor", "intonaco", (0.86, 0.76, 0.58), 0.9, 0.4, tint=(1.25, 0.95, 0.55))

A = Vector((-128.8, 379.8)); B = Vector((-174.3, 471.1)); MID = (A + B) / 2
u_sc = (B - A).normalized()
U = Vector((u_sc.x, -u_sc.y, 0))                  # along the bridge, north → south, in model XY (Y = north = −scene z)
E = Vector((-U.y, U.x, 0))                        # across the bridge
if E.x < 0: E = -E                                # +w = east (upstream), where the corridor runs
def P(s, w, z): return U * s + E * w + Vector((0, 0, z))
def F_side(w_face, outward):                      # wall frame on a plane of constant w, u along +s, n = ±E
    return Frame(P(0, w_face, 0), U if outward > 0 else -U, E * outward)

WATER, SPRING, DECK = 1.6, 3.0, 9.4
SPANS = [(-48, -21, 3.6), (-15, 15, 4.4), (21, 48, 3.6)]           # (s0, s1, rise) – side arches 27 m, centre 30 m
PIERS = [(-21, -15), (15, 21)]
HALF = 9.0                                                         # half width of the masonry body
deck_z = lambda s: DECK + 1.0 * (1 - (s / 50.0) ** 2)                # the street humps ≈1 m at mid-bridge

def intrados(s0, s1, rise, n=16):
    """Segmental arch: circle through the springings and the crown."""
    half = (s1 - s0) / 2; R = (half * half + rise * rise) / (2 * rise); cs = (s0 + s1) / 2; cz = SPRING + rise - R
    a0 = math.asin(half / R)
    return [(cs + R * math.sin(-a0 + 2 * a0 * i / n), cz + R * math.cos(-a0 + 2 * a0 * i / n)) for i in range(n + 1)]

def bridge(part):
    st = bm_for(part, "stone")
    for w in (-HALF, HALF):
        for s0, s1, rise in SPANS:                                   # spandrel between arch and deck, both faces
            ins = intrados(s0, s1, rise)
            quad_strip(st, [P(s, w, z) for s, z in ins], [P(s, w, deck_z(s) - 0.4) for s, _ in ins])
        for s0, s1 in PIERS:
            poly(st, [P(s0, w, WATER - 0.5), P(s1, w, WATER - 0.5), P(s1, w, deck_z(s1) - 0.4), P(s0, w, deck_z(s0) - 0.4)])
        for s in (-48, 48):                                          # abutments
            sg = 1 if s > 0 else -1
            poly(st, [P(s, w, WATER - 0.5), P(s + 6 * sg, w, WATER - 0.5), P(s + 6 * sg, w, deck_z(s) - 0.4), P(s, w, deck_z(s) - 0.4)])
    for s0, s1, rise in SPANS:                                       # soffits
        ins = intrados(s0, s1, rise)
        quad_strip(st, [P(s, -HALF, z) for s, z in ins], [P(s, HALF, z) for s, z in ins])
    # piers with pointed cutwaters both up- and downstream, capped by a sloping top
    for s0, s1 in PIERS:
        sm = (s0 + s1) / 2
        for sg in (-1, 1):
            tip = P(sm, sg * (HALF + 4.5), WATER - 0.5); a = P(s0, sg * HALF, WATER - 0.5); b = P(s1, sg * HALF, WATER - 0.5)
            top = 6.6
            for p0, p1 in ((a, tip), (tip, b)):
                poly(st, [p0, p1, p1 + Vector((0, 0, top - WATER + 0.5)), p0 + Vector((0, 0, top - WATER + 0.5))])
            poly(st, [a + Vector((0, 0, top - WATER + 0.5)), tip + Vector((0, 0, top - WATER + 0.5)), b + Vector((0, 0, top - WATER + 0.5))])
    # street surface and string course
    xs = [i * 2.0 - 54 for i in range(55)]
    quad_strip(bm_for(part, "stone"), [P(s, -HALF - 0.3, deck_z(s)) for s in xs], [P(s, HALF + 0.3, deck_z(s)) for s in xs])
    for w in (-HALF - 0.35, HALF + 0.35):
        for i in range(len(xs) - 1):
            s, t = xs[i], xs[i + 1]
            poly(st, [P(s, w, deck_z(s) - 0.9), P(t, w, deck_z(t) - 0.9), P(t, w, deck_z(t) - 0.4), P(s, w, deck_z(s) - 0.4)])

def shop_row(part_core, part_back, side, s_from, s_to, rnd, top_range, east=False, backs=True):
    """Shops along one side: plastered fronts with wooden shutter boxes (madielle), upper floor, back rooms over the river."""
    s = s_from
    while s < s_to - 1.5:
        w = min(rnd.uniform(3.2, 4.6), s_to - s); s1 = s + w; z0 = deck_z((s + s1) / 2)
        top = 17.6 if east else rnd.uniform(*top_range)
        mat = rnd.choice(("ochre", "rose", "yellow", "ochre", "rust"))
        Fs = Frame(P(s, side * 4.2, 0), U, -E * side)                                  # street front, n towards the street
        box(bm_for(part_core, mat), Fs, 0, w, z0, top, -4.4, 0)                          # body from the street to w = ±8.6
        pbox(bm_for(part_core, "wood"), Fs, 0.3, w - 0.3, z0, z0 + 2.9, 0, 0.55)           # madielle (closed shutter box)
        box(bm_for(part_core, "dark"), Fs, 0.6, w - 0.6, z0 + 0.4, z0 + 2.5, 0.55, 0.58)
        for v in (z0 + 4.0,) + ((z0 + 6.4,) if top - z0 > 7.5 else ()):
            pbox(bm_for(part_core, "dark"), Fs, w / 2 - 0.45, w / 2 + 0.45, v, v + 1.3, 0, 0.05)
        if not east:                                                                   # tiled lean-to roof over each shop
            rb = bm_for(part_core, "roof")
            poly(rb, [P(s, side * 3.9, top + 1.0), P(s1, side * 3.9, top + 1.0), P(s1, side * 9.0, top - 0.1), P(s, side * 9.0, top - 0.1)])
            box(rb, Fs, 0, w, top - 0.1, top + 1.0, -0.05, 0.3)   # eave towards the street
        Fr = Frame(P(s, side * 8.6, 0), U, E * side)                                    # river side of the shop
        for v in (z0 + 4.2,) + ((top - 2.2,) if top - z0 > 7.5 else ()):
            pbox(bm_for(part_core, "dark"), Fr, w / 2 - 0.4, w / 2 + 0.4, v, v + 1.2, 0, 0.04)
        # back room (retrochetto) cantilevered over the river on timber struts
        if backs and rnd.random() < 0.8:
            d = rnd.uniform(1.8, 3.2); b0 = rnd.uniform(10.6, 12.2); b1 = min(top - 0.3, b0 + rnd.uniform(3.0, 5.0))
            Fb = Frame(P(s, side * 8.6, 0), U, E * side)
            box(bm_for(part_back, rnd.choice(("ochre", "rose", "yellow", "rust"))), Fb, 0.15, w - 0.15, b0, b1, 0, d)
            box(bm_for(part_back, "roof"), Fb, 0.05, w - 0.05, b1, b1 + 0.25, 0, d + 0.3)
            box(bm_for(part_back, "dark"), Fb, w / 2 - 0.4, w / 2 + 0.4, b0 + 1.0, b0 + 2.1, d, d + 0.04)
            for k in (0.4, w - 0.6):                                                   # struts
                box(bm_for(part_back, "wood"), Fb, k, k + 0.2, b0 - 2.2, b0, d - 0.4, d - 0.2)
                box(bm_for(part_back, "wood"), Fb, k, k + 0.2, b0 - 2.2, b0 - 1.9, 0, d - 0.2)
        s = s1

def corridor(part):
    """Vasari Corridor on the east shops: plastered gallery with small windows; on an arcade across the centre."""
    W0, W1, z0, z1 = 5.4, 9.4, 17.6, 22.2
    for s0, s1, on_arcade in ((-48.5, -6.0, False), (-6.0, 10.0, True), (10.0, 46.0, False)):
        if on_arcade:
            z0a = 15.6
            for sp in (-6.0, -0.7, 4.7, 10.0):                                         # arcade piers
                box(bm_for(part, "stone"), Frame(P(sp - 0.6, W0, 0), U, E), 0, 1.2, deck_z(sp), z0a, 0, W1 - W0)
            for a0, a1 in ((-5.4, -1.3), (-0.1, 4.1), (5.3, 9.4)):                       # round arches
                for w in (W0, W1):
                    Fa = Frame(P(a0, w, 0), U, E * (1 if w == W1 else -1))
                    r = (a1 - a0) / 2
                    quad_strip(bm_for(part, "stone"),
                               [Fa.p(r - r * math.cos(t), 13.0 + r * math.sin(t) * 0.9, 0) for t in [k / 10 * math.pi for k in range(11)]],
                               [Fa.p(r - r * math.cos(t), z0a, 0) for t in [k / 10 * math.pi for k in range(11)]])
            zz0 = z0a
        else:
            zz0 = z0
        box(bm_for(part, "corr"), Frame(P(s0, W0, 0), U, -E), 0, s1 - s0, zz0, z1, -(W1 - W0), 0)
        for w, nn in ((W1, 1), (W0, -1)):
            Fw = Frame(P(s0, w, 0), U, E * nn)
            pbox(bm_for(part, "stone"), Fw, 0, s1 - s0, zz0 - 0.4, zz0, 0, 0.25)          # corbel course
            k = int((s1 - s0) / 3.6)
            for i in range(k):
                uu = (i + 0.5) * (s1 - s0) / k
                if i % 3 == 1:
                    poly(bm_for(part, "dark"), [Fw.p(uu + 0.45 * math.cos(a), z1 - 1.9 + 0.45 * math.sin(a), 0.03) for a in [j / 10 * 2 * math.pi for j in range(10)]])
                else:
                    pbox(bm_for(part, "dark"), Fw, uu - 0.35, uu + 0.35, z1 - 2.6, z1 - 1.2, 0, 0.03)
        rb = bm_for(part, "roof")
        poly(rb, [P(s0, W0 - 0.3, z1), P(s1, W0 - 0.3, z1), P(s1, (W0 + W1) / 2, z1 + 1.1), P(s0, (W0 + W1) / 2, z1 + 1.1)])
        poly(rb, [P(s1, W1 + 0.3, z1), P(s0, W1 + 0.3, z1), P(s0, (W0 + W1) / 2, z1 + 1.1), P(s1, (W0 + W1) / 2, z1 + 1.1)])

def terraces(part):
    """Open terraces at mid-bridge: stone parapets towards the river on the west side."""
    for side in (-1,):
        Fp = Frame(P(-6.0, side * 8.9, 0), U, E * side)
        box(bm_for(part, "stone"), Fp, 0, 16.0, deck_z(0), deck_z(0) + 1.1, -0.5, 0)
        for k in range(5):
            box(bm_for(part, "stone"), Fp, k * 4.0 - 0.3, k * 4.0 + 0.3, deck_z(0), deck_z(0) + 1.35, -0.6, 0.05)

rnd = random.Random(1345)
bridge(f"ponte_vecchio_1345@1345-{NOW}")
terraces(f"ponte_vecchio_1345@1345-{NOW}")
for a, b in ((-46.0, -6.4), (10.4, 46.5)):
    shop_row(f"shops_west@1345-{NOW}", f"retrochetti_west@1600-{NOW}", -1, a, b, rnd, (15.8, 17.6))
    shop_row(f"shops_east@1345-1565", "", 1, a, b, random.Random(int(a) + 99), (15.0, 17.4), backs=False)   # before the corridor
    shop_row(f"shops_east_corridor@1565-{NOW}", f"retrochetti_east@1600-{NOW}", 1, a, b, rnd, (15.8, 17.6), east=True)
corridor(f"corridoio_vasariano@1565-{NOW}")
# Benvenuto Cellini bust on its fountain base at the centre of the west terrace (Raffaello Romanelli, 1901)
Fc = Frame(P(2.0, -6.5, 0), U, -E)
box(bm_for(f"cellini_bust@1901-{NOW}", "white"), Fc, -1.1, 1.1, deck_z(2), deck_z(2) + 2.6, -1.0, 0.8)
box(bm_for(f"cellini_bust@1901-{NOW}", "bronze"), Fc, -0.4, 0.4, deck_z(2) + 2.6, deck_z(2) + 3.5, -0.5, 0.3)

K.export("ponte_vecchio")
