"""The Boboli garden's built pieces and Forte Belvedere – dated model (v1).

Run:  python pipeline/42_pitti.py   (once: outlines, ground, LiDAR → blender/data/pitti.json)
      blender -b --python blender/scripts/build_boboli.py  →  web/public/models/landmarks/boboli.glb
Frame: absolute scene coordinates (Blender X = scene x, Blender Y = −scene z, Z = scene y); placed at [0, 0], rot 0, ground 0.
Pieces (OSM outlines, docs/landmarks/PITTI-BOBOLI.md): the amphitheatre (way 473825738) – a hollow left by quarrying stone
for the palace, tiers of stone seats 1599, the edicules and urns of Giulio and Alfonso Parigi c. 1630–34 (inaugurated 1637),
the Egyptian obelisk 1790 and the granite basin (1840, *inferred*); the Grotta del Buontalenti 1583–93 (way 473825750);
the Kaffeehaus of Zanobi del Rosso 1776 (way 267801118); the Neptune basin 1777–78 with Stoldo Lorenzi's Neptune (1571)
on its rock (relation 2150390); Forte Belvedere, Buontalenti 1590–91 (way 24879633, wall tops from the DSM) with the
palazzina of the 1560s in the middle (size *inferred* from the LiDAR shell).
"""
import os, sys, math, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from mathutils import Vector
from landmark_detail import *
K.reset()
MAT["stone"] = material("pietra_forte", "pietra_forte", (0.62, 0.5, 0.36), 0.85, 0.32, tint=(3.0, 2.85, 2.55))
MAT["serena"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)
MAT["plaster"] = material("plaster_white", "intonaco", (0.9, 0.87, 0.8), 0.9, 0.4, tint=(1.3, 1.25, 1.1))
MAT["ochre"] = material("plaster_ochre", "intonaco", (0.84, 0.72, 0.5), 0.9, 0.4, tint=(1.2, 0.92, 0.55))
MAT["green"] = material("kaffeehaus_green", None, (0.36, 0.52, 0.42), 0.6)
MAT["copper"] = material("copper_green", None, (0.35, 0.55, 0.48), 0.5, metal=0.3)
MAT["water"] = material("basin_water", None, (0.18, 0.3, 0.32), 0.08)
MAT["lawn"] = material("lawn", None, (0.3, 0.42, 0.2), 0.95)
MAT["gravel"] = material("gravel", "terra", (0.72, 0.66, 0.55), 0.95, 0.3)
MAT["spugne"] = material("grotto_spugne", "pietra_forte", (0.6, 0.55, 0.46), 0.98, 0.9, tint=(2.4, 2.3, 2.1))
NOW = K.NOW
D = json.load(open(os.path.join(ROOT, "blender", "data", "pitti.json"), encoding="utf-8"))
Z = Vector((0, 0, 1))
def V(x, z, h=0.0): return Vector((x, -z, h))
def D3(dx, dz): return Vector((dx, -dz, 0)).normalized()
def outward(P):
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(P, P[1:] + P[:1])); return 1 if area > 0 else -1
def edges(P):
    sg = outward(P)
    for i, ((ax, az), (bx, bz)) in enumerate(zip(P, P[1:] + P[:1])):
        L = math.dist((ax, az), (bx, bz))
        if L < 0.05: continue
        tx, tz = (bx - ax) / L, (bz - az) / L
        yield i, (ax, az), (bx, bz), L, (tx, tz), (tz * sg, -tx * sg)
def ring_open(P): return P[:-1] if P[0] == P[-1] else P

# ------------------------------------------------------------------ amphitheatre
OB = (-315.0, 868.0)                                       # obelisk (OSM node area 160800066), the arena's centre
def amphitheatre():
    P = ring_open(D["anfiteatro"]["pts"]); g = D["anfiteatro"]["ground"]
    floor = min(g) - 0.3
    # direction towards the palace (the open end of the horseshoe), from the obelisk to the middle of the straight side
    mx, mz = (P[0][0] + P[3][0]) / 2, (P[0][1] + P[3][1]) / 2
    ax, az = mx - OB[0], mz - OB[1]; L = math.hypot(ax, az); ax, az = ax / L, az / L
    base = math.atan2(-az, -ax)                                # the curved end, away from the palace
    R0, steps, sw, rise = 30.0, 6, 1.8, 0.55
    # arena (gravel) and the tiers: arcs of 200° round the far end, straight arms 22 m towards the palace
    n = 40
    def tier_pts(r):
        arc = [(OB[0] + r * math.cos(base + a), OB[1] + r * math.sin(base + a)) for a in [math.radians(-100 + 200 * k / n) for k in range(n + 1)]]
        px, pz = -math.sin(base + math.radians(-100)) * 0, 0
        e0, e1 = arc[0], arc[-1]
        return [(e0[0] + ax * 22, e0[1] + az * 22)] + arc + [(e1[0] + ax * 22, e1[1] + az * 22)]
    prof = D["anfiteatro"]["profile"]
    gr = lambda r: min(prof, key=lambda q: abs(q[0] - r))[1]
    floor = max(q[1] for q in prof if q[0] <= R0) + 0.08          # the arena sits on the ground, never under it
    for s in range(steps):
        r0, r1 = R0 + s * sw, R0 + (s + 1) * sw
        h0 = floor if s == 0 else max(floor + s * rise, gr(r0) + 0.35)
        h1 = max(floor + (s + 1) * rise, gr(r1) + 0.35)
        a, b = tier_pts(r0), tier_pts(r1)
        quad_strip(bm_for(f"gradinate@1599-{NOW}", "stone"), [V(x, z, h1) for x, z in a], [V(x, z, h0) for x, z in a])       # riser
        quad_strip(bm_for(f"gradinate@1599-{NOW}", "stone"), [V(x, z, h1) for x, z in b], [V(x, z, h1) for x, z in a])       # tread
        # before the stone seats (1550–1599): a grassy slope
        quad_strip(bm_for(f"anfiteatro_prato@1550-1599", "lawn"), [V(x, z, h1) for x, z in b], [V(x, z, h0) for x, z in a])
    top_r = R0 + steps * sw; top_h = h1
    poly(bm_for(f"anfiteatro_arena@1550-{NOW}", "gravel"), [V(x, z, floor + 0.05) for x, z in tier_pts(R0)])
    # edicules with statues and terracotta urns along the top (Parigi, c. 1630–34)
    arc = tier_pts(top_r + 1.2)
    for k in range(2, len(arc) - 2, 3):
        x, z = arc[k]; cxx, czz = OB[0] - x, OB[1] - z; L = math.hypot(cxx, czz)
        F = Frame(V(x, z) + D3(czz / L, -cxx / L) * -0.9, D3(czz / L, -cxx / L), D3(cxx / L, czz / L))
        box(bm_for(f"edicole@1634-{NOW}", "plaster"), F, 0, 1.8, top_h, top_h + 3.4, -0.6, 0)
        arch_fill(f"edicole@1634-{NOW}", "dark", F, 0.35, 1.45, top_h + 0.6, top_h + 2.2, n=0.03)
        cylinder(f"edicole@1634-{NOW}", "stone", V(x, z) + D3(czz / L, -cxx / L) * 0.0, 0.32, top_h + 3.4, top_h + 4.2, seg=10)
    # the obelisk (1790) and the granite basin in front of it (1840, inferred)
    c = V(*OB)
    box(bm_for(f"obelisco@1790-{NOW}", "stone"), Frame(c + Vector((-1.2, -1.2, 0)), Vector((1, 0, 0)), Vector((0, 1, 0))), 0, 2.4, floor, floor + 1.6, 0, 2.4)
    cone(f"obelisco@1790-{NOW}", "red", c, 0.55, 0.32, floor + 1.6, floor + 6.2, seg=4)
    cone(f"obelisco@1790-{NOW}", "red", c, 0.32, 0.01, floor + 6.2, floor + 6.8, seg=4)
    bx = V(-317.0, 863.0)
    cylinder(f"vasca_granito@1840-{NOW}", "serena", bx, 1.6, floor, floor + 0.5, seg=20)
    cylinder(f"vasca_granito@1840-{NOW}", "serena", bx, 2.4, floor + 0.5, floor + 1.4, seg=24)

# ------------------------------------------------------------------ Grotta del Buontalenti (1583–93)
def grotta():
    part = f"grotta_buontalenti@1583-{NOW}"
    P = ring_open(D["grotta"]["pts"]); g = min(D["grotta"]["ground"]); top = g + 11.5
    pitti = (-393.0, 759.0)
    best = None
    for i, a, b, L, t, n in edges(P):
        poly(bm_for(part, "plaster"), [V(*a, g - 0.5), V(*b, g - 0.5), V(*b, top), V(*a, top)])
        mx, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2; dx, dz = pitti[0] - mx, pitti[1] - mz
        score = (n[0] * dx + n[1] * dz) / math.hypot(dx, dz) * L
        if best is None or score > best[0]: best = (score, a, L, t, n, i)
    poly(bm_for(part, "roof"), [V(x, z, top + 0.2) for x, z in P])
    _, a, L, t, n, i = best; F = Frame(V(*a), D3(*t), D3(*n)); c = L / 2
    gg = D["grotta"]["ground"]; g = max(gg[i], gg[(i + 1) % len(P)]) + 0.05          # the front stands on its own ground
    arch_fill(part, "dark", F, c - 2.4, c + 2.4, g, g + 4.2, n=0.03)                                  # the grotto mouth
    for s in (-1, 1):
        cylinder(part, "stone", F.p(c + s * 3.4, 0, 0.6), 0.45, g, g + 6.0, seg=12)                    # Tuscan columns
        pbox(bm_for(part, "spugne"), F, c + s * 4.4 - 0.9, c + s * 4.4 + 0.9, g + 1.0, g + 5.2, 0, 0.3)   # niches in rock work
    entablature(part, F, c - 4.4, c + 4.4, g + 6.0, mat="stone", h=1.0, proj=0.7)
    for q in range(14):
        rnd = random.Random(q)
        pbox(bm_for(part, "spugne"), F, c - 4.0 + rnd.random() * 7.6, c - 3.4 + rnd.random() * 7.6, g + 7.2 + rnd.random() * 2.4, g + 7.8 + rnd.random() * 2.6, 0, 0.25)
    pbox(bm_for(part, "plaster"), F, c - 2.5, c + 2.5, g + 9.8, top, 0, 0.2)                            # pediment field

# ------------------------------------------------------------------ Kaffeehaus (Zanobi del Rosso, 1776)
def kaffeehaus():
    part = f"kaffeehaus@1776-{NOW}"
    P = ring_open(D["kaffeehaus"]["pts"]); gl = min(D["kaffeehaus"]["ground"]); g = max(D["kaffeehaus"]["ground"]) + 0.05   # floor on the uphill side, plinth down the slope
    cx = sum(p[0] for p in P) / len(P); cz = sum(p[1] for p in P) / len(P); c = V(cx, cz)
    octagon_prism(part, "stone", c, 3.5, gl - 0.5, g)
    octagon_prism(part, "green", c, 3.3, g, g + 4.4)
    octagon_prism(part, "plaster", c, 3.45, g + 4.4, g + 4.9)
    octagon_prism(part, "green", c, 2.8, g + 4.9, g + 7.6)
    for F, L, k in oct_faces(c, 3.3):
        win_round(part, F, L / 2, g + 0.6, g + 3.6, 1.0, frame="plaster", fill="glass")
    dome(part, c, 2.9, g + 7.6, 2.4, ribs=8, mat="copper", rib_mat="plaster")
    cylinder(part, "plaster", c, 0.5, g + 10.0, g + 11.0, seg=8); cone(part, "copper", c, 0.6, 0.05, g + 11.0, g + 11.8, seg=8)
    # the long side wings are not drawn yet (review list)

# ------------------------------------------------------------------ Neptune basin (1777–78), statue 1571
def nettuno():
    N = D["nettuno"]; P = ring_open(N["pts"]); g = max(N["ground"]) + 0.05
    part = f"vasca_nettuno@1777-{NOW}"
    for i, a, b, L, t, n in edges(P):
        F = Frame(V(*a), D3(*t), D3(*n))
        box(bm_for(part, "stone"), F, 0, L, g - 0.6, g + 0.7, -0.7, 0)
    poly(bm_for(part, "water"), [V(x, z, g + 0.35) for x, z in P])
    I = ring_open(N["isle"]); ic = (sum(p[0] for p in I) / len(I), sum(p[1] for p in I) / len(I))
    cone(part, "spugne", V(*ic), 2.4, 0.9, g, g + 3.2, seg=9)
    cylinder(f"nettuno_statua@1778-{NOW}", "bronze", V(*ic), 0.45, g + 3.2, g + 5.6, seg=10)
    cone(f"nettuno_statua@1778-{NOW}", "bronze", V(*ic) + Vector((0.5, 0, 0)), 0.05, 0.05, g + 3.6, g + 7.0, seg=4)

# ------------------------------------------------------------------ Forte Belvedere (1590–91) and its palazzina (1560s)
def forte():
    part = f"forte_belvedere@1590-{NOW}"
    F_ = D["forte"]; P = ring_open(F_["pts"]); g, top, gin, gout = F_["ground"], F_["top"], F_["ground_in"], F_["ground_out"]
    for i, a, b, L, t, n in edges(P):
        j = (i + 1) % len(P)
        ta, tb = max(top[i], g[i], gin[i]) + 1.1, max(top[j], g[j], gin[j]) + 1.1      # parapet above the ground inside
        ba, bb = min(g[i], gout[i]) - 1.5, min(g[j], gout[j]) - 1.5                        # scarp from below the ground outside
        poly(bm_for(part, "stone"), [V(*a, ba), V(*b, bb), V(*b, tb), V(*a, ta)])                        # scarp
        F = Frame(V(*a), D3(*t), D3(*n))
        pbox(bm_for(part, "stone"), F, 0, L, (ta + tb) / 2 - 2.6, (ta + tb) / 2 - 2.2, 0, 0.35)          # cordon
        quad_strip(bm_for(part, "stone"), [V(*a, ta), V(*b, tb)], [V(a[0] - n[0] * 1.2, a[1] - n[1] * 1.2, ta), V(b[0] - n[0] * 1.2, b[1] - n[1] * 1.2, tb)])
    # the palazzina: white, three storeys, windows on the outer axes shrinking upwards (size inferred)
    pz = f"palazzina_belvedere@1565-{NOW}"
    pg = D["palazzina_ground"]; c = V(-89.9, 992.9); w, d, g0, H = 26.0, 20.0, max(pg) + 0.05, 17.0   # floor on its highest ground
    o = c - Vector((w / 2, d / 2, 0))
    for F, L in ((Frame(o, Vector((1, 0, 0)), Vector((0, -1, 0))), w), (Frame(o + Vector((w, 0, 0)), Vector((0, 1, 0)), Vector((1, 0, 0))), d),
                 (Frame(o + Vector((w, d, 0)), Vector((-1, 0, 0)), Vector((0, 1, 0))), w), (Frame(o + Vector((0, d, 0)), Vector((0, -1, 0)), Vector((-1, 0, 0))), d)):
        box(bm_for(pz, "plaster"), F, 0, L, min(pg) - 0.6, g0 + H, -0.6, 0)
        for s in (0.0, L - 1.0): pbox(bm_for(pz, "stone"), F, s, s + 1.0, g0, g0 + H, 0, 0.12)            # quoins
        for fl, (h0, h1) in enumerate(((1.4, 3.8), (6.6, 8.6), (11.8, 13.2))):
            for u in (2.6, L - 2.6): win_rect(pz, F, u, g0 + h0, g0 + h1, 1.3 - fl * 0.2, frame="stone")
        entablature(pz, F, -0.1, L + 0.1, g0 + H - 0.8, mat="stone", h=0.8, proj=0.6)
    top_ = g0 + H; e = 0.8; q = [o - Vector((e, e, 0)), o + Vector((w + e, -e, 0)), o + Vector((w + e, d + e, 0)), o + Vector((-e, d + e, 0))]
    ridge = [c + Vector((-w / 2 + d / 2, 0, 0)), c + Vector((w / 2 - d / 2, 0, 0))]
    poly(bm_for(pz, "roof"), [q[0] + Z * top_, q[1] + Z * top_, ridge[1] + Z * (top_ + 3.0), ridge[0] + Z * (top_ + 3.0)])
    poly(bm_for(pz, "roof"), [q[2] + Z * top_, q[3] + Z * top_, ridge[0] + Z * (top_ + 3.0), ridge[1] + Z * (top_ + 3.0)])
    poly(bm_for(pz, "roof"), [q[1] + Z * top_, q[2] + Z * top_, ridge[1] + Z * (top_ + 3.0)])
    poly(bm_for(pz, "roof"), [q[3] + Z * top_, q[0] + Z * top_, ridge[0] + Z * (top_ + 3.0)])

amphitheatre()
grotta()
kaffeehaus()
nettuno()
forte()
K.export("boboli")
