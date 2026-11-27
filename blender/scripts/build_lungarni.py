"""The lungarni: the Arno's river walls (muraglioni) and their parapets (spallette), dated by stretch (v1).

Run:  python pipeline/46_lungarni.py   (once: the wall's line on each bank from the app's ground → blender/data/lungarni.json)
      blender -b --python blender/scripts/build_lungarni.py  →  web/public/models/landmarks/lungarni.glb
Absolute scene coordinates. The ground model (4 m) turns the walls into slopes: the face stands a third of the way up the
slope from the river and the road is carried flat from it to the street. Each stretch (docs/landmarks/LUNGARNI.md) appears in the year its wall was built: the oldest on the
right bank (Acciaiuoli, the Archibusieri to the Grazie, 1287–90), the Lungarno Guicciardini by the 18th century, Vespucci and
Soderini before 1865, Poggi's lungarni from 1865 (Zecca 1865, Serristori 1870, Torrigiani and Cellini 1872). Where houses stand
in the river (Borgo San Jacopo, Via de' Bardi before 1869) there is no wall.
The wall: a vertical face of squared pietra forte and alberese from below the river-side ground up to the street; the parapet
on it ≈1 m high and 0.6 m thick, in the same stone, with a pietra serena coping (photographs of the lungarni; heights from the
LiDAR ground). Parapets that came down: the 1966 flood on the Lungarno Corsini (shown missing 1966–68, the stretch's place
*inferred*), the collapse of the Lungarno Torrigiani on 25 May 2016 (wall top and parapet, ≈150 m, shown missing 2016–17).
"""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from mathutils import Vector
K.reset()
MAT["muro"] = material("lungarno_wall", "pietra_forte", (0.56, 0.5, 0.42), 0.92, 0.35, tint=(2.4, 2.3, 2.15))
MAT["spalletta"] = material("lungarno_parapet", "pietra_forte", (0.62, 0.53, 0.42), 0.9, 0.3, tint=(2.7, 2.5, 2.2))
MAT["strada"] = material("lungarno_road", None, (0.42, 0.41, 0.4), 0.95)
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
    for (x0, z0, h0, l0, e0), (x1, z1, h1, l1, e1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, z1 - z0)
        if L < 0.2: continue
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
            if cut == 0.0 and not part.split("@")[0].endswith("_crollo"):
                # the road carried flat from the wall to the street's edge (the ground model smooths the wall into a slope)
                poly(bm_for(part, "strada"), [W(x0, z0, h0 + 0.03), W(x1, z1, h1 + 0.03), W(x1, e1, h1 + 0.03), W(x0, e0, h0 + 0.03)][::(1 if bank == "n" else -1)])
            # courses: a thin dark line every ≈1.2 m (the joints between the squared blocks)
            hh = lo0 + 1.2
            while hh < min(top0, top1) - 0.3:
                poly(bm_for(part, "coping"), [P(x0, z0, hh, -0.02), P(x1, z1, hh, -0.02), P(x1, z1, hh + 0.06, -0.02), P(x0, z0, hh + 0.06, -0.02)])
                hh += 1.2
        # the parapet on the wall: in place since the wall, gone in a breach's years
        if br:
            phases = [(s["from"], br["from"]), (br["to"], NOW)]
        else:
            phases = [(s["from"], NOW)]
        for (a, b) in phases:
            part = f"spalletta_{slug}@{a}-{b}"
            for (o0, o1, v0, v1, mat) in ((0.0, PT, 0.0, PH - 0.12, "spalletta"), (-0.08, PT + 0.08, PH - 0.12, PH, "coping")):
                bm = bm_for(part, mat)
                q = lambda x, z, h, o: P(x, z, h, o)
                b0 = (h0, h1)
                poly(bm, [q(x0, z0, h0 + v0, o0), q(x1, z1, h1 + v0, o0), q(x1, z1, h1 + v1, o0), q(x0, z0, h0 + v1, o0)])           # river side
                poly(bm, [q(x1, z1, h1 + v0, o1), q(x0, z0, h0 + v0, o1), q(x0, z0, h0 + v1, o1), q(x1, z1, h1 + v1, o1)])           # street side
                poly(bm, [q(x0, z0, h0 + v1, o0), q(x1, z1, h1 + v1, o0), q(x1, z1, h1 + v1, o1), q(x0, z0, h0 + v1, o1)])           # top
    # the ends of each stretch: close the parapet
print("stretches", len(D["stretches"]))
K.export("lungarni")
