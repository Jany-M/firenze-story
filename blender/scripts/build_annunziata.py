"""Piazza della Santissima Annunziata – the Spedale degli Innocenti, the Loggia dei Servi di Maria and the Basilica della
Santissima Annunziata (v1).

Run:  python pipeline/44_annunziata.py   (once: outlines, ground, DSM raster → blender/data/annunziata.json)
      blender -b --python blender/scripts/build_annunziata.py  →  web/public/models/landmarks/annunziata.glb
Frame: absolute scene coordinates (Blender X = scene x, Blender Y = −scene z, Z = scene y); placed at [0, 0], rot 0, ground 0.
Inside the script positions are in the square's own frame: a along the Innocenti front (0 at its south-west end, towards
the church), o across the square (0 = the Innocenti front, 61 = the Loggia dei Servi front, from a DSM profile).
Measured: the Innocenti front 73.8 m (OSM relation 7085758; it.wikipedia: ≈71 m, nine bays); the Servi front a 5–77 m
(DSM; twelve bays); the church portico at a 82–90, o 8–48 (DSM and OSM way 234428743); the nave a 104–152, o 17.5–31.5, ≈23.6 m;
the tribuna centred at a 164, o 21, r ≈14, its dome ≈34 m above the square (DSM). Behind the fronts: buildings massed
from a 1 m raster of the DSM (landmark_mass.py).
Details from photographs (docs/materials): the three porticoes with round arches on pietra serena columns, their arches at
the same height (it.wikipedia); the Innocenti on a long flight of steps, Andrea della Robbia's blue tondi in the
spandrels, the upper floor with a pedimented window over each arch, the end bays with fluted pilasters and a portal; the
Loggia dei Servi copying it, its three south-west arches walled up with windows; the church portico with seven arches, the
wider middle one under a curved canopy, the Pucci inscription in the frieze. Column heights, depths and the end bays'
width are *inferred*.
Dates (docs/landmarks/ANNUNZIATA.md): the church founded 1250; Michelozzo's tribuna begun 1444, inaugurated 1477, the nave
1481; the Chiostrino dei Voti begun 1447 (shown 1455); the portico's middle bay attributed to Antonio Manetti (shown 1460,
*inferred*), the whole portico 1601 (Caccini); the Innocenti portico and ground floor by 1427, the upper floor after
1435 (shown 1439), opened 1445, the tondi 1487, the end tondi 1845; the Loggia dei Servi 1516–25, upper floor by 1574,
three arches walled up 1720.
"""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from mathutils import Vector
from landmark_detail import *
from landmark_text import lettering
from landmark_mass import massing
K.reset()
MAT["plaster"] = material("plaster_white", "intonaco", (0.9, 0.88, 0.82), 0.9, 0.4, tint=(1.35, 1.3, 1.18))
MAT["serena"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)
MAT["robbia"] = material("robbia_blue", None, (0.16, 0.3, 0.62), 0.35)
MAT["glaze"] = material("robbia_white", None, (0.92, 0.92, 0.9), 0.35)
MAT["letters"] = material("inscription_letters", None, (0.2, 0.19, 0.17), 0.7)
MAT["lead"] = material("lead_sheet", None, (0.42, 0.44, 0.46), 0.6, metal=0.3)
MAT["iron"] = material("wrought_iron", None, (0.08, 0.08, 0.08), 0.6, metal=0.6)
NOW = K.NOW
D = json.load(open(os.path.join(ROOT, "blender", "data", "annunziata.json"), encoding="utf-8"))
P0 = D["frame"]["p0"]; Tt = D["frame"]["t"]; Nn = D["frame"]["n"]
def W(a, o, h=0.0):
    x = P0[0] + Tt[0] * a + Nn[0] * o; z = P0[1] + Tt[1] * a + Nn[1] * o
    return Vector((x, -z, h))
TA = Vector((Tt[0], -Tt[1], 0)); NO = Vector((Nn[0], -Nn[1], 0)); Z = Vector((0, 0, 1))

# the three porticoes keep their arches at one height (it.wikipedia: the church's columns are set higher for it)
GI = D["ground_fronts"]["innocenti"] + 0.05
STEPS_I = 1.4
COL = 5.6                                   # column with base and capital (inferred)
SPRING = GI + STEPS_I + COL                 # common springing line
BAY_I = 5.84                                # Brunelleschi's bay, 10 braccia (inferred)

def spandrel(part, mat, Fr, uc, spring, r, top, n=0.0):
    bm = bm_for(part, mat); seg = 10
    for s_ in (-1, 1):
        pts = [Fr.p(uc + s_ * r * math.cos(math.pi / 2 * k / seg), spring + r * math.sin(math.pi / 2 * k / seg), n) for k in range(seg + 1)]
        corner = Fr.p(uc + s_ * r, top, n)
        for k in range(seg): poly(bm, [pts[k], pts[k + 1], corner] if s_ > 0 else [pts[k + 1], pts[k], corner])
def column(part, Fr, u, base, top, n=-0.4, r=0.3):
    pbox(bm_for(part, "serena"), Fr, u - 0.42, u + 0.42, base, base + 0.35, n - 0.42, n + 0.42)
    cylinder(part, "serena", Fr.p(u, 0, n), r, base + 0.35, top - 0.7, seg=12)
    box(bm_for(part, "serena"), Fr, u - 0.36, u + 0.36, top - 0.7, top - 0.25, n - 0.36, n + 0.36)       # capital
    box(bm_for(part, "serena"), Fr, u - 0.5, u + 0.5, top - 0.25, top, n - 0.5, n + 0.5)                 # abacus / pulvino
def tondo(part, Fr, u, v, r=0.55, n=0.02, year=None):
    for (rr, mat, d) in ((r, "robbia", 0.0), (r * 0.62, "glaze", 0.02)):
        bm = bm_for(part, mat)
        poly(bm, [Fr.p(u + rr * math.cos(2 * math.pi * k / 16), v + rr * math.sin(2 * math.pi * k / 16), n + d) for k in range(16)])
def pediment(part, Fr, u, v, w, h=0.45, n=0.0, mat="serena"):
    pbox(bm_for(part, mat), Fr, u - w / 2, u + w / 2, v, v + 0.12, n, n + 0.2)
    bm = bm_for(part, mat); poly(bm, [Fr.p(u - w / 2, v + 0.12, n + 0.18), Fr.p(u + w / 2, v + 0.12, n + 0.18), Fr.p(u, v + 0.12 + h, n + 0.18)])
def steps(part, Fr, u0, u1, ground, top, run=0.42, mat="serena"):
    n_ = max(1, round((top - ground) / 0.16)); hstep = (top - ground) / n_
    for k in range(n_):
        box(bm_for(part, mat), Fr, u0, u1, ground - 0.5, ground + hstep * (k + 1), 0, (n_ - k) * run)

def loggia(parts, Fr, u0, nb, bay, floor, spring, depth, top, ends=(), back_doors=(), walled=(), walled_part=None):
    """An arcade of nb round arches on columns along Fr (u from u0), its back wall `depth` behind, a flat vault between.
    parts = (arcade, back); walled: bays closed with a wall and a window (walled_part)."""
    pa, pb = parts; r = bay / 2 - 0.2
    for k in range(nb + 1): column(pa, Fr, u0 + k * bay, floor, spring)
    for k in range(nb):
        uc = u0 + (k + 0.5) * bay
        spandrel(pa, "plaster", Fr, uc, spring, r, top)
        ring(pa, "serena", Fr, uc, spring, r, r + 0.32, 0, 0.1, seg=12, soffit=True)
        if k in walled:
            wp = walled_part
            arch_fill(wp, "plaster", Fr, uc - r, uc + r, floor, spring, n=-0.3)
            win_rect(wp, Fr, uc, floor + 1.4, floor + 3.6, 1.2, frame="serena", fill="dark", fw=0.16)
    # back wall with doors and windows, the vault, the floor of the portico
    u1 = u0 + nb * bay
    box(bm_for(pb, "plaster"), Fr, u0, u1, floor - 0.5, top, -depth - 0.6, -depth)
    for k in range(nb):
        uc = u0 + (k + 0.5) * bay
        if k in back_doors:
            poly(bm_for(pb, "dark"), [Fr.p(uc - 0.8, floor, -depth + 0.02), Fr.p(uc + 0.8, floor, -depth + 0.02), Fr.p(uc + 0.8, floor + 3.4, -depth + 0.02), Fr.p(uc - 0.8, floor + 3.4, -depth + 0.02)])
            pbox(bm_for(pb, "serena"), Fr, uc - 1.05, uc + 1.05, floor + 3.4, floor + 3.65, -depth, -depth + 0.15)
        else:
            poly(bm_for(pb, "dark"), [Fr.p(uc - 0.55, floor + 1.4, -depth + 0.02), Fr.p(uc + 0.55, floor + 1.4, -depth + 0.02), Fr.p(uc + 0.55, floor + 3.2, -depth + 0.02), Fr.p(uc - 0.55, floor + 3.2, -depth + 0.02)])
    poly(bm_for(pb, "plaster"), [Fr.p(u0, spring + r, -depth), Fr.p(u1, spring + r, -depth), Fr.p(u1, spring + r, 0), Fr.p(u0, spring + r, 0)][::-1])
    box(bm_for(pa, "serena"), Fr, u0, u1, floor - 0.3, floor, -depth, 0)

def upper(part, Fr, u0, u1, v0, eave, centres, win=(1.1, 1.9), sill=1.3, shutters=False):
    box(bm_for(part, "plaster"), Fr, u0, u1, v0, eave, -1.2, 0)
    pbox(bm_for(part, "serena"), Fr, u0, u1, v0 + sill - 0.12, v0 + sill, 0, 0.12)                       # sill band
    for uc in centres:
        w, h = win; s0 = v0 + sill
        win_rect(part, Fr, uc, s0, s0 + h, w, frame="serena", fill="dark", fw=0.14)
        pediment(part, Fr, uc, s0 + h + 0.14, w + 0.5)
        if shutters:
            for s_ in (-1, 1): pbox(bm_for(part, "shutter"), Fr, uc + s_ * (w / 2 + 0.05) - 0.27, uc + s_ * (w / 2 + 0.05) + 0.27, s0, s0 + h, 0.05, 0.1)
    pbox(bm_for(part, "serena"), Fr, u0 - 0.1, u1 + 0.1, eave - 0.3, eave, 0, 0.5)                          # gutter cornice
MAT["shutter"] = material("shutters_grey", None, (0.55, 0.58, 0.58), 0.7)

def roof_strip(part, Fr, u0, u1, n_front, n_back, z, ridge):
    m = (n_front + n_back) / 2; bm = bm_for(part, "roof")
    poly(bm, [Fr.p(u0, z, n_front + 0.5), Fr.p(u1, z, n_front + 0.5), Fr.p(u1, ridge, m), Fr.p(u0, ridge, m)])
    poly(bm, [Fr.p(u1, z, n_back), Fr.p(u0, z, n_back), Fr.p(u0, ridge, m), Fr.p(u1, ridge, m)])
    for u in (u0, u1): poly(bm_for(part, "plaster"), [Fr.p(u, z, n_front), Fr.p(u, z, n_back), Fr.p(u, ridge, m)])

# ------------------------------------------------------------------ Spedale degli Innocenti
def innocenti():
    F = Frame(W(0, 0), TA, NO); L = 73.8
    E = (L - 9 * BAY_I) / 2                                       # end bays (≈10.6 m)
    fl = GI + STEPS_I; top = SPRING + BAY_I / 2 + 0.35; ent = top + 1.0; eave = ent + 5.6
    p_port, p_up, p_end = f"innocenti_portico@1427-{NOW}", f"innocenti_piano@1439-{NOW}", f"innocenti_testate@1439-{NOW}"
    steps(p_port, F, 0, L, GI - 0.6, fl, run=0.36)
    loggia((p_port, p_port), F, E, 9, BAY_I, fl, SPRING, 6.2, top, back_doors=(1, 4, 7))
    entablature(p_port, F, E - 0.3, E + 9 * BAY_I + 0.3, top, mat="serena", h=1.0, proj=0.45)
    # Andrea della Robbia's tondi (1487) in the spandrels and at both ends of the arcade
    for k in range(10): tondo(f"innocenti_tondi@1487-{NOW}", F, E + k * BAY_I, SPRING + BAY_I / 2 - 0.3, r=0.55, n=0.03)
    # end bays: solid, fluted pilasters, a portal with a pediment (the right one Francesco della Luna's blind bay)
    for (u0, u1, oc) in ((0, E, True), (L - E, L, False)):
        box(bm_for(p_end, "plaster"), F, u0, u1, fl - 0.5, ent, -6.8, 0)
        for u in (u0 + 0.6, u1 - 0.6):
            pbox(bm_for(p_end, "serena"), F, u - 0.4, u + 0.4, fl, top, 0, 0.18)
            for f_ in (-0.24, -0.08, 0.08, 0.24): pbox(bm_for(p_end, "dark"), F, u + f_ - 0.03, u + f_ + 0.03, fl + 0.6, top - 0.7, 0.18, 0.19)
        uc = (u0 + u1) / 2
        poly(bm_for(p_end, "dark"), [F.p(uc - 0.9, fl, 0.02), F.p(uc + 0.9, fl, 0.02), F.p(uc + 0.9, fl + 3.6, 0.02), F.p(uc - 0.9, fl + 3.6, 0.02)])
        pbox(bm_for(p_end, "serena"), F, uc - 1.15, uc - 0.9, fl, fl + 3.6, 0, 0.12); pbox(bm_for(p_end, "serena"), F, uc + 0.9, uc + 1.15, fl, fl + 3.6, 0, 0.12)
        pediment(p_end, F, uc, fl + 3.6, 2.6, h=0.6)
        if oc: oculus(p_end, F, uc, fl + 6.0, 0.6, frame="serena", fill="dark", fw=0.2)
        tondo(f"innocenti_tondi_1845@1845-{NOW}", F, u1 - 1.6 if u0 == 0 else u0 + 1.6, SPRING + BAY_I / 2 - 0.3, r=0.5, n=0.2)
    entablature(p_end, F, 0, E, top, mat="serena", h=1.0, proj=0.45); entablature(p_end, F, L - E, L, top, mat="serena", h=1.0, proj=0.45)
    # the upper floor (after 1435): a window with a pediment over each arch and in the end bays
    cs = [E + (k + 0.5) * BAY_I for k in range(9)] + [E / 2, L - E / 2]
    upper(p_up, F, 0, L, ent, eave, cs)
    box(bm_for(p_up, "plaster"), F, 0, L, ent, eave, -11.0, -1.2)
    roof_strip(p_up, F, 0, L, 0.0, -11.0, eave, eave + 2.8)
innocenti()

# ------------------------------------------------------------------ Loggia dei Servi di Maria (opposite, facing the Innocenti)
def servi():
    GS = D["ground_fronts"]["servi"] + 0.05
    F = Frame(W(77, 61), -TA, -NO); L = 72.0; nb = 12; bay = L / nb
    fl = max(GS + 0.6, SPRING - COL)                              # its steps, as high as the arches allow
    top = SPRING + bay / 2 + 0.35; ent = top + 1.0; eave = ent + 6.0
    p_l, p_up = f"servi_loggia@1525-{NOW}", f"servi_piano@1574-{NOW}"
    steps(p_l, F, 0, L, GS - 0.6, fl, run=0.4)
    # the three arches at the south-west end (u = 54–72 here) were walled up in 1720
    loggia((p_l, p_l), F, 0, nb, bay, fl, SPRING, 6.0, top, back_doors=(1, 4, 7, 10), walled=(9, 10, 11), walled_part=f"servi_chiuse@1720-{NOW}")
    entablature(p_l, F, -0.3, L + 0.3, top, mat="serena", h=1.0, proj=0.45)
    for k in range(nb + 1): tondo(f"servi_tondi@1525-{NOW}", F, k * bay, SPRING + bay / 2 - 0.3, r=0.5, n=0.03)
    upper(p_up, F, 0, L, ent, eave, [(k + 0.5) * bay for k in range(nb)], win=(1.1, 2.0), shutters=True)
    box(bm_for(p_up, "plaster"), F, 0, L, ent, eave, -11.5, -1.2)
    roof_strip(p_up, F, 0, L, 0.0, -11.5, eave, eave + 2.6)
servi()

# ------------------------------------------------------------------ Basilica della Santissima Annunziata
def chiesa():
    GC = D["ground_fronts"]["chiesa"] + 0.05
    F = Frame(W(82, 48), -NO, -TA); L = 40.0                       # the portico front, u along o from 48 to 8
    fl = GC + 0.35; spring = SPRING; top_ = spring + 3.4 + 0.35; ent = top_ + 0.2; attic = ent + 2.2
    end = 1.6; mid = 6.8; side = (L - 2 * end - mid) / 6
    us = [end + k * side for k in range(4)] + [end + 3 * side + mid + k * side for k in range(4)]   # column positions
    p_mid, p_all = "chiesa_arco@1460-1601", f"chiesa_portico@1601-{NOW}"
    # 1460–1601: the middle bay only (attributed to Antonio Manetti; year inferred), on its own
    uc = L / 2; rm = mid / 2 - 0.3
    for u in (uc - mid / 2, uc + mid / 2): column(p_mid, F, u, fl, spring)
    spandrel(p_mid, "plaster", F, uc, spring, rm, top_ + 0.6); ring(p_mid, "serena", F, uc, spring, rm, rm + 0.35, 0, 0.12, seg=14)
    box(bm_for(p_mid, "plaster"), F, uc - mid / 2 - 0.4, uc + mid / 2 + 0.4, top_ + 0.6, attic, -8, 0.0)
    # 1601: Caccini's portico of seven arches between two pilastered ends
    box(bm_for(p_all, "serena"), F, 0, L, fl - 0.6, fl, -8, 0.4)
    for u in us: column(p_all, F, u, fl, spring)
    for k in range(7):
        a_, b_ = (us[k], us[k + 1]); c_ = (a_ + b_) / 2; r = (b_ - a_) / 2 - 0.25
        spandrel(p_all, "plaster", F, c_, spring, r, ent)
        ring(p_all, "serena", F, c_, spring, r, r + 0.32, 0, 0.12, seg=14)
    for (u0, u1) in ((0, end), (L - end, L)):
        box(bm_for(p_all, "serena"), F, u0, u1, fl, attic + 0.6, -8, 0.15)                            # end pilasters
        box(bm_for(p_all, "serena"), F, u0 + 0.15, u1 - 0.15, attic - 0.6, attic + 0.2, 0.15, 0.4)     # capitals
    # the canopy over the middle arch
    bm = bm_for(p_all, "lead"); seg = 12; rc = mid / 2 + 0.3
    for k in range(seg):
        t0, t1 = math.pi * k / seg, math.pi * (k + 1) / seg
        poly(bm, [F.p(uc + rc * math.cos(t0), spring + 3.6 + 0.9 * math.sin(t0), 1.2), F.p(uc + rc * math.cos(t1), spring + 3.6 + 0.9 * math.sin(t1), 1.2),
                  F.p(uc + rc * math.cos(t1), spring + 3.6 + 0.9 * math.sin(t1), 0), F.p(uc + rc * math.cos(t0), spring + 3.6 + 0.9 * math.sin(t0), 0)])
    # entablature with the Pucci inscription, the attic with urns, the back wall with three doors
    pbox(bm_for(p_all, "serena"), F, end, L - end, ent, ent + 0.35, 0, 0.35)
    pbox(bm_for(p_all, "plaster"), F, end, L - end, ent + 0.35, ent + 1.25, 0, 0.25)
    lettering(p_all, "letters", F, uc, ent + 0.55, 0.25, "ALEXANDER ET ROBERTVS PVCCII FRATRES DEI GENITRICI", 0.55, width=L - 2 * end - 1.0)
    pbox(bm_for(p_all, "serena"), F, end - 0.2, L - end + 0.2, ent + 1.25, ent + 1.7, 0, 0.6)
    box(bm_for(p_all, "plaster"), F, 0, L, ent + 1.7, attic + 0.6, -8, 0.2)
    pbox(bm_for(p_all, "serena"), F, -0.2, L + 0.2, attic + 0.6, attic + 0.85, 0, 0.45)
    for u in us[1:-1]: cylinder(p_all, "serena", F.p(u, 0, -0.1), 0.25, attic + 0.85, attic + 1.6, seg=8)
    box(bm_for(p_all, "plaster"), F, 0, L, fl - 0.5, attic, -8.6, -8.0)
    for (u, w, h) in ((uc, 2.4, 5.2), (us[1] + side / 2, 1.5, 3.6), (us[-2] - side / 2, 1.5, 3.6)):
        poly(bm_for(p_all, "dark"), [F.p(u - w / 2, fl, -7.98), F.p(u + w / 2, fl, -7.98), F.p(u + w / 2, fl + h, -7.98), F.p(u - w / 2, fl + h, -7.98)])
        pediment(p_all, F, u, fl + h, w + 0.6, h=0.5, n=-7.98)
    poly(bm_for(p_all, "plaster"), [F.p(0, spring + 3.0, -8), F.p(L, spring + 3.0, -8), F.p(L, spring + 3.0, 0), F.p(0, spring + 3.0, 0)][::-1])
    poly(bm_for(p_all, "lead"), [F.p(0, attic + 0.6, -8), F.p(L, attic + 0.6, -8), F.p(L, attic + 0.6, 0.2), F.p(0, attic + 0.6, 0.2)])
    # the church: before Michelozzo a lower nave (1250), then his nave (1481) between rows of side chapels, and the round
    # tribuna (1477). DSM: the nave o 17.5–31.5, ridge ≈23.6 m above the square; the tribuna centred at a 164, o 21,
    # its round wall r ≈14 up to ≈26.5 m, a ring of roof to the dome's foot at ≈28 m, the dome to ≈34 m.
    NV = (17.5, 31.5)
    def nave(part, z1, ridge, clerestory=False):
        Fn = Frame(W(104, NV[0]), TA, NO)
        box(bm_for(part, "plaster"), Fn, 0, 48, GC - 0.5, z1, 0, NV[1] - NV[0])
        pbox(bm_for(part, "serena"), Fn, -0.2, 48.2, z1 - 0.4, z1, -0.3, NV[1] - NV[0] + 0.3)        # eaves cornice
        bm = bm_for(part, "roof"); om = sum(NV) / 2
        poly(bm, [W(103.6, NV[0] - 0.5, z1), W(152, NV[0] - 0.5, z1), W(152, om, ridge), W(103.6, om, ridge)][::-1])
        poly(bm, [W(152, NV[1] + 0.5, z1), W(103.6, NV[1] + 0.5, z1), W(103.6, om, ridge), W(152, om, ridge)][::-1])
        for a in (104, 152): poly(bm_for(part, "plaster"), [W(a, NV[0], z1), W(a, NV[1], z1), W(a, om, ridge)])
        if clerestory:                    # a round-headed window over each of the five chapels on both sides (*inferred*)
            for (Fw, L_) in ((Frame(W(104, NV[0]), TA, -NO), 48), (Frame(W(152, NV[1]), -TA, NO), 48)):
                for k in range(5):
                    uc = 4.0 + (k + 0.5) * 8.0
                    arch_fill(part, "dark", Fw, uc - 0.9, uc + 0.9, GC + 14.6, GC + 17.4, n=0.03)
                    ring(part, "serena", Fw, uc, GC + 17.4, 0.9, 1.08, 0, 0.1, seg=10, soffit=False)
                    pbox(bm_for(part, "serena"), Fw, uc - 1.1, uc + 1.1, GC + 14.45, GC + 14.6, 0, 0.12)
    nave("chiesa_1250@1250-1481", GC + 13.0, GC + 16.0)
    nave(f"chiesa_navata@1481-{NOW}", GC + 20.6, GC + 23.8, clerestory=True)
    c = W(164, 21); pr = f"chiesa_tribuna@1477-{NOW}"; R = 14.0; E_ = GC + 26.5
    cylinder(pr, "plaster", c, R, GC - 0.5, E_, seg=32)
    for k in range(16):                                                # pietra serena pilaster strips and the cornice
        t = 2 * math.pi * k / 16; d = Vector((math.cos(t), math.sin(t), 0))
        Fp = Frame(c + d * R, Vector((-d.y, d.x, 0)), d)
        pbox(bm_for(pr, "serena"), Fp, -0.45, 0.45, GC + 6.0, E_ - 0.6, -0.1, 0.18)
    cylinder(pr, "serena", c, R + 0.35, E_ - 0.6, E_, seg=32)
    cone(pr, "tile", c, R + 0.6, 10.3, E_, GC + 28.2, seg=32)              # the ring roof over the chapels
    cylinder(pr, "plaster", c, 10.0, GC + 26.0, GC + 28.6, seg=32)
    cylinder(pr, "serena", c, 10.2, GC + 28.3, GC + 28.6, seg=32)
    dome(pr, c, 10.2, GC + 28.6, 5.4, ribs=8, mat="tile", seg=32, rib_mat="serena")
    cylinder(pr, "serena", c, 1.1, GC + 33.8, GC + 35.8, seg=8); cone(pr, "lead", c, 1.35, 0.1, GC + 35.8, GC + 37.2, seg=8)
    sphere(pr, "lead", c + Vector((0, 0, GC + 37.4)), 0.3)
    # the campanile a vela (it.wikipedia: a bell gable with five openings on the rear drum; the DSM has a narrow peak
    # ≈37 m high where the tribuna meets the nave on the north side). Its face and the order of the openings: *inferred*.
    pv = f"chiesa_campanile@1477-{NOW}"; Fv = Frame(W(154.0, 30.2), NO, -TA); vb, vt = E_ - 1.0, GC + 36.2
    box(bm_for(pv, "plaster"), Fv, -1.8, 1.8, vb, vt - 1.2, -0.45, 0.45)
    bmv = bm_for(pv, "plaster")
    for nn in (0.45, -0.45):
        pts = [Fv.p(-1.8, vt - 1.2, nn), Fv.p(1.8, vt - 1.2, nn), Fv.p(0, vt, nn)]
        poly(bmv, pts if nn > 0 else pts[::-1])
    poly(bm_for(pv, "roof"), [Fv.p(-1.95, vt - 1.25, 0.55), Fv.p(-1.95, vt - 1.25, -0.55), Fv.p(0, vt + 0.05, -0.55), Fv.p(0, vt + 0.05, 0.55)])
    poly(bm_for(pv, "roof"), [Fv.p(1.95, vt - 1.25, -0.55), Fv.p(1.95, vt - 1.25, 0.55), Fv.p(0, vt + 0.05, 0.55), Fv.p(0, vt + 0.05, -0.55)])
    for (u, v0) in ((-1.15, E_ + 2.6), (0.0, E_ + 2.6), (1.15, E_ + 2.6), (-0.58, E_ + 5.6), (0.58, E_ + 5.6)):
        for nn in (0.47, -0.47):
            Fo = Frame(Fv.p(0, 0, nn), Fv.u if nn > 0 else -Fv.u, Fv.n if nn > 0 else -Fv.n)
            uu = u if nn > 0 else -u
            arch_fill(pv, "dark", Fo, uu - 0.36, uu + 0.36, v0, v0 + 1.4, n=0.0)
    pbox(bm_for(pv, "serena"), Fv, -1.9, 1.9, E_ + 1.9, E_ + 2.1, -0.5, 0.5)
    cylinder(pv, "iron", Fv.p(0, vt, 0), 0.04, vt, vt + 1.0, seg=4)
    # the Chiostrino dei Voti (1447, shown 1455) between the portico and the church: arcades on its two long sides; closed
    # with an iron and glass roof under Leopold II (ermakvagus.com; shown 1850, *inferred*, before the 1857 restoration)
    # photographs (Sailko; Bernoud c. 1865): an arcade on all four sides on slender Corinthian columns, the church's door under
    # the far side; above the arches a floor with ochre panels, tondi and small paired windows, under the glazed roof
    pc = f"chiostrino@1455-{NOW}"; zg = GC + 10.0
    MAT["ochre"] = material("plaster_ochre_annunziata", None, (0.86, 0.66, 0.42), 0.9)
    MAT["skylight"] = material("skylight_glass", None, (0.78, 0.82, 0.84), 0.25)
    CA, CO = (93.1, 101.4), (19.8, 30.2)                               # the open court; the walks round it to the walls
    sides = ((Frame(W(90.5, CO[0]), TA, NO), 13.5, 3, 2.8, ()), (Frame(W(104.0, CO[1]), -TA, -NO), 13.5, 3, 2.8, ()),
             (Frame(W(CA[1], 17.0), NO, -TA), 16.0, 4, 2.6, (1, 2)), (Frame(W(CA[0], 33.0), -NO, TA), 16.0, 4, 2.6, (1, 2)))
    for (Fq, Lq, nb_, dq, doors) in sides:
        bay_ = (Lq - 0.6) / nb_; sp_ = fl + 4.4; top_q = sp_ + bay_ / 2 - 0.2 + 0.35
        loggia((pc, pc), Fq, 0.3, nb_, bay_, fl, sp_, dq, top_q, back_doors=doors)
        box(bm_for(pc, "ochre"), Fq, 0, Lq, top_q, zg, -dq - 0.6, 0)                       # the upper floor
        pbox(bm_for(pc, "serena"), Fq, 0, Lq, top_q, top_q + 0.25, 0, 0.12)
        pbox(bm_for(pc, "serena"), Fq, 0, Lq, zg - 0.3, zg, 0, 0.3)
        poly(bm_for(pc, "roof"), [Fq.p(-0.4, zg + 1.0, -dq - 0.6), Fq.p(Lq + 0.4, zg + 1.0, -dq - 0.6), Fq.p(Lq + 0.4, zg, 0.3), Fq.p(-0.4, zg, 0.3)])
        for k in range(nb_):
            uc = 0.3 + (k + 0.5) * bay_
            for du in (-0.38, 0.38):
                poly(bm_for(pc, "dark"), [Fq.p(uc + du - 0.28, top_q + 1.0, 0.02), Fq.p(uc + du + 0.28, top_q + 1.0, 0.02), Fq.p(uc + du + 0.28, top_q + 1.8, 0.02), Fq.p(uc + du - 0.28, top_q + 1.8, 0.02)])
            pbox(bm_for(pc, "serena"), Fq, uc - 0.85, uc + 0.85, top_q + 0.86, top_q + 1.0, 0, 0.1)
            if k: tondo(pc, Fq, 0.3 + k * bay_, sp_ + bay_ / 2 - 0.1, r=0.5, n=0.03)
    pg = f"chiostrino_vetri@1850-{NOW}"
    bmg = bm_for(pg, "skylight")
    hm_ = (CA[1] - CA[0]) / 2; am_ = (CA[0] + CA[1]) / 2; zr = zg + 2.0
    A_, B_, C_, D_ = W(CA[0], CO[0], zg), W(CA[1], CO[0], zg), W(CA[1], CO[1], zg), W(CA[0], CO[1], zg)
    R0, R1 = W(am_, CO[0] + hm_, zr), W(am_, CO[1] - hm_, zr)
    for q in ([A_, B_, R0], [B_, C_, R1, R0], [C_, D_, R1], [D_, A_, R0, R1]): poly(bmg, q[::-1])
    for k in range(1, 5):                                              # iron ribs
        o_ = CO[0] + (CO[1] - CO[0]) * k / 5; oc_ = min(max(o_, CO[0] + hm_), CO[1] - hm_)
        poly(bm_for(pg, "iron"), [W(CA[0], o_ - 0.05, zg + 0.02), W(CA[0], o_ + 0.05, zg + 0.02), W(am_, oc_ + 0.05, zr + 0.02), W(am_, oc_ - 0.05, zr + 0.02)])
        poly(bm_for(pg, "iron"), [W(CA[1], o_ + 0.05, zg + 0.02), W(CA[1], o_ - 0.05, zg + 0.02), W(am_, oc_ - 0.05, zr + 0.02), W(am_, oc_ + 0.05, zr + 0.02)])
    for (Fq, Lq) in ((Frame(W(CA[0], CO[0]), TA, -NO), CA[1] - CA[0]), (Frame(W(CA[1], CO[1]), -TA, NO), CA[1] - CA[0]), (Frame(W(CA[1], CO[0]), NO, TA), CO[1] - CO[0]), (Frame(W(CA[0], CO[1]), -NO, -TA), CO[1] - CO[0])):
        pbox(bm_for(pg, "iron"), Fq, 0, Lq, zg, zg + 0.45, -0.05, 0.05)                       # the cresting round the glass
chiesa()
NVS = (17.5, 31.5)

# ------------------------------------------------------------------ everything behind the fronts: massing from the DSM
# (blender/scripts/landmark_mass.py): the wards and cloisters of the Innocenti, the houses over the Loggia dei Servi, the
# chapels and convent rooms round the church – hipped roofs at the heights the DSM gives, walls, cornices and windows.
# Their layout is the DSM's; the form of each roof and window is *generic*, to be refined.
def cells_of(key, phase_of, skip=None):
    g = D["grid"][key]; out = {}
    for j in range(g["no"]):
        for i in range(g["na"]):
            h = g["h"][j][i]
            if h is None: continue
            a, o = g["a0"] + i + 0.5, g["o0"] + j + 0.5
            if skip and skip(a, o): continue
            out[(i, j)] = (phase_of(a, o), h, g["g"][j][i])
    return g["a0"], g["o0"], out
a0_, o0_, cs_ = cells_of("innocenti", lambda a, o: ("innocenti_corpi", 1445))
massing(cs_, a0_, o0_, W, TA, NO, solid=lambda a, o: -12.0 < o < 1 and -1 < a < 75)
a0_, o0_, cs_ = cells_of("servi", lambda a, o: ("servi_case", 1574))
massing(cs_, a0_, o0_, W, TA, NO, solid=lambda a, o: o < 73.0 and 4 < a < 78, shutters="shutter")
a0_, o0_, cs_ = cells_of("chiesa", lambda a, o: ("chiesa_chiostrino", 1455) if a < 104 else ("chiesa_cappelle", 1481),
                         skip=lambda a, o: 90.5 <= a <= 104 and 17.0 <= o <= 33.0)
massing(cs_, a0_, o0_, W, TA, NO, solid=lambda a, o: (104 <= a <= 152 and NVS[0] - 0.5 <= o <= NVS[1] + 0.5) or (a - 164) ** 2 + (o - 21) ** 2 < 14.6 ** 2 or a < 90.6)
K.export("annunziata")
