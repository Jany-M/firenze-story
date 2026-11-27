"""Piazza Santa Maria Novella: the lawns, the two obelisks of the Corsa dei Cocchi and the benches → blender/data/piazza_smn.json
for blender/scripts/build_piazza_smn.py.

Lawns: the green of the 2017 orthophoto over the whole square, traced and simplified to straight sides (1 m): the beds are
flat polygons cut by diagonal paths, two large and two small in each half (photographs from above, 2010s).
Obelisks: north one from the LiDAR 2023 DSM (top 10 m over the ground at -460, -221); the south one is too slender for the
1 m DSM: the mirror of the north one, which falls on its shadow in the photo (-475, -145).
Benches: six long low benches across the axis in the middle of the square (orthophoto and photographs).
"""
import os, sys, json, math
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(__file__))
from common import ROOT, ORIGIN

_m = json.load(open(os.path.join(ROOT, "web", "public", "data", "meta.json")))
_n, _st = _m["terrain"]["n"], _m["terrain"]["step"]
_T = np.fromfile(os.path.join(ROOT, "web", "public", "data", "terrain.f32"), dtype=np.float32).reshape(_n, _n); _half = (_n - 1) * _st / 2
def G(x, z):
    fx, fz = (x + _half) / _st, (z + _half) / _st
    i, j = min(max(int(fx), 0), _n - 2), min(max(int(fz), 0), _n - 2); a, b = fx - i, fz - j
    return float(_T[j, i] * (1 - a) * (1 - b) + _T[j, i + 1] * a * (1 - b) + _T[j + 1, i] * (1 - a) * b + _T[j + 1, i + 1] * a * b)

OB_N = (-460.0, -221.0)
C = (-466.75, -183.0)                                      # centre of symmetry: halfway between the obelisks
OB_S = (2 * C[0] - OB_N[0], 2 * C[1] - OB_N[1])
mir = lambda p: [round(2 * C[0] - p[0], 2), round(2 * C[1] - p[1], 2)]

x0, y0, x1, y1 = _m["bbox_utm"]
im = cv2.imread(os.path.join(ROOT, "web", "public", "data", "ortho2017.jpg")); H, W = im.shape[:2]
ax, bx, az, bz = -505, -432, -240, -125                    # the whole square
px = lambda x: (x + ORIGIN[0] - x0) / (x1 - x0) * W; py = lambda z: (y1 - (ORIGIN[1] - z)) / (y1 - y0) * H
c = im[int(py(az)):int(py(bz)), int(px(ax)):int(px(bx))].astype(np.float32)
c = cv2.resize(c, None, fx=8, fy=8, interpolation=cv2.INTER_CUBIC)
hsv = cv2.cvtColor(np.clip(c, 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV)       # by hue: the lawns in the buildings' shadow stay green
mask = ((hsv[..., 0] > 28) & (hsv[..., 0] < 90) & (hsv[..., 1] > 45)).astype(np.uint8) * 255
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)); mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((11, 11), np.uint8)); mask = cv2.dilate(mask, np.ones((5, 5), np.uint8))   # the photo blurs the edges inwards: give back ≈0.5 m
sx = (bx - ax) / mask.shape[1]; sz = (bz - az) / mask.shape[0]
cs, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
# the lawns are cut as flat polygons with straight sides (the 2010s layout, photographs): simplified to straight edges
# (1 m tolerance), not rounded
lawns = []
for k in cs:
    A = cv2.contourArea(k) * sx * sz
    if A < 15: continue
    a = cv2.approxPolyDP(k, 1.0 / sx, True)[:, 0, :]
    lawns.append([[round(ax + p[0] * sx, 2), round(az + p[1] * sz, 2)] for p in a]); print("lawn", round(A), len(a))
ax_dir = ((OB_S[0] - OB_N[0]), (OB_S[1] - OB_N[1])); L = math.hypot(*ax_dir); ux, uz = ax_dir[0] / L, ax_dir[1] / L   # along the axis (north → south)
# the benches in the middle of the square, between the two halves: long low benches across the axis, in staggered rows
# (orthophoto 2017 – six dark bars at the centre – and photographs)
BENCH_AT = [(-478.5, -183.5), (-467.0, -185.0), (-456.5, -182.5), (-471.5, -176.0), (-460.0, -176.5), (-468.5, -169.5)]
benches = [{"c": [x, z], "ang": round(math.atan2(ux, uz), 3), "ground": round(G(x, z), 2)} for x, z in BENCH_AT]   # length across the axis (Blender frame)
out = {"lawns": [{"pts": P, "ground": round(min(G(*p) for p in P), 2), "gpts": [round(G(*p), 2) for p in P]} for P in lawns],   # the square slopes: each corner at its own ground
       "obelisks": [{"c": list(o), "ground": round(G(*o), 2)} for o in (OB_N, OB_S)], "benches": benches, "axis": [ux, uz]}
json.dump(out, open(os.path.join(ROOT, "blender", "data", "piazza_smn.json"), "w"), indent=1)
print("lawns", len(lawns), "benches", len(benches), "obelisks", OB_N, OB_S)
