"""The lungarni: the Arno's river walls (muraglioni) and their parapets (spallette), dated by stretch (v1).

Run:  python pipeline/46_lungarni.py   (once: the wall's line on each bank from the app's ground → blender/data/lungarni.json)
      blender -b --python blender/scripts/build_lungarni.py  →  web/public/models/landmarks/lungarni.glb
Absolute scene coordinates. The ground model (4 m) turns the walls into slopes: the face stands a third of the way up the
slope from the river and the road is carried flat from it to the street. Each stretch (docs/landmarks/LUNGARNI.md) appears in the year its wall was built: the oldest on the
right bank (Acciaiuoli, the Archibusieri to the Grazie, 1287–90), the Lungarno Guicciardini by the 18th century, Vespucci and
Soderini before 1865, Poggi's lungarni from 1865 (Zecca 1865, Serristori 1870, Torrigiani and Cellini 1872). Where houses stand
in the river (Borgo San Jacopo, Via de' Bardi before 1869) there is no wall.
The wall: a vertical face of squared pietra forte and alberese from below the river-side ground up to the street; the parapet
on it ≈1 m high and 0.6 m thick, of brick (red, its joints in lime) under a stone coping – so on the Lungarno Corsini and the
Lungarno Torrigiani in Sailko's photographs from the river (2013); heights from the LiDAR ground). Parapets that came down: the 1966 flood on the Lungarno Corsini (shown missing 1966–68, the stretch's place
*inferred*), the collapse of the Lungarno Torrigiani on 25 May 2016 (wall top and parapet, ≈150 m, shown missing 2016–17).
"""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from mathutils import Vector
K.reset()
MAT["muro"] = material("lungarno_wall", "pietra_forte", (0.56, 0.5, 0.42), 0.92, 0.35, tint=(2.4, 2.3, 2.15))
MAT["spalletta"] = material("lungarno_parapet_brick", "cotto", (0.62, 0.33, 0.25), 0.88, 1.2)
MAT["lastrico"] = material("lungarno_paving", "lastrico_filari", (0.55, 0.52, 0.47), 0.9, 0.3)
MAT["asfalto"] = material("lungarno_asphalt", "asfalto", (0.24, 0.24, 0.25), 0.92, 0.3)
MAT["marciapiede"] = material("lungarno_sidewalk", "lastrico", (0.6, 0.58, 0.54), 0.85, 0.35)
# The street on the lungarno, from the parapet to the houses: the road, then the pavement by the houses (photographs of the
# lungarni today). Stone paving until asphalt (1950, *inferred*); the Lungarno degli Acciaiuoli back in stone from its 2020
# renovation, the Lungarno degli Archibusieri by the Uffizi in stone throughout; pavements from 1870 or the lungarno's year
# (*inferred*).
ASPHALT, SIDEWALK = 1950, 1870
STONE_AGAIN = {"acciaiuoli": 2020}
def stone_always(slug, x): return slug.startswith("archibusieri") and x < -40
BALUSTRADE = (2.0, 40.0)               # scene x of the balustrade in front of the Uffizi's loggia (right bank)
MAT["coping"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)
NOW = K.NOW
D = json.load(open(os.path.join(ROOT, "blender", "data", "lungarni.json"), encoding="utf-8"))
W = lambda x, z, h: Vector((x, -z, h))
PH, PT = 1.0, 0.6                      # parapet height and thickness

def densify(pts, step=5.0):
    out = []
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
        for k in range(n): out.append([a[i] + (b[i] - a[i]) * k / n for i in range(len(a))])
    out.append(pts[-1]); return out
def in_breach(bank, x, kinds):
    for br in D["breaches"]:
        if br["bank"] == bank and br["x0"] <= x <= br["x1"] and br["from"] in kinds: return br
    return None

for s in D["stretches"]:
    pts = densify(s["pts"]); bank = s["bank"]
    riv = 1.0 if bank == "n" else -1.0                  # the river lies towards +z from the north bank, −z from the south one
    slug = s["name"].split(",")[0].lower().replace("lungarni ", "").replace("lungarno ", "").replace("degli ", "").replace("della ", "").replace("delle ", "").replace(" ", "_").replace("'", "")
    for (x0, z0, h0, l0, e0, b0, r0, k0), (x1, z1, h1, l1, e1, b1, r1, k1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, z1 - z0)
        if L < 0.2: continue
        h0, h1 = max(h0, r0), max(h1, r1)                    # the wall's top at the road's level
        tx, tz = (x1 - x0) / L, (z1 - z0) / L; nx, nz = -tz, tx                     # normal; turned towards the river
        if nz * riv < 0: nx, nz = -nx, -nz
        xm = (x0 + x1) / 2
        def P(x, z, h, off=0.0): return W(x - nx * off, z - nz * off, h)          # off > 0: landwards
        br = in_breach(bank, xm, (1966, 2016))
        wall_top = lambda h: h
        parts_wall = [(f"muro_{slug}@{s['from']}-{NOW}", 0.0)]
        if br and br["from"] == 2016:                                               # the collapse took the wall's top as well
            parts_wall = [(f"muro_{slug}@{s['from']}-{NOW}", 2.5), (f"muro_{slug}_crollo@{s['from']}-{br['from']}", 0.0), (f"muro_{slug}_rifatto@{br['to']}-{NOW}", 0.0)]
        for part, cut in parts_wall:
            lo0, lo1 = min(l0, h0 - 1.5) - 0.6, min(l1, h1 - 1.5) - 0.6
            top0, top1 = h0 - cut, h1 - cut
            if part.split("@")[0].endswith(("_crollo", "_rifatto")): lo0, lo1 = h0 - 2.5, h1 - 2.5
            bm = bm_for(part, "muro")
            poly(bm, [P(x0, z0, lo0), P(x1, z1, lo1), P(x1, z1, top1), P(x0, z0, top0)])                   # the face to the river
            poly(bm, [P(x0, z0, top0), P(x1, z1, top1), P(x1, z1, top1, 1.0), P(x0, z0, top0, 1.0)])       # its top
            # courses: a thin dark line every ≈1.2 m (the joints between the squared blocks)
            hh = lo0 + 1.2
            while hh < min(top0, top1) - 0.3:
                poly(bm_for(part, "coping"), [P(x0, z0, hh, -0.02), P(x1, z1, hh, -0.02), P(x1, z1, hh + 0.06, -0.02), P(x0, z0, hh + 0.06, -0.02)])
                hh += 1.2
        # the street: road from the parapet to the pavement, the pavement (0.15 m up, with a kerb) along the houses
        sw = 2.0 if (k0 and k1) else 0.0
        if abs(b0 - z0) < 6: sw = min(sw, 1.2)
        def strip(bm, za0, za1, zb0, zb1, ha, hb):          # a band between two lines across the street, at heights ha / hb
            q = [W(x0, za0, ha), W(x1, za1, hb), W(x1, zb1, hb), W(x0, zb0, ha)]
            poly(bm, q if bank == "n" else q[::-1])
        def edge(bm, za, zb, ha0, ha1, hb0, hb1):            # a vertical band along the street (the kerb)
            poly(bm, [W(x0, za, ha0), W(x1, zb, hb0), W(x1, zb, hb1), W(x0, za, ha1)])
        rs0, rs1 = z0 - riv * PT, z1 - riv * PT               # the road starts behind the parapet
        re0, re1 = b0 + riv * sw, b1 + riv * sw               # and ends at the pavement
        y0r, y1r = s["from"], NOW
        stone_to = NOW if stone_always(slug, xm) else ASPHALT
        road = [("lastrico", y0r, max(y0r + 1, stone_to))]
        if stone_to < NOW:
            again = STONE_AGAIN.get(slug.split("_")[0])
            road += [("asfalto", max(y0r, ASPHALT), again or NOW)] + ([("lastrico", again, NOW)] if again else [])
        for mat, a, b in road:
            if a >= b: continue
            spans = [(a, b)]
            if br and br["from"] == 2016: spans = [(a, min(b, br["from"])), (max(a, br["to"]), b)]
            for (a2, b2) in spans:
                if a2 >= b2: continue
                strip(bm_for(f"strada_{slug}_{mat}@{a2}-{b2}", mat), rs0, rs1, re0, re1, h0 + 0.01, h1 + 0.01)
        if sw > 0:
            part = f"marciapiede_{slug}@{max(s['from'], SIDEWALK)}-{NOW}"
            strip(bm_for(part, "marciapiede"), re0, re1, b0, b1, h0 + 0.16, h1 + 0.16)
            edge(bm_for(part, "coping"), re0, re1, h0, h0 + 0.16, h1, h1 + 0.16)
            if max(s["from"], SIDEWALK) > s["from"]:          # before the pavements: the road ran to the houses
                strip(bm_for(f"strada_{slug}_lastrico@{s['from']}-{SIDEWALK}", "lastrico"), re0, re1, b0, b1, h0 + 0.01, h1 + 0.01)
        # the parapet on the wall: in place since the wall, gone in a breach's years
        if br:
            phases = [(s["from"], br["from"]), (br["to"], NOW)]
        else:
            phases = [(s["from"], NOW)]
        # in front of the Uffizi's loggia the parapet is a stone balustrade (Oursana's photograph from across the Arno, 2013)
        balus = bank == "n" and BALUSTRADE[0] <= xm <= BALUSTRADE[1]
        for (a, b) in phases:
            part = f"spalletta_{slug}@{a}-{b}"
            if balus:
                for k in range(int(L / 0.32)):                                                  # balusters
                    f0 = (k + 0.3) / int(L / 0.32); f1 = (k + 0.7) / int(L / 0.32)
                    xa, za, ha = x0 + (x1 - x0) * f0, z0 + (z1 - z0) * f0, h0 + (h1 - h0) * f0
                    xb, zb, hb = x0 + (x1 - x0) * f1, z0 + (z1 - z0) * f1, h0 + (h1 - h0) * f1
                    for o in (0.15, 0.45):
                        poly(bm_for(part, "coping"), [P(xa, za, ha + 0.2, o), P(xb, zb, hb + 0.2, o), P(xb, zb, hb + PH - 0.15, o), P(xa, za, ha + PH - 0.15, o)])
            layers = ((0.0, PT, 0.0, 0.2, "coping"), (-0.08, PT + 0.08, PH - 0.15, PH, "coping")) if balus else \
                     ((0.0, PT, 0.0, PH - 0.12, "spalletta"), (-0.08, PT + 0.08, PH - 0.12, PH, "coping"))
            for (o0, o1, v0, v1, mat) in layers:
                bm = bm_for(part, mat)
                q = lambda x, z, h, o: P(x, z, h, o)
                b0 = (h0, h1)
                poly(bm, [q(x0, z0, h0 + v0, o0), q(x1, z1, h1 + v0, o0), q(x1, z1, h1 + v1, o0), q(x0, z0, h0 + v1, o0)])           # river side
                poly(bm, [q(x1, z1, h1 + v0, o1), q(x0, z0, h0 + v0, o1), q(x0, z0, h0 + v1, o1), q(x1, z1, h1 + v1, o1)])           # street side
                poly(bm, [q(x0, z0, h0 + v1, o0), q(x1, z1, h1 + v1, o0), q(x1, z1, h1 + v1, o1), q(x0, z0, h0 + v1, o1)])           # top
    # the ends of each stretch: close the parapet
print("stretches", len(D["stretches"]))
K.export("lungarni")
