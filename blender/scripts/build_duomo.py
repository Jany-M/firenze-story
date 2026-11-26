"""Santa Maria del Fiore – measured, dated model (v1).

Run:  blender -b --python blender/scripts/build_duomo.py
Out:  web/public/models/landmarks/duomo.glb (+ duomo_materials.json), blender/landmarks/duomo.blend

Frame: origin = centre of the dome at ground level (LiDAR 2023 lantern top, scene x 138.5 / z -150.5),
X = east along the nave axis, Y = north, Z = up (metres). The web app rotates by the measured axis (1.93°).
Dimensions are measured on the Comune LiDAR 2023 DSM (0.5 m) and the OSM footprint (see docs/landmarks/DUOMO.md);
architectural detail (bays, panels, windows, portals, lantern) follows photographs and the standard literature.

Every object name carries its dates: "<part>@<from>-<to>" – the web app shows it when from <= year < to.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
K.reset()

# ------------------------------------------------------------------ measurements (metres, see header)
FACADE_X = -107.5          # west face of the façade
NAVE_Y = -3.8              # nave axis is ~3.8 m south of the dome centre (LiDAR + footprint)
NAVE_HW = 22.0             # half width over the aisle walls (footprint 44.1 m)
CLER_HW = 10.6             # half width of the clerestory (nave) walls
AISLE_H, CLER_H, RIDGE_H = 30.5, 44.5, 47.0
CROSS_X = -26.6            # nave meets the octagon (drum apothem)
BAYS = 4
OCT_A = 26.5               # drum apothem (outer)
DRUM_Z0, DRUM_Z1 = 41.5, 55.5
DOME_D0, DOME_Z0, DOME_R = 25.3, 58.0, 39.2      # springing apothem, springing height, radius of the pointed (quinto acuto) arc
DOME_TOP_D, LANTERN_Z = 8.2, 90.5
TRIB_A, TRIB_H, TRIB_ROOF = 13.0, 35.0, 42.0      # tribune half-octagon apothem, wall height, roof at the drum
CHAP_D, CHAP_H = 8.5, 18.0                        # radiating chapels: depth, height
T22 = math.tan(math.pi / 8)

# ------------------------------------------------------------------ nave (4 bays, built 1296–1380)
BAY_W = (CROSS_X - FACADE_X) / BAYS
def nave_bay(part, b):
    x0 = FACADE_X + b * BAY_W; x1 = x0 + BAY_W
    for side in (1, -1):                                   # north (+1) and south (-1) aisle walls
        yw = NAVE_Y + side * NAVE_HW
        F = Frame((x0, yw, 0) if side > 0 else (x1, yw, 0), (1, 0, 0) if side > 0 else (-1, 0, 0), (0, side, 0))
        L = BAY_W
        wall(part, F, 0, L, 0, AISLE_H - 0.9)
        pbox(bm_for(part, "white"), F, 0, L, 0, 1.2, 0, 0.45)                                  # plinth
        pilaster(part, F, 0.8, 1.2, AISLE_H - 1.2); pilaster(part, F, L - 0.8, 1.2, AISLE_H - 1.2)
        # lower register: two tall panels; upper: the big Gothic window (bifora) in the middle of the bay
        panels(part, F, 1.8, L - 1.8, 1.2, 14.0, 4, 3, accent=lambda i, j: (i in (1, 2) and j == 1))
        panels(part, F, 1.8, L - 1.8, 14.0, AISLE_H - 2.0, 6, 2)
        opening(part, F, L / 2 - 1.9, L / 2 + 1.9, 15.5, 26.8, mullion=True)
        cornice(part, F, 0, L, AISLE_H - 1.5, 1.5, 0.7)
        # side portals in the third bay (Porta della Mandorla north, Porta dei Canonici south)
        if b == 2:
            opening(part, F, L * 0.3 - 1.6, L * 0.3 + 1.6, 0, 8.2, depth=0.9, frame=0.8, pointed=True, fill="bronze")
            gab = bm_for(part, "white"); u = L * 0.3
            poly(gab, [F.p(u - 3.0, 9.4, 0.9), F.p(u + 3.0, 9.4, 0.9), F.p(u, 13.8, 0.9)])
            poly(bm_for(part, "mosaic"), [F.p(u - 1.8, 9.9, 0.95), F.p(u + 1.8, 9.9, 0.95), F.p(u, 12.6, 0.95)])
            pinnacle(part, (F.p(u - 3.2, 0, 0.6).x, F.p(u - 3.2, 0, 0.6).y), 9.4, 5.0, 0.7)
            pinnacle(part, (F.p(u + 3.2, 0, 0.6).x, F.p(u + 3.2, 0, 0.6).y), 9.4, 5.0, 0.7)
    # clerestory: walls with round oculi, lean-to aisle roofs, nave roof
    for side in (1, -1):
        yw = NAVE_Y + side * CLER_HW
        F = Frame((x0, yw, 0) if side > 0 else (x1, yw, 0), (1, 0, 0) if side > 0 else (-1, 0, 0), (0, side, 0))
        wall(part, F, 0, BAY_W, AISLE_H - 2, CLER_H, 1.0)
        panels(part, F, 1.0, BAY_W - 1.0, AISLE_H + 3.0, CLER_H - 1.2, 5, 2)
        cx = BAY_W / 2; cz = (AISLE_H + 3 + CLER_H - 1.2) / 2
        for rad, mat, nn in ((2.4, "white", 0.06), (2.0, "green", 0.09)):
            poly(bm_for(part, mat), [F.p(cx + rad * math.cos(a), cz + rad * math.sin(a), nn) for a in [i / 20 * 2 * math.pi for i in range(20)]])
        poly(bm_for(part, "glass"), [F.p(cx + 1.6 * math.cos(a), cz + 1.6 * math.sin(a), 0.12) for a in [i / 16 * 2 * math.pi for i in range(16)]])
        cornice(part, F, 0, BAY_W, CLER_H - 0.9, 0.9, 0.6, arches=False)
        lean_to(part, x0, x1, NAVE_Y + side * (NAVE_HW - 1.0), NAVE_Y + side * CLER_HW, AISLE_H - 0.6, AISLE_H + 3.6)

# (structure, marble revetment): first two bays clad before 1357 (sigec ICCD8234555), side portals decorated 1391–1423
BAY_DATES = [(1300, 1350, "nave_b1"), (1335, 1357, "nave_b2"), (1357, 1385, "nave_b3"), (1366, 1395, "nave_b4")]
def nave():
    for b, (yr, clad, nm) in enumerate(BAY_DATES):
        two_phase(nave_bay, nm, yr, clad, b)
    def nave_end(part):
        for side in (1, -1):                                   # east ends of the aisles, beside the octagon
            F = Frame((CROSS_X, NAVE_Y + side * CLER_HW, 0), (0, side, 0), (1, 0, 0))
            wall(part, F, 0, NAVE_HW - CLER_HW, 0, AISLE_H - 0.9, 1.2)
            panels(part, F, 0.5, NAVE_HW - CLER_HW - 0.5, 1.2, AISLE_H - 2.0, 4, 4)
            cornice(part, F, 0, NAVE_HW - CLER_HW, AISLE_H - 1.5, 1.5, 0.7)
    two_phase(nave_end, "nave_end", 1366, 1395)
    gable_roof(f"nave_roof@1380-{NOW}", FACADE_X + 1.5, CROSS_X, NAVE_Y - CLER_HW - 0.6, NAVE_Y + CLER_HW + 0.6, CLER_H, RIDGE_H)
nave()

# ------------------------------------------------------------------ octagon base, tribunes and chapels (1380–1421)
def tribune(k, part):
    """Half-octagon apse on octagon face k with five radiating chapels and a tiled semi-dome."""
    n = oct_dir(k); t = Vector((-n.y, n.x, 0)); c = n * OCT_A          # tribune centre on the drum face
    faces = []
    for j in range(-2, 3):                                              # five faces of the half octagon
        d = (n * math.cos(j * math.pi / 4) + t * math.sin(j * math.pi / 4)).normalized()
        dt = Vector((-d.y, d.x, 0)); half = TRIB_A * T22
        F = Frame(c + d * TRIB_A - dt * half, dt, d); faces.append((F, d))
        wall(part, F, 0, 2 * half, 0, TRIB_H, 1.4)
        panels(part, F, 0.6, 2 * half - 0.6, CHAP_H + 1.0, TRIB_H - 1.4, 4, 3)
        opening(part, F, half - 1.1, half + 1.1, CHAP_H + 3.5, CHAP_H + 12.5, mullion=False)
        cornice(part, F, 0, 2 * half, TRIB_H - 1.2, 1.2, 0.6)
        # radiating chapel in front of each face
        G = Frame(F.p(0.9, 0, 0), dt, d)
        wall(part, G, 0, 2 * half - 1.8, 0, CHAP_H, 0.2)
        cw = 2 * half - 1.8
        for side_u in (0.0, cw):                                         # chapel side walls
            S = Frame(G.p(side_u, 0, 0), d, -dt if side_u == 0 else dt)
            wall(part, S, 0, CHAP_D, 0, CHAP_H, 0.8)
            panels(part, S, 0.5, CHAP_D - 0.5, 1.2, CHAP_H - 1.6, 2, 2)
        E = Frame(G.p(0, 0, CHAP_D), dt, d)
        wall(part, E, 0, cw, 0, CHAP_H, 0.8)
        panels(part, E, 0.5, cw - 0.5, 1.2, CHAP_H - 1.6, 3, 2, accent=lambda i, j: i == 1 and j == 0)
        opening(part, E, cw / 2 - 0.9, cw / 2 + 0.9, 5.0, 13.0)
        cornice(part, E, 0, cw, CHAP_H - 1.0, 1.0, 0.5)
        r = bm_for(part, "roof")                                          # chapel roof: lean-to towards the tribune wall
        poly(r, [G.p(0, CHAP_H, CHAP_D + 0.6), G.p(cw, CHAP_H, CHAP_D + 0.6), G.p(cw, CHAP_H + 3.2, 0), G.p(0, CHAP_H + 3.2, 0)])
    # semi-dome roof: five tiled sails rising from the tribune cornice to the drum
    r = bm_for(part, "roof"); steps = 8
    for j in range(-3, 2):
        a0, a1 = j * math.pi / 4 + math.pi / 8, (j + 1) * math.pi / 4 + math.pi / 8
        corner = lambda a, rad: c + (n * math.cos(a) + t * math.sin(a)) * rad
        rows = []
        for s in range(steps + 1):
            f = s / steps; rad = TRIB_A / math.cos(math.pi / 8) * (1 - f) + 0.01
            z = TRIB_H + (TRIB_ROOF - TRIB_H) * math.sin(f * math.pi / 2)
            rows.append([corner(a0 - math.pi / 4 * 0, rad) + Vector((0, 0, z)), corner(a1, rad) + Vector((0, 0, z))])
        for s in range(steps):
            poly(r, [rows[s][0], rows[s][1], rows[s + 1][1], rows[s + 1][0]])

def octagon_base():
    two_phase(octagon_core, "octagon_base", 1380, 1430)
def octagon_core(part):
    for k in range(8):
        n = oct_dir(k); t = Vector((-n.y, n.x, 0)); half = OCT_A * T22
        F = Frame(n * OCT_A - t * half, t, n)
        wall(part, F, 0, 2 * half, 0, DRUM_Z0, 2.0)
    # diagonal faces between tribunes and nave aisles: panelled walls up to the drum
    for k in (1, 3, 5, 7):
        n = oct_dir(k); t = Vector((-n.y, n.x, 0)); half = OCT_A * T22
        F = Frame(n * OCT_A - t * half, t, n)
        panels(part, F, 0.5, 2 * half - 0.5, 1.0, DRUM_Z0 - 1.5, 5, 6)
        cornice(part, F, 0, 2 * half, DRUM_Z0 - 1.2, 1.2, 0.7)
def tribunes():
    # tribunes 1407–1420 (Le facciate del Duomo, 1407 start / last closed 1420); marble corbels of the third tribune 1422
    for k, yr, clad in ((0, 1420, 1425), (2, 1412, 1420), (6, 1412, 1420)):
        two_phase(lambda part, kk: tribune(kk, part), f"tribune_{'ENS'[[0, 2, 6].index(k)]}", yr, clad, k)

octagon_base(); tribunes()

def exedrae():
    """Tribune morte: four small semicircular exedrae on the diagonal faces at the foot of the drum (1439–1445)."""
    part = f"exedrae@1445-{NOW}"
    for k in (1, 3, 5, 7):
        n = oct_dir(k); c = n * (OCT_A + 0.2); seg = 12; R = 5.4
        ring = [c + (n * math.cos(a) + Vector((-n.y, n.x, 0)) * math.sin(a)) * R for a in [-math.pi / 2 + math.pi * i / seg for i in range(seg + 1)]]
        for i in range(seg):
            p0, p1 = ring[i], ring[i + 1]; tdir = (p1 - p0).normalized(); out = Vector((tdir.y, -tdir.x, 0))
            if out.dot(n) < 0: out = -out
            F = Frame(p0, tdir, out); L = (p1 - p0).length
            wall(part, F, 0, L, DRUM_Z0 - 10.5, DRUM_Z0 - 1.0, 1.0)
            if i % 2 == 0: pbox(bm_for(part, "white"), F, L - 0.25, L + 0.25, DRUM_Z0 - 10.5, DRUM_Z0 - 1.0, 0, 0.5)   # half-columns
        # conical shell roof
        r = bm_for(part, "roof"); apex = c + Vector((0, 0, DRUM_Z0 + 2.2))
        for i in range(seg): poly(r, [ring[i] + Vector((0, 0, DRUM_Z0 - 1.0)), ring[i + 1] + Vector((0, 0, DRUM_Z0 - 1.0)), apex])
exedrae()

# ------------------------------------------------------------------ drum (1410–1413) with the eight oculi
def drum():
    two_phase(drum_faces, "drum", 1413, 1436)       # drum 1410–13 (eight oculi); revetment date conjectural (before the consecration)
    drum_band()
def drum_faces(part):
    for k in range(8):
        n = oct_dir(k); t = Vector((-n.y, n.x, 0)); half = OCT_A * T22
        F = Frame(n * OCT_A - t * half, t, n)
        wall(part, F, 0, 2 * half, DRUM_Z0, DRUM_Z1, 2.2)
        pilaster(part, F, 0.7, DRUM_Z0, DRUM_Z1 - 1.0, 1.4, 0.4); pilaster(part, F, 2 * half - 0.7, DRUM_Z0, DRUM_Z1 - 1.0, 1.4, 0.4)
        panels(part, F, 1.6, 2 * half - 1.6, DRUM_Z0 + 0.5, DRUM_Z1 - 1.6, 6, 2,
               accent=lambda i, j: False)
        # oculus: big round window in a green/white ring, centred on the face
        cx, cz = half, (DRUM_Z0 + DRUM_Z1) / 2 + 0.4
        for rad, mat, nn in ((3.3, "white", 0.12), (2.85, "green", 0.16), (2.45, "white", 0.2)):
            poly(bm_for(part, mat), [F.p(cx + rad * math.cos(a), cz + rad * math.sin(a), nn) for a in [i / 24 * 2 * math.pi for i in range(24)]])
        poly(bm_for(part, "glass"), [F.p(cx + 2.0 * math.cos(a), cz + 2.0 * math.sin(a), 0.24) for a in [i / 24 * 2 * math.pi for i in range(24)]])
        cornice(part, F, -0.2, 2 * half + 0.2, DRUM_Z1 - 1.0, 1.4, 1.0, arches=False)
def drum_band():
    # base of the dome: the white "ballatoio" band between drum and tiles (only one face got its gallery, 1515)
    part = f"drum_top@1420-{NOW}"
    for k in range(8):
        n = oct_dir(k); t = Vector((-n.y, n.x, 0)); half = (OCT_A - 0.3) * T22
        F = Frame(n * (OCT_A - 0.3) - t * half, t, n)
        wall(part, F, 0, 2 * half, DRUM_Z1, DOME_Z0 + 0.3, 1.5)
        pbox(bm_for(part, "green"), F, 0, 2 * half, DRUM_Z1 + 1.2, DRUM_Z1 + 1.45, 0, 0.05)
    F = Frame(oct_dir(7) * (OCT_A + 0.4) - Vector((-oct_dir(7).y, oct_dir(7).x, 0)) * OCT_A * T22, Vector((-oct_dir(7).y, oct_dir(7).x, 0)), oct_dir(7))
    for i in range(14):                                           # Baccio d'Agnolo's gallery on the south-east face (1507–15)
        u = 0.8 + i * (2 * OCT_A * T22 - 1.6) / 13
        box(bm_for(f"ballatoio@1515-{NOW}", "white"), F, u - 0.25, u + 0.25, DRUM_Z1 + 0.4, DRUM_Z1 + 2.4, 0.2, 0.7)
    pbox(bm_for(f"ballatoio@1515-{NOW}", "white"), F, 0, 2 * OCT_A * T22, DRUM_Z1 + 2.4, DRUM_Z1 + 2.8, 0, 0.9)
drum()

# ------------------------------------------------------------------ dome (1420–1436): octagonal cloister vault, pointed profile, 8 ribs
def dome_z(d):
    cx = DOME_D0 - DOME_R
    return DOME_Z0 + math.sqrt(max(DOME_R ** 2 - (d - cx) ** 2, 0.0))
def dome(part, d_stop):
    """Eight tiled sails from the springing (apothem DOME_D0) up to apothem d_stop (open ring = under construction)."""
    rows = 26
    ds = [DOME_D0 - (DOME_D0 - d_stop) * i / rows for i in range(rows + 1)]
    for k in range(8):
        n = oct_dir(k); t = Vector((-n.y, n.x, 0))
        cols = 10; grid = []
        for d in ds:
            hw = d * T22 - 1.0                      # leave room for the rib
            grid.append([n * d + t * (-hw + 2 * hw * c / cols) + Vector((0, 0, dome_z(d))) for c in range(cols + 1)])
        bm = bm_for(part, "tile")
        for i in range(rows): quad_strip(bm, grid[i], grid[i + 1])
        # rib on the corner between face k and k+1: white marble, raised, 2.2 m wide
        corner = (oct_dir(k) + oct_dir(k + 1)).normalized()
        a_in = []; a_out = []; top = []
        for d in ds:
            cdist = d / math.cos(math.pi / 8); z = dome_z(d)
            side = Vector((-corner.y, corner.x, 0))
            a_in.append(corner * (cdist - 0.25) + side * 1.15 + Vector((0, 0, z)))
            a_out.append(corner * (cdist - 0.25) - side * 1.15 + Vector((0, 0, z)))
            top.append(corner * (cdist + 0.15) + Vector((0, 0, z + 0.45)))
        rb = bm_for(part, "white"); quad_strip(rb, a_in, top); quad_strip(rb, top, a_out)
        # thin white horizontal bands that mark the courses of the outer shell (three on each sail)
        for d in (DOME_D0 - 6, DOME_D0 - 11.5):
            if d < d_stop: continue
            hw = d * T22 - 1.0; z = dome_z(d)
            F = Frame(n * d - t * hw + Vector((0, 0, 0)), t, n)
            poly(bm_for(part, "white"), [F.p(0, z - 0.25, 0.08), F.p(2 * hw, z - 0.25, 0.08), F.p(2 * hw, z + 0.25, 0.08), F.p(0, z + 0.25, 0.08)])
dome(f"dome_1@1420-1428", 19.0)
dome(f"dome_2@1428-1436", 12.0)
dome(f"dome@1436-{NOW}", DOME_TOP_D)

# ------------------------------------------------------------------ lantern (1446–1461), ball and cross (Verrocchio 1471)
def lantern():
    part = f"lantern@1461-{NOW}"; z0 = LANTERN_Z
    ring = bm_for(part, "white")                                   # closing ring of the dome
    for k in range(8):
        n = oct_dir(k); t = Vector((-n.y, n.x, 0)); half = DOME_TOP_D * T22
        F = Frame(n * DOME_TOP_D - t * half, t, n); box(ring, F, 0, 2 * half, z0 - 1.2, z0 + 0.6, -1.2, 0.3)
    A = 3.3; H1 = 10.0
    for k in range(8):                                             # octagonal body with tall round-headed windows
        n = oct_dir(k); t = Vector((-n.y, n.x, 0)); half = A * T22
        F = Frame(n * A - t * half, t, n)
        wall(part, F, 0, 2 * half, z0 + 0.6, z0 + H1, 0.6)
        opening(part, F, half - 0.55, half + 0.55, z0 + 2.0, z0 + 7.6, depth=0.3, frame=0.18, pointed=False)
        cornice(part, F, -0.3, 2 * half + 0.3, z0 + H1 - 0.6, 1.0, 0.7, arches=False)
        # buttress on the corner: a wall fin stepping down in a volute
        c = (oct_dir(k) + oct_dir(k + 1)).normalized(); s = Vector((-c.y, c.x, 0))
        B = Frame(c * (A / math.cos(math.pi / 8)) - s * 0.35, c, s)
        bm = bm_for(part, "white")
        box(bm, B, 0, 1.2, z0 + 0.6, z0 + H1 - 0.6, -0.7, 0)          # buttress steps down outwards: the volutes
        box(bm, B, 1.2, 2.3, z0 + 0.6, z0 + 5.5, -0.7, 0)
        box(bm, B, 2.3, 3.2, z0 + 0.6, z0 + 2.6, -0.7, 0)
        bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=0.6, matrix=Matrix.Translation(B.p(2.9, z0 + 2.9, -0.35)))
        pinnacle(part, tuple(B.p(1.0, 0, -0.35)[:2]), z0 + H1 + 0.3, 3.0, 0.5)
    # conical marble spire with ribs, ball and cross
    cz0 = z0 + H1 + 0.4; cz1 = cz0 + 7.5
    bmesh.ops.create_cone(bm_for(part, "white"), cap_ends=True, segments=8, radius1=A * 0.92, radius2=0.35, depth=cz1 - cz0,
                          matrix=Matrix.Translation((0, 0, (cz0 + cz1) / 2)) @ Matrix.Rotation(math.pi / 8, 4, "Z"))
    p2 = f"ball@1471-{NOW}"
    bmesh.ops.create_uvsphere(bm_for(p2, "gold"), u_segments=20, v_segments=12, radius=1.15, matrix=Matrix.Translation((0, 0, cz1 + 1.0)))
    g = bm_for(p2, "gold")
    wbox(g, -0.12, 0.12, -0.12, 0.12, cz1 + 2.1, cz1 + 5.9)        # cross (top at ~114 m)
    wbox(g, -0.12, 0.12, -1.0, 1.0, cz1 + 4.4, cz1 + 4.65)
lantern()

# ------------------------------------------------------------------ façades
FY0, FY1 = NAVE_Y - NAVE_HW, NAVE_Y + NAVE_HW
def facade_defabris():
    """Emilio De Fabris, 1876–1887: three portals with gables, apostles' niches, rose window, crowning with pinnacles."""
    part = f"facade@1887-{NOW}"
    F = Frame((FACADE_X, FY1, 0), (0, -1, 0), (-1, 0, 0))        # u runs north → south along the façade, n = west
    W = FY1 - FY0
    piers = [0.0, W / 2 - 9.4, W / 2 + 9.4, W]                     # outer corners and the two piers of the central bay
    wall(part, F, 0, W, 0, AISLE_H + 1.0, 1.8)
    wall(part, F, piers[1], piers[2], AISLE_H + 1.0, 46.2, 1.8)
    # buttress piers with stacked niches, ending in pinnacles
    for i, u in enumerate(piers):
        w = 2.6; top = 33.5 if i in (0, 3) else 47.5
        box(bm_for(part, "white"), F, u - w / 2 + (w / 2 if i == 0 else 0) - (w / 2 if i == 3 else 0), u + w / 2 + (w / 2 if i == 0 else 0) - (w / 2 if i == 3 else 0), 0, top, 0, 1.4)
        uc = u + (1.3 if i == 0 else -1.3 if i == 3 else 0)
        for z in (3.0, 11.0, 20.5) + ((31.0, 39.0) if i in (1, 2) else ()):
            opening(part, F, uc - 0.55, uc + 0.55, z, z + 5.2, depth=0.4, frame=0.15, pointed=True, fill="dark", frame_mat="red")
        pinnacle(part, tuple(F.p(uc, 0, 0.7)[:2]), top, 6.0 if i in (1, 2) else 4.5, 1.6)
    # polychrome panels on every bay, horizontal bands of the registers
    for (a, b) in ((piers[0] + 2.6, piers[1] - 1.3), (piers[1] + 1.3, piers[2] - 1.3), (piers[2] + 1.3, piers[3] - 2.6)):
        panels(part, F, a, b, 0.8, 16.5, 6 if b - a > 10 else 3, 3, accent=lambda i, j: j == 2 and i % 2 == 1)
        panels(part, F, a, b, 21.8, AISLE_H, 6 if b - a > 10 else 3, 2, accent=lambda i, j: (i + j) % 2 == 0)
    for z in (16.5, 21.8, AISLE_H):
        box(bm_for(part, "white"), F, 0, W, z - 0.35, z + 0.35, 0, 1.0); box(bm_for(part, "green"), F, 0, W, z - 0.1, z + 0.1, 0, 1.05)
    # three portals: bronze doors, mosaic lunettes, gabled marble cusps
    for (uc, w, h, gh) in ((W / 2, 4.6, 10.0, 16.8), (piers[1] / 2 + 0.6, 3.0, 7.2, 12.6), ((piers[2] + W) / 2 - 0.6, 3.0, 7.2, 12.6)):
        opening(part, F, uc - w / 2, uc + w / 2, 0, h, depth=1.2, frame=0.9, pointed=False, fill="bronze", frame_mat="white")
        poly(bm_for(part, "mosaic"), [F.p(uc + w / 2 * math.cos(a), h - w / 2 + w / 2 * math.sin(a), 0.05) for a in [i / 12 * math.pi for i in range(13)]])
        poly(bm_for(part, "white"), [F.p(uc - w / 2 - 1.8, h + 0.4, 1.3), F.p(uc + w / 2 + 1.8, h + 0.4, 1.3), F.p(uc, gh, 1.3)])
        poly(bm_for(part, "red"), [F.p(uc - w / 2 - 0.6, h + 1.0, 1.35), F.p(uc + w / 2 + 0.6, h + 1.0, 1.35), F.p(uc, gh - 1.8, 1.35)])
        for s in (-1, 1): pinnacle(part, tuple(F.p(uc + s * (w / 2 + 1.6), 0, 1.0)[:2]), h + 0.2, gh - h + 1.0, 0.8)
    # gallery of the apostles: a row of small niches across the whole front
    for i in range(16):
        u = 2.2 + i * (W - 4.4) / 15
        opening(part, F, u - 0.5, u + 0.5, 17.2, 21.3, depth=0.45, frame=0.14, pointed=True, fill="dark", frame_mat="white")
    # side bays: pointed bifore; central bay: the rose window (Ghiberti's glass) and the crown
    for uc in (piers[1] / 2 + 0.6, (piers[2] + W) / 2 - 0.6):
        opening(part, F, uc - 1.4, uc + 1.4, 22.8, 29.6, mullion=True, frame_mat="white")
        poly(bm_for(part, "white"), [F.p(uc - 4.0, AISLE_H + 0.35, 1.0), F.p(uc + 4.0, AISLE_H + 0.35, 1.0), F.p(uc, AISLE_H + 3.4, 1.0)])
    uc, zc = W / 2, 33.5
    for rad, mat, nn in ((4.6, "white", 0.1), (4.1, "green", 0.14), (3.8, "white", 0.18)):
        poly(bm_for(part, mat), [F.p(uc + rad * math.cos(a), zc + rad * math.sin(a), nn) for a in [i / 32 * 2 * math.pi for i in range(32)]])
    poly(bm_for(part, "glass"), [F.p(uc + 3.3 * math.cos(a), zc + 3.3 * math.sin(a), 0.22) for a in [i / 32 * 2 * math.pi for i in range(32)]])
    for i in range(12):                                            # tracery spokes
        a = i / 12 * 2 * math.pi
        poly(bm_for(part, "white"), [F.p(uc + 0.5 * math.cos(a - 0.06), zc + 0.5 * math.sin(a - 0.06), 0.26), F.p(uc + 3.3 * math.cos(a - 0.02), zc + 3.3 * math.sin(a - 0.02), 0.26),
                                     F.p(uc + 3.3 * math.cos(a + 0.02), zc + 3.3 * math.sin(a + 0.02), 0.26), F.p(uc + 0.5 * math.cos(a + 0.06), zc + 0.5 * math.sin(a + 0.06), 0.26)])
    panels(part, F, piers[1] + 1.3, uc - 5.2, AISLE_H + 0.5, 42.0, 2, 4, accent=lambda i, j: j == 1)
    panels(part, F, uc + 5.2, piers[2] - 1.3, AISLE_H + 0.5, 42.0, 2, 4, accent=lambda i, j: j == 1)
    # crown: arcaded frieze with the busts, horizontal cornice and the central tympanum with the Madonna
    for i in range(12):
        u = piers[1] + 2.0 + i * (piers[2] - piers[1] - 4.0) / 11
        opening(part, F, u - 0.45, u + 0.45, 42.3, 44.6, depth=0.3, frame=0.12, pointed=False, fill="dark", frame_mat="white")
    cornice(part, F, piers[1] - 1.3, piers[2] + 1.3, 45.0, 1.2, 1.2, arches=False)
    poly(bm_for(part, "white"), [F.p(uc - 5.5, 46.2, 1.0), F.p(uc + 5.5, 46.2, 1.0), F.p(uc, 50.2, 1.0)])
    poly(bm_for(part, "mosaic"), [F.p(uc + 1.3 * math.cos(a), 47.6 + 1.3 * math.sin(a), 1.05) for a in [i / 16 * 2 * math.pi for i in range(16)]])
facade_defabris()

def facade_old():
    """Before De Fabris: Arnolfo's façade (lower third in marble with statues, 1296–c.1310; upper rough), dismantled 1587;
    then a bare rough-stone front (painted only for festivities) until 1876–87."""
    W = FY1 - FY0
    F = Frame((FACADE_X, FY1, 0), (0, -1, 0), (-1, 0, 0))
    lo = f"facade_arnolfo@1310-1587"
    wall(lo, F, 0, W, 0, 16.0, 1.6)
    for (uc, w, h) in ((W / 2, 4.2, 9.0), (W * 0.2, 2.8, 7.0), (W * 0.8, 2.8, 7.0)):
        opening(lo, F, uc - w / 2, uc + w / 2, 0, h, depth=1.0, frame=0.8, pointed=False, fill="dark")
        poly(bm_for(lo, "white"), [F.p(uc - w / 2 - 1.4, h + 0.3, 1.0), F.p(uc + w / 2 + 1.4, h + 0.3, 1.0), F.p(uc, h + 4.0, 1.0)])
    for i in range(14):
        u = 1.8 + i * (W - 3.6) / 13
        if abs(u - W / 2) < 4 or abs(u - W * 0.2) < 3 or abs(u - W * 0.8) < 3: continue
        opening(lo, F, u - 0.5, u + 0.5, 2.0, 6.5, depth=0.4, frame=0.15, pointed=True, fill="dark")
        opening(lo, F, u - 0.5, u + 0.5, 9.5, 14.0, depth=0.4, frame=0.15, pointed=True, fill="dark")
    panels(lo, F, 0.5, W - 0.5, 0.3, 15.5, 12, 1)
    up = f"facade_rough_upper@1310-1887"
    wall(up, F, 0, W, 16.0, AISLE_H + 1.0, 1.6, mat="brick")
    wall(up, F, W / 2 - 9.4, W / 2 + 9.4, AISLE_H + 1.0, 46.2, 1.6, mat="brick")
    opening(up, F, W / 2 - 3.4, W / 2 + 3.4, 30.0, 36.8, depth=0.6, frame=0.4, pointed=False, fill="glass", frame_mat="white")
    bare = f"facade_bare_lower@1587-1887"
    wall(bare, F, 0, W, 0, 16.0, 1.6, mat="brick")
    for (uc, w, h) in ((W / 2, 4.2, 9.0), (W * 0.2, 2.8, 7.0), (W * 0.8, 2.8, 7.0)):
        opening(bare, F, uc - w / 2, uc + w / 2, 0, h, depth=1.0, frame=0.4, pointed=False, fill="dark", frame_mat="brick")
facade_old()

K.export("duomo")
