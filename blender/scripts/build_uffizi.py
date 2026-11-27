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
MAT["plaster"] = material("plaster_uffizi", None, (0.84, 0.78, 0.64), 0.9)
MAT["marble"] = material("statue_marble", None, (0.9, 0.88, 0.84), 0.45)
MAT["rubble"] = material("old_masonry", "pietra_forte", (0.6, 0.5, 0.38), 0.9, 0.4)
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

# ---- Arno wing (1565) with the serliana, top loggia 1580 ----
a = f"arno@{tag_year['arno']}-{NOW}"; at = f"arno_top@1580-{NOW}"
# the two porticoes of the long wings run on through the Arno wing and open onto the Lungarno in a big arch each (photographs:
# Oursana 2013 from across the river, Txllxt TxllxT 2010 from the Lungarno, Joanbanjo 2011): the passage X ±(7…11.4) is open
# to the vault (≈11 m), the coffered vault over it, the arch ringed in pietra serena between pilasters, niches with statues
XP = XI + DEPTH
wbox(bm_for(a, "plaster"), XW, -XP, YS, 0, 0, NOB)                                                # left block
wbox(bm_for(a, "plaster"), XP, XE, YS, 0, 0, NOB)                                                 # right block
for (x0, x1) in ((-XP, -XI), (XI, XP)):
    wbox(bm_for(a, "plaster"), x0, x1, YS, 0, 11.0, NOB)                                         # over the passage
    wbox(bm_for(a, "stone"), x0, x1, YS, 0, 10.7, 11.0)                                          # its vault (coffered: stone)
    wbox(bm_for(a, "stone"), x0, x1, YS, 0, 0, 0.45)                                             # its floor
    for k in range(4):                                                                           # coffer ribs
        y = YS + (k + 0.5) * (-YS) / 4
        wbox(bm_for(a, "dark"), x0 + 0.5, x1 - 0.5, y - 0.6, y + 0.6, 10.62, 10.7)
wbox(bm_for(a, "plaster"), -XI, XI, YS, 0, 12.0, NOB)                                             # over the passage (above the screen)
wbox(bm_for(at, "plaster"), XW, XE, YS, 0, NOB, TOPF)
wbox(bm_for(a, "stone"), -XI, XI, YS - 0.9, YS + 0.2, 0, 0.45)                                    # steps / threshold
FS = Frame((XW, YS, 0), (1, 0, 0), (0, -1, 0))
for cx in (-XI + 0.3, -3.6, 3.6, XI - 0.3):                                                       # Doric screen (serliana): columns
    pbox(bm_for(a, "stone"), FS, cx - XW - 0.32, cx - XW + 0.32, 0.45, PORT - 0.8, 0.0, 0.9)
    pbox(bm_for(a, "stone"), FS, cx - XW - 0.42, cx - XW + 0.42, PORT - 1.1, PORT - 0.8, 0.0, 0.95)
box(bm_for(a, "stone"), FS, -XI - XW, XI - XW, PORT - 0.8, PORT, 0, 1.0)                           # architrave
for k in range(16):                                                                                # central arch of the serliana (ring)
    a0, a1 = math.pi * k / 16, math.pi * (k + 1) / 16; r0, r1 = 3.3, 4.1; cz = 8.7
    c = -XW
    for n in (0.0, 0.9):
        poly(bm_for(a, "stone"), [FS.p(c + r0 * math.cos(a0), cz + r0 * math.sin(a0), n), FS.p(c + r0 * math.cos(a1), cz + r0 * math.sin(a1), n),
                                  FS.p(c + r1 * math.cos(a1), cz + r1 * math.sin(a1), n), FS.p(c + r1 * math.cos(a0), cz + r1 * math.sin(a0), n)])
for (s0, s1) in ((-6.6, -3.4), (3.4, 6.6)):                                                      # spandrel blocks beside the arch
    pbox(bm_for(a, "stone"), FS, -XW + s0, -XW + s1, PORT, 12.0, 0, 0.5)
for xc in (-(XI + XP) / 2, (XI + XP) / 2):                                                         # the two side arches
    uc = xc - XW; rr = (XP - XI) / 2 - 0.15
    for k in range(16):
        a0, a1 = math.pi * k / 16, math.pi * (k + 1) / 16
        for n in (0.0, 0.6):
            poly(bm_for(a, "stone"), [FS.p(uc + rr * math.cos(a0), PORT + rr * math.sin(a0), n), FS.p(uc + rr * math.cos(a1), PORT + rr * math.sin(a1), n),
                                      FS.p(uc + (rr + 0.7) * math.cos(a1), PORT + (rr + 0.7) * math.sin(a1), n), FS.p(uc + (rr + 0.7) * math.cos(a0), PORT + (rr + 0.7) * math.sin(a0), n)])
    pts = [FS.p(uc + rr * math.cos(math.pi * k / 16), PORT + rr * math.sin(math.pi * k / 16), 0.0) for k in range(17)]
    sp = [FS.p(uc - rr - 0.7, PORT, 0.0), FS.p(uc + rr + 0.7, PORT, 0.0)]
    for k in range(16):                                                                          # spandrel up to the vault line
        poly(bm_for(a, "plaster"), [pts[k], pts[k + 1], FS.p(uc + (rr + 0.7) * (1 if k < 8 else -1), 11.0, 0.0)])
    poly(bm_for(a, "plaster"), [FS.p(uc - rr - 0.7, 11.0, 0), FS.p(uc + rr + 0.7, 11.0, 0), pts[8]])
    for s_ in (-1, 1):                                                                           # pilasters, a niche with a statue
        u = uc + s_ * (rr + 0.7 + 0.45)
        pbox(bm_for(a, "stone"), FS, u - 0.45, u + 0.45, 0.45, PORT, 0, 0.5)
        pbox(bm_for(a, "stone"), FS, u - 0.55, u + 0.55, PORT, PORT + 0.4, 0, 0.6)
    for s_ in ((1 if xc > 0 else -1),):                                                          # the niche on the outer side
        u = uc + s_ * (rr + 2.6)
        if True:
            box(bm_for(a, "dark"), FS, u - 0.6, u + 0.6, 1.6, 5.4, -0.05, 0.02)
            box(bm_for(f"statues@1850-{NOW}", "marble"), FS, u - 0.3, u + 0.3, 1.7, 4.6, 0.02, 0.4)
            box(bm_for(f"statues@1850-{NOW}", "marble"), FS, u - 0.15, u + 0.15, 4.6, 5.1, 0.05, 0.35)
pbox(bm_for(a, "stone"), FS, -XP - XW - 1.2, XP - XW + 1.2, PORT, PORT + 0.3, 0, 0.7)            # the order's entablature across the middle
for xc in (-4.0, 0.0, 4.0):                                                                        # piano nobile: three arched windows
    opening(a, FS, xc - XW - 0.9, xc - XW + 0.9, 13.0, 16.9, frame=0.3, pointed=False, fill="glass", frame_mat="stone")
    pbox(bm_for(a, "stone"), FS, xc - XW - 1.3, xc - XW + 1.3, 12.6, 12.85, 0, 0.6)
    for q in range(6): pbox(bm_for(a, "iron"), FS, xc - XW - 1.2 + q * 0.48, xc - XW - 1.16 + q * 0.48, 12.85, 13.8, 0.5, 0.54)
    pbox(bm_for(a, "iron"), FS, xc - XW - 1.25, xc - XW + 1.25, 13.75, 13.82, 0.45, 0.56)
for xc in (-(XI + XP) / 2, (XI + XP) / 2):
    rect_win(a, FS, xc - XW, 1.3, 13.1, 16.6, "tri", "glass")
for xc in (-XP, -XI, XI, XP):                                                                      # pilasters of the middle section
    pbox(bm_for(a, "stone"), FS, xc - XW - 0.35, xc - XW + 0.35, PORT + 0.3, NOB, 0, 0.25)
# top loggia on the Arno face: three round-arched openings over the screen, windows on the blocks
for k in range(3):
    c = -XW + (k - 1) * 4.0
    opening(at, FS, c - 1.5, c + 1.5, 19.2, 24.3, frame=0.3, pointed=False, fill="dark", frame_mat="stone")
pbox(bm_for(at, "stone"), FS, 0, XE - XW, NOB, NOB + 0.5, 0, 0.5)
box(bm_for(at, "stone"), FS, -0.3, XE - XW + 0.3, TOPF, CORN, 0, 1.0)
for side_u0, side_u1 in ((0, -XP - XW - 2.4), (XP - XW + 2.4, XE - XW)):
    n = int((side_u1 - side_u0) / 2.456)
    for i in range(n):
        c = side_u0 + (i + 0.5) * (side_u1 - side_u0) / n
        rect_win(a, FS, c, 1.1, 2.0, 5.4, None, "glass")
        rect_win(a, FS, c, 1.1, 12.4, 16.0, "tri" if i % 2 == 0 else "seg", "glass")
        rect_win(at, FS, c, 1.1, 19.3, 23.4, None, "glass")
bm = bm_for(at, "roof"); gable_roof(at, XW - 0.6, XE + 0.6, YS - 0.9, 0.6, CORN, RIDGE)

# ---- 28 statues of famous Tuscans in the pier niches (1842–56; shown from 1850, inferred) ----
ST = f"statues@1850-{NOW}"
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
