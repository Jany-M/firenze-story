"""Helpers for church complexes built from pipeline/45_chiese.py (blender/data/chiese.json): the façade frame, a DSM raster
for everything not built by hand, gabled halls, a dome on a drum with its lantern, a bell tower, a wall slab cut to an
outline (curved gables), and simple figures in niches."""
import os, json, math
from mathutils import Vector
from landmark_kit import *
from landmark_detail import *
def extra_materials():
    """Materials the cloisters and squares use; call after K.reset()."""
    for k, args in (("lawn", ("lawn", None, (0.24, 0.38, 0.17), 0.95)), ("path", ("gravel_path", None, (0.62, 0.58, 0.5), 0.95)),
                    ("water", ("water_still", None, (0.18, 0.28, 0.3), 0.1)), ("shutter", ("shutters_green", None, (0.25, 0.35, 0.27), 0.7)),
                    ("marble", ("marble_white", None, (0.9, 0.89, 0.86), 0.5)), ("granite", ("granite_pink", None, (0.66, 0.5, 0.46), 0.5)),
                    ("bronze", ("bronze", None, (0.25, 0.22, 0.15), 0.4)), ("breccia", ("breccia_medicea", None, (0.6, 0.45, 0.42), 0.5))):
        if k not in MAT: MAT[k] = material(*args)
    if "iron" not in MAT: MAT["iron"] = material("wrought_iron", None, (0.08, 0.08, 0.08), 0.6, metal=0.6)

class Site:
    """Frame of one site: a along the front from its corner A, o inwards (0 = the front line), h = scene height."""
    def __init__(s, key):
        s.D = json.load(open(os.path.join(ROOT, "blender", "data", "chiese.json"), encoding="utf-8"))[key]
        s.A = s.D["A"]; s.t = s.D["t"]; s.n = s.D["n"]
        s.TA = Vector((s.t[0], -s.t[1], 0)); s.NO = Vector((s.n[0], -s.n[1], 0))
        s.G = s.D["ground_front"] + 0.05; s.L = s.D["width"]
    def W(s, a, o, h=0.0):
        return Vector((s.A[0] + s.t[0] * a + s.n[0] * o, -(s.A[1] + s.t[1] * a + s.n[1] * o), h))
    def front(s):
        """Frame on the front: u along it from A, n outwards (towards the square)."""
        return Frame(s.W(0, 0), s.TA, -s.NO)

    def raster(s, phase_of, mat="plaster", step=2.5, detail=None, skip=None, solid=None, shutters=None):
        """Buildings massed from the DSM raster (landmark_mass.massing): phase_of(a, o, k) -> (part, year[, end]) or None
        (k = index of the OSM outline); detail(part) -> {"mat": …} picks the wall material; solid(a, o) marks hand-built
        masses that roofs lean against."""
        from landmark_mass import massing
        g = s.D["grid"]; a0, o0 = g["a0"], g["o0"]; cells = {}
        for j in range(g["no"]):
            for i in range(g["na"]):
                h = g["h"][j][i]
                if h is None: continue
                a, o = a0 + i + 0.5, o0 + j + 0.5
                ph = phase_of(a, o, g["k"][j][i])
                if ph is None or (skip and skip(a, o)): continue
                cells[(i, j)] = (ph, h, g["g"][j][i])
        def k_at(a, o):
            i, j = int(math.floor(a - a0)), int(math.floor(o - o0))
            return g["k"][j][i] if 0 <= i < g["na"] and 0 <= j < g["no"] else None
        if solid is None: solid = lambda a, o: k_at(a, o) == 0         # roofs lean against the church
        mat_of = (lambda ph: (detail(ph[0]) or {}).get("mat", mat)) if detail else None
        return massing(cells, a0, o0, s.W, s.TA, s.NO, mat=mat, solid=solid, mat_of=mat_of, shutters=shutters)

    def cloister(s, part, a0, a1, o0, o1, ground, spring, bays, depth, top, kind="loggia", upper=None, ring_top=None, garth="lawn", well=None, wall="plaster"):
        """A cloister on the garth a0..a1 × o0..o1: on each side an arcade of round arches on pietra serena columns, the
        walk `depth` deep behind it. kind "loggia": the walk under the upper floor (wall above the arches up to `top`,
        a string course, windows `upper` = (sill, h, w, style) per bay); kind "lean": a lean-to roof over the walk against
        the wing behind. bays = (n along a, n along o). The ring of wings behind is built up to ring_top (or top)."""
        sides = [(Frame(s.W(a0, o0), s.TA, s.NO), a1 - a0, bays[0]),        # faces into the garth (n towards its middle)
                 (Frame(s.W(a1, o1), -s.TA, -s.NO), a1 - a0, bays[0]),
                 (Frame(s.W(a0, o1), -s.NO, s.TA), o1 - o0, bays[1]),
                 (Frame(s.W(a1, o0), s.NO, -s.TA), o1 - o0, bays[1])]
        g = ground; R_top = ring_top or top
        for F, Lf, nb in sides:
            bay = Lf / nb; r = bay / 2 - 0.18
            for k in range(nb + 1):
                u = k * bay
                pbox(bm_for(part, "serena"), F, u - 0.32, u + 0.32, g, g + 0.3, -0.32, 0.32)
                cylinder(part, "serena", F.p(u, 0, 0), 0.2, g + 0.3, spring - 0.55, seg=10)
                pbox(bm_for(part, "serena"), F, u - 0.3, u + 0.3, spring - 0.55, spring - 0.2, -0.3, 0.3)   # capital
                pbox(bm_for(part, "serena"), F, u - 0.36, u + 0.36, spring - 0.2, spring, -0.36, 0.36)   # pulvino
            for k in range(nb):
                uc = (k + 0.5) * bay; bm = bm_for(part, wall); seg = 10
                for s_ in (-1, 1):
                    pts = [F.p(uc + s_ * r * math.cos(math.pi / 2 * i / seg), spring + r * math.sin(math.pi / 2 * i / seg), 0) for i in range(seg + 1)]
                    corner = F.p(uc + s_ * (bay / 2), spring + r + 0.5, 0)
                    for i in range(seg): poly(bm, [pts[i], pts[i + 1], corner] if s_ > 0 else [pts[i + 1], pts[i], corner])
                    poly(bm, [F.p(uc + s_ * r, spring, 0), F.p(uc + s_ * bay / 2, spring, 0), corner] if s_ > 0 else [F.p(uc + s_ * bay / 2, spring, 0), F.p(uc + s_ * r, spring, 0), corner])
                ring(part, "serena", F, uc, spring, r, r + 0.25, 0, 0.1, seg=12, soffit=True)
            pbox(bm_for(part, "serena"), F, -0.2, Lf + 0.2, spring + r + 0.5, spring + r + 0.85, 0, 0.25)   # cornice over the arches
            # the back wall of the walk with doors, its ceiling
            box(bm_for(part, wall), F, -depth, Lf + depth, g, spring + r + 0.5, -depth - 0.5, -depth)
            poly(bm_for(part, wall), [F.p(-depth, spring + r + 0.5, -depth), F.p(Lf + depth, spring + r + 0.5, -depth), F.p(Lf, spring + r + 0.5, 0), F.p(0, spring + r + 0.5, 0)][::-1])
            for k in (1, nb - 2):
                if 0 <= k < nb:
                    uc = (k + 0.5) * bay
                    poly(bm_for(part, "wood"), [F.p(uc - 0.7, g, -depth + 0.02), F.p(uc + 0.7, g, -depth + 0.02), F.p(uc + 0.7, g + 2.8, -depth + 0.02), F.p(uc - 0.7, g + 2.8, -depth + 0.02)])
            if kind == "loggia":
                v0 = spring + r + 0.85
                if upper and upper[3] == "colonnade":                # an open upper loggia: parapet, columns, architrave
                    pb = upper[0]
                    box(bm_for(part, wall), F, -depth, Lf + depth, v0, v0 + pb, -depth - 0.5, 0.0)
                    box(bm_for(part, wall), F, -depth, Lf + depth, v0 + pb, top, -depth - 0.5, -depth)
                    pbox(bm_for(part, "serena"), F, -0.2, Lf + 0.2, v0 + pb - 0.12, v0 + pb, 0, 0.2)
                    for k in range(nb + 1):
                        cylinder(part, "serena", F.p(k * bay, 0, -0.3), 0.15, v0 + pb, top - 0.65, seg=8)
                    pbox(bm_for(part, "serena"), F, -0.2, Lf + 0.2, top - 0.65, top - 0.35, -0.5, 0.0)
                    poly(bm_for(part, "wood"), [F.p(-depth, top - 0.65, -depth), F.p(Lf + depth, top - 0.65, -depth), F.p(Lf, top - 0.65, -0.5), F.p(0, top - 0.65, -0.5)])
                    upper = None
                else:
                    box(bm_for(part, wall), F, -depth, Lf + depth, v0, top, -depth - 0.5, 0.0)
                pbox(bm_for(part, "serena"), F, -0.2, Lf + 0.2, top - 0.35, top, 0, 0.5)
                if upper:
                    sill, hh, w, style = upper
                    for k in range(nb):
                        uc = (k + 0.5) * bay
                        if style == "arched":
                            tall_w = w / 2; sp = v0 + sill + hh - tall_w
                            arch_fill(part, "glass", F, uc - tall_w, uc + tall_w, v0 + sill, sp, n=0.03)
                            ring(part, "serena", F, uc, sp, tall_w, tall_w + 0.18, 0, 0.1, seg=10, soffit=False)
                            for s2 in (-1, 1): pbox(bm_for(part, "serena"), F, uc + s2 * (tall_w + 0.09) - 0.09, uc + s2 * (tall_w + 0.09) + 0.09, v0 + sill, sp, 0, 0.1)
                            pbox(bm_for(part, "serena"), F, k * bay - 0.25, k * bay + 0.25, v0, top - 0.35, 0, 0.1)   # pilaster strips
                        else:
                            win_rect(part, F, uc, v0 + sill, v0 + sill + hh, w, frame="serena", fill="glass", fw=0.14)
                            if style == "shutters":
                                for s2 in (-1, 1): pbox(bm_for(part, "shutter"), F, uc + s2 * (w / 2 + 0.05) - w / 4, uc + s2 * (w / 2 + 0.05) + w / 4, v0 + sill, v0 + sill + hh, 0.04, 0.08)
                rb = bm_for(part, "roof")                         # the wing's roof falls into the garth
                poly(rb, [F.p(-depth - 0.5, top + 1.6, -depth - 0.5), F.p(Lf + depth + 0.5, top + 1.6, -depth - 0.5), F.p(Lf + 0.6, top, 0.6), F.p(-0.6, top, 0.6)])
            else:
                rb = bm_for(part, "roof"); h0 = spring + r + 0.85
                poly(rb, [F.p(-depth - 0.3, h0 + 1.4, -depth), F.p(Lf + depth + 0.3, h0 + 1.4, -depth), F.p(Lf + 0.5, h0, 0.6), F.p(-0.5, h0, 0.6)])
                box(bm_for(part, wall), F, -depth, Lf + depth, h0 + 1.4, R_top, -depth - 0.5, -depth)    # the wing behind
                pbox(bm_for(part, "serena"), F, -depth, Lf + depth, R_top - 0.35, R_top, -depth, -depth + 0.45)
                if upper:
                    sill, hh, w, style = upper
                    for k in range(nb):
                        uc = (k + 0.5) * bay
                        if True: poly(bm_for(part, "glass"), [F.p(uc - w / 2, h0 + 1.4 + sill, -depth + 0.02), F.p(uc + w / 2, h0 + 1.4 + sill, -depth + 0.02), F.p(uc + w / 2, h0 + 1.4 + sill + hh, -depth + 0.02), F.p(uc - w / 2, h0 + 1.4 + sill + hh, -depth + 0.02)])
                        else: poly(bm_for(part, "glass"), [F.p(uc - w / 2, h0 + 1.4 + sill, -depth + 0.02), F.p(uc + w / 2, h0 + 1.4 + sill, -depth + 0.02), F.p(uc + w / 2, h0 + 1.4 + sill + hh, -depth + 0.02), F.p(uc - w / 2, h0 + 1.4 + sill + hh, -depth + 0.02)])
                rb2 = bm_for(part, "roof")
                poly(rb2, [F.p(-depth - 0.5, R_top + 1.6, -depth - 6.0), F.p(Lf + depth + 0.5, R_top + 1.6, -depth - 6.0), F.p(Lf + depth + 0.5, R_top, -depth + 0.5), F.p(-depth - 0.5, R_top, -depth + 0.5)])
        # the garth: lawn or paving, paths in a cross, a well or a basin in the middle
        gm = {"lawn": "lawn", "paved": "serena"}[garth]
        poly(bm_for(part, gm), [s.W(a0, o0, g + 0.04), s.W(a1, o0, g + 0.04), s.W(a1, o1, g + 0.04), s.W(a0, o1, g + 0.04)][::-1])
        am, om = (a0 + a1) / 2, (o0 + o1) / 2
        for (pa0, pa1, po0, po1) in ((am - 0.9, am + 0.9, o0, o1), (a0, a1, om - 0.9, om + 0.9)):
            poly(bm_for(part, "path"), [s.W(pa0, po0, g + 0.06), s.W(pa1, po0, g + 0.06), s.W(pa1, po1, g + 0.06), s.W(pa0, po1, g + 0.06)][::-1])
        c = s.W(am, om)
        if well == "well":
            cylinder(part, "serena", c, 1.0, g, g + 0.9, seg=12); cylinder(part, "dark", c, 0.75, g + 0.9, g + 0.92, seg=12)
            for t in (0, math.pi):
                p0 = c + Vector((math.cos(t) * 0.8, math.sin(t) * 0.8, 0))
                cylinder(part, "iron", p0, 0.05, g + 0.9, g + 3.0, seg=5)
            cylinder(part, "iron", c, 0.08, g + 3.0, g + 3.6, seg=5)
        elif well == "basin":
            cylinder(part, "serena", c, 2.4, g, g + 0.5, seg=20); cylinder(part, "water", c, 2.15, g + 0.5, g + 0.52, seg=20)

    def hall(s, part, a0, a1, o0, o1, base, eave, ridge, along="o", mat="plaster", gables=(True, True)):
        """A gabled hall over a0..a1 × o0..o1; the ridge runs along o (nave) or a (transept)."""
        box(bm_for(part, mat), Frame(s.W(a0, o0), s.TA, s.NO), 0, a1 - a0, base, eave, 0, o1 - o0)
        bm = bm_for(part, "roof"); e = 0.5
        if along == "o":
            am = (a0 + a1) / 2
            poly(bm, [s.W(a0 - e, o0, eave), s.W(a0 - e, o1, eave), s.W(am, o1, ridge), s.W(am, o0, ridge)])
            poly(bm, [s.W(a1 + e, o1, eave), s.W(a1 + e, o0, eave), s.W(am, o0, ridge), s.W(am, o1, ridge)])
            for o, gb in ((o0, gables[0]), (o1, gables[1])):
                if gb: poly(bm_for(part, mat), [s.W(a0, o, eave), s.W(a1, o, eave), s.W(am, o, ridge)])
        else:
            om = (o0 + o1) / 2
            poly(bm, [s.W(a1, o0 - e, eave), s.W(a0, o0 - e, eave), s.W(a0, om, ridge), s.W(a1, om, ridge)])
            poly(bm, [s.W(a0, o1 + e, eave), s.W(a1, o1 + e, eave), s.W(a1, om, ridge), s.W(a0, om, ridge)])
            for a, gb in ((a0, gables[0]), (a1, gables[1])):
                if gb: poly(bm_for(part, mat), [s.W(a, o0, eave), s.W(a, o1, eave), s.W(a, om, ridge)])

    def dome(s, part, a, o, r, drum0, drum1, rise, lantern_top, windows=8):
        c = s.W(a, o)
        cylinder(part, "plaster", c, r, drum0, drum1, seg=24)
        for k in range(windows):                                           # oculi round the drum
            t = 2 * math.pi * (k + 0.5) / windows; d = Vector((math.cos(t), math.sin(t), 0))
            F = Frame(c + d * r, Vector((-d.y, d.x, 0)), d)
            oculus(part, F, 0, (drum0 + drum1) / 2, 0.6, frame="serena", fill="dark", fw=0.15)
        dome(part, c, r + 0.2, drum1, rise, ribs=8, mat="tile", seg=24, rib_mat="serena")
        lt = drum1 + rise * 0.96
        cylinder(part, "serena", c, 1.3, lt, lantern_top - 1.6, seg=8)
        cone(part, "serena", c, 1.5, 0.15, lantern_top - 1.6, lantern_top, seg=8)

    def campanile(s, part, a, o, side, g, shaft, belfry, top, mat="plaster", spire="pyramid"):
        """Square tower centred at (a, o): shaft up to `shaft`, open belfry to `belfry`, roof or spire to `top`."""
        h = side / 2
        Fb = Frame(s.W(a - h, o - h), s.TA, s.NO)
        box(bm_for(part, mat), Fb, 0, side, g - 0.5, shaft, 0, side)
        for (o_, u_, n_) in ((s.W(a - h, o - h), s.TA, -s.NO), (s.W(a + h, o - h), s.NO, s.TA), (s.W(a + h, o + h), -s.TA, s.NO), (s.W(a - h, o + h), -s.NO, -s.TA)):
            F = Frame(o_, u_, n_)
            pbox(bm_for(part, "serena"), F, -0.1, side + 0.1, shaft - 0.3, shaft, 0, 0.2)
            for k in (0, 1):
                uc = side * (0.27 + 0.46 * k); r = side * 0.16
                arch_fill(part, "dark", F, uc - r, uc + r, shaft, belfry - r - 0.6, n=0.02)
            pbox(bm_for(part, "serena"), F, -0.15, side + 0.15, belfry - 0.4, belfry, 0, 0.3)
        box(bm_for(part, mat), Fb, 0, side, shaft, belfry, 0.4, side - 0.4)
        for (u0, u1, v0, v1) in ((0, 0.6, 0, 0.6), (side - 0.6, side, 0, 0.6), (0, 0.6, side - 0.6, side), (side - 0.6, side, side - 0.6, side), (side / 2 - 0.3, side / 2 + 0.3, 0, side), (0, side, side / 2 - 0.3, side / 2 + 0.3)):
            box(bm_for(part, mat), Fb, u0, u1, shaft, belfry, v0, v1)
        c = s.W(a, o)
        if spire == "pyramid":
            bm = bm_for(part, "roof"); pts = [s.W(a - h - 0.3, o - h - 0.3, belfry), s.W(a + h + 0.3, o - h - 0.3, belfry), s.W(a + h + 0.3, o + h + 0.3, belfry), s.W(a - h - 0.3, o + h + 0.3, belfry)]
            for p0, p1 in zip(pts, pts[1:] + pts[:1]): poly(bm, [p0, p1, c + Vector((0, 0, top))])
        else:                                                              # octagonal lantern and cone
            cylinder(part, mat, c, h * 0.8, belfry, belfry + (top - belfry) * 0.45, seg=8)
            cone(part, "roof", c, h * 0.85, 0.1, belfry + (top - belfry) * 0.45, top, seg=8)

def slab(part, mat, F, pts, n0, n1):
    """A wall slab cut to the outline pts [(u, v)] (counter-clockwise seen from outside), from n0 to n1 (n outwards)."""
    bm = bm_for(part, mat)
    poly(bm, [F.p(u, v, n1) for u, v in pts]); poly(bm, [F.p(u, v, n0) for u, v in pts[::-1]])
    for (u0, v0), (u1, v1) in zip(pts, pts[1:] + pts[:1]):
        poly(bm, [F.p(u0, v0, n0), F.p(u1, v1, n0), F.p(u1, v1, n1), F.p(u0, v0, n1)])

def scroll_curve(u0, v0, u1, v1, n=10, bulge=0.25):
    """A concave-convex curve from (u0, v0) down to (u1, v1): the volute profile of a Renaissance gable."""
    out = []
    for k in range(n + 1):
        t = k / n; u = u0 + (u1 - u0) * t
        v = v0 + (v1 - v0) * (3 * t * t - 2 * t * t * t) + bulge * (v0 - v1) * math.sin(math.pi * t) * (1 if t > 0.5 else -0.4)
        out.append((u, v))
    return out

def figure(part, F, u, v, h, n=0.25, mat="marble"):
    """Stand-in statue on the face of F."""
    box(bm_for(part, mat), F, u - 0.28, u + 0.28, v, v + h * 0.82, n - 0.2, n + 0.2)
    box(bm_for(part, mat), F, u - 0.13, u + 0.13, v + h * 0.82, v + h, n - 0.13, n + 0.13)

NOW_ = 99999

# ---------------------------------------------------------------- the squares: beds, fountains, monuments (scene x/z)
def Vs(x, z, h=0.0): return Vector((x, -z, h))

def bed(part, pts, g, curb=0.3, rail=True):
    """A raised garden bed on the outline pts (scene x/z): stone curb, lawn, a low iron railing on the curb."""
    P = pts[:-1] if pts[0] == pts[-1] else pts
    if sum(P[i - 1][0] * P[i][1] - P[i][0] * P[i - 1][1] for i in range(len(P))) < 0: P = P[::-1]
    poly(bm_for(part, "lawn"), [Vs(x, z, g + curb) for x, z in P][::-1])
    bc = bm_for(part, "serena")
    for (x0, z0), (x1, z1) in zip(P, P[1:] + P[:1]):
        L = math.hypot(x1 - x0, z1 - z0)
        if L < 0.05: continue
        poly(bc, [Vs(x0, z0, g - 0.1), Vs(x1, z1, g - 0.1), Vs(x1, z1, g + curb), Vs(x0, z0, g + curb)][::-1])
        if rail:
            n = max(1, int(L / 1.6))
            for k in range(n):
                t = k / n; x, z = x0 + (x1 - x0) * t, z0 + (z1 - z0) * t
                cylinder(part, "iron", Vs(x, z), 0.025, g + curb, g + curb + 0.55, seg=4, cap=False)
            ux, uz = (x1 - x0) / L, (z1 - z0) / L
            F = Frame(Vs(x0, z0), Vector((ux, -uz, 0)), Vector((uz, ux, 0)))
            box(bm_for(part, "iron"), F, 0, L, g + curb + 0.5, g + curb + 0.55, -0.02, 0.02)

def oct_ring(part, mat, c, r, z0, z1):
    cylinder(part, mat, c, r / math.cos(math.pi / 8), z0, z1, seg=8)

def fountain_spirito(part, c, r, g):
    """The fountain of Piazza Santo Spirito (photographs: Francesco Bini 2025, Rufus46 2014; it.wikipedia): an octagonal
    basin of pietra serena on three steps, a marble shaft with two basins (the lower of breccia medicea, the upper of white
    marble), a small trough with a Medusa head on one side."""
    C = Vs(*c)
    for k, (rr, h0, h1) in enumerate(((r + 1.6, -0.2, 0.17), (r + 1.05, 0.17, 0.34), (r + 0.55, 0.34, 0.51))):
        oct_ring(part, "serena", C, rr, g + h0, g + h1)
    oct_ring(part, "serena", C, r, g + 0.51, g + 1.45)
    oct_ring(part, "water", C, r - 0.3, g + 1.45, g + 1.47)
    cylinder(part, "serena", C, 0.55, g + 0.51, g + 1.9, seg=12)
    cylinder(part, "marble", C, 0.3, g + 1.9, g + 2.8, seg=12)
    cone(part, "breccia", C, 0.25, 1.15, g + 2.8, g + 3.05, seg=16); cylinder(part, "breccia", C, 1.15, g + 3.05, g + 3.15, seg=16)
    cylinder(part, "marble", C, 0.18, g + 3.15, g + 3.75, seg=10)
    cone(part, "marble", C, 0.15, 0.72, g + 3.75, g + 3.95, seg=16); cylinder(part, "marble", C, 0.72, g + 3.95, g + 4.02, seg=16)
    cylinder(part, "marble", C, 0.1, g + 4.02, g + 4.35, seg=8)
    F = Frame(C + Vector((r + 0.55, 0, 0)), Vector((0, 1, 0)), Vector((1, 0, 0)))                  # the Medusa trough
    box(bm_for(part, "marble"), F, -0.6, 0.6, g + 0.51, g + 1.2, 0, 0.7)

def statue(part, c, face, g, base=(1.7, 2.6), fig=2.6, ped="granite", body="marble", fence=None):
    """A standing statue on a pedestal with a moulded base and cap, turned to face the direction `face` (scene x/z)."""
    C = Vs(*c); u = Vector((face[1], face[0], 0)).normalized(); n = Vector((face[0], -face[1], 0)).normalized()
    F = Frame(C, u, n); w, h = base
    box(bm_for(part, ped), F, -w / 2 - 0.35, w / 2 + 0.35, g - 0.2, g + 0.35, -w / 2 - 0.35, w / 2 + 0.35)
    box(bm_for(part, ped), F, -w / 2, w / 2, g + 0.35, g + h - 0.3, -w / 2, w / 2)
    box(bm_for(part, ped), F, -w / 2 - 0.15, w / 2 + 0.15, g + h - 0.3, g + h, -w / 2 - 0.15, w / 2 + 0.15)
    z = g + h
    box(bm_for(part, body), F, -0.35, 0.35, z, z + fig * 0.5, -0.25, 0.25)                         # legs and coat
    box(bm_for(part, body), F, -0.42, 0.42, z + fig * 0.45, z + fig * 0.83, -0.27, 0.27)            # body
    box(bm_for(part, body), F, -0.14, 0.14, z + fig * 0.83, z + fig, -0.14, 0.14)                   # head
    if fence:
        P = fence[:-1] if fence[0] == fence[-1] else fence
        for (x0, z0), (x1, z1) in zip(P, P[1:] + P[:1]):
            L = math.hypot(x1 - x0, z1 - z0); ux, uz = (x1 - x0) / L, (z1 - z0) / L
            Ff = Frame(Vs(x0, z0), Vector((ux, -uz, 0)), Vector((uz, ux, 0)))
            box(bm_for(part, "serena"), Ff, 0, L, g - 0.1, g + 0.3, -0.15, 0.15)
            for k in range(int(L / 0.25)): box(bm_for(part, "iron"), Ff, k * 0.25, k * 0.25 + 0.03, g + 0.3, g + 1.1, -0.02, 0.02)
            box(bm_for(part, "iron"), Ff, 0, L, g + 1.05, g + 1.12, -0.03, 0.03)

def bench(part, c, ang, g, L=2.2):
    u = Vector((math.cos(ang), math.sin(ang), 0)); n = Vector((-u.y, u.x, 0))
    F = Frame(Vs(*c) - u * (L / 2), u, n)
    box(bm_for(part, "serena"), F, 0, L, g + 0.38, g + 0.46, -0.25, 0.25)
    for uu in (0.2, L - 0.4): box(bm_for(part, "serena"), F, uu, uu + 0.2, g - 0.05, g + 0.38, -0.2, 0.2)
