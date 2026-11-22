"""Addresses for the inspector card: street name in every era, today's house number, the 1808 French number.

Inputs (H20–H22 in docs/DATA-SOURCES.md, Comune di Firenze open data, CC-BY 4.0, EPSG:3003):
  _dev/data/raw/comune/stradario_storico.geojson   streets with dated name attestations (STORIA) and name origin
  _dev/data/raw/comune/civici_shp.zip              today's house numbers (point per civico, street code)
  _dev/data/raw/comune/civici_francesi_shp.zip     Napoleonic city-wide numbering (1808), historic address, cadastre,
                                                    owner, scans of the documents
  web/public/data/structures.json                  record centroids (step 20)
Output: web/public/data/addresses.json
  streets: code -> {n: today's name, o: origin of the name, since: first year the present name is attested,
                    h: [[year, text, ref], …] dated attestations}
  recs:    record id -> {s: street code, no: [house numbers], fr: [[n, historic address, attestation, [scan urls]], …]}
Each house number belongs to one building (nearest OSM footprint within 6 m); records without a footprint take the
numbers within 24 m of their centroid, French numbers within 16 m, otherwise the nearest street line within 30 m.
recs.pos / alt[i][2] = [metres along the street axis, side (-1 left, +1 right), frontage width] for the strip view.
"""
import os, sys, json, re, io, zipfile, unicodedata, math
import numpy as np
from pyproj import Transformer
from scipy.spatial import cKDTree
import shapefile
from shapely.geometry import shape, Point
from shapely.strtree import STRtree
sys.path.insert(0, os.path.dirname(__file__))
from common import ROOT
RAW = os.path.join(ROOT, "_dev", "data", "raw", "comune")
OUT = os.path.join(ROOT, "web", "public", "data")
T = Transformer.from_crs(3003, 25832, always_xy=True)
def scene(x, y):
    e, n = T.transform(x, y); return e - 681500.0, -(n - 4849000.0)

PARTICLES = {"dell", "nell", "sull", "all", "dall", "di", "de", "dei", "del", "della", "delle", "dello", "degli", "da", "dal", "dalla", "dai", "e", "in", "al", "alla",
             "alle", "allo", "ai", "agli", "a", "sul", "sulla", "per", "fra", "tra", "d", "l", "de'", "d'", "l'"}
def pretty(s):
    out = []
    for i, w in enumerate(s.lower().split()):
        parts = re.split(r"(['’])", w)
        w2 = "".join(p if p in ("'", "’") else (p if (i > 0 and p in PARTICLES) else p[:1].upper() + p[1:]) for p in parts)
        out.append(w2)
    return " ".join(out)
def fold(s): return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()

ATT = re.compile(r"(?:^|;)\s*((?:av\.|d\.|c\.|ca\.|post|ante)?\s*(\d{3,4})(?:/\d{1,4})?)\s*:\s*(\([^)]*\))?\s*(.*?)\s*\(Attestazione[^)]*\)", re.S)
def attestations(storia):
    out = []
    for m in ATT.finditer(storia or ""):
        yr = int(m.group(2)); ref = (m.group(3) or "").strip("() ")
        txt = re.sub(r"\s*\n\s*", " / ", m.group(4)).strip(" ;")
        txt = re.sub(r"\s+", " ", txt)
        if txt: out.append([yr, txt[:160], ref[:40]])
    out.sort(key=lambda a: a[0]); return out

# ---------- streets ----------
G = json.load(open(os.path.join(RAW, "stradario_storico.geojson"), encoding="utf-8", errors="replace"))
streets, lines, line_code = {}, [], []
for f in G["features"]:
    p = f["properties"]; code = p["FK_STRADE"]
    if code not in streets:
        name = pretty(p["TOPONIMO"] or "")
        h = attestations(p.get("STORIA"))
        key = [w for w in re.findall(r"[a-zà-ù']{4,}", fold(name)) if w not in ("piazza", "borgo", "lungarno", "piazzale", "viale", "vicolo", "chiasso", "costa")]
        since = next((a[0] for a in h if key and fold(a[1]).find(key[-1]) >= 0), h[-1][0] if h else None)
        streets[code] = {"n": name, "o": (p.get("ORIGINE_NOME") or "")[:400], "since": since, "h": h}
    try:
        g = shape(f["geometry"])
        segs = g.geoms if g.geom_type == "MultiLineString" else [g]
        for sgm in segs:
            from shapely.geometry import LineString
            lines.append(LineString([scene(x, y) for x, y in sgm.coords])); line_code.append(code)
    except Exception:
        pass
tree = STRtree(lines)
print("streets", len(streets), "segments", len(lines))

# ---------- house numbers ----------
def read_zip_shp(path):
    Z = zipfile.ZipFile(path); base = [n[:-4] for n in Z.namelist() if n.lower().endswith(".shp")][0]
    return shapefile.Reader(shp=io.BytesIO(Z.read(base + ".shp")), dbf=io.BytesIO(Z.read(base + ".dbf")), encoding="latin-1")
R = read_zip_shp(os.path.join(RAW, "civici_shp.zip"))
civ_xy, civ = [], []
for sr in R.iterShapeRecords():
    if not sr.shape.points: continue
    x, z = scene(*sr.shape.points[0])
    if abs(x) > 1100 or abs(z) > 1100: continue                     # core area only
    d = sr.record.as_dict(); civ_xy.append((x, z)); civ.append((d["CODICESTRA"], d["NUMEROCIVI"], d.get("TIPO", "N")))
civ_tree = cKDTree(np.array(civ_xy)); print("civici in core", len(civ))
F = read_zip_shp(os.path.join(RAW, "civici_francesi_shp.zip"))
fr_xy, fr = [], []
for sr in F.iterShapeRecords():
    if not sr.shape.points: continue
    d = sr.record.as_dict(); x, z = scene(*sr.shape.points[0])
    urls = re.findall(r'href="([^"]+)"', d.get("Allegati") or "")
    num = f'{d["NumeroFran"]}{d.get("Esponente") or ""}'
    fr_xy.append((x, z)); fr.append([num, d.get("Indirizzo") or "", (d.get("Attestazio") or "")[:300], urls[:3], d.get("SorgenteAt") or ""])
fr_tree = cKDTree(np.array(fr_xy)); print("french numbers", len(fr))

# ---------- OSM footprints (the same source as the records): house numbers inside the building, 4 m buffer ----------
from shapely.geometry import Polygon
T84 = Transformer.from_crs(4326, 25832, always_xy=True)
OSM = json.load(open(os.path.join(ROOT, "_dev", "data", "raw", "osm", "core_osm.json"), encoding="utf-8"))["elements"]
foot = []
for e in OSM:
    if e["type"] != "way" or "geometry" not in e or "building" not in e.get("tags", {}): continue
    pts = []
    for g in e["geometry"]:
        x, y = T84.transform(g["lon"], g["lat"]); pts.append((x - 681500.0, -(y - 4849000.0)))
    if len(pts) >= 4:
        try:
            P = Polygon(pts).buffer(0)
            if P.area > 4: foot.append(P)
        except Exception: pass
foot_tree = cKDTree(np.array([[P.centroid.x, P.centroid.y] for P in foot]))
print("osm footprints", len(foot))

def numkey(n):
    m = re.match(r"\d+", n); return (int(m.group()) if m else 0, n)

# every street of the core goes into the search index, with a point on it (middle of its longest stretch in the core)
CORE = 1000.0
used = set()
best = {}
for g, code in zip(lines, line_code):
    minx, miny, maxx, maxy = g.bounds
    if maxx < -CORE or minx > CORE or maxy < -CORE or miny > CORE: continue
    if g.length > best.get(code, (0, None))[0]: best[code] = (g.length, g)
for code, (L, g) in best.items():
    m = g.interpolate(0.5, normalized=True); streets[code]["c"] = [round(m.x, 1), round(m.y, 1)]; used.add(code)
# street geometry for the map highlight (core part, simplified to 1 m) and a merged centre line for the strip view
from shapely.ops import linemerge
from shapely.geometry import MultiLineString, box as sbox
CORE_BOX = sbox(-CORE, -CORE, CORE, CORE)
geom = {}
for g, code in zip(lines, line_code):
    if code in best: geom.setdefault(code, []).append(g.intersection(CORE_BOX))
axis = {}
for code, gs in geom.items():
    parts = [p for g in gs for p in (g.geoms if hasattr(g, "geoms") else [g]) if p.length > 0.5]
    if not parts: continue
    streets[code]["g"] = [[[round(x, 1), round(y, 1)] for x, y in p.simplify(1.0).coords] for p in parts]
    merged = linemerge(MultiLineString(parts))
    axis[code] = max(merged.geoms, key=lambda q: q.length) if hasattr(merged, "geoms") else merged

# ---------- records ----------
# Each house number goes to ONE building: the footprint nearest to the number's point (within 6 m). Records built
# from the same footprint (successive phases) share it. Records without a footprint fall back to nearby numbers.
S = json.load(open(os.path.join(OUT, "structures.json"), encoding="utf-8"))
items = [r for r in S["items"] if r["kind"] != "roman"]
rec_foot = {}
for r in items:
    d, j = foot_tree.query(r["c"])
    if d < 3.0: rec_foot[r["id"]] = int(j)
fp_ids = sorted(set(rec_foot.values())); fp_tree = STRtree([foot[j] for j in fp_ids])
civ_of_foot = {}
for i, (x, z) in enumerate(civ_xy):
    k = fp_tree.query_nearest(Point(x, z), max_distance=6.0)
    if len(k): civ_of_foot.setdefault(fp_ids[int(k[0])], []).append(i)

def label(i):
    n = civ[i][1].strip(); return n + "r" if civ[i][2] == "R" and not n.lower().endswith("r") else n

def place(code, pts, cx, cz, j):
    """position along the street axis, side (from the house-number points, which sit on the facade), frontage"""
    ax = axis[code]; px = sum(p[0] for p in pts) / len(pts); pz = sum(p[1] for p in pts) / len(pts)
    along = ax.project(Point(px, pz)); p0 = ax.interpolate(max(along - 1, 0)); p1 = ax.interpolate(min(along + 1, ax.length))
    tx, tz = p1.x - p0.x, p1.y - p0.y; tl = math.hypot(tx, tz) or 1; tx, tz = tx / tl, tz / tl
    q = ax.interpolate(along); side = 1 if ((cx if j is None else px) - q.x) * tz - ((cz if j is None else pz) - q.y) * tx > 0 else -1
    width = 8.0
    if j is not None:
        xs = [(x - px) * tx + (y - pz) * tz for x, y in foot[j].exterior.coords]; width = max(xs) - min(xs)
        along = ax.project(Point(foot[j].centroid.x, foot[j].centroid.y)) if width < 60 else along
    return [round(along, 1), side, round(min(max(width, 3.0), 120.0), 1)]

recs = {}
for r in items:
    cx, cz = r["c"]; out = {}; j = rec_foot.get(r["id"])
    big = bool(r.get("name")) or r.get("h", 0) > 25
    if j is not None: cand = civ_of_foot.get(j, [])
    elif big:                                      # landmark without a simple footprint (e.g. OSM relation): piazza first
        cand = civ_tree.query_ball_point((cx, cz), 75.0)
    else:                                          # no modern footprint (gone or conjectural): nearest number only
        d1, i1 = civ_tree.query((cx, cz)); cand = [int(i1)] if d1 < 24.0 else []
        if cand: out["ap"] = 1
    if cand:
        by = {}
        for i in cand: by.setdefault(civ[i][0], []).append(i)
        near = min(cand, key=lambda i: (civ_xy[i][0] - cx) ** 2 + (civ_xy[i][1] - cz) ** 2)
        def rank(code):
            nm = streets.get(code, {}).get("n", ""); black = [civ[i][1] for i in by[code] if civ[i][2] != "R"]
            if big: return (0 if nm.startswith("Piazza") else 1, min((numkey(b) for b in black), default=(9999, "")), -len(by[code]))
            return (0 if black else 1, -len(by[code]), 0 if code == civ[near][0] else 1)
        order = sorted(by, key=rank)
        def nums(code): return sorted({label(i) for i in by[code]}, key=numkey)[:8]
        def pos(code): return place(code, [civ_xy[i] for i in by[code]], cx, cz, j) if code in axis else None
        out["s"] = order[0]; out["no"] = nums(order[0]) if j is not None or not big else []   # landmark: street only, numbers nearby are the neighbours'
        p = pos(order[0])
        if p: out["pos"] = p
        if len(order) > 1 and (j is not None or not big): out["alt"] = [[c, nums(c)] + ([pos(c)] if pos(c) else []) for c in order[1:3]]
        for c in order[:3]: used.add(c)
    else:
        near = tree.query_nearest(Point(cx, cz), max_distance=60.0 if big else 30.0)
        if len(near):
            out["s"] = line_code[int(near[0])]
            if out["s"] in axis: out["pos"] = place(out["s"], [(cx, cz)], cx, cz, None)
    fi = fr_tree.query_ball_point((cx, cz), 16.0)
    if fi:
        fi.sort(key=lambda i: (fr_xy[i][0] - cx) ** 2 + (fr_xy[i][1] - cz) ** 2)
        seen = []; out["fr"] = [fr[i] for i in fi if not (fr[i][0] in seen or seen.append(fr[i][0]))][:2]
    if out:
        recs[r["id"]] = out
        if "s" in out: used.add(out["s"])
streets = {k: v for k, v in streets.items() if k in used}
print("streets in the search index", sum(1 for v in streets.values() if "c" in v))
json.dump({"streets": streets, "recs": recs, "note": "Comune di Firenze open data (CC-BY 4.0): Stradario storico, Civici, Numeri Civici Francesi"},
          open(os.path.join(OUT, "addresses.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("records with address", len(recs), "streets", len(streets), "with french number", sum(1 for v in recs.values() if "fr" in v))
