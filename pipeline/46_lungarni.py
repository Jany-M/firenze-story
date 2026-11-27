"""The lungarni's river walls (muraglioni) and parapets (spallette): their line on each bank, dated by stretch.

Inputs:  web/public/data/river.json (the Arno's axis: x, water level, z of the centre and of both banks every 20 m),
         web/public/data/terrain.f32 (the app's ground)
Output:  blender/data/lungarni.json – for each dated stretch (docs/landmarks/LUNGARNI.md): the bank, the years, and the wall's
         line as points [x, z of the face, street level, river-side level, z of the street's edge] (scene coordinates, y = elevation − 40 m)
The wall stands where the ground reaches the street's level (70th percentile of the ground 30–70 m from the bank) coming
out from the river: low strips along the water (the Renai below the Lungarno Serristori) stay in front of it. Stretches where houses stand in the river (Borgo San Jacopo, and
Via de' Bardi before the Lungarno Torrigiani) have no wall.
"""
import os, json
import numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
D = os.path.join(ROOT, "web", "public", "data")
m = json.load(open(os.path.join(D, "meta.json")))["terrain"]; n_, st = m["n"], m["step"]
# the ground before 21_build_env holds it at the walls' foot (that step reads this file's output: read its raw copy)
RAW_T = os.path.join(ROOT, "_dev", "data", "build", "terrain_raw.f32")
T = np.fromfile(RAW_T if os.path.exists(RAW_T) else os.path.join(D, "terrain.f32"), dtype=np.float32).reshape(n_, n_); half = (n_ - 1) * st / 2
def G(x, z):
    fx, fz = (x + half) / st, (z + half) / st
    i, j = min(max(int(fx), 0), n_ - 2), min(max(int(fz), 0), n_ - 2); a, b = fx - i, fz - j
    return float(T[j, i] * (1 - a) * (1 - b) + T[j, i + 1] * a * (1 - b) + T[j + 1, i] * (1 - a) * b + T[j + 1, i + 1] * a * b)
axis = json.load(open(os.path.join(D, "river.json")))["axis"]

# the stretches: bank, x range along the river's axis (bridges: Vittoria −1660, Vespucci −987, Carraia −626, Santa Trinita
# −380, Ponte Vecchio −151, Grazie 300, San Niccolò 1297; Piazza dei Cavalleggeri ≈560, Torre della Zecca ≈1080), name,
# first year of the wall, its basis and confidence
STRETCHES = [
    ("n", -1660, -626, "Lungarno Amerigo Vespucci", 1850, "before Poggi's works of 1865 (not in their list); year *inferred*", "inferred"),
    ("n", -626, -380, "Lungarno Corsini", 1300, "continues the older lungarno; year *inferred*", "inferred"),
    ("n", -380, -151, "Lungarno degli Acciaiuoli", 1290, "the oldest lungarno (first named 1246); a muraglione by Santa Trinita in 1290", "documented"),
    ("n", -151, 300, "Lungarni degli Archibusieri, Anna Maria Luisa de' Medici, Generale Diaz", 1290, "lungarno from Ponte Vecchio to Rubaconte, 1290", "documented"),
    ("n", 300, 560, "Lungarno delle Grazie", 1287, "lungarno with a wall from Rubaconte towards the Cavalleggeri, 1287", "documented"),
    ("n", 560, 1080, "Lungarno della Zecca Vecchia", 1865, "muraglione built in the river bed, 1865; the road raised 1872", "documented"),
    ("n", 1080, 1300, "Lungarno Pecori Giraldi", 1890, "reaches the Ponte di Ferro by the end of the century; year *inferred*", "inferred"),
    ("s", -1660, -626, "Lungarno Soderini", 1850, "before Poggi's works of 1865; year *inferred*", "inferred"),
    ("s", -626, -380, "Lungarno Guicciardini", 1600, "shown in Zocchi's view of 1744; year *inferred*", "inferred"),
    ("s", -151, 300, "Lungarno Torrigiani", 1872, "built 1869–72 in place of the houses of Via de' Bardi on the river", "documented"),
    ("s", 300, 1297, "Lungarno Serristori", 1870, "built 1866–70 over the Renai mill race", "documented"),
    ("s", 1297, 1800, "Lungarno Benvenuto Cellini", 1872, "built 1869–72", "documented"),
]
# parapets that came down: the 1966 flood (Lungarno Corsini: "the shoulders completely knocked down", Galleria Bazzanti);
# the collapse of 25 May 2016 on the Lungarno Torrigiani (≈200 m; the place along it *inferred*)
BREACHES = [("n", -560, -440, 1966, 1968, "1966 flood"), ("s", 20, 170, 2016, 2017, "collapse of 25 May 2016")]

def wall_point(row, side):
    """[x, z of the wall's face, street level, river-side level, z of the street's edge]: the ground model (4 m) smooths the
    real vertical wall into a slope; the face is put a third of the way up that slope from the river, and the road is
    carried flat from it to where the ground reaches the street."""
    x, wl, zc, zn, zs = row
    zb, out_ = (zn, -1.0) if side == "n" else (zs, 1.0)           # the bank and the way out of the river
    land = [G(x, zb + out_ * d) for d in range(30, 71, 2)]
    street = float(np.percentile(land, 70))
    d = 0.0
    while d < 70 and G(x, zb + out_ * d) < street - 1.0: d += 0.5   # from the river outwards to the street's level
    z_st = zb + out_ * (d - 0.5)
    low = max(min([G(x, z_st - out_ * k) for k in range(2, 20, 2)] + [street - 1.5]), wl - 1.0)
    d2 = 0.0
    while d2 < d and G(x, zb + out_ * d2) < low + 0.35 * (street - low): d2 += 0.5
    z_w = zb + out_ * d2
    return [round(x, 1), round(z_w, 2), round(street, 2), round(low, 2), round(z_st, 2)]

out = {"stretches": [], "breaches": [{"bank": b, "x0": a, "x1": c, "from": f, "to": t, "why": w} for b, a, c, f, t, w in BREACHES]}
for bank, x0, x1, name, year, basis, conf in STRETCHES:
    rows = [r for r in axis if x0 <= r[0] <= x1]
    pts = [wall_point(r, bank) for r in rows]
    if len(pts) >= 5:                                    # smooth the line (running median of 5) so it does not wander
        z = np.array([p[1] for p in pts]); zs_ = z.copy()
        for i in range(2, len(z) - 2): zs_[i] = np.median(z[i - 2:i + 3])
        for p, v in zip(pts, zs_): p[1] = round(float(v), 2)
        z2 = np.array([p[4] for p in pts]); z2s = z2.copy()
        for i in range(2, len(z2) - 2): z2s[i] = np.median(z2[i - 2:i + 3])
        for p, v in zip(pts, z2s): p[4] = round(float(v), 2)
    # The 4 m ground is drawn as triangles: a street-level vertex next to a river-level one makes a slope that runs out
    # through a face set between them, as teeth over the water. Put the face on the first river-level vertex of every grid
    # column within 20 m (a straight face between two points then stays in front of all of them), at most 6 m further out.
    sgn = 1.0 if bank == "n" else -1.0                       # riverward
    for p in pts:
        need = p[1]
        for cx in np.arange(np.ceil((p[0] - 20 + half) / st), np.floor((p[0] + 20 + half) / st) + 1):
            if not 0 <= cx < n_: continue
            j = int(round((p[4] + half) / st))
            for _ in range(20):
                if not 0 <= j < n_: break
                if T[j, int(cx)] < p[3] + 1.0: need = max(need, j * st - half) if bank == "n" else min(need, j * st - half); break
                j += int(sgn)
        p[1] = round(float(np.clip(need, p[1] - 6, p[1] + 6)), 2)
    out["stretches"].append({"bank": bank, "name": name, "from": year, "basis": basis, "conf": conf, "pts": pts})
    print(f"{bank} {name:55s} {year} {len(pts)} points, street ≈{np.median([p[2] for p in pts]):.1f}, river ≈{np.median([p[3] for p in pts]):.1f}")
dst = os.path.join(ROOT, "blender", "data", "lungarni.json"); json.dump(out, open(dst, "w", newline="\n")); print("→", dst)
