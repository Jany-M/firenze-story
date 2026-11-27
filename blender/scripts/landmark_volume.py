"""Hand-built volumes in a site frame (landmark_church.Site): prisms over (a, o) outlines, frames on their edges, glass
walls with mullions, ribbon and punched windows, flat and gabled roofs, railway tracks. Used by the 19th–21st century
landmarks (build_stazione_smn.py, build_leopolda.py, build_sinagoga.py, build_teatro_maggio.py), where the DSM raster
gave the masses but not the faces: here every wall, opening and roof is drawn from photographs, its size from the DSM."""
import math
from mathutils import Vector
from landmark_kit import Frame, box, pbox, poly, bm_for, MAT, material
from landmark_detail import ring, arch_fill, cylinder

class Vol:
    def __init__(s, S):
        s.S = S
    def W(s, a, o, h=0.0):
        return s.S.W(a, o, h)
    def frame(s, a0, o0, a1, o1, inside=None):
        """Frame on the edge (a0, o0) → (a1, o1): u along it, n away from `inside` (an (a, o) point), v = height."""
        p0, p1 = s.W(a0, o0), s.W(a1, o1); u = p1 - p0; L = u.length; u.normalize()
        n = Vector((u.y, -u.x, 0.0))
        if inside is not None:
            c = s.W(*inside); m = (p0 + p1) / 2
            if (c - m).dot(n) > 0: n = -n
        return Frame(p0, u, n), L
    def prism(s, part, mat, pts, h0, h1, top=True, bottom=False, top_mat=None):
        """Walls round the outline pts [(a, o), …] from h0 to h1, a flat top (and bottom)."""
        bm = bm_for(part, mat)
        lo = [s.W(a, o, h0) for a, o in pts]; hi = [s.W(a, o, h1) for a, o in pts]
        for i in range(len(pts)):
            j = (i + 1) % len(pts); poly(bm, [lo[i], lo[j], hi[j], hi[i]])
        if top: poly(bm_for(part, top_mat or mat), hi)
        if bottom: poly(bm, lo[::-1])
    def slab(s, part, mat, pts, h, t=0.3):
        s.prism(part, mat, pts, h - t, h, top=True, bottom=True)
    def rect(s, a0, a1, o0, o1):
        return [(a0, o0), (a1, o0), (a1, o1), (a0, o1)]
    def edges(s, pts):
        """(frame, length, (a0, o0), (a1, o1)) of each edge of an outline, normals outwards (from its centroid)."""
        ca = sum(p[0] for p in pts) / len(pts); co = sum(p[1] for p in pts) / len(pts); out = []
        for i in range(len(pts)):
            (a0, o0), (a1, o1) = pts[i], pts[(i + 1) % len(pts)]
            F, L = s.frame(a0, o0, a1, o1, inside=(ca, co)); out.append((F, L, (a0, o0), (a1, o1)))
        return out
    def gable(s, part, mat, a0, a1, o0, o1, h_eave, h_ridge, along="o", over=0.4, gable_mat=None):
        """Gabled roof over the rectangle; ridge along o (or a); gable triangles in gable_mat (walls) if given."""
        bm = bm_for(part, mat)
        if along == "o":
            am = (a0 + a1) / 2
            for (x0, x1) in ((a0 - over, am), (a1 + over, am)):
                poly(bm, [s.W(x0, o0 - over, h_eave), s.W(x0, o1 + over, h_eave), s.W(x1, o1 + over, h_ridge), s.W(x1, o0 - over, h_ridge)])
            if gable_mat:
                for o in (o0, o1): poly(bm_for(part, gable_mat), [s.W(a0, o, h_eave), s.W(a1, o, h_eave), s.W(am, o, h_ridge)])
        else:
            om = (o0 + o1) / 2
            for (y0, y1) in ((o0 - over, om), (o1 + over, om)):
                poly(bm, [s.W(a0 - over, y0, h_eave), s.W(a1 + over, y0, h_eave), s.W(a1 + over, y1, h_ridge), s.W(a0 - over, y1, h_ridge)])
            if gable_mat:
                for a in (a0, a1): poly(bm_for(part, gable_mat), [s.W(a, o0, h_eave), s.W(a, o1, h_eave), s.W(a, om, h_ridge)])
    def hip(s, part, mat, a0, a1, o0, o1, h_eave, h_ridge, over=0.5):
        """Hipped roof over the rectangle, ridge along its longer side."""
        bm = bm_for(part, mat); a0 -= over; a1 += over; o0 -= over; o1 += over
        da, do = a1 - a0, o1 - o0
        if da >= do:
            r = do / 2; A0, A1, om = a0 + r, a1 - r, (o0 + o1) / 2
            c = [s.W(a0, o0, h_eave), s.W(a1, o0, h_eave), s.W(a1, o1, h_eave), s.W(a0, o1, h_eave)]
            R0, R1 = s.W(A0, om, h_ridge), s.W(A1, om, h_ridge)
            poly(bm, [c[0], c[1], R1, R0]); poly(bm, [c[2], c[3], R0, R1]); poly(bm, [c[1], c[2], R1]); poly(bm, [c[3], c[0], R0])
        else:
            r = da / 2; O0, O1, am = o0 + r, o1 - r, (a0 + a1) / 2
            c = [s.W(a0, o0, h_eave), s.W(a1, o0, h_eave), s.W(a1, o1, h_eave), s.W(a0, o1, h_eave)]
            R0, R1 = s.W(am, O0, h_ridge), s.W(am, O1, h_ridge)
            poly(bm, [c[1], c[2], R1, R0]); poly(bm, [c[3], c[0], R0, R1]); poly(bm, [c[0], c[1], R0]); poly(bm, [c[2], c[3], R1])

def glass_wall(part, F, u0, u1, v0, v1, bays, rows=1, glass="glass", frame="steel", n=0.05, fw=0.12):
    """A glazed wall on a face: panes and a grid of mullions and transoms, a little proud of it."""
    poly(bm_for(part, glass), [F.p(u0, v0, n), F.p(u1, v0, n), F.p(u1, v1, n), F.p(u0, v1, n)])
    for i in range(bays + 1):
        u = u0 + (u1 - u0) * i / bays; pbox(bm_for(part, frame), F, u - fw, u + fw, v0, v1, 0, n + 0.08)
    for j in range(rows + 1):
        v = v0 + (v1 - v0) * j / rows; pbox(bm_for(part, frame), F, u0, u1, v - fw * 0.6, v + fw * 0.6, 0, n + 0.06)

def punched(part, F, u0, u1, v0, v1, w, pitch, fill="dark", frame=None, fw=0.12, n=0.04):
    """A row of rectangular windows of width w every `pitch` between u0 and u1 (centred), sill v0, head v1."""
    k = max(1, int((u1 - u0) / pitch)); s0 = u0 + ((u1 - u0) - (k - 1) * pitch) / 2
    for i in range(k):
        u = s0 + i * pitch
        poly(bm_for(part, fill), [F.p(u - w / 2, v0, n), F.p(u + w / 2, v0, n), F.p(u + w / 2, v1, n), F.p(u - w / 2, v1, n)])
        if frame:
            for (a, b, c, d) in ((u - w / 2 - fw, u - w / 2, v0, v1), (u + w / 2, u + w / 2 + fw, v0, v1), (u - w / 2 - fw, u + w / 2 + fw, v1, v1 + fw), (u - w / 2 - fw, u + w / 2 + fw, v0 - fw, v0)):
                pbox(bm_for(part, frame), F, a, b, c, d, 0, n + 0.06)
    return [s0 + i * pitch for i in range(k)]

def arched_row(part, F, u0, u1, v0, spring, w, pitch, fill="dark", frame="serena", fw=0.3, n=0.04):
    """A row of round-arched openings of width w every `pitch` (centred), with a proud arch ring and jambs."""
    k = max(1, int((u1 - u0) / pitch)); s0 = u0 + ((u1 - u0) - (k - 1) * pitch) / 2; r = w / 2
    for i in range(k):
        u = s0 + i * pitch
        arch_fill(part, fill, F, u - r, u + r, v0, spring, n=n)
        if frame:
            ring(part, frame, F, u, spring, r, r + fw, 0, n + 0.12, seg=12)
            pbox(bm_for(part, frame), F, u - r - fw, u - r, v0, spring, 0, n + 0.12); pbox(bm_for(part, frame), F, u + r, u + r + fw, v0, spring, 0, n + 0.12)
    return [s0 + i * pitch for i in range(k)]

def tracks(V, part, a_at, o0, o1, n, pitch=4.6, g=0.0, mats=("ballast", "rail")):
    """n parallel tracks: the i-th centred on a_at(o) + i·pitch (a function of o, for tracks that lean in the frame)."""
    steps = max(2, int((o1 - o0) / 20) + 1)
    os_ = [o0 + (o1 - o0) * k / (steps - 1) for k in range(steps)]
    for i in range(n):
        for k in range(steps - 1):
            oa, ob = os_[k], os_[k + 1]; ca, cb = a_at(oa) + i * pitch, a_at(ob) + i * pitch
            poly(bm_for(part, mats[0]), [V.W(ca - 1.6, oa, g + 0.12), V.W(ca + 1.6, oa, g + 0.12), V.W(cb + 1.6, ob, g + 0.12), V.W(cb - 1.6, ob, g + 0.12)])
            for s_ in (-0.72, 0.72):
                for (x0, x1, h) in ((s_ - 0.04, s_ + 0.04, g + 0.3),):
                    q = [V.W(ca + x0, oa, h), V.W(ca + x1, oa, h), V.W(cb + x1, ob, h), V.W(cb + x0, ob, h)]
                    poly(bm_for(part, mats[1]), q)
                    poly(bm_for(part, mats[1]), [V.W(ca + x0, oa, g + 0.14), V.W(ca + x0, oa, h), V.W(cb + x0, ob, h), V.W(cb + x0, ob, g + 0.14)])
