"""Landscape around the city -> OUT:
  terrain.f32        core terrain, 4 m (LiDAR 2023 DTM), riverbed carved under the water
  wide.f32           12 x 12 km terrain, 40 m (Copernicus GLO-30, buildings stripped by morphological opening,
                     offset to the LiDAR datum; core cells = LiDAR), riverbed carved
  land_s2.jpg        Sentinel-2 cloudless land texture for the wide area (UTM-aligned)
  water.{pos,idx}.bin  Arno + ponds, wide area; one surface per reach between weirs, sloping with the river
  weirs.json         pescaie (OSM geometry, dated), with upstream/downstream levels
  bridges.*          dated decks (wood / stone / iron / concrete phases)
  streets.json       walkable graph + zones + squares (with oriented rectangles)
  trees.bin          vegetation: Comune trees (modern) + historic scatter (until the ground is built) + wide ring
  urban.f32          per 8 m cell of the core: first year something stood there (vegetation / ground shader)
  yards.u8           per 4 m cell of the core: share of open ground inside the blocks (not street, not building), 0–255
  map textures, meta.json
"""
import sys, os, json, re, zipfile, io, math, numpy as np, cv2
sys.path.insert(0, os.path.dirname(__file__))
from common import *
from shapely.geometry import LineString, Point, Polygon, box, MultiPolygon, MultiPoint
from shapely.ops import unary_union, split, polygonize, linemerge
from shapely import affinity
import shapefile, mapbox_earcut as earcut, tifffile
from scipy.ndimage import map_coordinates
from PIL import Image

CORE = box(X0, Y0, X1, Y1)
HALF = 6000.0
WX0, WY0, WX1, WY1 = ORIGIN[0] - HALF, ORIGIN[1] - HALF, ORIGIN[0] + HALF, ORIGIN[1] + HALF
WIDE = box(WX0, WY0, WX1, WY1)
RAW = lambda *p: os.path.join(SRC, "data", "raw", *p)
rng = np.random.default_rng(1333)
DTM = load_grid("dtm"); DTM = np.where(np.isnan(DTM), np.nanmedian(DTM), DTM)
DSM = load_grid("dsm"); DSM = np.where(np.isnan(DSM), DTM, DSM)
dtm, dsm = Grid(DTM, 0.5), Grid(DSM, 0.5)
core_smooth = Grid(cv2.blur(DTM, (9, 9)), 0.5)
def utm_line(geom): return [T_WGS_UTM.transform(p["lon"], p["lat"]) for p in geom]
def year(s):
    m = re.match(r"^(-?\d{1,4})", (s or "").strip()); return int(m.group(1)) if m else None
def loc(x, y, h): return [round(x - ORIGIN[0], 2), round(h - BASE_Z, 2), round(-(y - ORIGIN[1]), 2)]
def in_core(x, y): return (x >= X0) & (x <= X1) & (y >= Y0) & (y <= Y1)

# ================= wide DEM (Copernicus GLO-30 DSM -> bare-earth approximation) =================
cop = tifffile.imread(RAW("wide", "cop30_N43E011.tif")).astype(np.float32)        # lat 44..43 (rows), lon 11..12 (cols)
nr, nc = cop.shape
lonA, latA = T_UTM_WGS.transform(np.array([WX0, WX1, WX0, WX1]), np.array([WY0, WY0, WY1, WY1]))
r0, r1 = int((44 - latA.max()) * nr) - 10, int((44 - latA.min()) * nr) + 10
c0, c1 = int((lonA.min() - 11) * nc) - 10, int((lonA.max() - 11) * nc) + 10
crop = cop[r0:r1, c0:c1]
k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))                         # ~150 m: removes blocks of buildings / tree stands
bare = cv2.GaussianBlur(cv2.morphologyEx(crop, cv2.MORPH_OPEN, k), (5, 5), 0)
def dem(x, y, src=None):
    lon, lat = T_UTM_WGS.transform(np.asarray(x, float).ravel(), np.asarray(y, float).ravel())
    r = ((44 - lat) * nr - 0.5 - r0).astype(np.float32); c = ((lon - 11) * nc - 0.5 - c0).astype(np.float32)
    return map_coordinates(bare if src is None else src, [r, c], order=1, mode="nearest")
dem_raw = lambda x, y: dem(x, y, crop)                                 # Copernicus flattens water: raw DEM = water level
WS = 40.0; nW = int(2 * HALF / WS) + 1
wx = WX0 + np.arange(nW) * WS; wy = WY1 - np.arange(nW) * WS
WXX, WYY = np.meshgrid(wx, wy)
HW = dem(WXX, WYY).reshape(nW, nW)
inC = in_core(WXX, WYY)
coreH = core_smooth(WXX[inC], WYY[inC])
off = 0.0                                                              # Copernicus -> LiDAR datum, calibrated on the river below
def height(x, y):
    """Best terrain height (m a.s.l.) anywhere in the wide area: LiDAR in the core, DEM outside."""
    x = np.asarray(x, float).ravel(); y = np.asarray(y, float).ravel(); out = dem(x, y) + off
    m = in_core(x, y)
    if m.any(): out[m] = core_smooth(x[m], y[m])
    return out

# ================= water: polygons, weirs, reaches, levels =================
def water_polys(path, clip):
    out = []
    for e in json.load(open(path, encoding="utf-8"))["elements"]:
        rings = []
        if e["type"] == "way" and len(e.get("geometry", [])) >= 4: rings = [("outer", e["geometry"])]
        elif e["type"] == "relation": rings = [(m.get("role"), m["geometry"]) for m in e.get("members", []) if m.get("geometry")]
        outs = [Polygon(utm_line(g)).buffer(0) for r_, g in rings if r_ == "outer" and len(g) >= 4 and g[0] == g[-1]]
        if not outs and e["type"] == "relation":
            outs = list(polygonize(linemerge([LineString(utm_line(g)) for r_, g in rings if r_ == "outer"])))
        ins = [Polygon(utm_line(g)).buffer(0) for r_, g in rings if r_ == "inner" and len(g) >= 4 and g[0] == g[-1]]
        for o in outs: out.append(o.difference(unary_union(ins)) if ins else o)
    return unary_union(out).intersection(clip)
W = unary_union([water_polys(RAW("osm", "wide_water.json"), WIDE), water_polys(RAW("osm", "core_water.json"), CORE)])
W = W.buffer(0.5).buffer(-0.5)
polys = [p for p in (W.geoms if hasattr(W, "geoms") else [W]) if p.area > 1500]
ARNO = max(polys, key=lambda p: p.area)

# weirs (pescaie): OSM lines crossing the Arno; dates from the literature (see docs/HISTORY.md, river section)
WEIR_DATES = [  # name regex, start, conf, note
    (r"niccol|giustizia", 1300, "inferred", "Pescaia di San Niccolò (della Giustizia); mills of San Niccolò documented 1423"),
    (r"santa rosa|ognissanti", 1300, "inferred", "Pescaia di Santa Rosa (d'Ognissanti); mills of Ognissanti documented 1417"),
]
weirs = []
for e in json.load(open(RAW("osm", "wide_weirs.json"), encoding="utf-8"))["elements"]:
    if e["type"] != "way" or len(e.get("geometry", [])) < 2: continue
    L = LineString(utm_line(e["geometry"]))
    if L.length < 30 or not L.intersects(ARNO): continue
    nm = e.get("tags", {}).get("name", "") or ""
    d = next(((s, c, n) for rx, s, c, n in WEIR_DATES if re.search(rx, nm, re.I)), (1900, "conjectural", "date unknown"))
    weirs.append({"name": nm or "pescaia", "line": L, "start": d[0], "conf": d[1], "note": d[2]})
weirs.sort(key=lambda w: w["line"].centroid.x)
print("weirs", [(w["name"], round(w["line"].centroid.x), w["start"]) for w in weirs])

# split the Arno into reaches at the weirs (lines extended across the whole bed)
reaches = [ARNO]
for w in weirs:
    cut = affinity.scale(w["line"], 3.0, 3.0)
    nxt = []
    for R in reaches:
        parts = split(R, cut) if R.intersects(cut) else [R]
        nxt += [p for p in getattr(parts, "geoms", parts) if p.area > 50]
    reaches = nxt
others = [p for p in polys if p is not ARNO]

def sample_pts(P, step=20.0):
    x0, y0, x1, y1 = P.bounds
    gx, gy = np.meshgrid(np.arange(x0, x1, step), np.arange(y0, y1, step))
    pts = [(x, y) for x, y in zip(gx.ravel(), gy.ravel()) if P.contains(Point(x, y))]
    return np.array(pts) if pts else np.array(P.representative_point().coords)
# Pools between weirs, west -> east. Ground under the water is often interpolated from the banks (reads high), so
# each pool takes a low percentile of its samples and pools are forced to step down at every weir going downstream.
wx_sorted = sorted(w["line"].centroid.x for w in weirs)
def pool_of(P): return int(np.searchsorted(wx_sorted, P.centroid.x))
pool_pts = {}
for R in reaches:
    pts = sample_pts(R); pool_pts.setdefault(pool_of(R), []).append(np.column_stack([pts, height(pts[:, 0], pts[:, 1])]))
pool_lv = {}
core_pool = {i: in_core(np.vstack(pool_pts[i])[:, 0], np.vstack(pool_pts[i])[:, 1]).mean() > 0.5 for i in pool_pts}
offs = []
for i in sorted(pool_pts):
    A = np.vstack(pool_pts[i])
    if core_pool[i]:
        pool_lv[i] = float(np.percentile(A[:, 2], 10))                  # LiDAR
        offs.append(pool_lv[i] - float(np.median(dem_raw(A[:, 0], A[:, 1]))))
off = float(np.median(offs)) if offs else 0.0
for i in sorted(pool_pts):
    if not core_pool[i]:
        A = np.vstack(pool_pts[i]); pool_lv[i] = float(np.median(dem_raw(A[:, 0], A[:, 1]))) + off
        A[:, 2] = dem_raw(A[:, 0], A[:, 1]) + off; pool_pts[i] = [A]
HW += off; HW[inC] = coreH
print("Copernicus -> LiDAR offset (from the river)", round(off, 2))
for i in sorted(pool_lv)[1:]:
    pool_lv[i] = max(pool_lv[i], pool_lv[i - 1] + 0.4) if (i - 1) in pool_lv else pool_lv[i]
def pool_fn(i):
    A = np.vstack(pool_pts[i]); xm = A[:, 0].mean(); a = 0.0
    if np.ptp(A[:, 0]) > 1500:                                            # long outer pools: gentle slope, 0–3 m/km
        a = float(np.clip(np.polyfit(A[:, 0] - xm, A[:, 2], 1)[0], 0.0, 0.003))
    return lambda x, a=a, xm=xm, c=pool_lv[i]: a * (np.asarray(x, float) - xm) + c
FN = {i: pool_fn(i) for i in pool_lv}
def pond_fn(P):
    pts = sample_pts(P); z = float(np.percentile(height(pts[:, 0], pts[:, 1]), 10))
    return lambda x, z=z: np.full_like(np.asarray(x, float), z)
levels = [(R, FN[pool_of(R)]) for R in reaches] + [(P, pond_fn(P)) for P in others]
print("pool levels (m a.s.l.)", {k: round(v, 2) for k, v in pool_lv.items()})
def level_at(x, y):
    for P, f in levels:
        if P.buffer(1).contains(Point(x, y)): return float(f(x))
    return None

# water mesh
wv, wi, base = [], [], 0
for P, f in levels:
    for G in getattr(P, "geoms", [P]):
        ring = np.array(G.exterior.coords)[:-1]; holes = [np.array(h.coords)[:-1] for h in G.interiors]
        allpts = np.vstack([ring] + holes); ends = np.cumsum([len(ring)] + [len(h) for h in holes]).astype(np.uint32)
        tri = earcut.triangulate_float64(allpts, ends)
        z = f(allpts[:, 0]) + 0.15
        for (x, y), zz in zip(allpts, z): wv.append(loc(x, y, zz))
        wi += (np.array(tri) + base).tolist(); base += len(allpts)
np.array(wv, np.float32).tofile(os.path.join(OUT, "water.pos.bin")); np.array(wi, np.uint32).tofile(os.path.join(OUT, "water.idx.bin"))
print("water reaches", len(reaches), "ponds", len(others), "tris", len(wi) // 3)

# weirs export: crest on the upstream (east) side, toe 7 m downstream
wexp = []
for w in weirs:
    L = w["line"].intersection(ARNO.buffer(2))
    if L.is_empty: continue
    L = max(getattr(L, "geoms", [L]), key=lambda g: g.length)
    pts = np.array(L.coords); c = L.centroid
    up = level_at(c.x + 25, c.y) or level_at(c.x + 40, c.y); dn = level_at(c.x - 25, c.y) or level_at(c.x - 40, c.y)
    if up is None or dn is None: continue
    up, dn = max(up, dn), min(up, dn)
    wexp.append({"name": w["name"], "start": w["start"], "end": None, "conf": w["conf"], "note": w["note"],
                 "pts": [[round(x - ORIGIN[0], 1), round(-(y - ORIGIN[1]), 1)] for x, y in pts],
                 "up": round(up + 0.15 - BASE_Z, 2), "down": round(dn + 0.15 - BASE_Z, 2)})
save_json("weirs.json", wexp); print("weirs exported", [(w["name"], w["up"], w["down"]) for w in wexp])

# river axis for boats, fishermen, landings: every 20 m along x, the widest wet section of the Arno (banks + mid)
axis = []
for x in np.arange(WX0 + 10, WX1, 20.0):
    cut = LineString([(x, WY0), (x, WY1)]).intersection(ARNO)
    if cut.is_empty: continue
    seg = max(getattr(cut, "geoms", [cut]), key=lambda g: g.length)
    (xa, ya), (xb, yb) = seg.coords[0], seg.coords[-1]
    ym = (ya + yb) / 2; lv = level_at(x, ym)
    if lv is None or seg.length < 15: continue
    axis.append([round(x - ORIGIN[0], 1), round(lv + 0.15 - BASE_Z, 2), round(-(ym - ORIGIN[1]), 1),
                 round(-(max(ya, yb) - ORIGIN[1]), 1), round(-(min(ya, yb) - ORIGIN[1]), 1)])   # x, level, z mid, z north bank, z south bank
save_json("river.json", {"axis": axis, "note": "x, water level, z centre, z right (north) bank, z left (south) bank; flow towards -x"})
print("river axis points", len(axis))

def carve(H, XX, YY, depth=1.6):
    """Lower terrain under water to level - depth so the surface never z-fights with the ground."""
    flat_x, flat_y = XX.ravel(), YY.ravel(); Hf = H.ravel()
    for P, f in levels:
        x0, y0, x1, y1 = P.bounds
        cand = np.where((flat_x >= x0) & (flat_x <= x1) & (flat_y >= y0) & (flat_y <= y1))[0]
        if not len(cand): continue
        from shapely import contains_xy
        inside = cand[contains_xy(P, flat_x[cand], flat_y[cand])]
        Hf[inside] = np.minimum(Hf[inside], f(flat_x[inside]) - depth)
    return Hf.reshape(H.shape)

# ================= terrains =================
STEP = 4.0; n = int((X1 - X0) / STEP) + 1
xs = X0 + np.arange(n) * STEP; ys = Y1 - np.arange(n) * STEP
XX, YY = np.meshgrid(xs, ys)
H = core_smooth(XX.ravel(), YY.ravel()).reshape(n, n)
H = carve(H, XX, YY)
os.makedirs(BUILD, exist_ok=True); (H - BASE_Z).astype(np.float32).tofile(os.path.join(BUILD, "terrain_raw.f32"))   # for 46_lungarni.py
# The lungarni's walls (pipeline/46_lungarni.py → blender/data/lungarni.json, from an earlier run of this step): the 4 m
# grid draws the vertical wall as a slope whose vertices poke out of the water in front of the model's wall as teeth.
# Under the model's street (wall to houses) the ground is held just below the road; in front of the wall, to 25 m out, at
# the wall's foot.
LJ = os.path.join(ROOT, "blender", "data", "lungarni.json")
if os.path.exists(LJ):
    zs_scene = -(YY - ORIGIN[1]); xs_scene = XX - ORIGIN[0]; held = 0
    for st in json.load(open(LJ, encoding="utf-8"))["stretches"]:
        P = np.array(st["pts"], float)
        if len(P) < 2: continue
        m = (xs_scene >= P[0, 0]) & (xs_scene <= P[-1, 0])
        zf = np.interp(xs_scene[m], P[:, 0], P[:, 1]); low = np.interp(xs_scene[m], P[:, 0], P[:, 3])
        out = zs_scene[m] - zf if st["bank"] == "n" else zf - zs_scene[m]          # metres riverward of the face
        sub = H[m]
        if P.shape[1] >= 7:                                                             # the street from the wall to the houses
            houses = np.abs(np.interp(xs_scene[m], P[:, 0], P[:, 5]) - zf); deck = np.interp(xs_scene[m], P[:, 0], P[:, 6])
            under = (out <= 0.5) & (out > -houses)                                       # under the model's road: just below it
            sub[under] = np.minimum(sub[under], deck[under] + BASE_Z - 0.12)
        sel = (out > 0.5) & (out < 25)                                                   # in front of the wall: at its foot
        cap = low + BASE_Z + 0.2
        held += int((sub[sel] > cap[sel]).sum()); sub[sel] = np.minimum(sub[sel], cap[sel]); H[m] = sub
    print("lungarni: ground held at the wall foot", held)
(H - BASE_Z).astype(np.float32).tofile(os.path.join(OUT, "terrain.f32"))
HW = carve(HW, WXX, WYY, 2.0)
(HW - BASE_Z).astype(np.float32).tofile(os.path.join(OUT, "wide.f32"))

# land texture (Sentinel-2 cloudless 2016, EOX, CC BY 4.0) resampled to the UTM wide square
mj = json.load(open(RAW("wide", "s2_z14.json"))); S2 = cv2.imread(RAW("wide", "s2_z14.jpg"))
NT = 2048; g = WX0 + (np.arange(NT) + 0.5) * (2 * HALF / NT); gy = WY1 - (np.arange(NT) + 0.5) * (2 * HALF / NT)
GX, GY = np.meshgrid(g, gy); lon, lat = T_UTM_WGS.transform(GX.ravel(), GY.ravel()); Z = 2 ** mj["z"]
px = ((lon + 180) / 360 * Z - mj["tx0"]) * 256
py = ((1 - np.log(np.tan(np.radians(lat)) + 1 / np.cos(np.radians(lat))) / np.pi) / 2 * Z - mj["ty0"]) * 256
LAND = cv2.remap(S2, px.reshape(NT, NT).astype(np.float32), py.reshape(NT, NT).astype(np.float32), cv2.INTER_LINEAR)
cv2.imwrite(os.path.join(OUT, "land_s2.jpg"), LAND, [cv2.IMWRITE_JPEG_QUALITY, 86])
def land_rgb(x, y):
    c = ((np.asarray(x) - WX0) / (2 * HALF) * NT).astype(int).clip(0, NT - 1); r = ((WY1 - np.asarray(y)) / (2 * HALF) * NT).astype(int).clip(0, NT - 1)
    return LAND[r, c][..., ::-1].astype(np.float32) / 255

# ================= streets graph + bridges (OSM) =================
ST = json.load(open(RAW("osm", "core_streets.json"), encoding="utf-8"))["elements"]
WALK = {"footway", "pedestrian", "residential", "living_street", "service", "unclassified", "tertiary", "secondary", "primary", "path", "steps", "cycleway", "square"}
nodes, edges, nid = [], [], {}
paved_e = []     # per edge: drawn as paved urban ground (roads and paved streets only, never inside a park or garden)
# Parks and gardens (OSM leisure=park/garden: Boboli, Cascine, Bardini, Semplici, Torrigiani…): their avenues and paths are
# gravel, earth or grass, so the ground shader must not lay street paving there; outside them a path counts as paved
# only with a paved surface tag (a footway with no tag is a pavement beside a road; a path or track is not)
_osm = json.load(open(RAW("osm", "core_osm.json"), encoding="utf-8"))["elements"]
_ways = {e["id"]: e for e in _osm if e["type"] == "way"}
_parks = []
for e in _osm:
    if e.get("tags", {}).get("leisure") not in ("park", "garden"): continue
    rings = [e.get("geometry")] if e["type"] == "way" else [m.get("geometry") or _ways.get(m["ref"], {}).get("geometry") for m in e.get("members", []) if m.get("role") == "outer"]
    for g in rings:
        if g and len(g) > 3:
            P = Polygon(utm_line(g)).buffer(0)
            if P.area > 2000: _parks.append(P)
PARKS = unary_union(_parks) if _parks else Polygon()
PAVED_S = {"paved", "asphalt", "concrete", "concrete:plates", "concrete:lanes", "paving_stones", "sett", "cobblestone", "unhewn_cobblestone", "stone", "metal", "wood", "bricks"}
ROADS = {"residential", "living_street", "service", "unclassified", "tertiary", "secondary", "primary", "pedestrian", "square"}
def is_paved(t, pts):
    sf = t.get("surface")
    if sf is not None and sf not in PAVED_S: return False                       # gravel, fine_gravel, ground, grass, compacted…
    if t.get("highway") in ("path", "track", "bridleway") and sf is None: return False
    mid = pts[len(pts) // 2]
    if PARKS.contains(Point(*mid)): return t.get("highway") in ROADS and sf in PAVED_S   # a real paved road through a park only
    return True
def key(x, y): return (round(x, 1), round(y, 1))
bridges = []
NAMED = {  # bridge -> dated phases (start, end, kind, conf). Sources: Comune "Una città e il suo fiume"; docs/HISTORY.md
    r"ponte vecchio": [(-30, 1177, "wood", "conjectural"), (1177, 1333, "stone", "documented"), (1345, None, "stone", "documented")],
    r"santa trinita": [(1252, 1333, "stone", "documented"), (1346, 1557, "stone", "inferred"), (1569, 1944, "stone", "documented"), (1958, None, "stone", "documented")],
    r"carraia": [(1220, 1333, "stone", "documented"), (1337, 1557, "stone", "inferred"), (1559, 1944, "stone", "inferred"), (1952, None, "stone", "documented")],
    r"alle grazie": [(1237, 1944, "stone", "documented"), (1957, None, "concrete", "documented")],
    r"vespucci": [(1957, None, "concrete", "documented")],
    r"san niccol": [(1837, 1844, "iron", "documented"), (1853, 1890, "iron", "documented"), (1890, 1944, "iron", "documented"),
                   (1949, None, "concrete", "documented")],
    r"vittoria": [(1835, 1931, "iron", "documented"), (1931, 1944, "concrete", "inferred"), (1946, None, "concrete", "documented")]}
for e in ST:
    t = e.get("tags", {})
    if e["type"] != "way" or "geometry" not in e: continue
    hw = t.get("highway"); pts = utm_line(e["geometry"])
    if t.get("bridge") == "yes" and hw and t.get("name"):
        L = LineString(pts)
        if CORE.intersects(L):
            for pat, spans in NAMED.items():
                if re.search(pat, t["name"], re.I): bridges.append((t["name"], L.intersection(CORE), spans)); break
    if hw not in WALK or t.get("area") == "yes": continue
    pv = is_paved(t, pts)
    seq = []
    for x, y in pts:
        if not (X0 <= x <= X1 and Y0 <= y <= Y1): seq.append(None); continue
        kk = key(x, y)
        if kk not in nid: nid[kk] = len(nodes); nodes.append(loc(x, y, float(dtm(x, y))))
        seq.append(nid[kk])
    for a, b in zip(seq[:-1], seq[1:]):
        if a is not None and b is not None and a != b: edges.append([a, b, 1 if t.get("bridge") == "yes" else 0]); paved_e.append(pv)
print("parks", len(_parks), "edges drawn as paved", sum(paved_e), "of", len(paved_e))
deck_items, bv, bi, merged = [], [], [], {}
for name, L, spans in bridges: merged.setdefault(name, ([], spans))[0].append(L)
for name, (ls, spans) in merged.items():
    L = unary_union(ls)
    if L.is_empty: continue
    P = L.buffer(7 if "vecchio" not in name.lower() else 11, cap_style=2)
    samples = [L.interpolate(f, normalized=True) for f in np.linspace(0.2, 0.8, 9)]
    dz = float(np.median([dtm(p.x, p.y) for p in samples]))
    ring = np.array(P.exterior.coords)[:-1]; tri = earcut.triangulate_float64(ring, np.array([len(ring)], np.uint32))
    for s0, s1, kind, conf in spans:
        deck_items.append({"name": name, "start": s0, "end": s1, "kind": kind, "conf": conf, "base": len(bv), "count": len(ring), "ibase": len(bi), "icount": len(tri)})
        bi += (np.array(tri) + len(bv)).tolist()
        for x, y in ring: bv.append([x - ORIGIN[0], dz - BASE_Z + 0.2, -(y - ORIGIN[1])])
np.array(bv, np.float32).tofile(os.path.join(OUT, "bridges.pos.bin")); np.array(bi, np.uint32).tofile(os.path.join(OUT, "bridges.idx.bin"))
print("streets nodes", len(nodes), "edges", len(edges), "bridge phases", len(deck_items))

OHM = json.load(open(RAW("ohm", "core_ohm.json"), encoding="utf-8"))["elements"]
wl = [(year(e["tags"].get("start_date")), LineString(utm_line(e["geometry"]))) for e in OHM
      if e["type"] == "way" and e.get("tags", {}).get("historic") == "citywalls"]
arn = MultiPoint([c for y, l in wl if y in (1284, 1333) for c in l.coords]).convex_hull.buffer(30)
rom = MultiPoint([c for y, l in wl if y == 15 for c in l.coords]).convex_hull
zone = [2 if rom.contains(Point(x + ORIGIN[0], -zz + ORIGIN[1])) else (1 if arn.contains(Point(x + ORIGIN[0], -zz + ORIGIN[1])) else 0) for x, h, zz in nodes]

# squares (piazze) with oriented rectangle: centre, long-axis rotation (three.js rotation.y), length, width
def sq_entry(nm, P):
    c = P.centroid; R = P.minimum_rotated_rectangle; q = np.array(R.exterior.coords)[:4]
    e1, e2 = q[1] - q[0], q[2] - q[1]; La, Lb = np.hypot(*e1), np.hypot(*e2); ax = e1 if La >= Lb else e2
    rot = -math.atan2(-ax[1], ax[0])                                   # local x along the long side (z = -north)
    return {"name": nm, "c": loc(c.x, c.y, float(dtm(c.x, c.y))), "r": round(math.sqrt(P.area / math.pi), 1),
            "rot": round(rot, 3), "len": round(max(La, Lb), 1), "wid": round(min(La, Lb), 1),
            "ring": [[round(x - ORIGIN[0], 1), round(-(y - ORIGIN[1]), 1)] for x, y in list(P.exterior.coords)[::max(1, len(P.exterior.coords) // 24)]]}
squares = []
for e in ST:
    t = e.get("tags", {})
    if e["type"] == "way" and (t.get("place") == "square" or t.get("highway") == "pedestrian" and t.get("area") == "yes") and t.get("name"):
        P = Polygon(utm_line(e["geometry"])).buffer(0)
        if P.area > 400 and CORE.contains(P.centroid): squares.append(dict(sq_entry(t["name"], P), park=bool(PARKS.contains(P.centroid))))
# Piazza Santa Croce is mapped in OSM only as street lines: outline from its edges + the basilica facade (OSM 2026)
SC = Polygon([T_WGS_UTM.transform(lo, la) for la, lo in [(43.76891, 11.26242), (43.76847, 11.26197), (43.76900, 11.26055), (43.76934, 11.26082)]])
squares.append(sq_entry("Piazza di Santa Croce", SC))
save_json("streets.json", {"nodes": nodes, "edges": edges, "zone": zone, "squares": squares, "bridges": deck_items})

# ================= urban raster: first year anything stood in each 8 m cell (from the dated city mesh) =================
UC = 8.0; nu = int((X1 - X0) / UC)
spos = np.fromfile(os.path.join(MESH, "structures.pos.bin"), np.float32).reshape(-1, 3)
sbid = np.fromfile(os.path.join(MESH, "structures.bid.bin"), np.float32).astype(int)
items = json.load(open(os.path.join(OUT, "structures.json"), encoding="utf-8"))["items"]
starts = np.array([it["start"] if it["kind"] != "roman" else 9999 for it in items], np.float32)   # Roman insulae are conjectural: keep greenery
U = np.full((nu, nu), 9999, np.float32)
cx = ((spos[:, 0] + ORIGIN[0] - X0) / UC).astype(int); cz = ((spos[:, 2] + (Y1 - ORIGIN[1])) / UC).astype(int)
ok = (cx >= 0) & (cx < nu) & (cz >= 0) & (cz < nu)
np.minimum.at(U, (cz[ok], cx[ok]), starts[sbid[ok]])
occ = (U < 9999).astype(np.float32)
U = cv2.erode(U, np.ones((3, 3), np.uint8))                             # spread 1 cell: yards, lanes
dense = cv2.blur(occ, (7, 7)) >= 0.35                                   # >= 35 % built within ~56 m
U_built = U.copy()

def urban_at(x, y):
    c = ((np.asarray(x) - X0) / UC).astype(int); r = ((Y1 - np.asarray(y)) / UC).astype(int)
    m = (c >= 0) & (c < nu) & (r >= 0) & (r < nu); out = np.full(np.shape(x), np.nan, np.float32)
    out[m] = U[r[m], c[m]]; return out

# ================= vegetation =================
# streets raster (2 m) to keep trees off today's streets and squares
NS = int((X1 - X0) / 2); SR = np.zeros((NS, NS), np.uint8)
for (a, b, _), pv in zip(edges, paved_e):
    if not pv: continue                                                 # garden paths: no paving, trees may grow by them
    A, B = nodes[a], nodes[b]
    cv2.line(SR, (int((A[0] + ORIGIN[0] - X0) / 2), int((A[2] + Y1 - ORIGIN[1]) / 2)), (int((B[0] + ORIGIN[0] - X0) / 2), int((B[2] + Y1 - ORIGIN[1]) / 2)), 1, 5)
for s in squares:
    if s.get("park"): continue                                           # a lawn or gravel "piazzale" inside a garden
    cv2.fillPoly(SR, [np.array([[(x + ORIGIN[0] - X0) / 2, (z + Y1 - ORIGIN[1]) / 2] for x, z in s["ring"]], np.int32)], 1)
def on_street(x, y):
    c = ((x - X0) / 2).astype(int).clip(0, NS - 1); r = ((Y1 - y) / 2).astype(int).clip(0, NS - 1); return SR[r, c] > 0
# streets and squares (Mercato Vecchio, Signoria, …) are urban ground from when the buildings around them stand
street8 = cv2.resize(SR, (nu, nu), interpolation=cv2.INTER_AREA) > 0
around = cv2.erode(U_built, np.ones((9, 9), np.uint8))                     # earliest building within ~36 m
U = np.where((U_built > 3000) & street8 & (around < 3000), around, U_built)
# the ground shader paves only built-up blocks and streets: in the sparse villa belt on the hills a detached house keeps
# its garden instead of a grey 8 m square around it (vegetation above still uses the full U)
np.where(dense | street8, U, 9999).astype(np.float32).tofile(os.path.join(OUT, "urban.f32"))
# yards: 4 m cells of the core that are neither street nor square nor under a present-day building – courtyards, gardens
# and orti inside the blocks. The ground shader lays a garden there where the 2017 orthophoto is green, paving elsewhere.
YC = 4.0; ny = int((X1 - X0) / YC)
FP = np.fromfile(os.path.join(OUT, "footprints.u16"), np.uint16).reshape(2, NS, NS)[0]     # layer 0: present-day buildings
free2 = ((FP == 0) & (SR == 0)).astype(np.float32)
YARD = cv2.resize(free2, (ny, ny), interpolation=cv2.INTER_AREA)
(np.clip(YARD, 0, 1) * 255).astype(np.uint8).tofile(os.path.join(OUT, "yards.u8"))
from shapely import contains_xy
TREES = []   # x, y, z (local), height, type (0 broadleaf, 1 cypress, 2 olive, 3 poplar), start, end
def add(x, y, h, typ, start, end):
    z = height(x, y)
    for i in range(len(x)): TREES.append([x[i] - ORIGIN[0], z[i] - BASE_Z, -(y[i] - ORIGIN[1]), h[i], typ[i], start[i], end[i]])
# 1. Comune trees (today's public trees), shown from 1880 (most are 19th–20th-century plantings)
z = zipfile.ZipFile(RAW("comune", "alberi.zip")); nm = z.namelist()
shp = [x for x in nm if x.lower().endswith(".shp")][0][:-4]
r = shapefile.Reader(shp=io.BytesIO(z.read(shp + ".shp")), dbf=io.BytesIO(z.read(shp + ".dbf")), encoding="latin-1")
prj = z.read(shp + ".prj").decode("latin-1") if (shp + ".prj") in nm else ""
ct = []
for s in r.shapes():
    if not s.points: continue
    x, y = s.points[0]
    if "Monte" in prj or x > 1e6: x, y = T_3003_UTM.transform(x, y)
    if X0 < x < X1 and Y0 < y < Y1: ct.append((x, y, min(max(float(dsm(x, y)) - float(dtm(x, y)), 4), 25)))
ct = np.array(ct)
add(ct[:, 0], ct[:, 1], ct[:, 2], np.where(rng.random(len(ct)) < 0.12, 3, 0), np.full(len(ct), 1880), np.full(len(ct), 99999))
n_comune = len(ct)
# 2. historic vegetation in the core: jittered 9 m grid; a tree lives until its ground is first built on
g = np.arange(X0 + 4.5, X1, 9.0); GX, GY = np.meshgrid(g, np.arange(Y0 + 4.5, Y1, 9.0))
x = GX.ravel() + rng.uniform(-4, 4, GX.size); y = GY.ravel() + rng.uniform(-4, 4, GX.size)
u = urban_at(x, y)
keep = (rng.random(x.size) < np.where(u > 3000, 0.22, 0.35)) & ~contains_xy(ARNO.buffer(3), x, y) & ~on_street(x, y)
x, y, u = x[keep], y[keep], u[keep]
typ = rng.choice([0, 1, 2, 3], x.size, p=[0.45, 0.15, 0.3, 0.1])
add(x, y, rng.uniform(5, 14, x.size), typ, np.full(x.size, -800), np.where(u > 3000, 99999, u))
n_hist = x.size
# 3. wide ring: woods/olive groves where Sentinel-2 is green today; trees on today's built-up land vanish by 1880-1960
g = np.arange(WX0 + 15, WX1, 30.0); GX, GY = np.meshgrid(g, g[::-1])
x = GX.ravel() + rng.uniform(-12, 12, GX.size); y = GY.ravel() + rng.uniform(-12, 12, GX.size)
m = ~in_core(x, y) & ~contains_xy(W.buffer(4), x, y); x, y = x[m], y[m]
rgb = land_rgb(x, y); lum = rgb.mean(1); green = rgb[:, 1] / (rgb.sum(1) + 1e-3)
wood = (green > 0.355) & (lum < 0.33); built = rgb[:, 0] > rgb[:, 1] * 1.04
p = np.where(wood, 0.36, np.where(built, 0.08, 0.06)); keep = rng.random(x.size) < p
x, y, wood, built = x[keep], y[keep], wood[keep], built[keep]
hz = height(x, y); hilly = hz > np.percentile(hz, 40)
typ = np.where(rng.random(x.size) < 0.13, 1, np.where(hilly & ~wood, 2, np.where(rng.random(x.size) < 0.15, 3, 0)))
end = np.where(built, rng.uniform(1880, 1960, x.size), 99999)
add(x, y, np.where(typ == 1, rng.uniform(10, 18, x.size), rng.uniform(5, 13, x.size)), typ, np.full(x.size, -800), end)
T = np.array(TREES, np.float32)
# no crown through a wall: a tree within its crown's reach of a building (any era, footprints of 20_build_city) lives only
# while that building does not stand – it ends when the building goes up, or starts after it comes down
SREC = json.load(open(os.path.join(OUT, "structures.json"), encoding="utf-8"))["items"]
BS = np.array([-9999] + [r["start"] for r in SREC], np.float32)
BE = np.array([99999] + [r["end"] if r.get("end") is not None else 99999 for r in SREC], np.float32)
FOOT2 = np.fromfile(os.path.join(OUT, "footprints.u16"), np.uint16).reshape(2, NS, NS)
tx, ty_ = T[:, 0] + ORIGIN[0], ORIGIN[1] - T[:, 2]
reach = np.clip(T[:, 3] * 0.3, 1.5, 5.0)                                  # crown radius, m (broadleaf ~0.22-0.3 h)
c0 = ((tx - X0) / 2).astype(int); r0 = ((Y1 - ty_) / 2).astype(int)
inside = (c0 >= 3) & (c0 < NS - 3) & (r0 >= 3) & (r0 < NS - 3)
t0, t1 = T[:, 5].copy(), T[:, 6].copy()
for dy in range(-2, 3):
    for dx in range(-2, 3):
        d = math.hypot(dx, dy) * 2.0
        m = inside & (d <= reach)
        for layer in (0, 1):
            b = np.zeros(len(T), np.int64); b[m] = FOOT2[layer, r0[m] + dy, c0[m] + dx]
            hit = b > 0
            if not hit.any(): continue
            bs, be = BS[b[hit]], BE[b[hit]]
            a0, a1 = t0[hit], t1[hit]
            later = bs > a0                                                # the building comes after the tree: cut its end
            a1 = np.where(later, np.minimum(a1, bs), a1)
            a0 = np.where(~later & (be > a0), be, a0)                       # it stood already: the tree only after it falls
            t0[hit], t1[hit] = a0, a1
gone = t0 >= t1
print("trees clear of walls: trimmed", int(((t0 != T[:, 5]) | (t1 != T[:, 6])).sum()), "dropped", int(gone.sum()))
T[:, 5], T[:, 6] = t0, t1
T = T[~gone]
T.tofile(os.path.join(OUT, "trees.bin"))
print("trees: comune", n_comune, "historic core", n_hist, "wide", x.size, "total", len(T))

# ================= map textures (UTM-aligned, core) =================
def tex(name, out, size, fmt="JPEG", q=82):
    a = resample_3857(RAW("historic_maps", name + ".png"), (X1 - X0) / size)
    im = Image.fromarray(a)
    if fmt == "JPEG":
        bg = Image.new("RGB", im.size, (236, 226, 204)); bg.paste(im, mask=im.split()[3]); bg.save(os.path.join(OUT, out), quality=q)
    else: im.save(os.path.join(OUT, out), optimize=True)
tex("Ortofoto2017_COL_2K_CoFi", "ortho2017.jpg", 4096, q=85)
tex("catasto_generale_toscano_fabbricati", "map_cadastre1830s.png", 2048, fmt="PNG")
tex("1843_PiantaGeometricaDiFirenzeFantozzi", "map_1843.jpg", 4096)
tex("1873_PiantaDiFirenzeEDintorniIGM", "map_1873.jpg", 4096)
tex("1937_MappaCittaDiFirenze", "map_1937.jpg", 4096)
save_json("meta.json", {"bbox_utm": [X0, Y0, X1, Y1], "origin_utm": list(ORIGIN), "base_z": BASE_Z, "crs": "EPSG:25832",
                        "terrain": {"n": n, "step": STEP}, "wide": {"n": nW, "step": WS, "half": HALF, "land": "land_s2.jpg"},
                        "urban": {"n": nu, "cell": UC}, "yards": {"n": ny, "cell": YC}, "trees": {"count": len(T), "stride": 7},
                        "built": __import__("datetime").date.today().isoformat()})
print("done")
