"""Basilica di Santa Croce – measured, dated model (v1).

Run:  blender -b --python blender/scripts/build_santa_croce.py  →  web/public/models/landmarks/santa_croce.glb
Frame: origin = middle of the façade at ground (scene x 576.5 / z 335.0), X along the nave towards the apse
(scene direction 0.880 / 0.476), Y = north side, Z up; landmarks.ts turns it by −0.496 rad. Ground 7.6 m (datum).
Measured (LiDAR 2023 DSM 0.5 m, sections across the nave every 4 m; OSM way 777563049):
  façade 41.6 m wide, gable ≈42 m · nave ≈20 m wide, eaves ≈33.5, ridge ≈38.4 · aisles to ±20.5 m, roofs 22.5–25.5
  seven bays of ≈13 m · transept t 93–114 m, ridge ≈31.4, north end chapels to −39.6 m · polygonal apse to t 121 m
  bell tower at t 116.7 / o +25.5 (south), ≈6.5 m square, top 76.9 m.
Dates (docs/landmarks/SANTA-CROCE.md): Arnolfo's church begun 1294/95 from the east end; transept and chapels c. 1300,
nave bays westwards to c. 1385 (stages *inferred*); consecrated 1443. Rough façade until Niccolò Matas' marble façade
(1857–63, shown from 1863). Gaetano Baccani's bell tower 1842–65 (shown from 1865).
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
K.reset()
MAT["stone"] = material("pietra_forte", "pietra_forte", (0.62, 0.5, 0.36), 0.85, 0.32, tint=(3.0, 2.85, 2.55))

def L(t, o, z=0.0): return Vector((t, -o, z))                     # nave coordinates → model (o positive = south)
def wall_frame(t0, o0, t1, o1):
    """Frame on the wall from (t0, o0) to (t1, o1); the outward side is to the right of that direction."""
    a, b = L(t0, o0), L(t1, o1); d = (b - a); n = d.length; uu = d / n
    return Frame(a, uu, Vector((uu.y, -uu.x, 0))), n

def block(part, outline, z0, z1, mat="stone"):
    """Prism from a (t, o) outline listed clockwise seen from above (so the right side is outside)."""
    bm = bm_for(part, mat); P = [L(t, o) for t, o in outline]
    bot = [bm.verts.new((p.x, p.y, z0)) for p in P]; top = [bm.verts.new((p.x, p.y, z1)) for p in P]
    try: bm.faces.new(top); bm.faces.new(bot[::-1])
    except ValueError: pass
    for i in range(len(P)):
        j = (i + 1) % len(P)
        try: bm.faces.new((bot[i], bot[j], top[j], top[i]))
        except ValueError: pass

def gable_along_t(part, t0, t1, o0, o1, z_eave, z_ridge, mat="roof"):
    om = (o0 + o1) / 2; bm = bm_for(part, mat)
    poly(bm, [L(t0, o0, z_eave), L(t1, o0, z_eave), L(t1, om, z_ridge), L(t0, om, z_ridge)])
    poly(bm, [L(t1, o1, z_eave), L(t0, o1, z_eave), L(t0, om, z_ridge), L(t1, om, z_ridge)])
    for t in (t0, t1): poly(bm_for(part, "stone"), [L(t, o0, z_eave), L(t, o1, z_eave), L(t, om, z_ridge)])

def gable_along_o(part, t0, t1, o0, o1, z_eave, z_ridge, mat="roof"):
    tm = (t0 + t1) / 2; bm = bm_for(part, mat)
    poly(bm, [L(t0, o0, z_eave), L(t0, o1, z_eave), L(tm, o1, z_ridge), L(tm, o0, z_ridge)])
    poly(bm, [L(t1, o1, z_eave), L(t1, o0, z_eave), L(tm, o0, z_ridge), L(tm, o1, z_ridge)])
    for o in (o0, o1): poly(bm_for(part, "stone"), [L(t0, o, z_eave), L(t1, o, z_eave), L(tm, o, z_ridge)])

NAVE_O = (-10.5, 9.5); AISLE_O = (-21.0, 19.5)
BAYS = [2.5, 15.1, 28.2, 41.4, 54.1, 67.1, 80.2, 92.8]

def nave_segment(part, t0, t1):
    """Nave and aisles between t0 and t1: aisle walls with tall lancets, clerestory with oculi, roofs."""
    block(part, [(t0, AISLE_O[0]), (t1, AISLE_O[0]), (t1, AISLE_O[1]), (t0, AISLE_O[1])], -1.5, 22.5)
    block(part, [(t0, NAVE_O[0]), (t1, NAVE_O[0]), (t1, NAVE_O[1]), (t0, NAVE_O[1])], 22.5, 33.5)
    gable_along_t(part, t0, t1, NAVE_O[0] - 0.6, NAVE_O[1] + 0.6, 33.5, 38.4)
    for o_out, o_in in ((AISLE_O[0] - 0.4, NAVE_O[0]), (AISLE_O[1] + 0.4, NAVE_O[1])):   # aisle lean-to roofs
        poly(bm_for(part, "roof"), [L(t0, o_out, 22.5), L(t1, o_out, 22.5), L(t1, o_in, 25.5), L(t0, o_in, 25.5)])
    for side, o in ((-1, AISLE_O[0]), (1, AISLE_O[1])):
        F, n = wall_frame(t1, o, t0, o) if side < 0 else wall_frame(t0, o, t1, o)
        Fc, _ = wall_frame(t1, NAVE_O[0], t0, NAVE_O[0]) if side < 0 else wall_frame(t0, NAVE_O[1], t1, NAVE_O[1])
        for b in BAYS:
            if not (t0 - 0.1 <= b <= t1 + 0.1): continue
            u = (t1 - b) if side < 0 else (b - t0)
            pbox(bm_for(part, "stone"), F, u - 0.9, u + 0.9, -1.5, 21.5, 0, 0.9)                    # buttress
        for k in range(len(BAYS) - 1):
            m = (BAYS[k] + BAYS[k + 1]) / 2
            if not (t0 <= m <= t1): continue
            u = (t1 - m) if side < 0 else (m - t0)
            opening(part, F, u - 1.1, u + 1.1, 9.0, 19.5, frame=0.35, pointed=True, fill="glass", frame_mat="stone")
            poly(bm_for(part, "glass"), [Fc.p(u + 1.3 * math.cos(a), 29.0 + 1.3 * math.sin(a), 0.06) for a in [i / 16 * 2 * math.pi for i in range(16)]])
            poly(bm_for(part, "stone"), [Fc.p(u + 1.65 * math.cos(a), 29.0 + 1.65 * math.sin(a), 0.03) for a in [i / 16 * 2 * math.pi for i in range(16)]])

def east_end(part):
    """Transept with its chapels, the north end block, the polygonal main chapel."""
    block(part, [(92.8, -31.1), (113.8, -31.1), (113.8, 29.8), (92.8, 29.8)], -1.5, 27.5)
    gable_along_o(part, 92.8, 113.8, -31.6, 30.3, 27.5, 31.4)
    block(part, [(102.6, -39.6), (113.8, -39.6), (113.8, -31.1), (102.6, -31.1)], -1.5, 16.5)
    gable_along_t(part, 102.4, 114.0, -39.9, -30.9, 16.5, 19.0)
    # main chapel: half-octagon beyond the transept, centre o +2.4
    c, r = 2.4, 7.0
    ring = [(113.8, c - r)] + [(113.8 + r * 0.95 * math.sin(a), c - r * math.cos(a)) for a in [k * math.pi / 4 for k in range(1, 4)]] + [(113.8, c + r)]
    block(part, ring, -1.5, 27.0)
    bm = bm_for(part, "roof"); apex = L(113.8, c, 30.5)
    for i in range(len(ring) - 1):
        poly(bm, [L(*ring[i], 27.0), L(*ring[i + 1], 27.0), apex])
    for k in range(1, 4):                                                                          # tall apse windows
        F, n = wall_frame(*ring[k - 1], *ring[k])
        opening(part, F, n / 2 - 0.9, n / 2 + 0.9, 8.0, 22.0, frame=0.3, pointed=True, fill="glass", frame_mat="stone")
    # transept end windows (big lancets on the north and south faces)
    for o, rev in ((29.8, False), (-31.1, True)):
        F, n = wall_frame(113.8, o, 92.8, o) if not rev else wall_frame(92.8, o, 113.8, o)
        opening(part, F, n / 2 - 1.5, n / 2 + 1.5, 10.0, 23.5, frame=0.4, pointed=True, fill="glass", frame_mat="stone")

def facade(part):
    """West front, t = 0: three bays between four pilasters, three portals, the rose window, central gable.
    In the bare phase (before 1863) the kit turns marble to rough masonry and skips the panels."""
    W0, W1 = -21.0, 20.8
    F, n = wall_frame(-1.0, W0, -1.0, W1)                   # 1 m in front of the nave wall; u from the north corner to the south, n = west
    def U(o): return o - W0
    box(bm_for(part, "white"), F, 0, n, -1.5, 23.0, -1.2, 0.0)                                       # side bays
    box(bm_for(part, "white"), F, U(-9.5), U(9.5), 23.0, 33.0, -1.2, 0.0)                           # central bay
    poly(bm_for(part, "white"), [F.p(U(9.8), 33.0, 0.02), F.p(U(-9.8), 33.0, 0.02), F.p(U(0), 42.4, 0.02)])   # gable
    for o0, o1 in ((W1, 9.5), (-9.5, W0)):                                                            # sloping tops of the side bays
        hi = 30.0
        poly(bm_for(part, "white"), [F.p(U(o0), 23.0, 0.02), F.p(U(o1), 23.0, 0.02), F.p(U(o1), hi, 0.02)] if o0 > 0
             else [F.p(U(o0), 23.0, 0.02), F.p(U(o1), 23.0, 0.02), F.p(U(o0), hi, 0.02)])
    panels(part, F, U(-9.0), U(9.0), 11.5, 21.5, 6, 2, accent=lambda i, j: (i + j) % 2 == 0)
    panels(part, F, U(11.6), U(18.0), 11.5, 21.0, 2, 2); panels(part, F, U(-18.0), U(-11.6), 11.5, 21.0, 2, 2)
    panels(part, F, U(-8.0), U(8.0), 30.5, 33.0, 8, 1, accent=lambda i, j: i % 2 == 0)
    for o in (20.0, 10.3, -10.3, -20.0):                                                              # four pilasters with pinnacles
        top = 33.5 if abs(o) < 15 else 30.5
        pilaster(part, F, U(o), -1.5, top, w=1.9, proj=0.8)
        if not K.BARE: pinnacle(part, tuple(F.p(U(o), 0, 0.5)[:2]), top, 4.5, 1.2)       # spires belong to the 1863 front
    # portals: central and two side doors, pointed, with gables
    for o, w, h in ((0.0, 4.2, 9.5), (15.0, 2.6, 6.8), (-15.0, 2.6, 6.8)):
        opening(part, F, U(o) - w / 2, U(o) + w / 2, 0.0, h, frame=0.7, pointed=True, fill="wood", frame_mat="white")
        poly(bm_for(part, "green"), [F.p(U(o) - w / 2 - 1.0, h + 0.6, 0.55), F.p(U(o) + w / 2 + 1.0, h + 0.6, 0.55), F.p(U(o), h + 0.6 + w * 0.75, 0.55)])
    cornice(part, F, U(W0 + 0.2), U(W1 - 0.2), 10.6, h=0.8, proj=0.5, arches=False)
    # rose window (the 14th-century stained-glass oculus, kept in the new front)
    for r, m, d in ((3.6, "white", 0.04), (3.1, "green", 0.07), (2.6, "glass", 0.1)):
        poly(bm_for(part, m), [F.p(U(0) + r * math.cos(a), 26.0 + r * math.sin(a), d) for a in [i / 24 * 2 * math.pi for i in range(24)]])
    # Star of David in the gable (Matas' signature) – only on the 1863 front
    for rot in ((0, math.pi) if not K.BARE else ()):
        poly(bm_for(part, "gold"), [F.p(U(0) + 0.9 * math.sin(a + rot), 37.6 + 0.9 * math.cos(a + rot), 0.12) for a in (0, 2 * math.pi / 3, 4 * math.pi / 3)])

def campanile(part):
    """Baccani's neo-Gothic bell tower (1842–65): stone shaft, belfry with bifore, octagonal spire."""
    t, o, h = 116.7, 25.5, 3.25
    F0 = Frame(L(t, o, 0), Vector((1, 0, 0)), Vector((0, 1, 0)))
    box(bm_for(part, "stone"), F0, -h, h, -1.5, 56.0, -h, h)
    for z in (14.0, 28.0, 42.0, 56.0):
        box(bm_for(part, "stone"), F0, -h - 0.25, h + 0.25, z - 0.4, z + 0.2, -h - 0.25, h + 0.25)
    for k, (uu, nn) in enumerate(((Vector((1, 0, 0)), Vector((0, -1, 0))), (Vector((-1, 0, 0)), Vector((0, 1, 0))),
                                  (Vector((0, 1, 0)), Vector((1, 0, 0))), (Vector((0, -1, 0)), Vector((-1, 0, 0))))):
        F = Frame(L(t, o, 0) + nn * h - uu * h, uu, nn)
        for z0, z1 in ((30.0, 36.0), (44.0, 50.0)):
            opening(part, F, h - 0.6, h + 0.6, z0, z1, frame=0.25, pointed=True, fill="dark", frame_mat="stone")
        opening(part, F, h - 1.6, h + 1.6, 57.5, 64.5, frame=0.35, pointed=True, fill="dark", frame_mat="stone", mullion=True)
        pinnacle(part, tuple((L(t, o, 0) + nn * h + uu * h)[:2]), 66.0, 4.0, 0.8)
    box(bm_for(part, "stone"), F0, -h, h, 56.0, 66.0, -h, h)
    box(bm_for(part, "stone"), F0, -h - 0.4, h + 0.4, 66.0, 66.8, -h - 0.4, h + 0.4)
    bmesh.ops.create_cone(bm_for(part, "stone"), cap_ends=True, segments=8, radius1=2.9, radius2=0.2, depth=9.0,
                          matrix=Matrix.Translation(L(t, o, 71.3)) @ Matrix.Rotation(math.pi / 8, 4, "Z"))
    bmesh.ops.create_cone(bm_for(part, "bronze"), cap_ends=True, segments=6, radius1=0.08, radius2=0.08, depth=1.6,
                          matrix=Matrix.Translation(L(t, o, 76.4)))

east_end(f"santa_croce_east@1300-{NOW}")
nave_segment(f"santa_croce_nave_east@1320-{NOW}", 54.1, 107.0)   # the nave roof runs on over the crossing
nave_segment(f"santa_croce_nave_mid@1350-{NOW}", 28.2, 54.1)
nave_segment(f"santa_croce_nave_west@1385-{NOW}", 0.0, 28.2)
two_phase(facade, "facade", 1385, 1863)
campanile(f"campanile_baccani@1865-{NOW}")
K.export("santa_croce")
