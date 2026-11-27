"""Palazzo degli Uffizi – measured, dated model (v1).

Run:  blender -b --python blender/scripts/build_uffizi.py  →  web/public/models/landmarks/uffizi.glb
Frame: origin = centre of the Arno end of the Piazzale degli Uffizi (scene x 21.5 / z 437.5); X across (east), Y along the
piazzale towards Piazza della Signoria (north-north-east), Z up. The app rotates it by −0.2947 rad (axis 16.9° east of north).
Ground 0 = 48.8 m a.s.l. (DTM at the piazzale).
Measured (OSM way 477279033 + LiDAR 2023 DSM 0.5 m): piazzale 13.8 m wide and ≈139 m long; west wing ≈21 m deep, east wing
≈29 m deep (it takes in the old church of San Pier Scheraggio); Arno wing 12 m deep; roofs ≈28 m above the piazzale.
Dates (docs/landmarks/UFFIZI.md): begun 1560 (Vasari, for Cosimo I); west wing and Arno wing standing 1565, east wing 1572
(the magistracies had moved in), top loggia, cornice and roofs 1574–80 (Buontalenti, Parigi) – the years of the parts are
*inferred* from these; 28 statues of famous Tuscans in the niches 1842–56 (shown from 1850, *inferred*). Before 1560 the site holds
a stand-in quarter of houses, the Zecca and the church of San Pier Scheraggio (*conjectural* masses).
Facade module (Vasari): 19 bays a wing, each a niched pier and an architraved portico with two Doric columns, three windows on the
piano nobile (alternating triangular and segmental pediments) and the top loggia – simplified, to be refined from photographs.
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
K.reset()
MAT["stone"] = material("pietra_serena_uffizi", "pietra_serena", (0.5, 0.5, 0.47), 0.7, 0.5)
MAT["plaster"] = material("plaster_uffizi", None, (0.96, 0.92, 0.82), 0.9)          # pale cream (photographs)
MAT["marble"] = material("statue_marble", None, (0.9, 0.88, 0.84), 0.45)
MAT["rubble"] = material("old_masonry", "pietra_forte", (0.6, 0.5, 0.38), 0.9, 0.4)
MAT["shade"] = material("loggia_shade", None, (0.3, 0.29, 0.27), 0.95)                 # deep inside the loggia: in shadow all day
MAT["iron"] = material("wrought_iron", None, (0.08, 0.08, 0.08), 0.6, metal=0.6)

LEN = 140.0                       # wings run Y 0 … 140
XI = 7.0                          # piazzale half width
XW, XE = -26.0, 30.0              # outer faces of the west and east wings
YS = -12.0                        # Arno face
PORT, MEZ, NOB, TOPF, CORN, RIDGE = 7.6, 11.2, 18.4, 25.0, 26.2, 28.5
DEPTH = 4.4                       # portico depth
NB = 19; BL = LEN / NB; PW = 2.2; SW = (BL - PW) / 3

FWi = Frame((-XI, 0, 0), (0, 1, 0), (1, 0, 0))        # west wing, piazzale side
FEi = Frame((XI, 0, 0), (0, 1, 0), (-1, 0, 0))        # east wing, piazzale side
FWo = Frame((XW, 0, 0), (0, 1, 0), (-1, 0, 0))        # west wing, outer side
FEo = Frame((XE, 0, 0), (0, 1, 0), (1, 0, 0))         # east wing, outer side
FA = Frame((XW, YS, 0), (1, 0, 0), (0, -1, 0))        # Arno face (u = X + 26)

def rect_win(part, F, uc, w, v0, v1, kind=None, mat="dark"):
    poly(bm_for(part, mat), [F.p(uc - w / 2, v0, 0.05), F.p(uc + w / 2, v0, 0.05), F.p(uc + w / 2, v1, 0.05), F.p(uc - w / 2, v1, 0.05)])
    f = 0.16
    pbox(bm_for(part, "stone"), F, uc - w / 2 - f, uc - w / 2, v0 - 0.05, v1 + 0.05, 0, 0.12)
    pbox(bm_for(part, "stone"), F, uc + w / 2, uc + w / 2 + f, v0 - 0.05, v1 + 0.05, 0, 0.12)
    pbox(bm_for(part, "stone"), F, uc - w / 2 - f, uc + w / 2 + f, v1, v1 + f, 0, 0.14)
    pbox(bm_for(part, "stone"), F, uc - w / 2 - f * 1.5, uc + w / 2 + f * 1.5, v0 - 0.2, v0, 0, 0.16)          # sill
    if kind == "tri":                                                           # triangular pediment
        poly(bm_for(part, "stone"), [F.p(uc - w / 2 - 0.3, v1 + f, 0.1), F.p(uc + w / 2 + 0.3, v1 + f, 0.1), F.p(uc, v1 + f + 0.75, 0.1)])
    elif kind == "seg":                                                         # segmental pediment
        pts = [F.p(uc - w / 2 - 0.3 + (w + 0.6) * k / 8, v1 + f + 0.5 * math.sin(math.pi * k / 8), 0.1) for k in range(9)]
        poly(bm_for(part, "stone"), pts)

def inner_facade(F, tag, y_from=0.0):
    """Portico, mezzanine, piano nobile, top loggia of one wing on the piazzale."""
    P = f"{tag}@{{a}}-{NOW}"
    base = P.format(a=tag_year[tag])
    top = f"{tag}_top@1580-{NOW}"
    for j in range(3):                                                                            # the three continuous steps
        box(bm_for(base, "stone"), F, 0, LEN, 0, 0.15 * (3 - j), 0.45 * j, 0.45 * (j + 1))
    for i in range(NB):
        u0 = i * BL
        pbox(bm_for(base, "stone"), F, u0, u0 + PW, 0.45, PORT - 0.8, 0, 0.7)                     # niched pier
        box(bm_for(base, "dark"), F, u0 + 0.5, u0 + PW - 0.5, 1.6, 5.4, 0.7, 0.74)               # niche
        for k in (1, 2):                                                                          # Doric columns
            c = u0 + PW + SW * k
            box(bm_for(base, "stone"), F, c - 0.26, c + 0.26, 0.45, PORT - 0.8, 0.12, 0.64)
            box(bm_for(base, "stone"), F, c - 0.34, c + 0.34, PORT - 1.1, PORT - 0.8, 0.06, 0.7)    # capital
        for k in range(3):
            c = u0 + PW + SW * (k + 0.5)
            rect_win(base, F, c, 1.2, 12.5, 15.9, "tri" if (i + k) % 2 == 0 else "seg", "glass")
            rect_win(base, F, c, 0.9, 8.5, 9.8, None, "glass")                                  # mezzanine
            rect_win(top, F, c, 1.35, 19.3, 24.0, None, "dark")                                   # top loggia opening
    pbox(bm_for(base, "stone"), F, -0.2, LEN + 0.2, PORT - 0.8, PORT, 0, 0.75)                    # architrave
    pbox(bm_for(base, "stone"), F, -0.2, LEN + 0.2, MEZ, MEZ + 0.4, 0, 0.35)                      # string course
    pbox(bm_for(top, "stone"), F, -0.2, LEN + 0.2, NOB, NOB + 0.7, 0, 0.55)                       # string course under the loggia
    box(bm_for(top, "stone"), F, -0.3, LEN + 0.3, TOPF, CORN, 0, 1.0)                            # crown cornice

def outer_facade(F, tag, u0=0.0, u1=LEN):
    base = f"{tag}@{tag_year[tag]}-{NOW}"; top = f"{tag}_top@1580-{NOW}"
    n = int((u1 - u0) / (BL / 3))
    for i in range(n):
        c = u0 + (i + 0.5) * (u1 - u0) / n
        rect_win(base, F, c, 1.1, 2.0, 5.4, None, "glass")
        rect_win(base, F, c, 0.8, 8.4, 9.6, None, "glass")
        rect_win(base, F, c, 1.1, 12.4, 16.0, "tri" if i % 2 == 0 else "seg", "glass")
        rect_win(top, F, c, 1.1, 19.3, 23.4, None, "glass")
    pbox(bm_for(base, "stone"), F, u0 - 0.2, u1 + 0.2, MEZ, MEZ + 0.4, 0, 0.3)
    pbox(bm_for(top, "stone"), F, u0 - 0.2, u1 + 0.2, NOB, NOB + 0.5, 0, 0.4)
    pbox(bm_for(top, "stone"), F, u0 - 0.3, u1 + 0.3, TOPF, CORN, 0, 0.9)

def roof_y(part, x0, x1, y0, y1, z0, ridge, mat="roof"):
    """Roof with the ridge along Y, hipped at both ends."""
    bm = bm_for(part, mat); xm = (x0 + x1) / 2; inset = (x1 - x0) / 2 * 0.9
    poly(bm, [(x0, y0, z0), (x0, y1, z0), (xm, y1 - inset, ridge), (xm, y0 + inset, ridge)])
    poly(bm, [(x1, y1, z0), (x1, y0, z0), (xm, y0 + inset, ridge), (xm, y1 - inset, ridge)])
    poly(bm, [(x0, y0, z0), (xm, y0 + inset, ridge), (x1, y0, z0)])
    poly(bm, [(x1, y1, z0), (xm, y1 - inset, ridge), (x0, y1, z0)])

tag_year = {"west": 1565, "east": 1572, "arno": 1565}

# ---- west wing (1565), east wing (1572) ----
for tag, F, Fo, x_out, x_in, side in (("west", FWi, FWo, XW, -XI, -1), ("east", FEi, FEo, XE, XI, 1)):
    base = f"{tag}@{tag_year[tag]}-{NOW}"; top = f"{tag}_top@1580-{NOW}"
    xp = x_in + side * DEPTH                                             # back wall of the portico
    lo, hi = (min(x_out, xp), max(x_out, xp))
    wbox(bm_for(base, "plaster"), lo, hi, 0, LEN, 0, PORT)                                        # ground-floor body
    wbox(bm_for(base, "plaster"), min(x_out, x_in), max(x_out, x_in), 0, LEN, PORT, NOB)         # upper floors over the portico
    wbox(bm_for(top, "plaster"), min(x_out, x_in), max(x_out, x_in), 0, LEN, NOB, TOPF)          # loggia storey
    wbox(bm_for(base, "stone"), min(x_in, xp), max(x_in, xp), 0, LEN, 0, 0.45)                    # portico floor
    inner_facade(F, tag)
    outer_facade(Fo, tag)
    Fb = Frame((xp, 0, 0), (0, 1, 0), (-side, 0, 0))                                              # back wall of the portico: doors
    for i in range(NB):
        c = i * BL + PW + SW * 1.5
        rect_win(base, Fb, c, 1.7, 0.45, 4.0, None, "dark")
    roof_y(top, min(x_out, x_in) - 0.6, max(x_out, x_in) + 0.6, -0.6, LEN + 0.6, CORN, RIDGE)

# ---- Arno wing (1565): the loggia on the river, top loggia 1580 ----
# Its river front, measured on Oursana's photograph from across the Arno (2013, CC0; heights scaled on the LiDAR eaves, 26.2 m):
# a pietra serena frame on white plaster, ±17.8 m round the piazzale's axis. Ground floor: an open loggia through the whole
# wing (12 m deep) with three openings on the river – Vasari's serliana in the middle (a round arch 6 m wide on columns, flat
# side bays under an architrave, across the piazzale's width) and a big arch each side (5 m wide, top ≈10.5 m) opening onto
# the loggia from the Lungarno – between piers with niches and statues. Above: the entablature (10.7–12 m), the piano nobile
# with three arched windows on balconies over the serliana and a pedimented window over each side arch, a band, the top loggia
# glazed in wide bays (1580), the cornice. The blocks beyond (to the west wing's and the east wing's outer faces) are plain
# plaster with rows of windows.
a = f"arno@{tag_year['arno']}-{NOW}"; at = f"arno_top@1580-{NOW}"; ST = f"statues@1850-{NOW}"
XC = 17.8                                                                                          # the frame's half width
SPR, ENT0, ENT1 = 8.0, 10.7, 12.0                                                                  # side arches' springing, entablature
FS = Frame((XW, YS, 0), (1, 0, 0), (0, -1, 0))                                                     # river face: u = X − XW, n outwards
U = lambda x: x - XW
D = 1.0                                                                                            # the front's thickness on the loggia
wbox(bm_for(a, "plaster"), XW, -XC, YS, 0, 0, NOB)                                                 # the blocks beyond the frame
wbox(bm_for(a, "plaster"), XC, XE, YS, 0, 0, NOB)
wbox(bm_for(a, "stone"), -XC, XC, YS, 0, 0, 0.45)                                                  # the loggia's floor
wbox(bm_for(a, "stone"), -XC, XC, YS + D, 0, ENT0 - 0.3, ENT0)                                     # its ceiling (stone, coffered below)
for k in range(5):
    y = YS + D + (k + 0.5) * (-YS - D) / 5
    wbox(bm_for(a, "dark"), -XC + 0.6, XC - 0.6, y - 0.5, y + 0.5, ENT0 - 0.38, ENT0 - 0.3)
wbox(bm_for(a, "plaster"), -XC, XC, YS, 0, ENT0, NOB)                                              # the floors over it
for sgn in (-1, 1):                                                                                # the loggia's back, behind the side arches
    x0, x1 = sorted((sgn * (XI + DEPTH), sgn * XC))
    poly(bm_for(a, "shade"), [(x0, -0.03, 0.45), (x1, -0.03, 0.45), (x1, -0.03, ENT0 - 0.3), (x0, -0.03, ENT0 - 0.3)])
def arch_wall(x0, x1, spring, top, mat="plaster"):
    """The front between two piers over a round arch (x0…x1, springing, up to `top`): front and back faces, the soffit."""
    r = (x1 - x0) / 2; xc = (x0 + x1) / 2; n = 18
    ring = [(xc - r * math.cos(math.pi * k / n), spring + r * math.sin(math.pi * k / n)) for k in range(n + 1)]
    for y, flip in ((YS, False), (YS + D, True)):
        bm = bm_for(a, mat)
        for k in range(n):
            (ua, va), (ub, vb) = ring[k], ring[k + 1]
            q = [(ua, y, va), (ub, y, vb), (ub, y, top), (ua, y, top)]
            poly(bm, q[::-1] if flip else q)
    for k in range(n):                                                                             # soffit
        (ua, va), (ub, vb) = ring[k], ring[k + 1]
        poly(bm_for(a, "stone"), [(ua, YS, va), (ua, YS + D, va), (ub, YS + D, vb), (ub, YS, vb)])
    for k in range(n):                                                                             # the arch's ring in pietra serena
        (ua, va), (ub, vb) = ring[k], ring[k + 1]
        oa = ((ua - xc) * 1.14 + xc, (va - spring) * 1.14 + spring); ob = ((ub - xc) * 1.14 + xc, (vb - spring) * 1.14 + spring)
        poly(bm_for(a, "stone"), [(ua, YS - 0.08, va), (ub, YS - 0.08, vb), (ob[0], YS - 0.08, ob[1]), (oa[0], YS - 0.08, oa[1])])
def pier(x0, x1, statue=True):
    wbox(bm_for(a, "plaster"), x0, x1, YS, YS + D, 0.45, ENT0)
    pbox(bm_for(a, "stone"), FS, U(x0), U(x0) + 0.35, 0.45, ENT0, 0, 0.3)                          # pilaster strips in pietra serena
    pbox(bm_for(a, "stone"), FS, U(x1) - 0.35, U(x1), 0.45, ENT0, 0, 0.3)
    if statue:                                                                                     # niche with a statue (19th c.)
        m = (U(x0) + U(x1)) / 2
        box(bm_for(a, "dark"), FS, m - 0.55, m + 0.55, 2.0, 5.6, -0.06, 0.01)
        poly(bm_for(a, "stone"), [FS.p(m - 0.75 + 1.5 * k / 8, 5.6 + 0.55 * math.sin(math.pi * k / 8), 0.06) for k in range(9)])
        box(bm_for(ST, "stone"), FS, m - 0.4, m + 0.4, 1.4, 2.0, 0.0, 0.5)
        box(bm_for(ST, "marble"), FS, m - 0.28, m + 0.28, 2.0, 4.6, 0.02, 0.4)
        box(bm_for(ST, "marble"), FS, m - 0.14, m + 0.14, 4.6, 5.1, 0.06, 0.34)
for sgn in (-1, 1):
    xs = sorted((sgn * 17.8, sgn * 15.0)); pier(*xs)                                               # outer piers
    xs = sorted((sgn * 10.0, sgn * 7.8)); pier(*xs)                                                # inner piers
    xs = sorted((sgn * 15.0, sgn * 10.0)); arch_wall(xs[0], xs[1], SPR, ENT0)                      # the side arch
    pbox(bm_for(a, "stone"), FS, U(min(sgn * 15.0, sgn * 10.0)) - 0.1, U(max(sgn * 15.0, sgn * 10.0)) + 0.1, SPR - 0.3, SPR, 0, 0.35)   # impost
# the serliana: columns, the architrave of the side bays, the central arch
for cx in (-7.4, -3.4, 3.4, 7.4):
    wbox(bm_for(a, "stone"), cx - 0.32, cx + 0.32, YS + 0.2, YS + 0.84, 0.45, 6.5)
    wbox(bm_for(a, "stone"), cx - 0.42, cx + 0.42, YS + 0.1, YS + 0.94, 6.5, 6.8)                  # capital
for (x0, x1) in ((-7.8, -3.0), (3.0, 7.8)):
    wbox(bm_for(a, "stone"), x0, x1, YS, YS + D, 6.8, 7.6)                                         # architrave
    wbox(bm_for(a, "plaster"), x0, x1, YS, YS + D, 7.6, ENT0)                                      # wall over it
arch_wall(-3.0, 3.0, 7.6, ENT0)
# entablature across the frame, piano nobile, band, top loggia, cornice
pbox(bm_for(a, "stone"), FS, U(-XC) - 0.2, U(XC) + 0.2, ENT0, ENT1, 0, 0.5)
pbox(bm_for(a, "stone"), FS, U(-XC) - 0.3, U(XC) + 0.3, ENT1 - 0.25, ENT1, 0, 0.7)
for xc in (-6.0, 0.0, 6.0):                                                                        # three arched windows on balconies
    opening(a, FS, U(xc) - 1.2, U(xc) + 1.2, 12.7, 16.9, frame=0.32, pointed=False, fill="glass", frame_mat="stone")
    pbox(bm_for(a, "stone"), FS, U(xc) - 1.7, U(xc) + 1.7, 12.2, 12.5, 0, 0.75)                    # balcony slab
    for q in range(8): pbox(bm_for(a, "stone"), FS, U(xc) - 1.55 + q * 0.43, U(xc) - 1.45 + q * 0.43, 12.5, 13.3, 0.55, 0.68)
    pbox(bm_for(a, "stone"), FS, U(xc) - 1.7, U(xc) + 1.7, 13.3, 13.45, 0.5, 0.75)
for xc in (-12.5, 12.5):                                                                           # over the side arches
    rect_win(a, FS, U(xc), 1.6, 12.8, 15.6, "tri", "glass")
for xc in (-17.8, -15.0, -10.0, -7.8, 7.8, 10.0, 15.0, 17.8):                                      # pilasters of the piano nobile
    pbox(bm_for(a, "stone"), FS, U(xc) - 0.3, U(xc) + 0.3, ENT1, 17.5, 0, 0.22)
pbox(bm_for(a, "stone"), FS, U(-XC) - 0.2, U(XC) + 0.2, 17.5, 19.2, 0, 0.35)                      # the band under the top loggia
for xc in (-XC, XC):                                                                               # the frame's corners up to the cornice
    pbox(bm_for(at, "stone"), FS, U(xc) - 0.45, U(xc) + 0.45, 19.2, TOPF, 0, 0.3)
wbox(bm_for(at, "plaster"), XW, XE, YS, 0, NOB, TOPF)
for (x0, x1) in ((-15.6, -10.4), (-7.8, -4.3), (-3.0, 2.7), (4.0, 7.1), (9.7, 15.4), (17.6, 22.4)):   # top loggia: glazed bays
    poly(bm_for(at, "glass"), [FS.p(U(x0), 19.9, 0.03), FS.p(U(x1), 19.9, 0.03), FS.p(U(x1), 24.3, 0.03), FS.p(U(x0), 24.3, 0.03)])
    for xm in [x0 + (x1 - x0) * k / 4 for k in range(1, 4)]:                                       # glazing bars
        pbox(bm_for(at, "stone"), FS, U(xm) - 0.05, U(xm) + 0.05, 19.9, 24.3, 0.03, 0.1)
    pbox(bm_for(at, "stone"), FS, U(x0) - 0.25, U(x0), 19.6, 24.6, 0, 0.2); pbox(bm_for(at, "stone"), FS, U(x1), U(x1) + 0.25, 19.6, 24.6, 0, 0.2)
    pbox(bm_for(at, "stone"), FS, U(x0) - 0.25, U(x1) + 0.25, 19.6, 19.9, 0, 0.25); pbox(bm_for(at, "stone"), FS, U(x0) - 0.25, U(x1) + 0.25, 24.3, 24.6, 0, 0.2)
box(bm_for(at, "stone"), FS, -0.3, XE - XW + 0.3, TOPF, CORN, 0, 1.0)
# the blocks beyond the frame: rows of plain windows (ground, mezzanine, piano nobile, top)
for side_u0, side_u1 in ((U(XW) + 0.8, U(-XC) - 0.8), (U(XC) + 0.8, U(XE) - 0.8)):
    n = max(1, int((side_u1 - side_u0) / 2.6))
    for i in range(n):
        c = side_u0 + (i + 0.5) * (side_u1 - side_u0) / n
        rect_win(a, FS, c, 1.1, 2.0, 4.6, None, "glass")
        rect_win(a, FS, c, 0.8, 8.4, 9.6, None, "glass")
        rect_win(a, FS, c, 1.1, 12.6, 15.4, None, "glass")
        if side_u0 < U(0): rect_win(at, FS, c, 1.1, 20.0, 22.6, None, "glass")
bm = bm_for(at, "roof"); gable_roof(at, XW - 0.6, XE + 0.6, YS - 0.9, 0.6, CORN, RIDGE)

# ---- 28 statues of famous Tuscans in the pier niches (1842–56; shown from 1850, inferred) ----
for F in (FWi, FEi):
    for i in range(2, 16):
        u = i * BL + PW / 2
        box(bm_for(ST, "stone"), F, u - 0.4, u + 0.4, 1.6, 2.4, 0.2, 0.7)                          # plinth in the niche
        box(bm_for(ST, "marble"), F, u - 0.3, u + 0.3, 2.4, 4.7, 0.25, 0.6)                        # body
        box(bm_for(ST, "marble"), F, u - 0.15, u + 0.15, 4.7, 5.2, 0.32, 0.58)                     # head

# ---- the site before the Uffizi: a stand-in quarter, the Zecca and San Pier Scheraggio (conjectural), until 1560 ----
OLD = "old_quarter@1100-1560"
random.seed(1560)
def old_house(x0, x1, y0, y1, h, ridge_h=3.0):
    wbox(bm_for(OLD, "plaster"), x0, x1, y0, y1, 0, h)
    gable_roof(OLD, x0 - 0.3, x1 + 0.3, y0 - 0.3, y1 + 0.3, h, h + ridge_h)
    for k in range(int((x1 - x0) / 3.2)):
        Fh = Frame((x0 + 1.5 + k * 3.2, y0, 0), (1, 0, 0), (0, -1, 0))
        poly(bm_for(OLD, "dark"), [Fh.p(-0.4, h * 0.35, 0.03), Fh.p(0.4, h * 0.35, 0.03), Fh.p(0.4, h * 0.35 + 1.5, 0.03), Fh.p(-0.4, h * 0.35 + 1.5, 0.03)])
strips = [(-26, -14), (-14, -3.5), (3.5, 15), (15, 30)]
for (x0, x1) in strips:
    y = YS
    while y < LEN - 6:
        d = random.uniform(8.5, 14.0); y1 = min(y + d, LEN)
        skip = (x0 >= 3 and x1 <= 15 and y >= 94) or (x0 == 3.5 and y >= 94) or (x1 <= -14 and y >= 98)
        if not skip:
            h = random.choice((10.5, 12.0, 13.5, 15.0, 16.5))
            old_house(x0 + 0.2, x1 - 0.2, y + 0.2, y1 - 0.2, h)
        y = y1
# San Pier Scheraggio: Romanesque church, nave with a pitched roof and a bell tower (stand-in masses)
wbox(bm_for(OLD, "rubble"), 4.0, 16.0, 96.0, 134.0, 0, 12.5)
gable_roof(OLD, 3.6, 16.4, 95.6, 134.4, 12.5, 16.0)
wbox(bm_for(OLD, "rubble"), 16.0, 20.0, 108.0, 116.0, 0, 8.5)                                      # apse
wbox(bm_for(OLD, "rubble"), 4.0, 8.0, 92.0, 96.0, 0, 24.0)                                         # bell tower
wbox(bm_for(OLD, "dark"), 4.2, 7.8, 92.1, 95.9, 20.0, 23.0)
# the Zecca (Mint): a tall block at the Signoria end of the west side
wbox(bm_for(OLD, "rubble"), -26.0, -12.0, 100.0, 136.0, 0, 19.0)
for k in range(10):
    x = -26.0 + 0.8 + k * 1.4; wbox(bm_for(OLD, "rubble"), x, x + 0.8, 100.0, 100.8, 19.0, 20.2)    # battlement on the street side

K.export("uffizi")
