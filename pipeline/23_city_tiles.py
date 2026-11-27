"""City tiles: splits the city mesh of 20_build_city.py into square tiles the app loads as the camera moves.

Input:  _dev/data/build/city/structures.{pos,nrm,bid,fu,fv,idx}.bin (one mesh, every structure; ~210 MB; written by 20_build_city.py)
Output: web/public/data/tiles/index.json and one gzipped t_<i>_<j>.bin.gz per tile (the app inflates it with DecompressionStream) (~half the size: positions as int16 at 2 cm
        from the tile corner, record ids as uint16, local uint16/uint32 indices)
A structure goes to the tile of its record's centre (structures.json "c"), so it is never split; structures longer than
400 m share one tile of their own. Each tile has its own corner (x0, z0) and scale q (index.json; 50 = 2 cm). File layout, all
little-endian, in this order: pos int16×3 (x, z from the tile corner, y + 100, each × q), nrm int8×4, bid uint16,
fu float32, fv float32, idx uint16 or uint32 (index.json "i32").
"""
import os, json, gzip, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "web", "public", "data"); OUT = os.path.join(D, "tiles")
M = os.environ.get("FS_MESH", os.path.join(ROOT, "_dev", "data", "build", "city"))
TILE = 300.0; Q = 50.0; YOFF = 100.0
recs = json.load(open(os.path.join(D, "structures.json"), encoding="utf-8"))["items"]
pos = np.fromfile(os.path.join(M, "structures.pos.bin"), np.float32).reshape(-1, 3)
nrm = np.fromfile(os.path.join(M, "structures.nrm.bin"), np.int8).reshape(-1, 4)
bid = np.fromfile(os.path.join(M, "structures.bid.bin"), np.float32)
fu = np.fromfile(os.path.join(M, "structures.fu.bin"), np.float32); fv = np.fromfile(os.path.join(M, "structures.fv.bin"), np.float32)
idx = np.fromfile(os.path.join(M, "structures.idx.bin"), np.uint32).reshape(-1, 3)
rb = np.rint(bid).astype(np.int64)
cx = np.array([r["c"][0] for r in recs]); cz = np.array([r["c"][1] for r in recs])
ti = np.floor(cx / TILE).astype(int); tj = np.floor(cz / TILE).astype(int)
rk = (ti + 100) * 1000 + (tj + 100)
# structures spanning more than 400 m (long walls, embankments) go together in one tile of their own, loaded first
ext = np.zeros(len(recs))
for a in (0, 2):
    mx = np.full(len(recs), -1e9); mn = np.full(len(recs), 1e9)
    np.maximum.at(mx, rb, pos[:, a]); np.minimum.at(mn, rb, pos[:, a]); ext = np.maximum(ext, mx - mn)
BIG = 999999; rk[ext > 400] = BIG
vt = rk[rb]                                       # tile key of each vertex
tri_t = vt[idx[:, 0]]
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):                       # old tiles (a tile that no longer exists would otherwise stay)
    if f.endswith((".bin", ".bin.gz")):
        try: os.remove(os.path.join(OUT, f))
        except OSError: pass
index = []
for key in np.unique(vt):
    vsel = np.nonzero(vt == key)[0]; tsel = idx[tri_t == key]
    if not len(tsel): continue
    P = pos[vsel]
    if key == BIG: i = j = 999; x0, z0 = float(np.floor(P[:, 0].min())), float(np.floor(P[:, 2].min()))
    else: i, j = int(key // 1000) - 100, int(key % 1000) - 100; x0, z0 = min(i * TILE, float(np.floor(P[:, 0].min()))), min(j * TILE, float(np.floor(P[:, 2].min())))
    span = max(P[:, 0].max() - x0, P[:, 2].max() - z0, P[:, 1].max() + YOFF) + 1
    q_ = min(Q, 32000.0 / span)
    remap = np.full(len(pos), -1, np.int64); remap[vsel] = np.arange(len(vsel))
    q = np.stack([(P[:, 0] - x0) * q_, (P[:, 1] + YOFF) * q_, (P[:, 2] - z0) * q_], 1)
    assert q.min() > -32768 and q.max() < 32767, (key, q.min(), q.max())
    loc = remap[tsel].reshape(-1); i32 = len(vsel) > 65535
    name = f"t_{i}_{j}.bin.gz"
    with gzip.open(os.path.join(OUT, name), "wb", compresslevel=9) as fh:
        fh.write(np.rint(q).astype("<i2").tobytes()); fh.write(nrm[vsel].tobytes())
        fh.write(rb[vsel].astype("<u2").tobytes()); fh.write(fu[vsel].astype("<f4").tobytes()); fh.write(fv[vsel].astype("<f4").tobytes())
        fh.write(loc.astype("<u4" if i32 else "<u2").tobytes())
    index.append({"f": name, "i": i, "j": j, "x0": x0, "z0": z0, "q": round(float(q_), 4), "big": bool(key == BIG), "nv": int(len(vsel)), "nt": int(len(tsel)), "i32": bool(i32),
                  "ymax": round(float(P[:, 1].max()), 1)})
json.dump({"tile": TILE, "q": Q, "yoff": YOFF, "tiles": index}, open(os.path.join(OUT, "index.json"), "w"), separators=(",", ":"))
tot = sum(os.path.getsize(os.path.join(OUT, t["f"])) for t in index)
print(f"{len(index)} tiles, {tot / 1e6:.1f} MB (was {sum(os.path.getsize(os.path.join(M, 'structures.' + n + '.bin')) for n in ('pos','nrm','bid','fu','fv','idx')) / 1e6:.1f} MB)")
