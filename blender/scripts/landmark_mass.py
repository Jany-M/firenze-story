"""Massing for the parts of a landmark that are not built by hand (convent wings, houses behind a front): turns a 1 m DSM
raster into buildings with walls, windows, an eaves cornice and hipped roofs, instead of stepped boxes.

How: the built cells (DSM more than 2.5 m above the ground) are smoothed (a 3 × 3 majority), each cell gets the ridge height
of its surroundings (the 80th percentile of the 5 × 5 DSM), ridge heights are grouped in steps and cleaned with a mode
filter, and connected cells of one step form one building; small pieces join their neighbour. Each building gets a roof
whose height grows with the chessboard distance from its outer walls (that is a hipped roof on any outline made of the
raster's edges, with hips and valleys at 45°); edges that step across the raster are straightened into slanting walls, up to the ridge measured on the DSM; against a taller building
or a hand-built mass (`solid`) the roof keeps rising, as a lean-to does against a wall. Walls stand on the open sides only,
with a cornice under the eaves and a window every ≈3.5 m on each floor above whatever stands in front.
"""
import math
from collections import Counter
import bmesh
from mathutils import Vector
from landmark_kit import *

NOW_ = 99999
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))

def _part(ph): return f"{ph[0]}@{ph[1]}-{ph[2] if len(ph) > 2 else NOW_}"

def massing(cells, a0, o0, W, TA, NO, mat="plaster", trim="serena", slope=0.32, dcap=7.0, step=3.0, min_cells=30,
            windows=True, floor=3.7, solid=None, mat_of=None, shutters=None, win=(0.9, 1.7), open_out=True, reg=2, nowin=None):
    """cells {(i, j): (ph, h, g)}: cell (i, j) covers a0+i..a0+i+1 × o0+j..o0+j+1 of the frame W(a, o, h) -> Vector;
    ph = (part name, from[, to]); h = DSM, g = terrain (scene heights). solid(a, o) -> True where a hand-built mass stands
    (roofs lean against it, no wall faces it). Returns the number of buildings."""
    if "roof_m" not in MAT: MAT["roof_m"] = MAT["roof"]
    ph_of = {c: v[0] for c, v in cells.items()}
    built = {c for c, (ph, h, g) in cells.items() if h > g + 2.5}
    for _ in range(2):                                                   # straighten the edges: 3 × 3 majority
        nb = set()
        for (i, j), ph in ph_of.items():
            n = sum(1 for di in (-1, 0, 1) for dj in (-1, 0, 1) if (i + di, j + dj) in built and ph_of.get((i + di, j + dj)) == ph)
            if n >= 5: nb.add((i, j))
        built = nb
    R = {}
    for (i, j) in built:
        ph = ph_of[(i, j)]
        v = sorted(cells[(i + di, j + dj)][1] for di in range(-2, 3) for dj in range(-2, 3)
                   if (i + di, j + dj) in built and ph_of[(i + di, j + dj)] == ph)
        R[(i, j)] = v[min(len(v) - 1, int(len(v) * 0.8))]
    lev = {c: round(R[c] / step) for c in built}
    for _ in range(3):                                                   # mode filter on the steps
        nl = {}
        for (i, j), l in lev.items():
            ph = ph_of[(i, j)]
            cnt = Counter(lev[(i + di, j + dj)] for di in (-1, 0, 1) for dj in (-1, 0, 1) if (i + di, j + dj) in lev and ph_of[(i + di, j + dj)] == ph)
            best, n = cnt.most_common(1)[0]
            nl[(i, j)] = best if n > cnt[l] else l
        lev = nl
    comp, comps = {}, []
    for c in sorted(built):
        if c in comp: continue
        k = len(comps); comp[c] = k; st = [c]; mem = [c]
        while st:
            i, j = st.pop()
            for di, dj in N4:
                n = (i + di, j + dj)
                if n in built and n not in comp and lev[n] == lev[c] and ph_of[n] == ph_of[c]:
                    comp[n] = k; st.append(n); mem.append(n)
        comps.append(mem)
    changed = True
    while changed:                                                       # small pieces join the neighbour they share most with
        changed = False
        for k in sorted(range(len(comps)), key=lambda k: len(comps[k])):
            m = comps[k]
            if not m or len(m) >= min_cells: continue
            cnt = Counter()
            for (i, j) in m:
                for di, dj in N4:
                    n = (i + di, j + dj)
                    if n in comp and comp[n] != k: cnt[comp[n]] += 2 if ph_of[n] == ph_of[(i, j)] else 1
            if not cnt:
                if len(m) < 8:
                    for c in m: del comp[c]
                    comps[k] = []; changed = True
                continue
            t = cnt.most_common(1)[0][0]
            for c in m: comp[c] = t
            comps[t] += m; comps[k] = []; changed = True
    # regular outlines: each building, tallest first, is closed and opened with a square of `reg` cells (fills notches,
    # drops spurs narrower than that) and claims those cells; what is left over joins its neighbour
    def morph(S, r, grow):
        out = set()
        cand = {(i + di, j + dj) for (i, j) in S for di in range(-r, r + 1) for dj in range(-r, r + 1)} if grow else S
        for (i, j) in cand:
            hit = [((i + di, j + dj) in S) for di in range(-r, r + 1) for dj in range(-r, r + 1)]
            if (any(hit) if grow else all(hit)): out.add((i, j))
        return out
    allb = set(comp)
    tk = {k: sorted(R[c] for c in comps[k])[len(comps[k]) // 2] for k in range(len(comps)) if comps[k]}
    claimed = {}
    for k in sorted(tk, key=lambda k: -tk[k]):
        S = set(comps[k])
        S = morph(morph(S, reg, True), reg, False) & allb                  # closing
        S2 = morph(morph(S, reg, False), reg, True) & S                    # opening
        if len(S2) >= min_cells: S = S2
        for c in S:
            if c not in claimed: claimed[c] = k
    left = [c for c in allb if c not in claimed]
    for _ in range(6):
        nxt = []
        for (i, j) in left:
            cnt = Counter(claimed[(i + di, j + dj)] for di, dj in N4 if (i + di, j + dj) in claimed)
            if cnt: claimed[(i, j)] = cnt.most_common(1)[0][0]
            else: nxt.append((i, j))
        left = nxt
    comp = claimed; comps = [[] for _ in comps]
    for c, k in comp.items(): comps[k].append(c)
    ids = [k for k in range(len(comps)) if comps[k]]
    top = {k: sorted(R[c] for c in comps[k])[len(comps[k]) // 2] for k in ids}
    gmin = {k: min(cells[c][2] for c in comps[k]) for k in ids}
    phk = {k: Counter(ph_of[c] for c in comps[k]).most_common(1)[0][0] for k in ids}
    def solid_at(c):
        return solid is not None and solid(a0 + c[0] + 0.5, o0 + c[1] + 0.5)
    sgn = (W(1, 0) - W(0, 0)).cross(W(0, 1) - W(0, 0)).z > 0
    eave, dist = {}, {}
    for k in ids:
        def outside(c, k=k):
            q = comp.get(c)
            if q == k: return False
            if q is not None: return top[q] <= top[k] + 0.5
            return not solid_at(c)
        I0 = min(c[0] for c in comps[k]) - int(dcap) - 2; I1 = max(c[0] for c in comps[k]) + int(dcap) + 3
        J0 = min(c[1] for c in comps[k]) - int(dcap) - 2; J1 = max(c[1] for c in comps[k]) + int(dcap) + 3
        ni, nj = I1 - I0 + 1, J1 - J0 + 1; INF = 1e9
        D = [[0 if any(outside((I0 + I + di, J0 + J + dj)) for di in (-1, 0) for dj in (-1, 0)) else INF for I in range(ni)] for J in range(nj)]
        for J in range(nj):                                              # chessboard distance, two passes
            for I in range(ni):
                v = D[J][I]
                if v == 0: continue
                if I > 0: v = min(v, D[J][I - 1] + 1)
                if J > 0:
                    for dI in (-1, 0, 1):
                        if 0 <= I + dI < ni: v = min(v, D[J - 1][I + dI] + 1)
                D[J][I] = v
        for J in range(nj - 1, -1, -1):
            for I in range(ni - 1, -1, -1):
                v = D[J][I]
                if v == 0: continue
                if I < ni - 1: v = min(v, D[J][I + 1] + 1)
                if J < nj - 1:
                    for dI in (-1, 0, 1):
                        if 0 <= I + dI < ni: v = min(v, D[J + 1][I + dI] + 1)
                D[J][I] = v
        dist[k] = (I0, J0, D)
        dmax = max(min(D[c[1] - J0 + dj][c[0] - I0 + di], dcap) for c in comps[k] for di in (0, 1) for dj in (0, 1))
        eave[k] = max(top[k] - slope * dmax, gmin[k] + 3.0)
    def zc(k, I, J):
        I0, J0, D = dist[k]
        return eave[k] + slope * min(D[J - J0][I - I0], dcap)
    # outlines: where a building's edge steps cell by cell (runs of one or two cells, monotone like a staircase), its
    # corners are laid on the straight line between the fixed corners at either end, so a wall that runs slantwise across
    # the raster becomes a straight slanting wall; long runs and real corners stay put
    EDG = {0: lambda i, j: ((i + 1, j), (i + 1, j + 1)), 1: lambda i, j: ((i, j), (i, j + 1)),
           2: lambda i, j: ((i, j + 1), (i + 1, j + 1)), 3: lambda i, j: ((i, j), (i + 1, j))}
    SM = {}
    for k in ids:
        adj = {}
        for (i, j) in comps[k]:
            for d, (di, dj) in enumerate(N4):
                if comp.get((i + di, j + dj)) == k: continue
                p_, q_ = EDG[d](i, j)
                adj.setdefault(p_, []).append(q_); adj.setdefault(q_, []).append(p_)
        def run(c, nxt):
            n = 0; prev = c; cur = nxt; dv = (nxt[0] - c[0], nxt[1] - c[1])
            while n < 3:
                n += 1
                nb_ = adj.get(cur, [])
                if len(nb_) != 2: break
                nn = nb_[0] if nb_[1] == prev else nb_[1]
                if (nn[0] - cur[0], nn[1] - cur[1]) != dv: break
                prev, cur = cur, nn
            return n
        free = {c for c, nb_ in adj.items() if len(nb_) == 2 and min(run(c, nb_[0]), run(c, nb_[1])) <= 2}
        pos = {c: (float(c[0]), float(c[1])) for c in adj}
        # each chain of stepped corners between two fixed corners is laid on the straight line between them, by arc length
        seen = set()
        for c in free:
            if c in seen: continue
            chain = [c]; seen.add(c); ends = []
            for side in (0, 1):
                prev, cur = c, adj[c][side]; part_ = []
                while cur in free and cur not in seen:
                    seen.add(cur); part_.append(cur)
                    nb_ = adj[cur]; nxt = nb_[0] if nb_[1] == prev else nb_[1]; prev, cur = cur, nxt
                ends.append(cur if cur not in free else None)
                chain = (part_[::-1] + chain) if side == 0 else (chain + part_)
            e0, e1 = ends
            if e0 is None or e1 is None or e0 == e1: continue
            pts = [e0] + chain + [e1]
            pieces, cur, sx, sy = [], [pts[0]], 0, 0                    # split into staircases monotone in both axes
            for q in range(1, len(pts)):
                dx = (pts[q][0] > pts[q - 1][0]) - (pts[q][0] < pts[q - 1][0]); dy = (pts[q][1] > pts[q - 1][1]) - (pts[q][1] < pts[q - 1][1])
                if (dx and sx and dx != sx) or (dy and sy and dy != sy):
                    pieces.append(cur); cur = [pts[q - 1]]; sx, sy = 0, 0
                sx = sx or dx; sy = sy or dy; cur.append(pts[q])
            pieces.append(cur)
            for pc in pieces:
                if len(pc) < 4: continue                                # a single step is a real corner
                cum = [0.0]
                for q in range(1, len(pc)): cum.append(cum[-1] + abs(pc[q][0] - pc[q - 1][0]) + abs(pc[q][1] - pc[q - 1][1]))
                (x0, y0), (x1, y1) = pc[0], pc[-1]
                if x0 == x1 or y0 == y1: continue
                for q in range(1, len(pc) - 1):
                    t = cum[q] / cum[-1]; pos[pc[q]] = (x0 + (x1 - x0) * t, y0 + (y1 - y0) * t)
        SM[k] = pos
    def P(k, I, J, z):
        x, y = SM[k].get((I, J), (I, J))
        return W(a0 + x, o0 + y, z)
    # roofs: one welded mesh per building, coplanar triangles dissolved
    for k in ids:
        part = _part(phk[k]); bm = bmesh.new(); vs = {}
        def V(I, J):
            if (I, J) not in vs: vs[(I, J)] = bm.verts.new(P(k, I, J, zc(k, I, J)))
            return vs[(I, J)]
        for (i, j) in comps[k]:
            v00, v10, v01, v11 = V(i, j), V(i + 1, j), V(i, j + 1), V(i + 1, j + 1)
            if abs(v00.co.z - v11.co.z) >= abs(v10.co.z - v01.co.z): tris = ((v00, v10, v11), (v00, v11, v01))
            else: tris = ((v00, v10, v01), (v10, v11, v01))
            for t in tris:
                try: bm.faces.new(t if sgn else t[::-1])
                except ValueError: pass
        bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(0.5), verts=bm.verts[:], edges=bm.edges[:])
        out = bm_for(part, "roof_m")
        for f in bm.faces: poly(out, [v.co.copy() for v in f.verts])
        bm.free()
    # walls on the open sides, cornices, windows
    faces = {}
    for k in ids:
        for (i, j) in comps[k]:
            for d, (di, dj) in enumerate(N4):
                n = (i + di, j + dj); q = comp.get(n)
                if q == k: continue
                if q is not None:
                    if top[q] > top[k] + 0.5: continue                       # the taller one has the wall
                    if top[q] >= top[k] - 0.5 and eave[k] <= eave[q] + 0.3: continue
                    cover = top[q] if top[q] < top[k] - 0.5 else eave[q]
                elif solid_at(n): continue
                else: cover = cells[n][2] if n in cells else (cells[(i, j)][2] if open_out else None)
                g = min(cells[(i, j)][2], cells[n][2]) if n in cells else cells[(i, j)][2]
                line = (i + 1 if d == 0 else i) if d < 2 else (j + 1 if d == 2 else j)
                pos = j if d < 2 else i
                if nowin is not None and nowin(a0 + n[0] + 0.5, o0 + n[1] + 0.5): cover = None   # windows drawn by hand there
                faces.setdefault((k, d, line), []).append((pos, None if cover is None else round(cover), g))
    nwin = 0
    for (k, d, line), lst in faces.items():
        lst.sort(); runs = []
        for pos, cov, g in lst:
            if runs and runs[-1][1] == pos and runs[-1][2] == cov: runs[-1][1] = pos + 1; runs[-1][3] = min(runs[-1][3], g)
            else: runs.append([pos, pos + 1, cov, g])
        part = _part(phk[k]); wm = (mat_of(phk[k]) if mat_of else None) or mat; e = eave[k]
        for p0, p1, cov, g in runs:
            if d == 0: c0, c1, nv = (line, p0), (line, p1), TA                # east face (+a)
            elif d == 1: c0, c1, nv = (line, p1), (line, p0), -TA             # west face
            elif d == 2: c0, c1, nv = (p1, line), (p0, line), NO              # north face (+o)
            else: c0, c1, nv = (p0, line), (p1, line), -NO                    # south face
            A_, B_ = P(k, c0[0], c0[1], 0), P(k, c1[0], c1[1], 0); uv = B_ - A_; L = uv.length
            if L < 0.05: continue
            uv = uv / L; nn_ = uv.cross(Vector((0, 0, 1)))
            if nn_.dot(nv) < 0: nn_ = -nn_
            F = Frame(A_, uv, nn_); g0 = g - 0.6
            step_ = 1 if (c1[0] - c0[0]) + (c1[1] - c0[1]) > 0 else -1
            seq = [(c0[0] + step_ * q, c0[1]) if c0[1] == c1[1] else (c0[0], c0[1] + step_ * q) for q in range(abs(c1[0] - c0[0]) + abs(c1[1] - c0[1]) + 1)]
            for q0, q1 in zip(seq, seq[1:]):                             # the wall follows every corner of the outline
                X0, X1 = P(k, q0[0], q0[1], 0), P(k, q1[0], q1[1], 0)
                poly(bm_for(part, wm), [X0 + Vector((0, 0, g0)), X1 + Vector((0, 0, g0)), X1 + Vector((0, 0, e)), X0 + Vector((0, 0, e))])
            c = -1e9 if cov is None else cov
            if c < e - 1.0: pbox(bm_for(part, trim), F, 0, L, e - 0.38, e, 0, 0.32)
            if not windows or cov is None or L < 2.6: continue
            nw = max(1, int(L / 3.5)); sp = L / nw
            if sp < 1.8: continue
            ww, wh = win; fl = g + 1.3
            while fl + wh <= e - 0.9:
                if fl > c + 0.4:
                    for q in range(nw):
                        uc = (q + 0.5) * sp
                        poly(bm_for(part, "dark"), [F.p(uc - ww / 2, fl, 0.02), F.p(uc + ww / 2, fl, 0.02), F.p(uc + ww / 2, fl + wh, 0.02), F.p(uc - ww / 2, fl + wh, 0.02)])
                        pbox(bm_for(part, trim), F, uc - ww / 2 - 0.15, uc + ww / 2 + 0.15, fl - 0.14, fl, 0, 0.1)
                        pbox(bm_for(part, trim), F, uc - ww / 2 - 0.1, uc + ww / 2 + 0.1, fl + wh, fl + wh + 0.16, 0, 0.06)
                        if shutters:
                            for s_ in (-1, 1): pbox(bm_for(part, shutters), F, uc + s_ * (ww / 2 + 0.04) - ww / 4, uc + s_ * (ww / 2 + 0.04) + ww / 4, fl, fl + wh, 0.03, 0.07)
                        nwin += 1
                fl += floor
    print("massing", len(ids), "buildings", nwin, "windows")
    return len(ids)
