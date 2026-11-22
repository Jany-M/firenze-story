"""Tileable material textures (albedo + normal + roughness) shared by the web app and the Blender asset library.
Pure numpy: every pattern is periodic by construction (FFT-filtered noise, integer brick/tile counts), so it tiles
seamlessly. Output: web/public/textures/<name>_{col,nrm,rgh}.jpg  (also linked by blender/scripts/build_assets.py)

Materials (Florentine palette):
  intonaco      lime plaster (neutral – tinted per building in the shader)
  pietra_forte  rusticated ashlar of brown sandstone (palazzi ground floors, Palazzo Vecchio, walls)
  pietra_serena grey-blue sandstone dressed blocks (cornices, columns, Brunelleschi)
  coppi         Tuscan curved roof tiles (coppo + embrice)
  lastrico      large irregular pietra forte street slabs (lastricato)
  cotto         terracotta brick (herring-bone courtyards, walls, Roman brick)
  wood          weathered oak planks (stalls, carts, stands)
  canvas        undyed linen/hemp (awnings) – tinted in use
  marble_white  Carrara/Lunigiana white marble (Duomo, Baptistery, Campanile), fine grey veins
  marble_green  Prato serpentine ("verde di Prato"), green-black with pale veins
  marble_red    Monsummano / Maremma red limestone, pink-red with white veins
  terra         beaten earth street: wheel ruts, gravel, dung, dried puddles (unpaved streets, all eras)
  basoli        Roman polygonal paving blocks (cardo / decumanus of Florentia)
  ammattonato   brick paving in herring-bone (early paved streets and courtyards, 13th–15th c.)
  lastrico_filari  regular pietra forte slabs in rows (19th c. → today, historic centre)
  lastrico_spina   regular pietra forte slabs in herring-bone (19th c. → today)
  asfalto       asphalt with patches and tar seams (20th c. boulevards and new quarters)
"""
import os, sys, numpy as np
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get("TEX_OUT") or os.path.join(ROOT, "web", "public", "textures"); os.makedirs(OUT, exist_ok=True)
N = 1024
rng = np.random.default_rng(1492)

def fbm(n=N, octaves=6, beta=2.2, seed=None):
    """Periodic fractal noise via FFT (power spectrum 1/f^beta), normalised 0..1."""
    r = np.random.default_rng(seed) if seed is not None else rng
    f = np.fft.fftfreq(n)[:, None] ** 2 + np.fft.fftfreq(n)[None, :] ** 2
    f[0, 0] = 1
    spec = (r.normal(size=(n, n)) + 1j * r.normal(size=(n, n))) / f ** (beta / 4)
    spec[0, 0] = 0
    x = np.real(np.fft.ifft2(spec))
    return (x - x.min()) / (x.max() - x.min())

def blur_wrap(a, k=3):
    for _ in range(k):
        a = (a + np.roll(a, 1, 0) + np.roll(a, -1, 0) + np.roll(a, 1, 1) + np.roll(a, -1, 1)) / 5
    return a

def normal_from_height(h, strength=4.0):
    dx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * strength
    dy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * strength
    nz = np.ones_like(h)
    n = np.stack([-dx, dy, nz], -1); n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return ((n * 0.5 + 0.5) * 255).astype(np.uint8)

def save(name, col, h, rough, strength=4.0):
    Image.fromarray(np.clip(col * 255, 0, 255).astype(np.uint8)).save(os.path.join(OUT, f"{name}_col.jpg"), quality=88)
    Image.fromarray(normal_from_height(h, strength)).save(os.path.join(OUT, f"{name}_nrm.jpg"), quality=92)
    rough = np.broadcast_to(np.asarray(rough, dtype=float), h.shape)
    Image.fromarray(np.clip(rough * 255, 0, 255).astype(np.uint8)).save(os.path.join(OUT, f"{name}_rgh.jpg"), quality=88)
    print("texture", name)

def tint(gray, c0, c1):
    return np.asarray(c0)[None, None, :] * (1 - gray[..., None]) + np.asarray(c1)[None, None, :] * gray[..., None]

yy, xx = np.mgrid[0:N, 0:N] / N

def blocks(rows, cols_per_row, jitter=0.0, offset=0.5, mortar=0.012, bevel=0.025, seed=0):
    """Running-bond block layout (periodic). Returns height (0 mortar..1 face), block id map, local coords."""
    r = np.random.default_rng(seed)
    row = np.floor(yy * rows).astype(int)
    shift = (row % 2) * offset / cols_per_row
    u = (xx + shift) % 1.0
    col = np.floor(u * cols_per_row).astype(int)
    fu, fv = (u * cols_per_row) % 1.0, (yy * rows) % 1.0
    # distance to block edge in block-local units scaled to texture space
    du = np.minimum(fu, 1 - fu) / cols_per_row; dv = np.minimum(fv, 1 - fv) / rows
    d = np.minimum(du, dv)
    h = np.clip((d - mortar) / bevel, 0, 1)
    bid = row * 997 + col
    rnd = r.random(rows * 997 + cols_per_row + 1)
    return h, rnd[bid], fu, fv

# ---- intonaco (lime plaster): soft mottling, fine grain, small cracks ----
g = fbm(seed=1) * 0.6 + fbm(beta=1.2, seed=2) * 0.4
grain = fbm(beta=0.6, seed=3)
col = tint(g * 0.55 + grain * 0.15 + 0.3, (0.80, 0.77, 0.70), (0.97, 0.95, 0.90))
patch = (fbm(beta=2.8, seed=4) > 0.72).astype(float); patch = blur_wrap(patch, 6)
col = col * (1 - 0.12 * patch[..., None])                            # weathered patches (exposed render)
save("intonaco", col, g * 0.3 + grain * 0.2 - patch * 0.4, 0.85 + 0.1 * grain, 2.0)

# ---- pietra forte: rusticated ashlar (bugnato), irregular courses ----
h, rnd, fu, fv = blocks(rows=4, cols_per_row=2, offset=0.5, mortar=0.006, bevel=0.06, seed=5)
rough_face = fbm(beta=1.6, seed=6)
face = h * (0.75 + 0.25 * rough_face) * (0.85 + 0.15 * (1 - np.abs(fu - 0.5) * 2) * (1 - np.abs(fv - 0.5) * 2))   # cushion
base = tint(fbm(seed=7) * 0.6 + rnd * 0.4, (0.43, 0.34, 0.25), (0.66, 0.55, 0.41))
col = base * (0.55 + 0.45 * h[..., None]) * (0.85 + 0.15 * rough_face[..., None])
save("pietra_forte", col, face, 0.8 + 0.15 * rough_face, 9.0)

# ---- pietra serena: finely dressed grey sandstone blocks ----
h, rnd, fu, fv = blocks(rows=6, cols_per_row=3, offset=0.5, mortar=0.003, bevel=0.01, seed=8)
fine = fbm(beta=0.9, seed=9)
col = tint(rnd * 0.4 + fine * 0.4 + 0.1, (0.42, 0.44, 0.45), (0.62, 0.64, 0.64)) * (0.8 + 0.2 * h[..., None])
save("pietra_serena", col, h * 0.6 + fine * 0.1, 0.75 + 0.1 * fine, 4.0)

# ---- coppi: Tuscan curved roof tiles, columns of overlapping half-cylinders ----
cols_n, rows_n = 16, 10
cu = (xx * cols_n) % 1.0; cv = (yy * rows_n) % 1.0
cid = np.floor(xx * cols_n).astype(int); rid = np.floor(yy * rows_n).astype(int)
arch = np.sqrt(np.clip(1 - (2 * cu - 1) ** 2, 0, 1))                  # half-cylinder profile
overlap = np.clip(cv * 1.4, 0, 1)                                     # tile end overlaps the next row
hh = arch * (0.65 + 0.35 * overlap) - (cv < 0.06) * 0.25
rt = np.random.default_rng(10).random((rows_n, cols_n))[rid % rows_n, cid % cols_n]
col = tint(rt * 0.6 + fbm(seed=11) * 0.4, (0.55, 0.27, 0.17), (0.78, 0.45, 0.30))
lichen = blur_wrap((fbm(beta=2.4, seed=12) > 0.78).astype(float), 3)
col = col * (0.62 + 0.38 * arch[..., None]) * (1 - 0.25 * lichen[..., None]) + lichen[..., None] * np.array([0.08, 0.08, 0.05])
save("coppi", col, hh, 0.7 + 0.2 * lichen, 6.0)

# ---- lastrico: large irregular pietra forte paving slabs (Voronoi-like, periodic) ----
pts = rng.random((70, 2))
P = np.concatenate([pts + [dx, dy] for dx in (-1, 0, 1) for dy in (-1, 0, 1)])
grid = np.stack([xx.ravel(), yy.ravel()], 1)
from scipy.spatial import cKDTree
d, i = cKDTree(P).query(grid, k=2)
edge = (d[:, 1] - d[:, 0]).reshape(N, N); sid = (i[:, 0] % len(pts)).reshape(N, N)
h = np.clip(edge / 0.012, 0, 1)
rs = np.random.default_rng(13).random(len(pts))[sid]
wear = fbm(beta=1.4, seed=14)
col = tint(rs * 0.5 + wear * 0.5, (0.40, 0.35, 0.29), (0.62, 0.56, 0.47)) * (0.5 + 0.5 * h[..., None])
save("lastrico", col, h * (0.8 + 0.2 * wear), 0.85 + 0.1 * wear, 5.0)

# ---- cotto: brick (Roman & medieval walls, courtyards) ----
h, rnd, fu, fv = blocks(rows=16, cols_per_row=6, offset=0.5, mortar=0.004, bevel=0.006, seed=15)
col = tint(rnd * 0.6 + fbm(seed=16) * 0.4, (0.50, 0.26, 0.17), (0.72, 0.42, 0.28))
col = np.where(h[..., None] > 0.05, col, np.array([0.72, 0.68, 0.60]))
save("cotto", col, h * 0.8, 0.85, 4.0)

# ---- wood: weathered oak planks ----
planks = 6
pu = (yy * planks) % 1.0; pid = np.floor(yy * planks).astype(int)
streak = fbm(n=N, beta=1.0, seed=17)
streak = (np.roll(streak, 0, 0) + 0)
grainw = np.sin((xx * 40 + streak * 6 + pid * 1.7) * np.pi) * 0.5 + 0.5
gap = np.clip(np.minimum(pu, 1 - pu) / 0.03, 0, 1)
rp = np.random.default_rng(18).random(planks)[pid % planks]
col = tint(grainw * 0.4 + rp * 0.4 + streak * 0.2, (0.30, 0.22, 0.15), (0.55, 0.43, 0.30)) * (0.4 + 0.6 * gap[..., None])
save("wood", col, gap * 0.7 + grainw * 0.15, 0.8, 3.0)

# ---- canvas: woven linen ----
weave = (np.sin(xx * N * np.pi / 2) * np.sin(yy * N * np.pi / 2)) * 0.5 + 0.5
cg = fbm(beta=1.8, seed=19)
col = tint(cg * 0.5 + weave * 0.15 + 0.35, (0.75, 0.71, 0.62), (0.93, 0.90, 0.82))
save("canvas", col, weave * 0.3, 0.9, 1.5)
print("done ->", OUT)

# ---- marbles of the Florentine polychrome revetment (Duomo, Campanile, Baptistery, Santa Croce / SMN façades) ----
def veins(seed, freq=3, warp=2.5, sharp=14.0):
    """Periodic ridged veining: |sin| of a periodic-noise-warped coordinate (integer frequency keeps it tileable)."""
    w = fbm(beta=2.4, seed=seed) - 0.5
    t = np.abs(np.sin(np.pi * (xx * freq + yy * (freq - 1) + w * warp)))
    return np.exp(-t * sharp)
def marble(name, base0, base1, vein_col, seed, vein_amt=0.8, rough=0.4, freq=3):
    cloud = fbm(beta=2.0, seed=seed + 1)
    v = np.clip(veins(seed, freq) + 0.6 * veins(seed + 2, freq + 2, 3.5, 22.0), 0, 1)
    col = tint(cloud, base0, base1)
    col = col * (1 - vein_amt * v[..., None]) + np.asarray(vein_col)[None, None, :] * (vein_amt * v[..., None])
    grime = blur_wrap(fbm(beta=2.6, seed=seed + 3), 2)
    col = col * (0.93 + 0.07 * grime[..., None])
    save(name, col, cloud * 0.15 - v * 0.05, rough + 0.15 * grime, 1.0)
marble("marble_white", (0.84, 0.83, 0.80), (0.95, 0.94, 0.91), (0.55, 0.56, 0.58), 31, 0.55, 0.38)
marble("marble_green", (0.07, 0.12, 0.10), (0.16, 0.24, 0.20), (0.42, 0.52, 0.45), 41, 0.6, 0.32, 4)
marble("marble_red", (0.58, 0.27, 0.24), (0.74, 0.42, 0.37), (0.90, 0.84, 0.80), 51, 0.5, 0.36)

# ---------------------------------------------------------------- street surfaces by era (docs/MATERIALS.md)
from scipy.spatial import cKDTree as _KD
def voronoi(npts, seed, jitter_grid=None):
    r = np.random.default_rng(seed)
    pts = r.random((npts, 2)) if jitter_grid is None else np.stack(np.meshgrid((np.arange(jitter_grid[0]) + 0.5) / jitter_grid[0],
          (np.arange(jitter_grid[1]) + 0.5) / jitter_grid[1]), -1).reshape(-1, 2) + (r.random((jitter_grid[0] * jitter_grid[1], 2)) - 0.5) * 0.6 / np.array(jitter_grid)
    P = np.concatenate([pts + [dx, dy] for dx in (-1, 0, 1) for dy in (-1, 0, 1)])
    d, i = _KD(P).query(np.stack([xx.ravel(), yy.ravel()], 1), k=2)
    return (d[:, 1] - d[:, 0]).reshape(N, N), (i[:, 0] % len(pts)).reshape(N, N), len(pts)

# terra battuta: ruts along x, scattered gravel, darker damp patches (8 m tile)
n1 = fbm(beta=2.2, seed=61); n2 = fbm(beta=1.2, seed=62)
ruts = np.exp(-((np.sin(2 * np.pi * (yy * 2 + 0.35 * (fbm(beta=2.6, seed=63) - 0.5))) - 0.7) ** 2) * 30) * fbm(beta=2.2, seed=65)
grav = (fbm(beta=0.6, seed=64) > 0.72).astype(float)
col = tint(n1 * 0.7 + n2 * 0.3, (0.37, 0.34, 0.29), (0.53, 0.50, 0.43))   # grey-brown packed earth (was too orange, read as roof tile)
damp = blur_wrap((fbm(beta=2.4, seed=66) > 0.7).astype(float), 5)
col = col * (1 - 0.12 * ruts[..., None]) * (1 - 0.22 * damp[..., None]) + grav[..., None] * 0.06
save("terra", col, n1 * 0.4 - ruts * 0.2 + grav * 0.2, 0.95 - 0.35 * damp, 3.0)

# basoli: big polygonal blocks with tight joints (Roman streets), 4 m tile
e, sid, k = voronoi(0, 71, (6, 6))
h = np.clip(e / 0.01, 0, 1) ** 0.6; rs = np.random.default_rng(72).random(k)[sid]; w = fbm(beta=1.6, seed=73)
col = tint(rs * 0.5 + w * 0.5, (0.33, 0.31, 0.29), (0.50, 0.47, 0.43)) * (0.45 + 0.55 * h[..., None])
save("basoli", col, h * (0.9 + 0.1 * w), 0.7 + 0.15 * w, 6.0)

# ammattonato: bricks on edge in herring-bone, 2 m tile (bricks 0.25 x 0.06 m on the visible face ~ 0.25 x 0.12)
u = xx * 8; v = yy * 8
a = np.floor(u + v); b = np.floor(u - v)
stripe = (np.floor((u + v) / 1.0) % 2)
lu = np.where(stripe == 0, (u - v) * 2 % 1, (u + v) * 2 % 1)
lv = np.where(stripe == 0, (u + v) % 1, (u - v) % 1)
mort = np.minimum(np.minimum(lu, 1 - lu) * 6, np.minimum(lv, 1 - lv) * 18).clip(0, 1)
bid = np.where(stripe == 0, np.floor((u - v) * 2) * 31 + a, np.floor((u + v) * 2) * 17 + b)
rb = (np.sin(bid * 12.9898) * 43758.5453) % 1
col = tint(rb * 0.6 + fbm(seed=74) * 0.4, (0.48, 0.27, 0.19), (0.68, 0.42, 0.30))
col = np.where(mort[..., None] > 0.25, col, np.array([0.62, 0.58, 0.50])) * (0.85 + 0.15 * fbm(beta=2.4, seed=75)[..., None])
save("ammattonato", col, mort, 0.85, 3.0)

# lastrico a filari: regular rectangular pietra forte slabs in running rows (0.5 x 1.0 m), 4 m tile
h, rnd, fu, fv = blocks(rows=8, cols_per_row=4, offset=0.5, mortar=0.004, bevel=0.01, seed=81)
chisel = fbm(beta=0.4, seed=82); wear = fbm(beta=1.8, seed=83)
col = tint(rnd * 0.55 + wear * 0.45, (0.46, 0.45, 0.43), (0.66, 0.65, 0.62))   # weathered pietra forte reads grey today * (0.55 + 0.45 * h[..., None]) * (0.93 + 0.07 * chisel[..., None])
save("lastrico_filari", col, h * 0.8 + chisel * 0.08, 0.78 + 0.12 * wear, 5.0)

# asfalto: fine aggregate, darker tar seams and patches, 6 m tile
g = fbm(beta=0.3, seed=91); pt = blur_wrap((fbm(beta=2.4, seed=92) > 0.7).astype(float), 4)
seam = np.exp(-((xx % 1 - 0.37) ** 2) * 6000) * (fbm(beta=2.0, seed=93) > 0.62)
col = tint(g * 0.6 + fbm(beta=1.8, seed=94) * 0.4, (0.16, 0.16, 0.17), (0.30, 0.30, 0.30)) * (1 - 0.25 * pt[..., None]) * (1 - 0.5 * seam[..., None])
save("asfalto", col, g * 0.15, 0.88 - 0.1 * pt, 2.0)

# lastrico (replaces the first version): the historic Florentine pavement – large pietra forte slabs, roughly
# rectangular, in irregular courses (~1.0 x 0.6 m), chiselled surface, worn and darker joints. 5 m tile.
e, sid, k = voronoi(0, 13, (5, 8))
h = np.clip(e / 0.008, 0, 1) ** 0.5; rs = np.random.default_rng(14).random(k)[sid]
wear = fbm(beta=1.4, seed=15); chisel = fbm(beta=0.3, seed=16)
col = tint(rs * 0.5 + wear * 0.5, (0.44, 0.43, 0.41), (0.67, 0.66, 0.63)) * (0.5 + 0.5 * h[..., None])   # light to mid grey slabs * (0.92 + 0.08 * chisel[..., None])
save("lastrico", col, h * (0.85 + 0.15 * wear) + chisel * 0.05, 0.82 + 0.1 * wear, 5.0)

# lastrico a spina di pesce: regular pietra forte slabs (~0.9 x 0.45 m) laid in herring-bone, grey, chiselled, 4 m tile.
# Many streets of today's centre (19th-century relaying and modern restorations) have this neat pattern.
u = xx * 4.5; v = yy * 4.5
a = np.floor(u + v); b = np.floor(u - v)
stripe = (np.floor(u + v) % 2)
lu = np.where(stripe == 0, (u - v) * 2 % 1, (u + v) * 2 % 1)
lv = np.where(stripe == 0, (u + v) % 1, (u - v) % 1)
joint = np.minimum(np.minimum(lu, 1 - lu) * 9, np.minimum(lv, 1 - lv) * 18).clip(0, 1)
bid = np.where(stripe == 0, np.floor((u - v) * 2) * 31 + a, np.floor((u + v) * 2) * 17 + b)
rb = (np.sin(bid * 12.9898) * 43758.5453) % 1
wear = fbm(beta=1.6, seed=101); chisel = fbm(beta=0.3, seed=102)
col = tint(rb * 0.55 + wear * 0.45, (0.47, 0.46, 0.44), (0.68, 0.67, 0.64)) * (0.93 + 0.07 * chisel[..., None])
col = np.where(joint[..., None] > 0.3, col, np.array([0.34, 0.33, 0.31])) * (0.9 + 0.1 * wear[..., None])
save("lastrico_spina", col, joint * 0.9 + chisel * 0.06, 0.8 + 0.1 * wear, 5.0)

# ==================== street stone from photographs (Jany, Nov 2026) ====================
# Florence's lastricato: rectangular slabs of pietra forte (grey-brown) and pietra serena (blue-grey) laid in courses,
# lengths varying along each course, joints filled with light grey mortar; the top is dressed against slipping:
# parallel chisel grooves, herring-bone grooves (spina di pesce), or rows of punched dots ("bocciardato"), and old
# slabs are worn smooth and mottled. Relief is baked into the colour (the ground shader uses colour maps only).
def baked(h, k=9.0):
    """Light from the north-west at 40°, baked into a 0.6..1.15 factor from the height field."""
    dx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * k; dy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * k
    n = np.stack([-dx, dy, np.ones_like(h)], -1); n /= np.linalg.norm(n, axis=-1, keepdims=True)
    L = np.array([-0.5, 0.45, 0.74]); L /= np.linalg.norm(L)
    return np.clip(0.55 + 0.55 * (n @ L), 0.55, 1.15)

def coursed_slabs(rows, lmin, lmax, seed, finish_p, tint_p=0.5, wear=0.5, edge_noise=0.006, joint=0.0045):
    """rows of slabs across the tile (periodic); finish_p: probabilities of [smooth, grooves, herringbone, dots]."""
    r = np.random.default_rng(seed)
    row = np.floor(yy * rows).astype(int); v = yy * rows - row                    # 0..1 across the course
    sid = np.zeros((N, N), int); u = np.zeros((N, N)); L = np.zeros((N, N))
    k = 0
    for ri in range(rows):
        ls = []; tot = 0
        while tot < 1:
            l = r.uniform(lmin, lmax); ls.append(l); tot += l
        ls = np.array(ls) / tot; edges = np.concatenate([[0], np.cumsum(ls)]) + r.random()   # random phase per course
        m = row == ri; x = xx[m]
        xi = np.mod(x - edges[0], 1.0) + edges[0]
        j = np.clip(np.searchsorted(edges, xi, side="right") - 1, 0, len(ls) - 1)
        sid[m] = k + j; u[m] = (xi - edges[j]) / ls[j]; L[m] = ls[j]; k += len(ls)
    nS = k
    # distance to the slab edge in metres-ish units, wobbly (hand-cut edges), rounded corners
    en = (fbm(beta=2.6, seed=seed + 1) - 0.5) * edge_noise * 2
    du = np.minimum(u, 1 - u) * L; dv = np.minimum(v, 1 - v) / rows
    d = np.sqrt(np.minimum(du, 0.05) ** 2 + np.minimum(dv, 0.05) ** 2) * 0 + np.minimum(du, dv) + en
    body = np.clip((d - joint) / 0.003, 0, 1)                                     # 0 joint .. 1 slab top
    edge_round = np.clip((d - joint) / 0.008, 0, 1) ** 0.4
    rs = r.random((nS, 6)); S = rs[sid]
    fin = np.searchsorted(np.cumsum(finish_p), S[:, :, 0])                       # finish per slab
    ang = np.where(S[:, :, 1] < 0.5, 0, 1)                                       # grooves along or across
    # local coords in "metres" for the dressing patterns
    lx = u * L * 4.0; ly = v / rows * 4.0                                          # tile = 4 m
    wob = (fbm(beta=2.2, seed=seed + 6) - 0.5) * 0.02                            # hand-chiselled: grooves wander
    grooves = np.where(ang == 0, np.sin((lx + wob) * 2 * np.pi / 0.05), np.sin((ly + wob) * 2 * np.pi / 0.05))
    hb_band = np.floor(ly / 0.09) % 2
    herring = np.sin(((lx + wob + np.where(hb_band == 0, ly, -ly)) * 2 * np.pi / 0.055))
    dots = np.sqrt(((lx / 0.045) % 1 - 0.5) ** 2 + ((ly / 0.05 + (np.floor(lx / 0.045) % 2) * 0.5) % 1 - 0.5) ** 2)
    pit = np.clip(1 - dots / 0.22, 0, 1)
    w = fbm(beta=1.7, seed=seed + 2)                                               # wear: smooths the dressing away
    keep = np.clip((S[:, :, 2] * 0.6 + 0.5) - w * wear, 0, 1)
    rel = np.select([fin == 1, fin == 2, fin == 3], [np.abs(grooves) * -0.5, np.abs(herring) * -0.5, -pit], 0.0) * keep
    mott = fbm(beta=1.1, seed=seed + 3)                                            # stone grain and mottling
    h = body * 0.12 * edge_round + body * 0.35 * rel + mott * 0.02
    # colour: pietra serena blue-grey or pietra forte grey-brown per slab, varied; joints light mortar with grit
    serena = np.array([0.49, 0.50, 0.52]); forte = np.array([0.50, 0.48, 0.45])
    base = np.where((S[:, :, 3] < tint_p)[..., None], serena, forte) * (0.88 + 0.16 * S[:, :, 4])[..., None]
    base = base * (0.9 + 0.2 * mott[..., None])
    base = base * (1 - 0.18 * (np.clip(-rel, 0, 1) * keep)[..., None])            # dirt in the grooves and pits
    stains = (fbm(beta=2.0, seed=seed + 4) > 0.8) * 0.12
    base = base * (1 - stains[..., None])
    grit = fbm(beta=0.2, seed=seed + 5)
    mortar = np.array([0.60, 0.59, 0.56]) * (0.85 + 0.25 * grit)[..., None]
    col = mortar * (1 - body[..., None]) + base * body[..., None]
    col = col * baked(h, 6.0)[..., None]
    rough = 0.75 + 0.15 * (1 - body) - 0.1 * (1 - keep) * body
    return col, h, rough

# lastrico: older, irregular courses, mostly worn smooth (some faint grooves)
col, h, rough = coursed_slabs(rows=6, lmin=0.12, lmax=0.32, seed=301, finish_p=[0.6, 0.2, 0.05, 0.15], tint_p=0.3, wear=0.8, edge_noise=0.02)
save("lastrico", col, h, rough, 5.0)
# lastrico_filari: neat courses, dressed tops (grooves, herring-bone, punched dots), some worn
col, h, rough = coursed_slabs(rows=7, lmin=0.14, lmax=0.26, seed=311, finish_p=[0.3, 0.3, 0.15, 0.25], tint_p=0.5, wear=0.45, edge_noise=0.008)
save("lastrico_filari", col, h, rough, 5.0)
# lastrico_spina: squarer slabs dressed in herring-bone (laid on the diagonal by the shader, as in Piazza Donatello)
col, h, rough = coursed_slabs(rows=5, lmin=0.16, lmax=0.24, seed=321, finish_p=[0.1, 0.05, 0.8, 0.05], tint_p=0.6, wear=0.3, edge_noise=0.006)
save("lastrico_spina", col, h, rough, 5.0)

# terra (redone): packed earth with fine gravel and small stones, wheel-worn paler bands, damp darker hollows,
# grey-brown (Arno valley alluvium), never orange
n1 = fbm(beta=2.3, seed=401); n2 = fbm(beta=1.3, seed=402); n3 = fbm(beta=0.6, seed=403)
earth = tint(n1 * 0.6 + n2 * 0.4, (0.36, 0.33, 0.28), (0.52, 0.48, 0.41))
_r = np.random.default_rng(404); _pts = _r.random((5000, 2)); _rad = _r.uniform(0.0007, 0.0026, 5000)   # pebbles 1-4 cm (8 m tile)
_P = np.concatenate([_pts + [dx, dy] for dx in (-1, 0, 1) for dy in (-1, 0, 1)])
_d, _i = _KD(_P).query(np.stack([xx.ravel(), yy.ravel()], 1), k=1); _i = _i % len(_pts)
_d = _d.reshape(N, N); _i = _i.reshape(N, N)
pebble = _d < _rad[_i]; e = np.clip(_rad[_i] - _d, 0, None)
peb_col = tint(_r.random(5000)[_i], (0.42, 0.40, 0.36), (0.58, 0.56, 0.51))
ruts = np.exp(-((np.sin(2 * np.pi * (yy * 2 + 0.3 * (fbm(beta=2.6, seed=407) - 0.5))) - 0.75) ** 2) * 25)
damp = blur_wrap((fbm(beta=2.4, seed=408) > 0.72).astype(float), 6)
hh = n1 * 0.3 + n3 * 0.15 + pebble * (0.3 + 0.5 * np.sqrt(np.clip(e / 0.003, 0, 1))) - ruts * 0.1
col = np.where(pebble[..., None], peb_col, earth) * (1 + 0.1 * ruts[..., None]) * (1 - 0.25 * damp[..., None])
col = col * (0.88 + 0.18 * n3[..., None]) * baked(hh, 4.0)[..., None]
save("terra", col, hh, 0.95 - 0.3 * damp, 3.0)

# ammattonato (redone): old bricks on edge in herring-bone, weathered and dusty – muted brown-grey, not roof-tile red
u = xx * 8; v = yy * 8
stripe = (np.floor(u + v) % 2); a = np.floor(u + v); b = np.floor(u - v)
lu = np.where(stripe == 0, (u - v) * 2 % 1, (u + v) * 2 % 1); lv = np.where(stripe == 0, (u + v) % 1, (u - v) % 1)
mort = np.minimum(np.minimum(lu, 1 - lu) * 6, np.minimum(lv, 1 - lv) * 18).clip(0, 1)
bid = np.where(stripe == 0, np.floor((u - v) * 2) * 31 + a, np.floor((u + v) * 2) * 17 + b)
rb = (np.sin(bid * 12.9898) * 43758.5453) % 1; dust = fbm(beta=1.5, seed=411)
brick = tint(rb * 0.6 + fbm(seed=412) * 0.4, (0.42, 0.36, 0.31), (0.54, 0.46, 0.39))
brick = brick * (1 - 0.35 * dust[..., None]) + np.array([0.52, 0.49, 0.44]) * 0.35 * dust[..., None]   # dust and wear
hh = mort * 0.8 + dust * 0.05
col = np.where(mort[..., None] > 0.25, brick, np.array([0.55, 0.52, 0.47])) * baked(hh, 5.0)[..., None]
save("ammattonato", col, hh, 0.88, 3.0)
