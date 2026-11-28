"""Piazzale Michelangelo, the Loggia and the Rampe del Poggi (v1), absolute scene coordinates.

Run: blender -b --python blender/scripts/build_piazzale.py  →  web/public/models/landmarks/piazzale.glb
Measured (LiDAR 2023, DTM and DSM sampled every 3–5 m and 0.5–1 m round the monument: _dev/tmp/piazzale_probe*.py, values
in scene height = metres a.s.l. − 40):
- the terrace: 63.0–64.0 m; its north wall drops 7.5 m (west) to 9 m (east) to the paths below, its line from
  (745, 927) to (790, 936.5), (845, 939), a step out to (848, 950) and on to (895, 957.5);
- the monument at (818.5, 976.5): a raised platform ≈ 12 m across, 1.1 m over the terrace; the statue's top in the DSM
  at 71.7 (thin bronze: the scan catches little of it);
- the Loggia: a block x 790..814, z 1069..1083, 9–10 m over its ground (67.5), the terrace before it held by a wall at
  z ≈ 1050 (64.1 → 67.2);
- the Rampe: levels at 8.6 (Piazza Poggi), 13.8, then the bends of Viale Poggi at 21.3 and 30.3 (the Comune's carriageway
  polygons), 34–39 above; retaining walls at z ≈ 808, 829, 853 and 869 between them,
  the upper fountain's recess x 795..820 back to z ≈ 881.
From photographs (Commons; credited on the library page): walls of rusticated pietra forte with balustrades; on the
monument a stepped base ringed by posts and chains, a lower pedestal with red marble panels and the arms of Florence,
four bronze allegories (Day, Night, Dawn, Dusk) reclining on volutes at its corners, an upper pedestal with Cesare
Guasti's inscriptions, the bronze David; the Loggia a neoclassical arcade of three round arches on paired columns under
a balustraded roof terrace; the Rampe's grottoes faced with spugne (tufa), with arches, basins and cascades.
History: Giuseppe Poggi for Florence as capital; the piazzale built 1869 (Wikipedia, italia.it; visittuscany gives works
from 1873, opened 1875); the bronze David (Clemente Papi's cast) set up on 25 June 1873; the Loggia, meant as a museum
of Michelangelo's works, a café-restaurant from 1876 (its building date taken as 1873, *inferred*); the Rampe 1872–76,
their fountains dry for most of the 20th century and running again from 2019.
"""
import os, sys, math, json
import numpy as np, bmesh
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from landmark_detail import *
from landmark_church import Vs, extra_materials
from landmark_figure import figure, lying, recline, DAVID
from mathutils import Vector
K.reset()
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WJ = json.load(open(os.path.join(ROOT, "blender", "data", "piazzale_walls.json")))   # walls snapped to the LiDAR (_dev/tmp/wall_snap.py)
DTM = np.load(os.path.join(ROOT, "blender", "data", "piazzale_dtm.npy"))             # LiDAR 2023 DTM, 1 m, x 680.., z 760..
def dtm(x, z):
    fx, fz = x - 680, z - 760; i, j = int(fx), int(fz)
    i = max(0, min(DTM.shape[1] - 2, i)); j = max(0, min(DTM.shape[0] - 2, j)); a, b = fx - i, fz - j
    return float((DTM[j, i] * (1 - a) + DTM[j, i + 1] * a) * (1 - b) + (DTM[j + 1, i] * (1 - a) + DTM[j + 1, i + 1] * a) * b)
EDITS = []                                                            # ground edits: the terrain gives way to the model
MAT["forte"] = material("pietra_forte_poggi", "pietra_forte", (0.72, 0.62, 0.47), 0.9, 0.5)
MAT["fortedk"] = material("pietra_forte_joints", None, (0.55, 0.46, 0.34), 0.9)
MAT["spugne"] = material("spugne_tufa", None, (0.78, 0.76, 0.7), 0.95)
MAT["pinkm"] = material("marble_red_panels", None, (0.78, 0.5, 0.45), 0.5)
MAT["bronzev"] = material("bronze_verdigris", None, (0.25, 0.45, 0.38), 0.45, metal=0.5)
MAT["stucco"] = material("loggia_stucco", None, (0.86, 0.82, 0.72), 0.85)
MAT["asph"] = material("piazzale_asphalt", "asfalto", (0.45, 0.44, 0.42), 0.95, 0.25, tint=(2.5, 2.46, 2.4))
MAT["gravel"] = material("piazzale_gravel", "terra", (0.72, 0.68, 0.6), 1.0, 0.3, tint=(1.25, 1.2, 1.1))
MAT["ghisa"] = material("cast_iron_pietraforte", None, (0.66, 0.58, 0.45), 0.7, metal=0.25)     # the cast-iron balustrade, painted the colour of pietra forte (Comune 2017)
MAT["iron"] = material("cast_iron_lamp", None, (0.2, 0.22, 0.23), 0.5, metal=0.6)
MAT["globe"] = material("lamp_globe", None, (0.95, 0.94, 0.9), 0.3)
MAT["step"] = material("pietra_steps", "lastrico", (0.62, 0.6, 0.56), 0.85, 0.5)
extra_materials()
NOW = K.NOW
PZ, MO, LG, RA = f"piazzale@1869-{NOW}", f"monumento_david@1873-{NOW}", f"loggia@1873-{NOW}", f"rampe@1876-{NOW}"
VW = f"viale_muri@1869-{NOW}"                                           # the Viale's containing walls below the piazzale
GRAVEL, ASPH = "piazzale_ghiaia@1869-1959", f"piazzale_asfalto@1960-{NOW}"

def seg(p0, p1, out):
    """Frame on the segment p0 → p1 (scene x, z): u along it, n horizontal towards the point `out`."""
    a, b = Vs(*p0), Vs(*p1); u = (b - a); L = u.length; u.normalize(); n = Vector((u.y, -u.x, 0))
    if (Vs(*out) - (a + b) / 2).dot(n) < 0: n = -n
    return Frame(a, u, n), L
def rusticated(part, F, L, v0, v1, course=0.6, depth=1.4):
    """A retaining wall: the body into the hill, the face in courses of pietra forte with sunk joints."""
    box(bm_for(part, "forte"), F, 0, L, v0, v1, -depth, 0)
    v = v0 + course
    while v < v1 - 0.2:
        pbox(bm_for(part, "fortedk"), F, 0, L, v - 0.05, v, 0, 0.015); v += course
def balustrade(part, F, L, v, h=1.05, step=0.3, pier=6.0):
    """Poggi's balustrade: a pietra forte base, squat Doric cast-iron balusters and a cast-iron cap rail (Fonderia di
    Follonica, 1865–75), painted the colour of the stone; stone dados at intervals (spacing *inferred*)."""
    b0 = 0.32
    pbox(bm_for(part, "forte"), F, -0.05, L + 0.05, v, v + b0, -0.55, 0.05)
    pbox(bm_for(part, "ghisa"), F, -0.05, L + 0.05, v + h - 0.12, v + h, -0.42, -0.08)
    nb = max(1, int(L / step))
    for k in range(nb):
        c = F.p((k + 0.5) * L / nb, 0, -0.25)
        cone(part, "ghisa", c, 0.08, 0.11, v + b0, v + b0 + 0.18, seg=5)                   # the swelling foot
        cone(part, "ghisa", c, 0.11, 0.07, v + b0 + 0.18, v + h - 0.12, seg=5)             # the tapering shaft up to the rail
        # (5 sides and no separate capital: a third of the faces of the balustrade, which is most of the model's – the
        # tab's memory on small devices, perf note 2026-11-28; the difference does not show at the distances it is seen)
    for kk in range(int(L / pier) + 1):
        u = min(L, kk * pier); pbox(bm_for(part, "forte"), F, u - 0.22, u + 0.22, v, v + h + 0.06, -0.5, 0.0)
def lamp(part, x, z, g):
    """The candelabra on the balustrade line: a lion-paw tripod, a twisted shaft, scrolled arms and four white globes
    (photograph: Otrębski 2015 on Commons). The same lamp is drawn in every year (the older heads are *inferred*)."""
    c = Vs(x, z)
    cone(part, "iron", c, 0.42, 0.22, g, g + 0.6, seg=6)
    cylinder(part, "iron", c, 0.11, g + 0.6, g + 3.6, seg=8)
    for k in range(6): cylinder(part, "iron", c, 0.135, g + 0.9 + k * 0.45, g + 1.05 + k * 0.45, seg=8, cap=False)   # the twist
    cone(part, "iron", c, 0.13, 0.2, g + 3.6, g + 3.9, seg=8)
    for a in range(3):
        t = a * 2 * math.pi / 3 + 0.4; d = Vector((math.cos(t), math.sin(t), 0))
        Fa = Frame(c, d, Vector((-d.y, d.x, 0))); pbox(bm_for(part, "iron"), Fa, 0, 0.62, g + 3.75, g + 3.83, -0.03, 0.03)
        cylinder(part, "iron", c + d * 0.62, 0.03, g + 3.75, g + 4.15, seg=5); sphere(part, "globe", c + d * 0.62 + Vector((0, 0, g + 4.38)), 0.24)
    cylinder(part, "iron", c, 0.05, g + 3.9, g + 4.5, seg=5); sphere(part, "globe", c + Vector((0, 0, g + 4.75)), 0.25)
def grotto(part, F, u, v0, w, h, depth=1.6):
    """A round-headed grotto niche faced with spugne, dark inside."""
    arch_fill(part, "dark", F, u - w / 2, u + w / 2, v0, v0 + h - w / 2, n=0.03)
    ring(part, "spugne", F, u, v0 + h - w / 2, w / 2, w / 2 + 0.5, 0, 0.35, seg=12)
    for s in (-1, 1): pbox(bm_for(part, "spugne"), F, u + s * w / 2 - (0.5 if s < 0 else 0), u + s * w / 2 + (0.5 if s > 0 else 0), v0, v0 + h - w / 2, 0, 0.35)
def basin(part, cx, cz, w, d, g, rim=0.5):
    q = [Vs(cx - w / 2, cz - d / 2, g + rim - 0.1), Vs(cx + w / 2, cz - d / 2, g + rim - 0.1), Vs(cx + w / 2, cz + d / 2, g + rim - 0.1), Vs(cx - w / 2, cz + d / 2, g + rim - 0.1)]
    poly(bm_for(part, "water"), q[::-1])
    for (x0, z0, x1, z1) in ((cx - w / 2, cz - d / 2, cx + w / 2, cz - d / 2 + 0.35), (cx - w / 2, cz + d / 2 - 0.35, cx + w / 2, cz + d / 2),
                             (cx - w / 2, cz - d / 2, cx - w / 2 + 0.35, cz + d / 2), (cx + w / 2 - 0.35, cz - d / 2, cx + w / 2, cz + d / 2)):
        F, L = seg((x0, (z0 + z1) / 2), (x1, (z0 + z1) / 2), (x0, z1 + 5)); box(bm_for(part, "spugne"), F, 0, L, g - 0.2, g + rim, -(z1 - z0) / 2, (z1 - z0) / 2)

# ------------------------------------------------------------------ walls from the LiDAR (snapped lines, _dev/tmp/wall_snap.py)
def med(a, k=2):
    return [sorted(a[max(0, i - k):i + k + 1])[len(a[max(0, i - k):i + k + 1]) // 2] for i in range(len(a))]
def strip(p0, p1, n, a, b):
    """Ground-edit polygon along p0 -> p1, from a to b metres along the normal n (scene x, z)."""
    return [[p0[0] + n[0] * a, p0[1] + n[1] * a], [p1[0] + n[0] * a, p1[1] + n[1] * a], [p1[0] + n[0] * b, p1[1] + n[1] * b], [p0[0] + n[0] * b, p0[1] + n[1] * b]]
def wall_line(name, part, top=None, rail="bal", course=0.6, depth=4.5, upto=None, cut=5.0, fill=3.0, grottoes=(), open_below=0.0, footfn=None, slope=False):
    """A retaining wall along the snapped line `name`: rusticated pietra forte from the foot to the top, a coping, then
    the balustrade (rail="bal"), a plain stone parapet ("parapet", *inferred*) or nothing. The ground in front is cut
    down to the foot and filled up behind to the top. grottoes: (x, width, height) – niches at that x along the wall."""
    w = WJ[name]; P = [p for p in w["pts"] if upto is None or upto(p)]; nx, nz = w["low"]
    tops = med([p[2] for p in P]); feet = med([p[3] for p in P])
    if slope: tops = [sum(tops[max(0, i - 2):i + 3]) / len(tops[max(0, i - 2):i + 3]) for i in range(len(tops))]
    if top is not None: tops = [top] * len(P)
    frames = []
    for i in range(len(P) - 1):
        p0, p1 = (P[i][0], P[i][1]), (P[i + 1][0], P[i + 1][1])
        F, L = seg(p0, p1, ((p0[0] + p1[0]) / 2 + nx * 10, (p0[1] + p1[1]) / 2 + nz * 10))
        t, f = max(tops[i], tops[i + 1]), min(feet[i], feet[i + 1])
        if footfn:                                                     # a ramp runs along the wall's foot here
            ff = [footfn(*q) for q in (p0, p1)]
            if None not in ff: f = min(ff)
        if open_below and min(feet[i], feet[i + 1]) > (top if top is not None else t) - open_below:
            continue                                                   # the ramp reaches the terrace here: no wall, no rail
        if t - f < 0.4: t = f + 0.4
        if slope:                                                      # a wall stepping down a slope: its top follows the ground
            ta, tb = max(tops[i], f + 0.4), max(tops[i + 1], f + 0.4); pcs = max(1, int(L / 0.6))
            for k in range(pcs):
                u0, u1 = L * k / pcs, L * (k + 1) / pcs; tt = ta + (tb - ta) * (k + 0.5) / pcs
                box(bm_for(part, "forte"), F, u0, u1 + 0.01, f - 0.8, tt, -depth, 0)
                pbox(bm_for(part, "forte"), F, u0 - 0.01, u1 + 0.02, tt - 0.3, tt + 0.05, 0, 0.25)
                if rail == "parapet": box(bm_for(part, "forte"), F, u0, u1 + 0.01, tt, tt + 0.85, -0.5, 0.05)
            EDITS.append({"poly": strip(p0, p1, (nx, nz), -3.1, cut), "max": round(f - 0.05, 2)})
            EDITS.append({"poly": strip(p0, p1, (nx, nz), -3.2 - fill, -3.2), "min": round(min(ta, tb) - 0.08, 2)})
            frames.append((F, L, t, f, p0, p1)); continue
        rusticated(part, F, L, f - 0.8, t, course=course, depth=depth)
        pbox(bm_for(part, "forte"), F, -0.15, L + 0.15, t - 0.35, t, 0, 0.3)                   # coping
        if rail == "bal": balustrade(part, F, L, t)
        elif rail == "parapet": box(bm_for(part, "forte"), F, -0.05, L + 0.05, t, t + 0.85, -0.5, 0.05)
        for gx, gw, gh in grottoes:
            lo, hi = sorted((p0[0], p1[0]))
            if lo <= gx < hi: grotto(part, F, abs(gx - p0[0]) / max(1e-6, abs(p1[0] - p0[0])) * L, f, gw, min(gh, t - f - 0.8))
        # the ground is cut to the foot from just behind the face (under the wall's body) to `cut` in front, and filled to
        # the top beyond: the nearest terrain point behind the face (2 m grid) is always cut, so the step between the two falls
        # inside the wall's body (4.5 m deep), never in front of the face
        EDITS.append({"poly": strip(p0, p1, (nx, nz), -3.1, cut), "max": round(f - 0.05, 2)})
        EDITS.append({"poly": strip(p0, p1, (nx, nz), -3.2 - fill, -3.2), "min": round(t - 0.08, 2)})
        frames.append((F, L, t, f, p0, p1))
    return frames

# ------------------------------------------------------------------ the city side: the great rectangle's front, the small rectangle, the two ramps
# Drawn as the geometric shapes they are (Jany's review 5; pipeline/49_piazzale.py "front"): the great rectangle's front wall
# is one straight line F0; in its middle a smaller rectangle stands out towards the city by the ramps' width; off its two
# sides Viale Poggi's two ramps run down along F0, mirror images of each other (Street View 2022, 2024: the balustrade of the
# great rectangle stops where a ramp reaches the terrace, the small rectangle's front carries its own). The ramps' level
# along them is the LiDAR's, the two sides averaged (so they mirror), smoothed and made to fall steadily.
def lerp(a, b, t): return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
GJ = json.load(open(os.path.join(ROOT, "blender", "data", "piazzale_ground.json")))   # pipeline/49_piazzale.py
FR = GJ["front"]; FA, FB = FR["A"], FR["B"]; SA, SB, RWD, RLEN = FR["sa"], FR["sb"], FR["w"], FR["len"]
_fl = math.hypot(FB[0] - FA[0], FB[1] - FA[1]); FD = ((FB[0] - FA[0]) / _fl, (FB[1] - FA[1]) / _fl); NOUT = (FD[1], -FD[0])   # towards the city
def F0(s): return (FA[0] + FD[0] * s, FA[1] + FD[1] * s)
def F1(s): p = F0(s); return (p[0] + NOUT[0] * RWD, p[1] + NOUT[1] * RWD)
TOPL = 63.1                                                           # the terrace's level where a ramp meets it
def _across(s): return float(np.median([dtm(*lerp(F0(s), F1(s), t)) for t in (0.45, 0.6, 0.75, 0.9)]))
RT = [float(t) for t in np.arange(0, RLEN + 0.01, 2.0)]                # stations, metres from a ramp's top
_raw = [(_across(SA - t) + _across(SB + t)) / 2 for t in RT]
RL = []; prev = TOPL
for i, t in enumerate(RT):
    sm = _raw[max(0, i - 2):i + 3]; v = min(sum(sm) / len(sm), prev, TOPL)
    if t < 12: v = max(v, TOPL - 0.2 * t)                             # no step where it leaves the terrace: at most 1 in 5
    RL.append(v); prev = v
RL = [RL[0]] + [(RL[i - 1] + RL[i] + RL[i + 1]) / 3 for i in range(1, len(RL) - 1)] + [RL[-1]]
def ramp_level(t): return float(np.interp(t, RT, RL))
def ramp_of(sign):
    """sign -1: the west ramp (s = SA - t), +1: the east one (s = SB + t); stations from the top."""
    ss = [(SA - t) if sign < 0 else (SB + t) for t in RT]
    # the last 10 m come down onto this side's own ground (the shared profile is the two sides' mean): no step at the foot
    own = [_across(s) for s in ss]; L = []
    for t, l, o in zip(RT, RL, own):
        w = max(0.0, min(1.0, (t - (RLEN - 10)) / 10)); L.append(l + w * (o - l))
    return {"xs": RT, "I": [F0(s) for s in ss], "O": [F1(s) for s in ss], "L": L, "HI": L[:], "top_first": True}
RW, RE = ramp_of(-1), ramp_of(1)
def _low(x, z): return min(dtm(x + NOUT[0] * k, z + NOUT[1] * k) for k in (1.5, 2.5, 3.5))
# the walls of the city side as lines with [x, z, top, foot] points, the low side towards the city
_s_w0 = SA - RLEN
_west = [p for p in WJ["north_w"]["pts"] if p[0] < F0(_s_w0)[0] - 1.0]           # the great rectangle's west end, as measured
WJ["front_w"] = {"low": list(NOUT), "pts": _west + [[*F0(s), 63.2, ramp_level(SA - s)] for s in np.arange(_s_w0, SA + 0.01, 3.0)]}
_e = [float(s) for s in np.arange(SB, _fl + 0.01, 3.0)] + [_fl]
WJ["front_e"] = {"low": list(NOUT), "pts": [[*F0(s), 63.2, ramp_level(s - SB) if s - SB <= RLEN else _low(*F0(s))] for s in _e] + [[901.8, 959.1, 62.4, 55.0]]}
WJ["front_s"] = {"low": list(NOUT), "pts": [[*F1(s), 63.2, _low(*F1(s))] for s in list(np.arange(SA, SB, 3.0)) + [SB]]}
print("ramp levels", [round(v, 1) for v in RL])

# ------------------------------------------------------------------ the terrace: walls on the city side, the Iris side, the west
TOP = 63.2
wall_line("front_w", PZ, top=TOP, open_below=1.3)   # the ramps run at the great rectangle's wall's foot: it opens where they
wall_line("front_e", PZ, top=TOP, open_below=1.3)   # reach the terrace's level (the balustrade stops there)
wall_line("front_s", PZ, top=TOP)                    # the small rectangle's front, with its own balustrade
wall_line("east", PZ)
WJ["west_n"]["pts"].append([736.6, 955.3, 63.3, 57.6])            # carried on to the staircase's corner: no open slot down to the lower terrace
wall_line("west_n", PZ, top=63.3)
wall_line("west_s", PZ, upto=lambda p: p[1] < 1004)
# the containing walls below, along Viale Poggi's bends and on the Iris garden side (built with the Viale, 1865–76)
for nm in ("viale_low", "viale_w1", "viale_w2", "iris"): wall_line(nm, VW, rail="parapet", slope=True)

# ------------------------------------------------------------------ the great staircase on the city side (west end)
# 40 steps (OSM way 233265212) from the terrace (63.4) down to the lower terrace by the Belvedere (57.3), 12 m wide,
# LiDAR: the flight runs x 736.5 -> 720.5 between z 955.5 and 967.5
SX0, SX1, SZ0, SZ1, NST = 736.5, 720.5, 955.5, 967.5, 40
lowg, topg = 57.3, 63.35; rise = (topg - lowg) / NST; run = (SX0 - SX1) / NST
for k in range(NST):
    x_hi = SX0 - k * run; x_lo = x_hi - run; v = topg - (k + 1) * rise
    wbox(bm_for(PZ, "step"), x_lo, x_hi + 0.02, -SZ1, -SZ0, lowg - 0.4, v + rise)          # Blender y = -z
for zz in (SZ0, SZ1):                                               # the side walls, a balustrade stepping down with them
    s_ = -1 if zz == SZ0 else 1
    for k in range(0, NST, 4):
        x_hi = SX0 - k * run; x_lo = max(SX1, x_hi - 4 * run); v = topg - k * rise
        ya, yb = sorted((-(zz + s_ * 0.6), -zz)); wbox(bm_for(PZ, "forte"), x_lo, x_hi, ya, yb, lowg - 0.4, v + 0.2)
        Fb, Lb = seg((x_hi, zz + s_ * 0.3), (x_lo, zz + s_ * 0.3), (x_lo, zz + s_ * 5)); balustrade(PZ, Fb, Lb, v + 0.2, pier=Lb + 1)
for x, z in ((SX0 + 0.8, SZ0 - 0.8), (SX0 + 0.8, SZ1 + 0.8), (SX1 - 0.6, SZ0 - 0.8), (SX1 - 0.6, SZ1 + 0.8)):
    lamp(PZ, x, z, topg if x > 730 else lowg)
EDITS.append({"poly": [[SX1 - 0.5, SZ0 - 0.5], [SX0 + 0.3, SZ0 - 0.5], [SX0 + 0.3, SZ1 + 0.5], [SX1 - 0.5, SZ1 + 0.5]], "max": lowg - 0.1})

# ------------------------------------------------------------------ the terrace's ground: gravel at first, asphalt today
# (gravel in the photographs of the 1870s–1900s, asphalt in those of the 1990s on; the change is dated 1960, *inferred*)
def wl(nm, cond=lambda p: True): return [(p[0], p[1]) for p in WJ[nm]["pts"] if cond(p)]
from mathutils.geometry import tessellate_polygon
def slab(part, mat, outer, holes=(), lift=0.04, cell=4.0, flat=None, hfn=None):
    """A ground slab on the polygon (with holes), cut into 4 m cells and laid on the LiDAR heights (or flat at `flat`)."""
    rings = [list(outer)] + [list(h) for h in holes]
    pts = [Vector((x, -z, 0)) for r in rings for x, z in r]
    tris = tessellate_polygon([[Vector((x, -z, 0)) for x, z in r] for r in rings])
    bt = bmesh.new(); vs = [bt.verts.new(p) for p in pts]
    for a, b, c in tris:
        try: bt.faces.new((vs[a], vs[b], vs[c]))
        except ValueError: pass
    bmesh.ops.remove_doubles(bt, verts=bt.verts[:], dist=0.001)
    xs = [p.x for p in pts]; ys = [p.y for p in pts]
    for x in np.arange(math.floor(min(xs)), max(xs), cell):
        bmesh.ops.bisect_plane(bt, geom=bt.verts[:] + bt.edges[:] + bt.faces[:], plane_co=(x, 0, 0), plane_no=(1, 0, 0))
    for y in np.arange(math.floor(min(ys)), max(ys), cell):
        bmesh.ops.bisect_plane(bt, geom=bt.verts[:] + bt.edges[:] + bt.faces[:], plane_co=(0, y, 0), plane_no=(0, 1, 0))
    bmesh.ops.triangulate(bt, faces=bt.faces[:])
    for v in bt.verts: v.co.z = (flat if flat is not None else (hfn or dtm)(v.co.x, -v.co.y)) + lift
    tb = bm_for(part, mat)
    for f in bt.faces:
        q = [v.co.copy() for v in f.verts]
        if (q[1] - q[0]).cross(q[2] - q[0]).z < 0: q = q[::-1]                       # facing up
        poly(tb, q)
    bt.free()
# the terrace, less the carriageway round its south side (Viale Galileo into Viale Michelangiolo, left to the city's
# streets, so the road runs on unbroken past both ends of the square) and less the monument's platform
# laid on the LiDAR, but never below the level the ramps arrive at (where the old entries dipped the ground towards them):
# the ramps' tops and the paving meet flush
pvh = lambda x, z: max(dtm(x, z), TOPL - 0.01)
pv = GJ["pave"]; slab(GRAVEL, "gravel", pv["outer"], pv["holes"], hfn=pvh); slab(ASPH, "asph", pv["outer"], pv["holes"], hfn=pvh)
EDITS.append({"poly": pv["outer"], "drop": 0.3})
mx, mz, mr = GJ["monument"]                                            # the LiDAR's hump of the platform cut away: the
EDITS.append({"poly": [[mx + mr * math.cos(a), mz + mr * math.sin(a)] for a in np.linspace(0, 2 * math.pi, 20, endpoint=False)], "max": 63.35})   # monument stands on the terrace
# Viale Poggi where it climbs to the terrace along the city side and goes down again on the other side: the two ramps
# (geometry above), gravel, then asphalt like the terrace, on a fill held by a rusticated wall where the bank falls away
def railing(part, F, L, v, h=1.0):
    """An iron railing: posts, a top and a bottom rail, plain bars (*inferred*: the photographs show it only from afar)."""
    for k in range(int(L / 1.8) + 1):
        u = min(L, k * 1.8); pbox(bm_for(part, "iron"), F, u - 0.03, u + 0.03, v, v + h, -0.33, -0.27)
    for v0 in (v + 0.1, v + h - 0.05): pbox(bm_for(part, "iron"), F, 0, L, v0, v0 + 0.05, -0.33, -0.27)
    for k in range(int(L / 0.14)): u = k * 0.14 + 0.07; pbox(bm_for(part, "iron"), F, u - 0.01, u + 0.01, v + 0.1, v + h, -0.31, -0.29)
def build_ramp(R, low, bal_len):
    I, O, HI, L, n = R["I"], R["O"], R["HI"], R["L"], len(R["xs"])
    for i in range(n - 1):
        q = [Vs(*I[i], HI[i] + 0.04), Vs(*O[i], L[i] + 0.04), Vs(*O[i + 1], L[i + 1] + 0.04), Vs(*I[i + 1], HI[i + 1] + 0.04)]   # as the paving
        for tri in ((q[0], q[1], q[2]), (q[0], q[2], q[3])):
            t = list(tri)
            if (t[1] - t[0]).cross(t[2] - t[0]).z < 0: t = t[::-1]
            if (t[1] - t[0]).cross(t[2] - t[0]).length < 1e-6: continue
            poly(bm_for(GRAVEL, "gravel"), t); poly(bm_for(ASPH, "asph"), t)
        lo = min(HI[i], HI[i + 1], L[i], L[i + 1])
        pq = [list(I[i]), list(O[i]), list(O[i + 1]), list(I[i + 1])]
        lift = (HI[i] + HI[i + 1] + L[i] + L[i + 1]) / 4 + 0.05 - (lo - 0.08)   # the ramp's surface over the ground left under it
        EDITS.append({"poly": pq, "min": round(lo - 0.45, 2)}); EDITS.append({"poly": pq, "max": round(lo - 0.08, 2), "lift": round(lift, 2)})
    # the outer side, from the top end down: a balustrade over the first stretch (as on the terrace), then an iron railing;
    # the wall below follows the fall of the bank and gives way to a kerb where the bank is level with the road
    order = list(range(n - 1)) if R["top_first"] else list(range(n - 2, -1, -1)); acc = 0.0
    for i in order:
        a, b = O[i], O[i + 1]; ta, tb = L[i], L[i + 1]
        if math.hypot(b[0] - a[0], b[1] - a[1]) < 0.05: continue
        F, Ls = seg(a, b, ((a[0] + b[0]) / 2 + low[0] * 5, (a[1] + b[1]) / 2 + low[1] * 5))
        ga = min(ta, dtm(a[0] + low[0] * 2, a[1] + low[1] * 2)); gb = min(tb, dtm(b[0] + low[0] * 2, b[1] + low[1] * 2))
        drop = max(ta - ga, tb - gb); pieces = max(1, int(Ls / 0.5))
        for k in range(pieces):                                          # sloping top, in 0.5 m pieces
            u0, u1 = Ls * k / pieces, Ls * (k + 1) / pieces; tt = ta + (tb - ta) * (k + 0.5) / pieces
            if drop > 0.6:
                box(bm_for(VW, "forte"), F, u0, u1 + 0.01, min(ga, gb) - 0.8, tt, -1.4, 0)
                pbox(bm_for(VW, "forte"), F, u0 - 0.01, u1 + 0.02, tt - 0.3, tt + 0.05, 0, 0.12)
            else: box(bm_for(VW, "forte"), F, u0, u1 + 0.01, tt - 0.5, tt + 0.18, -0.3, 0)
        if drop > 0.6:
            EDITS.append({"poly": strip(a, b, low, 0.0, 2.2), "max": round(min(ga, gb) - 0.05, 2)})
        p1 = max(1, int(Ls / 1.5))
        for k in range(p1):
            u0, u1 = Ls * k / p1, Ls * (k + 1) / p1; tt = ta + (tb - ta) * (k + 0.5) / p1
            Fk = Frame(F.p(u0, 0, 0), F.u, F.n)
            if acc + u0 < bal_len: balustrade(VW, Fk, u1 - u0, tt + 0.05, pier=99)
            elif drop > 0.8: railing(VW, Fk, u1 - u0, tt + 0.05)
        acc += Ls
build_ramp(RW, NOUT, 18.0)
build_ramp(RE, NOUT, 18.0)
# the lower terrace by the Belvedere at the foot of the great staircase: stone paving on the LiDAR (the Comune's pedestrian area,
# grey in the orthophoto), so the staircase lands on a floor and not on the bare ground model
LW = GJ["lower"]; slab(PZ, "step", LW["outer"], LW["holes"], lift=0.05)
EDITS.append({"poly": LW["outer"], "drop": 0.3})
# the garden before the Loggia, between the carriageway and the Loggia's terrace wall: gravel paths, lawn beds edged in
# stone, the oval fountain (OSM way 1093617565; photographs: Sailko on Commons, localistorici.it)
isl = GJ["island"]; MAT["path"] = material("garden_gravel", "terra", (0.74, 0.69, 0.6), 1.0, 0.3, tint=(1.3, 1.25, 1.15))
MAT["grass"] = material("garden_lawn", None, (0.2, 0.36, 0.12), 1.0)
slab(LG, "path", isl["outer"], isl["holes"])
EDITS.append({"poly": isl["outer"], "drop": 0.3})
for b in GJ["beds"]:
    slab(LG, "grass", b, lift=0.12)
    for (x0, z0), (x1, z1) in zip(b, b[1:] + b[:1]):                    # the stone edge
        if math.hypot(x1 - x0, z1 - z0) < 0.05: continue
        F, L = seg((x0, z0), (x1, z1), ((x0 + x1) / 2 + 0.01, (z0 + z1) / 2)); g = dtm((x0 + x1) / 2, (z0 + z1) / 2)
        box(bm_for(LG, "marble"), F, 0, L, g - 0.05, g + 0.16, -0.08, 0.08)
FT = GJ["fountain"]; fc = (sum(p[0] for p in FT) / len(FT), sum(p[1] for p in FT) / len(FT)); fg = min(dtm(x, z) for x, z in FT)
slab(LG, "water", FT, lift=0.35, flat=fg)
for (x0, z0), (x1, z1) in zip(FT, FT[1:] + FT[:1]):                     # the basin's rim
    F, L = seg((x0, z0), (x1, z1), fc); box(bm_for(LG, "marble"), F, -0.05, L + 0.05, fg - 0.1, fg + 0.55, -0.45, 0)
cylinder(LG, "marble", Vs(*fc), 0.45, fg, fg + 1.1, seg=12); cone(LG, "marble", Vs(*fc), 0.9, 0.5, fg + 1.1, fg + 1.3, seg=12)   # the jet's base (*inferred* form)
cylinder(LG, "water", Vs(*fc), 0.05, fg + 1.3, fg + 2.2, seg=6)

# lamp posts along the balustrades (every ≈ 24 m, *inferred* spacing; on the line in every photograph)
def along(nm, every, off, g=TOP):
    P = WJ[nm]["pts"]; nx, nz = WJ[nm]["low"]; acc = every / 2
    def ff(x, z):                                                     # the wall's foot by the nearest point
        q = min(P, key=lambda p: (p[0] - x) ** 2 + (p[1] - z) ** 2); return q[3] if nm.startswith("front") else None
    for a, b in zip(P, P[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1]); t = acc
        while t < L:
            x = a[0] + (b[0] - a[0]) * t / L - nx * off; z = a[1] + (b[1] - a[1]) * t / L - nz * off
            fv = ff(x, z)
            if fv is None or fv < TOP - 1.3: lamp(PZ, x, z, g if g is not None else dtm(x, z))   # none over a ramp's opening
            t += every
        acc = t - L
for nm in ("front_w", "front_e", "front_s"): along(nm, 24, 1.0)
along("east", 24, 1.0, None); along("west_n", 24, 1.0)

# ------------------------------------------------------------------ the monument to Michelangelo
C = (818.5, 976.5); G = 63.45                                          # on the terrace's level round it (LiDAR, 8–11 m out)
face = Vector((-0.57, 0.82, 0)).normalized()                        # David faces the city, towards the Duomo (north-west; scene -z is north: +y in Blender)
Fm = Frame(Vs(*C), Vector((-face.y, face.x, 0)), face)
for k, (w, h) in enumerate(((13.0, 0.3), (11.6, 0.6), (10.2, 0.9))):  # three steps
    box(bm_for(MO, "marble"), Fm, -w / 2, w / 2, G - 0.2, G + h, -w / 2, w / 2)
for k in range(12):                                                 # posts and chains round the steps
    t = 2 * math.pi * k / 12; p = Vs(*C) + Vector((math.cos(t), math.sin(t), 0)) * 7.4
    cylinder(MO, "marble", p, 0.25, G - 0.1, G + 1.0, seg=8)
    t2 = 2 * math.pi * (k + 1) / 12; p2 = Vs(*C) + Vector((math.cos(t2), math.sin(t2), 0)) * 7.4
    Fc = Frame(p, (p2 - p).normalized(), Vector((0, 0, 0)) + Vector((-(p2 - p).y, (p2 - p).x, 0)).normalized())
    pbox(bm_for(MO, "iron"), Fc, 0, (p2 - p).length, G + 0.72, G + 0.78, -0.03, 0.03)
B = G + 0.9
box(bm_for(MO, "marble"), Fm, -3.6, 3.6, B, B + 0.5, -3.6, 3.6)                         # plinth
box(bm_for(MO, "marble"), Fm, -3.2, 3.2, B + 0.5, B + 2.6, -3.2, 3.2)                   # the lower pedestal
for s in range(4):                                                  # its red marble panels and the arms
    ang = s * math.pi / 2; d = Vector((math.cos(ang), math.sin(ang), 0)); Fs = Frame(Vs(*C) + d * 3.2, Vector((-d.y, d.x, 0)), d)
    for u in (-2.0, 2.0): pbox(bm_for(MO, "pinkm"), Fs, u - 0.9, u + 0.9, B + 0.9, B + 2.2, 0, 0.04)
    pbox(bm_for(MO, "bronze"), Fs, -0.6, 0.6, B + 1.0, B + 2.1, 0, 0.12)
box(bm_for(MO, "marble"), Fm, -3.5, 3.5, B + 2.6, B + 3.0, -3.5, 3.5)                   # its cornice
# the four Times of Day (bronze copies of Michelangelo's figures for the Medici tombs) reclining on scrolled couches at the
# corners, each along its side with the head towards the corner (landmark_figure.py; which figure at which corner *inferred*)
TIMES = {(-1, -1): ("Night", recline(arm="head"), True), (-1, 1): ("Dawn", recline(arm="rest", knee=0.3), True),
         (1, -1): ("Day", recline(arm="back", head_up=0.33), False), (1, 1): ("Dusk", recline(arm="rest", bend=0.35, knee=0.22), False)}
for (su, sn), (name, pose, fem) in TIMES.items():
    cu, cn = su * 2.4, sn * 2.4
    box(bm_for(MO, "marble"), Fm, min(cu - su * 1.75, cu + su * 0.9), max(cu - su * 1.75, cu + su * 0.9), B + 3.0, B + 3.45, cn - 0.75, cn + 0.75)   # the couch
    sphere(MO, "marble", Fm.p(cu + su * 0.75, B + 3.55, cn), 0.32)                                      # its scroll at the corner end
    lying(MO, "bronzev", Fm.p(cu - su * 0.15, B + 3.45, cn), Fm.u * su, Fm.n * sn, 2.15, pose, female=fem)
box(bm_for(MO, "marble"), Fm, -1.9, 1.9, B + 3.0, B + 5.9, -1.9, 1.9)                   # the upper pedestal (inscriptions)
for s in range(4):
    ang = s * math.pi / 2; d = Vector((math.cos(ang), math.sin(ang), 0)); Fs = Frame(Vs(*C) + d * 1.9, Vector((-d.y, d.x, 0)), d)
    pbox(bm_for(MO, "pinkm"), Fs, -1.1, 1.1, B + 3.7, B + 5.3, 0, 0.03)
box(bm_for(MO, "bronzev"), Fm, -2.1, 2.1, B + 5.9, B + 6.3, -2.1, 2.1)                  # bronze top moulding
D = B + 6.3                                                         # the David, 5.2 m with its rock, weight on the right leg
box(bm_for(MO, "bronzev"), Fm, -0.75, 0.75, D, D + 0.35, -0.55, 0.55)                   # rock and base
figure(MO, "bronzev", Fm.p(0, D + 0.35, 0), face, 4.85, DAVID)                                  # landmark_figure.py
rt = Vector((face.y, -face.x, 0))                                                                  # the tree stump by his right leg
cone(MO, "bronzev", Fm.p(0, 0, 0) + rt * 0.42 - face * 0.28, 0.24, 0.17, D + 0.35, D + 1.75, seg=10)


# ------------------------------------------------------------------ the Rampe: walls on the measured lines, grottoes, basins
def at_x(frames, x):
    """The wall segment over x and the distance along it."""
    for F, L, t, f, p0, p1 in frames:
        lo, hi = sorted((p0[0], p1[0]))
        if lo <= x <= hi: return F, abs(x - p0[0]) / max(1e-6, abs(p1[0] - p0[0])) * L, t, f
    F, L, t, f, p0, p1 = frames[len(frames) // 2]; return F, L / 2, t, f
wall_line("r1", RA, course=0.55, depth=4.5, grottoes=((790, 2.2, 3.8), (800.5, 2.2, 3.8), (811, 2.2, 3.8)))   # the lower fountains, behind the tower
for nm in ("r1e", "r2", "r3e", "r4w", "r4w2", "r6", "r6e", "r7"): wall_line(nm, RA, course=0.55, depth=4.5)
f3 = wall_line("r3", RA, course=0.55, depth=4.5, grottoes=((805, 3.0, 3.8),))                                 # the first level's fountain
F, u, t, f = at_x(f3, 805); basin(RA, 804.8, 828.3, 10, 3.2, f)                                                # OSM way 463430105
f5 = wall_line("r5", RA, course=0.55, depth=4.5)                                                               # the middle level: the great grotto
F3, u3, t5, f5_ = at_x(f5, 807.5)
box(bm_for(RA, "spugne"), F3, u3 - 13, u3 + 13, f5_ - 0.4, t5 + 0.4, 0, 1.6)                                 # the rock-faced front, a curved crest
F3f = Frame(F3.p(0, 0, 1.6), F3.u, F3.n)
for du in (-6.5, 0, 6.5): grotto(RA, F3f, u3 + du, f5_ + 0.2, 4.6, min(6.6, t5 - f5_ - 0.6), depth=2.5)
for du in (-3.25, 3.25): pbox(bm_for(RA, "water"), F3f, u3 + du - 0.6, u3 + du + 0.6, f5_ + 0.5, t5 - 0.6, 0, 0.05)   # the cascades
for k in range(9):
    tt = k / 8; pbox(bm_for(RA, "spugne"), F3, u3 - 13 + tt * 26 - 1.6, u3 - 13 + tt * 26 + 1.6, t5 + 0.4, t5 + 0.4 + 1.6 * math.sin(math.pi * tt) + 0.3, 0, 1.6)
basin(RA, 807.5, 851.0, 38, 3.2, f5_, rim=0.6)                                                                 # OSM way 690889344, the road just below it
f6 = wall_line("r6r", RA, course=0.55, depth=4.5, grottoes=((803.5, 3.2, 4.0),))                               # the upper fountain's recess
F6, u6, t6, f6_ = at_x(f6, 803.5); basin(RA, 803.5, 881.0, 18, 4.0, f6_)

# ------------------------------------------------------------------ the Loggia and the terrace wall below it
GL = 67.5
Ff, Lf = seg((790, 1069), (814, 1069), (802, 1060))                  # its front, towards the piazzale (north)
box(bm_for(LG, "stucco"), Ff, 0, Lf, GL - 0.5, GL + 8.9, -14.0, 0)   # below the cornice's top: the two tops were one plane and flickered
box(bm_for(LG, "forte"), Ff, -0.3, Lf + 0.3, GL + 8.4, GL + 9.0, -14.3, 0.4)            # cornice
for F_, L_ in (seg((790, 1069), (790, 1083), (780, 1076)), seg((814, 1069), (814, 1083), (824, 1076)), seg((790, 1083), (814, 1083), (802, 1095)), (Ff, Lf)):
    balustrade(LG, F_, L_, GL + 9.0, h=0.9)
# the arcade: three round arches between paired columns, the back of the loggia in shade
BAY = Lf / 5
for i in range(1, 4):
    u = BAY * (i + 0.5)
    arch_fill(LG, "dark", Ff, u - BAY / 2 + 0.7, u + BAY / 2 - 0.7, GL + 0.6, GL + 5.6, n=0.02)
    ring(LG, "stucco", Ff, u, GL + 5.6, BAY / 2 - 0.7, BAY / 2 - 0.25, 0, 0.3, seg=12)
for i in range(1, 5):
    for du in (-0.45, 0.45):
        cylinder(LG, "stucco", Ff.p(BAY * i + du, 0, 0.5), 0.26, GL + 0.6, GL + 7.4, seg=10)
    pbox(bm_for(LG, "stucco"), Ff, BAY * i - 0.85, BAY * i + 0.85, GL + 7.4, GL + 7.8, 0, 0.85)
for i in (0, 4):                                                    # the closed end bays with a window
    u = BAY * (i + 0.5); poly(bm_for(LG, "glass" if "glass" in MAT else "dark"), [Ff.p(u - 0.8, GL + 2.5, 0.03), Ff.p(u + 0.8, GL + 2.5, 0.03), Ff.p(u + 0.8, GL + 5.0, 0.03), Ff.p(u - 0.8, GL + 5.0, 0.03)])
pbox(bm_for(LG, "stucco"), Ff, 0, Lf, GL + 7.8, GL + 8.4, 0, 0.6)                       # entablature
box(bm_for(LG, "forte"), Ff, -3.0, Lf + 3.0, GL - 0.6, GL + 0.6, 0, 3.5)                 # its podium and steps
fl = wall_line("loggia", LG)                                         # the balcony wall under the loggia (the epigraph), on its measured line
Fw, uw, tw, fw = at_x(fl, 800)
pbox(bm_for(LG, "marble"), Fw, uw - 3.0, uw + 3.0, fw + 0.8, min(tw - 0.6, fw + 2.4), 0, 0.06)         # the inscription


# ------------------------------------------------------------------ the ground edits for the web terrain
GE = os.path.join(ROOT, "web", "public", "models", "landmarks", "ground_edits.json")
ge = json.load(open(GE)) if os.path.exists(GE) else {}
ge["piazzale"] = EDITS; json.dump(ge, open(GE, "w"), separators=(",", ":"))
print("ground edits", len(EDITS))
K.export("piazzale")
