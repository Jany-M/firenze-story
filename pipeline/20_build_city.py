"""Build the 4D city for the web app.

Inputs  (SRC/data): LiDAR 2023 DSM/DTM core tiles, OSM buildings, OpenHistoricalMap, Wikidata, Comune archaeology,
                    historic map mosaics (cadastre 1830s partial, 1843, 1873, 1937) resampled by BUILD/*_05.npy.
Outputs (OUT):      structures.json (one record per structure); the merged geometry structures.*.bin goes to MESH
                    (_dev/data/build/city) for 23_city_tiles.py – the app loads the tiles, not the one big mesh
Every structure has: start/end year, construction ramp, confidence (documented|inferred|conjectural), sources.
"""
import sys, os, json, math, re, zipfile, io, numpy as np, cv2
sys.path.insert(0, os.path.dirname(__file__))
from common import *
import shapefile
from shapely.geometry import Polygon, MultiPolygon, LineString, Point, box, MultiPoint
from shapely.ops import unary_union
from shapely import delaunay_triangles, prepared, STRtree
from shapely.geometry.polygon import orient
import mapbox_earcut as earcut
from roofs import fit_planes, envelope, env_z, roof_uv

CORE = box(X0, Y0, X1, Y1)
RES = 0.5
print("loading LiDAR…"); DSM = load_grid("dsm"); DTM = load_grid("dtm")
DTM = np.where(np.isnan(DTM), np.nanmedian(DTM), DTM)
DSM = np.where(np.isnan(DSM), DTM, DSM)
DSMS = cv2.medianBlur(DSM.astype(np.float32), 5); DSMS = cv2.medianBlur(DSMS, 5)   # 2x 2.5 m median: removes chimneys/antennas/noise
dsm, dtm = Grid(DSMS, RES), Grid(DTM, RES)
MAPS = {k: np.load(os.path.join(BUILD, f"{v}_05.npy")) for k, v in {
    "cad": "catasto_generale_toscano_fabbricati", "m1843": "1843_PiantaGeometricaDiFirenzeFantozzi",
    "m1873": "1873_PiantaDiFirenzeEDintorniIGM", "m1937": "1937_MappaCittaDiFirenze", "ortho": "Ortofoto2017_COL_2K_CoFi"}.items()}

# ---------- "built" masks per historic map (calibrated on sample crops) ----------
F43_R = 1640.0                                             # inner edge of the 1843 map's circular frame, m from the origin
def built_masks():
    m = {}
    c = MAPS["cad"]; m["cad"] = (c[..., 3] > 0)
    # 1843 Fantozzi: dark building fill only (lum < 105; at 150 garden texture, tree rows, ditches and road lines count), and only
    # inside the map's round frame (F43_R m from the origin): the ring scale and the corner vignettes are decoration.
    a = MAPS["m1843"][..., :3].astype(int); lum = a.mean(-1)
    yy, xx = np.ogrid[:lum.shape[0], :lum.shape[1]]
    inside = ((xx * RES + X0 - ORIGIN[0]) ** 2 + (Y1 - yy * RES - ORIGIN[1]) ** 2) < F43_R ** 2
    m["m1843"] = (lum < 105) & inside
    a = MAPS["m1873"][..., :3].astype(int); m["m1873"] = (a[..., 0] - a[..., 1] > 55) & (a[..., 1] < 150)
    a = MAPS["m1937"][..., :3].astype(int); m["m1937"] = (a[..., 0] > 170) & (a[..., 0] - a[..., 2] > 110) & (a[..., 1] < 185) & (a[..., 1] > 90)
    # cadastre coverage = union of drawn parcels, closed + dilated ~25 m
    cov = cv2.dilate(m["cad"].astype(np.uint8), np.ones((51, 51), np.uint8))
    m["cad_cov"] = cv2.erode(cov, np.ones((31, 31), np.uint8)) > 0
    return m
BM = built_masks()

def poly_mask(poly, shrink=0.0):
    """Raster mask (0.5 m) of a polygon within its bbox -> (rows, cols) index arrays."""
    p = poly.buffer(-shrink) if shrink else poly
    if p.is_empty: p = poly
    minx, miny, maxx, maxy = p.bounds
    c0, r0 = int((minx - X0) / RES), int((Y1 - maxy) / RES)
    c1, r1 = int((maxx - X0) / RES) + 1, int((Y1 - miny) / RES) + 1
    c0, r0 = max(c0, 0), max(r0, 0); c1, r1 = min(c1, DSM.shape[1]), min(r1, DSM.shape[0])
    if c1 <= c0 or r1 <= r0: return None
    mk = np.zeros((r1 - r0, c1 - c0), np.uint8)
    polys = p.geoms if isinstance(p, MultiPolygon) else [p]
    for g in polys:
        pts = np.array([[(x - X0) / RES - c0, (Y1 - y) / RES - r0] for x, y in g.exterior.coords], np.int32)
        cv2.fillPoly(mk, [pts], 1)
        for h in g.interiors:
            cv2.fillPoly(mk, [np.array([[(x - X0) / RES - c0, (Y1 - y) / RES - r0] for x, y in h.coords], np.int32)], 0)
    rr, cc = np.nonzero(mk)
    if len(rr) == 0: return None
    return rr + r0, cc + c0

# ---------- zones (historic wall circuits) for conjectural dating ----------
OHM = json.load(open(os.path.join(SRC, "data/raw/ohm/core_ohm.json"), encoding="utf-8"))["elements"]
def utm_line(geom): return [T_WGS_UTM.transform(p["lon"], p["lat"]) for p in geom]
def year(s):
    if not s: return None
    m = re.match(r"^(-?\d{1,4})", s.strip()); return int(m.group(1)) if m else None
walls = []
for e in OHM:
    t = e.get("tags", {})
    if e["type"] == "way" and t.get("historic") == "citywalls":
        walls.append((year(t.get("start_date")), year(t.get("end_date")), LineString(utm_line(e["geometry"])), t.get("name", "")))
def hull_of(pred):
    ls = [w[2] for w in walls if pred(w)]
    return MultiPoint([c for l in ls for c in l.coords]).convex_hull if ls else None
ZONE_ROMAN = hull_of(lambda w: w[0] == 15)
ZONE_1172 = hull_of(lambda w: w[0] in (1172, 1072))
ZONE_ARNOLFO = MultiPoint([c for w in walls if w[0] in (1284, 1333) for c in w[2].coords]).convex_hull.buffer(30)
def zone_start(p):
    c = p.representative_point()
    if ZONE_ROMAN is not None and ZONE_ROMAN.contains(c): return 1150, "inside Roman castrum: medieval fabric"
    if ZONE_1172 is not None and ZONE_1172.contains(c): return 1220, "inside 1172 walls"
    if ZONE_ARNOLFO.contains(c): return 1320, "inside 1284–1333 walls"
    return 1550, "outside the medieval walls"

# ---------- curated landmarks (dates from standard historiography; verify) ----------
LANDMARKS = [  # (name regex, start, ramp_years, phases, wiki title)
    (r"santa maria del fiore|^duomo", 1296, 140, [[1420, 52]], "Cattedrale di Santa Maria del Fiore"),   # nave until the dome (1420–36)
    (r"campanile di giotto", 1334, 25, [], "Campanile di Giotto"),
    (r"battistero", 1059, 70, [], "Battistero di San Giovanni (Firenze)"),
    (r"palazzo vecchio|palazzo della signoria", 1299, 15, [], "Palazzo Vecchio"),
    (r"loggia dei lanzi|loggia della signoria", 1376, 6, [], "Loggia dei Lanzi"),
    (r"basilica di santa croce|^santa croce$", 1294, 90, [], "Basilica di Santa Croce (Firenze)"),
    (r"santa maria novella", 1279, 78, [], "Santa Maria Novella"),
    (r"basilica di san lorenzo|^san lorenzo$", 1419, 40, [], "Basilica di San Lorenzo (Firenze)"),
    (r"orsanmichele", 1337, 43, [], "Orsanmichele"),
    (r"bargello|palazzo del podest", 1255, 6, [], "Museo nazionale del Bargello"),
    (r"medici riccardi", 1444, 40, [], "Palazzo Medici Riccardi"),
    (r"^palazzo pitti$", 1458, 12, [], "Palazzo Pitti"),
    (r"palazzo strozzi", 1489, 49, [], "Palazzo Strozzi"),
    (r"uffizi", 1560, 21, [], "Galleria degli Uffizi"),
    (r"corridoio vasariano", 1565, 1, [], "Corridoio Vasariano"),
    (r"santo spirito", 1444, 43, [], "Basilica di Santo Spirito"),
    (r"palazzo rucellai", 1446, 5, [], "Palazzo Rucellai"),
    (r"innocenti", 1419, 26, [], "Spedale degli Innocenti"),
    (r"santissima annunziata", 1444, 37, [], "Basilica della Santissima Annunziata"),
    (r"badia fiorentina", 978, 20, [], "Badia Fiorentina"),
    (r"palazzo davanzati", 1350, 10, [], "Palazzo Davanzati"),
    (r"mercato nuovo|loggia del porcellino", 1547, 4, [], "Loggia del Mercato Nuovo"),
    (r"santa trinita", 1250, 80, [], "Santa Trinita"),
    (r"ognissanti", 1251, 10, [], "Chiesa di Ognissanti"),
    (r"santa felicita", 1736, 3, [], "Santa Felicita (Firenze)"),
    (r"biblioteca nazionale", 1911, 24, [], "Biblioteca nazionale centrale di Firenze"),
    (r"stazione.*santa maria novella|firenze santa maria novella", 1932, 3, [], "Stazione di Firenze Santa Maria Novella"),
    (r"tempio maggiore|sinagoga", 1874, 8, [], "Sinagoga di Firenze"),
    (r"mercato centrale", 1870, 4, [], "Mercato Centrale (Firenze)"),
    (r"teatro della pergola", 1656, 1, [], "Teatro della Pergola"),
    (r"palazzo gondi", 1490, 11, [], "Palazzo Gondi"),
    (r"palazzo antinori", 1461, 8, [], "Palazzo Antinori"),
    (r"cappelle medicee|cappella dei principi", 1604, 36, [], "Cappelle medicee"),
    (r"palazzo vecchio", 1299, 15, [], "Palazzo Vecchio"),
]
LM_RE = [(re.compile(p, re.I), s, r, ph, w) for p, s, r, ph, w in LANDMARKS]

# ---------- Wikidata inception by QID ----------
WD = {}
for b in json.load(open(os.path.join(SRC, "data/raw/wikidata/core_items.json"), encoding="utf-8"))["results"]["bindings"]:
    q = b["item"]["value"].rsplit("/", 1)[1]; d = WD.setdefault(q, {"label": b.get("itemLabel", {}).get("value", "")})
    for k in ("inception", "dissolved"):
        if k in b:
            y = year(b[k]["value"].lstrip("+"))
            if y is not None: d[k] = min(d.get(k, y), y) if k == "inception" else d.get(k, y)

# ---------- geometry accumulators ----------
POS, NRM, BID, FU, FV, IDX = [], [], [], [], [], []
NV = [0]
REC = []
# fu codes (read by the city shader): >= 0 wall (metres along the footprint) · (-500, 0) roof (u = -fu - 1, v = fv down the
# slope) · (-1500, -1000] stone trim (sills, balcony slabs, soffits) · (-2500, -2000] iron (railings) · (-3500, -3000] plaster
FU_STONE, FU_IRON, FU_PLASTER = -1000.0, -2000.0, -3000.0
def add_mesh(bid, verts, norms, fu, tris, fv=None):
    v = np.asarray(verts, np.float32); n = np.asarray(norms, np.float32)
    POS.append(v); NRM.append(n); BID.append(np.full(len(v), bid, np.float32)); FU.append(np.asarray(fu, np.float32))
    FV.append(np.zeros(len(v), np.float32) if fv is None else np.asarray(fv, np.float32))
    IDX.append(np.asarray(tris, np.uint32) + NV[0]); NV[0] += len(v)

def add_box(bid, cx, cy, z0, sx, sy, h, ang, fu_code, bottom=False):
    """Oriented box (balcony slab, railing, chimney). cx, cy UTM; sx along ang, sy across; z0 absolute bottom."""
    ca, sa = math.cos(ang), math.sin(ang)
    corners = [(-sx / 2, -sy / 2), (sx / 2, -sy / 2), (sx / 2, sy / 2), (-sx / 2, sy / 2)]
    P = [(cx + u * ca - v * sa, cy + u * sa + v * ca) for u, v in corners]
    for i in range(4):
        (ax, ay), (bx, by) = P[i], P[(i + 1) % 4]; L = math.hypot(bx - ax, by - ay) or 1
        N = [(by - ay) / L, 0.0, (bx - ax) / L]
        add_mesh(bid, [lx(ax, ay, z0), lx(bx, by, z0), lx(bx, by, z0 + h), lx(ax, ay, z0 + h)], [N] * 4, [fu_code] * 4, [[0, 1, 2], [0, 2, 3]])
    add_mesh(bid, [lx(x, y, z0 + h) for x, y in P], [[0, 1, 0]] * 4, [fu_code] * 4, [[0, 2, 1], [0, 3, 2]])
    if bottom: add_mesh(bid, [lx(x, y, z0) for x, y in P], [[0, -1, 0]] * 4, [fu_code] * 4, [[0, 1, 2], [0, 2, 3]])

def lx(x, y, z): a, b, c = to_local(x, y, z); return [float(a), float(b), float(c)]

def hip_planes(p, eave_z, pitch=0.42):
    """Synthetic Tuscan hip roof (about 23 deg) over the footprint's oriented rectangle, eaves at eave_z (local frame)."""
    R = p.minimum_rotated_rectangle; q = np.array(R.exterior.coords)[:4]; c = np.array(p.centroid.coords[0])
    planes = []
    for i in range(4):
        A, B = q[i], q[(i + 1) % 4]; e = B - A; L = np.hypot(*e)
        if L < 0.5: continue
        n_in = np.array([-e[1], e[0]]) / L
        if np.dot(c - A, n_in) < 0: n_in = -n_in                       # inward normal of this eave edge
        # z = eave_z + pitch * (distance inside from edge AB)
        planes.append((pitch * n_in[0], pitch * n_in[1], eave_z - pitch * (n_in[0] * A[0] + n_in[1] * A[1])))
    return planes

def lidar_planes(p_local, pts, lo, hi):
    """Fit roof planes to DSM points; accept only if the lower envelope reproduces the scan."""
    if len(pts) < 40: return None
    if len(pts) > 2500: pts = pts[np.random.default_rng(len(pts)).choice(len(pts), 2500, replace=False)]
    planes, cover = fit_planes(pts, maxk=5)
    if not planes or cover < 0.5: return None
    z = env_z(planes, pts[:, 0], pts[:, 1])
    rms = float(np.sqrt(np.mean((np.clip(z, lo - 50, hi + 1) - pts[:, 2]) ** 2)))
    if rms > 0.95: return None
    return planes

def lidar_hip(p_local, pts, lo, hi):
    """When no plane set fits (several roofs in one footprint, noisy scan): a hip roof with the scan's own eave and
    ridge heights. Terraces (ridge ~ eave) become flat. Returns planes or None."""
    if len(pts) < 20: return None
    eave, ridge = float(np.percentile(pts[:, 2], 20)), float(np.percentile(pts[:, 2], 95))
    R = p_local.minimum_rotated_rectangle; q = np.array(R.exterior.coords)[:4]
    half = min(np.hypot(*(q[1] - q[0])), np.hypot(*(q[2] - q[1]))) / 2
    if half < 1.0: return None
    if ridge - eave < 0.8: return [(0.0, 0.0, float(np.percentile(pts[:, 2], 60)))]
    return hip_planes(p_local, eave, pitch=float(np.clip((ridge - eave) / half, 0.25, 0.7)))

ROOF_STATS = {"planes": 0, "lidar-hip": 0, "grid": 0, "hip": 0, "flat": 0}
# ---------- walkability: every record's footprint burnt into a 2 m grid (record id + 1), two layers because historic
# and present buildings overlap: 0 = present-day buildings, 1 = demolished / OHM / Roman. The browser checks the year.
FOOT_RES = 2.0
FOOT = np.zeros((2, int((Y1 - Y0) / FOOT_RES), int((X1 - X0) / FOOT_RES)), np.uint16)
def burn_footprint(bid, polys):
    r = REC[bid]
    if r["kind"] == "gate" or r.get("sub") == "citywalls": return          # passages through gates and walls stay open
    layer = 0 if r["kind"] == "building" else 1
    to_px = lambda cs: np.array([[(x - X0) / FOOT_RES, (Y1 - y) / FOOT_RES] for x, y in cs], np.int32)
    for p in polys:
        if p.is_empty or p.area < 4: continue
        cv2.fillPoly(FOOT[layer], [to_px(p.exterior.coords)], int(bid + 1))
        for h in p.interiors: cv2.fillPoly(FOOT[layer], [to_px(h.coords)], 0)    # courtyards

def extrude(bid, poly, ground, top_fn, roof="lidar", step=3.5, eave_poly=None, style=None, keep_scan=False):
    """Walls along every ring + roof. roof: 'lidar' (planes fitted to the DSM, grid fallback), 'hip' (synthetic), 'flat'.
    eave_poly: footprint grown where the roof may overhang the street (Florentine gronda). style: facade layout dict."""
    poly = poly.buffer(0)
    polys = list(poly.geoms) if isinstance(poly, MultiPolygon) else [poly]
    burn_footprint(bid, polys)
    top_raw = top_fn
    for p in polys:
        if p.area < 4: continue
        p = orient(p, 1.0)  # exterior CCW (E/N), holes CW
        cx, cy = p.centroid.x, p.centroid.y
        to_l = lambda g: __import__("shapely").affinity.translate(g, -cx, -cy)
        planes, lo, hi, mode = None, -1e9, 1e9, roof
        if roof == "lidar":
            inner_s = p.buffer(-1.2)
            if inner_s.is_empty: inner_s = p.buffer(-0.4)
            if inner_s.is_empty: inner_s = p
            rcI = poly_mask(inner_s)
            vals = DSMS[rcI] if rcI is not None else np.array([ground + 6])
            lo, hi = max(ground + 2.5, float(np.nanpercentile(vals, 5))), float(np.nanpercentile(vals, 99.5))
            if rcI is not None and p.area > 20:
                rr, cc = rcI; zr = DSM[rr, cc]; ok = (zr > lo - 0.5) & (zr < hi + 0.5)
                pts = np.c_[X0 + (cc[ok] + 0.5) * RES - cx, Y1 - (rr[ok] + 0.5) * RES - cy, zr[ok]]
                planes = lidar_planes(to_l(p), pts, lo, hi)
                # curated landmarks keep the scanned surface only when it has real relief (domes, towers, lanterns); a
                # palazzo whose planes do not fit gets the scan's hip roof like any house (the scan grid drew sagging
                # roofs with saw-toothed eaves)
                if planes is None and (not keep_scan or hi - lo < 10.0):
                    planes = lidar_hip(to_l(p), pts, lo, hi)
                    if planes is not None: mode = "lidar-hip"
            if planes is None:
                mode = "grid"; ib = inner_s.boundary
                def top_fn(x, y, _ib=ib, _lo=lo, _hi=hi, _in=prepared.prep(inner_s)):
                    pt = Point(x, y)
                    if not _in.contains(pt): pt = _ib.interpolate(_ib.project(pt))
                    return float(min(max(top_raw(pt.x, pt.y), _lo), _hi))
            elif mode != "lidar-hip": mode = "planes"
        elif roof == "hip" and p.area > 12:
            planes = hip_planes(to_l(p), top_raw(cx, cy)); mode = "hip"; lo, hi = ground + 2, 1e9
        if planes is not None:
            def top_fn(x, y, _pl=planes, _lo=lo, _hi=hi):
                return float(np.clip(env_z(_pl, x - cx, y - cy), _lo, _hi))
        ROOF_STATS[mode if mode in ROOF_STATS else "flat"] += 1
        # roof faces (and the walls' top line, which must pass through every ridge / hip end)
        extra_u = {}
        if planes is not None:
            E = p if eave_poly is None else orient(p.union(eave_poly.intersection(p.buffer(0.9, join_style=2))).buffer(0), 1.0)
            regions = envelope(planes, to_l(E), None)
            if not regions: planes = None
        rings = [p.exterior] + list(p.interiors)
        if planes is not None:
            for ring in rings:
                ls = LineString(ring.coords); ext = []
                for _, R in regions:
                    for x, y in R.exterior.coords:
                        pt = Point(x + cx, y + cy)
                        if ls.distance(pt) < 0.05: ext.append(ls.project(pt))
                extra_u[id(ring)] = ext
        bpts = []; SMOOTH = {}
        for ring in rings:
            ls = LineString(ring.coords); L = ls.length
            if planes is not None:     # planar roof: wall tops are straight between corners and ridge/hip crossings
                cc = np.array(ring.coords); seg_l = np.hypot(*np.diff(cc, axis=0).T)
                base_d = list(np.concatenate([[0], np.cumsum(seg_l)])[:-1])
            else:
                n = max(int(L / 2.0), 3); base_d = [i * L / n for i in range(n)]
            ds = sorted(set([round(d, 4) for d in base_d] + [L] + [round(d, 4) for d in extra_u.get(id(ring), []) if 0 < d < L]))
            pts = [ls.interpolate(d) for d in ds]
            if planes is None and len(pts) > 4:
                # scan-grid roofs: the eave line read off the DSM at every 2 m jumps between roof and street; a running
                # median of five samples round the ring (then a light mean) gives a straight, level eave
                raw = np.array([top_fn(q.x, q.y) for q in pts[:-1]]); n_ = len(raw)
                med = np.array([np.median(raw[[(k + d) % n_ for d in range(-2, 3)]]) for k in range(n_)])
                sm = np.array([med[[(k + d) % n_ for d in (-1, 0, 1)]].mean() for k in range(n_)])
                for q, h_ in zip(pts[:-1], sm): SMOOTH[(q.x, q.y)] = float(h_)
                SMOOTH[(pts[-1].x, pts[-1].y)] = float(sm[0])
            hz = lambda x, y: SMOOTH.get((x, y)) if (x, y) in SMOOTH else top_fn(x, y)
            u = 0.0
            for a, b in zip(pts[:-1], pts[1:]):
                ax, ay, bx, by = a.x, a.y, b.x, b.y
                seg = math.hypot(bx - ax, by - ay)
                if seg < 1e-3: continue
                ta, tb = hz(ax, ay), hz(bx, by)
                nx, ny = (by - ay) / seg, -(bx - ax) / seg          # outward for CCW exterior / CW holes
                N = [nx, 0.0, -ny]
                verts = [lx(ax, ay, ground), lx(bx, by, ground), lx(bx, by, tb), lx(ax, ay, ta)]
                add_mesh(bid, verts, [N] * 4, [u, u + seg, u + seg, u], [[0, 1, 2], [0, 2, 3]])
                u += seg
            bpts += [(q.x, q.y) for q in pts[:-1]]
        if planes is not None:
            for i, R in regions:
                a_, b_, c_ = planes[i]
                ring = np.array(R.exterior.coords)[:-1]; holes = [np.array(h.coords)[:-1] for h in R.interiors]
                allp = np.vstack([ring] + holes); ends = np.cumsum([len(ring)] + [len(h) for h in holes]).astype(np.uint32)
                T = np.array(earcut.triangulate_float64(allp, ends)).reshape(-1, 3)
                if not len(T): continue
                z = allp[:, 0] * a_ + allp[:, 1] * b_ + c_
                verts = np.array([lx(x + cx, y + cy, zz) for (x, y), zz in zip(allp, z)], np.float32)
                nrm = np.array([-a_, 1.0, b_]); nrm /= np.linalg.norm(nrm)    # local frame: x=E, y=up, z=-N
                v0, v1, v2 = verts[T[:, 0]], verts[T[:, 1]], verts[T[:, 2]]
                flip = np.cross(v1 - v0, v2 - v0)[:, 1] < 0; T[flip] = T[flip][:, [0, 2, 1]]
                uu, vv = roof_uv((a_, b_, c_), allp[:, 0], allp[:, 1])
                add_mesh(bid, verts, [nrm] * len(verts), -1.0 - np.mod(uu, 400), T, fv=vv)
                # soffit under the overhang (outside the walls), 0.18 m below the tiles, facing down
                ov = R.difference(to_l(p).buffer(0.01))
                for g in getattr(ov, "geoms", [ov]):
                    if not isinstance(g, Polygon) or g.area < 0.05: continue
                    rg = np.array(g.exterior.coords)[:-1]
                    Tg = np.array(earcut.triangulate_float64(rg, np.array([len(rg)], np.uint32))).reshape(-1, 3)
                    if not len(Tg): continue
                    zg = rg[:, 0] * a_ + rg[:, 1] * b_ + c_ - 0.18
                    vg = np.array([lx(x + cx, y + cy, zz) for (x, y), zz in zip(rg, zg)], np.float32)
                    w0, w1, w2 = vg[Tg[:, 0]], vg[Tg[:, 1]], vg[Tg[:, 2]]
                    fl = np.cross(w1 - w0, w2 - w0)[:, 1] > 0; Tg[fl] = Tg[fl][:, [0, 2, 1]]
                    add_mesh(bid, vg, [[0, -1, 0]] * len(vg), [FU_STONE] * len(vg), Tg)
            # chimneys (comignoli): 1–3 per roof, near the ridge, plastered
            if mode in ("planes", "lidar-hip") and p.area > 60:
                inner = p.buffer(-2.0); rng_c = np.random.default_rng(bid)
                if not inner.is_empty:
                    x0, y0, x1, y1 = inner.bounds
                    for _ in range(min(3, 1 + int(p.area / 180))):
                        for _t in range(12):
                            x, y = rng_c.uniform(x0, x1), rng_c.uniform(y0, y1)
                            if inner.contains(Point(x, y)): break
                        else: continue
                        z = top_fn(x, y)
                        add_box(bid, x, y, z - 0.3, 0.55, 0.55, 1.5, rng_c.uniform(0, 3.14), FU_PLASTER)
                        add_box(bid, x, y, z + 1.2, 0.8, 0.8, 0.12, 0, FU_STONE)
            if style: balconies(bid, p, ground, style)
            continue
        # fallback roofs: scan grid (mode 'grid') or flat
        pts = list(bpts)
        if roof == "lidar" and p.area > 25:
            minx, miny, maxx, maxy = p.bounds
            inner = p.buffer(-1.0)
            if not inner.is_empty:
                pi = prepared.prep(inner)
                gx = np.arange(minx + step / 2, maxx, step); gy = np.arange(miny + step / 2, maxy, step)
                pts += [(x, y) for x in gx for y in gy if pi.contains(Point(x, y))]
        tri = delaunay_triangles(MultiPoint(pts))
        pp = prepared.prep(p.buffer(0.05))
        index = {k: i for i, k in enumerate(pts)}
        tris = []
        for t in tri.geoms:
            if not pp.contains(t.centroid): continue
            c = list(t.exterior.coords)[:3]
            try: tris.append([index[(c[0][0], c[0][1])], index[(c[1][0], c[1][1])], index[(c[2][0], c[2][1])]])
            except KeyError: pass
        if not tris: continue
        z = np.array([SMOOTH[(x, y)] if (x, y) in SMOOTH else top_fn(x, y) for x, y in pts])
        verts = np.array([lx(x, y, zz) for (x, y), zz in zip(pts, z)], np.float32)
        T = np.array(tris)
        v0, v1, v2 = verts[T[:, 0]], verts[T[:, 1]], verts[T[:, 2]]
        fn = np.cross(v1 - v0, v2 - v0)
        flip = fn[:, 1] < 0; T[flip] = T[flip][:, [0, 2, 1]]; fn[flip] *= -1
        vn = np.zeros_like(verts)
        for k in range(3): np.add.at(vn, T[:, k], fn)
        vn /= np.linalg.norm(vn, axis=1, keepdims=True) + 1e-9
        add_mesh(bid, verts, vn, np.full(len(verts), -1.0), T)
        if style: balconies(bid, p, ground, style)

FOOT_TREE = None   # STRtree of present-day footprints (set before the building loop)
FOOT_LIST = []
def street_side(px, py, own):
    """True if the point lies outside every footprint (i.e. on a street, square or courtyard)."""
    pt = Point(px, py)
    if own.contains(pt): return False
    if FOOT_TREE is None: return True
    for i in FOOT_TREE.query(pt):
        if FOOT_LIST[i].contains(pt): return False
    return True

def balconies(bid, p, ground, st):
    """19th-century balconies on street facades, aligned with the shader's window grid (piano nobile)."""
    if not st.get("balc"): return
    gf, sp = st["gf"], st["sp"]; zb = ground + gf + 0.9 - 0.14
    ring = p.exterior; C = list(ring.coords); u = 0.0
    for (ax, ay), (bx, by) in zip(C[:-1], C[1:]):
        L = math.hypot(bx - ax, by - ay)
        if L >= 2 * sp + 1:
            tx, ty = (bx - ax) / L, (by - ay) / L; nx, ny = ty, -tx
            mx, my = (ax + bx) / 2, (ay + by) / 2
            if street_side(mx + nx * 1.6, my + ny * 1.6, p):
                m0, m1 = math.ceil((u + 0.8) / sp - 0.5), math.floor((u + L - 0.8) / sp - 0.5)
                if m1 >= m0:
                    mids = [(m0 + m1) // 2] if st["balc"] == 1 else list(range((m0 + m1) // 2 - 1, (m0 + m1) // 2 + 2))
                    mids = [m for m in mids if m0 <= m <= m1]
                    if mids:
                        s0, s1 = (mids[0] + 0.5) * sp - u - 0.85, (mids[-1] + 0.5) * sp - u + 0.85
                        w = s1 - s0; c = (s0 + s1) / 2; ang = math.atan2(ty, tx)
                        bx_, by_ = ax + tx * c + nx * 0.45, ay + ty * c + ny * 0.45
                        add_box(bid, bx_, by_, zb, w, 0.9, 0.16, ang, FU_STONE, bottom=True)             # slab
                        fx, fy = ax + tx * c + nx * 0.86, ay + ty * c + ny * 0.86
                        add_box(bid, fx, fy, zb + 0.16, w, 0.05, 1.0, ang, FU_IRON)                      # railing front
                        for sgn in (-1, 1):
                            sx, sy = ax + tx * (c + sgn * w / 2) + nx * 0.45, ay + ty * (c + sgn * w / 2) + ny * 0.45
                            add_box(bid, sx, sy, zb + 0.16, 0.05, 0.9, 1.0, ang, FU_IRON)              # railing sides
        u += L

def frac(mask, rc):
    if rc is None: return 0.0
    return float(mask[rc].mean())

def new_rec(**k):
    k["id"] = len(REC)
    if "style" not in k: k["style"] = style_for(k["id"], k["kind"], k["start"], k.get("h", 10) or 10, 100, k.get("name", ""))
    if "rgb" not in k: k["rgb"] = tile_rgb(k["id"])
    REC.append(k); return k["id"]

# ---------- facade style (single source of truth for the city shader: floor heights, window grid, types) ----------
# win: 0 framed rectangular · 1 arched (centinata) · 2 Gothic two-light (bifora) · 3 modern · 4 none (walls, towers, churches)
# grd: ground floor 0 plain + doors · 1 rusticated pietra forte · 2 shop arches (botteghe) · 3 shopfronts
# shut: 0 none · 1 green · 2 brown · 3 grey roller (shown from 1750 in the shader; modern from 1945)
# mat: 0 plaster · 1 pietra forte ashlar · 2 marble bichrome (white Carrara / green Prato) · 3 bare brick · 4 pietra serena
MAT_RE = [(re.compile(r, re.I), m) for r, m in [
    (r"battistero|santa maria del fiore|^duomo|campanile di giotto|basilica di santa croce|^santa croce$|santa maria novella$|^basilica di santa maria novella|san miniato", 2),
    (r"palazzo vecchio|palazzo della signoria|bargello|palazzo del podest|strozzi|^palazzo pitti$|medici riccardi|davanzati|gondi|antinori|rucellai|orsanmichele|loggia dei lanzi|loggia della signoria|torre|^porta ", 1),
    (r"basilica di san lorenzo|^san lorenzo$|santo spirito|ognissanti", 3),
    (r"innocenti|uffizi|mercato nuovo", 4)]]
CHURCH_RE = re.compile(r"chiesa|basilica|cattedrale|oratorio|cappell|battistero|duomo|^san |^santa |^santo |^santi |^ss\.", re.I)
def hsh(i, k): return ((i * 2654435761 + k * 40503) % 100003) / 100003.0
def style_for(rid, kind, start, h, area, name):
    mat = next((m for rx, m in MAT_RE if name and rx.search(name)), 0)
    church = bool(name and CHURCH_RE.search(name))
    H = lambda k: hsh(rid, k)
    if kind in ("ohm", "gate"): return dict(gf=4, fh=4, sp=6, win=4, grd=0, shut=0, mat=mat or 1, balc=0)
    if kind == "roman": return dict(gf=3.4, fh=3.2, sp=3.0, win=0 if H(1) < 0.5 else 4, grd=2, shut=0, mat=3 if H(2) < 0.3 else 0, balc=0)
    palazzo = area > 380 and h > 15
    if start < 1400:
        st = dict(gf=4.0 + 0.8 * H(1), fh=3.9 + 0.7 * H(2), sp=3.0 + 0.8 * H(3), win=1 if H(4) < 0.7 else 2,
                  grd=2 if H(5) < 0.55 else (1 if palazzo else 0), shut=1 if H(6) < 0.6 else 2, balc=0)
    elif start < 1600:
        st = dict(gf=5.2 if palazzo else 4.2, fh=(4.8 if palazzo else 3.9) + 0.4 * H(2), sp=(4.2 if palazzo else 3.3) + 0.5 * H(3),
                  win=1 if (palazzo and H(4) < 0.5) else 0, grd=1 if palazzo else (2 if H(5) < 0.4 else 0), shut=1 if H(6) < 0.7 else 2, balc=0)
    elif start < 1850:
        st = dict(gf=4.3, fh=3.7 + 0.4 * H(2), sp=3.2 + 0.4 * H(3), win=0, grd=2 if H(5) < 0.35 else 0, shut=1 if H(6) < 0.75 else 2, balc=0)
    elif start < 1945:
        st = dict(gf=4.6, fh=3.9 + 0.3 * H(2), sp=3.3 + 0.3 * H(3), win=0, grd=3 if H(5) < 0.5 else 0, shut=1 if H(6) < 0.6 else 2,
                  balc=(2 if palazzo else 1) if (h > 10 and H(7) < 0.6) else 0)
    else:
        st = dict(gf=3.8, fh=3.1, sp=2.9 + 0.4 * H(3), win=3, grd=3, shut=3, balc=0)
    if church: st.update(win=4, grd=0, shut=0, balc=0)
    if mat in (1, 2, 3): st.update(shut=0 if church or mat == 2 else st["shut"], balc=0)
    st["mat"] = mat
    return st
def roof_rgb(rc):
    """Median orthophoto colour of a roof (2017), 0-255; None if unavailable."""
    if rc is None: return None
    px = MAPS["ortho"][rc][:, :3]
    if not len(px): return None
    return [int(v) for v in np.median(px, axis=0)]
def tile_rgb(rid):
    t = hsh(rid, 9); return [int(150 + 40 * t), int(86 + 25 * t), int(62 + 15 * t)]    # weathered coppi

# ================= 1. Present-day buildings (OSM) dated by maps/cadastre/wikidata/landmarks ===========
OSM = json.load(open(os.path.join(SRC, "data/raw/osm/core_osm.json"), encoding="utf-8"))["elements"]
def osm_polys(e):
    if e["type"] == "way" and len(e.get("geometry", [])) >= 4:
        return Polygon(utm_line(e["geometry"]))
    if e["type"] == "relation":
        outer = [Polygon(utm_line(m["geometry"])) for m in e.get("members", []) if m.get("role") == "outer" and len(m.get("geometry", [])) >= 4]
        inner = [Polygon(utm_line(m["geometry"])) for m in e.get("members", []) if m.get("role") == "inner" and len(m.get("geometry", [])) >= 4]
        if not outer: return None
        g = unary_union([o.buffer(0) for o in outer])
        if inner: g = g.difference(unary_union([i.buffer(0) for i in inner]))
        return g
REPUBBLICA = Point(681500 - 92, 4849000 - 35).buffer(130)   # Mercato Vecchio + ghetto, rebuilt in the Risanamento 1885–95
today_polys = []
old_polys = []          # present-day buildings that already stood in the 1830s/1843
# pre-pass: all present-day footprints (neighbours decide where eaves and balconies may face the street)
for e in OSM:
    t = e.get("tags", {})
    if "building" not in t or t.get("building") in ("construction", "roof"): continue
    try: g = osm_polys(e)
    except Exception: continue
    if g is not None and not g.is_empty:
        g = g.buffer(0).intersection(CORE)
        if not g.is_empty and g.area >= 6: FOOT_LIST.append(g)
FOOT_TREE = STRtree(FOOT_LIST)
def eave_zone(g, depth=0.85):
    """Where the roof may overhang: around the footprint, minus every neighbouring footprint."""
    zone = g.buffer(depth, join_style=2).difference(g)
    near = [FOOT_LIST[i] for i in FOOT_TREE.query(g.buffer(depth))]
    near = [n for n in near if not n.equals(g)]
    return zone.difference(unary_union(near).buffer(0.05)) if near else zone
stats = {}
for e in OSM:
    t = e.get("tags", {})
    if "building" not in t or t.get("building") in ("construction", "roof"): continue
    try: g = osm_polys(e)
    except Exception: continue
    if g is None or g.is_empty: continue
    g = g.buffer(0).intersection(CORE)
    if g.is_empty or g.area < 6: continue
    rc_full = poly_mask(g)
    if rc_full is None: continue
    ground = float(np.nanpercentile(DTM[rc_full], 15))
    roofz = DSM[rc_full]; h95 = float(np.nanpercentile(roofz, 95)) - ground
    if h95 < 2.5: continue
    name = t.get("name", "")
    qid = t.get("wikidata", "")
    rc = poly_mask(g, shrink=1.0)
    f_cad, f43, f73, f37 = (frac(BM[k], rc) for k in ("cad", "m1843", "m1873", "m1937"))
    in_cov = frac(BM["cad_cov"], rc) > 0.6
    src = ["OSM footprint", "LiDAR 2023 heights"]
    lm = next((x for x in LM_RE if name and x[0].search(name)), None)
    end, phases, wiki = None, [], ""
    if lm:
        start, ramp, phases, wiki = lm[1], lm[2], lm[3], lm[4]; conf = "documented"; src.append("historiography (curated landmark list)")
    elif year(t.get("start_date")):
        start, ramp, conf = year(t.get("start_date")), 3, "documented"; src.append("OSM start_date")
    elif qid in WD and "inception" in WD[qid]:
        start, ramp, conf = WD[qid]["inception"], 5, "documented"; src.append(f"Wikidata {qid} inception")
    elif REPUBBLICA.contains(g.centroid):
        start, ramp, conf = 1890, 6, "inferred"; src.append("inside the Risanamento area (Mercato Vecchio & ghetto rebuilt 1885–95)")
    else:
        existed_1834 = (in_cov and f_cad > 0.35) or (not in_cov and f43 > 0.5)
        if existed_1834:
            start, why = zone_start(g); ramp = 10; conf = "conjectural"
            src.append("Catasto Generale Toscano 1830s" if in_cov else "Fantozzi map 1843")
            src.append(f"start estimated ({why})")
        elif f73 > 0.5:
            start, ramp, conf = 1865, 8, "inferred"; src.append("absent 1843 · present IGM 1873")
        elif f37 > 0.5:
            start, ramp, conf = 1905, 10, "inferred"; src.append("absent 1873 · present map 1937")
        else:
            start, ramp, conf = 1955, 8, "inferred"; src.append("absent on 1937 map")
    if qid in WD and "dissolved" in WD[qid]: end = WD[qid]["dissolved"]
    stats[conf] = stats.get(conf, 0) + 1
    c = g.centroid
    rid = len(REC); st = style_for(rid, "building", start, h95, g.area, name)
    bid = new_rec(kind="building", name=name, start=start, ramp=ramp, end=end, conf=conf, src=src, qid=qid, wiki=wiki,
                  ground=round(ground - BASE_Z, 2), h=round(h95, 1), phases=phases, roof="ortho",
                  c=[round(c.x - ORIGIN[0], 1), round(-(c.y - ORIGIN[1]), 1)], f=[round(f_cad, 2), round(f43, 2), round(f73, 2), round(f37, 2)],
                  style=st, rgb=roof_rgb(rc) or tile_rgb(rid))
    extrude(bid, g, ground, lambda x, y: max(float(dsm(x, y)), ground + 3.0), eave_poly=eave_zone(g), style=st,
            keep_scan=bool(lm))                                 # landmarks (domes, towers, lanterns) keep the scanned surface
    today_polys.append(g)
    if start <= 1840: old_polys.append(g)
print("today buildings", len(REC), stats)
TODAY = unary_union(today_polys)
TODAY_P = prepared.prep(TODAY.buffer(1.5))

# ================= 2. Demolished fabric: 1830s cadastre (where digitised) + 1843 map blocks elsewhere =====
STREETS = json.load(open(os.path.join(SRC, "data/raw/osm/core_streets.json"), encoding="utf-8"))["elements"]
def vectorise(mask, min_area, open_=True):
    """Mask -> list of shapely polygons (UTM)."""
    m = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) if open_ else mask.astype(np.uint8)
    cs, hier = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    out = []
    for i, c in enumerate(cs):
        if hier[0][i][3] != -1 or len(c) < 4: continue
        c = cv2.approxPolyDP(c, 1.0, True)
        if len(c) < 3: continue
        P = Polygon([(X0 + (p[0][0] + 0.5) * RES, Y1 - (p[0][1] + 0.5) * RES) for p in c]).buffer(0)
        if P.area >= min_area: out.append(P)
    return out
# today's river bed (OSM water polygons, the same as step 21): map tracings that fall in it are hatching, sandbank shading
# or bridge lines on the old maps, not buildings. Real structures over the water (bridge shops, the houses on the Grazie
# piers, mills on the weirs) are modelled explicitly from documents (landmarks, bridges.ts).
def _river_bed():
    try: WJ = json.load(open(os.path.join(SRC, "data/raw/osm/core_water.json"), encoding="utf-8"))["elements"]
    except OSError: return None
    parts = []
    for e in WJ:
        rings = [("outer", e["geometry"])] if e["type"] == "way" and len(e.get("geometry", [])) >= 4 else \
                [(m.get("role"), m["geometry"]) for m in e.get("members", []) if m.get("geometry")] if e["type"] == "relation" else []
        outs = [Polygon(utm_line(g)).buffer(0) for r_, g in rings if r_ == "outer" and len(g) >= 4 and g[0] == g[-1]]
        if not outs and e["type"] == "relation":
            from shapely.ops import polygonize, linemerge
            outs = list(polygonize(linemerge([LineString(utm_line(g)) for r_, g in rings if r_ == "outer"])))
        parts += outs
    return prepared.prep(unary_union(parts)) if parts else None, unary_union(parts) if parts else None
RIVER_BED = _river_bed() or (None, None)
SKIPPED_IN_RIVER = []

def demolished_from(mask, label, conf, individual=False, keep=None):
    """Historic buildings absent today. individual=True: mask already separates units (cadastre fill), no merging."""
    old_r = np.zeros(mask.shape, np.uint8)
    for g in old_polys:
        rc = poly_mask(g)
        if rc is not None: old_r[rc] = 1
    m = mask & (old_r == 0)
    if individual: m = m.astype(np.uint8) > 0
    else: m = cv2.erode(m.astype(np.uint8), np.ones((7, 7), np.uint8)); m = cv2.dilate(m, np.ones((7, 7), np.uint8)) > 0
    n = 0; rng = np.random.default_rng(3)
    polys_ = [P.buffer(0.9, join_style=2) for P in vectorise(m, 4, open_=False)] if individual else vectorise(m, 60)   # regrow by half the outline width
    for P in polys_:
        if individual and P.area < 15: continue
        if REPUBBLICA.contains(P.centroid) and (P.area < 30 or (P.area < 60 and P.centroid.distance(Point(ORIGIN[0] - 90, ORIGIN[1] - 14)) < 18)):
            continue   # market stalls / loggia bays of Mercato Vecchio drawn as parcels
        if P.centroid.distance(Point(ORIGIN[0] - 90, ORIGIN[1] - 14)) < 22: continue   # keep the Mercato Vecchio square open
        if RIVER_BED[1] is not None and RIVER_BED[0].intersects(P) and P.intersection(RIVER_BED[1]).area > 0.5 * P.area:
            SKIPPED_IN_RIVER.append((label[:20], round(P.centroid.x - ORIGIN[0], 1), round(-(P.centroid.y - ORIGIN[1]), 1))); continue
        # skip if it is mostly covered by a present-day building that already existed (pixel noise at shared walls)
        rc = poly_mask(P, 0.5)
        if rc is not None and old_r[rc].mean() > 0.4: continue
        f73, f37 = frac(BM["m1873"], rc), frac(BM["m1937"], rc)
        if keep is not None and not keep(P, f73): continue
        if REPUBBLICA.contains(P.centroid): end, why = 1888, "Risanamento of Mercato Vecchio and the ghetto (1885–95)"
        elif f73 < 0.3: end, why = 1868, "absent on IGM 1873 map"
        elif f37 < 0.3: end, why = 1900, "absent on 1937 map"
        else: end, why = 1944, "present 1937, gone today (war damage Aug 1944 or later)"
        start, wz = zone_start(P)
        rc2 = poly_mask(P)
        if rc2 is None: continue
        ground = float(np.nanpercentile(DTM[rc2], 15))
        h = float(rng.choice([10.5, 12.5, 14.0, 16.0, 18.0])) if individual else (14.0 if start < 1500 else 12.0)
        c = P.centroid
        bid = new_rec(kind="demolished", name="", start=start, ramp=10, end=end, conf=conf,
                      src=[label, f"start estimated ({wz})", f"end: {why}", "height: estimate (3–5 storeys)"], qid="", wiki="",
                      ground=round(ground - BASE_Z, 2), h=h, phases=[], roof="tile", c=[round(c.x - ORIGIN[0], 1), round(-(c.y - ORIGIN[1]), 1)])
        extrude(bid, P, ground, lambda x, y, gz=ground, hh=h: gz + hh, roof="hip", style=REC[bid]["style"])
        n += 1
    return n
a = MAPS["cad"].astype(int)
cad_fill = (a[..., 3] > 0) & (a[..., 0] > 200) & (a[..., 1] > 35)          # light-red fill only (dark outlines separate units)
cad_mask = cad_fill & BM["cad_cov"]
n1 = demolished_from(cad_mask, "Catasto Generale Toscano 1830s (Comune WMS, vectorised per building)", "inferred", individual=True)
# Mercato Vecchio square & Colonna dell'Abbondanza: positions verified visually on cadastre vs 2017 orthophoto (local coords)
MV = {"mercato_vecchio": [-90, 14], "colonna_abbondanza": [-96, 25]}
# 1843 Fantozzi map (mask: see built_masks): never on the wall line (drawn by the walls model), and outside the sixth circle only if the IGM 1873 map confirms a building there
# (countryside lines and hatching look like blocks after the threshold). Checked on _dev/tmp/f1843_*.jpg overlays.
m43 = BM["m1843"] & ~BM["cad_cov"]
WALL_LINE = unary_union([w[2] for w in walls if w[0] in (1284, 1333)]).buffer(12)
# today's squares (OSM place=square): a block traced only on the 1843 map in the middle of one is the market, a statue base
# or lettering, not a house (Piazza San Lorenzo is open on every view since the 18th century)
_sq = []
for e in OSM:
    t = e.get("tags", {})
    if e["type"] == "way" and t.get("place") == "square" and len(e.get("geometry", [])) >= 4:
        g_ = Polygon(utm_line(e["geometry"])).buffer(0)
        if g_.area > 200: _sq.append(g_.buffer(-3))
SQUARES = prepared.prep(unary_union(_sq)) if _sq else None
def keep43(P, f73):
    c = P.centroid; x, y = c.x - ORIGIN[0], c.y - ORIGIN[1]
    if (x * x + y * y) ** 0.5 > F43_R: return False
    if WALL_LINE.intersects(c): return False
    if SQUARES is not None and SQUARES.contains(c): return False
    return ZONE_ARNOLFO.contains(c) or f73 >= 0.3
n2 = demolished_from(m43, "Fantozzi map 1843 (Comune WMS, vectorised)", "conjectural", keep=keep43)
print("demolished: cadastre", n1, "1843", n2, "| skipped in the river bed (map hatching, not buildings):", len(SKIPPED_IN_RIVER))

# ================= 3. OpenHistoricalMap dated structures (walls, gates, towers, churches, Roman monuments) =====
CONFLICTS = []
OHM_H = {"citywalls": 11.0, "tower": 34.0, "church": 16.0, "place_of_worship": 16.0, "theatre": 14.0,
         "temple": 13.0, "building": 9.0, "castle": 18.0, "yes": 10.0}
def ohm_struct(e, kind_key, name, sy, ey):
    g = e["geometry"]; pts = utm_line(g)
    if kind_key == "citywalls" or not (len(pts) >= 4 and pts[0] == pts[-1]):
        line = LineString(pts).intersection(CORE)
        if line.is_empty: return
        thick = 2.5 if kind_key == "citywalls" else 1.2
        P = line.buffer(thick / 2, cap_style=2, join_style=2)
        h = 11.6 if (sy or 0) >= 1284 else (9.0 if (sy or 0) >= 1000 else 7.0)
        if kind_key != "citywalls": h = 1.0
    else:
        P = Polygon(pts).buffer(0).intersection(CORE)
        if P.is_empty or P.area < 6: return
        h = OHM_H.get(kind_key, 10.0)
        if kind_key == "theatre" or "amphitheatr" in name.lower():
            P = P.difference(P.buffer(-14))   # cavea ring
    if P.intersects(Point(ORIGIN[0] - 90, ORIGIN[1] - 14).buffer(12)):   # overlaps the open Mercato Vecchio square of the 1830s cadastre
        print("OHM polygon skipped (conflicts with cadastre / open Mercato Vecchio):", name); CONFLICTS.append(name); return
    rc = poly_mask(P)
    if rc is None: return
    ground = float(np.nanpercentile(DTM[rc], 15))
    phases = [[1250, -29.0]] if kind_key == "tower" else []    # tower heights capped (~50 braccia) by the Primo Popolo c.1250
    c = P.centroid
    bid = new_rec(kind="ohm", name=name or kind_key, start=sy if sy is not None else 1200, ramp=4 if kind_key != "citywalls" else 12,
                  end=ey, conf="inferred", src=["OpenHistoricalMap (CC0)", "height: typology estimate"], qid=e.get("tags", {}).get("wikidata", ""),
                  wiki="", ground=round(ground - BASE_Z, 2), h=h, phases=phases, roof="tile", sub=kind_key,
                  c=[round(c.x - ORIGIN[0], 1), round(-(c.y - ORIGIN[1]), 1)])
    extrude(bid, P, ground, lambda x, y, gz=ground, hh=h: gz + hh, roof="flat")
for e in OHM:
    t = e.get("tags", {})
    if e["type"] != "way" or not t: continue
    k = t.get("historic") or t.get("building") or t.get("amenity") or t.get("man_made") or ""
    if k in ("citywalls", "tower", "church", "place_of_worship", "theatre", "temple", "castle") or (t.get("building") in ("yes",) and (t.get("start_date") or "")[:1] == "0") or t.get("name") in ("Thermae", "Amphitheatrum", "domūs syriacōrum mercatorium"):
        sy, ey = year(t.get("start_date")), year(t.get("end_date"))
        if sy is None and ey is None: continue
        ohm_struct(e, k if k else "building", t.get("name", ""), sy, ey)
# gates (nodes) as towers
for e in OHM:
    t = e.get("tags", {})
    if e["type"] == "node" and t.get("historic") == "city_gate":
        x, y = T_WGS_UTM.transform(e["lon"], e["lat"])
        if not CORE.contains(Point(x, y)): continue
        sy, ey = year(t.get("start_date")), year(t.get("end_date"))
        P = Point(x, y).buffer(6, cap_style=3)
        ground = float(dtm(x, y)); h = 28.0 if (sy or 1300) >= 1284 else 14.0
        bid = new_rec(kind="gate", name=t.get("name", "Porta"), start=sy if sy is not None else 1284, ramp=5, end=ey, conf="inferred",
                      src=["OpenHistoricalMap (CC0)", "gate tower size: typology estimate"], qid="", wiki="", ground=round(ground - BASE_Z, 2),
                      h=h, phases=[[1527, -16.0]] if h > 20 else [], roof="tile", sub="city_gate",   # gate towers lowered c.1526–29 for the siege
                      c=[round(x - ORIGIN[0], 1), round(-(y - ORIGIN[1]), 1)])
        extrude(bid, P, ground, lambda xx, yy, gz=ground, hh=h: gz + hh, roof="flat")

# ================= 4. Roman Florentia from Comune excavation data (scavi_linee: Romano) ===================
z = zipfile.ZipFile(os.path.join(SRC, "data/raw/comune/dati_archeologici_del_centro_storico_di_firenze.zip"))
nm = z.namelist(); g_ = lambda b, ext: io.BytesIO(z.read([n for n in nm if n.lower() == (b + ext).lower()][0]))
r = shapefile.Reader(shp=g_("scavi_linee", ".shp"), dbf=g_("scavi_linee", ".dbf"), encoding="latin-1")
ROMAN_H = {"domus": 5.0, "terme": 7.0, "porta/cinta muraria": 7.5, "basilica paleocristiana/chiesa": 9.0, "edificio abitativo": 5.0,
           "fullonica/edificio produttivo": 4.5, "edificio non determinabile": 4.0, "teatro": 12.0, "anfiteatro": 12.0, "tempio": 11.0}
groups = {}
for shp, rec in zip(r.shapes(), r.records()):
    per = (rec["periodo_ve"] or "").strip(); d = (rec["definizion"] or "").strip()
    if per != "Romano" or d.startswith("area cimiteriale") or d.startswith("strada"): continue
    xs = [T_3003_UTM.transform(x, y) for x, y in shp.points]
    if len(xs) < 2: continue
    groups.setdefault(d, []).append(LineString(xs))
nroman = 0
for d, ls in groups.items():
    G = unary_union([l.buffer(0.35, cap_style=2) for l in ls]).intersection(CORE)
    if G.is_empty: continue
    h = ROMAN_H.get(d, 4.0)
    rc = poly_mask(G)
    if rc is None: continue
    ground = float(np.nanpercentile(DTM[rc], 10))   # shown on today's ground; the Roman level is ~2–3 m lower
    c = G.centroid
    bid = new_rec(kind="roman", name=f"Roman {d}", start=-30, ramp=30, end=550, conf="inferred",
                  src=["Comune di Firenze – Dati archeologici del centro storico (excavated wall traces)", "height: typology estimate", "shown on today's ground; Roman street level was ~2–3 m lower"],
                  qid="", wiki="Florentia (città romana)", ground=round(ground - BASE_Z, 2), h=h, phases=[], roof="tile", sub=d,
                  c=[round(c.x - ORIGIN[0], 1), round(-(c.y - ORIGIN[1]), 1)])
    extrude(bid, G, ground, lambda x, y, gz=ground, hh=h: gz + hh, roof="flat"); nroman += 1
print("roman groups", nroman)

# ================= 4b. Conjectural Roman insulae inside the castrum (orthogonal grid on cardo/decumanus) ======
# Castrum from OpenHistoricalMap walls (EPSG:25832): W 681195 · E 681720 · S 4848795 · N 4849180; cardo x≈681445, decumanus y≈4848965
CW, CE, CS, CN, CARDO, DECU = 681200.0, 681715.0, 4848800.0, 4849175.0, 681445.0, 4848965.0
BLK, STR = 40.0, 5.0
forum = box(CARDO - 55, DECU - 40, CARDO + 55, DECU + 40)
monuments = unary_union([Polygon(utm_line(e["geometry"])).buffer(4) for e in OHM if e["type"] == "way" and len(e.get("geometry", [])) >= 4
                         and e["geometry"][0] == e["geometry"][-1] and (year(e.get("tags", {}).get("start_date")) or 9999) < 600])
rng = np.random.default_rng(7); nins = 0
xs = np.concatenate([np.arange(CARDO + STR / 2, CE, BLK + STR), np.arange(CARDO - STR / 2 - BLK, CW - BLK, -(BLK + STR))])
ys = np.concatenate([np.arange(DECU + STR / 2, CN, BLK + STR), np.arange(DECU - STR / 2 - BLK, CS - BLK, -(BLK + STR))])
for bx in xs:
    for by in ys:
        B = box(bx, by, bx + BLK, by + BLK).intersection(box(CW + 3, CS + 3, CE - 3, CN - 3))
        if B.area < 300 or B.intersects(forum): continue
        B = B.difference(monuments)
        if B.is_empty or B.area < 200: continue
        # split block into 2–4 houses, each with a courtyard (atrium/peristyle)
        n = int(rng.integers(2, 5)); minx, miny, maxx, maxy = B.bounds; w = (maxx - minx) / n
        for k in range(n):
            U = B.intersection(box(minx + k * w + 0.6, miny, minx + (k + 1) * w - 0.6, maxy))
            if U.is_empty or U.area < 80: continue
            cx_, cy_ = U.centroid.x, U.centroid.y
            court = box(cx_ - w * 0.22, cy_ - BLK * 0.2, cx_ + w * 0.22, cy_ + BLK * 0.2)
            U = U.difference(court) if U.area > 260 else U
            ground = float(dtm(cx_, cy_)); h = float(rng.choice([6.0, 7.0, 8.5]))
            bid = new_rec(kind="roman", name="Roman house (insula)", start=-30, ramp=60, end=550, conf="conjectural",
                          src=["layout conjectural: orthogonal castrum grid aligned on cardo/decumanus (OpenHistoricalMap)", "size & height: typology estimate"],
                          qid="", wiki="Florentia (città romana)", ground=round(ground - BASE_Z, 2), h=h, phases=[], roof="tile", sub="domus / insula",
                          c=[round(cx_ - ORIGIN[0], 1), round(-(cy_ - ORIGIN[1]), 1)])
            extrude(bid, U, ground, lambda x, y, gz=ground, hh=h: gz + hh, roof="hip", style=REC[bid]["style"]); nins += 1
print("roman insulae", nins)

# ================= write =================
os.makedirs(OUT, exist_ok=True)
pos = np.concatenate(POS); nrm = np.concatenate(NRM); bid = np.concatenate(BID); fu = np.concatenate(FU); fv = np.concatenate(FV); idx = np.concatenate(IDX).ravel()
nrm8 = np.clip(np.round(nrm * 127), -127, 127).astype(np.int8)
nrm8 = np.concatenate([nrm8, np.zeros((len(nrm8), 1), np.int8)], 1)
for nmn, arr in (("pos", pos.astype(np.float32)), ("nrm", nrm8), ("bid", bid.astype(np.float32)), ("fu", fu.astype(np.float32)), ("fv", fv.astype(np.float32)), ("idx", idx.astype(np.uint32))):
    os.makedirs(MESH, exist_ok=True); arr.tofile(os.path.join(MESH, f"structures.{nmn}.bin"))
FOOT.tofile(os.path.join(OUT, "footprints.u16"))      # 2 × rows × cols uint16, row 0 = north edge (Y1), 2 m cells
save_json("structures.json", {"places": MV, "conflicts": CONFLICTS, "count": len(REC), "verts": int(len(pos)), "tris": int(len(idx) // 3), "items": REC})
print("verts", len(pos), "tris", len(idx) // 3, "records", len(REC), "roofs", ROOF_STATS)
