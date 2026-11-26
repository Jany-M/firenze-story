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
    if b < -1: return ("rondo_carrozze", 1765) if t < 86 else ("rondo_bacco", 1783)
    if b < DEPTH: return None                                     # the front block is built by hand below
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
    arch_fill(part, fill, F, u - r, u + r, sill, spring, n=-0.15)
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
courtyard()
K.export("pitti")
