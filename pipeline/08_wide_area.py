"""Wide area around the LiDAR core (12 x 12 km, centred on the scene origin) so the city sits in its real landscape:
  - DEM  : Copernicus GLO-30 (30 m, tile N43E011)            -> _dev/data/raw/wide/cop30_N43E011.tif   (free, attribution)
  - land : Sentinel-2 cloudless 2016 by EOX (z14 WMTS)      -> _dev/data/raw/wide/s2_z14.jpg + .json  (CC BY 4.0)
  - water: OSM Arno / water polygons + weirs in the wide bbox -> _dev/data/raw/osm/wide_{water,weirs}.json (ODbL)
Re-run safe: existing files are kept.  Needs: tifffile imagecodecs (DEM), pillow, pyproj."""
import os, sys, json, math, time, urllib.request, urllib.parse, io
sys.path.insert(0, os.path.dirname(__file__))
from common import *
from PIL import Image

D = os.path.join(SRC, "data", "raw", "wide"); os.makedirs(D, exist_ok=True)
HALF = 6000.0
WX0, WY0, WX1, WY1 = ORIGIN[0] - HALF, ORIGIN[1] - HALF, ORIGIN[0] + HALF, ORIGIN[1] + HALF
UA = {"User-Agent": "firenze-story/0.2 (non-commercial cultural project)"}

def overpass(q):
    for k in range(6):
        url = ("https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter")[k % 2]
        try:
            req = urllib.request.Request(url, data=urllib.parse.urlencode({"data": q}).encode(), headers=UA)
            return json.load(urllib.request.urlopen(req, timeout=300))
        except Exception as ex: print("overpass retry", url, ex); time.sleep(5 * (k + 1))
    raise RuntimeError("overpass unavailable")

def get(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 0: return
    for k in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r: open(path, "wb").write(r.read()); return
        except Exception as e: print("retry", url, e); time.sleep(3 * (k + 1))
    raise RuntimeError(url)

# ---- DEM ----
get("https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N43_00_E011_00_DEM/Copernicus_DSM_COG_10_N43_00_E011_00_DEM.tif",
    os.path.join(D, "cop30_N43E011.tif"))

# ---- Sentinel-2 cloudless mosaic (Web Mercator z14 tiles) ----
Z = 14; N = 2 ** Z
lon0, lat0 = T_UTM_WGS.transform(WX0, WY0); lon1, lat1 = T_UTM_WGS.transform(WX1, WY1)
def tile(lon, lat):
    x = (lon + 180) / 360 * N; y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * N
    return x, y
tx0, ty0 = tile(min(lon0, lon1) - 0.01, max(lat0, lat1) + 0.01); tx1, ty1 = tile(max(lon0, lon1) + 0.01, min(lat0, lat1) - 0.01)
tx0, ty0, tx1, ty1 = int(tx0), int(ty0), int(tx1), int(ty1)
out = os.path.join(D, "s2_z14.jpg")
if not os.path.exists(out):
    W, H = (tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256; mos = Image.new("RGB", (W, H))
    for ty in range(ty0, ty1 + 1):
        for tx in range(tx0, tx1 + 1):
            p = os.path.join(D, f"s2_{Z}_{tx}_{ty}.jpg")
            get(f"https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless_3857/default/g/{Z}/{ty}/{tx}.jpg", p)
            mos.paste(Image.open(p).convert("RGB"), ((tx - tx0) * 256, (ty - ty0) * 256))
    mos.save(out, quality=92)
    json.dump({"z": Z, "tx0": tx0, "ty0": ty0, "tx1": tx1, "ty1": ty1}, open(out[:-4] + ".json", "w"))
print("s2 tiles", (tx1 - tx0 + 1) * (ty1 - ty0 + 1))

# ---- OSM water (wide) ----
ow = os.path.join(SRC, "data", "raw", "osm", "wide_water.json")
if not os.path.exists(ow):
    s, w = min(lat0, lat1), min(lon0, lon1); n, e = max(lat0, lat1), max(lon0, lon1)
    q = f"""[out:json][timeout:180];(way["natural"="water"]({s},{w},{n},{e});relation["natural"="water"]({s},{w},{n},{e});
            way["waterway"="riverbank"]({s},{w},{n},{e});relation["waterway"="riverbank"]({s},{w},{n},{e}););out geom;"""
    json.dump(overpass(q), open(ow, "w"))
print("wide water", len(json.load(open(ow))["elements"]))

# ---- OSM weirs (pescaie) and dams in the wide bbox ----
owr = os.path.join(SRC, "data", "raw", "osm", "wide_weirs.json")
if not os.path.exists(owr):
    s, w = min(lat0, lat1), min(lon0, lon1); n, e = max(lat0, lat1), max(lon0, lon1)
    q = f"""[out:json][timeout:120];(way["waterway"~"weir|dam"]({s},{w},{n},{e}););out geom;"""
    json.dump(overpass(q), open(owr, "w"))
print("weirs", [(e.get("tags", {}).get("name"), e["tags"].get("waterway")) for e in json.load(open(owr))["elements"]])
