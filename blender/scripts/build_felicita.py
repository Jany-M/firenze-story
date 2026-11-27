"""Chiesa di Santa Felicita, its bell tower, the former nunnery and the column in the piazza (v1).

Run:  python pipeline/45_chiese.py   (once: outlines, ground, DSM raster → blender/data/chiese.json)
      blender -b --python blender/scripts/build_felicita.py  →  web/public/models/landmarks/felicita.glb
Frame: a along the front from its north corner (OSM way 159394659, the corners on the Vasari Corridor's centre line, the
frame 2 m behind it), o inwards along the church's axis.
Measured (LiDAR 2023 DSM, ground 9.05 m scene): the nave a 0–16.5 to o 42, eaves ≈19.8 and ridge ≈23 above the piazza (a low
roof); behind the choir, on the axis's left, a square tower a 3–9, o 43–49 ≈6.5 m wide with its top ≈33; the block with
the canonica on the left (a −20…0, o 30–66) ≈20–25 m; the nunnery's wings on the right ≈10–19 m.
Details from photographs (docs/materials): the flank in ochre plaster with tall round-headed windows and a low tiled roof;
the bell tower in bare stone with tall arched openings at the top and a low roof (Sailko 2013, from Palazzo
Franceschi-Dragomanni). The front stands behind the corridor's portico; above the corridor it is plastered, with two
round windows (Ferdinando Ruggieri's front of 1736–39).
Dates (docs/landmarks/SANTA-FELICITA.md): the church rebuilt in the 11th century and again in Gothic form (the medieval
church shown 1000–1739, size *inferred*); Ruggieri's rebuilding 1736–39; the bell tower from 1300 (*inferred*); the
nunnery suppressed 1808–10 (its buildings shown from 1300, *inferred*); the column late 14th century (shown from 1400), with
the terracotta St Peter Martyr of 1484 that fell in 1723 and Montauti's statue that replaced it, taken down in the
19th century (shown to 1850, *inferred*).
"""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from mathutils import Vector
from landmark_detail import *
from landmark_church import Site, slab, extra_materials, figure
K.reset()
MAT["plaster"] = material("plaster_ochre_sf", None, (0.9, 0.76, 0.5), 0.9)
MAT["rough"] = material("rubble_stone", "pietra_forte", (0.6, 0.5, 0.38), 0.9, 0.5, tint=(2.6, 2.4, 2.1))
MAT["forte"] = material("pietra_forte", "pietra_forte", (0.62, 0.5, 0.36), 0.85, 0.32, tint=(3.0, 2.85, 2.55))
MAT["serena"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)
MAT["granite"] = material("grey_granite", None, (0.55, 0.54, 0.52), 0.6)
MAT["terracotta"] = material("glazed_terracotta", None, (0.85, 0.86, 0.88), 0.4)
MAT["iron"] = material("wrought_iron", None, (0.08, 0.08, 0.08), 0.6, metal=0.6)
extra_materials()
MAT["conv"] = material("plaster_convent", None, (0.9, 0.82, 0.62), 0.9)
NOW = K.NOW
S = Site("felicita"); G = S.G; L = S.L
F = S.front()
NAVE_END = 42.0; EAVE, RIDGE = G + 19.8, G + 23.0
TW = (6.0, 46.0, 6.4)                                       # bell tower: a, o, side
B = f"chiesa@1739-{NOW}"

def face_a(a, o0, o1, out):
    return (Frame(S.W(a, o1), -S.NO, -S.TA), o1 - o0) if out < 0 else (Frame(S.W(a, o0), S.NO, S.TA), o1 - o0)
def face_o(o, a0, a1, out):
    return (Frame(S.W(a0, o), S.TA, -S.NO), a1 - a0) if out < 0 else (Frame(S.W(a1, o), -S.TA, S.NO), a1 - a0)
def tall_window(part, Fr, u, sill, h, w=1.4):
    r = w / 2; spring = sill + h - r
    arch_fill(part, "glass", Fr, u - r, u + r, sill, spring, n=0.03)
    ring(part, "serena", Fr, u, spring, r, r + 0.22, 0, 0.1, seg=10, soffit=False)
    for s_ in (-1, 1): pbox(bm_for(part, "serena"), Fr, u + s_ * (r + 0.11) - 0.11, u + s_ * (r + 0.11) + 0.11, sill, spring, 0, 0.1)
    pbox(bm_for(part, "serena"), Fr, u - r - 0.3, u + r + 0.3, sill - 0.18, sill, 0, 0.16)

# ---------------------------------------------------------------- the medieval church (to 1739; its size *inferred*)
S.hall("chiesa_medievale@1000-1739", 0.3, 16.2, 0.0, NAVE_END - 2.0, G - 0.5, G + 16.5, G + 21.0, mat="rough", gables=(True, True))

# ---------------------------------------------------------------- Ruggieri's church (1736–39)
S.hall(B, 0.0, L, 0.0, NAVE_END, G - 0.5, EAVE, RIDGE, mat="plaster", gables=(False, True))
for a, out in ((0.0, -1), (L, 1)):
    Fr, Lf = face_a(a, 0.0, NAVE_END, out)
    pbox(bm_for(B, "serena"), Fr, -0.1, Lf + 0.1, EAVE - 0.6, EAVE, 0, 0.35)
    for k in range(4): tall_window(B, Fr, Lf * (0.16 + 0.22 * k), G + 12.6, 5.0)
Fr, Lf = face_o(NAVE_END, 0.0, L, 1)
pbox(bm_for(B, "serena"), Fr, -0.1, Lf + 0.1, EAVE - 0.6, EAVE, 0, 0.35)
oculus(B, Fr, Lf / 2, EAVE + 1.3, 0.6, frame="serena", fill="dark", fw=0.15)
# the front above the corridor: plaster between pietra serena pilasters, a pediment, two round windows
APEX = RIDGE + 0.5
slab(B, "plaster", F, [(0, G - 0.5), (L, G - 0.5), (L, EAVE), (L / 2, APEX), (0, EAVE)], -1.0, 0.0)
for (u0, u1) in ((0, 0.9), (L - 0.9, L)): pbox(bm_for(B, "serena"), F, u0, u1, G + 10.9, EAVE - 0.6, 0, 0.15)
pbox(bm_for(B, "serena"), F, -0.2, L + 0.2, EAVE - 0.6, EAVE, 0, 0.45)
bm = bm_for(B, "serena")
for (u0, v0), (u1, v1) in (((-0.2, EAVE), (L / 2, APEX + 0.15)), ((L / 2, APEX + 0.15), (L + 0.2, EAVE))):
    poly(bm, [F.p(u0, v0, 0.02), F.p(u1, v1, 0.02), F.p(u1, v1 + 0.35, 0.4), F.p(u0, v0 + 0.35, 0.4)])
for u in (L * 0.3, L * 0.7): oculus(B, F, u, G + 15.6, 0.95, frame="serena", fill="glass", fw=0.3)
pbox(bm_for(B, "serena"), F, -0.1, L + 0.1, G + 12.6, G + 12.9, 0, 0.2)        # a string course over the corridor's roof
cross(B, F.p(L / 2, APEX + 0.3, -0.5), 1.3)

# ---------------------------------------------------------------- the bell tower: bare stone, arched openings, a low roof
T = f"campanile@1300-{NOW}"; ta, to, ts = TW; h = ts / 2
Fb = Frame(S.W(ta - h, to - h), S.TA, S.NO)
box(bm_for(T, "forte"), Fb, 0, ts, G - 0.5, G + 31.0, 0, ts)
faces = [(Frame(o_, u_, n_), ts) for (o_, u_, n_) in ((S.W(ta - h, to - h), S.TA, -S.NO), (S.W(ta + h, to - h), S.NO, S.TA), (S.W(ta + h, to + h), -S.TA, S.NO), (S.W(ta - h, to + h), -S.NO, -S.TA))]
for Fr, Lf in faces:
    for u in (Lf * 0.3, Lf * 0.7):
        arch_fill(T, "dark", Fr, u - 0.55, u + 0.55, G + 26.6, G + 29.4, n=0.03)
        ring(T, "forte", Fr, u, G + 29.4, 0.55, 0.8, 0, 0.1, seg=10, soffit=False)
    pbox(bm_for(T, "forte"), Fr, -0.15, Lf + 0.15, G + 30.6, G + 31.0, 0, 0.3)
    pbox(bm_for(T, "forte"), Fr, -0.05, Lf + 0.05, G + 26.2, G + 26.45, 0, 0.12)
rp = [S.W(ta - h - 0.5, to - h - 0.5, G + 31.0), S.W(ta + h + 0.5, to - h - 0.5, G + 31.0), S.W(ta + h + 0.5, to + h + 0.5, G + 31.0), S.W(ta - h - 0.5, to + h + 0.5, G + 31.0)]
for p0, p1 in zip(rp, rp[1:] + rp[:1]): poly(bm_for(T, "roof"), [p0, p1, S.W(ta, to, G + 33.0)])
box(bm_for(T, "iron"), Frame(S.W(ta, to), S.TA, -S.NO), -0.04, 0.04, G + 33.0, G + 34.4, -0.04, 0.04)

# ---------------------------------------------------------------- the column in the piazza (late 14th century)
CL = S.D["square"]["column"]; cg = CL["ground"] + 0.05; cc = Vector((CL["c"][0], -CL["c"][1], 0))
C = f"colonna@1400-{NOW}"
box(bm_for(C, "serena"), Frame(cc - Vector((0.8, 0.8, 0)), Vector((1, 0, 0)), Vector((0, 1, 0))), 0, 1.6, cg, cg + 1.0, 0, 1.6)
cylinder(C, "serena", cc, 0.42, cg + 1.0, cg + 1.35, seg=12)
cylinder(C, "granite", cc, 0.3, cg + 1.35, cg + 6.6, seg=12)
cone(C, "marble", cc, 0.32, 0.5, cg + 6.6, cg + 7.2, seg=12)                       # the Corinthian capital
box(bm_for(C, "marble"), Frame(cc - Vector((0.55, 0.55, 0)), Vector((1, 0, 0)), Vector((0, 1, 0))), 0, 1.1, cg + 7.2, cg + 7.45, 0, 1.1)
Fc = Frame(cc, Vector((1, 0, 0)), Vector((0, -1, 0)))
figure("statua_san_pietro@1484-1723", Fc, 0, cg + 7.45, 1.2, n=0.0, mat="terracotta")
figure("statua_montauti@1723-1850", Fc, 0, cg + 7.45, 1.4, n=0.0, mat="marble")

# ---------------------------------------------------------------- everything else from the DSM (the canonica, the nunnery)
COR = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "corridoio.json"), encoding="utf-8"))["oltrarno"]
cpts = COR["pts"]; cw = COR["width"]
def near_corridor(a, o):
    x = S.A[0] + S.t[0] * a + S.n[0] * o; z = S.A[1] + S.t[1] * a + S.n[1] * o
    for i in range(len(cpts) - 1):
        (x0, z0), (x1, z1) = cpts[i], cpts[i + 1]
        dx, dz = x1 - x0, z1 - z0; l2 = dx * dx + dz * dz or 1e-9
        tt = max(0.0, min(1.0, ((x - x0) * dx + (z - z0) * dz) / l2))
        w = cw[i] if isinstance(cw, list) else cw
        if math.hypot(x - x0 - tt * dx, z - z0 - tt * dz) < w / 2 + 1.2: return True
    return False
def hand(a, o, m=0.3):
    if -m <= a <= L + m and -2.0 <= o <= NAVE_END + m: return True
    return abs(a - TW[0]) <= TW[2] / 2 + m and abs(o - TW[1]) <= TW[2] / 2 + m
def phase(a, o, k):
    if hand(a, o) or near_corridor(a, o): return None
    return {0: ("cappelle", 1739), 1: ("canonica", 1300), 2: ("monastero", 1300)}[k]
def detail(part):
    return {"roof": "hip", "windows": part != "cappelle", "mat": "conv" if part != "cappelle" else "plaster"}
def solid(a, o): return hand(a, o, 0.0)
print("massing", S.raster(phase, detail=detail, solid=solid))
K.export("felicita")
