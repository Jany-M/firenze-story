"""Vasari Corridor beyond the bridge: centre lines and heights for blender/scripts/build_corridoio.py.

Inputs (M19 in docs/DATA-SOURCES.md):
  _dev/data/raw/osm/core_osm.json   OSM relations 21744598–21744601 (Corridoio Vasariano, building:part level 2): the outline
                                    of the corridor on the Lungarno degli Archibusieri, across the Uffizi and Via della Ninna,
                                    and in Oltrarno from the bridge to the Boboli garden
  LiDAR 2023 DSM/DTM (0.5 m)        roof height along the corridor where it stands free (lower envelope of the DSM)
  web/public/data/terrain.f32       ground under the corridor (the app's own terrain mesh, as for the walls)
Output: blender/data/corridoio.json – scene coordinates (x east, z south, y = elevation − 40 m):
  {run: {pts: [[x, z]], s: [...], width: [...], ground: [...], top_dsm: [...], eave: [...], floor: [...]}}
  for run in lungarno (bridge head → Uffizi), oltrarno (bridge end → Boboli), ninna (overpass on Via della Ninna).
"""
import os, sys, json, math
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from common import ROOT, SRC, ORIGIN, T_WGS_UTM, load_grid, Grid

el = json.load(open(os.path.join(SRC, "data", "raw", "osm", "core_osm.json"), encoding="utf-8"))["elements"]
ways = {e["id"]: e for e in el if e["type"] == "way"}
rels = {e["id"]: e for e in el if e["type"] == "relation"}
def sc(p): x, y = T_WGS_UTM.transform(p["lon"], p["lat"]); return [round(x - ORIGIN[0], 2), round(-(y - ORIGIN[1]), 2)]
def member_pts(rel, ref):
    for m in rels[rel]["members"]:
        if m["ref"] == ref: return [sc(p) for p in (m.get("geometry") or ways[ref]["geometry"])]
    raise KeyError(ref)

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

def resample(pl, step):
    pl = [np.array(p, float) for p in pl]; out = [pl[0]]
    for a, b in zip(pl, pl[1:]):
        n = max(1, int(np.linalg.norm(b - a) / step)); out += [a + (b - a) * (k / n) for k in range(1, n + 1)]
    return np.array(out)
def centre(A, B, step=2.0):
    """Centre line of a narrow strip given its two long sides (each from the same end)."""
    A = resample(A, 0.5); Bp = resample(B, 0.5); mids, wid = [], []
    for p in A:
        d = np.linalg.norm(Bp - p, axis=1); j = int(d.argmin()); mids.append((p + Bp[j]) / 2); wid.append(float(d[j]))
    mids = np.array(mids); k = 5
    sm = np.array([mids[max(0, i - k):i + k + 1].mean(0) for i in range(len(mids))]); sm[0], sm[-1] = mids[0], mids[-1]
    c = resample(sm.tolist(), 0.25); s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(c, axis=0), axis=1))])
    t = list(np.arange(0, s[-1], step)) + [s[-1]]
    pts = [[float(np.interp(v, s, c[:, 0])), float(np.interp(v, s, c[:, 1]))] for v in t]
    w = np.interp(np.linspace(0, 1, len(pts)), np.linspace(0, 1, len(wid)), wid)
    return pts, [float(v) for v in w]
def profile(pts, half=1.5):
    top = []
    for i, (x, z) in enumerate(pts):
        a, b = pts[max(0, i - 1)], pts[min(len(pts) - 1, i + 1)]; dx, dz = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dz) or 1
        nx, nz = -dz / L, dx / L
        top.append(max(DS(x + nx * o, z + nz * o) for o in np.linspace(-half, half, 7)))
    return top
def eaves(s, top, pin=()):
    """Roof eave along the run: the corridor's own roof where the DSM shows it (lower envelope), taller buildings bridged
    by interpolation; `pin` = [(s, eave)] fixed points (the bridge corridor)."""
    s, top = np.array(s), np.array(top); env = np.array([top[np.abs(s - v) <= 12].min() for v in s])
    free = top <= env + 1.5
    e = np.interp(s, s[free], top[free]) - 1.1
    for sp, ev in pin:
        w = np.clip(1 - np.abs(s - sp) / 10.0, 0, 1); e = e * (1 - w) + ev * w
    return [round(float(v), 2) for v in np.convolve(np.pad(e, 3, mode="edge"), np.ones(7) / 7, mode="valid")]

# bridge corridor ends (build_ponte_vecchio.py: s = −48.5 / 46, w = 7.4 east of the axis; floor 17.6, eave 22.2)
A, B = np.array((-128.8, 379.8)), np.array((-174.3, 471.1)); MID = (A + B) / 2; u = (B - A) / np.linalg.norm(B - A); E = np.array((u[1], -u[0]))
if E[0] < 0: E = -E
P_N, P_S = (MID + u * -48.5 + E * 7.4).tolist(), (MID + u * 46.0 + E * 7.4).tolist()
BR_FLOOR, BR_EAVE = 17.6, 22.2

out = {"bridge": {"north": P_N, "south": P_S, "floor": BR_FLOOR, "eave": BR_EAVE}}
# Oltrarno: the strip out to the Boboli end and back (relation 21744599), plus the bend round Torre dei Mannelli
ring = member_pts(21744599, 1570307796); bend = member_pts(21744599, 1570361457)
iend = max(range(len(ring)), key=lambda i: math.dist(ring[i], ring[0]) if i < 30 else 0)
side_a = ring[:iend + 1]; side_b = (ring[iend + 1:] + bend[1:])[::-1]
side_b = side_b[::-1] if math.dist(side_b[0], side_a[0]) > math.dist(side_b[-1], side_a[0]) else side_b
pts, wid = centre(side_a, side_b[::-1] if math.dist(side_b[0], side_a[0]) > 30 else side_b)
pts = [P_S] + pts; wid = [3.0] + wid
# Lungarno degli Archibusieri (relation 21744601): river side and street side of the loggia; corner on the bridge axis
lung, lw = centre([[-122.8, 376.8], [-64.1, 405.7], [-33.9, 421.3]], [[-119.1, 385.8], [-30.9, 428.0]])
runs = {"oltrarno": (pts, wid, [(0.0, BR_EAVE)]), "lungarno": (lung, lw, [])}
for k, (P, W, pin) in runs.items():
    s = [0.0]
    for a, b in zip(P, P[1:]): s.append(s[-1] + math.dist(a, b))
    top = profile(P); ev = eaves(s, top, pin)
    out[k] = {"pts": [[round(x, 2), round(z, 2)] for x, z in P], "s": [round(v, 2) for v in s], "width": [round(v, 2) for v in W],
              "ground": [round(G(x, z), 2) for x, z in P], "top_dsm": [round(v, 2) for v in top], "eave": ev,
              "floor": [round(v - 4.6, 2) for v in ev]}
    print(k, len(P), "pts", round(s[-1], 1), "m; eave", min(ev), "–", max(ev), "; ground", round(min(out[k]["ground"]), 1), "–", round(max(out[k]["ground"]), 1))
# Via della Ninna: the overpass between the Uffizi and Palazzo Vecchio (outline points 92.5/303.4 … 89.4/310.9)
n0, n1 = [95.65, 304.7], [92.55, 312.2]
out["ninna"] = {"pts": [n0, n1], "width": 6.8, "ground": round(G(94.1, 308.45), 2)}
dst = os.path.join(ROOT, "blender", "data", "corridoio.json")
json.dump(out, open(dst, "w", newline="\n"), indent=0); print("→", dst)
