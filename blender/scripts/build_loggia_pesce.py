"""Loggia del Pesce – Vasari's fish market loggia, in the Mercato Vecchio (1569–1889) and in Piazza dei Ciompi (since 1955) (v1).

Run:  blender -b --python blender/scripts/build_loggia_pesce.py  →  web/public/models/landmarks/loggia_pesce.glb
Frame: absolute scene coordinates (Blender X = scene x, Blender Y = −scene z, Z = scene y); placed at [0, 0], rot 0, ground 0.
Measured: Piazza dei Ciompi – OSM way 204145494, 32.4 × 6.2 m, long side east–west; LiDAR roof ≈9.4 m above the square
(DSM 17.0–17.2 m scene, ground 7.6 m). Mercato Vecchio – the lone rectangle on the market's west side in the Catasto
Generale Toscano of the 1830s (the app's cadastre map): x −115.6 … −109.4, z 1.8 … 34.2, long side north–south, the same
32.4 × 6.2 m; the city data had traced it as a "demolished" medieval house (record 14785).
Details from photographs (docs/materials): a double row of nine round arches on Tuscan columns of pietra serena, piers at
the corners and in the middle, two arches on each short end with a column between, a medallion in every spandrel, the
Medici and Grascia arms at the corners, a plain band over the arches and a hipped tiled roof on deep eaves; domed vaults
inside. Arch, column and eave heights are *inferred* from the photographs and the DSM; inside, a flat ceiling stands for the
domed vaults.
Dates (docs/landmarks/LOGGIA-DEL-PESCE.md): built 19 August 1568 – 22 February 1569 for Cosimo I; one arch added per side
in 1699 (1669 elsewhere on the same page) – read here as seven bays growing to nine; dismantled from May 1889 in the
Risanamento, the pieces kept at San Marco; rebuilt in Piazza dei Ciompi in 1955.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from mathutils import Vector
from landmark_detail import *
K.reset()
MAT["serena"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)
MAT["plaster"] = material("plaster_ochre", None, (0.86, 0.76, 0.56), 0.9)
MAT["tondo"] = material("tondo_plaster", None, (0.82, 0.8, 0.74), 0.7)
MAT["arms"] = material("arms_painted", None, (0.72, 0.18, 0.14), 0.6)
NOW = K.NOW
LONG, WIDE = 32.4, 6.2
BAY_L = LONG / 9; BAY_S = WIDE / 2
SPRING = 3.2; EAVE = 7.6; RIDGE = 9.4                    # above the floor

def loggia(prefix, years, c, axis, ground, nb):
    """One loggia of nb bays a side (centred on c, scene x/z), long side along axis (unit scene x/z)."""
    part = f"{prefix}@{years[0]}-{years[1]}"
    ax, az = axis; nx, nz = -az, ax                          # across
    L = BAY_L * nb; g = ground
    def P(u, w, h=0.0): return Vector((c[0] + ax * u + nx * w, -(c[1] + az * u + nz * w), h))
    # the four faces: frame origin at a corner, u along the face, n outwards
    faces = [(P(-L / 2, WIDE / 2), Vector((ax, -az, 0)), Vector((nx, -nz, 0)), L, nb, BAY_L),
             (P(L / 2, -WIDE / 2), Vector((-ax, az, 0)), Vector((-nx, nz, 0)), L, nb, BAY_L),
             (P(L / 2, WIDE / 2), Vector((-nx, nz, 0)), Vector((ax, -az, 0)), WIDE, 2, BAY_S),
             (P(-L / 2, -WIDE / 2), Vector((nx, -nz, 0)), Vector((-ax, az, 0)), WIDE, 2, BAY_S)]
    box(bm_for(part, "serena"), Frame(P(-L / 2 - 0.3, -WIDE / 2 - 0.3), Vector((ax, -az, 0)), Vector((nx, -nz, 0))), 0, L + 0.6, g - 0.6, g + 0.15, 0, WIDE + 0.6)
    top = g + SPRING
    for o, u, n, Lf, k, bay in faces:
        F = Frame(o, u, n)
        for j in range(k + 1):
            uu = j * bay
            if j in (0, k):
                pbox(bm_for(part, "serena"), F, uu - 0.35, uu + 0.35, g + 0.15, top + 0.25, -0.35, 0.15)          # piers
            else:
                pbox(bm_for(part, "serena"), F, uu - 0.3, uu + 0.3, g + 0.15, g + 0.45, -0.3, 0.1)
                cylinder(part, "serena", F.p(uu, 0, -0.1), 0.2, g + 0.45, top - 0.35, seg=10)
                pbox(bm_for(part, "serena"), F, uu - 0.3, uu + 0.3, top - 0.35, top + 0.05, -0.3, 0.1)
        for j in range(k):
            uc = (j + 0.5) * bay; r = bay / 2 - 0.25
            ring(part, "serena", F, uc, top + 0.05, r, r + 0.28, 0, 0.08, seg=12, soffit=True)
            bm = bm_for(part, "plaster"); seg = 10
            for s_ in (-1, 1):                                    # spandrels up to the band
                pts = [F.p(uc + s_ * r * math.cos(math.pi / 2 * i / seg), top + 0.05 + r * math.sin(math.pi / 2 * i / seg), 0) for i in range(seg + 1)]
                corner = F.p(uc + s_ * (bay / 2), EAVE + g - 1.6, 0)
                for i in range(seg): poly(bm, [pts[i], pts[i + 1], corner] if s_ > 0 else [pts[i + 1], pts[i], corner])
                poly(bm, [F.p(uc + s_ * r, top + 0.05, 0), F.p(uc + s_ * bay / 2, top + 0.05, 0), corner] if s_ > 0 else [F.p(uc + s_ * bay / 2, top + 0.05, 0), F.p(uc + s_ * r, top + 0.05, 0), corner])
            poly(bm, [F.p(uc + bay / 2, EAVE + g - 1.6, 0), F.p(uc - bay / 2, EAVE + g - 1.6, 0), F.p(uc, top + 0.05 + r, 0)])   # over the crown
        for j in range(1, k):                                     # a medallion over every column
            oculus(part, F, j * bay, top + (bay / 2 - 0.25) * 0.95, 0.42, frame="serena", fill="tondo", fw=0.1)
        pbox(bm_for(part, "plaster"), F, 0, Lf, g + EAVE - 1.6, g + EAVE, -0.3, 0)                   # band over the arches
        pbox(bm_for(part, "serena"), F, -0.1, Lf + 0.1, g + EAVE - 1.65, g + EAVE - 1.5, 0, 0.12)
        pbox(bm_for(part, "serena"), F, -0.1, Lf + 0.1, g + EAVE - 0.2, g + EAVE, 0, 0.25)
        for uu in (0.9, Lf - 0.9):                                                                 # arms at the corners
            if Lf > 10: poly(bm_for(part, "arms"), [F.p(uu - 0.45, g + EAVE - 1.3, 0.02), F.p(uu + 0.45, g + EAVE - 1.3, 0.02), F.p(uu + 0.45, g + EAVE - 0.5, 0.02), F.p(uu, g + EAVE - 0.25, 0.02), F.p(uu - 0.45, g + EAVE - 0.5, 0.02)])
        if Lf > 10:                                                                                # the cartouche in the middle
            pbox(bm_for(part, "tondo"), F, Lf / 2 - 0.9, Lf / 2 + 0.9, g + EAVE - 1.35, g + EAVE - 0.35, 0, 0.06)
    # the ceiling over the arches (the domed vaults are not drawn), the middle row of columns
    for j in range(1, nb):
        cylinder(part, "serena", P(-L / 2 + j * BAY_L, 0), 0.2, g + 0.15, top - 0.35, seg=10)
    poly(bm_for(part, "plaster"), [P(-L / 2, -WIDE / 2, g + EAVE - 1.6), P(L / 2, -WIDE / 2, g + EAVE - 1.6), P(L / 2, WIDE / 2, g + EAVE - 1.6), P(-L / 2, WIDE / 2, g + EAVE - 1.6)])
    # hipped roof on deep eaves
    e = 1.1; z0, z1 = g + EAVE, g + RIDGE; h = WIDE / 2 + e
    A, B, C_, D_ = P(-L / 2 - e, -h, z0), P(L / 2 + e, -h, z0), P(L / 2 + e, h, z0), P(-L / 2 - e, h, z0)
    R0, R1 = P(-L / 2 - e + h, 0, z1), P(L / 2 + e - h, 0, z1)
    bm = bm_for(part, "roof")
    poly(bm, [A, B, R1, R0]); poly(bm, [C_, D_, R0, R1]); poly(bm, [B, C_, R1]); poly(bm, [D_, A, R0])
    poly(bm_for(part, "serena"), [A, D_, C_, B])                                                    # soffit of the eaves

# Mercato Vecchio, west side of the market (1830s cadastre): seven bays 1569–1699, nine after (one arch added at each end)
MV_C = (-112.5, 18.0); MV_AX = (0.0, 1.0); MV_G = 9.26
loggia("pesce_mercato_vecchio", (1569, 1699), MV_C, MV_AX, MV_G, 7)
loggia("pesce_mercato_vecchio_1699", (1699, 1889), MV_C, MV_AX, MV_G, 9)
# Piazza dei Ciompi, rebuilt 1955 (OSM way 204145494)
CI_C = (787.2, 29.2)
CI_AX = (32.3 / math.hypot(32.3, -1.2), -1.2 / math.hypot(32.3, -1.2)); CI_G = 7.79
loggia("pesce_ciompi", (1955, NOW), CI_C, CI_AX, CI_G, 9)
K.export("loggia_pesce")
