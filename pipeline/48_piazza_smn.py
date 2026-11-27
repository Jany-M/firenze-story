"""Piazza Santa Maria Novella: the lawns, the two obelisks of the Corsa dei Cocchi and the benches → blender/data/piazza_smn.json
for blender/scripts/build_piazza_smn.py.

Lawns: the green of the 2017 orthophoto inside the square, traced (closed, simplified to 0.4 m). The square is laid out
point-symmetric (two ovals of four lawns each, an obelisk at the outer end of each); the north oval's four lawns are traced
and mirrored through the centre for the south oval, which the photo shows the same.
Obelisks: north one from the LiDAR 2023 DSM (top 10 m over the ground at -460, -221); the south one is too slender for the
1 m DSM: the mirror of the north one, which falls on its shadow in the photo (-475, -145).
Benches: pietra serena benches on the paved ring round each oval, facing the lawns (*inferred* from the 2023 photographs).
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
ax, bx, az, bz = -500, -425, -235, -183                    # the north oval
px = lambda x: (x + ORIGIN[0] - x0) / (x1 - x0) * W; py = lambda z: (y1 - (ORIGIN[1] - z)) / (y1 - y0) * H
c = im[int(py(az)):int(py(bz)), int(px(ax)):int(px(bx))].astype(np.float32)
c = cv2.resize(c, None, fx=8, fy=8, interpolation=cv2.INTER_CUBIC)
b, g, r = c[..., 0], c[..., 1], c[..., 2]
mask = ((g / (r + g + b + 1)) > 0.37).astype(np.uint8) * 255
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)); mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
# the photo has ≈0.9 m pixels: smooth the traced edge (σ ≈ 1.2 m) so the beds get the photo's clean curves, not its pixel steps
k = int(1.2 / ((bx - ax) / mask.shape[1])) * 2 + 1
mask = (cv2.GaussianBlur(mask.astype(np.float32), (k * 3 | 1, k * 3 | 1), k / 2) > 127).astype(np.uint8) * 255
sx = (bx - ax) / mask.shape[1]; sz = (bz - az) / mask.shape[0]
cs, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
north = []
for k in cs:
    A = cv2.contourArea(k) * sx * sz
    if A < 20: continue
    a = cv2.approxPolyDP(k, 0.25 / sx, True)[:, 0, :]
    north.append([[round(ax + p[0] * sx, 2), round(az + p[1] * sz, 2)] for p in a]); print("lawn", round(A), len(a))
lawns = north + [[mir(p) for p in L] for L in north]

def ring_around(P):                                        # centroid of a lawn
    return sum(p[0] for p in P) / len(P), sum(p[1] for p in P) / len(P)
# benches: two along the outer side of each big lawn, parallel to the square's axis, facing the lawn
ax_dir = ((OB_S[0] - OB_N[0]), (OB_S[1] - OB_N[1])); L = math.hypot(*ax_dir); ux, uz = ax_dir[0] / L, ax_dir[1] / L   # along the axis (north → south)
benches = []
for P in lawns:
    cx, cz = ring_around(P); area = abs(sum(P[i - 1][0] * P[i][1] - P[i][0] * P[i - 1][1] for i in range(len(P)))) / 2
    if area < 100: continue
    # outward from the axis line through the obelisks
    s = (cx - OB_N[0]) * uz - (cz - OB_N[1]) * ux; nx, nz = (uz, -ux) if s > 0 else (-uz, ux)
    far = max(((p[0] - cx) * nx + (p[1] - cz) * nz) for p in P)
    for t in (-4.5, 4.5):
        bxp, bzp = cx + nx * (far + 1.6) + ux * t, cz + nz * (far + 1.6) + uz * t
        benches.append({"c": [round(bxp, 2), round(bzp, 2)], "ang": round(math.atan2(-uz, ux), 3), "ground": round(G(bxp, bzp), 2)})
out = {"lawns": [{"pts": P, "ground": round(min(G(*p) for p in P), 2)} for P in lawns],
       "obelisks": [{"c": list(o), "ground": round(G(*o), 2)} for o in (OB_N, OB_S)], "benches": benches, "axis": [ux, uz]}
json.dump(out, open(os.path.join(ROOT, "blender", "data", "piazza_smn.json"), "w"), indent=1)
print("lawns", len(lawns), "benches", len(benches), "obelisks", OB_N, OB_S)
