"""Vasari Corridor beyond Ponte Vecchio – dated model (v1). The stretch over the bridge is in build_ponte_vecchio.py.

Run:  python pipeline/41_corridoio.py   (once: centre lines and heights → blender/data/corridoio.json)
      blender -b --python blender/scripts/build_corridoio.py  →  web/public/models/landmarks/corridoio.glb
Frame: absolute scene coordinates (Blender X = scene x, Blender Y = −scene z, Z = scene y = elevation − 40 m); the app places
it at [0, 0], rot 0, ground 0.
Route (OSM relations 21744598–601, docs/landmarks/CORRIDOIO-VASARIANO.md): Palazzo Vecchio → overpass on Via della Ninna →
Uffizi (inside that model) → loggia on the Lungarno degli Archibusieri → Ponte Vecchio (bridge model) → round Torre dei
Mannelli on stone corbels → over Via de' Bardi → above the houses of Via de' Guicciardini → over the portico of Santa
Felicita → behind Palazzo Guicciardini → on a wall along the gardens to the Boboli end by the Grotta del Buontalenti.
Measured: roof height along the free-standing stretches from the LiDAR 2023 DSM (lower envelope, 41_corridoio.py), ground
from the app's terrain; Lungarno roof ≈22.6 m, Oltrarno eave 18.7–24.6 m (rising to Boboli).
Details from photographs (docs/materials): plastered walls, brick string courses, pietra serena frames; rectangular windows
towards the river and round oculi towards the city on the Lungarno; tall round arches on plain piers along the river;
pietra serena corbels round the tower; Santa Felicita portico of four arches on columns with the Arco dei Rossi; small
square windows and oculi above a row of corbels on the Boboli side.
Dates: built 12 March – 17 December 1565 (window frames 1568); Lungarno loggia closed into shops with overhangs towards
the river 1572, cleared after the 1864 flood (overhangs demolished 1884–85; shown until 1885); Via de' Bardi stretch
destroyed by the German mines on 4 August 1944, rebuilt by 1950 with an arch 4 m wider; Torre dei Mannelli first recorded
1249 ("nova"). Positions of the Via de' Bardi arches and of the Arco dei Rossi along the run are *inferred*.
"""
import os, sys, math, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from mathutils import Vector
from landmark_detail import *
K.reset()
MAT["corr"] = material("plaster_corridor", "intonaco", (0.86, 0.76, 0.58), 0.9, 0.4, tint=(1.25, 0.95, 0.55))   # as on the bridge
MAT["stone"] = material("pietra_forte", "pietra_forte", (0.62, 0.5, 0.36), 0.85, 0.32, tint=(3.0, 2.85, 2.55))
MAT["serena"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)
MAT["iron"] = material("wrought_iron", None, (0.08, 0.08, 0.08), 0.6, metal=0.6)
MAT["shop"] = material("plaster_shop", "intonaco", (0.74, 0.66, 0.52), 0.9, 0.4, tint=(1.0, 0.85, 0.6))
NOW = K.NOW
D = json.load(open(os.path.join(ROOT, "blender", "data", "corridoio.json"), encoding="utf-8"))
Z = Vector((0, 0, 1))
def V(x, z, h=0.0): return Vector((x, -z, h))
def D3(dx, dz): return Vector((dx, -dz, 0)).normalized()

def arch_curve(L, spring, rise, n=16):
    """Intrados from u = 0 to L: a semicircle, or a segmental arch when the rise is less than half the span.
    Returns the points and the centre (cu, cv) and radius of the circle."""
    h = L / 2
    if rise >= h - 1e-6:
        return [(h - h * math.cos(math.pi * q / n), spring + h * math.sin(math.pi * q / n)) for q in range(n + 1)], (h, spring), h
    R = (h * h + rise * rise) / (2 * rise); cv = spring + rise - R; a0 = math.asin(h / R)
    return [(h + R * math.sin(-a0 + 2 * a0 * q / n), cv + R * math.cos(-a0 + 2 * a0 * q / n)) for q in range(n + 1)], (h, cv), R

def arch_face(part, mat, F, L, spring, rise, top, band=0.32):
    """Wall face over an arch: spandrel from the intrados up to `top`, with a pietra serena archivolt."""
    pts, (cu, cv), R = arch_curve(L, spring, rise)
    poly(bm_for(part, mat), [F.p(0, spring, 0)] + [F.p(u, v, 0) for u, v in pts] + [F.p(L, top, 0), F.p(0, top, 0)])
    out = [(cu + (u - cu) * (R + band) / R, cv + (v - cv) * (R + band) / R) for u, v in pts]
    b = bm_for(part, "serena")
    for (a, c), (d, e) in zip(zip(pts, out), zip(pts[1:], out[1:])):
        poly(b, [F.p(a[0], a[1], 0.08), F.p(d[0], d[1], 0.08), F.p(e[0], e[1], 0.08), F.p(c[0], c[1], 0.08)])
    return pts

class Run:
    """A corridor run along a centre line: per point floor / eave / ground and arc length s. Side +1 is the normal
    (−dz, dx) of the direction of travel (on the Lungarno: the river; in Oltrarno: the street, then the north side)."""
    def __init__(s, pts, floor, eave, ground, W):
        s.P = [tuple(p) for p in pts]; s.F, s.E, s.G, s.W = list(floor), list(eave), list(ground), W
        s.S = [0.0]
        for a, b in zip(s.P, s.P[1:]): s.S.append(s.S[-1] + math.dist(a, b))
        s.T = []
        for i in range(len(s.P)):
            a, b = s.P[max(0, i - 1)], s.P[min(len(s.P) - 1, i + 1)]; L = math.dist(a, b) or 1
            s.T.append(((b[0] - a[0]) / L, (b[1] - a[1]) / L))
    def at(s, sv):
        """Sample at arc length sv: dict x, z, t (unit direction), f (floor), e (eave), g (ground)."""
        j = 0
        while j < len(s.S) - 2 and s.S[j + 1] < sv: j += 1
        t = min(1.0, max(0.0, (sv - s.S[j]) / max(1e-6, s.S[j + 1] - s.S[j]))); lp = lambda A: A[j] + (A[j + 1] - A[j]) * t
        L = math.dist(s.P[j], s.P[j + 1]) or 1
        return dict(s=sv, x=lp([p[0] for p in s.P]), z=lp([p[1] for p in s.P]), t=((s.P[j + 1][0] - s.P[j][0]) / L, (s.P[j + 1][1] - s.P[j][1]) / L),
                    f=lp(s.F), e=lp(s.E), g=lp(s.G))
    def samples(s, s0, s1):
        """Samples from s0 to s1: the ends interpolated, the centre-line points between them (mitred directions)."""
        out = [s.at(s0)]
        for i in range(len(s.S)):
            if s0 + 0.05 < s.S[i] < s1 - 0.05: out.append(dict(s=s.S[i], x=s.P[i][0], z=s.P[i][1], t=s.T[i], f=s.F[i], e=s.E[i], g=s.G[i]))
        return out + [s.at(s1)]
    def side(s, q, k, w=None):
        w = s.W / 2 if w is None else w; tx, tz = q["t"]; return (q["x"] - tz * k * w, q["z"] + tx * k * w)
    def frame(s, sv, k, w=None):
        q = s.at(sv); tx, tz = q["t"]; return Frame(V(*s.side(q, k, w)), D3(tx, tz), D3(-tz * k, tx * k))

def body(part, R, s0, s1, rect_side=1, oc_side=-1, spacing=4.6, cap0=False, cap1=False, sq=False):
    """The gallery: two plastered walls floor → eave, soffit, brick string course, cornice, tiled roof with a central ridge,
    pietra serena windows every `spacing` m: rectangular on rect_side, oculi on oc_side (sq = small square windows)."""
    Q = R.samples(s0, s1)
    for k in (1, -1):
        quad_strip(bm_for(part, "corr"), [V(*R.side(q, k), q["f"]) for q in Q], [V(*R.side(q, k), q["e"]) for q in Q])
        quad_strip(bm_for(part, "roof"), [V(*R.side(q, k, R.W / 2 + 0.45), q["e"] - 0.15) for q in Q], [V(q["x"], q["z"], q["e"] + 1.1) for q in Q])
    quad_strip(bm_for(part, "corr"), [V(*R.side(q, 1), q["f"]) for q in Q], [V(*R.side(q, -1), q["f"]) for q in Q])      # soffit
    for a, b in zip(Q, Q[1:]):
        L = b["s"] - a["s"]
        for k in (1, -1):
            Fk = R.frame(a["s"] + 1e-3, k)
            pbox(bm_for(part, "brick"), Fk, 0, L, a["f"] - 0.05, a["f"] + 0.3, 0, 0.12)                       # string course
            pbox(bm_for(part, "corr"), Fk, -0.02, L + 0.02, a["e"] - 0.45, a["e"] - 0.15, 0, 0.3)              # cornice
    for q, cap in ((Q[0], cap0), (Q[-1], cap1)):
        if cap:
            poly(bm_for(part, "corr"), [V(*R.side(q, 1), q["f"]), V(*R.side(q, -1), q["f"]), V(*R.side(q, -1), q["e"]), V(q["x"], q["z"], q["e"] + 1.1), V(*R.side(q, 1), q["e"])])
    n = max(1, int((s1 - s0) / spacing))
    for j in range(n):
        sv = s0 + (j + 0.5) * (s1 - s0) / n; q = R.at(sv); f, e = q["f"], q["e"]
        if rect_side:
            F = R.frame(sv, rect_side)
            if sq: win_rect(part, F, 0, e - 2.0, e - 1.1, 0.8, fw=0.14)
            else: win_rect(part, F, 0, f + 1.2, min(e - 0.8, f + 2.9), 1.0)
        if oc_side: oculus(part, R.frame(sv, oc_side), 0, (f + e) / 2 + 0.2, 0.42, fw=0.18)

def substructure(part, R, s0, s1, sides=(1, -1), openings=(), mat="corr", inset=None):
    """Wall from the ground up to the corridor floor on the given sides, except over the openings [(s0, s1, spring, rise)],
    which get arches (spandrel up to the floor, soffit through, serena archivolt, jambs). inset = {side: metres}."""
    inset = inset or {}
    for k in sides:
        w = R.W / 2 - inset.get(k, 0.0)
        cuts = sorted((o[0], o[1]) for o in openings)
        a = s0; free = []
        for c0, c1 in cuts:
            if c0 > a: free.append((a, min(c0, s1)))
            a = max(a, c1)
        if a < s1: free.append((a, s1))
        for fa, fb in free:
            Q = R.samples(fa, fb)
            quad_strip(bm_for(part, mat), [V(*R.side(q, k, w), q["g"] - 0.5) for q in Q], [V(*R.side(q, k, w), q["f"]) for q in Q])
    for op in openings:
        o0, o1, spring, rise = op[:4]; jambs = op[4] if len(op) > 4 else True
        qa, qb = R.at(o0), R.at(o1); L = math.dist((qa["x"], qa["z"]), (qb["x"], qb["z"]))
        tx, tz = (qb["x"] - qa["x"]) / L, (qb["z"] - qa["z"]) / L; top = min(qa["f"], qb["f"])
        for k in sides:
            w = R.W / 2 - inset.get(k, 0.0)
            F = Frame(V(qa["x"] - tz * k * w, qa["z"] + tx * k * w), D3(tx, tz), D3(-tz * k, tx * k))
            pts = arch_face(part, mat, F, L, spring, rise, top)
        Fm = Frame(V(qa["x"] + tz * R.W / 2, qa["z"] - tx * R.W / 2), D3(tx, tz), D3(-tz, tx))
        quad_strip(bm_for(part, mat), [Fm.p(u, v, 0) for u, v in pts], [Fm.p(u, v, R.W) for u, v in pts])                  # soffit
        ga = min(qa["g"], qb["g"]) - 0.5
        for u0, u1 in ((0, 0.25), (L - 0.25, L)) if jambs else ():                                                           # jambs
            box(bm_for(part, mat), Fm, u0, u1, ga, spring, 0.02, R.W - 0.02)

def corbels(part, R, s0, s1, k, step=1.25, drop=1.5, proj=0.9, mat="serena", arches=True):
    """Beccatelli: stepped stone corbels under the floor on side k, small arches between them."""
    n = max(1, int((s1 - s0) / step)); du = (s1 - s0) / n
    for j in range(n + 1):
        sv = s0 + j * du; F = R.frame(sv, k, R.W / 2 - proj); f = R.at(sv)["f"]
        for q in range(3):
            pbox(bm_for(part, mat), F, -0.22, 0.22, f - drop + q * drop / 3, f - drop + (q + 1) * drop / 3, 0, proj * (q + 1) / 3 + 0.02)
        if arches and j < n:
            ring(part, mat, R.frame(sv, k), du / 2, f - 0.55, du / 2 - 0.22, du / 2, -0.05, 0.08, seg=8, soffit=False)

# ------------------------------------------------------------------ Via della Ninna: overpass Uffizi ↔ Palazzo Vecchio
def ninna(part):
    N = D["ninna"]; (xa, za), (xb, zb) = N["pts"]; g = N["ground"]; W = N["width"]
    L = math.dist((xa, za), (xb, zb)); tx, tz = (xb - xa) / L, (zb - za) / L
    spring, f0, top = g + 8.0, g + 14.2, g + 20.6
    for k in (1, -1):
        F = Frame(V(xa - tz * k * W / 2, za + tx * k * W / 2), D3(tx, tz), D3(-tz * k, tx * k))
        pts = arch_face(part, "corr", F, L, spring, L / 2, f0, band=0.4)
        poly(bm_for(part, "corr"), [F.p(0, f0, 0), F.p(L, f0, 0), F.p(L, top, 0), F.p(0, top, 0)])
        pbox(bm_for(part, "serena"), F, -0.05, L + 0.05, f0 - 0.1, f0 + 0.3, 0, 0.18)                       # sill course
        for u in (L * 0.2, L * 0.5, L * 0.8): win_rect(part, F, u, f0 + 1.6, f0 + 3.9, 1.1, fw=0.2, pediment="cornice")
        entablature(part, F, -0.05, L + 0.05, top - 0.9, mat="serena", h=0.9, proj=0.55)
    Fm = Frame(V(xa + tz * W / 2, za - tx * W / 2), D3(tx, tz), D3(-tz, tx))
    quad_strip(bm_for(part, "corr"), [Fm.p(u, v, 0) for u, v in pts], [Fm.p(u, v, W) for u, v in pts])
    for k in (1, -1):
        o = (W / 2 + 0.5) * k
        poly(bm_for(part, "roof"), [V(xa - tz * o, za + tx * o, top), V(xb - tz * o, zb + tx * o, top), V(xb, zb, top + 1.3), V(xa, za, top + 1.3)])

# ------------------------------------------------------------------ Lungarno degli Archibusieri: loggia under the corridor
LUNG = {}
def lungarno():
    Lr, br = D["lungarno"], D["bridge"]
    T = Run(Lr["pts"], Lr["floor"], Lr["eave"], Lr["ground"], 6).T
    P = [(x - t[1] * 0.6, z + t[0] * 0.6) for (x, z), t in zip(Lr["pts"], T)]        # 0.6 m towards the river (the DSM ridge)
    d0 = (P[1][0] - P[0][0], P[1][1] - P[0][1]); L0 = math.hypot(*d0); d0 = (d0[0] / L0, d0[1] / L0)
    pn = br["north"]; ub = (0.446, -0.895)                                     # the bridge corridor, heading north
    den = ub[0] * d0[1] - ub[1] * d0[0]; t = ((P[0][0] - pn[0]) * d0[1] - (P[0][1] - pn[1]) * d0[0]) / den
    C = (pn[0] + ub[0] * t, pn[1] + ub[1] * t)                                 # the corner over the bridge head
    pts = [tuple(pn), C] + P[1:]
    fl = [br["floor"], br["floor"]] + Lr["floor"][1:]; ev = [br["eave"], br["eave"]] + Lr["eave"][1:]
    gr = [Lr["ground"][0]] * 2 + Lr["ground"][1:]
    R = Run(pts, fl, ev, gr, 6.0); sC, sEnd = R.S[1], R.S[-1]
    LUNG["run"] = R
    p = f"lungarno@1565-{NOW}"
    body(p, R, 0, sEnd, rect_side=1, oc_side=-1, spacing=4.75, cap1=True)
    nb = int((sEnd - sC - 2.0) / 4.75); bay = (sEnd - sC - 2.0) / nb
    ops = []
    for j in range(nb):
        a, b = sC + 1.0 + j * bay + 0.65, sC + 1.0 + (j + 1) * bay - 0.65; g = R.at((a + b) / 2)["g"]
        ops.append((a, b, g + 7.3, (b - a) / 2))
    substructure(p, R, sC, sEnd, openings=ops)
    substructure(p, R, 0, sC, openings=[(0.4, sC - 0.2, R.at(0)["g"] + 4.5, 9)])                            # over the bridge head
    Q = R.samples(sC, sEnd)                                                                                    # river face: stone plinth
    quad_strip(bm_for(p, "stone"), [V(*R.side(q, 1, R.W / 2 + 0.03), 2.6) for q in Q], [V(*R.side(q, 1, R.W / 2 + 0.03), q["g"] - 0.4) for q in Q])
    # 1572–1885: arches closed into shops (doors, small windows); rooms overhanging the river on struts
    rnd = random.Random(1572)
    for a, b, spring, rise in ops:
        r = (b - a) / 2; g = R.at(a)["g"]
        for k in (1, -1):
            F = R.frame(a, k)
            arch_fill("botteghe@1572-1885", "shop", F, 0, b - a, g - 0.4, spring, n=-0.25)
            pbox(bm_for("botteghe@1572-1885", "dark"), F, r - 0.6, r + 0.6, g, g + 2.4, -0.24, -0.2)
            pbox(bm_for("botteghe@1572-1885", "dark"), F, r - 0.35, r + 0.35, g + 3.4, g + 4.2, -0.24, -0.2)
        if rnd.random() < 0.8:
            F = R.frame(a, 1); d = rnd.uniform(1.6, 2.6); h0 = g - rnd.uniform(0.5, 1.5); h1 = h0 + rnd.uniform(3.0, 4.2)
            box(bm_for("sporti@1572-1885", rnd.choice(("shop", "corr"))), F, 0.15, b - a - 0.15, h0, h1, 0.03, d)
            poly(bm_for("sporti@1572-1885", "roof"), [F.p(0.05, h1 + 0.6, 0.03), F.p(b - a - 0.05, h1 + 0.6, 0.03), F.p(b - a - 0.05, h1, d + 0.3), F.p(0.05, h1, d + 0.3)])
            for u in (0.4, b - a - 0.6):
                box(bm_for("sporti@1572-1885", "wood"), F, u, u + 0.2, h0 - 2.2, h0, d - 0.4, d - 0.2)
                box(bm_for("sporti@1572-1885", "wood"), F, u, u + 0.2, h0 - 2.2, h0 - 1.9, 0.03, d - 0.2)

# ------------------------------------------------------------------ Oltrarno
O = D["oltrarno"]
RO = Run(O["pts"], O["floor"], O["eave"], O["ground"], 4.0)
SEND = RO.S[-1]
# stretches along the run (arc length s from the end of the bridge corridor, m), from the DSM profile and the photographs
S_TOWER = (2.0, 24.0)         # round Torre dei Mannelli on corbels
S_BARDI = (24.0, 56.0)        # over Via de' Bardi: destroyed 4 Aug 1944, rebuilt by 1950 (arch 4 m wider)
S_FELIC = (124.0, 152.0)      # Arco dei Rossi + portico of Santa Felicita
S_GARDEN = (195.0, SEND)      # on a wall along the gardens to Boboli
D1944 = "1944_217"            # 4 August 1944
# Santa Felicita: portico ≈6.6 m to the corridor floor, corridor storey ≈4 m (photographs; the DSM gives ≈10.9 m in all)
for i, sv in enumerate(RO.S):
    w = max(0.0, min(1.0, (min(sv - S_FELIC[0], S_FELIC[1] - sv) + 6) / 6))
    if w > 0:
        RO.F[i] = RO.F[i] * (1 - w) + (RO.G[i] + 6.6) * w; RO.E[i] = RO.E[i] * (1 - w) + (RO.G[i] + 10.6) * w

def oltrarno_common():
    p = f"corridoio_oltrarno@1565-{NOW}"
    body(p, RO, 0, S_BARDI[0], rect_side=1, oc_side=-1, spacing=4.4)
    body(p, RO, S_BARDI[1], S_GARDEN[0], rect_side=1, oc_side=-1, spacing=4.6)
    body(p, RO, S_GARDEN[0], SEND, rect_side=-1, oc_side=1, spacing=4.2, cap1=True, sq=True)
    corbels(p, RO, S_TOWER[0] + 6.0, S_TOWER[1], 1)                         # round the tower, street side
    # Santa Felicita: Arco dei Rossi over the lane, then the portico of four arches on columns towards the piazza (+1);
    # the church front behind (−1)
    a0, a1 = S_FELIC; g = lambda sv: RO.at(sv)["g"]
    arco = (a0 + 0.4, a0 + 6.0, g(a0) + 3.3, 2.8)
    port = [(a0 + 6.8 + j * 5.2, a0 + 6.8 + (j + 1) * 5.2) for j in range(4)]                  # contiguous: columns between
    substructure(p, RO, a0, a1, sides=(1,), openings=[arco] + [(a, b, g(a) + 3.9, 2.6, False) for a, b in port])
    substructure(p, RO, a0, a1, sides=(-1,), openings=[arco])
    for j in range(len(port) + 1):                                                    # columns between the arches
        sv = port[j][0] if j < len(port) else port[-1][1]
        q = RO.at(sv); tx, tz = q["t"]; c = V(q["x"] - tz * (RO.W / 2 - 0.3), q["z"] + tx * (RO.W / 2 - 0.3)); gg = q["g"]
        cylinder(p, "serena", c, 0.36, gg - 0.3, gg + 0.3, seg=12)
        cylinder(p, "serena", c, 0.27, gg + 0.3, gg + 3.6, seg=12)
        cylinder(p, "serena", c, 0.38, gg + 3.6, gg + 3.9, seg=12)
    # gardens: the corridor on a wall set back 0.45 m on the garden side (−1), carried on a row of plastered corbels
    substructure(p, RO, S_GARDEN[0], SEND, inset={-1: 0.45})
    corbels(p, RO, S_GARDEN[0] + 1.0, SEND - 1.0, -1, step=1.6, drop=0.9, proj=0.45, mat="corr", arches=False)
    # elsewhere the city model's own houses stand under it

def bardi(part, wide):
    """Via de' Bardi stretch on two arches: on the street 8 m, 12 m and flatter after the 1950 rebuilding (inferred places)."""
    s0, s1 = S_BARDI
    body(part, RO, s0, s1, rect_side=1, oc_side=-1, spacing=4.4)
    g = lambda sv: RO.at(sv)["g"]
    main = (31.0, 43.0, g(31.0) + 4.2, 3.4) if wide else (33.0, 41.0, g(33.0) + 5.0, 4.0)
    substructure(part, RO, s0, s1, openings=[main, (45.5, 52.0, g(45.5) + 4.0, 3.25)])
    for sv in (27.0, 54.0):
        q = RO.at(sv); win_rect(part, RO.frame(sv, 1), 0, q["f"] - 3.6, q["f"] - 1.6, 0.9)

def mannelli(part):
    """Torre dei Mannelli (first recorded 1249): filaretto stone, small arched openings, a later top floor under deep eaves."""
    c = (-168.6, 482.2); ub = D3(-0.446, 0.895); eb = D3(0.895, 0.446); g, H, h = 7.4, 31.4, 3.5
    o = V(*c) - ub * h - eb * h
    for F in (Frame(o, eb, -ub), Frame(o + eb * 2 * h, ub, eb), Frame(o + eb * 2 * h + ub * 2 * h, -eb, ub), Frame(o + ub * 2 * h, -ub, -eb)):
        L = 2 * h
        box(bm_for(part, "stone"), F, 0, L, g - 0.5, H, -0.8, 0)
        for v in (12.0, 17.5, 23.0): win_round(part, F, L / 2, g + v, g + v + 1.6, 0.8, frame="stone")
        pbox(bm_for(part, "brick"), F, -0.1, L + 0.1, H - 0.1, H + 0.25, 0, 0.3)
        box(bm_for(part, "brick"), F, 0.4, L - 0.4, H + 0.25, H + 2.6, -0.6, 0)                     # top floor (belvedere)
        for q in range(3): pbox(bm_for(part, "dark"), F, 0.9 + q * (L - 1.8) / 3, 0.9 + q * (L - 1.8) / 3 + 0.9, H + 0.9, H + 2.0, 0, 0.03)
    top = H + 2.6; e = 1.3
    q = [o - ub * e - eb * e, o + eb * (2 * h + e) - ub * e, o + eb * (2 * h + e) + ub * (2 * h + e), o + ub * (2 * h + e) - eb * e]
    apex = V(*c) + Z * (top + 1.5)
    for a, b in zip(q, q[1:] + q[:1]):
        poly(bm_for(part, "roof"), [a + Z * top, b + Z * top, apex])
        poly(bm_for(part, "wood"), [a + Z * (top - 0.25), b + Z * (top - 0.25), b + Z * top, a + Z * top])

def uffizi_west(part):
    """The Uffizi's west end on the Lungarno, where the corridor comes out of the gallery and down to the loggia: the wedge of
    OSM way 477279033 west of the Uffizi model (the model's own wings stop at its west wing). LiDAR roof ≈38 m."""
    P = [(-10.4, 405.7), (-18.0, 401.0), (-21.9, 398.6), (-29.8, 413.7), (-32.0, 418.0), (-26.5, 420.5), (-19.0, 423.8), (1.3, 435.5)]
    g, top = 7.4, 37.4
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(P, P[1:] + P[:1]))
    sg = 1 if area > 0 else -1
    for (ax, az), (bx, bz) in zip(P, P[1:] + P[:1]):
        L = math.dist((ax, az), (bx, bz)); tx, tz = (bx - ax) / L, (bz - az) / L
        nx, nz = tz * sg, -tx * sg                                                  # outward (scene x/z)
        F = Frame(V(ax, az), D3(tx, tz), D3(nx, nz))
        poly(bm_for(part, "corr"), [F.p(0, g - 0.5, 0), F.p(L, g - 0.5, 0), F.p(L, top, 0), F.p(0, top, 0)])
        river = abs(nz) > 0.5 and nz > 0                                            # the Lungarno side
        n = int(L / 3.8)
        for k in range(n):
            u = (k + 0.5) * L / n
            if river and k % 2 == 0: arch_fill(part, "dark", F, u - 1.3, u + 1.3, g, g + 3.6, n=0.04); ring(part, "serena", F, u, g + 3.6, 1.3, 1.6, 0, 0.08, seg=10, soffit=False)
            elif not river: win_rect(part, F, u, g + 2.2, g + 3.6, 0.8, grille=True)
            for v in (8.6, 13.6, 18.6, 23.6, 28.0): win_rect(part, F, u, g + v, g + v + (2.2 if v < 20 else 1.6), 1.0, pediment="cornice" if v == 8.6 else None)
        if L > 1.0:
            for v in (7.6, 12.6): pbox(bm_for(part, "serena"), F, 0, L, g + v, g + v + 0.25, 0, 0.18)
            entablature(part, F, -0.1, L + 0.1, top - 1.0, mat="serena", h=1.0, proj=0.9)
    poly(bm_for(part, "roof"), [V(x, z, top + 0.6) for x, z in P])

uffizi_west(f"uffizi_ponente@1565-{NOW}")
ninna(f"cavalcavia_ninna@1565-{NOW}")
lungarno()
oltrarno_common()
bardi(f"corridoio_bardi@1565-{D1944}", wide=False)
bardi(f"corridoio_bardi_1950@1950-{NOW}", wide=True)
mannelli(f"mannelli@1249-{NOW}")
K.export("corridoio")
# the corridor's footprint and floor for the app: city buildings the corridor runs through are cut open above its floor
# (web/src/scene/city.ts setCorridorCut), so its whole path shows where LiDAR houses would hide it
def path(R): return {"pts": [[round(x, 2), round(z, 2)] for x, z in R.P], "floor": [round(v, 2) for v in R.F], "eave": [round(v, 2) for v in R.E], "w": R.W}
json.dump({"from": 1565, "runs": [path(RO), path(LUNG["run"])]}, open(os.path.join(K.OUT, "corridoio_path.json"), "w", newline="\n"))
