"""Piazza della Santissima Annunziata: geometry for blender/scripts/build_annunziata.py.

Inputs (M25 in docs/DATA-SOURCES.md): OSM relation 7085758 (Spedale degli Innocenti), way 234428743 (Basilica della
Santissima Annunziata), relation 7021619 (Loggia dei Servi di Maria), relation 17485081 (the square), way 1311312620 and
node 2426833324 (Tacca's fountains), way 1364484939 (Ferdinando I); LiDAR 2023 DSM; the app's terrain.
Output: blender/data/annunziata.json – outlines (scene x/z), ground per vertex (app terrain), DSM heights.
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

def node(i):
    n = [e for e in el if e["type"] == "node" and e["id"] == i][0]; return sc(n)
I = rel(7085758); L = rel(7021619); Pz = rel(17485081)
out = {"innocenti": feat(I["outer"][0], I["inner"]), "chiesa": feat(way(234428743)), "servi": feat(L["outer"][0], L["inner"]),
       "piazza": Pz["outer"], "fontane": [way(1311312620), node(2426833324)], "ferdinando": way(1364484939)}
out["ground_piazza"] = round(float(np.median([G(x, z) for x in np.arange(395, 465, 4.0) for z in np.arange(-560, -480, 4.0)])), 2)
# the square's frame: a along the Innocenti front (from its south-west end towards the church), o across the square
# (0 = the Innocenti front line, ≈61 = the Loggia dei Servi front, measured on the DSM profile across the square)
P0 = np.array([423.54, -477.69]); T = np.array([44.33, -58.96]); T /= np.linalg.norm(T); N = np.array([-T[1], T[0]])
if np.dot(np.array([428.0, -518.0]) - P0, N) < 0: N = -N
def XZ(a, o): p = P0 + T * a + N * o; return float(p[0]), float(p[1])
out["frame"] = {"p0": P0.round(3).tolist(), "t": T.round(6).tolist(), "n": N.round(6).tolist()}
def front_ground(a0, a1, o): return round(max(G(*XZ(a, o)) for a in np.arange(a0, a1 + 0.1, 1.0)), 2)
out["ground_fronts"] = {"innocenti": front_ground(0, 74, 1.5), "servi": front_ground(5, 77, 59.5), "chiesa": round(max(G(*XZ(80.5, o)) for o in np.arange(8, 49, 1.0)), 2)}
# raster massing behind the hand-built fronts: 1 m cells in the (a, o) frame, median DSM of 5 × 5 samples, terrain
SERVI = [XZ(5, 61), XZ(77, 61), XZ(77, 92), XZ(5, 92)]
masks = {"innocenti": (I["outer"][0], I["inner"], lambda a, o: o < -11.5),
         "servi": (SERVI, [], lambda a, o: o > 72.5),
         "chiesa": (way(234428743), [], lambda a, o: a > 90.5 and not (104 <= a <= 152 and 17.5 <= o <= 31.5) and (a - 164) ** 2 + (o - 21) ** 2 > 14.3 ** 2)}
grids = {}
for k, (Pk, holes, keep) in masks.items():
    A = [float(np.dot(np.array(p) - P0, T)) for p in Pk]; O = [float(np.dot(np.array(p) - P0, N)) for p in Pk]
    a0, a1, o0, o1 = int(min(A)) - 1, int(max(A)) + 2, int(min(O)) - 1, int(max(O)) + 2
    h, g = [], []
    for o in range(o0, o1):
        hr, gr = [], []
        for a in range(a0, a1):
            ac, oc = a + 0.5, o + 0.5; x, z = XZ(ac, oc)
            if keep(ac, oc) and inside(x, z, Pk) and not any(inside(x, z, hh) for hh in holes):
                v = float(np.median([DS(*XZ(ac + da, oc + do)) for da in (-1, -0.5, 0, 0.5, 1) for do in (-1, -0.5, 0, 0.5, 1)]))
                hr.append(round(v, 1)); gr.append(round(G(x, z), 2))
            else: hr.append(None); gr.append(None)
        h.append(hr); g.append(gr)
    grids[k] = {"a0": a0, "o0": o0, "na": a1 - a0, "no": o1 - o0, "h": h, "g": g}
out["grid"] = grids; out["servi_rect"] = SERVI
dst = os.path.join(ROOT, "blender", "data", "annunziata.json"); json.dump(out, open(dst, "w", newline="\n")); print("→", dst)
for k in ("innocenti", "chiesa", "servi"): print(k, len(out[k]["pts"]), "pts", len(out[k]["holes"]), "holes", out[k]["p50"], out[k]["p90"], "ground", min(out[k]["ground"]), max(out[k]["ground"]))
print("piazza ground", out["ground_piazza"], "fronts", out["ground_fronts"], "cells", {k: sum(v is not None for r in g["h"] for v in r) for k, g in grids.items()})
