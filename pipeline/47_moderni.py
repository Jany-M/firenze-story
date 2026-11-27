"""§12 item 7: the Santa Maria Novella station, the Stazione Leopolda, the Synagogue, the Murate, the Teatro del Maggio and the Biblioteca Nazionale – geometry for
blender/scripts/build_<site>.py (the same frame and raster as pipeline/45_chiese.py).

For each site: a frame on the façade (a along the front from its corner A to B, o inwards, 0 = the front line), the OSM
outlines of the complex, the ground along the front, a DSM profile along the main axis and a 1 m DSM raster of the whole
complex in the frame (median of 5 × 5 samples; terrain under each cell) → blender/data/chiese.json.
Inputs (M33+ in docs/DATA-SOURCES.md): OSM (ways and relations listed in SITES), LiDAR 2023 DSM, the app's terrain.
"""
import os, sys, json, math
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from common import ROOT, SRC, ORIGIN, T_WGS_UTM, load_grid, Grid

el = json.load(open(os.path.join(SRC, "data", "raw", "osm", "core_osm.json"), encoding="utf-8"))["elements"]
ways = {e["id"]: e for e in el if e["type"] == "way"}; rels = {e["id"]: e for e in el if e["type"] == "relation"}
def sc(p): x, y = T_WGS_UTM.transform(p["lon"], p["lat"]); return [round(x - ORIGIN[0], 2), round(-(y - ORIGIN[1]), 2)]
def way(i): return [sc(p) for p in ways[i]["geometry"]]
def rel(i):
    out = {"outer": [], "inner": []}
    for m in rels[i]["members"]: out[m["role"]].append([sc(p) for p in (m.get("geometry") or ways[m["ref"]]["geometry"])])
    return out
print("loading LiDAR…")
DTM = load_grid("dtm"); DTM = np.where(np.isnan(DTM), np.nanmedian(DTM), DTM)
DSM = load_grid("dsm"); DSM = np.where(np.isnan(DSM), DTM, DSM)
dsm = Grid(DSM, 0.5)
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
def tops(P, holes=()):
    xs = [p[0] for p in P]; zs = [p[1] for p in P]; v = []
    for x in np.arange(min(xs), max(xs), 1.0):
        for z in np.arange(min(zs), max(zs), 1.0):
            if inside(x, z, P) and not any(inside(x, z, h) for h in holes): v.append(DS(x, z))
    return {"p50": round(float(np.percentile(v, 50)), 2), "p90": round(float(np.percentile(v, 90)), 2)}
def feat(P, holes=()):
    return {"pts": P, "ground": [round(G(x, z), 2) for x, z in P], "holes": list(holes), **tops(P, holes)}


SITES = {
    # Santa Maria Novella station (relation 3324492): the front on Piazza della Stazione, from its west corner
    "smn": {"A": (-636.0, -437.0), "B": (-565.3, -446.0), "ways": [], "rels": [3324492]},
    # Stazione Leopolda (way 269666091): the head towards Porta al Prato
    "leopolda": {"A": (-1382.5, -663.9), "B": (-1405.4, -627.5), "ways": [269666091], "rels": []},
    # the Synagogue (way 102979678): the front towards Via Farini (west)
    "sinagoga": {"A": (879.5, -145.2), "B": (867.4, -125.5), "ways": [102979678], "rels": []},
    # the Murate (relation 1609313): the front on Via Ghibellina (south)
    "murate": {"A": (965.9, 271.8), "B": (1065.1, 296.6), "ways": [], "rels": [1609313]},
    # the Teatro del Maggio Musicale Fiorentino (relation 3609352): its south-west side on Piazza Vittorio Gui, from the
    # west corner
    "teatro": {"A": (-1742.2, -731.1), "B": (-1608.2, -646.3), "ways": [], "rels": [3609352]},
    # the Biblioteca Nazionale Centrale (way 102979687): its front on Piazza dei Cavalleggeri (south), from the west corner
    # by the rotunda on Via Magliabechi to the east corner on Via Tripoli
    "biblioteca": {"A": (514.9, 504.6), "B": (645.0, 529.0), "ways": [102979687], "rels": []},
}
ONLY = sys.argv[1:]                                                  # e.g. `47_moderni.py biblioteca`: redo one site, keep the rest
def outline(kind, i):
    if kind == "way": return way(i), []
    r = rel(i); return r["outer"][0], r["inner"]
dst = os.path.join(ROOT, "blender", "data", "moderni.json")
out = json.load(open(dst)) if ONLY and os.path.exists(dst) else {}
for key, S in SITES.items():
    if ONLY and key not in ONLY: continue
    A, B = np.array(S["A"]), np.array(S["B"]); T = (B - A) / np.linalg.norm(B - A); N = np.array([-T[1], T[0]])
    polys = [outline("way", i) for i in S["ways"]]
    for i in S["rels"]:                                              # every outer ring of a relation (the station has two)
        r = rel(i); polys += [(P, r["inner"]) for P in r["outer"]]
    c = np.mean(np.array(polys[0][0]), axis=0)
    if np.dot(c - A, N) < 0: N = -N
    def XZ(a, o): p = A + T * a + N * o; return float(p[0]), float(p[1])
    polys += [([list(XZ(a, o)) for a, o in P], []) for P in S.get("extra", [])]      # outlines traced in the frame
    AO = [(float(np.dot(np.array(p) - A, T)), float(np.dot(np.array(p) - A, N))) for P, _ in polys for p in P]
    a0, a1 = int(min(a for a, _ in AO)) - 1, int(max(a for a, _ in AO)) + 2
    o0, o1 = int(min(o for _, o in AO)) - 1, int(max(o for _, o in AO)) + 2
    h, g, k = [], [], []
    for o in range(o0, o1):
        hr, gr, kr = [], [], []
        for a in range(a0, a1):
            ac, oc = a + 0.5, o + 0.5; x, z = XZ(ac, oc)
            hit = next((i for i, (P, H) in enumerate(polys) if inside(x, z, P) and not any(inside(x, z, hh) for hh in H)), None)
            if hit is None: hr.append(None); gr.append(None); kr.append(None); continue
            v = float(np.median([DS(*XZ(ac + da, oc + do)) for da in (-1, -0.5, 0, 0.5, 1) for do in (-1, -0.5, 0, 0.5, 1)]))
            hr.append(round(v, 1)); gr.append(round(G(x, z), 2)); kr.append(hit)
        h.append(hr); g.append(gr); k.append(kr)
    L = float(np.linalg.norm(B - A))
    out[key] = {"A": A.tolist(), "t": T.round(6).tolist(), "n": N.round(6).tolist(), "width": round(L, 2),
                "ground_front": round(max(G(*XZ(a, -1.0)) for a in np.arange(0, L + 0.1, 1.0)), 2),
                "axis": [[o, round(DS(*XZ(L / 2, o)), 1)] for o in range(0, o1, 2)],
                "polys": [[list(map(list, P)), [list(map(list, hh)) for hh in H]] for P, H in polys],
                "grid": {"a0": a0, "o0": o0, "na": a1 - a0, "no": o1 - o0, "h": h, "g": g, "k": k}}
    print(key, "width", round(L, 1), "front ground", out[key]["ground_front"], "cells", sum(v is not None for r in h for v in r))
    print("  axis", out[key]["axis"])
json.dump(out, open(dst, "w", newline="\n")); print("→", dst)
