"""The sixth circle of walls (1284–1333), its gates and towers, the 16th-century bastions and the Fortezza da Basso:
geometry for blender/scripts/build_mura.py.

Inputs (M14 in docs/DATA-SOURCES.md):
  _dev/data/raw/osm/core_osm.json   OSM: surviving wall stretches (barrier=city_wall), gate and tower footprints
  _dev/data/raw/ohm/core_ohm.json   OpenHistoricalMap: the whole dated circuit (also the demolished north bank)
  LiDAR 2023 DTM/DSM                ground under every wall sample, today's height of every standing gate and tower
Output: blender/data/walls.json, in scene coordinates (x east, z south, y = elevation − 40 m):
  walls:  [{id, pts: [[x, z, ground, top?], …], from, to, kind, conf, src}]   top = wall height above ground (DSM) where it stands
  gates:  [{key, name, c: [x, z], ground, L, W, ang, h_now, foot}]             oriented box of the OSM footprint
  polys:  [{id, kind, from, to, pts: [[x, z, ground], …]}]                     bastions and the Fortezza outline
"""
import os, sys, json, math
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from common import ROOT, SRC, ORIGIN, BASE_Z, T_WGS_UTM, load_grid, Grid

osm = {(e["type"], e["id"]): e for e in json.load(open(os.path.join(SRC, "data", "raw", "osm", "core_osm.json"), encoding="utf-8"))["elements"]}
ohm = {(e["type"], e["id"]): e for e in json.load(open(os.path.join(SRC, "data", "raw", "ohm", "core_ohm.json"), encoding="utf-8"))["elements"]}
print("loading LiDAR…")
DTM = load_grid("dtm"); DTM = np.where(np.isnan(DTM), np.nanmedian(DTM), DTM)
DSM = load_grid("dsm"); DSM = np.where(np.isnan(DSM), DTM, DSM)
dtm, dsm = Grid(DTM, 0.5), Grid(DSM, 0.5)

def utm(p): return T_WGS_UTM.transform(p["lon"], p["lat"])
def sc(e, n): return [round(e - ORIGIN[0], 2), round(-(n - ORIGIN[1]), 2)]
def way(src, i): return [utm(p) for p in src[("way", i)]["geometry"]]
# Ground = the app's own terrain mesh (web/public/data/terrain.f32, step 21), bilinear like makeHeight() in the app, so
# the walls stand exactly on the surface that is drawn (the 0.5 m DTM differs from it by up to ±4 m on steep slopes).
_m = json.load(open(os.path.join(ROOT, "web", "public", "data", "meta.json")))["terrain"]; _n, _st = _m["n"], _m["step"]
_T = np.fromfile(os.path.join(ROOT, "web", "public", "data", "terrain.f32"), dtype=np.float32).reshape(_n, _n); _half = (_n - 1) * _st / 2
def g(e, n):
    x, z = e - ORIGIN[0], -(n - ORIGIN[1]); fx, fz = (x + _half) / _st, (z + _half) / _st
    i, j = min(max(int(fx), 0), _n - 2), min(max(int(fz), 0), _n - 2); a, b = fx - i, fz - j
    return float(_T[j, i] * (1 - a) * (1 - b) + _T[j, i + 1] * a * (1 - b) + _T[j + 1, i] * (1 - a) * b + _T[j + 1, i + 1] * a * b)

def densify(P, step=5.0):
    out = [P[0]]
    for a, b in zip(P, P[1:]):
        d = math.dist(a, b); k = max(1, int(d // step))
        out += [(a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k) for i in range(1, k + 1)]
    return out

def wall_top(e, n, nx, ny):
    """Height of a standing wall above the ground beside it: DSM across a 3 m swath, lowest decile (skips trees)."""
    hs = [float(dsm(e + nx * t, n + ny * t)) - float(dtm(e + nx * t * 3, n + ny * t * 3)) for t in (-1.0, -0.5, 0, 0.5, 1.0)]
    return max(hs)

walls = []
def add_wall(id, P, frm, to, kind, conf, src, standing=False):
    P = densify(P); pts = []
    for i, (e, n) in enumerate(P):
        a, b = P[max(0, i - 1)], P[min(len(P) - 1, i + 1)]; dx, dy = b[0] - a[0], b[1] - a[1]; l = math.hypot(dx, dy) or 1
        q = sc(e, n) + [round(g(e, n), 2)]
        if standing: q.append(round(wall_top(e, n, -dy / l, dx / l), 1))
        pts.append(q)
    walls.append({"id": id, "pts": pts, "from": frm, "to": to, "kind": kind, "conf": conf, "src": src})

NOW = 99999
def utm_from_scene(x, z): return (x + ORIGIN[0], -z + ORIGIN[1])
J = lambda a, b: [utm_from_scene(*a), utm_from_scene(*b)]
# North bank: OHM, dated 1284 → demolished by Poggi 1865–70 (gates kept)
add_wall("north", way(ohm, 198777547), 1284, 1868, "wall", "inferred", "OHM way 198777547")
add_wall("north_w", way(ohm, 198777726), 1284, 1868, "wall", "inferred", "OHM way 198777726")
# Oltrarno, west to east. OSM where it stands today, OHM / straight joins where it is gone.
add_wall("rosa_frediano", way(osm, 118932463)[::-1] + way(osm, 118932485)[::-1], 1320, NOW, "wall", "documented",
         "OSM ways 118932463, 118932485", True)
add_wall("frediano_s", J((-1192.9, 165.9), (-1237.4, 327.1)), 1320, 1868, "wall", "conjectural", "join between OSM stretches")
add_wall("verzaia", way(osm, 118821960) + way(osm, 118821962)[1:], 1320, NOW, "wall", "documented", "OSM ways 118821960, 118821962", True)
add_wall("ariosto_gap", way(ohm, 198777727), 1320, 1868, "wall", "inferred", "OHM way 198777727")
add_wall("ariosto_petrarca", way(osm, 30430358), 1320, NOW, "wall", "documented", "OSM way 30430358", True)
add_wall("romana_e", way(osm, 1558637634), 1320, NOW, "wall", "documented", "OSM way 1558637634", True)
add_wall("boboli_s", J((-928.9, 1272.0), (-558.5, 1220.6)), 1320, NOW, "wall", "conjectural", "join between OSM stretches (Boboli)")
add_wall("boboli_s2", way(osm, 119943564), 1320, NOW, "wall", "documented", "OSM way 119943564", True)
add_wall("belvedere_old", way(ohm, 198777574)[::-1], 1320, 1590, "wall", "inferred", "OHM way 198777574 (replaced by the Forte di Belvedere)")
add_wall("giorgio_niccolo", way(osm, 140235977) + way(osm, 690890820)[::-1][1:], 1320, NOW, "wall", "documented", "OSM ways 140235977, 690890820", True)
add_wall("niccolo_arno", J((749.1, 833.2), (797.0, 800.5)) + [utm_from_scene(803.0, 783.0), utm_from_scene(806.0, 725.0)], 1320, 1870, "wall", "conjectural", "down to the river (Piazza Poggi, 1870s)")

# The earlier circles (OHM): Roman Florentia, Carolingian, Matildine, the first communal circle and its 1260 extension.
# Drawn by the model like the sixth circle, following the ground sample by sample (the city records of these lines stood
# on one ground height each and sank into the slopes of Oltrarno).
EARLY = {198777552: 7.0, 198777553: 7.0, 198777555: 7.0, 198777556: 7.0,              # Roman (OHM "0015")
         198777554: 7.0,                                                               # Carolingian
         198777557: 9.0, 198777558: 9.0, 198777559: 9.0, 198777560: 9.0,               # Matildine
         198777561: 9.0, 198777562: 9.0, 198777563: 9.0, 198777572: 9.0, 198777573: 9.0,   # first communal circle
         198777571: 9.0}                                                               # its 1260 extension
for i, h in EARLY.items():
    t = ohm[("way", i)]["tags"]; fr = int(t["start_date"][:4]); to = int(t["end_date"][:4])
    if fr == 15: fr = -30                                                              # the colony's foundation, as the Roman records
    add_wall(f"early_{i}", way(ohm, i), fr, to, "early", "inferred", f"OHM way {i} ({t.get('name') or 'Roman walls'})")
    walls[-1]["h"] = h

# Gates and towers: OSM footprints, oriented box (PCA), today's height from the DSM.
GATES = [  # key, name (as the city record), OSM way id or None, fallback centre (scene), demolished/absorbed
    ("romana", "Porta Romana", 167972690), ("frediano", "Porta San Frediano", 118932420),
    ("croce", "Porta alla Croce", 72905107), ("prato", "Porta al Prato", 72915039), ("gallo", "Porta San Gallo", 72905103),
    ("niccolo", "Torre San Niccolò", 72915036), ("giorgio", "Porta San Giorgio", 707346991), ("zecca", "Torre della Zecca", 72905106),
    ("serpe", "Torre della Serpe", 72915046), ("rosa", "Torrino di Santa Rosa", 119009554), ("faenza", "Porta a Faenza", 866278404),
    ("arco", "Arco di Trionfo", 72905104), ("verzaia", "Torre della Verzaia", 464120152),
]
gates = []
for key, name, wid in GATES:
    P = np.array(way(osm, wid)[:-1]); c = P.mean(0); d = P - c
    w, v = np.linalg.eigh(d.T @ d); ax = v[:, 1]; ang = math.atan2(ax[1], ax[0])   # long axis, angle from east (UTM, CCW)
    u = d @ ax; t = d @ np.array([-ax[1], ax[0]])
    L, W = float(u.max() - u.min()), float(t.max() - t.min()); c = c + ax * (u.max() + u.min()) / 2 + np.array([-ax[1], ax[0]]) * (t.max() + t.min()) / 2
    gr = g(*c)
    xs = np.linspace(-L / 2 + 1, L / 2 - 1, 7); ys = np.linspace(-W / 2 + 1, W / 2 - 1, 7)
    top = max(float(dsm(*(c + ax * a + np.array([-ax[1], ax[0]]) * b))) for a in xs for b in ys) - BASE_Z
    gates.append({"key": key, "name": name, "c": sc(*c), "ground": round(gr, 2), "L": round(L, 1), "W": round(W, 1),
                  "ang": round(ang, 4), "h_now": round(top - gr, 1), "foot": [sc(*p) for p in P], "src": f"OSM way {wid}"})
    print(f"{key:9s} c={gates[-1]['c']} L={L:.1f} W={W:.1f} ang={math.degrees(ang):6.1f} h={top - gr:5.1f} ground={gr:.1f}")
# demolished gates: OHM nodes, size of their surviving sisters
for key, name, x, z in (("pinti", "Porta a Pinti", 969.0, -727.9), ("giustizia", "Porta alla Giustizia", 1095.0, 527.5),
                        ("miniato", "Porta San Miniato", None, None)):
    if x is None:
        e, n = utm(osm[("node", 1536508532)]); x, z = sc(e, n)
    e, n = utm_from_scene(x, z)
    gates.append({"key": key, "name": name, "c": [x, z], "ground": round(g(e, n), 2), "L": 13.0, "W": 11.0, "ang": None, "h_now": 0, "foot": [],
                  "src": "OHM node" if key != "miniato" else "OSM node 1536508532"})

polys = []
for id, src, i, frm, to in (("mongibello", ohm, 198781234, 1531, 1865), ("serpe_b", ohm, 198777577, 1554, 1870),
                            ("trecanti", ohm, 198777575, 1554, 1870), ("sangallo_b", ohm, 198777576, 1554, 1870),
                            ("fortezza", osm, 1489561765, 1534, NOW)):
    P = way(src, i)
    polys.append({"id": id, "from": frm, "to": to, "pts": [sc(*p) + [round(g(*p), 2)] for p in P],
                  "src": ("OHM" if src is ohm else "OSM") + f" way {i}"})

out = os.path.join(ROOT, "blender", "data"); os.makedirs(out, exist_ok=True)
json.dump({"walls": walls, "gates": gates, "polys": polys}, open(os.path.join(out, "walls.json"), "w", encoding="utf-8"), ensure_ascii=False)
print("walls", len(walls), sum(len(w["pts"]) for w in walls), "samples; gates", len(gates), "; polys", len(polys))
for w in walls:
    if len(w["pts"][0]) > 3:
        h = [p[3] for p in w["pts"]]; print(f"  {w['id']:18s} standing wall top: median {np.median(h):.1f}  p25 {np.percentile(h, 25):.1f}  p75 {np.percentile(h, 75):.1f}")
