"""Shared constants/helpers for the Firenze Story build pipeline."""
import os, json, numpy as np
from pyproj import Transformer
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))   # firenze-story/
SRC = os.environ.get("FS_SRC", os.path.join(ROOT, "_dev"))                  # work cache (gitignored): _dev/data/raw, _dev/data/processed
OUT = os.environ.get("FS_OUT", os.path.join(ROOT, "web", "public", "data"))
BUILD = os.environ.get("FS_BUILD", os.path.join(ROOT, "_dev", "data", "build"))  # intermediate rasters (regenerable)
MESH = os.path.join(BUILD, "city")   # the merged city mesh structures.*.bin (input of 23_city_tiles.py; not deployed: the app loads tiles)
# Study area (EPSG:25832, ETRS89 / UTM 32N): a square of +-CORE_HALF m around the origin (Cascine to Piazza Ferrucci,
# Ponte alla Vittoria to Ponte San Niccolo). LiDAR 500 m tiles are fetched for the enclosing tile grid and cropped.
ORIGIN = (681500.0, 4849000.0)      # local scene origin (three.js x=E, z=-N)
CORE_HALF = 1800.0
X0, Y0, X1, Y1 = ORIGIN[0] - CORE_HALF, ORIGIN[1] - CORE_HALF, ORIGIN[0] + CORE_HALF, ORIGIN[1] + CORE_HALF
LIDAR_BBOX = tuple(int(v // 500 * 500) for v in (X0, Y0)) + tuple(int(-(-v // 500) * 500) for v in (X1, Y1))
def wgs_bbox(pad=0.002):
    """(S, W, N, E) in WGS84 enclosing the study area, padded in degrees (for Overpass / WMS / Wikidata queries)."""
    lon, lat = T_UTM_WGS.transform([X0, X1, X0, X1], [Y0, Y0, Y1, Y1])
    return min(lat) - pad, min(lon) - pad, max(lat) + pad, max(lon) + pad
BASE_Z = 40.0                       # metres a.s.l. subtracted from all heights
T_UTM_WGS = Transformer.from_crs(25832, 4326, always_xy=True)
T_WGS_UTM = Transformer.from_crs(4326, 25832, always_xy=True)
T_UTM_3857 = Transformer.from_crs(25832, 3857, always_xy=True)
T_3003_UTM = Transformer.from_crs(3003, 25832, always_xy=True)

def load_grid(kind):
    """Mosaic LiDAR 0.5 m tiles of the core into one array (north-up, row 0 = Y1). kind = dsm|dtm"""
    tx0, ty0, tx1, ty1 = LIDAR_BBOX
    m = int((tx1 - tx0) / 0.5)
    g = np.full((int((ty1 - ty0) / 0.5), m), np.nan, np.float32)
    d = os.path.join(SRC, "data", "processed", "lidar2023", kind)
    for x in range(tx0, tx1, 500):
        for y in range(ty0, ty1, 500):
            z = np.load(os.path.join(d, f"32_{x}_{y}.npz"))["z"]
            r0 = int((ty1 - (y + 500)) / 0.5); c0 = int((x - tx0) / 0.5)
            g[r0:r0 + 1000, c0:c0 + 1000] = z
    r, c = int((ty1 - Y1) / 0.5), int((X0 - tx0) / 0.5); n = int((X1 - X0) / 0.5)
    return np.ascontiguousarray(g[r:r + n, c:c + n])

class Grid:
    """Sample a north-up raster covering the core at resolution res (m)."""
    def __init__(self, arr, res): self.a, self.res = arr, res
    def rc(self, x, y):
        c = ((np.asarray(x) - X0) / self.res).astype(int); r = ((Y1 - np.asarray(y)) / self.res).astype(int)
        h, w = self.a.shape[:2]
        return np.clip(r, 0, h - 1), np.clip(c, 0, w - 1)
    def __call__(self, x, y):
        r, c = self.rc(x, y); return self.a[r, c]

def resample_3857(png_path, res=0.5, interp=None):
    """Resample a Web-Mercator mosaic (+ .pgw) onto the core UTM grid at `res` m/px -> RGBA uint8 array."""
    import cv2
    from PIL import Image
    im = np.array(Image.open(png_path).convert("RGBA"))
    a, _, _, e, cx, cy = [float(v) for v in open(png_path[:-4] + ".pgw").read().split()]
    n = int((X1 - X0) / res)
    xs = X0 + (np.arange(n) + 0.5) * res; ys = Y1 - (np.arange(n) + 0.5) * res
    XX, YY = np.meshgrid(xs, ys)
    mx, my = T_UTM_3857.transform(XX.ravel(), YY.ravel())
    mapx = ((np.array(mx) - cx) / a).reshape(n, n).astype(np.float32)
    mapy = ((np.array(my) - cy) / e).reshape(n, n).astype(np.float32)
    return cv2.remap(im, mapx, mapy, interp if interp is not None else cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))

def to_local(x, y, z):
    """UTM + elevation -> three.js local coords (x east, y up, z south)."""
    return np.asarray(x) - ORIGIN[0], np.asarray(z) - BASE_Z, -(np.asarray(y) - ORIGIN[1])

def save_json(name, obj):
    os.makedirs(OUT, exist_ok=True)
    json.dump(obj, open(os.path.join(OUT, name), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
