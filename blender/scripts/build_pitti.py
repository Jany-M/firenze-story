"""Palazzo Pitti and the Palazzina della Meridiana – dated model (v1).

Run:  python pipeline/42_pitti.py   (once: footprint, LiDAR roof grid → blender/data/pitti.json)
      blender -b --python blender/scripts/build_pitti.py  →  web/public/models/landmarks/pitti.glb
Frame: absolute scene coordinates (Blender X = scene x, Blender Y = −scene z, Z = scene y); the app places it at [0, 0],
rot 0, ground 0. The palace frame: t along the piazza front from its south end (OSM, A = −472.1/784.1) to the north,
b into the palace, n towards the piazza.
Measured (LiDAR 2023 DSM, docs/landmarks/PITTI.md): front ≈201 m from t −14 to 187, 23 bays of ≈8.74 m; the central 13 bays
three storeys, roof ≈38.5 m above the piazza (17.0 m scene); the outer five bays a side two storeys, ≈26.5 m; front
block ≈24 m deep; the rest of the palace (courtyard wings, garden front, rondò, Meridiana) massed from a 1 m raster of
the DSM (landmark_mass.py).
Details from photographs (docs/materials): rough pietra forte rustication over the whole front, large round-arched windows
with rusticated voussoirs, a continuous balustraded balcony on each floor, the central portal; the lateral doors of the
1458 front become Ammannati's kneeling windows; the Ammannati courtyard with rusticated orders.
Dates: Luca Pitti's palace 1458 (7 bays, 3 storeys, three doors); bought by Eleonora di Toledo 1549–50; Ammannati
1558–70 (rear wings, courtyard, kneeling windows – shown from 1560); the front lengthened by Giulio Parigi from 1618 (north,
3 bays) and Alfonso Parigi from 1631 (south, 3 bays); the low outer bays finished in the 1640s (23 bays – shown from 1640,
*inferred*); rondò delle Carrozze (south) 1764–66 (Giuseppe Ruggieri) and rondò di Bacco (north) by 1783 (*inferred*;
Poccianti's final form in the 19th century); Palazzina della Meridiana begun 1776 (completed c. 1823).
"""
import os, sys, math, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from mathutils import Vector
from landmark_detail import *
K.reset()
MAT["stone"] = material("pietra_forte", "pietra_forte", (0.62, 0.5, 0.36), 0.85, 0.32, tint=(3.0, 2.85, 2.55))
MAT["rust"] = material("pitti_rustication", "pietra_forte", (0.58, 0.48, 0.36), 0.95, 0.22, tint=(2.75, 2.55, 2.25))
MAT["serena"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)
MAT["plaster"] = material("plaster_meridiana", "intonaco", (0.84, 0.74, 0.56), 0.9, 0.4, tint=(1.2, 0.95, 0.6))
MAT["iron"] = material("wrought_iron", None, (0.08, 0.08, 0.08), 0.6, metal=0.6)
MAT["loggia"] = material("plaster_loggia_yellow", "intonaco", (0.86, 0.7, 0.36), 0.9, 0.4, tint=(1.25, 1.0, 0.55))
MAT["piazza"] = material("piazza_pitti_ground", None, (0.45, 0.42, 0.38), 0.95)
MAT["wall"] = material("terrace_wall_rubble", "pietra_forte", (0.5, 0.42, 0.32), 0.95, 0.5, tint=(2.3, 2.1, 1.85))
NOW = K.NOW
D = json.load(open(os.path.join(ROOT, "blender", "data", "pitti.json"), encoding="utf-8"))
FR = D["frame"]; A = Vector((FR["A"][0], -FR["A"][1], 0)); DD = Vector((FR["d"][0], -FR["d"][1], 0)); NN = Vector((FR["n"][0], -FR["n"][1], 0))
G0 = FR["ground_front"]
Z = Vector((0, 0, 1))
def W(t, b, h=0.0): return A + DD * t - NN * b + Z * h            # palace frame → Blender
F_FRONT = Frame(A, DD, NN)                                        # u = t, v = height, n towards the piazza
BAY = 8.74; T_S, T_N = -14.0, 187.0
def bay_c(k): return T_S + (k + 0.5) * BAY
def section(k):
    if 8 <= k <= 14: return "nucleo", 1458
    if 15 <= k <= 17: return "parigi_nord", 1618
    if 5 <= k <= 7: return "parigi_sud", 1631
    return "ali_basse", 1640
def high(k): return 5 <= k <= 17
H_LOW, H_HIGH, DEPTH = G0 + 26.5, G0 + 38.5, 24.0
FL = [G0, G0 + 11.5, G0 + 24.5]                                   # ground floor, piano nobile, second floor

# ------------------------------------------------------------------ the rest of the palace: massed from the DSM raster
def phase_of(t, b, k):
    if k == "mer": return "meridiana", 1776
    if b < DEPTH: return None              # the front block, the end pavilions and the rondò are built by hand below (a 1 m
                                           # strip of DSM in front of the front – balconies, cornice – must not become a wall)
    if 25 <= t <= 150: return "ammannati", 1560
    return "retro", 1640
def raster():
    """The palace behind the front block: buildings massed from the DSM (landmark_mass.py) – hipped roofs at the measured
    heights, walls, cornices and windows; the form of each roof and window is *generic*."""
    from landmark_mass import massing
    g = D["grid"]; t0, b0, nt, nb = g["t0"], g["b0"], g["nt"], g["nb"]; cells = {}
    for j in range(nb):
        for i in range(nt):
            h = g["h"][j][i]
            if h is None: continue
            t, b = t0 + i + 0.5, b0 + j + 0.5
            ph = phase_of(t, b, g["k"][j][i])
            if ph is None: continue
            cells[(i, j)] = (ph, h, g["g"][j][i])
    massing(cells, t0, b0, W, DD, -NN, mat="stone", trim="stone", mat_of=lambda ph: "plaster" if ph[0] == "meridiana" else "stone",
            solid=lambda t, b: -1 <= b < DEPTH and T_S <= t <= T_N, win=(1.3, 2.4), floor=5.2, nowin=in_court)
def in_court(t, b):
    """True inside Ammannati's courtyard (its sides get their orders by hand)."""
    ring_ = max(D["inners"], key=lambda q: abs(sum(a[0] * c[1] - c[0] * a[1] for a, c in zip(q, q[1:] + q[:1]))))
    x = FR["A"][0] + FR["d"][0] * t - FR["n"][0] * b; z = FR["A"][1] + FR["d"][1] * t - FR["n"][1] * b
    c = False
    for i in range(len(ring_)):
        (xi, zi), (xj, zj) = ring_[i], ring_[i - 1]
        if (zi > z) != (zj > z) and x < (xj - xi) * (z - zi) / (zj - zi) + xi: c = not c
    return c

# ------------------------------------------------------------------ the piazza front
def rustication(part, F, u0, u1, v0, v1, seed, course=1.05, proud=(0.12, 0.32), holes=()):
    rnd = random.Random(seed); v = v0
    while v < v1 - 0.1:
        h = min(course * rnd.uniform(0.85, 1.15), v1 - v); u = u0 + (rnd.random() * 0.8 if rnd.random() < 0.5 else 0)
        while u < u1 - 0.05:
            ue = min(u + rnd.uniform(1.2, 2.8), u1)
            if not any(a - 0.05 < ue and u < b + 0.05 and c - 0.05 < v + h and v < dd + 0.05 for (a, b, c, dd) in holes):
                pbox(bm_for(part, "rust"), F, u + 0.04, ue - 0.04, v + 0.04, v + h - 0.04, 0, rnd.uniform(*proud))
            u = ue
        v += h

def arched_window(part, F, u, sill, w, spring, mat="rust", fill="glass"):
    r = w / 2
    arch_fill(part, fill, F, u - r, u + r, sill, spring, n=0.01)
    voussoirs(part, mat, F, u, spring, r, r + 1.1, n=13, proud=0.35)
    pbox(bm_for(part, "stone"), F, u - r - 0.3, u + r + 0.3, sill - 0.35, sill, 0, 0.45)

def balcony(part, F, u0, u1, v, proj=1.3):
    pbox(bm_for(part, "stone"), F, u0, u1, v - 0.35, v, 0, proj)
    n = int((u1 - u0) / 0.45)
    for q in range(n): cylinder(part, "stone", F.p(u0 + (q + 0.5) * (u1 - u0) / n, 0, proj - 0.2), 0.1, v, v + 0.9, seg=6)
    pbox(bm_for(part, "stone"), F, u0, u1, v + 0.9, v + 1.1, proj - 0.4, proj)

def front():
    for k in range(23):
        name, y = section(k); part = f"{name}@{y}-{NOW}"
        u0, u1 = T_S + k * BAY, T_S + (k + 1) * BAY; uc = (u0 + u1) / 2
        top = H_HIGH if high(k) else H_LOW
        box(bm_for(part, "stone"), F_FRONT, u0, u1, G0 - 1.0, top, -DEPTH, -0.02)
        holes = []
        # ground floor
        door = (k == 11); side_door = k in (9, 13)
        if door:
            holes.append((uc - 2.8, uc + 2.8, G0, G0 + 9.2)); arched_window(part, F_FRONT, uc, G0, 4.6, G0 + 6.6, fill="dark")
        elif side_door:
            holes.append((uc - 2.4, uc + 2.4, G0, G0 + 8.4))
            arched_window(f"porte_laterali@1458-1560", F_FRONT, uc, G0, 3.6, G0 + 5.8, fill="dark")
            kw = f"inginocchiate@1560-{NOW}"
            pbox(bm_for(kw, "rust"), F_FRONT, uc - 1.9, uc + 1.9, G0, G0 + 8.0, -0.1, 0.05)                    # walled up
            win_rect(kw, F_FRONT, uc, G0 + 3.2, G0 + 6.0, 1.8, frame="stone", fw=0.3, pediment="cornice", grille=True)
            for s in (-1, 1): pbox(bm_for(kw, "stone"), F_FRONT, uc + s * 1.15 - 0.2, uc + s * 1.15 + 0.2, G0 + 1.6, G0 + 3.0, 0, 0.6)   # consoles
        else:
            holes.append((uc - 2.6, uc + 2.6, G0 + 1.0, G0 + 9.0))
            voussoirs(part, "rust", F_FRONT, uc, G0 + 6.4, 2.0, 3.1, n=11, proud=0.3)                      # blind arch
            win_rect(part, F_FRONT, uc, G0 + 3.8, G0 + 5.6, 1.2, frame="stone", fw=0.22, grille=True)
        # piano nobile and second floor: large round-arched windows over a balustraded balcony
        holes.append((uc - 3.3, uc + 3.3, FL[1] + 1.4, FL[1] + 10.6))
        arched_window(part, F_FRONT, uc, FL[1] + 1.6, 4.0, FL[1] + 7.4)
        if high(k):
            holes.append((uc - 3.3, uc + 3.3, FL[2] + 1.4, FL[2] + 10.6))
            arched_window(part, F_FRONT, uc, FL[2] + 1.6, 4.0, FL[2] + 7.4)
        rustication(part, F_FRONT, u0, u1, G0 - 0.4, top - 1.2, seed=k, holes=holes)
        balcony(part, F_FRONT, u0, u1, FL[1] + 0.2)
        if high(k): balcony(part, F_FRONT, u0, u1, FL[2] + 0.2)
        else: balcony(part, F_FRONT, u0, u1, top - 0.2, proj=0.6)                                              # roof terrace
        pbox(bm_for(part, "stone"), F_FRONT, u0 - 0.02, u1 + 0.02, top - 1.2, top - 0.2, 0, 0.9)              # cornice
        poly(bm_for(part, "roof"), [F_FRONT.p(u0, top, -DEPTH), F_FRONT.p(u1, top, -DEPTH), F_FRONT.p(u1, top + 1.6, -DEPTH / 2), F_FRONT.p(u0, top + 1.6, -DEPTH / 2)])
        poly(bm_for(part, "roof"), [F_FRONT.p(u0, top, 0.6), F_FRONT.p(u1, top, 0.6), F_FRONT.p(u1, top + 1.6, -DEPTH / 2), F_FRONT.p(u0, top + 1.6, -DEPTH / 2)])


# ------------------------------------------------------------------ the two rondò, their terraces and the end pavilions
# DSM: the rondò arms 12–13 m high, t −14…0 (south, rondò delle Carrozze) and t 174…188 (north, rondò di Bacco), from b −10
# out to b −48; the end pavilions in front of the low wings (t −14…2 and 172…188, b −10…0) ≈25 m. LiDAR DTM: each rondò on
# a terrace ≈16.6 m (scene) above the street, t −22…9 (south) and 165…196 (north), b to −55, with a retaining wall down to
# the street (≈10 m) and to the piazza on its inner side. Photographs (Sailko 2009, rondò di Bacco): an arcade of seven round
# arches in rusticated pietra forte facing the piazza, one more arch on the end, the yellow-plastered loggia with doors
# behind, a balustraded roof terrace; the terrace wall of big rough blocks, battered, with stone bollards and an iron rail.
GR = D["ground"]
def gnd(t, b):
    i, j = t - GR["t0"], b - GR["b0"]; i0, j0 = int(math.floor(i)), int(math.floor(j))
    i0 = min(max(i0, 0), GR["nt"] - 2); j0 = min(max(j0, 0), GR["nb"] - 2); a, c = i - i0, j - j0
    h = GR["h"]
    return h[j0][i0] * (1 - a) * (1 - c) + h[j0][i0 + 1] * a * (1 - c) + h[j0 + 1][i0] * (1 - a) * c + h[j0 + 1][i0 + 1] * a * c
def face_t(t, bA, bB, out):
    """Wall at constant t over bA < bB; out = +1 faces +t. u from 0 to bB − bA."""
    return (Frame(W(t, bA), -NN, DD), bB - bA) if out > 0 else (Frame(W(t, bB), NN, -DD), bB - bA)
def face_b(b, tA, tB, out):
    """Wall at constant b over tA < tB; out = −1 faces the piazza (−b)."""
    return (Frame(W(tA, b), DD, NN), tB - tA) if out < 0 else (Frame(W(tB, b), -DD, -NN), tB - tA)
def balustrade(part, F, u0, u1, v, h=1.0, n0=0.0):
    pbox(bm_for(part, "stone"), F, u0, u1, v, v + 0.25, n0 - 0.5, n0)
    k = int((u1 - u0) / 0.42)
    for q in range(k): cylinder(part, "stone", F.p(u0 + (q + 0.5) * (u1 - u0) / k, 0, n0 - 0.25), 0.11, v + 0.25, v + h - 0.15, seg=6)
    pbox(bm_for(part, "stone"), F, u0, u1, v + h - 0.15, v + h, n0 - 0.55, n0 + 0.05)
def rondo(part, side):
    """side −1: the south rondò (t −14…0, the arcade on t = 0 facing +t); +1: the north one, mirrored round t = 87."""
    m = (lambda t: t) if side < 0 else (lambda t: 174.0 - t)
    tO, tI, tB = m(-14.0), m(0.0), m(-5.0)              # outer face, arcade face, back wall of the loggia
    lo, hi = min(tO, tI), max(tO, tI)
    b0, b1 = -48.0, -10.0
    zg = gnd(m(-7.0), -30.0) + 0.05; H = zg + 11.0
    io = 1 if tI > tO else -1                            # the arcade faces +t (south) or −t (north)
    # the solid part behind the loggia, the loggia's back wall, the arcade's piers and the band over the arches
    core0, core1 = (min(tO, tB), max(tO, tB))
    box(bm_for(part, "stone"), Frame(W(core0, b0), DD, -NN), 0, core1 - core0, zg - 1.0, H, 0, b1 - b0)
    Fl, Ll = face_t(tB, b0, b1, io); pbox(bm_for(part, "loggia"), Fl, 0, Ll, zg - 0.2, zg + 7.3, 0, 0.02)
    a0w, a1w = min(tB, tI), max(tB, tI)
    box(bm_for(part, "loggia"), Frame(W(a0w, b0), DD, -NN), 0, a1w - a0w, zg + 7.2, zg + 7.3, 0, b1 - b0)      # ceiling
    Fa, La = face_t(tI, b0, b1, io)
    W_ARCH, PIER = 3.0, 1.9; n_arch = 7
    # from the palace (b = −10) outwards: in face u, the palace end is u = La (south) or u = 0 (north)
    def u_of(b): return b - b0 if io > 0 else b1 - b
    arches = []
    for k in range(n_arch):
        bc = b1 - PIER - W_ARCH / 2 - k * (W_ARCH + PIER); arches.append(u_of(bc))
    end_solid = (min(u_of(b0), u_of(b0 + 2.2)), max(u_of(b0), u_of(b0 + 2.2)))
    edges = sorted([0.0, La] + [u - W_ARCH / 2 for u in arches] + [u + W_ARCH / 2 for u in arches])
    for q in range(0, len(edges), 2):                                                  # piers
        if edges[q + 1] - edges[q] > 0.05: box(bm_for(part, "stone"), Fa, edges[q], edges[q + 1], zg - 1.0, zg + 5.6, -1.2, 0.0)
    box(bm_for(part, "stone"), Fa, 0, La, zg + 5.6, H, -1.2, 0.0)                      # band over the arches
    for u in arches:
        arch_fill(part, "loggia", Fa, u - W_ARCH / 2, u + W_ARCH / 2, zg + 5.6, zg + 5.6, n=0.01)
        voussoirs(part, "rust", Fa, u, zg + 5.6, W_ARCH / 2, W_ARCH / 2 + 1.0, n=11, proud=0.3)
    for k, u in enumerate(arches):
        ub = (b0 + u) if io > 0 else (b1 - u)
        Fl2, _ = face_t(tB, b0, b1, io); ul = ub - b0 if io > 0 else b1 - ub
        if k % 2 == 0:
            poly(bm_for(part, "wood"), [Fl2.p(ul - 0.8, zg, 0.04), Fl2.p(ul + 0.8, zg, 0.04), Fl2.p(ul + 0.8, zg + 3.2, 0.04), Fl2.p(ul - 0.8, zg + 3.2, 0.04)])
            pbox(bm_for(part, "stone"), Fl2, ul - 1.0, ul + 1.0, zg + 3.2, zg + 3.45, 0, 0.1)
        win_rect(part, Fl2, ul, zg + 4.0, zg + 5.4, 1.0, frame="stone", fw=0.15, grille=True)
    rustication(part, Fa, 0, La, zg - 0.4, H - 1.0, seed=int(77 + side), holes=[(u - W_ARCH / 2 - 0.2, u + W_ARCH / 2 + 0.2, zg - 1, zg + 7.2) for u in arches])
    # the end facing the street: one big arch into the loggia; the outer face: rusticated, small barred windows
    Fe, Le = face_b(b0, lo, hi, -1)
    ue = (tI + tB) / 2 - lo
    arch_fill(part, "loggia", Fe, ue - 1.8, ue + 1.8, zg, zg + 6.2, n=0.01)
    voussoirs(part, "rust", Fe, ue, zg + 6.2, 1.8, 2.9, n=11, proud=0.3)
    rustication(part, Fe, 0, Le, zg - 0.4, H - 1.0, seed=int(91 + side), holes=[(ue - 2.0, ue + 2.0, zg - 1, zg + 8.2)])
    Fo, Lo = face_t(tO, b0, b1, -io)
    for k in range(5): win_rect(part, Fo, (k + 0.5) * Lo / 5, zg + 2.0, zg + 3.2, 0.9, frame="stone", fw=0.15, grille=True)
    rustication(part, Fo, 0, Lo, zg - 0.4, H - 1.0, seed=int(103 + side), holes=[((k + 0.5) * Lo / 5 - 0.7, (k + 0.5) * Lo / 5 + 0.7, zg + 1.7, zg + 3.6) for k in range(5)])
    # cornice and the balustrade round the roof terrace
    for Fx, Lx in ((Fa, La), (Fe, Le), (Fo, Lo)):
        pbox(bm_for(part, "stone"), Fx, -0.1, Lx + 0.1, H - 1.0, H, 0, 0.6)
        balustrade(part, Fx, 0, Lx, H, n0=0.4)
    box(bm_for(part, "stone"), Frame(W(lo, b0), DD, -NN), 0, hi - lo, H - 0.05, H + 0.02, 0, b1 - b0)            # terrace paving
def pavilion(part, side):
    """The end pavilion in front of the low wing (DSM ≈25 m): rusticated, arched windows on its free faces, a balustrade."""
    m = (lambda t: t) if side < 0 else (lambda t: 174.0 - t)
    lo, hi = sorted((m(-14.0), m(2.0))); b0, b1 = -10.0, 0.0
    zg = G0; H = G0 + 25.0
    box(bm_for(part, "stone"), Frame(W(lo, b0), DD, -NN), 0, hi - lo, zg - 1.0, H, 0, b1 - b0)
    io = 1 if side < 0 else -1
    Fi, Li = face_t(m(2.0), b0, b1, io)                                        # the face towards the middle of the piazza
    Fp, Lp = face_b(b0, lo, hi, -1)                                            # the face towards the piazza, over the rondò
    for (Fx, Lx, wins) in ((Fi, Li, [Li / 2]), (Fp, Lp, [Lp * 0.3, Lp * 0.7])):
        holes = []
        for u in wins:
            arched_window(part, Fx, u, FL[1] + 1.6, 3.4, FL[1] + 6.9); holes.append((u - 2.8, u + 2.8, FL[1] + 1.2, FL[1] + 10.0))
        if Fx is Fi:
            win_rect(part, Fx, Li / 2, zg + 3.6, zg + 5.4, 1.2, frame="stone", fw=0.22, grille=True); holes.append((Li / 2 - 1.0, Li / 2 + 1.0, zg + 3.2, zg + 5.8))
        rustication(part, Fx, 0, Lx, zg - 0.4, H - 1.2, seed=int(131 + side + len(wins)), holes=holes)
        pbox(bm_for(part, "stone"), Fx, -0.1, Lx + 0.1, H - 1.2, H - 0.2, 0, 0.8)
        balustrade(part, Fx, 0, Lx, H - 0.2, n0=0.5)
    poly(bm_for(part, "roof"), [W(lo, b0, H - 0.2), W(hi, b0, H - 0.2), W(hi, b1, H + 0.6), W(lo, b1, H + 0.6)])
def piazza(part):
    """The piazza's slope (LiDAR / the app's ground: ≈17.8 m at the palace down to ≈10.5 m at the street, ≈11 %) drawn in its
    own grey stone surface between the two terraces, down to a long stone kerb where it meets the street (photographs:
    Zairon 2023, Deror avi 2009)."""
    def edge(t):
        street = min(gnd(t, b) for b in range(-96, -60, 2))
        for b in range(-30, -96, -1):
            if gnd(t, b) < street + 0.5: return float(b)
        return -80.0
    T = [float(t) for t in range(12, 165, 3)]
    E = [edge(t) for t in T]
    nb_ = 24
    rows = [[W(t, e * k / nb_ - 0.0 * (1 - k / nb_), gnd(t, e * k / nb_) + 0.06) for k in range(nb_ + 1)] for t, e in zip(T, E)]
    bm = bm_for(part, "piazza")
    for i in range(len(T) - 1):
        for k in range(nb_):
            poly(bm, [rows[i][k], rows[i + 1][k], rows[i + 1][k + 1], rows[i][k + 1]][::-1])
    for (t0_, e0), (t1_, e1) in zip(zip(T, E), zip(T[1:], E[1:])):                          # the kerb
        a_, b_ = W(t0_, e0, gnd(t0_, e0)), W(t1_, e1, gnd(t1_, e1))
        for (n0, n1, h0, h1) in ((0.0, 0.0, -0.2, 0.22), (0.0, 0.5, 0.22, 0.22)):
            off0 = -NN * 0 + Vector((0, 0, 0)); d_ = (b_ - a_).normalized(); nrm = Vector((-d_.y, d_.x, 0))
            poly(bm_for(part, "stone"), [a_ + nrm * n0 + Z * h0, b_ + nrm * n0 + Z * h0, b_ + nrm * n1 + Z * h1, a_ + nrm * n1 + Z * h1])
def terrace_walls(part, side):
    """The retaining wall round the rondò's terrace: battered rough blocks, a coping, stone bollards and an iron rail."""
    m = (lambda t: t) if side < 0 else (lambda t: 174.0 - t)
    path = [(-11, -22), (-11, -31), (-16, -34.5), (-22, -38.5), (-22, -55), (3, -55)]
    path += [(3 + 6 * math.sin(math.radians(a)), -49 - 6 * math.cos(math.radians(a))) for a in range(15, 91, 15)]
    path += [(9, -36), (11, -28)]
    pts = [(m(t), b) for t, b in path]
    rnd = random.Random(7 + side)
    top_ref = gnd(m(-7.0), -40.0) + 0.05
    for (ta, ba), (tb, bb) in zip(pts, pts[1:]):
        L = math.hypot(tb - ta, bb - ba)
        if L < 0.3: continue
        dt, db = (tb - ta) / L, (bb - ba) / L
        # the outward normal: away from the terrace's middle
        cx, cb = m(-7.0), -40.0; nt_, nb_ = db, -dt
        mt, mb = (ta + tb) / 2, (ba + bb) / 2
        if (mt - cx) * nt_ + (mb - cb) * nb_ < 0: nt_, nb_ = -nt_, -nb_
        steps = max(1, int(L / 2.0))
        for q in range(steps):
            s0, s1 = q * L / steps, (q + 1) * L / steps
            t0_, b0_ = ta + dt * s0, ba + db * s0; t1_, b1_ = ta + dt * s1, ba + db * s1
            tm, bm_ = (t0_ + t1_) / 2, (b0_ + b1_) / 2
            top = max(top_ref - 0.15 * (1 if q % 2 else 0), gnd(tm - nt_ * 4, bm_ - nb_ * 4))
            low = min(gnd(tm + nt_ * 5, bm_ + nb_ * 5), top) - 1.0
            if top - low < 2.2: continue
            o = lambda t_, b_, h_, out=0.0: W(t_ + nt_ * out, b_ + nb_ * out, h_)
            batter = 0.08 * (top - low)
            # face (battered), top coping, back
            poly(bm_for(part, "wall"), [o(t0_, b0_, low, batter), o(t1_, b1_, low, batter), o(t1_, b1_, top, 0), o(t0_, b0_, top, 0)])
            poly(bm_for(part, "stone"), [o(t0_, b0_, top, 0.15), o(t1_, b1_, top, 0.15), o(t1_, b1_, top + 0.3, 0.15), o(t0_, b0_, top + 0.3, 0.15)])
            poly(bm_for(part, "stone"), [o(t0_, b0_, top + 0.3, 0.15), o(t1_, b1_, top + 0.3, 0.15), o(t1_, b1_, top + 0.3, -1.2), o(t0_, b0_, top + 0.3, -1.2)][::-1])
            poly(bm_for(part, "stone"), [o(t0_, b0_, low, -1.2), o(t1_, b1_, low, -1.2), o(t1_, b1_, top + 0.3, -1.2), o(t0_, b0_, top + 0.3, -1.2)][::-1])
            # big rough blocks proud of the face
            z = low + 0.2
            while z < top - 0.5:
                hh = rnd.uniform(0.7, 1.1); uu = rnd.uniform(0, 0.6)
                while uu < (s1 - s0) - 0.3:
                    ww = rnd.uniform(0.9, 1.7); ue = min(uu + ww, s1 - s0)
                    f0 = (z - low) / (top - low); ob = batter * (1 - f0) + 0.08
                    pa = (t0_ + dt * uu, b0_ + db * uu); pb = (t0_ + dt * ue, b0_ + db * ue)
                    poly(bm_for(part, "wall"), [o(pa[0], pa[1], z + 0.05, ob), o(pb[0], pb[1], z + 0.05, ob), o(pb[0], pb[1], z + hh - 0.05, ob - 0.06), o(pa[0], pa[1], z + hh - 0.05, ob - 0.06)])
                    uu = ue + 0.05
                z += hh
            # a bollard every ≈3 m, the iron rail between them
            if q % 2 == 0: cylinder(part, "stone", o(t0_, b0_, 0, -0.4), 0.2, top + 0.3, top + 1.0, seg=8)
            for zz in (top + 0.75,):
                a_, b_ = o(t0_, b0_, zz, -0.4), o(t1_, b1_, zz, -0.4)
                poly(bm_for(part, "iron"), [a_, b_, b_ + Vector((0, 0, 0.05)), a_ + Vector((0, 0, 0.05))])

# ------------------------------------------------------------------ Ammannati's courtyard
def courtyard():
    part = f"cortile_ammannati@1560-{NOW}"
    ring_ = max(D["inners"], key=lambda q: abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(q, q[1:] + q[:1]))))
    P = ring_[:-1] if ring_[0] == ring_[-1] else ring_
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(P, P[1:] + P[:1])); sg = 1 if area > 0 else -1
    cx = sum(p[0] for p in P) / len(P); cz = sum(p[1] for p in P) / len(P)
    g = G0 + 0.5
    for (ax, az), (bx, bz) in zip(P, P[1:] + P[:1]):
        L = math.dist((ax, az), (bx, bz))
        if L < 6: continue
        tx, tz = (bx - ax) / L, (bz - az) / L; nx, nz = -tz * sg, tx * sg                                       # pointing into the court
        if (cx - ax) * nx + (cz - az) * nz < 0: nx, nz = -nx, -nz
        F = Frame(Vector((ax, -az, 0)), Vector((tx, -tz, 0)), Vector((nx, -nz, 0)))
        # the wing behind this side, from the DSM 4 m back from the court: the orders stop where the wing stops (the garden
        # side is the low terrace towards the Boboli amphitheatre)
        mx, mz = (ax + bx) / 2 - nx * 4.0, (az + bz) / 2 - nz * 4.0
        t_ = (mx - FR["A"][0]) * FR["d"][0] + (mz - FR["A"][1]) * FR["d"][1]; b_ = -((mx - FR["A"][0]) * FR["n"][0] + (mz - FR["A"][1]) * FR["n"][1])
        gg = D["grid"]; ii, jj = int(t_ - gg["t0"]), int(b_ - gg["b0"])
        hb = gg["h"][jj][ii] if 0 <= jj < gg["nb"] and 0 <= ii < gg["nt"] and gg["h"][jj][ii] is not None else g
        if hb < g + 9.0: continue
        nb = max(1, round(L / 6.2)); bw = L / nb
        for q in range(nb):
            u = (q + 0.5) * bw
            arch_fill(part, "dark", F, u - bw * 0.32, u + bw * 0.32, g, g + 5.4, n=0.02)
            voussoirs(part, "rust", F, u, g + 5.4, bw * 0.32, bw * 0.32 + 0.9, n=9, proud=0.3)
            for s in (-1, 1):                                                                          # banded columns
                for v in range(5): pbox(bm_for(part, "rust"), F, u + s * bw * 0.5 - 0.55, u + s * bw * 0.5 + 0.55, g + v * 1.25, g + v * 1.25 + 0.8, 0, 0.55)
            if hb > g + 19.5: win_round(part, F, u, g + 13.6, g + 18.6, 1.7, frame="stone")
            if hb > g + 30.0: win_round(part, F, u, g + 24.8, g + 29.0, 1.5, frame="stone")
        for v in (g + 11.0, g + 22.0):
            if hb > v + 1.5: entablature(part, F, 0, L, v, mat="stone", h=1.0, proj=0.6)

raster()
front()
for sd, (nm, yr) in ((-1, ("rondo_carrozze", 1766)), (1, ("rondo_bacco", 1783))):
    rondo(f"{nm}@{yr}-{NOW}", sd)
    terrace_walls(f"{nm}_terrazza@{yr}-{NOW}", sd)
    pavilion(f"padiglione_{'sud' if sd < 0 else 'nord'}@1640-{NOW}", sd)
piazza(f"piazza_pitti@1640-{NOW}")
courtyard()
K.export("pitti")
