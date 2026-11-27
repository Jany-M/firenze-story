"""Baptistery of San Giovanni – measured, dated model (v1).

Run:  blender -b --python blender/scripts/build_baptistery.py   →  web/public/models/landmarks/baptistery.glb
Frame: origin = centre of the octagon at ground level (LiDAR 2023 lantern top: scene x −14.0 / z −149.0), X east, Y north.
Measured (DSM 0.5 m): octagon apothem 16 m over the pilasters (flats facing the cardinal points), attic edge 23.4 m,
white marble roof pyramid rising to 33.8 m at the lantern, lantern + ball + cross to 39.3 m; rectangular scarsella to
the west, roof at 13 m. Elevation in three orders as in photographs: pilastered lower order with panelled bays and the
three doors (E, N, S), upper order with three round arches and window aedicules per face, striped attic.
Dates: consecrated 1059; marble revetment of the lower and upper orders 1059–1128 (cladding years conjectural);
pyramid roof 1128, lantern 1150, scarsella 1202, striped attic pilasters (trad. Arnolfo) c. 1293;
bronze doors: south (Andrea Pisano) 1336, north (Ghiberti) 1424, east "Gates of Paradise" (Ghiberti) 1452.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
K.reset()

A = 15.6                           # apothem of the wall faces; pilasters stand 0.4 m proud
Z1, Z2, Z3 = 10.2, 18.6, 23.4      # lower order, upper order, attic top
DOORS = {0: (1452, "east"), 2: (1424, "north"), 6: (1336, "south")}

def lower(part):
    for k in range(8):
        F, W = oct_face(k, A)
        wall(part, F, 0, W, 0, Z1, 2.0)
        for b in range(3):                                                                         # plinth (not across the doors)
            if not (b == 1 and k in DOORS): pbox(bm_for(part, "white"), F, b * W / 3, (b + 1) * W / 3, 0, 0.9, 0, 0.5)
        for u in (0.0, W / 3, 2 * W / 3, W):                                                       # pilasters, corners striped
            pilaster(part, F, u, 0.9, Z1 - 0.6, 1.0 if 0 < u < W else 1.3, 0.4, stripes=u in (0.0, W))
        for b in range(3):
            a0, a1 = b * W / 3 + 0.8, (b + 1) * W / 3 - 0.8
            if b == 1 and k in DOORS: continue
            panels(part, F, a0, a1, 1.2, Z1 - 1.0, 1, 3, accent=lambda i, j: j == 1)
        cornice(part, F, -0.3, W + 0.3, Z1 - 0.6, 0.9, 0.7, arches=False)

def doors(k, part_frame, part_door):
    F, W = oct_face(k, A)
    u0, u1 = W / 2 - 1.6, W / 2 + 1.6
    w = bm_for(part_frame, "white")                                                                  # marble door frame (jambs + lintel)
    box(w, F, u0 - 0.7, u0, 0, 7.4, 0, 0.55); box(w, F, u1, u1 + 0.7, 0, 7.4, 0, 0.55); box(w, F, u0, u1, 7.2, 7.4, 0, 0.55)
    pbox(bm_for(part_frame, "green"), F, u0 - 0.7, u1 + 0.7, 7.4, 7.8, 0, 0.65)
    pbox(bm_for(part_frame, "white"), F, u0 - 0.9, u1 + 0.9, 7.8, 8.4, 0, 0.75)                      # architrave (bronze groups above not modelled)
    return F, u0, u1

def upper(part):
    for k in range(8):
        F, W = oct_face(k, A)
        wall(part, F, 0, W, Z1, Z2, 2.0)
        for u in (0.0, W / 3, 2 * W / 3, W):
            pilaster(part, F, u, Z1 + 0.3, Z2 - 0.5, 0.9 if 0 < u < W else 1.2, 0.35, stripes=u in (0.0, W))
        for b in range(3):                                                                         # round arches
            a0, a1 = b * W / 3 + 0.45, (b + 1) * W / 3 - 0.45
            opening(part, F, a0, a1, Z1 + 0.4, Z2 - 0.7, depth=0.2, frame=0.32, pointed=False, fill="white", frame_mat="green")
            panels(part, F, a0 + 0.4, a1 - 0.4, Z1 + 0.6, Z1 + 2.2, 2, 1, proud=0.14)                     # in front of the arch's fill (0.05)
            m = (a0 + a1) / 2                                                                      # window aedicule
            opening(part, F, m - 0.55, m + 0.55, Z1 + 2.8, Z1 + 5.9, depth=0.2, frame=0.22, pointed=False, fill="dark", frame_mat="white", lift=0.12)
            ped = bm_for(part, "white")
            if b == 1: poly(ped, [F.p(m - 1.0, Z1 + 6.2, 0.3), F.p(m + 1.0, Z1 + 6.2, 0.3), F.p(m, Z1 + 7.0, 0.3)])
            else: poly(ped, [F.p(m + 0.95 * math.cos(a), Z1 + 6.2 + 0.6 * math.sin(a), 0.3) for a in [i / 10 * math.pi for i in range(11)]])
        cornice(part, F, -0.3, W + 0.3, Z2 - 0.5, 0.8, 0.6, arches=False)

def attic(part):
    for k in range(8):
        F, W = oct_face(k, A)
        wall(part, F, 0, W, Z2, Z3, 1.6)
        n = 14
        for i in range(n):                                                                         # white / green striped pilasters
            u = (i + 0.5) * W / n
            pbox(bm_for(part, "green" if i % 2 else "white"), F, u - 0.32, u + 0.32, Z2 + 0.5, Z3 - 0.6, 0, 0.18)
        cornice(part, F, -0.35, W + 0.35, Z3 - 0.6, 0.6, 0.55, arches=False)

def roof(part):
    """Flattened octagonal pyramid in white marble slabs, from the attic edge to the lantern ring, with ribs."""
    bm = bm_for(part, "white"); rib = bm_for(part, "green")
    R0, R1, H0, H1 = A + 0.2, 2.1, Z3 - 0.1, 33.8
    for k in range(8):
        c0 = (oct_dir(k) + oct_dir(k - 1)).normalized() / math.cos(math.pi / 8); c1 = (oct_dir(k) + oct_dir(k + 1)).normalized() / math.cos(math.pi / 8)
        poly(bm, [c0 * R0 + Vector((0, 0, H0)), c1 * R0 + Vector((0, 0, H0)), c1 * R1 + Vector((0, 0, H1)), c0 * R1 + Vector((0, 0, H1))])
        s = Vector((-c1.y, c1.x, 0)).normalized() * 0.25
        quad_strip(rib, [c1 * R0 + s + Vector((0, 0, H0 + 0.05)), c1 * R1 + s + Vector((0, 0, H1 + 0.05))],
                        [c1 * R0 - s + Vector((0, 0, H0 + 0.05)), c1 * R1 - s + Vector((0, 0, H1 + 0.05))])

def lantern(part):
    z0 = 33.8
    bm = bm_for(part, "white")
    bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=2.2, radius2=2.2, depth=0.5, matrix=Matrix.Translation((0, 0, z0 + 0.25)))
    for i in range(8):                                                                              # columns
        a = (i + 0.5) * math.pi / 4
        bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.14, radius2=0.14, depth=2.4, matrix=Matrix.Translation((1.7 * math.cos(a), 1.7 * math.sin(a), z0 + 1.7)))
    bmesh.ops.create_cone(bm_for(part, "dark"), cap_ends=True, segments=8, radius1=1.45, radius2=1.45, depth=2.4, matrix=Matrix.Translation((0, 0, z0 + 1.7)))
    bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=2.1, radius2=2.1, depth=0.45, matrix=Matrix.Translation((0, 0, z0 + 3.1)))
    bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=1.9, radius2=0.15, depth=1.6, matrix=Matrix.Translation((0, 0, z0 + 4.1)))
    g = bm_for(part, "gold")
    bmesh.ops.create_uvsphere(g, u_segments=12, v_segments=8, radius=0.35, matrix=Matrix.Translation((0, 0, z0 + 5.1)))
    wbox(g, -0.06, 0.06, -0.06, 0.06, z0 + 5.4, 39.3)
    wbox(g, -0.06, 0.06, -0.45, 0.45, 38.4, 38.55)

def scarsella(part):
    """Rectangular chancel on the west face (1202), clad like the lower order."""
    x0, x1, hw, H = -A - 7.2, -A + 0.5, 4.6, 12.6
    for F, L in ((Frame((x0, -hw, 0), (0, 1, 0), (-1, 0, 0)), 2 * hw), (Frame((x0, hw, 0), (1, 0, 0), (0, 1, 0)), x1 - x0),
                 (Frame((x1, -hw, 0), (-1, 0, 0), (0, -1, 0)), x1 - x0)):
        wall(part, F, 0, L, 0, H, 1.2)
        pilaster(part, F, 0.6, 0.9, H - 0.8, 1.0, 0.35); pilaster(part, F, L - 0.6, 0.9, H - 0.8, 1.0, 0.35)
        panels(part, F, 1.4, L - 1.4, 1.2, H - 1.4, 3 if L > 8 else 2, 3, accent=lambda i, j: j == 1)
        cornice(part, F, -0.2, L + 0.2, H - 0.8, 0.8, 0.5, arches=False)
    gable_roof(part, x0 - 0.3, x1, -hw - 0.4, hw + 0.4, H, H + 1.4, mat="white")

two_phase(lower, "baptistery_lower", 1059, 1090)          # cladding years conjectural (1059–1128)
two_phase(upper, "baptistery_upper", 1080, 1110)
two_phase(attic, "baptistery_attic", 1110, 1128)
roof(f"baptistery_roof@1128-{NOW}")
lantern(f"baptistery_lantern@1150-{NOW}")
scarsella(f"scarsella@1202-{NOW}")
for k, (yr, side) in DOORS.items():
    F, u0, u1 = doors(k, f"doorframe_{side}@1059-{NOW}", None)
    opening(f"door_{side}_wood@1059-{yr}", F, u0, u1, 0, 7.2, depth=0.3, frame=0.05, pointed=False, fill="wood", frame_mat="white")
    opening(f"door_{side}_bronze@{yr}-{NOW}", F, u0, u1, 0, 7.2, depth=0.3, frame=0.05, pointed=False, fill="bronze" if side != "east" else "gold", frame_mat="white")
K.export("baptistery")
