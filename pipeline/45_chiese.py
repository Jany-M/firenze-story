"""Churches of §12 item 6 (Santo Spirito, San Marco with its convent, and later the Carmine, Santa Felicita, San Miniato):
geometry for blender/scripts/build_<site>.py.

For each site: a frame on the façade (a along the front from its corner A to B, o inwards, 0 = the front line), the OSM
outlines of the complex, the ground along the front, a DSM profile along the main axis and a 1 m DSM raster of the whole
complex in the frame (median of 5 × 5 samples; terrain under each cell) → blender/data/chiese.json.
Inputs (M27+ in docs/DATA-SOURCES.md): OSM (ways and relations listed in SITES), LiDAR 2023 DSM, the app's terrain.
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
    # Santo Spirito: the church (way 24881563), the sacristy (relation 7101376), the Cenacolo (way 493525529), the convent
    # with its cloisters (relation 1631265); the front on the piazza from its south-west corner
    "spirito": {"A": (-573.6, 540.8), "B": (-546.2, 554.5), "ways": [24881563, 493525529], "rels": [7101376, 1631265]},
    # San Marco: the church (way 225706552) and the former convent (relation 1575764); the front on the square
    "marco": {"A": (267.8, -723.9), "B": (286.3, -714.1), "ways": [225706552], "rels": [1575764]},
}
def outline(kind, i):
    if kind == "way": return way(i), []
    r = rel(i); return r["outer"][0], r["inner"]
out = {}
for key, S in SITES.items():
    A, B = np.array(S["A"]), np.array(S["B"]); T = (B - A) / np.linalg.norm(B - A); N = np.array([-T[1], T[0]])
    polys = [outline("way", i) for i in S["ways"]] + [outline("rel", i) for i in S["rels"]]
    c = np.mean(np.array(polys[0][0]), axis=0)
    if np.dot(c - A, N) < 0: N = -N
    def XZ(a, o): p = A + T * a + N * o; return float(p[0]), float(p[1])
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
# ---- the squares in front: monuments, fountains, garden beds -------------------------------------------------------
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
def node(i): return sc([e for e in el if e["type"] == "node" and e["id"] == i][0])
def hull(pts):
    pts = sorted(set(pts))
    if len(pts) < 3: return pts
    def cr(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]
def green_beds(P, exclude=(), min_px=30):
    """Green areas of the 2017 orthophoto (the app's ortho2017.jpg, 0.88 m/px) inside polygon P, as convex hulls."""
    im = np.asarray(Image.open(os.path.join(ROOT, "web", "public", "data", "ortho2017.jpg")).convert("RGB")).astype(int)
    s_ = 3600 / im.shape[1]
    xs = [p[0] for p in P]; zs = [p[1] for p in P]
    i0, i1 = int((min(xs) + 1800) / s_), int((max(xs) + 1800) / s_) + 1
    j0, j1 = int((min(zs) + 1800) / s_), int((max(zs) + 1800) / s_) + 1
    c = im[j0:j1, i0:i1]; r, g, b = c[..., 0], c[..., 1], c[..., 2]
    M = (g >= r + 2) & (g > b)
    seen = np.zeros_like(M); out = []
    for j in range(M.shape[0]):
        for i in range(M.shape[1]):
            if not M[j, i] or seen[j, i]: continue
            stack = [(j, i)]; seen[j, i] = 1; cells = []
            while stack:
                y, x = stack.pop(); cells.append((y, x))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < M.shape[0] and 0 <= xx < M.shape[1] and M[yy, xx] and not seen[yy, xx]: seen[yy, xx] = 1; stack.append((yy, xx))
            if len(cells) < min_px: continue
            pts = [((i0 + x + 0.5) * s_ - 1800, (j0 + y + 0.5) * s_ - 1800) for y, x in cells]
            pts = [p for p in pts if inside(p[0], p[1], P) and not any(math.dist(p, e) < 3.5 for e in exclude)]
            if len(pts) < min_px: continue
            hp = [(round(x, 2), round(z, 2)) for x, z in hull(pts)]
            out.append({"pts": hp, "ground": round(float(np.median([G(x, z) for x, z in hp])), 2)})
    return out
import math
sq = {}
R = rel(1631844)
fz = way(118376983); fc = (float(np.mean([p[0] for p in fz[:-1]])), float(np.mean([p[1] for p in fz[:-1]])))
cald = way([e for e in el if e["type"] == "way" and e.get("tags", {}).get("name") == "Via delle Caldaie"][0]["id"])
rid = node(3118048295); near = min(cald, key=lambda p: math.dist(p, rid)); far = max(cald, key=lambda p: math.dist(p, rid))
dv = (far[0] - near[0], far[1] - near[1]); dl = math.hypot(*dv)
sq["spirito"] = {"square": R["outer"][0], "beds": [{"pts": h, "ground": round(float(np.median([G(x, z) for x, z in h])), 2)} for h in R["inner"]],
                 "fountain": {"c": [round(fc[0], 2), round(fc[1], 2)], "r": round(float(np.mean([math.dist(p, fc) for p in fz[:-1]])), 2), "ground": round(G(*fc), 2)},
                 "ridolfi": {"c": list(rid), "face": [round(dv[0] / dl, 3), round(dv[1] / dl, 3)], "ground": round(G(*rid), 2)}}
SM = way(1086789430); fanti = way(111797401); fcx = (float(np.mean([p[0] for p in fanti[:-1]])), float(np.mean([p[1] for p in fanti[:-1]])))
sq["marco"] = {"square": SM, "beds": green_beds(SM, exclude=[fcx]),
               "fanti": {"fence": fanti, "c": [round(fcx[0], 2), round(fcx[1], 2)], "ground": round(G(*fcx), 2)}}
for k, v in sq.items():
    out[k]["square"] = v; print(k, "beds", len(v["beds"]), [len(b["pts"]) for b in v["beds"]])
dst = os.path.join(ROOT, "blender", "data", "chiese.json"); json.dump(out, open(dst, "w", newline="\n")); print("→", dst)
