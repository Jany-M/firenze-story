"""Shared detail helpers for the landmark models (arches, voussoirs, windows, doors, pilasters, entablatures, rubble and
ashlar walls, blind arcades, domes, drums, lanterns, octagons). Built on landmark_kit (Frame, box, poly, bm_for); the
materials they use by name ("stone", "serena", "shade", "iron", "wood", "dark", "white", "gold", "tile", "lead", "brick",
"rubble") must exist in MAT in the calling script."""
import math, random
import bmesh
from mathutils import Vector, Matrix
from landmark_kit import Frame, box, pbox, poly, bm_for
Z = Vector((0, 0, 1))

def ring(part, mat, F, cu, cv, r0, r1, n0=0.0, n1=0.15, a0=0.0, a1=math.pi, seg=14, soffit=True):
    """Arch band between radii r0 < r1 centred at (cu, cv) on frame F, front face at n1, with the inner soffit."""
    bm = bm_for(part, mat)
    for k in range(seg):
        t0 = a0 + (a1 - a0) * k / seg; t1 = a0 + (a1 - a0) * (k + 1) / seg
        p = lambda r, t, n: F.p(cu + r * math.cos(t), cv + r * math.sin(t), n)
        poly(bm, [p(r0, t0, n1), p(r1, t0, n1), p(r1, t1, n1), p(r0, t1, n1)])
        if soffit: poly(bm, [p(r0, t0, n0), p(r0, t0, n1), p(r0, t1, n1), p(r0, t1, n0)])
def arch_fill(part, mat, F, u0, u1, v0, spring, n=0.03, seg=12):
    r = (u1 - u0) / 2; c = u0 + r
    pts = [F.p(u0, v0, n), F.p(u1, v0, n)] + [F.p(c + r * math.cos(math.pi * k / seg), spring + r * math.sin(math.pi * k / seg), n) for k in range(seg + 1)]
    poly(bm_for(part, mat), pts)
def blind_arch(part, F, u0, u1, v0, spring, frame="stone", fill="shade", band=0.35):
    """Tall blind arch: darker field with a proud stone ring and jambs."""
    r = (u1 - u0) / 2
    arch_fill(part, fill, F, u0, u1, v0, spring)
    pbox(bm_for(part, frame), F, u0 - band, u0, v0, spring, 0, 0.12); pbox(bm_for(part, frame), F, u1, u1 + band, v0, spring, 0, 0.12)
    ring(part, frame, F, u0 + r, spring, r, r + band, 0, 0.12)
def win_round(part, F, u, v0, v1, w, frame="serena", fill="dark", fw=0.22):
    """Round-headed window with a moulded frame and sill."""
    r = w / 2; spring = v1 - r
    arch_fill(part, fill, F, u - r, u + r, v0, spring, n=0.04)
    pbox(bm_for(part, frame), F, u - r - fw, u - r, v0, spring, 0, 0.1); pbox(bm_for(part, frame), F, u + r, u + r + fw, v0, spring, 0, 0.1)
    ring(part, frame, F, u, spring, r, r + fw, 0, 0.1)
    pbox(bm_for(part, frame), F, u - r - fw - 0.1, u + r + fw + 0.1, v0 - 0.18, v0, 0, 0.18)
def win_rect(part, F, u, v0, v1, w, frame="serena", fill="dark", fw=0.18, pediment=None, grille=False):
    poly(bm_for(part, fill), [F.p(u - w / 2, v0, 0.04), F.p(u + w / 2, v0, 0.04), F.p(u + w / 2, v1, 0.04), F.p(u - w / 2, v1, 0.04)])
    for (a, b, c, d) in ((u - w / 2 - fw, u - w / 2, v0, v1), (u + w / 2, u + w / 2 + fw, v0, v1), (u - w / 2 - fw, u + w / 2 + fw, v1, v1 + fw)):
        pbox(bm_for(part, frame), F, a, b, c, d, 0, 0.1)
    pbox(bm_for(part, frame), F, u - w / 2 - fw - 0.08, u + w / 2 + fw + 0.08, v0 - 0.16, v0, 0, 0.16)
    if pediment == "cornice": pbox(bm_for(part, frame), F, u - w / 2 - fw - 0.15, u + w / 2 + fw + 0.15, v1 + fw, v1 + fw + 0.18, 0, 0.25)
    if grille:
        for k in range(1, int(w / 0.18)):
            pbox(bm_for(part, "iron"), F, u - w / 2 + k * 0.18 - 0.015, u - w / 2 + k * 0.18 + 0.015, v0, v1, 0.05, 0.08)
def oculus(part, F, u, v, r, frame="serena", fill="dark", fw=0.25):
    poly(bm_for(part, fill), [F.p(u + r * math.cos(t), v + r * math.sin(t), 0.04) for t in [2 * math.pi * k / 16 for k in range(16)]])
    ring(part, frame, F, u, v, r, r + fw, 0, 0.1, a0=0, a1=2 * math.pi, seg=16)
def pilaster(part, F, u, w, v0, v1, proj=0.3, mat="stone", base=True):
    pbox(bm_for(part, mat), F, u - w / 2, u + w / 2, v0, v1, 0, proj)
    if base: pbox(bm_for(part, mat), F, u - w / 2 - 0.12, u + w / 2 + 0.12, v0, v0 + 0.5, 0, proj + 0.1)
    pbox(bm_for(part, mat), F, u - w / 2 - 0.12, u + w / 2 + 0.12, v1 - 0.35, v1, 0, proj + 0.12)
def entablature(part, F, u0, u1, v, mat="serena", h=1.1, proj=0.6):
    """Architrave, frieze and projecting cornice."""
    pbox(bm_for(part, mat), F, u0, u1, v, v + h * 0.3, 0, proj * 0.35)
    pbox(bm_for(part, mat), F, u0, u1, v + h * 0.3, v + h * 0.65, 0, proj * 0.2)
    pbox(bm_for(part, mat), F, u0 - 0.1, u1 + 0.1, v + h * 0.65, v + h * 0.8, 0, proj * 0.7)
    pbox(bm_for(part, mat), F, u0 - 0.2, u1 + 0.2, v + h * 0.8, v + h, 0, proj)
def courses(part, F, u0, u1, v0, v1, h=0.55, mat="joint"):
    """Ashlar courses: thin mortar lines on the wall face (off: the pietra forte texture already shows its courses)."""
    return
    v = v0 + h
    while v < v1 - 0.05:
        pbox(bm_for(part, mat), F, u0, u1, v, v + 0.03, 0, 0.012); v += h
def rubble(part, F, u0, u1, v0, top, seed=0, holes=()):
    """Rubble masonry in rough courses up to top(u): irregular stones a few cm proud, a few bricks, put-log holes;
    holes = (u0, u1, v0, v1) rectangles kept clear (doors, windows, the brick arch)."""
    rnd = random.Random(seed); v = v0
    while v < max(top(u0), top(u1), top((u0 + u1) / 2)):
        h = rnd.uniform(0.24, 0.42); u = u0
        while u < u1 - 0.05:
            ue = min(u + rnd.uniform(0.3, 1.1), u1); t = min(top(u), top(ue))
            clear = not any(a - 0.05 < ue and u < b + 0.05 and c - 0.05 < v + h and v < d + 0.05 for (a, b, c, d) in holes)
            if v + h <= t and clear:
                mat = "brick" if rnd.random() < 0.025 else ("stone" if rnd.random() < 0.15 else "rubble")
                pbox(bm_for(part, mat), F, u + 0.025, ue - 0.025, v + 0.025, v + h - 0.025, 0, rnd.uniform(0.015, 0.06))
                if rnd.random() < 0.012: poly(bm_for(part, "dark"), [F.p(u + 0.2, v + 0.1, 0.13), F.p(u + 0.45, v + 0.1, 0.13), F.p(u + 0.45, v + 0.35, 0.13), F.p(u + 0.2, v + 0.35, 0.13)])
            u = ue
        v += h
def arcade_wall(part, F, L, nb, h, depth=0.6, pier=1.4, mat="stone"):
    """Wall of blind arches: piers and spandrels flush with the face, arch fields recessed by depth (the wall block behind
    must stop at n = -depth); pilaster strips on the piers, impost blocks, cornice at h."""
    bay = L / nb
    for i in range(nb + 1):
        u = i * bay; a = max(0, u - pier / 2); b = min(L, u + pier / 2)
        pbox(bm_for(part, mat), F, a, b, -1.5, h, -depth, 0)
        pbox(bm_for(part, mat), F, max(0, u - 0.45), min(L, u + 0.45), -1.5, h - 0.3, 0, 0.22)          # pilaster strip
    for i in range(nb):
        u0 = i * bay + pier / 2; u1 = (i + 1) * bay - pier / 2; r = (u1 - u0) / 2; uc = u0 + r; spring = h - 1.3 - r
        pts = [F.p(u0, spring, 0)] + [F.p(uc - r * math.cos(math.pi * k / 12), spring + r * math.sin(math.pi * k / 12), 0) for k in range(13)] + [F.p(u1, h, 0), F.p(u0, h, 0)]
        poly(bm_for(part, mat), pts)                                                                # spandrel
        ring(part, mat, F, uc, spring, r, r + 0.01, -depth, 0.0, seg=12)                            # soffit
        ring(part, "serena" if mat == "serena" else mat, F, uc, spring, r, r + 0.4, 0, 0.08, seg=12, soffit=False)
        pbox(bm_for(part, mat), F, u0 - 0.1, u0 + 0.25, spring - 0.3, spring, -depth, 0.05); pbox(bm_for(part, mat), F, u1 - 0.25, u1 + 0.1, spring - 0.3, spring, -depth, 0.05)
    entablature(part, F, -0.2, L + 0.2, h, mat=mat, h=0.8, proj=0.5)

def cylinder(part, mat, c, r, z0, z1, seg=24, cap=True):
    bmesh.ops.create_cone(bm_for(part, mat), cap_ends=cap, segments=seg, radius1=r, radius2=r, depth=z1 - z0, matrix=Matrix.Translation(c + Z * ((z0 + z1) / 2)))
def cone(part, mat, c, r0, r1, z0, z1, seg=16):
    bmesh.ops.create_cone(bm_for(part, mat), cap_ends=True, segments=seg, radius1=r0, radius2=r1, depth=z1 - z0, matrix=Matrix.Translation(c + Z * ((z0 + z1) / 2)))
def sphere(part, mat, c, r):
    bmesh.ops.create_uvsphere(bm_for(part, mat), u_segments=10, v_segments=6, radius=r, matrix=Matrix.Translation(c))
def cross(part, c, h=1.6):
    b = bm_for(part, "gold"); pbox(b, Frame(c + Vector((-0.06, -0.06, 0)), Vector((1, 0, 0)), Vector((0, 1, 0))), 0, 0.12, 0, h, 0, 0.12)
    pbox(b, Frame(c + Vector((-0.4, -0.06, 0)), Vector((1, 0, 0)), Vector((0, 1, 0))), 0, 0.8, h * 0.62, h * 0.72, 0, 0.12)
def column_lantern(part, c, base_z, r, h, n=8, mat="white"):
    """Lantern of columns on a ring, with entablature, small cupola, ball and cross."""
    cylinder(part, mat, c, r * 1.15, base_z, base_z + 0.5)
    for k in range(n):
        t = 2 * math.pi * k / n; cylinder(part, mat, c + Vector((math.cos(t), math.sin(t), 0)) * r, r * 0.09, base_z + 0.5, base_z + 0.5 + h * 0.6, seg=8)
    cylinder(part, "dark", c, r * 0.7, base_z + 0.5, base_z + 0.5 + h * 0.6, seg=12)
    cylinder(part, mat, c, r * 1.12, base_z + 0.5 + h * 0.6, base_z + 0.9 + h * 0.6)
    cone(part, mat, c, r * 0.95, r * 0.15, base_z + 0.9 + h * 0.6, base_z + h)
    sphere(part, "gold", c + Z * (base_z + h + 0.3), max(0.25, r * 0.2)); cross(part, c + Z * (base_z + h + 0.5), max(1.0, r * 0.9))
def dome(part, c, r, z0, h, ribs=8, mat="tile", seg=24, rib_mat="white", rot=0.0):
    """Dome (half-ellipsoid) with raised ribs; returns the top height."""
    bm = bm_for(part, mat); rings = 9
    pts = [[c + Vector((r * math.cos(t) * math.cos(2 * math.pi * k / seg + rot), r * math.cos(t) * math.sin(2 * math.pi * k / seg + rot), z0 + h * math.sin(t)))
            for k in range(seg)] for t in [math.pi / 2 * i / rings for i in range(rings)]]
    for i in range(rings - 1):
        for k in range(seg): poly(bm, [pts[i][k], pts[i][(k + 1) % seg], pts[i + 1][(k + 1) % seg], pts[i + 1][k]])
    poly(bm, [pts[-1][k] for k in range(seg)])
    for k in range(ribs):
        ang = 2 * math.pi * k / ribs + rot; d = Vector((math.cos(ang), math.sin(ang), 0)); nn = Vector((-d.y, d.x, 0)) * max(0.2, r * 0.03)
        for i in range(rings - 1):
            t0, t1 = math.pi / 2 * i / rings, math.pi / 2 * (i + 1) / rings
            a = c + d * r * 1.015 * math.cos(t0) + Z * (z0 + h * 1.015 * math.sin(t0)); b = c + d * r * 1.015 * math.cos(t1) + Z * (z0 + h * 1.015 * math.sin(t1))
            poly(bm_for(part, rib_mat), [a - nn, a + nn, b + nn, b - nn])
    return z0 + h * math.sin(math.pi / 2 * (rings - 1) / rings)
def octagon_prism(part, mat, c, apothem, z0, z1, rot=0.0):
    R = apothem / math.cos(math.pi / 8); bm = bm_for(part, mat)
    pts = [(c.x + R * math.cos(rot + math.pi / 8 + k * math.pi / 4), c.y + R * math.sin(rot + math.pi / 8 + k * math.pi / 4)) for k in range(8)]
    lo = [bm.verts.new((x, y, z0)) for x, y in pts]; hi = [bm.verts.new((x, y, z1)) for x, y in pts]
    for k in range(8): bm.faces.new((lo[k], lo[(k + 1) % 8], hi[(k + 1) % 8], hi[k]))
    bm.faces.new(hi); bm.faces.new(list(reversed(lo)))
def oct_faces(c, apothem, rot=0.0):
    """Frames on the 8 faces of an octagon (u from the face's left corner, n outward) and the face width."""
    w = 2 * apothem * math.tan(math.pi / 8); out = []
    for k in range(8):
        ang = rot + k * math.pi / 4; n = Vector((math.cos(ang), math.sin(ang), 0)); t = Vector((-n.y, n.x, 0))
        out.append((Frame(c + n * apothem - t * (w / 2), t, n), w, k))
    return out
def door(part, F, u, w, h, arch_mat="brick", leaf="wood", gate=True, relieving=True):
    """Portal: panelled wooden leaves in a stone frame, a relieving arch over it, an iron gate in front."""
    poly(bm_for(part, leaf), [F.p(u - w / 2, 0.0, 0.05), F.p(u + w / 2, 0.0, 0.05), F.p(u + w / 2, h, 0.05), F.p(u - w / 2, h, 0.05)])
    for k in range(1, 4):
        pbox(bm_for(part, leaf), F, u - w / 2 + 0.15, u + w / 2 - 0.15, h * k / 4 - 0.05, h * k / 4 + 0.05, 0.05, 0.09)
    pbox(bm_for(part, leaf), F, u - 0.04, u + 0.04, 0, h, 0.05, 0.1)
    for (a, b, c, d) in ((u - w / 2 - 0.35, u - w / 2, 0, h), (u + w / 2, u + w / 2 + 0.35, 0, h), (u - w / 2 - 0.35, u + w / 2 + 0.35, h, h + 0.45)):
        pbox(bm_for(part, "stone"), F, a, b, c, d, 0, 0.16)
    if relieving: ring(part, arch_mat, F, u, h + 0.45, w / 2 + 0.35, w / 2 + 0.95, 0, 0.1, seg=12, soffit=False)
    if gate:
        for k in range(int(w / 0.14) + 1):
            pbox(bm_for(part, "iron"), F, u - w / 2 + k * 0.14, u - w / 2 + k * 0.14 + 0.03, 0, h * 0.72, 0.4, 0.43)
        for v in (0.15, h * 0.36, h * 0.7):
            pbox(bm_for(part, "iron"), F, u - w / 2, u + w / 2, v, v + 0.05, 0.4, 0.44)


def voussoirs(part, mat, F, cu, cv, r0, r1, n=13, proud=0.12, a0=0.0, a1=math.pi):
    """Arch of separate radiating wedges (voussoirs) between radii r0 and r1, proud of the wall face."""
    bm = bm_for(part, mat); gap = 0.12 * (a1 - a0) / n / 2
    for k in range(n):
        t0 = a0 + (a1 - a0) * k / n + gap; t1 = a0 + (a1 - a0) * (k + 1) / n - gap
        q = [F.p(cu + r * math.cos(t), cv + r * math.sin(t), proud) for r, t in ((r0, t0), (r1, t0), (r1, t1), (r0, t1))]
        poly(bm, q)
        for i in range(4): poly(bm, [q[i], q[(i + 1) % 4], q[(i + 1) % 4] - F.n * proud, q[i] - F.n * proud])
