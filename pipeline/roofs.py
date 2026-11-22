"""Roof reconstruction from the LiDAR surface: planar faces instead of a sampled height grid.

fit_planes()   sequential RANSAC on the 0.5 m DSM points inside a footprint (up to 4 planes, <= 45 deg)
envelope()     convex roofs (gable, hip, pyramid, shed, flat) are the LOWER envelope of their planes:
               z(x, y) = min_i plane_i(x, y). Each plane owns the part of the footprint where it is lowest,
               which gives exact faces with crisp ridges and hips.
A fit is accepted only if the envelope reproduces the scan (RMS and inlier coverage); domes, terraces and
complex roofs keep the scan-based mesh (caller's fallback).
"""
import math, numpy as np
from shapely.geometry import Polygon, MultiPolygon

RNG = np.random.default_rng(1296)


def fit_planes(P, maxk=4, thr=0.3, min_frac=0.08, iters=150):
    """P: (n,3) points in a local frame. Returns list of (a, b, c) with z = a*x + b*y + c."""
    planes, remaining = [], np.ones(len(P), bool)
    need = max(25, int(min_frac * len(P)))
    for _ in range(maxk):
        idx = np.nonzero(remaining)[0]
        if len(idx) < need: break
        best, bestn = None, 0
        for _ in range(iters):
            s = idx[RNG.choice(len(idx), 3, replace=False)]
            A = np.c_[P[s, :2], np.ones(3)]
            if abs(np.linalg.det(A)) < 1e-6: continue
            coef = np.linalg.solve(A, P[s, 2])
            if math.hypot(coef[0], coef[1]) > 1.0: continue                 # steeper than 45 deg: walls / noise
            n = int((np.abs(P[idx, :2] @ coef[:2] + coef[2] - P[idx, 2]) < thr).sum())
            if n > bestn: best, bestn = coef, n
        if best is None or bestn < need: break
        inl = idx[np.abs(P[idx, :2] @ best[:2] + best[2] - P[idx, 2]) < thr]
        best = np.linalg.lstsq(np.c_[P[inl, :2], np.ones(len(inl))], P[inl, 2], rcond=None)[0]
        planes.append(best); remaining[inl] = False
    cover = 1.0 - remaining.mean()
    return planes, cover


def clip_halfplane(poly, a, b, c):
    """Sutherland–Hodgman: keep the part of convex polygon (list of xy) where a*x + b*y <= c."""
    out = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        fp, fq = a * p[0] + b * p[1] - c, a * q[0] + b * q[1] - c
        if fp <= 0: out.append(p)
        if fp * fq < 0:
            t = fp / (fp - fq); out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out


def envelope(planes, footprint, frame):
    """Regions of `footprint` (shapely, local frame) where each plane is the lowest. Returns [(i, polygon)]."""
    x0, y0, x1, y1 = footprint.bounds
    big = [(x0 - 50, y0 - 50), (x1 + 50, y0 - 50), (x1 + 50, y1 + 50), (x0 - 50, y1 + 50)]
    out = []
    for i, (ai, bi, ci) in enumerate(planes):
        cell = big
        for j, (aj, bj, cj) in enumerate(planes):
            if i == j or not cell: continue
            cell = clip_halfplane(cell, ai - aj, bi - bj, cj - ci)          # plane_i <= plane_j
        if len(cell) < 3: continue
        R = Polygon(cell).intersection(footprint)
        if R.is_empty or R.area < 0.5: continue
        for g in getattr(R, "geoms", [R]):
            if isinstance(g, Polygon) and g.area >= 0.5: out.append((i, g))
    return out


def env_z(planes, x, y):
    return np.min([a * x + b * y + c for a, b, c in planes], axis=0)


def roof_uv(plane, x, y):
    """Tile UVs on a roof face: v runs down the slope, u along the eaves (metres). Flat roofs: plain x/y."""
    a, b, _ = plane; g = math.hypot(a, b)
    if g < 0.03: return x, y
    dx, dy = -a / g, -b / g                                                    # downhill direction
    k = math.sqrt(1 + g * g)                                                   # slope length per horizontal metre
    return (x * -dy + y * dx), (x * dx + y * dy) * k
