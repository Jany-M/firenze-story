"""Piazzale Michelangelo: the ground pieces of the model (v1, 2026-11-27) from the Comune's circulation areas.

In:  blender/data/piazzale_walls.json (walls snapped to the LiDAR, _dev/tmp/wall_snap.py); the Comune's pedestrian and
     carriageway polygons (S02 viabilità, _dev/data/raw/comune); the fountain before the Loggia (OSM way 1093617565)
Out: blender/data/piazzale_ground.json, read by blender/scripts/build_piazzale.py:
  pave    the terrace's ground: inside its walls, less the carriageway that runs round its south side (Viale Galileo into
          Viale Michelangiolo, Comune polygon 3717, left to the app's streets) and less the monument's platform
  ramps   Viale Poggi where it climbs to the terrace along the city side and goes down again (Comune polygon 1165, the
          stretch between the terrace's north walls and the walls below)
  island  the garden between the carriageway and the Loggia's terrace wall: gravel paths (Comune polygon 812), its beds
          (the polygon's holes) and the oval fountain
"""
import os, io, json, zipfile, shapefile
from shapely.geometry import Polygon, Point, box, MultiPolygon
from shapely.ops import unary_union
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
O = json.load(open(os.path.join(ROOT, "web", "public", "data", "meta.json")))["origin_utm"]
W = json.load(open(os.path.join(ROOT, "blender", "data", "piazzale_walls.json")))
def comune(zn, base):
    Z = zipfile.ZipFile(os.path.join(ROOT, "_dev", "data", "raw", "comune", zn)); r = shapefile.Reader(shp=io.BytesIO(Z.read(base + ".shp")), dbf=io.BytesIO(Z.read(base + ".dbf")))
    out = []
    for sr in r.iterShapeRecords():
        pts = sr.shape.points; parts = list(sr.shape.parts) + [len(pts)]
        rings = [[(x - O[0], -(y - O[1])) for x, y in pts[a:b]] for a, b in zip(parts[:-1], parts[1:])]
        P = Polygon(rings[0], rings[1:]); out.append(P if P.is_valid else P.buffer(0))
    return out
PED = comune("viabilit_area_di_circolazione_pedonale_con_geometria_polygon.zip", "acPed_s")
VEI = comune("viabilit_area_di_circolazione_veicolare_con_geometria_polygo.zip", "acVei_s")
def find(L, x, z):
    c = [P for P in L if P.contains(Point(x, z))]
    return min(c, key=lambda P: P.area) if c else None
ROAD = next(P for P in VEI if abs(P.bounds[0] - 753.6) < 1 and abs(P.bounds[2] - 1123.5) < 1)   # the carriageway round the south side (Viale Galileo – Viale Michelangiolo)
VIALE = max((P for P in VEI if P.intersects(box(780, 915, 880, 950))), key=lambda P: P.intersection(box(745, 900, 905, 960)).area)   # Viale Poggi along the city side
PATHS = find(PED, 790, 1030)                 # the garden's paths before the Loggia
wl = lambda n, f=lambda p: True: [(p[0], p[1]) for p in W[n]["pts"] if f(p)]
SX0, SZ0, SZ1 = 736.5, 955.5, 967.5          # the great staircase's head (build_piazzale.py)
terr = Polygon(wl("north_w") + wl("north_step") + wl("north_e") + wl("east", lambda p: p[1] < 1040) + [(895, 1050), (760, 1050), (745, 1014)] +
               wl("west_s", lambda p: p[1] < 1004)[::-1] + [(SX0, SZ1), (SX0, SZ0)] + wl("west_n")[::-1]).buffer(0)
MON = Point(818.5, 976.5).buffer(6.6, 24)
pave = terr.difference(ROAD.buffer(0.2)).difference(MON)
pave = max(getattr(pave, "geoms", [pave]), key=lambda g: g.area)      # the terrace (bits south of the road dropped)
# The two ramps of Viale Poggi that meet the terrace on the city side, read off the 0.5 m LiDAR (Jany's Street View
# checks, 2026-11-27): west of the step the road climbs along the outside of the city-side wall, ≈ 6 m wide, from 56 m at
# x 770 to the terrace's level at x ≈ 810; east of it it goes down again, 10–15 m wide, to 54 m at x 900. Each ramp runs
# from the wall's line out to where the ground drops more than a metre below its level (sampled every 2 m along the wall).
import numpy as np
DTM = np.load(os.path.join(ROOT, "blender", "data", "piazzale_dtm.npy")); X0, Z0, S = 680, 760, 1.0   # LiDAR 2023 DTM, 1 m
def dtm(x, z): return float(DTM[int((z - Z0) / S), int((x - X0) / S)])
def ramp(names, x0, x1, dmax):
    pts = [p for n in names for p in W[n]["pts"]]; nx, nz = W[names[0]]["low"]
    inner, outer = [], []
    for x in np.arange(x0, x1 + 0.1, 2.0):
        seg = next(((a, b) for a, b in zip(pts, pts[1:]) if a[0] <= x <= b[0]), None)
        if not seg: continue
        a, b = seg; f = (x - a[0]) / max(1e-6, b[0] - a[0]); z = a[1] + (b[1] - a[1]) * f
        lev = float(np.median([dtm(x + nx * q, z + nz * q) for q in (2.5, 3.5, 4.5)])); d = 3.0
        while d < dmax and dtm(x + nx * (d + 1), z + nz * (d + 1)) > lev - 0.9: d += 1
        inner.append((x + nx * 0.2, z + nz * 0.2)); outer.append((x + nx * d, z + nz * d))
    return Polygon(inner + outer[::-1]).buffer(0), outer, (nx, nz), names[0]
RMP = [ramp(["north_w"], 766, 812, 7), ramp(["north_e"], 850, 896, 12)]
ramps = [r[0] for r in RMP]
isl = PATHS.intersection(box(760, 1018, 860, 1056))
isl = max(getattr(isl, "geoms", [isl]), key=lambda g: g.area)
FOUNT = Polygon([(810.3, 1033.7), (807.9, 1033.3), (806.2, 1033.6), (804.1, 1034.7), (803.0, 1036.3), (802.8, 1037.9), (803.6, 1039.6), (804.9, 1041.0), (807.0, 1041.9), (808.9, 1042.4), (811.0, 1042.3), (813.1, 1041.6), (814.5, 1040.2), (815.1, 1038.4), (814.4, 1036.3), (812.7, 1034.6)])
beds = [Polygon(h) for h in isl.interiors if not Polygon(h).buffer(0).intersects(FOUNT.buffer(-1))]
# the whole island (paths + beds + fountain): its outline, to lay the paths on and to cut the beds and the fountain from
island_all = Polygon(isl.exterior)
R = lambda g: [[round(x, 2), round(z, 2)] for x, z in list(g.exterior.coords)[:-1]]
H = lambda g: [[[round(x, 2), round(z, 2)] for x, z in list(h.coords)[:-1]] for h in g.interiors]
out = {"pave": {"outer": R(pave), "holes": H(pave)}, "ramp_low": [W["north_w"]["low"], W["north_e"]["low"]],
       "ramps": [{"outer": R(g), "holes": H(g), "edge": [[round(x, 2), round(z, 2)] for x, z in e], "low": list(n), "wall": w} for g, e, n, w in RMP],
       "island": {"outer": R(island_all), "holes": [R(b) for b in beds] + [R(FOUNT)]},
       "beds": [R(b) for b in beds], "fountain": R(FOUNT), "monument": [818.5, 976.5, 6.6]}
json.dump(out, open(os.path.join(ROOT, "blender", "data", "piazzale_ground.json"), "w"), indent=0)
print("pave %.0f m2 (%d holes), ramps %s m2, island %.0f m2, beds %d" % (pave.area, len(pave.interiors), [round(g.area) for g in ramps], island_all.area, len(beds)))
