"""Teatro del Maggio Musicale Fiorentino (Opera di Firenze) – v1.

Run:  python pipeline/47_moderni.py ; blender -b --python blender/scripts/build_teatro_maggio.py → web/public/models/landmarks/teatro_maggio.glb
Frame: a along the south-west side on Piazza Vittorio Gui from the west corner (OSM relation 3609352; a grows
east-south-east), o inwards (north-north-east). Ground 4.4 m (scene).
Measured (LiDAR 2023 DSM, height above the ground, read in this frame – _dev/tmp/asc_tea.txt; outline OSM):
  the west block a 0..36 over the whole depth 16–20 m; the white block of the great hall a 36..72, o 0..30, 32–34 m;
  the fly tower a 40..70, o 30..66, 34–38 m; a middle block o 66..92 14–16 m; the rear wing a 36..136, o 92..130,
  12–14 m round a courtyard (OSM inner ring a 94..111, o 92..120); two arms of the inclined base o 0..18 and o 65..86
  falling from 12–14 m at a 70 to the ground at a 140–166; between them the open-air cavea, its seats rising from
  16–18 m at a 76 to 24–26 m at a 134, closed by a wall at a 136.
From photographs (Commons: Manuelarosi 2017 and 2025, Sailko 2014 and 2018, Dennis Radaelli 2019, Peaceray; credited
on the library page): the great hall a block clad in pale stone, its top slightly slanted, a few square windows and a
long band window, the name on a dark panel at its top corner; the foyer below glazed between white piers carrying the
red letters of MAGGIO; the sloping stone walls of the base walked over to the terraces; the fly tower dark, clad in
glazed terracotta (ABDR); the cavea's stage in front of the fly tower's dark wall.
History: designed by Paolo Desideri (ABDR); the base and its roofs are public space – square, terraces, cavea (Desideri,
artribune.com); fly tower 35 m (risorgimentofirenze.it); inaugurated 21 December 2011 (maggiofiorentino.com); full
seasons from 2014. Shown from 2011.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from landmark_detail import *
from landmark_church import Site, extra_materials
from landmark_volume import Vol, glass_wall, punched
from mathutils import Vector
K.reset()
MAT["stone"] = material("pale_limestone", "marble_white", (0.88, 0.86, 0.82), 0.7, 0.2, tint=(0.97, 0.95, 0.92))
MAT["paving"] = material("terrace_paving", "lastrico", (0.72, 0.7, 0.66), 0.85, 0.3, tint=(1.25, 1.22, 1.18))
MAT["cotto_g"] = material("glazed_terracotta_dark", None, (0.2, 0.21, 0.23), 0.35, metal=0.3)
MAT["cotto_l"] = material("glazed_terracotta_line", None, (0.34, 0.35, 0.37), 0.3, metal=0.3)
MAT["glass"] = material("foyer_glass", None, (0.14, 0.18, 0.2), 0.1, metal=0.3)
MAT["steel"] = material("steel_grey", None, (0.3, 0.3, 0.3), 0.5, metal=0.6)
MAT["red"] = material("letters_red", None, (0.72, 0.1, 0.1), 0.5)
MAT["seat"] = material("cavea_steps", None, (0.8, 0.78, 0.74), 0.8)
MAT["sign"] = material("sign_panel", None, (0.12, 0.12, 0.13), 0.5)
extra_materials()
NOW = K.NOW
S = Site("teatro", "moderni"); G = S.G; V = Vol(S)
T = f"teatro_maggio@2011-{NOW}"
def H(z): return G + z

def wedge(part, mat, a0, a1, o0, o1, h0, h1, top="paving"):
    """A block whose top falls along a from h0 (at a0) to h1 (at a1): the inclined base."""
    lo = [V.W(a0, o0, G - 0.3), V.W(a1, o0, G - 0.3), V.W(a1, o1, G - 0.3), V.W(a0, o1, G - 0.3)]
    hi = [V.W(a0, o0, h0), V.W(a1, o0, h1), V.W(a1, o1, h1), V.W(a0, o1, h0)]
    bm = bm_for(part, mat)
    for i in range(4):
        j = (i + 1) % 4; poly(bm, [lo[i], lo[j], hi[j], hi[i]])
    poly(bm_for(part, top), hi)
def slit_windows(F, L, rows, w=3.6, pitch=7.2):
    for (v0, v1) in rows:
        punched(T, F, 2.0, L - 2.0, v0, v1, w, pitch, fill="glass", frame=None)

# ------------------------------------------------------------------ the west block (rehearsal rooms, offices)
WB = [(0.0, 0.0), (36.0, 0.0), (36.0, 132.0), (-0.4, 133.2)]
V.prism(T, "stone", WB, G - 0.3, H(17.0), top_mat="paving")
for F, L, p0, p1 in V.edges(WB):
    if L > 30: slit_windows(F, L, ((H(3.0), H(5.0)), (H(8.0), H(9.4)), (H(12.6), H(14.0))))
    pbox(bm_for(T, "stone"), F, -0.1, L + 0.1, H(16.6), H(17.6), 0, 0.12)                     # a parapet edge
# ------------------------------------------------------------------ the great hall: the white block on the square
HB = V.rect(36.0, 72.0, 0.0, 32.0)
lo = [V.W(a, o, G - 0.3) for a, o in HB]
hi = [V.W(36.0, 0.0, H(35.0)), V.W(72.0, 0.0, H(32.0)), V.W(72.0, 32.0, H(32.0)), V.W(36.0, 32.0, H(35.0))]
for i in range(4):
    j = (i + 1) % 4; poly(bm_for(T, "stone"), [lo[i], lo[j], hi[j], hi[i]])
poly(bm_for(T, "stone"), hi)
Fh, Lh = V.frame(36.0, 0.0, 72.0, 0.0, inside=(54, 10))
poly(bm_for(T, "glass"), [Fh.p(4.0, H(18.6), 0.04), Fh.p(30.0, H(18.6), 0.04), Fh.p(30.0, H(20.4), 0.04), Fh.p(4.0, H(20.4), 0.04)])   # the band window
pbox(bm_for(T, "stone"), Fh, 3.6, 30.4, H(17.6), H(18.6), 0, 0.6)                                # its sill-shelf (a deep slab)
for u in (3.0, 9.0):
    poly(bm_for(T, "glass"), [Fh.p(u, H(27.0), 0.04), Fh.p(u + 2.6, H(27.0), 0.04), Fh.p(u + 2.6, H(28.6), 0.04), Fh.p(u, H(28.6), 0.04)])
pbox(bm_for(T, "sign"), Fh, 28.4, 35.4, H(24.0), H(31.4), 0, 0.15)                               # the name at the top corner
for k in range(4):
    pbox(bm_for(T, "stone"), Fh, 29.2, 34.6, H(29.8) - k * 1.6, H(30.4) - k * 1.6, 0, 0.18)
# the foyer: glass between white piers with the red letters MAGGIO, under the block and along the base
for (a0, a1) in ((20.0, 72.0), (72.0, 104.0)):
    Ff, Lf = V.frame(a0, -0.05, a1, -0.05, inside=(54, 10))
    glass_wall(T, Ff, 0.5, Lf - 0.5, G, H(6.4), max(2, int(Lf / 3.0)), rows=2, glass="glass", frame="steel")
    pbox(bm_for(T, "stone"), Ff, 0, Lf, H(6.4), H(7.2), 0, 0.3)
for i, u in enumerate((24.0, 34.0, 44.0, 54.0, 64.0, 74.0)):                                     # the piers and their letters
    Fp = Frame(V.W(u, -0.3), S.TA, -S.NO)
    pbox(bm_for(T, "stone"), Fp, -1.0, 1.0, G, H(6.4), 0, 0.6)
    pbox(bm_for(T, "red"), Fp, -0.7, 0.7, H(4.2), H(5.8), 0, 0.65)
# ------------------------------------------------------------------ the fly tower in dark glazed terracotta
FT = V.rect(40.0, 70.0, 32.0, 66.0)
V.prism(T, "cotto_g", FT, G - 0.3, H(38.5), top_mat="steel")
for F, L, p0, p1 in V.edges(FT):
    v = H(15.0)
    while v < H(38.0):
        pbox(bm_for(T, "cotto_l"), F, 0.0, L, v, v + 0.12, 0, 0.08); v += 0.9
    pbox(bm_for(T, "steel"), F, -0.1, L + 0.1, H(38.0), H(38.6), 0, 0.15)
# ------------------------------------------------------------------ the middle and rear blocks round the courtyard
V.prism(T, "stone", V.rect(36.0, 72.0, 66.0, 92.0), G - 0.3, H(15.0), top_mat="paving")
REAR = [(36.0, 92.0), (94.0, 92.3), (94.0, 120.0), (110.6, 120.0), (110.6, 128.5), (36.0, 131.9)]   # round the courtyard
V.prism(T, "stone", REAR, G - 0.3, H(13.0), top_mat="paving")
V.prism(T, "stone", [(110.6, 92.6), (136.5, 92.6), (136.5, 126.7), (110.6, 128.5)], G - 0.3, H(5.5), top_mat="paving")
for F, L, p0, p1 in V.edges(V.rect(36.0, 94.0, 92.0, 131.0)):
    if L > 40 and p0[1] > 125: slit_windows(F, L, ((H(3.0), H(4.6)), (H(8.0), H(9.4))))
# ------------------------------------------------------------------ the inclined base: two arms falling to the ground
wedge(T, "stone", 72.0, 166.0, 0.0, 18.6, H(14.0), G + 0.3)
wedge(T, "stone", 72.0, 165.0, 65.0, 86.0, H(14.0), G + 0.4)
wedge(T, "stone", 72.0, 136.5, 86.0, 92.6, H(14.0), H(6.0))
for o in (0.0, 18.6, 65.0, 86.0):                                  # glass rails along their edges
    a1 = 166.0 if o < 30 else 165.0
    for k in range(int((a1 - 72.0) / 3.0)):
        a = 72.0 + k * 3.0; h = H(14.0) + (G + 0.3 - H(14.0)) * (a - 72.0) / (a1 - 72.0)
        pbox(bm_for(T, "steel"), Frame(V.W(a, o), S.TA, S.NO), 0, 0.08, h, h + 1.1, -0.04, 0.04)
# ------------------------------------------------------------------ the cavea: seats rising east from the fly tower's stage
N = 46; A0C, A1C = 74.0, 134.0
V.prism(T, "paving", V.rect(70.0, A0C, 18.6, 65.0), G - 0.3, H(14.6))                           # the open-air stage
for i in range(N):
    a = A0C + (A1C - A0C) * i / N; h = H(15.2) + (H(25.6) - H(15.2)) * i / (N - 1)
    V.prism(T, "seat", V.rect(a, a + (A1C - A0C) / N, 18.6, 65.0), G - 0.3, h, top=True)
V.prism(T, "stone", V.rect(A1C, 136.5, 18.6, 65.0), G - 0.3, H(27.0), top_mat="paving")      # the wall closing it
for o in (18.6, 65.0):                                             # its side walls rise with the seats
    F, L = V.frame(A0C, o, A1C, o, inside=(100, 40))
    poly(bm_for(T, "stone"), [F.p(0, H(15.2), 0.05), F.p(L, H(25.6), 0.05), F.p(L, H(26.6), 0.05), F.p(0, H(16.2), 0.05)])
# the square in front: pale paving, lamp posts
V.prism(T, "paving", [(0.0, -40.0), (166.0, -40.0), (166.0, 0.0), (0.0, 0.0)], G - 0.3, G + 0.05)
for a in range(10, 160, 24):
    cylinder(T, "steel", V.W(a, -20.0), 0.12, G, H(9.0), seg=8)
    pbox(bm_for(T, "steel"), Frame(V.W(a, -20.0), S.TA, S.NO), -0.3, 0.3, H(9.0), H(9.8), -0.25, 0.25)
K.export("teatro_maggio")
