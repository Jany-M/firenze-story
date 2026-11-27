"""Tempio Maggiore Israelitico – the Synagogue of Florence (v1, detailed).

Run:  python pipeline/47_moderni.py   (once: outlines, ground, DSM raster → blender/data/moderni.json)
      blender -b --python blender/scripts/build_sinagoga.py  →  web/public/models/landmarks/sinagoga.glb
Frame: a along the west front (towards Via Farini) from the north corner of OSM way 102979678 (a grows southwards),
o inwards (east). Ground 9.5 m (scene).
Measured (LiDAR 2023 DSM, height above the ground, read in this frame – _dev/tmp/asc_sin.txt): the building spans
a -5.5..22.5 (28 m) and o -1..48; the towers on the front at a ≈ -2.5 and 19.5 reach 26–28 m (DSM, on their domes'
flanks); the front's middle 22–26 m; the side parts of the arms 14–18 m; the arms' vaults 24–26 m along the middle,
falling to 20–22 m at their sides (round vaults); the cross arms o 19..36 25–28 m over the whole width; the drum and
dome centred at a 8.5, o 27.5, ≈ 17 m across, top 48–50 m; the apse o 41..48 20–24 m; low annexes 6–8 m behind.
From photographs (Commons: Txllxt TxllxT 2010, Yair Haklai 2008 and 2019, Rufus46 2014, Zairon 2023, Luca Aless 2014;
credited on the library page): bands of white travertine and pink stone over every wall; the front between two towers
under a great round arch with a broad archivolt; a portico of three horseshoe arches on columns; paired horseshoe
windows above it, a three-light window and a small rose in the arch; the towers square and banded to the main cornice,
then an open belfry stage and a small ribbed copper dome with a finial; Moorish cresting along the cornices; each arm of
the cross ends in the same great round arch; the drum ringed with arched windows under the green ribbed copper dome;
the front garden behind a cast-iron railing with a gate between lamp pillars, palms by the front.
History: 1874–1882 by Marco Treves, Mariano Falcini and Vincenzo Micheli, inaugurated 24 October 1882; travertine and
pink stone of Assisi, the domes copper (meer.com); dome restored 2003–05 (WMF). Shown from 1882.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from landmark_detail import *
from landmark_church import Site, extra_materials
from landmark_volume import Vol, punched
from mathutils import Vector
K.reset()
MAT["trav"] = material("travertine", None, (0.95, 0.88, 0.75), 0.8)
MAT["pink"] = material("pink_stone_assisi", None, (0.93, 0.6, 0.48), 0.8)
MAT["copper"] = material("copper_verdigris", None, (0.33, 0.62, 0.53), 0.5, metal=0.3)
MAT["copper_rib"] = material("copper_ribs", None, (0.27, 0.52, 0.45), 0.5, metal=0.3)
MAT["lead"] = material("vault_roof", None, (0.47, 0.47, 0.45), 0.75, metal=0.2)
MAT["gold"] = material("gilt", None, (0.85, 0.68, 0.3), 0.35, metal=0.8)
MAT["glass"] = material("window_glass", None, (0.08, 0.09, 0.11), 0.15)
MAT["wood"] = material("door_walnut", "wood", (0.3, 0.2, 0.13), 0.8, 0.8)
MAT["palm"] = material("palm_leaves", None, (0.22, 0.34, 0.16), 0.9)
MAT["trunk"] = material("palm_trunk", None, (0.4, 0.33, 0.25), 0.95)
extra_materials()
NOW = K.NOW
S = Site("sinagoga", "moderni"); G = S.G; V = Vol(S)
P = f"tempio@1882-{NOW}"; GD = f"giardino@1882-{NOW}"
A0, A1 = -5.5, 22.5; AC = (A0 + A1) / 2                          # 28 m wide, centred on a 8.5
T_IN = 0.5                                                        # the towers: a -5.5..0.5 and 16.5..22.5, o -1..5
SIDE, MID_R, CROSS = G + 16.0, 8.0, (19.0, 36.0)
def H(z): return G + z

def banded(part, F, u0, u1, v0, v1, n=0.025, step=1.1):
    """Bands of pink stone over the travertine wall face: half of every 1.1 m course."""
    v = v0 + step / 2
    while v < v1 - 0.05:
        pbox(bm_for(part, "pink"), F, u0, u1, v, min(v1, v + step / 2), 0, n); v += step
def horseshoe(part, F, u, v0, w, spring, fill="glass", frame="trav", fw=0.22, n=0.05, extra=0.38):
    """A horseshoe-arched opening: jambs to the springing, then an arc wider than a half circle."""
    r = w / 2; seg = 16; a0, a1 = -extra, math.pi + extra
    pts = [F.p(u - r * math.cos(extra), v0, n), F.p(u + r * math.cos(extra), v0, n)]
    pts += [F.p(u + r * math.cos(t), spring + r * math.sin(t), n) for t in [a0 + (a1 - a0) * k / seg for k in range(seg + 1)]]
    poly(bm_for(part, fill), pts)
    if frame:
        ring(part, frame, F, u, spring, r, r + fw, 0, n + 0.1, a0=a0, a1=a1, seg=seg)
        for s_ in (-1, 1):
            x = u + s_ * r * math.cos(extra)
            pbox(bm_for(part, frame), F, x - fw / 2, x + fw / 2, v0, spring - r * math.sin(extra), 0, n + 0.08)
def cresting(part, F, u0, u1, v, step=0.9, h=0.7):
    """Moorish cresting: stepped merlons along a cornice."""
    k = int((u1 - u0) / step)
    for i in range(k):
        u = u0 + (i + 0.5) * (u1 - u0) / k
        pbox(bm_for(part, "trav"), F, u - 0.3, u + 0.3, v, v + h * 0.55, -0.15, 0.15)
        pbox(bm_for(part, "trav"), F, u - 0.15, u + 0.15, v + h * 0.55, v + h, -0.1, 0.1)
def arch_gable(part, F, u0, u1, spring, band=0.9):
    """The great round arch closing an arm: the wall's top follows a half circle; a broad archivolt with a pink fillet."""
    r = (u1 - u0) / 2; c = u0 + r; seg = 20
    pts = [F.p(u0, spring, 0), F.p(u1, spring, 0)] + [F.p(c + r * math.cos(math.pi * k / seg), spring + r * math.sin(math.pi * k / seg), 0) for k in range(seg + 1)]
    poly(bm_for(part, "trav"), pts)
    ring(part, "trav", F, c, spring, r - band, r + 0.15, 0, 0.35, seg=seg)
    ring(part, "pink", F, c, spring, r - band - 0.3, r - band, 0, 0.2, seg=seg, soffit=False)
    pbox(bm_for(part, "trav"), F, u0 - 0.4, u0 + 0.6, spring - 1.0, spring + 0.4, 0, 0.45)
    pbox(bm_for(part, "trav"), F, u1 - 0.6, u1 + 0.4, spring - 1.0, spring + 0.4, 0, 0.45)
def vault(part, a0, a1, o0, o1, base, r, along="o", seg=12):
    """A round vault roof (half cylinder) over the rectangle, axis along o or a."""
    bm = bm_for(part, "lead")
    for k in range(seg):
        t0, t1 = math.pi * k / seg, math.pi * (k + 1) / seg
        if along == "o":
            c = (a0 + a1) / 2; x0, x1 = c + r * math.cos(t0), c + r * math.cos(t1); h0, h1 = base + r * math.sin(t0), base + r * math.sin(t1)
            poly(bm, [V.W(x0, o0, h0), V.W(x1, o0, h1), V.W(x1, o1, h1), V.W(x0, o1, h0)])
        else:
            c = (o0 + o1) / 2; y0, y1 = c + r * math.cos(t0), c + r * math.cos(t1); h0, h1 = base + r * math.sin(t0), base + r * math.sin(t1)
            poly(bm, [V.W(a0, y0, h0), V.W(a0, y1, h1), V.W(a1, y1, h1), V.W(a1, y0, h0)])

# ------------------------------------------------------------------ the masses: a Greek cross with towers on the front
# side parts of the front and rear arms (between the towers and the cross arm, and behind it)
for (o0, o1) in ((5.0, CROSS[0]), (CROSS[1], 41.0)):
    for (a0, a1) in ((A0, T_IN), (16.5, A1)):
        V.prism(P, "trav", V.rect(a0, a1, o0, o1), G - 0.3, SIDE, top_mat="lead")
# the middle of the front and rear arms: walls to the springing of the vault, the vault
V.prism(P, "trav", V.rect(T_IN, 16.5, -1.0, 41.0), G - 0.3, H(16.5), top=False)
vault(P, T_IN, 16.5, -1.0, 41.0, H(16.5), MID_R, along="o")
# the cross arm over the whole width (o 19..36), its vault across
V.prism(P, "trav", V.rect(A0, A1, CROSS[0], CROSS[1]), G - 0.3, H(18.0), top=False)
vault(P, A0, A1, CROSS[0], CROSS[1], H(18.0), (CROSS[1] - CROSS[0]) / 2, along="a")
# the apse behind (o 41..48) and the low annexes beside it
ac = V.W(AC, 41.0)
for k in range(12):
    t0, t1 = math.pi * k / 12, math.pi * (k + 1) / 12
    d0 = S.TA * math.cos(t0) + S.NO * math.sin(t0); d1 = S.TA * math.cos(t1) + S.NO * math.sin(t1)
    poly(bm_for(P, "trav"), [ac + d0 * 7 + Vector((0, 0, G - 0.3)), ac + d1 * 7 + Vector((0, 0, G - 0.3)), ac + d1 * 7 + Vector((0, 0, H(17))), ac + d0 * 7 + Vector((0, 0, H(17)))])
    for j in range(6):                                            # its half dome
        p0, p1 = math.pi / 2 * j / 6, math.pi / 2 * (j + 1) / 6
        q = lambda d, p: ac + d * 7 * math.cos(p) + Vector((0, 0, H(17) + 6 * math.sin(p)))
        poly(bm_for(P, "lead"), [q(d0, p0), q(d1, p0), q(d1, p1), q(d0, p1)])
    pm = (t0 + t1) / 2; dm = S.TA * math.cos(pm) + S.NO * math.sin(pm)
    if 2 <= k <= 9 and k % 2 == 0:
        Fa = Frame(ac + dm * 7.02, (d1 - d0).normalized(), dm)
        horseshoe(P, Fa, 0, H(7.0), 1.3, H(11.5), frame="trav")
for (a0, a1) in ((A0, 1.5), (15.5, A1)):
    V.prism(P, "trav", V.rect(a0, a1, 41.0, 50.0), G - 0.3, H(7.0), top_mat="lead")

# ------------------------------------------------------------------ walls: bands, cornices, cresting, windows
def side_faces():
    out = []
    for (o0, o1) in ((5.0, CROSS[0]), (CROSS[1], 41.0)):
        out.append(V.frame(A0, o0, A0, o1, inside=(AC, 20)) + (SIDE,))
        out.append(V.frame(A1, o0, A1, o1, inside=(AC, 20)) + (SIDE,))
    return out
for F, L, top in side_faces():
    banded(P, F, 0, L, G, top)
    pbox(bm_for(P, "trav"), F, -0.3, L + 0.3, top - 0.7, top, 0, 0.55)
    cresting(P, F, 0, L, top)
    n = max(1, int(L / 5.5))
    for i in range(n):
        u = (i + 0.5) * L / n
        for du in (-0.75, 0.75):                                  # tall paired horseshoe windows
            horseshoe(P, F, u + du, H(5.5), 1.2, H(11.8), fw=0.18)
        pbox(bm_for(P, "trav"), F, u - 0.08, u + 0.08, H(5.5), H(11.6), 0, 0.15)
        horseshoe(P, F, u, H(1.2), 1.0, H(3.2), fw=0.15)
# the cross arms' ends (north and south): banded wall, the great arch, a three-light window and a rose
for (a, ins) in ((A0, (AC, 27.5)), (A1, (AC, 27.5))):
    F, L = V.frame(a, CROSS[0], a, CROSS[1], inside=ins)
    banded(P, F, 0, L, G, H(18.0))
    arch_gable(P, F, 0, L, H(18.0))
    banded(P, F, 1.0, L - 1.0, H(18.0), H(18.0) + L / 2 - 1.2, n=0.04)
    pbox(bm_for(P, "trav"), F, -0.3, L + 0.3, H(17.4), H(18.0), 0, 0.5)
    for du in (-2.2, 0, 2.2):
        horseshoe(P, F, L / 2 + du, H(9.5), 1.6 if du == 0 else 1.3, H(15.0) if du == 0 else H(14.2), fw=0.2)
    oculus(P, F, L / 2, H(21.6), 1.4, frame="trav", fill="glass", fw=0.3)
    for du in (-4.6, 4.6):
        horseshoe(P, F, L / 2 + du, H(2.0), 1.4, H(6.5), fw=0.2)
# the rear wall of the middle arm above the apse
Fr, Lr = V.frame(T_IN, 41.0, 16.5, 41.0, inside=(AC, 30))
arch_gable(P, Fr, 0, Lr, H(16.5))
# ------------------------------------------------------------------ the front (o = -1) between the towers
Ff, Lf = V.frame(T_IN, -1.0, 16.5, -1.0, inside=(AC, 10))         # u from the north tower to the south one
arch_gable(P, Ff, 0, Lf, H(16.5))
banded(P, Ff, 0, Lf, H(10.8), H(16.5))
banded(P, Ff, 1.0, Lf - 1.0, H(16.5), H(22.6), n=0.04)
# the portico: three horseshoe arches on columns, dark behind (a loggia ≈3 m deep), the frieze over it
for (u, w, sp) in ((Lf / 2 - 5.0, 3.6, H(6.0)), (Lf / 2, 4.4, H(6.4)), (Lf / 2 + 5.0, 3.6, H(6.0))):
    horseshoe(P, Ff, u, G, w, sp, fill="dark", frame="trav", fw=0.35, n=0.06)
    ring(P, "pink", Ff, u, sp, w / 2 + 0.35, w / 2 + 0.6, 0, 0.12, a0=-0.38, a1=math.pi + 0.38, seg=16, soffit=False)
    poly(bm_for(P, "wood"), [Ff.p(u - 0.9, G, 0.08), Ff.p(u + 0.9, G, 0.08), Ff.p(u + 0.9, G + 3.6, 0.08), Ff.p(u - 0.9, G + 3.6, 0.08)])
for u in (Lf / 2 - 7.2, Lf / 2 - 2.6, Lf / 2 + 2.6, Lf / 2 + 7.2):  # the columns between the arches
    cylinder(P, "trav", Ff.p(u, 0, 0.55), 0.28, G + 0.4, H(5.6), seg=10)
    pbox(bm_for(P, "trav"), Ff, u - 0.45, u + 0.45, G, G + 0.4, 0.1, 0.95)
    pbox(bm_for(P, "trav"), Ff, u - 0.5, u + 0.5, H(5.6), H(6.1), 0.1, 1.0)
pbox(bm_for(P, "trav"), Ff, 0, Lf, H(9.6), H(10.8), 0, 0.35)                                     # frieze and cornice
for k in range(int(Lf / 0.8)):
    pbox(bm_for(P, "pink"), Ff, 0.2 + k * 0.8, 0.6 + k * 0.8, H(9.8), H(10.6), 0, 0.42)
pbox(bm_for(P, "trav"), Ff, -0.2, Lf + 0.2, H(10.8), H(11.2), 0, 0.6)
for u in (Lf / 2 - 4.2, Lf / 2 + 4.2):                            # paired horseshoe windows over the portico
    for du in (-0.85, 0.85):
        horseshoe(P, Ff, u + du, H(12.0), 1.3, H(15.0), fw=0.2)
    pbox(bm_for(P, "trav"), Ff, u - 0.1, u + 0.1, H(12.0), H(14.9), 0, 0.16)
    pbox(bm_for(P, "trav"), Ff, u - 2.0, u + 2.0, H(11.6), H(12.0), 0, 0.3)
for du in (-1.55, 0, 1.55):                                      # in the arch: a three-light window, two single ones, a rose
    horseshoe(P, Ff, Lf / 2 + du, H(17.2), 1.2, H(20.0), fw=0.2)
for du in (-5.0, 5.0):
    horseshoe(P, Ff, Lf / 2 + du, H(17.2), 1.2, H(19.4), fw=0.2)
oculus(P, Ff, Lf / 2, H(22.2), 0.9, frame="trav", fill="glass", fw=0.25)
# ------------------------------------------------------------------ the towers
for ac_ in (-2.5, 19.5):
    TW = V.rect(ac_ - 3.0, ac_ + 3.0, -1.0, 5.0)
    V.prism(P, "trav", TW, G - 0.3, H(21.0), top_mat="lead")
    for F, L, p0, p1 in V.edges(TW):
        banded(P, F, 0, L, G, H(20.4))
        pbox(bm_for(P, "trav"), F, -0.3, L + 0.3, H(20.3), H(21.0), 0, 0.5)
        cresting(P, F, 0, L, H(21.0), step=0.75, h=0.6)
        horseshoe(P, F, L / 2, H(8.0), 0.9, H(11.6), fw=0.18)
        horseshoe(P, F, L / 2, H(13.6), 0.9, H(16.8), fw=0.18)
    tc = V.W(ac_, 2.0)
    TB = V.rect(ac_ - 2.1, ac_ + 2.1, -0.1, 4.1)                  # the belfry stage: open arches on each face
    V.prism(P, "trav", TB, H(21.0), H(27.0), top_mat="lead")
    for F, L, p0, p1 in V.edges(TB):
        banded(P, F, 0, L, H(21.0), H(26.2))
        for du in (-0.8, 0.8):
            horseshoe(P, F, L / 2 + du, H(22.0), 1.1, H(25.0), fill="dark", fw=0.16)
        pbox(bm_for(P, "trav"), F, -0.25, L + 0.25, H(26.2), H(27.0), 0, 0.4)
    cylinder(P, "trav", tc, 1.75, H(27.0), H(28.0), seg=16)
    t2 = dome(P, tc, 1.95, H(28.0), 4.0, ribs=12, mat="copper", seg=20, rib_mat="copper_rib")
    cone(P, "copper", tc, 0.35, 0.05, t2 - 0.1, t2 + 1.3, seg=8); sphere(P, "gold", tc + Vector((0, 0, t2 + 0.5)), 0.22)
# ------------------------------------------------------------------ the drum and the great dome over the crossing
c = V.W(AC, 27.5); R = 8.6; DR0, DR1 = H(24.0), H(31.2)
cylinder(P, "trav", c, R, DR0, DR1, seg=32)
for k in range(int((DR1 - DR0) / 1.1)):
    if k % 2: cylinder(P, "pink", c, R + 0.03, DR0 + k * 1.1, DR0 + k * 1.1 + 0.55, seg=32, cap=False)
for k in range(16):                                               # arched windows round the drum, pilasters between
    t = 2 * math.pi * (k + 0.5) / 16; d = Vector((math.cos(t), math.sin(t), 0)); Fd = Frame(c + d * (R + 0.05), Vector((-d.y, d.x, 0)), d)
    horseshoe(P, Fd, 0, DR0 + 1.6, 1.3, DR0 + 4.6, fw=0.18)
    t3 = 2 * math.pi * k / 16; d3 = Vector((math.cos(t3), math.sin(t3), 0)); F3 = Frame(c + d3 * (R + 0.05), Vector((-d3.y, d3.x, 0)), d3)
    pbox(bm_for(P, "trav"), F3, -0.3, 0.3, DR0 + 0.6, DR1 - 0.8, 0, 0.25)
cylinder(P, "trav", c, R + 0.5, DR1 - 0.8, DR1, seg=32)                                          # its cornice
for k in range(48):                                               # a ring of small arches under the cornice
    t = 2 * math.pi * k / 48; d = Vector((math.cos(t), math.sin(t), 0)); Fd = Frame(c + d * (R + 0.05), Vector((-d.y, d.x, 0)), d)
    ring(P, "trav", Fd, 0, DR1 - 1.3, 0.42, 0.55, 0, 0.2, seg=6, soffit=False)
top = dome(P, c, R + 0.2, DR1, 14.8, ribs=24, mat="copper", seg=40, rib_mat="copper_rib")     # slightly raised profile
cylinder(P, "copper", c, 1.1, top - 0.4, top + 0.6, seg=12)
cone(P, "copper", c, 0.9, 0.12, top + 0.6, top + 2.4, seg=12); sphere(P, "gold", c + Vector((0, 0, top + 2.6)), 0.4)
# ------------------------------------------------------------------ the front garden: railing, gate, lamp pillars, palms
Fg = Frame(V.W(-9.0, -13.0), S.TA, -S.NO)                         # Via Farini's line (≈ 12 m in front of the portico)
pbox(bm_for(GD, "trav"), Fg, 0, 40.0, G, G + 0.8, -0.3, 0.3)
for k in range(int(40.0 / 0.25)):
    u = k * 0.25
    if 17.0 < u < 23.0: continue                                  # the gate
    pbox(bm_for(GD, "iron"), Fg, u, u + 0.04, G + 0.8, G + 2.9, -0.02, 0.02)
pbox(bm_for(GD, "iron"), Fg, 0, 40, G + 2.8, G + 2.9, -0.04, 0.04); pbox(bm_for(GD, "iron"), Fg, 0, 40, G + 1.0, G + 1.08, -0.04, 0.04)
for k in range(int(6.0 / 0.18)):
    pbox(bm_for(GD, "iron"), Fg, 17.0 + k * 0.18, 17.04 + k * 0.18, G + 0.1, G + 3.6, -0.02, 0.02)
for u in (16.6, 23.4):                                            # lamp pillars by the gate
    cylinder(GD, "iron", Fg.p(u, 0, 0), 0.25, G, G + 4.6, seg=8)
    sphere(GD, "frost" if "frost" in MAT else "marble", Fg.p(u, G + 4.9, 0), 0.35)
V.prism(GD, "lawn", V.rect(-9.0, 31.0, -13.0, -1.2), G - 0.2, G + 0.06)
for (a, o) in ((-3.5, -6.0), (21.0, -7.0)):                       # palms
    tc = V.W(a, o); cylinder(GD, "trunk", tc, 0.22, G, G + 9.5, seg=8)
    for k in range(9):
        t = 2 * math.pi * k / 9; d = Vector((math.cos(t), math.sin(t), 0))
        poly(bm_for(GD, "palm"), [tc + Vector((0, 0, G + 9.5)), tc + d * 3.2 + Vector((0, 0, G + 8.4)) + Vector((-d.y, d.x, 0)) * 0.45, tc + d * 3.4 + Vector((0, 0, G + 8.0)), tc + d * 3.2 + Vector((0, 0, G + 8.4)) - Vector((-d.y, d.x, 0)) * 0.45])
K.export("sinagoga")
