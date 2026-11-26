"""Basilica di Santa Maria Novella – measured, dated model (v1).

Run:  blender -b --python blender/scripts/build_santa_maria_novella.py → web/public/models/landmarks/santa_maria_novella.glb
Frame: origin = middle of the façade at ground (scene x −476.0 / z −254.6); the nave runs due north, so model X = east
(o), Y = north (t, metres from the façade), no rotation. Ground 5.9 m (datum).
Measured (LiDAR 2023 DSM 0.5 m, sections every 4 m; OSM way 449369047):
  façade 33 m wide, side parts ≈18 m, pediment apex ≈34 m · nave 16 m wide, ridge ≈30.5 m · aisles 8 m, roofs ≈17.5 m
  nave to t ≈79 m · transept t 79–92 m, ridge ≈28 m, lower chapels on both arms · main chapel to t 103 m
  bell tower o −23 / t 80 (north-west), ≈6.5 m square, top 63.9 m.
Dates (docs/landmarks/SANTA-MARIA-NOVELLA.md): Dominican church begun 1279 from the east end; transept and chapels
c. 1300, nave westwards to c. 1357 (stages *inferred*); bell tower by c. 1330 (Fra Jacopo Talenti); lower marble façade
(Gothic, with the avelli) c. 1360; Leon Battista Alberti's upper façade and portal for Giovanni Rucellai, 1458–70.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
K.reset()
MAT["stone"] = material("pietra_forte", "pietra_forte", (0.62, 0.5, 0.36), 0.85, 0.32, tint=(3.0, 2.85, 2.55))

def L(t, o, z=0.0): return Vector((o, t, z))                      # t north from the façade, o east
def wall_frame(t0, o0, t1, o1):
    a, b = L(t0, o0), L(t1, o1); d = b - a; n = d.length; uu = d / n
    return Frame(a, uu, Vector((uu.y, -uu.x, 0))), n                # right of the walking direction = outside

def block(part, outline, z0, z1, mat="stone"):
    bm = bm_for(part, mat); P = [L(t, o) for t, o in outline]
    bot = [bm.verts.new((p.x, p.y, z0)) for p in P]; top = [bm.verts.new((p.x, p.y, z1)) for p in P]
    for f in (top, bot[::-1]):
        try: bm.faces.new(f)
        except ValueError: pass
    for i in range(len(P)):
        j = (i + 1) % len(P)
        try: bm.faces.new((bot[i], bot[j], top[j], top[i]))
        except ValueError: pass

def rect(t0, t1, o0, o1): return [(t0, o0), (t0, o1), (t1, o1), (t1, o0)]   # clockwise seen from above
def gable_t(part, t0, t1, o0, o1, ze, zr):
    om = (o0 + o1) / 2; bm = bm_for(part, "roof")
    poly(bm, [L(t0, o0, ze), L(t1, o0, ze), L(t1, om, zr), L(t0, om, zr)]); poly(bm, [L(t1, o1, ze), L(t0, o1, ze), L(t0, om, zr), L(t1, om, zr)])
    for t in (t0, t1): poly(bm_for(part, "stone"), [L(t, o0, ze), L(t, o1, ze), L(t, om, zr)])
def gable_o(part, t0, t1, o0, o1, ze, zr):
    tm = (t0 + t1) / 2; bm = bm_for(part, "roof")
    poly(bm, [L(t0, o0, ze), L(t0, o1, ze), L(tm, o1, zr), L(tm, o0, zr)]); poly(bm, [L(t1, o1, ze), L(t1, o0, ze), L(tm, o0, zr), L(tm, o1, zr)])
    for o in (o0, o1): poly(bm_for(part, "stone"), [L(t0, o, ze), L(t1, o, ze), L(tm, o, zr)])

NAVE, AISLE = (-8.0, 8.0), (-16.4, 16.6)

def nave(part, t0, t1):
    block(part, rect(t0, t1, *AISLE), -1.5, 16.5)
    block(part, rect(t0, t1, *NAVE), 16.5, 27.0)
    gable_t(part, t0, t1, NAVE[0] - 0.5, NAVE[1] + 0.5, 27.0, 30.5)
    for oo, oi in ((AISLE[0] - 0.4, NAVE[0]), (AISLE[1] + 0.4, NAVE[1])):
        poly(bm_for(part, "roof"), [L(t0, oo, 16.5), L(t1, oo, 16.5), L(t1, oi, 19.0), L(t0, oi, 19.0)])
    for o, sgn in ((AISLE[0], -1), (AISLE[1], 1)):                    # aisle windows and buttresses, clerestory oculi
        F, n = wall_frame(t1, o, t0, o) if sgn < 0 else wall_frame(t0, o, t1, o)
        Fc, _ = wall_frame(t1, NAVE[0], t0, NAVE[0]) if sgn < 0 else wall_frame(t0, NAVE[1], t1, NAVE[1])
        bay = 11.5; k = int((t1 - t0) / bay)
        for i in range(k):
            m = t0 + (i + 0.5) * (t1 - t0) / k; u = (t1 - m) if sgn < 0 else (m - t0)
            opening(part, F, u - 0.9, u + 0.9, 6.5, 14.0, frame=0.3, pointed=True, fill="glass", frame_mat="stone")
            poly(bm_for(part, "glass"), [Fc.p(u + 1.1 * math.cos(a), 23.0 + 1.1 * math.sin(a), 0.06) for a in [j / 16 * 2 * math.pi for j in range(16)]])
            ub = (t1 - (t0 + i * (t1 - t0) / k)) if sgn < 0 else (i * (t1 - t0) / k)
            pbox(bm_for(part, "stone"), F, ub - 0.7, ub + 0.7, -1.5, 15.5, 0, 0.8)

def east_end(part):
    block(part, rect(79.0, 92.0, -24.0, 24.0), -1.5, 25.0); gable_o(part, 79.0, 92.0, -24.5, 24.5, 25.0, 28.0)
    block(part, rect(60.0, 79.0, -26.6, -16.4), -1.5, 18.0); gable_t(part, 60.0, 79.0, -26.9, -16.1, 18.0, 20.0)   # west chapels
    block(part, rect(66.0, 87.0, 16.6, 35.0), -1.5, 13.5); gable_t(part, 66.0, 87.0, 16.3, 35.3, 13.5, 15.5)        # east chapels
    block(part, rect(92.0, 103.0, -8.0, 8.0), -1.5, 26.0); gable_t(part, 92.0, 103.4, -8.4, 8.4, 26.0, 28.5)      # main chapel
    for o0, o1 in ((-24.0, -8.0), (8.0, 24.0)):
        block(part, rect(92.0, 99.0, o0, o1), -1.5, 16.0); gable_t(part, 92.0, 99.4, o0 - 0.3, o1 + 0.3, 16.0, 17.5)
    F, n = wall_frame(103.0, 8.0, 103.0, -8.0)                       # tall east window (the Ghirlandaio choir behind it)
    opening(part, F, n / 2 - 1.4, n / 2 + 1.4, 7.0, 21.0, frame=0.35, pointed=True, fill="glass", frame_mat="stone", mullion=True)

def facade_lower(part):
    """Gothic lower order (c. 1360): striped corner pilasters, avelli (tomb arcades) along the base, two side doors,
    green-and-white bands, the frieze; the central portal is Alberti's (shown with the upper order)."""
    W0, W1 = AISLE
    F, n = wall_frame(-1.0, W0, -1.0, W1)                            # 1 m in front of the church wall; u from west to east, n = south
    U = lambda o: o - W0
    box(bm_for(part, "white"), F, 0, n, -1.5, 18.0, -1.2, 0.0)
    for o in (W1 - 0.9, W0 + 0.9): pilaster(part, F, U(o), -1.5, 18.0, w=1.8, proj=0.6)
    for o in (8.3, -8.3): pilaster(part, F, U(o), -1.5, 18.0, w=1.3, proj=0.5)
    for i in range(12):                                              # avelli: pointed blind arches on the plinth
        u = 0.8 + (i + 0.5) * (n - 1.6) / 12
        if abs(u - U(0)) < 3.2: continue                            # the central portal
        opening(part, F, u - 0.75, u + 0.75, 0.3, 3.2, depth=0.2, frame=0.18, pointed=True, fill="green", frame_mat="white")
    for o in (12.0, -12.0):
        opening(part, F, U(o) - 1.0, U(o) + 1.0, 0.0, 5.4, frame=0.45, pointed=True, fill="wood", frame_mat="green")
    for v in (4.0, 8.0, 12.0): pbox(bm_for(part, "green"), F, 0.2, n - 0.2, v, v + 0.25, 0, 0.05)
    panels(part, F, U(-7.7), U(7.7), 6.0, 15.5, 4, 2, accent=lambda i, j: False)
    pbox(bm_for(part, "green"), F, 0, n, 17.3, 18.0, 0, 0.35)
    for i in range(16):                                              # frieze of inlaid squares
        u = (i + 0.5) * n / 16; box(bm_for(part, "white"), F, u - 0.5, u + 0.5, 17.4, 17.9, 0.35, 0.4)

def facade_upper(part):
    """Alberti's upper order (1458–70): attic band, central temple front with pilasters and the rose window, pediment with
    the sun, scroll volutes on both sides, and the round-arched central portal. In the bare phase it is the rough wall."""
    W0, W1 = AISLE
    F, n = wall_frame(-1.0, W0, -1.0, W1)
    U = lambda o: o - W0
    box(bm_for(part, "white"), F, U(-8.0), U(8.0), 18.0, 29.0, -1.2, 0.0)
    box(bm_for(part, "white"), F, 0, n, 18.0, 21.0, -1.2, 0.0)       # attic
    poly(bm_for(part, "white"), [F.p(U(8.6), 29.0, 0.02), F.p(U(-8.6), 29.0, 0.02), F.p(U(0), 34.0, 0.02)])
    for r, m, d in ((2.8, "white", 0.04), (2.4, "green", 0.07), (2.0, "glass", 0.1)):        # rose window (14th c.)
        poly(bm_for(part, m), [F.p(U(0) + r * math.cos(a), 24.5 + r * math.sin(a), d) for a in [i / 24 * 2 * math.pi for i in range(24)]])
    if K.BARE: return
    panels(part, F, 0.4, n - 0.4, 18.3, 20.7, 14, 1, accent=lambda i, j: False)
    for o in (7.6, 3.2, -3.2, -7.6): pilaster(part, F, U(o), 21.0, 28.6, w=0.9, proj=0.35)
    pbox(bm_for(part, "green"), F, U(-8.8), U(8.8), 28.6, 29.2, 0, 0.45)
    for s in (1, -1):                                                # scroll volutes: high at the temple front, down to the attic ends
        cx = 8.0 * s; R = 6.2; H = 6.0
        curve = [F.p(U(cx + s * R * math.sin(a)), 21.0 + H * math.cos(a), 0.05) for a in [k / 16 * math.pi / 2 for k in range(17)]]
        poly(bm_for(part, "white"), [F.p(U(cx), 21.0, 0.05)] + (curve if s < 0 else curve[::-1]))
        for r_, m in ((1.5, "green"), (0.95, "white"), (0.4, "green")):
            poly(bm_for(part, m), [F.p(U(cx + s * 2.6) + r_ * math.cos(a), 23.4 + r_ * math.sin(a), 0.09) for a in [i / 16 * 2 * math.pi for i in range(16)]])
    for r_, m in ((1.3, "white"), (0.9, "gold")):                    # the Rucellai sun in the pediment
        poly(bm_for(part, m), [F.p(U(0) + r_ * math.cos(a), 31.0 + r_ * math.sin(a), 0.1) for a in [i / 16 * 2 * math.pi for i in range(16)]])
    opening(part, F, U(0) - 1.8, U(0) + 1.8, 0.0, 8.6, frame=0.6, pointed=False, fill="wood", frame_mat="green")
    for o in (3.0, -3.0): pbox(bm_for(part, "green"), F, U(o) - 0.35, U(o) + 0.35, 0.0, 9.8, 0, 0.6)   # half-columns by the portal

def campanile(part):
    t, o, h = 80.2, -23.0, 3.25
    F0 = Frame(L(t, o, 0), Vector((1, 0, 0)), Vector((0, 1, 0)))
    box(bm_for(part, "stone"), F0, -h, h, -1.5, 50.0, -h, h)
    for z in (20.0, 30.0, 40.0): box(bm_for(part, "white"), F0, -h - 0.15, h + 0.15, z, z + 0.4, -h - 0.15, h + 0.15)
    for uu, nn in ((Vector((1, 0, 0)), Vector((0, -1, 0))), (Vector((-1, 0, 0)), Vector((0, 1, 0))), (Vector((0, 1, 0)), Vector((1, 0, 0))), (Vector((0, -1, 0)), Vector((-1, 0, 0)))):
        Fs = Frame(L(t, o, 0) + nn * h - uu * h, uu, nn)
        for z0, z1 in ((32.0, 37.0), (42.0, 48.0)): opening(part, Fs, h - 0.5, h + 0.5, z0, z1, frame=0.22, pointed=True, fill="dark", frame_mat="white")
        opening(part, Fs, h - 1.5, h + 1.5, 50.5, 55.5, frame=0.3, pointed=True, fill="dark", frame_mat="white", mullion=True)
    box(bm_for(part, "stone"), F0, -h, h, 50.0, 56.5, -h, h)
    box(bm_for(part, "white"), F0, -h - 0.35, h + 0.35, 56.5, 57.2, -h - 0.35, h + 0.35)
    bmesh.ops.create_cone(bm_for(part, "brick"), cap_ends=True, segments=4, radius1=h * 1.38, radius2=0.15, depth=6.4,
                          matrix=Matrix.Translation(L(t, o, 60.4)) @ Matrix.Rotation(math.pi / 4, 4, "Z"))
    bmesh.ops.create_cone(bm_for(part, "bronze"), cap_ends=True, segments=6, radius1=0.06, radius2=0.06, depth=1.4, matrix=Matrix.Translation(L(t, o, 64.2)))

east_end(f"smn_east@1300-{NOW}")
nave(f"smn_nave_east@1330-{NOW}", 30.0, 79.4)
nave(f"smn_nave_west@1357-{NOW}", 0.0, 30.0)
campanile(f"campanile_smn@1330-{NOW}")
facade_lower(f"facade_lower@1360-{NOW}")
two_phase(facade_upper, "facade_upper", 1360, 1470)
K.export("santa_maria_novella")
