"""Palazzo Strozzi, the Arcone block of Piazza della Repubblica and the Mercato Centrale: geometry for
blender/scripts/build_strozzi.py, build_repubblica.py and build_mercato_centrale.py.

Inputs (M22–M24 in docs/DATA-SOURCES.md): OSM relation 2951949 (Palazzo Strozzi), relation 1593627 (the Arcone block),
way 23298757 (Piazza della Repubblica), way 480015428 (Mercato Centrale); LiDAR 2023 DSM; the app's terrain.
Output: blender/data/centro.json – outlines (scene x/z), ground per vertex (app terrain), DSM heights.
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
S = rel(2951949); A = rel(1593627)
out = {"strozzi": feat(S["outer"][0], S["inner"]), "arcone": feat(A["outer"][0], A["inner"]), "piazza": way(23298757),
       "mercato": feat(way(480015428))}
# Via Strozzi under the Arcone: ground and the DSM across the passage (x −144 … −132, z 32 … 43)
out["arcone"]["passage"] = {"x": [-144.0, -131.8], "z": [32.0, 43.0], "ground": round(G(-138.0, 37.5), 2),
                            "dsm": round(float(np.median([DS(x, z) for x in np.arange(-143, -133, 1.0) for z in np.arange(33, 42, 1.0)])), 2)}
dst = os.path.join(ROOT, "blender", "data", "centro.json"); json.dump(out, open(dst, "w", newline="\n")); print("→", dst)
for k in ("strozzi", "arcone", "mercato"): print(k, out[k]["p50"], out[k]["p90"], "ground", min(out[k]["ground"]), max(out[k]["ground"]))
print("passage", out["arcone"]["passage"])
