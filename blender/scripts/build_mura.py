"""Le mura – the sixth circle of walls (1284–1333) with its gates and towers, over the eras up to today (v1).

Run:  python pipeline/40_walls.py   (once: geometry from OSM / OHM / LiDAR → blender/data/walls.json)
      blender -b --python blender/scripts/build_mura.py  →  web/public/models/landmarks/mura.glb
Frame: absolute scene coordinates (the app places it at 0/0 with ground 0): Blender X = scene x (east),
Blender Y = −scene z (north), Z = elevation − 40 m. Every part is dated; node names start with the member key
("g_romana_…", "wall_…") so a click on a gate opens that gate's card.
Dates and sources: docs/landmarks/MURA.md. In short: walls 1284–1333 (Oltrarno stretches from c. 1320), towers every
≈115 m, 40 braccia ≈ 23 m; gates and towers lowered in the siege of 1529–30 (San Niccolò excepted); bastions
1529–54; Fortezza da Basso 1534–37; north-bank walls pulled down by Poggi 1865–70, gates left standing in their squares.
Heights before 1529 are conjectural; today's heights are measured (LiDAR 2023 DSM).
"""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
K.reset()
MAT["stone"] = material("pietra_forte", "pietra_forte", (0.62, 0.5, 0.36), 0.85, 0.32, tint=(3.0, 2.85, 2.55))
MAT["rubble"] = material("wall_rubble", "pietra_forte", (0.52, 0.5, 0.45), 0.92, 0.3, tint=(1.85, 1.9, 1.95))
MAT["shade"] = material("tower_inside", "pietra_forte", (0.3, 0.28, 0.25), 0.95, 0.3, tint=(0.9, 0.9, 0.92))
MAT["serena"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)
MAT["fresco"] = material("gate_fresco", None, (0.55, 0.42, 0.3), 0.8)
MAT["earth"] = material("bastion_earth", "terra", (0.42, 0.38, 0.28), 0.95, 0.15)
MAT["plaster"] = material("arch_plaster", "intonaco", (0.86, 0.82, 0.74), 0.8, 0.4)

D = json.load(open(os.path.join(ROOT, "blender", "data", "walls.json"), encoding="utf-8"))
CITY = (0.0, 300.0)                       # scene x/z inside the circle: walls and towers face away from it
SIEGE = 1529                              # towers and gates cut down in the siege of 1529–30
V = lambda x, z, y: Vector((x, -z, y))    # scene → Blender

def out_normal(ax, az, bx, bz):
    tx, tz = bx - ax, bz - az; l = math.hypot(tx, tz) or 1; tx, tz = tx / l, tz / l
    nx, nz = -tz, tx
    if nx * ((ax + bx) / 2 - CITY[0]) + nz * ((az + bz) / 2 - CITY[1]) < 0: nx, nz = -nx, -nz
    return (tx, tz), (nx, nz), l

def prism(bm, a, b, n, t0, t1, ga, gb, h0a, h1a, h0b, h1b):
    """Slab between wall samples a→b (scene x/z), from offset t0 to t1 along the outward normal n, bottoms/tops above
    each end's ground."""
    c = []
    for t in (t0, t1):
        for (p, gr, lo, hi) in ((a, ga, h0a, h1a), (b, gb, h0b, h1b)):
            c += [V(p[0] + n[0] * t, p[1] + n[1] * t, gr + lo), V(p[0] + n[0] * t, p[1] + n[1] * t, gr + hi)]
    # c: t0: a_lo a_hi b_lo b_hi | t1: a_lo a_hi b_lo b_hi
    vs = [bm.verts.new(x) for x in c]
    for f in ((0, 2, 3, 1), (4, 5, 7, 6), (1, 3, 7, 5), (0, 4, 6, 2), (0, 1, 5, 4), (2, 6, 7, 3)):
        bm.faces.new([vs[i] for i in f])

def smooth(v, k=4):
    return [sorted(v[max(0, i - k):i + k + 1])[len(v[max(0, i - k):i + k + 1]) // 2] for i in range(len(v))]

# ------------------------------------------------------------------ walls with their wall-walk merlons and towers
THICK, NORTH_H = 2.2, 11.6                # 20 braccia (Villani); thickness ≈ 2 m at the top
gates_at = [(g["c"][0], g["c"][1]) for g in D["gates"]]
tower_count = 0
for w in D["walls"]:
    P = w["pts"]; fr, to = w["from"], w["to"]
    if len(P[0]) > 3: H = [min(13.0, max(5.5, h)) for h in smooth([p[3] for p in P])]
    else: H = [w.get("h") or (NORTH_H if w["id"].startswith("north") else 10.0)] * len(P)
    part = f"wall_{w['id']}@{fr}-{to}"; bm, mb = bm_for(part, "rubble"), bm_for(part, "stone")
    run = 0.0; next_tower = 57.0
    for i in range(len(P) - 1):
        a, b = P[i], P[i + 1]; (tx, tz), n, l = out_normal(a[0], a[1], b[0], b[1])
        prism(bm, a, b, n, -THICK / 2, THICK / 2, a[2], b[2], -2.5, H[i], -2.5, H[i + 1])
        # merlons (Guelph, square) on the outer edge of the wall-walk
        k = int(l // 2.4)
        for j in range(k):
            s0, s1 = (j * 2.4 + 0.5) / l, (j * 2.4 + 1.9) / l
            pa = (a[0] + (b[0] - a[0]) * s0, a[1] + (b[1] - a[1]) * s0); pb = (a[0] + (b[0] - a[0]) * s1, a[1] + (b[1] - a[1]) * s1)
            ga, gb = a[2] + (b[2] - a[2]) * s0, a[2] + (b[2] - a[2]) * s1; hh = H[i] + (H[i + 1] - H[i]) * (s0 + s1) / 2
            prism(mb if j % 7 == 0 else bm, pa, pb, n, THICK / 2 - 0.55, THICK / 2, ga, gb, hh - 0.1, hh + 1.7, hh - 0.1, hh + 1.7)
        # towers: every ≈115 m (200 braccia), not where a gate stands
        while run + l > next_tower:
            s = (next_tower - run) / l; x, z = a[0] + (b[0] - a[0]) * s, a[1] + (b[1] - a[1]) * s; gr = a[2] + (b[2] - a[2]) * s
            next_tower += 115.0
            if min(math.dist((x, z), q) for q in gates_at) < 40 or w["kind"] != "wall": continue
            hw = H[i]; tower_count += 1
            phases = [(f"tw{tower_count}_hi@{fr}-{min(to, SIEGE)}", hw + 11.5, True)] if fr < SIEGE else []
            if to > SIEGE: phases.append((f"tw{tower_count}_lo@{max(fr, SIEGE)}-{to}", hw + 1.2, False))
            for pn, top, crenel in phases:
                tb = bm_for(pn, "rubble"); p0, p1 = (x - tx * 4, z - tz * 4), (x + tx * 4, z + tz * 4)
                prism(tb, p0, p1, n, -THICK / 2, THICK / 2 + 6.0, gr, gr, -2.5, top, -2.5, top)
                F = Frame(V(x + n[0] * (THICK / 2 + 6.0), z + n[1] * (THICK / 2 + 6.0), gr), V(tx, tz, 0), V(n[0], n[1], 0))
                for v in ([4.5, 10.0, 15.5] if crenel else [4.5]):
                    if v < top - 2: pbox(bm_for(pn, "dark"), F, -0.15, 0.15, v, v + 1.6, 0, 0.05)      # arrow slits
                if crenel:                                                                          # merlons round the top
                    for u in (-3.6, -1.2, 1.2, 3.6): box(bm_for(pn, "rubble"), F, u - 0.65, u + 0.65, top, top + 1.7, -0.6, 0)
                    for side in (-1, 1):
                        Fs = Frame(V(x + tx * 4 * side, z + tz * 4 * side, gr), V(-n[0] * side, -n[1] * side, 0), V(tx * side, tz * side, 0))
                        for u in (-5.0, -2.5): box(bm_for(pn, "rubble"), Fs, u - 0.6, u + 0.6, top, top + 1.7, -0.6, 0)
                else:                                                                               # cut down: stone coping
                    prism(bm_for(pn, "stone"), p0, p1, n, -THICK / 2, THICK / 2 + 6.2, gr, gr, top - 0.1, top + 0.45, top - 0.1, top + 0.45)
        run += l

# ------------------------------------------------------------------ gates
def wall_dir(x, z):
    best = None
    for w in D["walls"]:
        P = w["pts"]
        for a, b in zip(P, P[1:]):
            d = math.dist((x, z), ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2))
            if best is None or d < best[0]: best = (d, a, b)
    _, a, b = best; return out_normal(a[0], a[1], b[0], b[1])[:2]

def frames(g, L, Dp, along_footprint=False):
    (tx, tz), (nx, nz) = wall_dir(*g["c"]); x, z = g["c"]; gr = g["ground"]
    if along_footprint:          # the wall runs along the footprint's long axis (San Niccolò: down to the river)
        tx, tz = math.cos(g["ang"]), -math.sin(g["ang"]); nx, nz = -tz, tx
        if nx * (x - CITY[0]) + nz * (z - CITY[1]) < 0: nx, nz = -nx, -nz
    Fo = Frame(V(x + nx * Dp / 2, z + nz * Dp / 2, gr), V(tx, tz, 0), V(nx, nz, 0))
    Fi = Frame(V(x - nx * Dp / 2, z - nz * Dp / 2, gr), V(-tx, -tz, 0), V(-nx, -nz, 0))
    Fc = Frame(V(x, z, gr), V(tx, tz, 0), V(nx, nz, 0))
    return Fo, Fi, Fc

def tower_body(part, Fc, L, Dp, H, open_inside, arch_w=0.0, arch_h=0.0, mat="rubble"):
    """Gate tower: outer and side walls full height; open towards the city (wooden floors seen through), passage arch."""
    t = 1.9; bm = bm_for(part, mat)
    box(bm, Fc, -L / 2, L / 2, -3, H, Dp / 2 - t, Dp / 2)                                  # outer wall
    for s in (-1, 1): box(bm, Fc, s * L / 2 - (t if s > 0 else 0), s * L / 2 + (0 if s > 0 else t), -3, H, -Dp / 2, Dp / 2)
    if open_inside:
        low = arch_h + 2.5
        box(bm, Fc, -L / 2, L / 2, -3, low, -Dp / 2, -Dp / 2 + t)                          # inner wall up to above the arch
        # the shell seen from the city: inside of the outer wall in shadow, floors on beams at every storey
        box(bm_for(part, "shade"), Fc, -L / 2 + t, L / 2 - t, low, H - 0.6, Dp / 2 - t - 0.1, Dp / 2 - t)
        for s_ in (-1, 1): box(bm_for(part, "shade"), Fc, s_ * (L / 2 - t) - (0.1 if s_ > 0 else 0), s_ * (L / 2 - t) + (0 if s_ > 0 else 0.1), low, H - 0.6, -Dp / 2, Dp / 2 - t)
        for v in range(int(low) + 5, int(H) - 1, 5):
            box(bm_for(part, "wood"), Fc, -L / 2 + t, L / 2 - t, v, v + 0.35, -Dp / 2 + t, Dp / 2 - t)            # floor
            for u in range(int(-L / 2 + t) + 1, int(L / 2 - t), 2):
                box(bm_for(part, "wood"), Fc, u, u + 0.35, v - 0.4, v, -Dp / 2 + t, Dp / 2 - t)                  # joists
    else:
        box(bm, Fc, -L / 2, L / 2, -3, H, -Dp / 2, -Dp / 2 + t)
    box(bm_for(part, "dark"), Fc, -L / 2 + t, L / 2 - t, H - 0.7, H - 0.6, -Dp / 2 + t, Dp / 2 - t)   # floor of the top
    if arch_w:
        box(bm_for(part, "dark"), Fc, -arch_w / 2, arch_w / 2, 0, arch_h - arch_w / 2, -Dp / 2 - 0.02, Dp / 2 + 0.02)  # passage

def crenels(part, Fc, L, Dp, H, corbels=False):
    """Merlons round the top; with corbels (beccatelli) the parapet stands out on brackets."""
    pr = 0.8 if corbels else 0.0
    for (u0, u1, n0, n1) in ((-L / 2 - pr, L / 2 + pr, Dp / 2 - 0.6 + pr, Dp / 2 + pr), (-L / 2 - pr, L / 2 + pr, -Dp / 2 - pr, -Dp / 2 + 0.6 - pr),
                             (-L / 2 - pr, -L / 2 + 0.6 - pr, -Dp / 2 - pr, Dp / 2 + pr), (L / 2 - 0.6 + pr, L / 2 + pr, -Dp / 2 - pr, Dp / 2 + pr)):
        if corbels: box(bm_for(part, "stone"), Fc, u0, u1, H - 1.4, H, n0, n1)
        along_u = (u1 - u0) > (n1 - n0); span = (u1 - u0) if along_u else (n1 - n0); k = max(2, int(span / 2.2))
        for j in range(k):
            s0, s1 = j / k + 0.18 / k * 2, (j + 1) / k - 0.18 / k * 2
            if along_u: box(bm_for(part, "rubble"), Fc, u0 + span * s0, u0 + span * s1, H, H + 1.8, n0, n1)
            else: box(bm_for(part, "rubble"), Fc, u0, u1, H, H + 1.8, n0 + span * s0, n0 + span * s1)

def hip_roof(part, Fc, L, Dp, z0, rise):
    bm = bm_for(part, "roof"); e = 0.6
    a, b, c, d = Fc.p(-L / 2 - e, z0, -Dp / 2 - e), Fc.p(L / 2 + e, z0, -Dp / 2 - e), Fc.p(L / 2 + e, z0, Dp / 2 + e), Fc.p(-L / 2 - e, z0, Dp / 2 + e)
    r0, r1 = Fc.p(-L / 2 + Dp / 2, z0 + rise, 0), Fc.p(L / 2 - Dp / 2, z0 + rise, 0)
    for f in ((a, b, r1, r0), (c, d, r0, r1), (b, c, r1), (d, a, r0)): poly(bm, f)

def lean_roof(part, Fc, L, Dp, z_out, z_in):
    """Roof of a cut-down gate: one slope from the outer wall down towards the city."""
    poly(bm_for(part, "roof"), [Fc.p(L / 2 + 0.5, z_out, Dp / 2 + 0.4), Fc.p(-L / 2 - 0.5, z_out, Dp / 2 + 0.4),
                                Fc.p(-L / 2 - 0.5, z_in, -Dp / 2 - 0.6), Fc.p(L / 2 + 0.5, z_in, -Dp / 2 - 0.6)])

def faces(part, Fo, Fi, aw, ah, arms=True, lunette=True, round_arch=False):
    opening(part, Fo, -aw / 2, aw / 2, 0, ah, depth=0.3, frame=0.7, pointed=not round_arch, fill="dark", frame_mat="stone")
    opening(part, Fi, -aw / 2, aw / 2, 0, ah, depth=0.3, frame=0.6, pointed=not round_arch, fill="dark", frame_mat="stone")
    if arms:     # the lily of Florence carved in stone above the arch (outer face)
        pbox(bm_for(part, "stone"), Fo, -1.0, 1.0, ah + 1.6, ah + 4.0, 0, 0.35)
        pbox(bm_for(part, "stone"), Fo, -1.3, 1.3, ah + 4.0, ah + 4.4, 0, 0.5)
    if lunette:  # frescoed lunette over the inner arch (Madonna and saints, 14th–16th c.)
        poly(bm_for(part, "fresco"), [Fi.p(aw * 0.42 * math.cos(a), ah - aw * 0.42 + aw * 0.5 * math.sin(a) + 0.4, 0.12)
                                      for a in [math.pi * k / 12 for k in range(13)]])

GD = {g["key"]: g for g in D["gates"]}
# key: (from, hi before the siege (None: never lowered), until, size override (L, D), arch (w, apex), roof)
SPEC = {
    "romana":   (1326, 33.0, NOW, None, (6.2, 13.0), "lean"),
    "frediano": (1332, None, NOW, (20.0, 14.5), (6.5, 14.0), "lean"),
    "croce":    (1284, 32.0, NOW, None, (5.0, 11.0), "lean"),
    "prato":    (1284, 32.0, NOW, (18.0, 13.0), (5.2, 11.5), "lean"),
    "gallo":    (1285, 33.0, NOW, None, (5.4, 12.0), "lean"),
    "niccolo":  (1324, None, NOW, None, (5.5, 11.0), "hip"),
    "giorgio":  (1324, None, NOW, None, (3.6, 6.5), "hip"),
    "zecca":    (1320, 31.0, NOW, None, (0, 0), "hip"),
    "serpe":    (1320, 23.0, NOW, None, (0, 0), "hip"),
    "rosa":     (1324, None, NOW, None, (0, 0), "hip"),
    "verzaia":  (1320, None, NOW, None, (0, 0), "flat"),
    "faenza":   (1284, 32.0, NOW, None, (5.0, 11.0), "lean"),
    "pinti":    (1284, 32.0, 1866, None, (5.0, 11.0), "lean"),
    "giustizia":(1284, 30.0, 1530, None, (5.0, 11.0), "lean"),
}
for key, (fr, hi, to, size, (aw, ah), roof) in SPEC.items():
    g = GD[key]
    L, Dp = size or ((g["L"], g["W"]) if g["ang"] is None else (g["L"], g["W"]))
    if g["ang"] is not None:      # the footprint's long axis may lie across the wall
        (tx, tz), _ = wall_dir(*g["c"]); ax = (math.cos(g["ang"]), -math.sin(g["ang"]))   # UTM angle → scene x/z
        if size is None and abs(ax[0] * tx + ax[1] * tz) < 0.7: L, Dp = g["W"], g["L"]
    if key == "niccolo": L, Dp = g["L"], g["W"]
    Fo, Fi, Fc = frames(g, L, Dp, along_footprint=key == "niccolo")
    now = g["h_now"] or 20.0
    roof_h = {"lean": 2.0, "hip": 3.5, "flat": 0.0}[roof]
    H_lo = max(8.0, now - roof_h)
    is_gate = aw > 0; open_in = is_gate and key not in ("giorgio",)
    phases = []
    if hi and fr < SIEGE: phases.append((f"g_{key}_hi@{fr}-{min(SIEGE, to)}", hi, True))
    if to > SIEGE or not hi: phases.append((f"g_{key}@{SIEGE if hi else fr}-{to}", H_lo, False))
    for pn, H, tall in phases:
        if key == "niccolo": H = now - 6.0
        tower_body(pn, Fc, L, Dp, H, open_in, aw, ah)
        if is_gate: faces(pn, Fo, Fi, aw, ah, arms=key not in ("giorgio",), lunette=key in ("romana", "croce", "gallo", "prato", "giorgio", "pinti", "frediano"),
                          round_arch=key in ("frediano",))
        if tall: crenels(pn, Fc, L, Dp, H)
        elif key == "niccolo": crenels(pn, Fc, L, Dp, H, corbels=True); hip_roof(pn, Fc, L - 2, Dp - 2, H + 0.3, 4.5)
        elif roof == "lean": lean_roof(pn, Fc, L, Dp, H + roof_h, H)
        elif roof == "hip": hip_roof(pn, Fc, L, Dp, H, roof_h)
        else: crenels(pn, Fc, L, Dp, H)
        if key == "giorgio":   # St George and the dragon, relief on the outer face (copy; original in Palazzo Vecchio)
            pbox(bm_for(pn, "stone"), Fo, -1.2, 1.2, ah + 1.2, ah + 3.0, 0, 0.3)

# Porta San Miniato: an arch through the wall, no tower (1320)
g = GD["miniato"]; Fo, Fi, Fc = frames(g, 8.0, 3.4)
pn = f"g_miniato@1320-{NOW}"; box(bm_for(pn, "rubble"), Fc, -4.5, 4.5, -3, 9.5, -1.7, 1.7)
opening(pn, Fo, -1.8, 1.8, 0, 6.2, frame=0.5, pointed=False, fill="dark", frame_mat="stone")
opening(pn, Fi, -1.8, 1.8, 0, 6.2, frame=0.5, pointed=False, fill="dark", frame_mat="stone")
box(bm_for(pn, "dark"), Fc, -1.8, 1.8, 0, 4.4, -1.75, 1.75)
box(bm_for(pn, "rubble"), Fc, -4.6, 4.6, 9.5, 10.3, -1.8, 1.8)

# Arco di Trionfo dei Lorena, Jean-Nicolas Jadot 1739–45: one great arch, coupled columns, attic with the statues
g = GD["arco"]; (tx, tz), (nx, nz) = wall_dir(*g["c"])
ax = (math.cos(g["ang"]), -math.sin(g["ang"]))
Fc = Frame(V(g["c"][0], g["c"][1], g["ground"]), V(ax[0], ax[1], 0), V(-ax[1], ax[0], 0))
pn = f"g_arco@1739-{NOW}"; L, Dp = g["L"], g["W"]; aw, ah = 7.6, 15.0
for s in (-1, 1):
    box(bm_for(pn, "serena"), Fc, s * aw / 2 if s > 0 else -L / 2, L / 2 if s > 0 else -aw / 2, 0, 18.5, -Dp / 2, Dp / 2)
    for u in (aw / 2 + 1.1, L / 2 - 1.1):      # coupled columns on both faces
        for side in (-1, 1): box(bm_for(pn, "stone"), Fc, s * u - 0.55, s * u + 0.55, 0.8, 16.8, side * Dp / 2, side * (Dp / 2 + 0.6))
box(bm_for(pn, "serena"), Fc, -aw / 2, aw / 2, ah, 18.5, -Dp / 2, Dp / 2)
for f in (1, -1):
    F = Frame(Fc.p(0, 0, f * Dp / 2), Fc.u * f, Fc.n * f)
    opening(pn, F, -aw / 2, aw / 2, 0, ah, frame=0.7, pointed=False, fill="dark", frame_mat="stone")
box(bm_for(pn, "stone"), Fc, -L / 2 - 0.4, L / 2 + 0.4, 18.5, 19.6, -Dp / 2 - 0.4, Dp / 2 + 0.4)            # cornice
box(bm_for(pn, "serena"), Fc, -L / 2 + 0.8, L / 2 - 0.8, 19.6, 22.6, -Dp / 2 + 0.3, Dp / 2 - 0.3)          # attic
box(bm_for(pn, "plaster"), Fc, -4.5, 4.5, 20.0, 22.2, -Dp / 2 + 0.25, Dp / 2 - 0.25)                      # inscription tablet
for u, h in ((0, 4.2), (-7.0, 3.0), (7.0, 3.0)):                                                         # statue groups
    box(bm_for(pn, "white"), Fc, u - 1.4, u + 1.4, 22.6, 22.6 + h, -1.2, 1.2)
box(bm_for(pn, "dark"), Fc, -aw / 2, aw / 2, 0, ah - aw / 2, -Dp / 2 - 0.02, Dp / 2 + 0.02)

# ------------------------------------------------------------------ bastions (1529–54) and the Fortezza da Basso (1534)
def signed_area(P): return sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(P, P[1:] + P[:1])) / 2
for p in D["polys"]:
    P = [q for q in p["pts"]]; P = P[:-1] if P[0][:2] == P[-1][:2] else P
    pn = f"{'fortezza' if p['id'] == 'fortezza' else 'bastion_' + p['id']}@{p['from']}-{p['to']}"
    if p["id"] == "fortezza":
        # curtain walls and bastions faced in brick on a stone plinth, ≈12 m, scarped; terreplein inside
        ccw = signed_area([q[:2] for q in P]) > 0
        for a, b in zip(P, P[1:] + P[:1]):
            tx, tz = b[0] - a[0], b[1] - a[1]; l = math.hypot(tx, tz) or 1; nx, nz = -tz / l, tx / l
            inn = (nx, nz) if ccw else (-nx, -nz)          # in scene x/z (z south) the inward side flips with the winding
            out = (-inn[0], -inn[1])
            prism(bm_for(pn, "brick"), a, b, out, -9.0, 0.0, a[2], b[2], -3, 12.0, -3, 12.0)
            prism(bm_for(pn, "stone"), a, b, out, -0.1, 0.35, a[2], b[2], -3, 2.2, -3, 2.2)          # plinth
            prism(bm_for(pn, "stone"), a, b, out, -0.1, 0.45, a[2], b[2], 7.0, 7.6, 7.0, 7.6)        # torus cordon
            prism(bm_for(pn, "earth"), a, b, out, -16.0, -9.0, a[2], b[2], -3, 10.5, -3, 10.5)      # terreplein
        continue
    g0 = min(q[2] for q in P); top = g0 + 10.0
    cx = sum(q[0] for q in P) / len(P); cz = sum(q[1] for q in P) / len(P)
    bm = bm_for(pn, "earth")
    base = [V(q[0], q[1], q[2] - 2.5) for q in P]
    topp = [V(cx + (q[0] - cx) * 0.93, cz + (q[1] - cz) * 0.93, top) for q in P]
    poly(bm, topp)
    sb = bm_for(pn, "rubble")
    for i in range(len(P)):
        j = (i + 1) % len(P); poly(sb, [base[i], base[j], topp[j], topp[i]])

export("mura")
print("towers", tower_count)
# record clearing: city records whose LiDAR shell is the gate (footprint + 3 m) — read by the app as mura_clear.json
clear = []
for g in D["gates"]:
    if g["foot"]:
        cx = sum(p[0] for p in g["foot"]) / len(g["foot"]); cz = sum(p[1] for p in g["foot"]) / len(g["foot"])
        clear.append([[round(cx + (p[0] - cx) * 1.25, 1), round(cz + (p[1] - cz) * 1.25, 1)] for p in g["foot"]])
json.dump(clear, open(os.path.join(OUT, "mura_clear.json"), "w", newline="\n"))
