"""Palazzo Strozzi – dated model (v1).

Run:  python pipeline/43_centro.py   (once: outline, ground, LiDAR → blender/data/centro.json)
      blender -b --python blender/scripts/build_strozzi.py  →  web/public/models/landmarks/strozzi.glb
Frame: absolute scene coordinates (Blender X = scene x, Blender Y = −scene z, Z = scene y); placed at [0, 0], rot 0, ground 0.
Measured: OSM relation 2951949 – ≈57 × 44 m, courtyard in the middle; LiDAR roof ≈40–41.5 m (scene), ground ≈7.8 m, so the
cornice top ≈33 m above the street. Storeys (*inferred* from photographs and the DSM): ground floor to 12.4 m, piano nobile
to 21.2 m, second floor to 29.6 m, cornice to 33.2 m.
Details from photographs (docs/materials): uniform rustication tapering upwards, rectangular barred windows on the ground
floor, two orders of bifore under voussoir arches, a round-arched portal in the middle of each street front (Via Strozzi,
Piazza Strozzi, Via Tornabuoni), Caparra's iron lanterns on the corners, rings and torch holders, the stone bench along the
base, Cronaca's great cornice on the north and east fronts and half of the west front.
Dates (docs/landmarks/STROZZI.md): foundation stone 6 August 1489; Cronaca directs the works 1490–1504 (cornice 1502,
courtyard 1503); ironwork 1491–98; works stop 1538 with the south front and half the Tornabuoni cornice unfinished; the
west cornice completed 1938–40; the stone bench by Poggi 1863–65. The ground floor shown from 1489, the piano nobile from
1495 (*inferred*), the second floor and cornice from 1502.
"""
import os, sys, math, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from mathutils import Vector
from landmark_detail import *
K.reset()
MAT["stone"] = material("pietra_forte", "pietra_forte", (0.62, 0.5, 0.36), 0.85, 0.32, tint=(3.0, 2.85, 2.55))
MAT["boss"] = material("pietra_forte_boss", "pietra_forte", (0.6, 0.49, 0.36), 0.9, 0.32, tint=(2.85, 2.7, 2.4))
MAT["serena"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)
MAT["iron"] = material("wrought_iron", None, (0.08, 0.08, 0.08), 0.6, metal=0.6)
NOW = K.NOW
D = json.load(open(os.path.join(ROOT, "blender", "data", "centro.json"), encoding="utf-8"))["strozzi"]
P = D["pts"][:-1] if D["pts"][0] == D["pts"][-1] else D["pts"]
G = max(D["ground"]) + 0.05
H1, H2, H3, TOP = G + 12.4, G + 21.2, G + 29.6, G + 29.6
CORN = TOP + 3.6
Z = Vector((0, 0, 1))
def V(x, z, h=0.0): return Vector((x, -z, h))
# the four fronts from the outline's corners (NW −301.4/45.4, NE −244.4/43.2, SE −242.7/87.1, SW −299.7/89.3)
NW, NE, SE, SW = (-301.4, 45.4), (-244.4, 43.2), (-242.7, 87.1), (-299.7, 89.3)
def front(a, b):
    L = math.dist(a, b); tx, tz = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    cx, cz = sum(p[0] for p in (NW, NE, SE, SW)) / 4, sum(p[1] for p in (NW, NE, SE, SW)) / 4
    nx, nz = -tz, tx
    if (a[0] - cx) * nx + (a[1] - cz) * nz < 0: nx, nz = -nx, -nz
    return Frame(V(*a), Vector((tx, -tz, 0)), Vector((nx, -nz, 0))), L
FRONTS = {"north": front(NW, NE), "east": front(NE, SE), "south": front(SE, SW), "west": front(SW, NW)}
BAYS = {"north": 13, "east": 9, "south": 13, "west": 9}

def rusticate(part, F, u0, u1, v0, v1, course, proud, length, seed, holes=()):
    rnd = random.Random(seed); v = v0; row = 0
    while v < v1 - 0.05:
        h = min(course * rnd.uniform(0.9, 1.1), v1 - v); u = u0 - rnd.uniform(0, length[0]) * (row % 2)
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
                box(bm_for(part, "stone"), F, us + 0.04, ue - 0.04, v + 0.04, v + h - 0.04, 0, p * 0.5)
                box(bm_for(part, "boss"), F, us + 0.12, ue - 0.12, v + 0.1, v + h - 0.1, 0, p)
            u = ue
        v += h; row += 1

def bifora(part, F, uc, v0, w=1.9, h=4.2):
    r = w / 2; spring = v0 + h - r
    arch_fill(part, "dark", F, uc - r, uc + r, v0, spring, n=0.04)
    voussoirs(part, "stone", F, uc, spring, r, r + 0.6, n=13, proud=0.18)
    cylinder(part, "serena", F.p(uc, 0, 0.12), 0.08, v0, spring - 0.15, seg=8)
    for s_ in (-1, 1): ring(part, "serena", F, uc + s_ * r / 2, spring - 0.12, r / 2 - 0.06, r / 2 + 0.05, 0, 0.1, seg=8, soffit=False)
    oculus(part, F, uc, spring + r * 0.55, 0.2, frame="serena", fill="serena", fw=0.07)
    pbox(bm_for(part, "stone"), F, uc - r - 0.3, uc + r + 0.3, v0 - 0.2, v0, 0, 0.3)

def string_course(part, F, L, v):
    pbox(bm_for(part, "stone"), F, -0.05, L + 0.05, v - 0.15, v + 0.1, 0, 0.3)
    for k in range(int(L / 0.3)):
        u = 0.06 + k * 0.3; pbox(bm_for(part, "stone"), F, u, u + 0.15, v + 0.1, v + 0.28, 0, 0.36)
    pbox(bm_for(part, "stone"), F, -0.1, L + 0.1, v + 0.28, v + 0.5, 0, 0.5)

def great_cornice(part, F, u0, u1):
    pbox(bm_for(part, "stone"), F, u0, u1, TOP, TOP + 0.5, 0, 0.3)
    for k in range(int((u1 - u0) / 0.32)):
        u = u0 + 0.05 + k * 0.32; pbox(bm_for(part, "stone"), F, u, u + 0.17, TOP + 0.5, TOP + 0.8, 0, 0.55)
    pbox(bm_for(part, "stone"), F, u0 - 0.1, u1 + 0.1, TOP + 0.8, TOP + 1.1, 0, 0.8)
    for k in range(int((u1 - u0) / 0.8) + 1):
        u = u0 + 0.2 + k * 0.8; box(bm_for(part, "stone"), F, u, u + 0.32, TOP + 1.1, TOP + 2.2, 0, 2.3)
    box(bm_for(part, "stone"), F, u0 - 0.4, u1 + 0.4, TOP + 2.2, TOP + 2.8, 0, 2.5)
    box(bm_for(part, "stone"), F, u0 - 0.5, u1 + 0.5, TOP + 2.8, CORN, 0, 2.65)

def lantern(part, F, u, v):
    """Caparra's wrought-iron corner lantern on its bracket."""
    box(bm_for(part, "iron"), F, u - 0.06, u + 0.06, v - 0.8, v, 0, 1.1)
    cylinder(part, "iron", F.p(u, 0, 1.3), 0.32, v - 0.2, v + 1.3, seg=8)
    cone(part, "iron", F.p(u, 0, 1.3), 0.4, 0.05, v + 1.3, v + 2.1, seg=8)

def finished_front(side, F, L, parts, portal=True, bench=True):
    """A finished front: rusticated ground floor with barred windows (and the portal), two orders of bifore."""
    nb = BAYS[side]; bay = L / nb; p0, p1, p2 = parts
    pk = nb // 2 if portal else -1
    box(bm_for(p0, "stone"), F, 0, L, G - 1.5, H1, -1.6, -0.02)
    holes = []
    for k in range(nb):
        uc = (k + 0.5) * bay
        if k == pk:
            holes.append(("arch", uc, G + 5.4, 3.4))
            arch_fill(p0, "dark", F, uc - 2.0, uc + 2.0, G, G + 5.4, n=0.03)
            voussoirs(p0, "stone", F, uc, G + 5.4, 2.0, 3.3, n=15, proud=0.45)
        else:
            holes.append((uc - 0.85, uc + 0.85, G + 6.6, G + 8.6))
            poly(bm_for(p0, "dark"), [F.p(uc - 0.55, G + 6.9, 0.3), F.p(uc + 0.55, G + 6.9, 0.3), F.p(uc + 0.55, G + 8.3, 0.3), F.p(uc - 0.55, G + 8.3, 0.3)])
            pbox(bm_for(p0, "stone"), F, uc - 0.85, uc + 0.85, G + 6.6, G + 6.9, 0, 0.45)
            for q in range(4): box(bm_for(p0, "iron"), F, uc - 0.4 + q * 0.27, uc - 0.36 + q * 0.27, G + 6.9, G + 8.3, 0.32, 0.38)
            if k % 2 == 0: cylinder(p0, "iron", F.p(uc, 0, 0.25), 0.12, G + 3.2, G + 3.3, seg=8)          # horse rings
    rusticate(p0, F, 0, L, G - 0.3, H1 - 0.4, 0.95, (0.25, 0.42), (1.1, 2.6), seed=sum(map(ord, side)), holes=holes)
    string_course(p0, F, L, H1 - 0.3)
    if bench: box(bm_for(f"panca@1865-{NOW}", "stone"), F, 0.3, L - 0.3, G - 0.3, G + 0.45, 0, 0.7)     # Poggi, 1863–65
    for (v0, v1, part, seed, pr) in ((H1, H2, p1, 3, (0.12, 0.22)), (H2, TOP, p2, 7, (0.06, 0.12))):
        box(bm_for(part, "stone"), F, 0, L, v0, v1, -1.6, -0.02)
        hs = []
        for k in range(nb):
            uc = (k + 0.5) * bay; bifora(part, F, uc, v0 + 1.6, h=4.4 if v0 == H1 else 4.0)
            hs.append(("arch", uc, v0 + 1.6 + (4.4 if v0 == H1 else 4.0) - 0.95, 1.6)); hs.append((uc - 1.6, uc + 1.6, v0 + 1.3, v0 + 4.8))
        rusticate(part, F, 0, L, v0 + 0.3, v1 - 0.3, 0.85, pr, (1.0, 2.2), seed=seed + sum(map(ord, side)), holes=hs)
        if v0 == H1: string_course(part, F, L, H2 - 0.3)

def eave(part, F, u0, u1):
    """Where the cornice stops: only its dentils and egg-and-dart frieze run on, with a gutter under the roof's edge."""
    pbox(bm_for(part, "stone"), F, u0, u1, TOP, TOP + 0.5, 0, 0.3)
    for k in range(int((u1 - u0) / 0.32)):
        u = u0 + 0.05 + k * 0.32; pbox(bm_for(part, "stone"), F, u, u + 0.17, TOP + 0.5, TOP + 0.8, 0, 0.55)
    pbox(bm_for(part, "stone"), F, u0, u1, TOP + 0.8, TOP + 1.2, 0, 0.75)
    box(bm_for(part, "iron"), F, u0, u1, TOP + 1.2, TOP + 1.35, 0.6, 0.9)

def strozzi():
    for side, (F, L) in FRONTS.items():
        nb = BAYS[side]; bay = L / nb
        if side == "south":
            # left unfinished in 1538: rough masonry, few openings, no cornice – until the 1938–40 restoration
            box(bm_for("strozzi_sud_grezzo@1489-1938", "stone"), F, 0, L, G - 1.5, H1, -1.6, 0)
            box(bm_for("strozzi_sud_grezzo@1495-1938", "stone"), F, 0, L, H1, H2, -1.6, 0)
            box(bm_for("strozzi_sud_grezzo@1502-1938", "stone"), F, 0, L, H2, TOP + 0.6, -1.6, 0)
            for k in range(nb):
                uc = (k + 0.5) * bay
                for v0, part in ((H1 + 2.2, "strozzi_sud_grezzo@1495-1938"), (H2 + 2.2, "strozzi_sud_grezzo@1502-1938")):
                    if k % 3 == 1: poly(bm_for(part, "dark"), [F.p(uc - 0.7, v0, 0.03), F.p(uc + 0.7, v0, 0.03), F.p(uc + 0.7, v0 + 2.6, 0.03), F.p(uc - 0.7, v0 + 2.6, 0.03)])
            # 1938–40: the side finished like the others; the great cornice turns the corners and stops, a plain eave runs on
            sp = f"strozzi_sud@1938-{NOW}"
            finished_front(side, F, L, (sp, sp, sp), portal=False, bench=False)
            great_cornice(f"cornicione@1502-{NOW}", F, 0, 2.4); great_cornice(f"cornicione@1502-{NOW}", F, L - 2.4, L)
            eave(sp, F, 2.4, L - 2.4)
            continue
        finished_front(side, F, L, (f"strozzi_terreno@1489-{NOW}", f"strozzi_nobile@1495-{NOW}", f"strozzi_secondo@1502-{NOW}"))
        # Cronaca's cornice: north and east whole, west half (the other half completed 1938–40)
        if side in ("north", "east"): great_cornice(f"cornicione@1502-{NOW}", F, 0, L)
        elif side == "west":
            great_cornice(f"cornicione@1502-{NOW}", F, L / 2, L)
            great_cornice(f"cornicione_1938@1938-{NOW}", F, 0, L / 2)
        # lanterns on the corners of the piano nobile (Caparra, 1491–98)
        for u in (1.2, L - 1.2): lantern(f"lanterne@1498-{NOW}", F, u, H1 + 1.2)

    # roof
    rp = f"strozzi_secondo@1502-{NOW}"
    # low roofs on the four wings, ridge over the middle of each wing, the courtyard left open
    ring_ = D["holes"][0]; Q = ring_[:-1] if ring_[0] == ring_[-1] else ring_
    inner = {"NW": Q[0], "SW": Q[1], "SE": Q[2], "NE": Q[3]}; outer = {"NW": NW, "NE": NE, "SE": SE, "SW": SW}
    for a, b in (("NW", "NE"), ("NE", "SE"), ("SE", "SW"), ("SW", "NW")):
        mid = lambda k: ((outer[k][0] + inner[k][0]) / 2, (outer[k][1] + inner[k][1]) / 2)
        poly(bm_for(rp, "roof"), [V(*outer[a], TOP + 0.6), V(*outer[b], TOP + 0.6), V(*mid(b), TOP + 3.6), V(*mid(a), TOP + 3.6)])
        poly(bm_for(rp, "roof"), [V(*mid(a), TOP + 3.6), V(*mid(b), TOP + 3.6), V(*inner[b], TOP + 0.6), V(*inner[a], TOP + 0.6)])
    # Cronaca's courtyard (1503): arcades on the four sides of the inner ring
    ring_ = D["holes"][0]; Q = ring_[:-1] if ring_[0] == ring_[-1] else ring_
    qc = (sum(p[0] for p in Q) / len(Q), sum(p[1] for p in Q) / len(Q)); cp = f"cortile@1503-{NOW}"
    for a, b in zip(Q, Q[1:] + Q[:1]):
        L = math.dist(a, b); tx, tz = (b[0] - a[0]) / L, (b[1] - a[1]) / L; nx, nz = -tz, tx
        if (qc[0] - a[0]) * nx + (qc[1] - a[1]) * nz < 0: nx, nz = -nx, -nz
        F = Frame(V(*a), Vector((tx, -tz, 0)), Vector((nx, -nz, 0)))
        n = max(1, round(L / 4.2)); w = L / n
        box(bm_for(cp, "plaster"), F, 0, L, G - 0.5, TOP, -0.8, 0)
        for k in range(n):
            u = (k + 0.5) * w
            arch_fill(cp, "dark", F, u - w * 0.38, u + w * 0.38, G, G + 5.2, n=0.03)
            ring(cp, "serena", F, u, G + 5.2, w * 0.38, w * 0.38 + 0.3, 0, 0.1, seg=10, soffit=False)
            win_round(cp, F, u, H1 + 1.8, H1 + 5.6, 1.1, frame="serena")
            win_rect(cp, F, u, H2 + 1.8, H2 + 4.6, 1.0, frame="serena")
        for v in (H1, H2): entablature(cp, F, 0, L, v - 0.6, mat="serena", h=0.6, proj=0.35)
MAT["plaster"] = material("plaster_white", "intonaco", (0.88, 0.85, 0.78), 0.9, 0.4, tint=(1.3, 1.25, 1.1))
strozzi()
K.export("strozzi")
