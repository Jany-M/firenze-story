"""Palazzo Pitti, the Boboli garden and Forte Belvedere: geometry for blender/scripts/build_pitti.py and build_boboli.py.

Inputs (M20 in docs/DATA-SOURCES.md):
  _dev/data/raw/osm/core_osm.json   OSM: Palazzo Pitti (relation 1637338, with its courtyards), Palazzina della Meridiana
                                    (relation 7071160), Anfiteatro (way 473825738), Grotta del Buontalenti (473825750),
                                    Kaffeehaus (267801118), Bacino del Nettuno (relation 2150390), Forte di Belvedere (24879633)
  LiDAR 2023 DSM/DTM (0.5 m)        roof heights of the palace (per 1 m cell in the palace's own frame), heights of the fort
  web/public/data/terrain.f32       ground (the app's own terrain, as for the walls)
Output: blender/data/pitti.json – scene coordinates (x east, z south, y = elevation − 40 m):
  frame: A (south end of the piazza front), d (along the front, to the north), n (towards the piazza)
  grid:  t0, b0, nt, nb, h[nb][nt] (roof, scene y; null = outside or open courtyard), phase key per cell
  features: outlines with ground and DSM tops for the garden pieces and the fort
"""
import os, sys, json, math
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from common import ROOT, SRC, ORIGIN, T_WGS_UTM, load_grid, Grid

el = json.load(open(os.path.join(SRC, "data", "raw", "osm", "core_osm.json"), encoding="utf-8"))["elements"]
ways = {e["id"]: e for e in el if e["type"] == "way"}; rels = {e["id"]: e for e in el if e["type"] == "relation"}
def sc(p): x, y = T_WGS_UTM.transform(p["lon"], p["lat"]); return (round(x - ORIGIN[0], 2), round(-(y - ORIGIN[1]), 2))
def way(i): return [sc(p) for p in ways[i]["geometry"]]
def rel(i):
    out = {"outer": [], "inner": []}
    for m in rels[i]["members"]:
        g = m.get("geometry") or ways[m["ref"]]["geometry"]; out[m["role"]].append([sc(p) for p in g])
    return out
print("loading LiDAR…")
DTM = load_grid("dtm"); DTM = np.where(np.isnan(DTM), np.nanmedian(DTM), DTM)
DSM = load_grid("dsm"); DSM = np.where(np.isnan(DSM), DTM, DSM)
dsm, dtm = Grid(DSM, 0.5), Grid(DTM, 0.5)
def DS(x, z): return float(dsm(ORIGIN[0] + x, ORIGIN[1] - z)) - 40.0
_m = json.load(open(os.path.join(ROOT, "web", "public", "data", "meta.json")))["terrain"]; _n, _st = _m["n"], _m["step"]
_T = np.fromfile(os.path.join(ROOT, "web", "public", "data", "terrain.f32"), dtype=np.float32).reshape(_n, _n); _half = (_n - 1) * _st / 2
def G(x, z):
    fx, fz = (x + _half) / _st, (z + _half) / _st
    i, j = min(max(int(fx), 0), _n - 2), min(max(int(fz), 0), _n - 2); a, b = fx - i, fz - j
    return float(_T[j, i] * (1 - a) * (1 - b) + _T[j, i + 1] * a * (1 - b) + _T[j + 1, i] * (1 - a) * b + _T[j + 1, i + 1] * a * b)
def inside(x, z, P):
    c = False
    for i in range(len(P)):
        (xi, zi), (xj, zj) = P[i], P[i - 1]
        if (zi > z) != (zj > z) and x < (xj - xi) * (z - zi) / (zj - zi) + xi: c = not c
    return c

# palace frame: the piazza front from its south end A to the north end B (OSM), n towards the piazza
A = np.array((-472.1, 784.1)); B = np.array((-327.2, 689.4)); d = (B - A) / np.linalg.norm(B - A); n = np.array((d[1], -d[0]))
if n @ (np.array((-415.0, 689.0)) - A) < 0: n = -n
P = rel(1637338); M = rel(7071160)
outer = P["outer"][0]; inners = P["inner"]; mer_o = M["outer"][0]; mer_i = M["inner"]
t0, t1, b0, b1 = -60, 210, -60, 160                       # t along the front, b into the palace (b < 0: towards the piazza)
nt, nb = t1 - t0, b1 - b0
H = [[None] * nt for _ in range(nb)]; K = [[""] * nt for _ in range(nb)]; GR = [[None] * nt for _ in range(nb)]
ground_front = round(G(*(A + d * 86 + n * 8)), 2)
for j in range(nb):
    b = b0 + j + 0.5
    for i in range(nt):
        t = t0 + i + 0.5
        x, z = A + d * t - n * b
        mer = inside(x, z, mer_o) and not any(inside(x, z, q) for q in mer_i)
        pal = inside(x, z, outer) and not any(inside(x, z, q) for q in inners)
        if not (mer or pal): continue
        hs = sorted(DS(x + ox, z + oz) for ox in (-0.5, 0, 0.5) for oz in (-0.5, 0, 0.5)); h = hs[4]
        g = G(x, z)
        if h < g + 3.0: continue                             # open court / terrace
        H[j][i] = round(h, 1); GR[j][i] = round(g, 2)
        K[j][i] = "mer" if mer else "pal"
Hs = [row[:] for row in H]
for j in range(nb):
    for i in range(nt):
        if H[j][i] is None: continue
        v = sorted(H[jj][ii] for jj in range(max(0, j - 3), min(nb, j + 4)) for ii in range(max(0, i - 3), min(nt, i + 4)) if H[jj][ii] is not None and K[jj][ii] == K[j][i])
        Hs[j][i] = v[len(v) // 2]
H = Hs
out = {"frame": {"A": A.round(3).tolist(), "d": d.round(5).tolist(), "n": n.round(5).tolist(), "ground_front": ground_front},
       "grid": {"t0": t0, "b0": b0, "nt": nt, "nb": nb, "h": H, "g": GR, "k": K},
       "outline": outer, "inners": inners, "meridiana": mer_o}
# garden pieces and the fort
def feat(pts, top=True):
    g = [round(G(x, z), 2) for x, z in pts]
    f = {"pts": [list(p) for p in pts], "ground": g}
    if top:
        cx, cz = np.mean(pts, axis=0); f["top_dsm"] = round(float(np.median([DS(cx + ox, cz + oz) for ox in range(-3, 4) for oz in range(-3, 4)])), 2)
    return f
out["anfiteatro"] = feat(way(473825738), top=False)
out["grotta"] = feat(way(473825750))
out["kaffeehaus"] = feat(way(267801118))
nb_ = rel(2150390); out["nettuno"] = {**feat(nb_["outer"][0], top=False), "isle": nb_["inner"][0]}
fort = way(24879633)
out["forte"] = feat(fort, top=False)
# wall top along the fort outline (DSM a little inside, the parapet) and the palazzina in the middle
fc = np.mean(fort[:-1], axis=0)
tops = []
for x, z in fort:
    v = np.array((x, z)) - fc; v = v / (np.linalg.norm(v) or 1)
    tops.append(round(max(DS(x - v[0] * o, z - v[1] * o) for o in (1.0, 2.0, 3.0)), 2))
out["forte"]["top"] = tops
# the app's ground 3 m inside and 4 m outside every vertex: the parapet stands above the one, the scarp starts below the other
gin, gout = [], []
for x, z in fort:
    v = np.array((x, z)) - fc; v = v / (np.linalg.norm(v) or 1)
    gin.append(round(max(G(x - v[0] * o, z - v[1] * o) for o in (1.5, 3.0, 5.0)), 2)); gout.append(round(min(G(x + v[0] * o, z + v[1] * o) for o in (2.0, 4.0, 8.0)), 2))
out["forte"]["ground_in"] = gin; out["forte"]["ground_out"] = gout
out["forte"]["centre"] = fc.round(2).tolist()
# amphitheatre: the app's ground along arcs round the obelisk (the tiers follow it), r = 18…44 m
OB = (-315.0, 868.0); P_ = way(473825738)
mx, mz = (P_[0][0] + P_[3][0]) / 2, (P_[0][1] + P_[3][1]) / 2; ax, az = mx - OB[0], mz - OB[1]; base = math.atan2(-az, -ax)
out["anfiteatro"]["profile"] = [[r, round(float(np.median([G(OB[0] + r * math.cos(base + math.radians(a)), OB[1] + r * math.sin(base + math.radians(a))) for a in range(-90, 91, 10)])), 2)] for r in range(16, 46)]
PZ = (-89.9, 992.9)
out["palazzina_ground"] = [round(G(PZ[0] + dx, PZ[1] + dz), 2) for dx in (-13, 0, 13) for dz in (-10, 0, 10)]
out["courtyard_ground"] = round(float(np.median([G(x, z) for x, z in max(inners, key=len)])), 2)
out["front_ground"] = [[t, round(G(*(A + d * t + n * 1.5)), 2)] for t in range(-14, 190, 4)]                     # the Belvedere palazzina inside the fort (OSM building)
# the app's ground round the piazza and the two rondò terraces (1 m in the palace frame): the retaining walls of the
# terraces and the piazza's slope are drawn on it
out["ground"] = {"t0": -40, "b0": -100, "nt": 271, "nb": 111,
                 "h": [[round(G(*(A + d * t - n * b)), 2) for t in range(-40, 231)] for b in range(-100, 11)]}
dst = os.path.join(ROOT, "blender", "data", "pitti.json"); json.dump(out, open(dst, "w", newline="\n")); print("→", dst, "ground front", ground_front)
