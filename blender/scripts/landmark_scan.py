"""Place a reduced 3D scan (blender/data/scans/<name>.npz, made by prep_scan.py) into a landmark part, smooth-shaded.

place(part, mat, name, origin, forward, height): the base's centre at `origin` (Blender coordinates), the statue's front
turned to the horizontal direction `forward`, scaled to `height` metres overall (base included).
"""
import os, numpy as np
from mathutils import Vector
from landmark_kit import bm_for, ROOT

_CACHE = {}
def _load(name):
    if name not in _CACHE:
        d = np.load(os.path.join(ROOT, "blender", "data", "scans", f"{name}.npz")); _CACHE[name] = (d["v"], d["f"])
    return _CACHE[name]

def place(part, mat, name, origin, forward, height):
    v, f = _load(name)
    fw = Vector((forward.x, forward.y, 0)).normalized(); up = Vector((0, 0, 1)); rx = up.cross(fw)   # scan: front -Y, x to his left
    R = np.array([[rx.x, -fw.x, 0], [rx.y, -fw.y, 0], [0, 0, 1]])
    P = (v.astype(np.float64) * height) @ R.T + np.array(origin[:])
    bm = bm_for(part, mat); vs = [bm.verts.new(p) for p in P]
    for a, b, c in f:
        try: bm.faces.new((vs[a], vs[b], vs[c])).smooth = True
        except ValueError: pass
