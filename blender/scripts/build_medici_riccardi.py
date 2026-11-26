"""Palazzo Medici Riccardi – dated model (v1).

Run:  blender -b --python blender/scripts/build_medici_riccardi.py  →  web/public/models/landmarks/medici_riccardi.glb
Frame: absolute scene coordinates (Blender X = scene x, Blender Y = −scene z); the app places it at [0, 0], rot 0, ground 8.0
(48.0 m a.s.l., Via Cavour / Via de' Gori). Outline: OSM relation 1379977; heights from the LiDAR 2023 DSM.
Measured: Via Cavour (Via Larga) front 76.3 m = 17 bays of 4.49 m (Michelozzo's 10 + the Riccardi's 7); Via de' Gori front of the
Michelozzo block ≈40 m (9 bays) then the garden wall to Via de' Ginori; cornice ≈25.5–27.6 m, roofs ≈28 m; courtyard ≈10 × 10 m open.
Details from photographs (docs/landmarks/MEDICI-RICCARDI.md, pictures in docs/materials): ground floor of huge rusticated
bosses with the stone bench (panca di via), the great round arches of the portals and of the corner loggia in radiating
voussoirs, small square windows high up, iron rings; piano nobile in flatter rustication, top floor smooth; string courses
with dentils; bifore under voussoir arches with a tondo between the lights; the great cornice on modillions; the Medici arms
at the corner; kneeling windows (1517) in the walled-up loggia arch; courtyard with arches on columns, sgraffito frieze with
tondi, bifore on the first floor and an open loggia on top; battlemented garden wall.
Dates (docs/landmarks/MEDICI-RICCARDI.md): begun c. 1444–45 for Cosimo il Vecchio (Michelozzo), works shown 1445–52, finished 1452
(the earlier of the 1452 / 1460 the sources give); corner loggia walled up 1517 with Michelangelo's kneeling windows; sold to the
Riccardi 1659; northward extension along Via Larga 1670–84 (Pier Maria Baldi; other sources: 1679–82 and 1687–89, or 1715) – shown
from 1689; before it, houses on the lot (conjectural).
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from mathutils import Vector, Matrix
from landmark_detail import *
K.reset()
MAT["stone"] = material("pietra_forte", "pietra_forte", (0.62, 0.5, 0.36), 0.85, 0.32, tint=(3.0, 2.85, 2.55))
MAT["boss"] = material("pietra_forte_boss", "pietra_forte", (0.58, 0.47, 0.34), 0.95, 0.5, tint=(2.8, 2.6, 2.3))
MAT["serena"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)
MAT["sgraffito"] = material("sgraffito_grey", None, (0.42, 0.43, 0.44), 0.9)
MAT["plaster"] = material("plaster_warm", None, (0.82, 0.74, 0.6), 0.9)
MAT["shade"] = material("stone_shade", "pietra_forte", (0.48, 0.38, 0.28), 0.9, 0.32, tint=(2.3, 2.1, 1.85))
MAT["iron"] = material("wrought_iron", None, (0.08, 0.08, 0.08), 0.6, metal=0.6)
MAT["lawn"] = material("lawn", None, (0.24, 0.38, 0.17), 0.95)
MAT["hedge"] = material("box_hedge", None, (0.12, 0.26, 0.1), 0.95)
NOW = K.NOW

C = Vector((40.4, 338.7, 0))                     # corner Via Cavour / Via de' Gori (scene 40.4 / −338.7)
CAV = Vector((0.402, 0.915, 0))                  # along Via Cavour, northwards
GOR = Vector((-0.912, 0.411, 0))                 # along Via de' Gori, westwards
def Q(a, g, z=0.0): return C + CAV * a + GOR * g + Vector((0, 0, z))
def blk(part, mat, a0, a1, g0, g1, z0, z1):
    box(bm_for(part, mat), Frame(Q(a0, g0), CAV, GOR), 0, a1 - a0, z0, z1, 0, g1 - g0)
def hip(part, a0, a1, g0, g1, z0, ridge, mat="roof"):
    bm = bm_for(part, mat); ins = min(a1 - a0, g1 - g0) / 2
    if a1 - a0 >= g1 - g0:
        gm = (g0 + g1) / 2
        poly(bm, [Q(a0, g0, z0), Q(a1, g0, z0), Q(a1 - ins, gm, ridge), Q(a0 + ins, gm, ridge)])
        poly(bm, [Q(a1, g1, z0), Q(a0, g1, z0), Q(a0 + ins, gm, ridge), Q(a1 - ins, gm, ridge)])
        poly(bm, [Q(a0, g1, z0), Q(a0, g0, z0), Q(a0 + ins, gm, ridge)]); poly(bm, [Q(a1, g0, z0), Q(a1, g1, z0), Q(a1 - ins, gm, ridge)])
    else:
        am = (a0 + a1) / 2
        poly(bm, [Q(a0, g1, z0), Q(a0, g0, z0), Q(am, g0 + ins, ridge), Q(am, g1 - ins, ridge)])
        poly(bm, [Q(a1, g0, z0), Q(a1, g1, z0), Q(am, g1 - ins, ridge), Q(am, g0 + ins, ridge)])
        poly(bm, [Q(a0, g0, z0), Q(a1, g0, z0), Q(am, g0 + ins, ridge)]); poly(bm, [Q(a1, g1, z0), Q(a0, g1, z0), Q(am, g1 - ins, ridge)])

BAY = 76.3 / 17
GF, NOB, TOP, CORN = 8.6, 16.8, 25.5, 27.6
DEPTH = 1.2                                       # thickness of the street wall (the blocks behind start at 1.2)

def rusticate(part, F, u0, u1, v0, v1, course, proud, length, seed, holes=(), boss=True):
    """Rusticated masonry: rows of blocks of irregular length; boss=True gives the bold cushioned bosses of the ground floor."""
    rnd = random.Random(seed); v = v0; row = 0
    while v < v1 - 0.05:
        h = min(course * rnd.uniform(0.85, 1.15), v1 - v); u = u0 - rnd.uniform(0, length[0]) * (row % 2)
        while u < u1 - 0.05:
            ue = min(u + rnd.uniform(*length), u1); us = max(u, u0)
            def hit(hl):
                if hl[0] == "arch":
                    _, uc, sp, R = hl
                    if us < uc + R and ue > uc - R and v < sp: return True
                    cu = min(max(uc, us), ue); cv = min(max(sp, v), v + h)
                    return (cu - uc) ** 2 + (cv - sp) ** 2 < R * R
                a, b, c, d = hl; return a < ue and us < b and c < v + h and v < d
            if not any(hit(hl) for hl in holes):
                p = rnd.uniform(*proud)
                box(bm_for(part, "stone"), F, us + 0.04, ue - 0.04, v + 0.04, v + h - 0.04, 0, p * (0.45 if boss else 1.0))
                if boss: box(bm_for(part, "boss"), F, us + 0.14, ue - 0.14, v + 0.12, v + h - 0.12, 0, p)
            u = ue
        v += h; row += 1

def voussoir_arch(part, F, uc, spring, r, depth, n=15, mat="stone", wedge=0.75):
    """Round arch of radiating voussoirs with its soffit through the wall."""
    voussoirs(part, mat, F, uc, spring, r, r + wedge, n=n, proud=0.5)
    ring(part, mat, F, uc, spring, r, r + 0.01, -depth, 0.0, seg=14)

def bifora(part, F, uc, v0, w=2.1, h=4.0):
    """Michelozzo's bifora: round-headed opening under a ring of voussoirs, two lights on a colonnette, a tondo in the lunette."""
    r = w / 2; spring = v0 + h - r
    arch_fill(part, "dark", F, uc - r, uc + r, v0, spring, n=0.04)
    voussoirs(part, "stone", F, uc, spring, r, r + 0.55, n=13, proud=0.14)
    pbox(bm_for(part, "stone"), F, uc - r - 0.12, uc - r, v0, spring, 0, 0.1); pbox(bm_for(part, "stone"), F, uc + r, uc + r + 0.12, v0, spring, 0, 0.1)
    cylinder(part, "serena", F.p(uc, 0, 0.12), 0.09, v0, spring - 0.15, seg=8)                          # colonnette
    box(bm_for(part, "serena"), F, uc - 0.18, uc + 0.18, spring - 0.3, spring - 0.12, 0.02, 0.24)
    for s_ in (-1, 1):                                                                                 # the two small arches
        ring(part, "serena", F, uc + s_ * r / 2, spring - 0.12, r / 2 - 0.06, r / 2 + 0.06, 0, 0.1, seg=8, soffit=False)
    oculus(part, F, uc, spring + r * 0.55, 0.22, frame="serena", fill="serena", fw=0.08)
    pbox(bm_for(part, "serena"), F, uc - r - 0.3, uc + r + 0.3, v0 - 0.18, v0, 0, 0.22)                  # sill

def string_course(part, F, L, v, dent=True):
    pbox(bm_for(part, "stone"), F, -0.1, L + 0.1, v - 0.2, v + 0.05, 0, 0.35)
    if dent:
        for k in range(int(L / 0.28)):
            u = 0.06 + k * 0.28; pbox(bm_for(part, "stone"), F, u, u + 0.14, v + 0.05, v + 0.25, 0, 0.42)
    pbox(bm_for(part, "stone"), F, -0.15, L + 0.15, v + 0.25, v + 0.45, 0, 0.55)

def great_cornice(part, F, L):
    """Michelozzo's cornice: architrave band, dentils, egg-and-dart, modillions, corona with a 2.7 m projection."""
    pbox(bm_for(part, "stone"), F, -0.1, L + 0.1, TOP - 0.4, TOP, 0, 0.3)
    for k in range(int(L / 0.3)):
        u = 0.05 + k * 0.3; pbox(bm_for(part, "stone"), F, u, u + 0.16, TOP, TOP + 0.28, 0, 0.55)               # dentils
    pbox(bm_for(part, "stone"), F, -0.2, L + 0.2, TOP + 0.28, TOP + 0.55, 0, 0.75)
    for k in range(int(L / 0.35)):
        sphere(part, "stone", F.p(0.1 + k * 0.35, TOP + 0.42, 0.78), 0.12)                                     # egg-and-dart
    for k in range(int(L / 0.75) + 1):
        u = 0.2 + k * 0.75; box(bm_for(part, "stone"), F, u, u + 0.3, TOP + 0.55, TOP + 1.35, 0, 2.2)          # modillions
    box(bm_for(part, "stone"), F, -0.6, L + 0.6, TOP + 1.35, TOP + 1.75, 0, 2.5)                              # corona
    box(bm_for(part, "stone"), F, -0.7, L + 0.7, TOP + 1.75, CORN, 0, 2.7)

def kneeling_window(part, F, uc, v0=0.0):
    """Michelangelo's finestra inginocchiata: window on consoles ('knees'), with sill, grille and a triangular pediment."""
    pbox(bm_for(part, "stone"), F, uc - 1.25, uc + 1.25, v0 + 0.4, v0 + 2.3, 0, 0.2)                          # apron
    for u in (uc - 1.15, uc + 0.85):
        box(bm_for(part, "stone"), F, u, u + 0.3, v0 + 0.5, v0 + 2.3, 0.2, 0.75)                            # consoles
    pbox(bm_for(part, "stone"), F, uc - 1.4, uc + 1.4, v0 + 2.3, v0 + 2.55, 0, 0.8)                           # sill
    poly(bm_for(part, "dark"), [F.p(uc - 0.95, v0 + 2.55, 0.25), F.p(uc + 0.95, v0 + 2.55, 0.25), F.p(uc + 0.95, v0 + 5.2, 0.25), F.p(uc - 0.95, v0 + 5.2, 0.25)])
    for (a, b) in ((uc - 1.2, uc - 0.95), (uc + 0.95, uc + 1.2)):
        pbox(bm_for(part, "stone"), F, a, b, v0 + 2.55, v0 + 5.2, 0, 0.35)
    for k in range(8):
        box(bm_for(part, "iron"), F, uc - 0.9 + k * 0.25, uc - 0.86 + k * 0.25, v0 + 2.6, v0 + 5.15, 0.3, 0.36)
    for k in range(5):
        box(bm_for(part, "iron"), F, uc - 0.95, uc + 0.95, v0 + 2.8 + k * 0.55, v0 + 2.84 + k * 0.55, 0.3, 0.37)
    pbox(bm_for(part, "stone"), F, uc - 1.3, uc + 1.3, v0 + 5.2, v0 + 5.5, 0, 0.45)
    poly(bm_for(part, "stone"), [F.p(uc - 1.45, v0 + 5.5, 0.45), F.p(uc + 1.45, v0 + 5.5, 0.45), F.p(uc, v0 + 6.3, 0.45)])

def square_window(part, F, uc, v0=5.0, w=0.95):
    poly(bm_for(part, "dark"), [F.p(uc - w / 2, v0, 0.3), F.p(uc + w / 2, v0, 0.3), F.p(uc + w / 2, v0 + w, 0.3), F.p(uc - w / 2, v0 + w, 0.3)])
    for (a, b, c, d) in ((uc - w / 2 - 0.2, uc - w / 2, v0, v0 + w), (uc + w / 2, uc + w / 2 + 0.2, v0, v0 + w), (uc - w / 2 - 0.2, uc + w / 2 + 0.2, v0 - 0.2, v0), (uc - w / 2 - 0.2, uc + w / 2 + 0.2, v0 + w, v0 + w + 0.2)):
        pbox(bm_for(part, "stone"), F, a, b, c, d, 0, 0.42)
    for k in range(4): box(bm_for(part, "iron"), F, uc - w / 2 + 0.1 + k * 0.25, uc - w / 2 + 0.14 + k * 0.25, v0, v0 + w, 0.35, 0.4)

ARCH = {"portal": (2.0, 4.4), "loggia": (2.9, 4.6)}          # radius, springing

def facade(part, F, n_bays, ground, seed):
    """Michelozzo's street front. ground: {bay index or u: 'portal' | 'loggia' | 'kneel' | 'sq'} for the ground floor."""
    L = n_bays * BAY
    ops = sorted(((i if isinstance(i, float) else (i + 0.5) * BAY), k) for i, k in ground.items())
    holes = []
    for uc, kind in ops:
        if kind in ARCH:
            r, sp = ARCH[kind]; holes.append(("arch", uc, sp, r + 0.8))
        elif kind == "kneel": holes.append((uc - 1.5, uc + 1.5, 0.4, 6.4))
        elif kind == "sq": holes.append((uc - 0.8, uc + 0.8, 4.7, 6.3))
    # the wall behind the facing stones, with the arched openings left open
    u = 0.0
    for uc, kind in ops:
        if kind not in ARCH: continue
        r, sp = ARCH[kind]
        box(bm_for(part, "stone"), F, u, uc - r, -1.0, TOP, -DEPTH, 0.0)
        box(bm_for(part, "stone"), F, uc - r, uc + r, sp + r, TOP, -DEPTH, 0.0)
        for s_ in (-1, 1):                                                                          # spandrel corners
            pts = [F.p(uc + s_ * r, sp, 0)] + [F.p(uc + s_ * r * math.cos(math.pi / 2 * k / 6), sp + r * math.sin(math.pi / 2 * k / 6), 0) for k in range(7)] + [F.p(uc + s_ * r, sp + r, 0)]
            poly(bm_for(part, "stone"), pts)
        poly(bm_for(part, "wood" if kind == "portal" else "dark"), [F.p(uc - r, 0, -DEPTH + 0.05), F.p(uc + r, 0, -DEPTH + 0.05)] +
             [F.p(uc + r * math.cos(math.pi * k / 12), sp + r * math.sin(math.pi * k / 12), -DEPTH + 0.05) for k in range(13)])
        voussoir_arch(part, F, uc, sp, r, DEPTH, n=15 if kind == "portal" else 17, wedge=0.85)
        u = uc + r
    box(bm_for(part, "stone"), F, u, L, -1.0, TOP, -DEPTH, 0.0)
    rusticate(part, F, 0, L, 0.6, GF - 0.2, 0.95, (0.3, 0.55), (1.0, 2.4), seed, holes, boss=True)
    for (a, b, c, d) in holes or [(L + 1, L + 2, 0, 0)]:
        pass
    bench = [(0.0, L)]
    for uc, kind in ops:
        if kind in ARCH:
            r = ARCH[kind][0]; nb = []
            for (a, b) in bench:
                if b <= uc - r or a >= uc + r: nb.append((a, b))
                else:
                    if a < uc - r: nb.append((a, uc - r))
                    if b > uc + r: nb.append((uc + r, b))
            bench = nb
    for (a, b) in bench: pbox(bm_for(part, "stone"), F, a, b, -1.0, 0.55, 0, 0.6)                      # the panca di via
    string_course(part, F, L, GF)
    holes2 = [((i + 0.5) * BAY - 1.45, (i + 0.5) * BAY + 1.45, NOB - 5.0, NOB - 0.4) for i in range(n_bays)]
    rusticate(part, F, 0, L, GF + 0.45, NOB - 0.2, 0.62, (0.06, 0.12), (1.0, 2.0), seed + 1, holes2, boss=False)
    string_course(part, F, L, NOB)
    for i in range(n_bays):
        bifora(part, F, (i + 0.5) * BAY, NOB - 4.6)
        bifora(part, F, (i + 0.5) * BAY, TOP - 5.0)
        if i % 2 == 0: box(bm_for(part, "iron"), F, (i + 0.5) * BAY + 1.9, (i + 0.5) * BAY + 2.05, 3.2, 3.5, 0.5, 0.75)   # iron rings
    great_cornice(part, F, L)
    for uc, kind in ops:
        if kind == "sq": square_window(part, F, uc)
        elif kind == "kneel": kneeling_window(part, F, uc)
    return L

# ---------------------------------------------------------------- the lot before the palace and the Riccardi lot (conjectural)
OLD = "houses_via_larga@1300-1445"
rnd = random.Random(1300)
for a0 in range(0, 44, 9):
    h = rnd.choice((11.0, 12.5, 14.0)); blk(OLD, "plaster", a0 + 0.3, a0 + 8.7, 0.3, 14, -1.0, h); hip(OLD, a0 + 0.1, a0 + 8.9, 0.1, 14.2, h, h + 2.5)
    F = Frame(Q(a0 + 0.3, 0.3), CAV, -GOR)
    for k in range(3):
        for v in (4.2, 7.6, 11.0)[: int(h / 3.6)]: win_rect(OLD, F, 1.4 + k * 2.8, v, v + 1.6, 0.8, frame="stone")
    win_round(OLD, F, 4.2, 0.0, 3.2, 2.2, frame="stone", fill="wood")
for g0 in range(14, 40, 9):
    blk(OLD, "plaster", 0.3, 12, g0 + 0.3, g0 + 8.7, -1.0, 12.0); hip(OLD, 0.1, 12.2, g0 + 0.1, g0 + 8.9, 12.0, 14.4)
    F = Frame(Q(0.3, g0 + 8.7), -GOR, -CAV)
    for k in range(3):
        for v in (4.2, 7.6): win_rect(OLD, F, 1.4 + k * 2.8, v, v + 1.6, 0.8, frame="stone")
RH = "houses_north@1300-1689"
for a0 in range(45, 76, 8):
    a1 = min(a0 + 7.7, 76.3); h = rnd.choice((12.5, 14.0, 15.5))
    blk(RH, "plaster", a0 + 0.3, a1, 0.3, 14, -1.0, h); hip(RH, a0 + 0.1, min(a0 + 7.9, 76.3), 0.1, 14.2, h, h + 2.5)
    F = Frame(Q(a0 + 0.3, 0.3), CAV, -GOR)
    for k in range(2):
        for v in (4.2, 7.6, 11.0): win_rect(RH, F, 1.8 + k * 3.4, v, v + 1.6, 0.8, frame="stone")
    win_round(RH, F, 3.6, 0.0, 3.2, 2.2, frame="stone", fill="wood")

# ---------------------------------------------------------------- Michelozzo's palace: works 1445–52, then finished (1452 or 1460 in the sources)
WK = "michelozzo_works@1445-1452"
for (a0, a1, g0, g1) in ((0, 44.9, 0, 13.0), (0, 13.0, 13.0, 40.0), (28.0, 44.9, 13.0, 40.0), (13.0, 28.0, 30.0, 40.0)):
    blk(WK, "stone", a0, a1, g0, g1, -1.0, NOB)
M = "michelozzo@1452-" + str(NOW)
for (a0, a1, g0, g1) in ((DEPTH, 44.9, DEPTH, 13.0), (DEPTH, 13.0, 13.0, 40.0), (28.0, 44.9, 13.0, 40.0), (13.0, 28.0, 30.0, 40.0)):
    blk(M, "stone", a0, a1, g0, g1, -1.0, TOP)
hip(M, -1.6, 44.9, -1.6, 13.0, CORN - 0.2, CORN + 1.8); hip(M, -1.6, 13.0, 13.0, 41.6, CORN - 0.2, CORN + 1.8)
hip(M, 28.0, 44.9, 13.0, 40.0, CORN - 0.6, CORN + 1.4); hip(M, 13.0, 28.0, 30.0, 41.6, CORN - 0.6, CORN + 1.4)
FC = Frame(Q(0, 0), CAV, -GOR)                       # Via Larga front: u from the corner northwards, n east (outward)
FG = Frame(Q(0, 40.0), -GOR, -CAV)                   # Via de' Gori front: u from the garden end towards the corner, n south
facade(M, FC, 10, {1.0 * BAY: "loggia", 4: "portal", 3: "sq", 6: "sq", 7: "sq", 8: "sq", 9: "sq"}, seed=1444)
facade(M, FG, 9, {0: "sq", 1: "sq", 2: "portal", 4: "sq", 5: "sq", 8.0 * BAY: "loggia"}, seed=1445)
# the corner loggia arches: open until 1517 (the arch and its vault are drawn by facade()), then walled with kneeling windows
LW = "corner_loggia_walled@1517-" + str(NOW)
for F, uc in ((FC, 1.0 * BAY), (FG, 8.0 * BAY)):
    r, sp = ARCH["loggia"]
    poly(bm_for(LW, "stone"), [F.p(uc - r, 0, -0.2), F.p(uc + r, 0, -0.2)] + [F.p(uc + r * math.cos(math.pi * k / 12), sp + r * math.sin(math.pi * k / 12), -0.2) for k in range(13)])
    kneeling_window(LW, Frame(F.o - F.n * 0.2, F.u, F.n), uc)
    pbox(bm_for(LW, "stone"), Frame(F.o - F.n * 0.2, F.u, F.n), uc - r, uc + r, -1.0, 0.55, 0, 0.6)     # bench across the infill
LO = "corner_loggia@1452-1517"
for F, uc in ((FC, 1.0 * BAY), (FG, 8.0 * BAY)):
    poly(bm_for(LO, "serena"), [F.p(uc - 2.9, 0.02, -0.1), F.p(uc + 2.9, 0.02, -0.1), F.p(uc + 2.9, 0.02, -DEPTH), F.p(uc - 2.9, 0.02, -DEPTH)])
# the Medici arms on the corner of the piano nobile (palle on a gilded field)
AR = "medici_arms@1452-" + str(NOW)
nB = (FC.n + FG.n).normalized(); uB = Vector((-nB.y, nB.x, 0))
Fs = Frame(Q(0, 0) + nB * 0.9, uB, nB)
box(bm_for(AR, "stone"), Fs, -1.5, 1.5, 9.4, 9.8, -0.9, 0.3)                                      # bracket
poly(bm_for(AR, "stone"), [Fs.p(-1.45, 9.8, 0.05), Fs.p(1.45, 9.8, 0.05), Fs.p(1.45, 13.4, 0.05), Fs.p(0.0, 14.2, 0.05), Fs.p(-1.45, 13.4, 0.05)])
poly(bm_for(AR, "gold"), [Fs.p(-1.2, 10.1, 0.12), Fs.p(1.2, 10.1, 0.12), Fs.p(1.2, 13.1, 0.12), Fs.p(0.0, 13.8, 0.12), Fs.p(-1.2, 13.1, 0.12)])
for (du, dv, m) in ((-0.65, 12.4, "red"), (0.65, 12.4, "red"), (-0.75, 11.5, "red"), (0.75, 11.5, "red"), (0.0, 10.6, "red"), (0.0, 13.0, "lead")):
    sphere(AR, m, Fs.p(du, dv, 0.3), 0.3)
cylinder(AR, "iron", Q(0, 0) + nB * 1.2, 0.05, 6.2, 8.0, seg=6)                                     # the corner lantern bracket
sphere(AR, "iron", Q(0, 0) + nB * 1.2 + Vector((0, 0, 8.3)), 0.35)
# courtyard: three arches a side on composite columns round a 10 × 10 m open well; sgraffito frieze with tondi, bifore on
# the first floor, windows on the second, an open loggia on top (photographs)
CY = "courtyard@1452-" + str(NOW)
A0, A1, G0, G1 = 15.5, 25.5, 17.0, 27.0
RING = ((13.0, 28.0, 13.0, G0), (13.0, 28.0, G1, 30.0), (13.0, A0, G0, G1), (A1, 28.0, G0, G1))
for (a0, a1, g0, g1) in RING: blk(CY, "plaster", a0, a1, g0, g1, 6.4, 20.5)                      # rooms over the galleries
SB = 1.4                                                                                          # the top loggia is set back
for (a0, a1, g0, g1) in ((13.0, 28.0, 13.0, G0 - SB), (13.0, 28.0, G1 + SB, 30.0), (13.0, A0 - SB, G0 - SB, G1 + SB), (A1 + SB, 28.0, G0 - SB, G1 + SB)):
    blk(CY, "plaster", a0, a1, g0, g1, 20.5, 24.5)
for (a0, a1, g0, g1) in RING: hip(CY, a0, a1, g0, g1, 24.5, 25.8)
CF = [(Frame(Q(A0, G0), CAV, GOR), A1 - A0), (Frame(Q(A1, G0), GOR, -CAV), G1 - G0), (Frame(Q(A1, G1), -CAV, -GOR), A1 - A0), (Frame(Q(A0, G1), -GOR, CAV), G1 - G0)]
for F, L in CF:                                                     # n points into the well
    bay = L / 3
    for k in range(4):
        cylinder(CY, "serena", F.p(k * bay, 0, 0.0), 0.3, 0.0, 4.6, seg=12)
        box(bm_for(CY, "serena"), F, k * bay - 0.45, k * bay + 0.45, 4.6, 5.1, -0.45, 0.45)              # composite capital
    for k in range(3):
        uc = (k + 0.5) * bay; r = bay / 2 - 0.3
        poly(bm_for(CY, "sgraffito"), [F.p(uc - bay / 2, 5.1, 0), F.p(uc - r, 5.1, 0)] +
             [F.p(uc - r * math.cos(math.pi * i / 10), 5.1 + r * math.sin(math.pi * i / 10), 0) for i in range(11)] +
             [F.p(uc + bay / 2, 5.1, 0), F.p(uc + bay / 2, 6.9, 0), F.p(uc - bay / 2, 6.9, 0)])
        ring(CY, "serena", F, uc, 5.1, r, r + 0.25, -0.5, 0.06, seg=10)
        poly(bm_for(CY, "dark"), [F.p(uc - r, 0, -2.4), F.p(uc + r, 0, -2.4), F.p(uc + r, 5.1, -2.4), F.p(uc - r, 5.1, -2.4)])
    pbox(bm_for(CY, "serena"), F, -0.1, L + 0.1, 6.9, 7.1, 0, 0.2)
    box(bm_for(CY, "sgraffito"), F, 0, L, 7.1, 8.6, -0.5, 0.02)                                        # frieze with tondi
    for k in range(4): oculus(CY, F, L / 8 * (2 * k + 1), 7.85, 0.45, frame="white", fill="white", fw=0.1)
    pbox(bm_for(CY, "serena"), F, -0.1, L + 0.1, 8.6, 8.85, 0, 0.25)
    box(bm_for(CY, "sgraffito"), F, 0, L, 8.85, 20.5, -0.5, 0.0)                                       # grey sgraffito walls
    for k in range(3): bifora(CY, F, (k + 0.5) * bay, 10.2, w=1.7, h=3.4)
    pbox(bm_for(CY, "serena"), F, -0.1, L + 0.1, 15.0, 15.25, 0, 0.2)
    for k in range(3): win_rect(CY, F, (k + 0.5) * bay, 16.4, 18.4, 1.2, frame="serena")
    pbox(bm_for(CY, "serena"), F, -0.1, L + 0.1, 20.5, 20.8, 0, 0.25)
    poly(bm_for(CY, "dark"), [F.p(0, 20.8, -SB), F.p(L, 20.8, -SB), F.p(L, 24.2, -SB), F.p(0, 24.2, -SB)])   # top loggia
    for k in range(4): cylinder(CY, "serena", F.p(k * bay, 0, -0.2), 0.16, 20.8, 24.2, seg=8)
    box(bm_for(CY, "serena"), F, -0.1, L + 0.1, 24.2, 24.5, -SB, 0.2)
poly(bm_for(CY, "stone"), [Q(A0, G0, 0.03), Q(A1, G0, 0.03), Q(A1, G1, 0.03), Q(A0, G1, 0.03)])
# garden behind the battlemented wall along Via de' Gori and Via de' Ginori, with its gate
GW = "garden_wall@1452-" + str(NOW)
blk(GW, "stone", 0, 0.8, 40.0, 54.3, -1.0, 7.0)
for i in range(int(14.3 / 1.4)):
    g = 40.4 + i * 1.4; blk(GW, "stone", 0, 0.8, g, g + 0.7, 7.0, 7.9)
Fgw = Frame(Q(0, 54.3), -GOR, -CAV)
voussoirs(GW, "stone", Fgw, 7.2, 2.6, 1.4, 2.0, n=11, proud=0.2)
arch_fill(GW, "wood", Fgw, 5.8, 8.6, 0.0, 2.6, n=0.05)
GN0, GN1 = Q(0.5, 54.3), Q(70.5, 69.6)
dG = (GN1 - GN0).normalized(); Fgn = Frame(GN0, dG, Vector((-dG.y, dG.x, 0)))
box(bm_for(GW, "stone"), Fgn, 0, 22.0, -1.0, 7.0, -0.8, 0)
for i in range(int(22.0 / 1.4)): box(bm_for(GW, "stone"), Fgn, 0.4 + i * 1.4, 1.1 + i * 1.4, 7.0, 7.9, -0.8, 0)
poly(bm_for(GW, "lawn"), [Q(13.0, 40.5, 0.03), Q(40.0, 40.5, 0.03), Q(40.0, 52.0, 0.03), Q(13.0, 52.0, 0.03)])
for (a, g) in ((18, 44), (26, 47), (34, 44), (22, 50), (31, 50)):
    cylinder(GW, "wood", Q(a, g), 0.18, 0, 2.2, seg=6); sphere(GW, "hedge", Q(a, g, 3.4), 1.6)

# ---------------------------------------------------------------- the Riccardi extension along Via Larga (shown from 1689)
RC = "riccardi@1689-" + str(NOW)
blk(RC, "stone", 44.9, 76.3, DEPTH, 14.0, -1.0, TOP); hip(RC, 44.9, 77.9, -1.6, 14.0, CORN - 0.2, CORN + 1.8)
blk(RC, "stone", 64.0, 76.3, 14.0, 42.0, -1.0, TOP - 2.0); hip(RC, 64.0, 76.3, 14.0, 42.0, TOP - 2.0, TOP)
blk(RC, "plaster", 44.9, 64.0, 30.0, 42.0, -1.0, TOP - 2.0); hip(RC, 44.9, 64.0, 30.0, 42.0, TOP - 2.0, TOP)
FR = Frame(Q(44.9, 0), CAV, -GOR)
facade(RC, FR, 7, {0: "kneel", 1: "kneel", 3: "portal", 5: "kneel", 6: "kneel"}, seed=1689)
FN = Frame(Q(76.3, 14.0), -GOR, CAV)                                                                    # north end (plain, stone windows)
for v in (4.0, 10.6, 18.6):
    for k in range(3): win_rect(RC, FN, 2.5 + k * 4.0, v, v + 2.4, 1.2, frame="stone", pediment="cornice")
# the Riccardi courtyard (Cortile dei Muli): windows on its four faces, an arcade on the ground floor of the street range
for F, L in ((Frame(Q(44.9, 14.0), CAV, GOR), 19.1), (Frame(Q(64.0, 14.0), GOR, -CAV), 16.0), (Frame(Q(64.0, 30.0), -CAV, -GOR), 19.1), (Frame(Q(44.9, 30.0), -GOR, CAV), 16.0)):
    m = int(L / 3.4)
    for k in range(m):
        uc = (k + 0.5) * L / m
        for v in (10.2, 17.6): win_rect(RC, F, uc, v, v + 2.3, 1.1, frame="serena", pediment="cornice")
        if F.u == CAV: win_round(RC, F, uc, 0.0, 4.6, 2.4, frame="serena", fill="dark")
        else: win_rect(RC, F, uc, 2.4, 4.4, 1.0, frame="serena", grille=True)
    pbox(bm_for(RC, "serena"), F, -0.1, L + 0.1, 8.0, 8.3, 0, 0.25)
poly(bm_for(RC, "stone"), [Q(44.9, 14.0, 0.03), Q(64.0, 14.0, 0.03), Q(64.0, 30.0, 0.03), Q(44.9, 30.0, 0.03)])
# Riccardi wing on Via de' Ginori (gallery and library), lower, plastered with stone windows
blk(RC, "plaster", 42.0, 70.0, 42.0, 60.0, -1.0, 20.0); hip(RC, 42.0, 70.0, 42.0, 60.0, 20.0, 22.5)
FGi = Frame(Q(42.0, 60.0), CAV, GOR)
for k in range(7):
    for v in (3.0, 8.6, 14.4): win_rect(RC, FGi, 2.0 + k * 4.0, v, v + 2.4, 1.2, frame="stone", pediment="cornice")
pbox(bm_for(RC, "stone"), FGi, -0.2, 28.2, 19.4, 20.0, 0, 0.6)

K.export("medici_riccardi")
