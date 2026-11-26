"""Loggia dei Lanzi (Loggia della Signoria) – measured, dated model (v1) with its statues.

Run:  blender -b --python blender/scripts/build_loggia_lanzi.py  →  web/public/models/landmarks/loggia_lanzi.glb
Frame: origin = west front corner on the piazza (scene x 22.8 / z 275.8); X along the front towards the Uffizi corner,
Y out to the piazza (north-north-west), Z up; the app rotates it by −0.3696 rad (front at 21.2° to the grid).
Ground 9.6 (DTM 49.6 m a.s.l.). Outline: OSM way 43284457, ≈39 × 13 m.
Measured (LiDAR 2023 DSM 0.5 m): roof terrace ≈21.3 m, balustrade ≈22.4 m above the piazza.
Dates (docs/landmarks/LOGGIA-DEI-LANZI.md): built 1376–82 (Benci di Cione, Simone Talenti); Virtues in the spandrels
1384–89 (Agnolo Gaddi's designs); roof terrace with balustrade c. 1585 (Buontalenti, *inferred*); Judith 1506–82
(*inferred*); Perseus 1554; Rape of the Sabines 1583; Medici lions and the Roman matrons 1789; Menelaus 1838 and
Hercules and Nessus 1841 (*inferred* years, "19th century" in the sources); Rape of Polyxena 1865.
East side open onto the Piazzale degli Uffizi (one arch), west side closed. Statues are stand-ins (pedestal and figure masses at their places and sizes), to be refined.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
K.reset()
MAT["stone"] = material("pietra_forte", "pietra_forte", (0.62, 0.5, 0.36), 0.85, 0.32, tint=(3.0, 2.85, 2.55))
MAT["serena"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)
MAT["bronze"] = material("bronze_patina", None, (0.2, 0.17, 0.11), 0.45, metal=0.75)
MAT["marble"] = material("statue_marble", None, (0.9, 0.88, 0.84), 0.45)

L, D = 39.0, 13.0                 # front length, depth (Y from 0 at the front to −D at the back wall)
FLOOR = 1.3                       # the loggia floor stands on steps above the piazza
PIER = 2.2                        # composite piers
SPAN = (L - 4 * PIER) / 3         # three front arches ≈10.1 m
SPRING, TOP = FLOOR + 10.6, 21.3  # springing of the arches, roof terrace
ARCH_R = SPAN / 2

Ffront = Frame((0, 0, 0), (1, 0, 0), (0, 1, 0))       # u along the front, n towards the piazza
Fwest = Frame((0, -D, 0), (0, 1, 0), (-1, 0, 0))      # west side, u from the back to the front
Fback = Frame((L, -D, 0), (-1, 0, 0), (0, -1, 0))
Feast = Frame((L, 0, 0), (0, -1, 0), (1, 0, 0))

def arcade(part, F, Lf, n_arches, depth=1.2):
    """Wall with round arches on composite piers (the openings are left open: the wall is built around them)."""
    span = (Lf - (n_arches + 1) * PIER) / n_arches; r = span / 2
    bm = bm_for(part, "serena")
    for i in range(n_arches + 1):                                  # piers with a moulded base and capital
        u0 = i * (span + PIER)
        box(bm, F, u0, u0 + PIER, FLOOR, SPRING, -depth, 0)
        box(bm_for(part, "stone"), F, u0 - 0.15, u0 + PIER + 0.15, FLOOR, FLOOR + 0.8, -depth - 0.15, 0.15)
        box(bm_for(part, "stone"), F, u0 - 0.2, u0 + PIER + 0.2, SPRING - 0.9, SPRING, -depth - 0.2, 0.2)
    for i in range(n_arches):                                      # arch rings + spandrel walls up to the cornice
        c = i * (span + PIER) + PIER + r
        seg = 16
        for k in range(seg):
            a0, a1 = math.pi * k / seg, math.pi * (k + 1) / seg
            p = [(c + r * math.cos(a0), SPRING + r * math.sin(a0)), (c + r * math.cos(a1), SPRING + r * math.sin(a1))]
            q = [(c + (r + 0.9) * math.cos(a0), SPRING + (r + 0.9) * math.sin(a0)), (c + (r + 0.9) * math.cos(a1), SPRING + (r + 0.9) * math.sin(a1))]
            for nn in (0, -depth):
                poly(bm_for(part, "serena"), [F.p(p[0][0], p[0][1], nn), F.p(p[1][0], p[1][1], nn), F.p(q[1][0], q[1][1], nn), F.p(q[0][0], q[0][1], nn)])
            poly(bm_for(part, "serena"), [F.p(p[0][0], p[0][1], 0), F.p(p[0][0], p[0][1], -depth), F.p(p[1][0], p[1][1], -depth), F.p(p[1][0], p[1][1], 0)])   # soffit
            # spandrel: from the outer ring up to the frieze
            for nn in (0, -depth):
                poly(bm_for(part, "stone"), [F.p(q[0][0], q[0][1], nn), F.p(q[1][0], q[1][1], nn), F.p(q[1][0], TOP - 3.0, nn), F.p(q[0][0], TOP - 3.0, nn)])
        # the side bits of the spandrels above the piers
        box(bm_for(part, "stone"), F, c - r - PIER / 2 - 0.01, c - r - 0.85, SPRING, TOP - 3.0, -depth, 0)
        box(bm_for(part, "stone"), F, c + r + 0.85, c + r + PIER / 2 + 0.01, SPRING, TOP - 3.0, -depth, 0)
    box(bm_for(part, "stone"), F, -0.3, Lf + 0.3, TOP - 3.0, TOP, -depth, 0)                    # frieze band
    box(bm_for(part, "serena"), F, -0.6, Lf + 0.6, TOP - 0.8, TOP, -depth, 0.55)                # cornice
    for i in range(int(Lf / 1.1)):                                                               # small corbels under it
        u = 0.5 + i * 1.1; pbox(bm_for(part, "serena"), F, u - 0.15, u + 0.15, TOP - 1.4, TOP - 0.8, 0, 0.45)
    return span

def virtues(part, F, Lf, n_arches):
    """Quatrefoil panels with the seated Virtues between the arches (blue enamel ground, white figures)."""
    span = (Lf - (n_arches + 1) * PIER) / n_arches
    for i in range(n_arches + 1):
        c = i * (span + PIER) + PIER / 2; v = SPRING + span / 2 + 1.6
        if v + 1.4 > TOP - 3.0: v = TOP - 4.5
        pts = []
        for k in range(32):
            a = 2 * math.pi * k / 32; rr = 1.05 + 0.28 * abs(math.cos(2 * a))
            pts.append(F.p(c + rr * math.cos(a), v + rr * math.sin(a), 0.06))
        poly(bm_for(part, "dark"), pts)
        box(bm_for(part, "marble"), F, c - 0.35, c + 0.35, v - 0.8, v + 0.7, 0.06, 0.2)

# ---- the loggia, 1376–82 ----
P = "loggia@1376-" + str(NOW)
wbox(bm_for(P, "stone"), 0, L, -D, 0, 0, FLOOR)                                                   # raised floor
for k in range(4):                                                                                # steps on the piazza side
    wbox(bm_for(P, "stone"), -0.4, L + 0.4, 0.45 * k, 0.45 * (k + 1), 0, FLOOR - FLOOR * k / 4)
arcade(P, Ffront, L, 3)
arcade(P, Feast, D, 1)                                                                            # the side arch opens onto the Piazzale degli Uffizi
wall(P, Fback, 0, L, 0, TOP, 1.4, "stone")                                                        # back wall (to the Uffizi range)
wall(P, Fwest, 0, D, 0, TOP, 1.4, "stone")                                                        # west side, against the houses on Via Vacchereccia
for i in range(6):                                                                                # niches in the back wall
    u = 3.5 + i * (L - 7) / 5
    opening(P, Fback, u - 0.9, u + 0.9, FLOOR + 0.4, FLOOR + 4.2, depth=0.4, frame=0.25, pointed=False, fill="dark", frame_mat="serena")
wbox(bm_for(P, "white"), 0, L, -D, 0, TOP - 1.0, TOP - 0.6)                                       # vault ceiling (simplified as a flat soffit)
for i in range(3):                                                                                # cross vaults: ribs
    x0 = PIER + i * (SPAN + PIER); x1 = x0 + SPAN
    for (a, b) in (((x0, 0), (x1, -D)), ((x1, 0), (x0, -D))):
        n = 10
        for k in range(n):
            t0, t1 = k / n, (k + 1) / n
            pa = (a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0); pb = (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)
            z0 = SPRING + (TOP - 1.0 - SPRING) * math.sin(math.pi * t0); z1 = SPRING + (TOP - 1.0 - SPRING) * math.sin(math.pi * t1)
            wbox(bm_for(P, "serena"), min(pa[0], pb[0]) - 0.15, max(pa[0], pb[0]) + 0.15, min(pa[1], pb[1]) - 0.15, max(pa[1], pb[1]) + 0.15, min(z0, z1) - 0.3, max(z0, z1))
wbox(bm_for(P, "stone"), 0, L, -D, 0, TOP, TOP + 0.6)                                             # parapet / roof
wbox(bm_for(P, "serena"), 0.6, L - 0.6, -D + 0.6, -0.6, TOP + 0.6, TOP + 0.66)   # stone-paved roof terrace

virtues("virtues@1384-" + str(NOW), Ffront, L, 3)
virtues("virtues@1384-" + str(NOW), Feast, D, 1)

# roof terrace with balustrade (part of the Uffizi works, c. 1585 – inferred date)
B = "terrace@1585-" + str(NOW)
for F, Lf in ((Ffront, L), (Feast, D)):
    box(bm_for(B, "stone"), F, -0.6, Lf + 0.6, TOP + 0.6, TOP + 0.75, -0.3, 0.3)
    for i in range(int(Lf / 0.35)):
        u = 0.15 + i * 0.35; box(bm_for(B, "serena"), F, u - 0.08, u + 0.08, TOP + 0.75, TOP + 1.65, -0.15, 0.15)
    box(bm_for(B, "stone"), F, -0.6, Lf + 0.6, TOP + 1.65, TOP + 1.85, -0.25, 0.25)

# ---- statues ----
def figure(part, x, y, base_w, base_h, fig_h, mat="marble", group=1, rot=0.0):
    """Stand-in statue: pedestal and one or more figure masses (a group reads as a cluster)."""
    F = Frame((x, y, 0), (math.cos(rot), math.sin(rot), 0), (-math.sin(rot), math.cos(rot), 0))
    box(bm_for(part, "stone" if mat == "bronze" else "white"), F, -base_w / 2, base_w / 2, FLOOR, FLOOR + base_h, -base_w / 2, base_w / 2)
    z = FLOOR + base_h
    for g in range(group):
        dx = (g - (group - 1) / 2) * 0.45; h = fig_h * (1 - 0.18 * g)
        box(bm_for(part, mat), F, dx - 0.28, dx + 0.28, z, z + h * 0.82, -0.2, 0.2)                 # body
        box(bm_for(part, mat), F, dx - 0.13, dx + 0.13, z + h * 0.82, z + h, -0.13, 0.13)           # head
        box(bm_for(part, mat), F, dx + 0.2, dx + 0.6, z + h * 0.55, z + h * 0.65, -0.08, 0.08)      # arm
xL, xC, xR = PIER + SPAN / 2, 2 * PIER + 1.5 * SPAN, 3 * PIER + 2.5 * SPAN
figure("judith@1506-1582", xL, -1.8, 1.2, 2.0, 2.4, "bronze", 2)                                   # Donatello's Judith, under the right arch until the Sabines took its place (inferred)
figure(f"perseus@1554-{NOW}", xR, -1.6, 1.4, 3.0, 3.2, "bronze", 1)                               # Cellini, under the left arch (east, seen from the piazza)
figure(f"sabines@1583-{NOW}", xL, -1.8, 1.8, 2.6, 4.1, "marble", 3)                                # Giambologna, under the right arch (west)
figure(f"menelaus@1838-{NOW}", xR, -8.0, 1.6, 1.6, 2.5, "marble", 2)                               # Roman group (19th c.)
figure(f"hercules_nessus@1841-{NOW}", xL, -7.5, 1.7, 1.6, 2.7, "marble", 2)                        # Giambologna 1599, placed 19th c.
figure(f"polyxena@1865-{NOW}", xC, -6.5, 1.8, 1.4, 3.3, "marble", 3)                              # Pio Fedi 1865
for i in range(6):                                                                                 # Roman matrons along the back wall (1789)
    u = 3.5 + i * (L - 7) / 5
    figure(f"matrons@1789-{NOW}", u, -D + 1.6, 0.9, 1.0, 2.3, "marble", 1)
for s in (-1, 1):                                                                                  # Medici lions flanking the central steps (1789)
    x = xC + s * (SPAN / 2 - 0.6)
    Fl = Frame((x, -0.8, 0), (1, 0, 0), (0, 1, 0))
    box(bm_for(f"lions@1789-{NOW}", "white"), Fl, -0.5, 0.5, FLOOR, FLOOR + 1.3, -1.1, 1.1)                       # plinth
    box(bm_for(f"lions@1789-{NOW}", "marble"), Fl, -0.35, 0.35, FLOOR + 1.3, FLOOR + 2.1, -0.9, 0.7)              # body
    box(bm_for(f"lions@1789-{NOW}", "marble"), Fl, -0.3, 0.3, FLOOR + 1.9, FLOOR + 2.6, 0.5, 1.0)                 # head and mane

K.export("loggia_lanzi")
