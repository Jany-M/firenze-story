"""Santa Maria Novella station (1935), the Palazzina Reale (1935) and the Maria Antonia station before them (1848) – v1.

Run:  python pipeline/47_moderni.py ; blender -b --python blender/scripts/build_stazione_smn.py → web/public/models/landmarks/stazione_smn.glb
Frame: a along the front on Piazza della Stazione from its west corner (A = -636, -437 scene; a grows eastwards), o inwards
(northwards, along the tracks). Ground 8.3 m (scene).

Measured (LiDAR 2023 DSM, height above the ground, read in this frame):
  the front at o ≈ 3; a low band 7–9 m from a -10 to 30; the clock block 13–14 m (a -10..4, o 24..50); the glazed
  "cascade" 9–13 m (a 4..30); the high block 14–15 m (a 30..116, o 12..50) whose front swings back north-east from
  a 62 to a 116 (o 12 → 31); the canopy 5–6 m in front of it; the east wing 12–14 m along Via Valfonda leaning with the
  tracks (a ≈ 116 − 0.21·(o − 30)); the west wing 10–13 m (16–18 m on its outer side) along Via Alamanni; platform
  canopies 3–4 m from o ≈ 66; the Palazzina Reale 9–12 m (a 80..112, o 188..218) with a low gallery west of it.
From photographs (Commons; credited in docs/landmarks/STAZIONE-SMN.md): the long low front in pietra forte, the clock
block with its square clock, the cascade of frosted glass in two tiers between two stone blocks, the flat canopy with a
deep fascia running along the front and the whole east side, the blind stone walls with their courses; the Palazzina in
white marble with a grid of windows, a tall glazed entrance and the portico of honour by the exedra with Italo
Griselli's "The Arno and its valley".
History: Gruppo Toscano (Michelucci, Baroni, Berardi, Gamberini, Guarnieri, Lusanna), competition 1932, inaugurated
30 October 1935; the Palazzina Reale inaugurated October 1935 (fondazionefs.it). The Maria Antonia station opened
3 February 1848 (Museo Galileo), much nearer the church; drawn from the map of 1873 and a photograph of c. 1900: a
two-storey block with a clock turret, lower wings and a train shed with four tracks (*inferred* sizes); shown to 1934.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from landmark_detail import *
from landmark_church import Site, extra_materials
from landmark_volume import Vol, glass_wall, punched, arched_row, tracks
from mathutils import Vector
K.reset()
MAT["pf"] = material("pietra_forte_smn", None, (0.69, 0.57, 0.4), 0.85)            # plain: the courses are drawn as joints
MAT["pf_joint"] = material("pietra_forte_joint", None, (0.5, 0.41, 0.29), 0.9)
MAT["pf_trim"] = material("pietra_forte_trim", None, (0.47, 0.39, 0.28), 0.8)
MAT["frost"] = material("glass_frosted", None, (0.8, 0.84, 0.86), 0.35)
MAT["glass"] = material("station_glass", None, (0.12, 0.15, 0.17), 0.12, metal=0.2)
MAT["glass_roof"] = material("glass_roof", None, (0.55, 0.62, 0.66), 0.2, metal=0.1)
MAT["steel"] = material("steel_dark", None, (0.16, 0.16, 0.16), 0.5, metal=0.6)
MAT["concrete"] = material("canopy_concrete", None, (0.72, 0.71, 0.67), 0.85)
MAT["roof_m"] = material("flat_roof", None, (0.5, 0.49, 0.46), 0.9)
MAT["platform"] = material("platform_paving", None, (0.62, 0.6, 0.56), 0.9)
MAT["ballast"] = material("track_ballast", None, (0.33, 0.3, 0.27), 1.0)
MAT["rail"] = material("rail_steel", None, (0.46, 0.44, 0.42), 0.4, metal=0.7)
MAT["marble_w"] = material("marble_palazzina", "marble_white", (0.92, 0.91, 0.88), 0.5, 0.3)
MAT["plaster"] = material("plaster_ochre", None, (0.86, 0.78, 0.62), 0.9)
MAT["serena"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)
MAT["clock"] = material("clock_face", None, (0.9, 0.9, 0.86), 0.5)
extra_materials()
NOW = K.NOW
S = Site("smn", "moderni"); G = S.G; V = Vol(S)
NEW = f"fabbricato_viaggiatori@1935-{NOW}"; PAL = f"palazzina_reale@1935-{NOW}"
MA = "maria_antonia@1848-1934"; TR = f"binari@1935-{NOW}"; TR_OLD = "binari_maria_antonia@1848-1934"; YARD = f"binari_scalo@1848-{NOW}"
LEAN = 0.21                                                       # the tracks lean west in this frame (≈ 12°)
def a_east(o): return 116.0 - LEAN * (o - 30.0)                   # the east wing's outer face (Via Valfonda)
def a_west(o): return -34.0 - LEAN * (o - 50.0)                   # the west wing's inner face (towards the tracks)

def stone_block(part, pts, h, cornice=0.45, trim=True):
    """A pietra forte mass with a thin projecting coping; its walls blind (the station's walls have few openings)."""
    V.prism(part, "pf", pts, G - 0.3, h, top_mat="roof_m")
    E = V.edges(pts)
    for F, L, p0, p1 in E:
        if trim: pbox(bm_for(part, "pf_trim"), F, -0.15, L + 0.15, h - cornice, h, 0, 0.35)
        courses_on(part, F, L, G + 0.6, h - cornice - 0.2)
    return E
def courses_on(part, F, L, v0, v1, step=0.62):
    """The ashlar courses of the pietra forte walls: thin darker joints across the whole face (photos: long, even beds)."""
    v = v0
    while v < v1:
        pbox(bm_for(part, "pf_joint"), F, 0.02, L - 0.02, v, v + 0.05, 0, 0.015); v += step

# ------------------------------------------------------------------ the passenger building (1935)
H_CLK, H_LOW, H_CAS, H_HIGH = G + 13.8, G + 8.4, G + 13.6, G + 14.8      # the upper glass rises to the blocks' tops
# the clock block, west end of the front (a -10..4): its tall part behind a low band of the same stone
stone_block(NEW, V.rect(-10, 4, 24, 50), H_CLK)
stone_block(NEW, V.rect(-10, 4, 3, 24), H_LOW)
Fc, _ = V.frame(-10, 24, 4, 24, inside=(0, 40))                 # the clock, high on the block's front by the glass
pbox(bm_for(NEW, "steel"), Fc, 9.4, 12.6, H_CLK - 4.6, H_CLK - 1.0, 0, 0.35)
pbox(bm_for(NEW, "glass"), Fc, 9.8, 12.2, H_CLK - 4.2, H_CLK - 1.4, 0, 0.4)
for vv in (H_CLK - 3.3, H_CLK - 2.2):                             # hours above minutes, white figures on dark glass
    for du in (10.35, 11.35):
        pbox(bm_for(NEW, "clock"), Fc, du, du + 0.32, vv - 0.42, vv + 0.42, 0, 0.44)
Ff, _ = V.frame(-10, 3, 4, 3, inside=(0, 10))
punched(NEW, Ff, 0.5, 13.5, G + 0.2, G + 3.2, 1.6, 3.2, fill="glass", frame="steel")    # doors under the low band
# the cascade (a 4..30): a stone base, then frosted glass in two tiers stepping back up to the clock block's height
V.prism(NEW, "pf", V.rect(4, 30, 3, 6), G - 0.3, G + 3.0, top_mat="pf_trim")
Fb, _ = V.frame(4, 3, 30, 3, inside=(15, 10))
punched(NEW, Fb, 0.5, 25.5, G + 0.2, G + 2.8, 2.2, 3.25, fill="glass", frame="steel")
V.prism(NEW, "frost", V.rect(4, 30, 6, 24), G + 3.0, H_LOW, top_mat="glass_roof")
glass_wall(NEW, V.frame(4, 6, 30, 6, inside=(15, 15))[0], 0, 26, G + 3.0, H_LOW, 8, rows=3, glass="frost")
V.prism(NEW, "frost", V.rect(4, 30, 24, 50), H_LOW, H_CAS, top_mat="glass_roof")
glass_wall(NEW, V.frame(4, 24, 30, 24, inside=(15, 35))[0], 0, 26, H_LOW, H_CAS, 7, rows=2, glass="frost")
for o in range(26, 50, 3):                                       # ribs of the glazed roof
    pbox(bm_for(NEW, "steel"), Frame(V.W(4, o), S.TA, S.NO), 0, 26, H_CAS, H_CAS + 0.25, -0.12, 0.12)
# the high block east of the cascade; its front swings back north-east (DSM), the canopy runs in front of it
HIGH = [(30, 12), (62, 12), (64, 18), (98, 28), (116, 31), (a_east(50), 50), (30, 50)]
for F, L, p0, p1 in stone_block(NEW, HIGH, H_HIGH):
    if p0[1] < 40 and p1[1] < 40 and L > 5:                       # shop fronts under the canopy
        glass_wall(NEW, F, 0.6, L - 0.6, G, G + 4.4, max(2, int(L / 4.5)), rows=1)
CAN = [(30, 0), (64, 0), (121, 19.5), (a_east(31) + 9, 31), (a_east(31), 31), (116, 31), (98, 28), (64, 18), (62, 12), (30, 12)]
V.prism(NEW, "concrete", CAN, G + 4.6, G + 5.5, top=True, bottom=True)
for F, L, p0, p1 in V.edges(CAN):
    if L > 3: pbox(bm_for(NEW, "pf_trim"), F, 0, L, G + 4.5, G + 5.6, 0, 0.12)          # its deep fascia
for a in (34, 44, 54):                                            # slim steel posts at the front corner of the canopy
    cylinder(NEW, "steel", V.W(a, 0.8), 0.14, G, G + 4.6, seg=8)
# the east wing along Via Valfonda: a long blind wall leaning with the tracks, its canopy (the taxi rank) along it
EW = [(a_east(30) - 12, 30), (a_east(30), 30), (a_east(205), 205), (a_east(205) - 12, 205)]
stone_block(NEW, EW, G + 14.0)
Fe, Le = V.frame(a_east(30), 30, a_east(205), 205, inside=(a_east(100) - 6, 100))
glass_wall(NEW, Fe, 3, Le - 3, G, G + 4.3, int(Le / 5), rows=1)
ECAN = [(a_east(31), 31), (a_east(31) + 9, 31), (a_east(195) + 9, 195), (a_east(195), 195)]
V.prism(NEW, "concrete", ECAN, G + 4.6, G + 5.5, top=True, bottom=True)
for F, L, p0, p1 in V.edges(ECAN):
    pbox(bm_for(NEW, "pf_trim"), F, 0, L, G + 4.5, G + 5.6, 0, 0.12)
# the gallery at the head of the tracks (o 50..66): a glazed roof over the concourse, open to the platforms
GAL = [(a_west(50) - 2, 50), (a_east(50) - 12, 50), (a_east(66) - 12, 66), (a_west(66) - 2, 66)]
V.prism(NEW, "pf", GAL, G + 10.0, G + 11.0, top_mat="glass_roof")
for k in range(int((a_east(50) - a_west(50)) / 5)):
    a = a_west(50) + 2 + k * 5
    pbox(bm_for(NEW, "steel"), Frame(V.W(a, 50), S.NO, -S.TA), 0, 16, G + 11.0, G + 11.4, -0.1, 0.1)
Fg, Lg = V.frame(a_west(66) - 2, 66, a_east(66) - 12, 66, inside=(40, 55))
glass_wall(NEW, Fg, 0, Lg, G + 5.2, G + 10.0, 24, rows=1, glass="frost")
# the west wing along Via Alamanni (offices: three floors of windows, arched at the ground floor), its rounded corner
WW = [(a_west(46) - 22, 46), (a_west(46), 46), (a_west(205), 205), (a_west(205) - 22, 205)]
V.prism(NEW, "pf", WW, G - 0.3, G + 12.0, top_mat="roof_m")
V.prism(NEW, "pf", [(a_west(60) - 22, 60), (a_west(60) - 15, 60), (a_west(200) - 15, 200), (a_west(200) - 22, 200)], G + 12.0, G + 17.0, top_mat="roof_m")
for F, L, p0, p1 in V.edges(WW):
    pbox(bm_for(NEW, "pf_trim"), F, -0.1, L + 0.1, G + 11.6, G + 12.0, 0, 0.35)
    courses_on(NEW, F, L, G + 11.0, G + 11.5)
Fw, Lw = V.frame(a_west(46) - 22, 46, a_west(205) - 22, 205, inside=(a_west(100) - 10, 100))   # the street front
arched_row(NEW, Fw, 14, Lw - 3, G + 0.2, G + 3.0, 1.8, 4.4, fill="glass", frame=None)
punched(NEW, Fw, 14, Lw - 3, G + 5.0, G + 6.8, 1.3, 4.4, fill="glass", frame="pf_trim")
punched(NEW, Fw, 14, Lw - 3, G + 8.6, G + 10.4, 1.3, 4.4, fill="glass", frame="pf_trim")
cyl_c = V.W(a_west(46) - 11, 52)                                 # the curved corner towards the square (photo "lato 02")
cylinder(NEW, "pf", cyl_c, 10.0, G - 0.3, G + 10.0, seg=28)
cylinder(NEW, "pf", cyl_c, 8.5, G + 10.0, G + 12.6, seg=28)
Fr, _ = V.frame(a_west(46) - 20, 42, a_west(46) - 2, 42, inside=(a_west(46) - 11, 52))
glass_wall(NEW, Fr, 5.0, 13.0, G + 0.3, G + 7.5, 3, rows=3)
# the platforms and their flat canopies on one row of posts (o 66 → 300), the tracks between them
def pcen(k, o): return a_west(o) + 5.0 + k * 15.2
for k in range(9):
    P0, P1 = 66.0, 300.0
    pts = [(pcen(k, P0) - 3.0, P0), (pcen(k, P0) + 3.0, P0), (pcen(k, P1) + 3.0, P1), (pcen(k, P1) - 3.0, P1)]
    V.prism(TR, "platform", pts, G - 0.2, G + 0.55)
    cpts = [(pcen(k, P0) - 2.8, P0 + 2), (pcen(k, P0) + 2.8, P0 + 2), (pcen(k, 280) + 2.8, 280), (pcen(k, 280) - 2.8, 280)]
    V.prism(TR, "concrete", cpts, G + 4.0, G + 4.4, bottom=True)
    for o in range(72, 280, 12):
        pbox(bm_for(TR, "concrete"), Frame(V.W(pcen(k, o), o), S.TA, S.NO), -0.25, 0.25, G + 0.55, G + 4.0, -0.4, 0.4)
    tracks(V, TR, lambda o, k=k: pcen(k, o) + 5.3, 64, 300, 2, pitch=4.6, g=G)
    for d in (5.3, 9.9):                                          # buffer stops at the head of each track
        pbox(bm_for(TR, "steel"), Frame(V.W(pcen(k, 64) + d, 64), S.TA, S.NO), -1.0, 1.0, G + 0.3, G + 1.2, -0.3, 0.3)
    # the yard beyond the platforms: the same tracks run on north-west (o 300 → 430)
    tracks(V, YARD, lambda o, k=k: pcen(k, o) + 5.3, 300, 430, 2, pitch=4.6, g=G)

# ------------------------------------------------------------------ the Palazzina Reale (1935), north of the east wing
PALB = V.rect(80, 112, 188, 218); HP = G + 11.6
V.prism(PAL, "marble_w", PALB, G - 0.3, HP, top_mat="roof_m")
for F, L, p0, p1 in V.edges(PALB):
    pbox(bm_for(PAL, "marble_w"), F, -0.2, L + 0.2, HP - 0.5, HP, 0, 0.4)                 # thin coping
Fn, Ln = V.frame(80, 218, 112, 218, inside=(96, 200))                                      # north: a grid of windows
punched(PAL, Fn, 1.5, Ln - 1.5, G + 1.0, G + 4.6, 2.2, 4.6, fill="glass", frame="steel")
punched(PAL, Fn, 1.5, Ln - 1.5, G + 6.4, G + 9.4, 2.2, 4.6, fill="glass", frame="steel")
Fe2, Le2 = V.frame(112, 188, 112, 218, inside=(96, 200))                                   # east: the tall glazed entrance
poly(bm_for(PAL, "dark"), [Fe2.p(Le2 / 2 - 3.2, G, 0.03), Fe2.p(Le2 / 2 + 3.2, G, 0.03), Fe2.p(Le2 / 2 + 3.2, G + 9.6, 0.03), Fe2.p(Le2 / 2 - 3.2, G + 9.6, 0.03)])
glass_wall(PAL, Fe2, Le2 / 2 - 2.8, Le2 / 2 + 2.8, G, G + 9.4, 4, rows=4)
punched(PAL, Fe2, 1.5, Le2 / 2 - 4.5, G + 6.4, G + 9.4, 2.0, 4.2, fill="glass", frame="steel")
punched(PAL, Fe2, Le2 / 2 + 4.5, Le2 - 1.5, G + 6.4, G + 9.4, 2.0, 4.2, fill="glass", frame="steel")
# the portico of honour on slim marble piers along the east side, the exedra with the sculpture group in its basin
V.prism(PAL, "marble_w", V.rect(112, 122, 190, 216), G + 7.4, G + 8.2, bottom=True)
for o in range(191, 217, 3):
    pbox(bm_for(PAL, "marble_w"), Frame(V.W(120.5, o), S.TA, S.NO), -0.35, 0.35, G, G + 7.4, -0.35, 0.35)
c_ex = V.W(132, 203)
for k in range(13):                                               # the exedra wall, open towards the portico
    t0 = -math.pi / 2 + math.pi * k / 13; t1 = -math.pi / 2 + math.pi * (k + 1) / 13
    u = S.TA * math.cos(t0) + S.NO * math.sin(t0); w = S.TA * math.cos(t1) + S.NO * math.sin(t1)
    poly(bm_for(PAL, "marble_w"), [c_ex + u * 13 + Vector((0, 0, G)), c_ex + w * 13 + Vector((0, 0, G)), c_ex + w * 13 + Vector((0, 0, G + 3.2)), c_ex + u * 13 + Vector((0, 0, G + 3.2))])
fc = V.W(128, 203)
cylinder(PAL, "marble_w", fc, 4.2, G, G + 0.7, seg=24)
cylinder(PAL, "water", fc, 3.8, G + 0.7, G + 0.74, seg=24)
pbox(bm_for(PAL, "marble"), Frame(fc, S.TA, S.NO), -1.6, 1.6, G + 0.7, G + 1.9, -0.9, 0.9)
for dx, hh in ((-0.7, 2.3), (0.7, 2.0)):                          # two figures (the Arno and his valley)
    pbox(bm_for(PAL, "marble"), Frame(fc, S.TA, S.NO), dx - 0.45, dx + 0.45, G + 1.9, G + 1.9 + hh, -0.5, 0.4)
    sphere(PAL, "marble", fc + S.TA * dx + Vector((0, 0, G + 2.2 + hh)), 0.28)
V.prism(PAL, "pf", V.rect(56, 80, 188, 216), G - 0.3, G + 4.2, top_mat="roof_m")              # the low gallery to the platforms
glass_wall(PAL, V.frame(56, 216, 80, 216, inside=(68, 200))[0], 1, 23, G, G + 3.6, 6, rows=1)

# ------------------------------------------------------------------ the Maria Antonia station (1848–1934), nearer the church
OF = -45.0                                                        # its front (map of 1873: ≈ 40 m south of today's)
for (a0, a1, o0, h, ridge) in ((52, 90, OF, G + 11.0, G + 14.2), (30, 52, OF + 3, G + 6.6, G + 9.0), (90, 112, OF + 3, G + 6.6, G + 9.0)):
    V.prism(MA, "plaster", V.rect(a0, a1, o0, OF + 17), G - 0.3, h, top=False)
    V.hip(MA, "roof", a0, a1, o0, OF + 17, h, ridge, over=0.6)
    F, L = V.frame(a0, o0, a1, o0, inside=((a0 + a1) / 2, o0 + 5))
    pbox(bm_for(MA, "serena"), F, -0.3, L + 0.3, h - 0.5, h, 0, 0.45)
    arched_row(MA, F, 1.5, L - 1.5, G + 0.1, G + 3.6, 1.8, 3.8, fill="dark", frame="serena", fw=0.25)
    if h > G + 8:
        pbox(bm_for(MA, "serena"), F, 0, L, G + 5.2, G + 5.5, 0, 0.25)
        punched(MA, F, 1.5, L - 1.5, G + 6.6, G + 9.0, 1.2, 3.8, fill="dark", frame="serena")
tc = V.W(71, OF + 6)                                              # the clock turret on the middle of the front (photo c. 1900)
pbox(bm_for(MA, "plaster"), Frame(tc, S.TA, S.NO), -1.8, 1.8, G + 11.0, G + 16.2, -1.8, 1.8)
Ft = Frame(tc - S.NO * 1.8, S.TA, -S.NO)
poly(bm_for(MA, "clock"), [Ft.p(-1.0, G + 13.2, 0.03), Ft.p(1.0, G + 13.2, 0.03), Ft.p(1.0, G + 15.2, 0.03), Ft.p(-1.0, G + 15.2, 0.03)])
V.hip(MA, "roof", 69.2, 72.8, OF + 4.2, OF + 7.8, G + 16.2, G + 17.6, over=0.4)
SHED = V.rect(44, 100, OF + 17, 115)                              # the train shed over its four tracks
V.prism(MA, "plaster", SHED, G - 0.3, G + 8.0, top=False)
V.gable(MA, "roof", 44, 100, OF + 17, 115, G + 8.0, G + 14.0, along="o", gable_mat="plaster")
V.prism(MA, "glass_roof", V.rect(69, 75, OF + 19, 112), G + 13.4, G + 15.2)                  # a glazed lantern on the ridge
for F, L, p0, p1 in V.edges(SHED):
    if L > 100: arched_row(MA, F, 3, L - 3, G + 4.8, G + 6.4, 1.6, 6.0, fill="dark", frame="serena", fw=0.2)
tracks(V, TR_OLD, lambda o: 63.0 - LEAN * (o - 115), 115, 300, 4, pitch=4.6, g=G)
K.export("stazione_smn")
