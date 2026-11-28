"""Piazzale Michelangelo: the ground pieces of the model (v1, 2026-11-27) from the Comune's circulation areas.

In:  blender/data/piazzale_walls.json (walls snapped to the LiDAR, _dev/tmp/wall_snap.py); the Comune's pedestrian and
     carriageway polygons (S02 viabilità, _dev/data/raw/comune); the fountain before the Loggia (OSM way 1093617565)
Out: blender/data/piazzale_ground.json, read by blender/scripts/build_piazzale.py:
  pave    the terrace's ground: inside its walls, less the carriageway that runs round its south side (Viale Galileo into
          Viale Michelangiolo, Comune polygon 3717, left to the app's streets) and less the monument's platform
  front   the city side's geometry: the great rectangle's front line, the small rectangle standing out in its middle, the
          two ramps off its sides (built in build_piazzale.py)
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
# The front on the city side, drawn as the geometric shapes it is (Jany's review 5, 2026-11-28; the LiDAR walls agree within
# 1–3 m): the great rectangle's front wall is one straight line F0 through the measured wall at its west end (745, 927.4) and
# its east end (899, 958.2); in its middle a smaller rectangle stands out towards the city by the ramps' width, between
# s = 66 and 99 m along F0 (x ≈ 810–842); off its two sides Viale Poggi's two ramps run down along F0, mirror images of each
# other, 46 m long, the outer line F1 continuing the small rectangle's front.
FA, FB = (745.0, 927.4), (899.0, 958.2); FSA, FSB, FW, FLEN = 66.0, 99.0, 7.5, 46.0
_L = ((FB[0] - FA[0]) ** 2 + (FB[1] - FA[1]) ** 2) ** 0.5; _d = ((FB[0] - FA[0]) / _L, (FB[1] - FA[1]) / _L); _n = (_d[1], -_d[0])
F0 = lambda s: (FA[0] + _d[0] * s, FA[1] + _d[1] * s)
F1 = lambda s: (F0(s)[0] + _n[0] * FW, F0(s)[1] + _n[1] * FW)
front = [F0(-3.0), F0(FSA), F1(FSA), F1(FSB), F0(FSB), F0(_L), (901.8, 959.1)]
terr = Polygon(front + wl("east", lambda p: p[1] < 1040)[1:] + [(895, 1050), (760, 1050), (745, 1014)] +
               wl("west_s", lambda p: p[1] < 1004)[::-1] + [(SX0, SZ1), (SX0, SZ0)] + wl("west_n")[::-1]).buffer(0)
# the lower terrace by the Belvedere at the foot of the great staircase (57.3 m): the Comune's pedestrian area there, west of the
# staircase's foot (its flight is a polygon of its own, left to the model); grey stone in the orthophoto, laid as such
_stair = find(PED, 728, 961)
LOWER = next(P for P in PED if abs(P.bounds[0] - 711.0) < 0.5 and abs(P.bounds[3] - 985.9) < 0.5).intersection(box(700, 912, 737, 990))
if _stair is not None: LOWER = LOWER.difference(_stair.buffer(0.3))
LOWER = max(getattr(LOWER, "geoms", [LOWER]), key=lambda g: g.area)
MON = Point(818.5, 976.5).buffer(6.6, 24)
pave = terr.difference(ROAD.buffer(0.2)).difference(MON)
pave = max(getattr(pave, "geoms", [pave]), key=lambda g: g.area)      # the terrace (bits south of the road dropped)
isl = PATHS.intersection(box(760, 1018, 860, 1056))
isl = max(getattr(isl, "geoms", [isl]), key=lambda g: g.area)
FOUNT = Polygon([(810.3, 1033.7), (807.9, 1033.3), (806.2, 1033.6), (804.1, 1034.7), (803.0, 1036.3), (802.8, 1037.9), (803.6, 1039.6), (804.9, 1041.0), (807.0, 1041.9), (808.9, 1042.4), (811.0, 1042.3), (813.1, 1041.6), (814.5, 1040.2), (815.1, 1038.4), (814.4, 1036.3), (812.7, 1034.6)])
beds = [Polygon(h) for h in isl.interiors if not Polygon(h).buffer(0).intersects(FOUNT.buffer(-1))]
# the whole island (paths + beds + fountain): its outline, to lay the paths on and to cut the beds and the fountain from
island_all = Polygon(isl.exterior)
R = lambda g: [[round(x, 2), round(z, 2)] for x, z in list(g.exterior.coords)[:-1]]
H = lambda g: [[[round(x, 2), round(z, 2)] for x, z in list(h.coords)[:-1]] for h in g.interiors]
out = {"pave": {"outer": R(pave), "holes": H(pave)}, "front": {"A": FA, "B": FB, "sa": FSA, "sb": FSB, "w": FW, "len": FLEN},
       "lower": {"outer": R(LOWER), "holes": H(LOWER)},
       "island": {"outer": R(island_all), "holes": [R(b) for b in beds] + [R(FOUNT)]},
       "beds": [R(b) for b in beds], "fountain": R(FOUNT), "monument": [818.5, 976.5, 6.6]}
json.dump(out, open(os.path.join(ROOT, "blender", "data", "piazzale_ground.json"), "w"), indent=0)
print("pave %.0f m2 (%d holes), island %.0f m2, beds %d" % (pave.area, len(pave.interiors), island_all.area, len(beds)))
