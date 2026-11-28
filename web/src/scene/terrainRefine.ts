// Rounder ground: the LiDAR terrain is a 4 m grid, so slopes read as straight facets meeting at sharp corners. Here it is
//  1. softened, in two ways:
//     a. bumps: each point moves most of the way to its neighbours' weighted mean wherever that mean is within 2 m of it,
//        three times over, so a field of small ridges and hollows close together relaxes as a whole into rolling ground
//        instead of reading as a row of separate bumps;
//     b. breaks: what is left of a step (a bank, a terrace edge with no wall) is spread by a wider blur into a slope, a point
//        moving by at most 3 m: a 7 m river bank becomes a bank sloping over some 10–12 m, not a cliff. Ground under or
//        beside a building (the footprint grid, any year) is kept as measured, so no house is left standing on air. Walls
//        built as models (the lungarni, the Piazzale) put their vertical faces back through the ground edits below.
//  2. resampled at half the step with Catmull-Rom splines through the softened points (clamped to each cell's own range,
//     so a wall's foot never rings above or below it): the surface passes through the softened heights, curving between.
// The same grid is used for the mesh and for every height lookup (people, props, boats), so nothing floats or sinks.

export interface TerrainGrid { h: Float32Array; n: number; step: number }

export function refineTerrain(h0: Float32Array, n: number, step: number, up = 2, keep = 2.0, amount = 0.75, keepMask?: Uint8Array): TerrainGrid {
  // 1a. bumps
  const nb = (g: Float32Array, k: number) =>
    (4 * g[k] + 2 * (g[k - 1] + g[k + 1] + g[k - n] + g[k + n]) + g[k - n - 1] + g[k - n + 1] + g[k + n - 1] + g[k + n + 1]) / 16;
  let h = new Float32Array(h0);
  for (let pass = 0; pass < 3; pass++) {
    const src = h; h = new Float32Array(src);
    for (let j = 1; j < n - 1; j++) for (let i = 1; i < n - 1; i++) {
      const k = j * n + i, strict = keepMask?.[k] === 1;      // 1: by a building, 2: round a landmark's walls (bumps only)
      if (strict && pass) continue;
      const d = nb(src, k) - src[k], lim = strict ? 1.0 : keep;
      if (Math.abs(d) < lim) h[k] = src[k] + d * (strict ? 0.6 : amount);
    }
  }
  // 1b. breaks: five passes of the same kernel (a blur some 6 m wide), the move capped at 3 m, none at buildings
  let b = h;
  for (let pass = 0; pass < 5; pass++) {
    const src = b; b = new Float32Array(src);
    for (let j = 1; j < n - 1; j++) for (let i = 1; i < n - 1; i++) b[j * n + i] = nb(src, j * n + i);
  }
  for (let k = 0; k < h.length; k++) {
    if (keepMask && keepMask[k]) continue;
    h[k] += Math.max(-3, Math.min(3, b[k] - h[k]));
  }
  if (up <= 1) return { h, n, step };
  // 2. Catmull-Rom resampling, separable: rows first, then columns
  const m = (n - 1) * up + 1;
  const cr = (p0: number, p1: number, p2: number, p3: number, t: number) => {
    const t2 = t * t, t3 = t2 * t;
    const v = 0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3);
    return Math.min(Math.max(v, Math.min(p1, p2)), Math.max(p1, p2));          // no overshoot past the cell's two ends
  };
  const rows = new Float32Array(n * m);
  for (let j = 0; j < n; j++) {
    const r = j * n;
    for (let I = 0; I < m; I++) {
      const i = Math.min(n - 2, Math.floor(I / up)), t = I / up - i;
      rows[j * m + I] = cr(h[r + Math.max(0, i - 1)], h[r + i], h[r + i + 1], h[r + Math.min(n - 1, i + 2)], t);
    }
  }
  const out = new Float32Array(m * m);
  for (let J = 0; J < m; J++) {
    const j = Math.min(n - 2, Math.floor(J / up)), t = J / up - j;
    const a = Math.max(0, j - 1) * m, b = j * m, c = (j + 1) * m, d = Math.min(n - 1, j + 2) * m;
    for (let I = 0; I < m; I++) out[J * m + I] = cr(rows[a + I], rows[b + I], rows[c + I], rows[d + I], t);
  }
  return { h: out, n: m, step: step / up };
}

let cached: { src: Float32Array; grid: TerrainGrid } | null = null;
/** One refined grid per session (the environment and the height lookup ask for the same one). */
export function terrainGrid(src: Float32Array, n: number, step: number, up: number, keepMask?: Uint8Array): TerrainGrid {
  if (cached && cached.src.length === src.length && cached.src[12345] === src[12345] && cached.grid.step === step / Math.max(1, up)) return cached.grid;
  const grid = refineTerrain(src, n, step, up, 2.0, 0.75, keepMask); cached = { src, grid }; return grid;
}

/** Marks (in place) the vertices within `pad` m of an undated ground edit: round a landmark's walls the ground stays as
 *  measured, so the softening does not push a slope out past the strip the model cuts in front of its walls. */
export function markEdits(m: Uint8Array, edits: GroundEdit[], n: number, step: number, pad = 8) {
  const half = ((n - 1) * step) / 2;
  for (const e of edits) {
    if (e.from !== undefined) continue;
    let x0 = Infinity, x1 = -Infinity, z0 = Infinity, z1 = -Infinity;
    for (const [x, z] of e.poly) { x0 = Math.min(x0, x); x1 = Math.max(x1, x); z0 = Math.min(z0, z); z1 = Math.max(z1, z); }
    const i0 = Math.max(0, Math.floor((x0 - pad + half) / step)), i1 = Math.min(n - 1, Math.ceil((x1 + pad + half) / step));
    const j0 = Math.max(0, Math.floor((z0 - pad + half) / step)), j1 = Math.min(n - 1, Math.ceil((z1 + pad + half) / step));
    for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) if (!m[j * n + i]) m[j * n + i] = 2;
  }
  return m;
}

/** Marks (in place, never lowering a mark) the vertices within r m of the outline pts (its vertices and edges) with `val`. */
export function markNear(m: Uint8Array, pts: [number, number][], n: number, step: number, r: number, val: 1 | 2) {
  const half = ((n - 1) * step) / 2;
  for (let a = 0; a < pts.length; a++) {
    const [x0, z0] = pts[a], [x1, z1] = pts[(a + 1) % pts.length], L = Math.hypot(x1 - x0, z1 - z0);
    const i0 = Math.max(0, Math.floor((Math.min(x0, x1) - r + half) / step)), i1 = Math.min(n - 1, Math.ceil((Math.max(x0, x1) + r + half) / step));
    const j0 = Math.max(0, Math.floor((Math.min(z0, z1) - r + half) / step)), j1 = Math.min(n - 1, Math.ceil((Math.max(z0, z1) + r + half) / step));
    for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) {
      const x = -half + i * step, z = -half + j * step;
      const t = L ? Math.max(0, Math.min(1, ((x - x0) * (x1 - x0) + (z - z0) * (z1 - z0)) / (L * L))) : 0;
      if (Math.hypot(x - x0 - (x1 - x0) * t, z - z0 - (z1 - z0) * t) > r) continue;
      const k = j * n + i; if (!m[k] || val < m[k]) m[k] = val;
    }
  }
}

/** Terrain vertices to keep as measured: within one cell of a building's footprint in any year (footprints.u16: 2 m cells,
 *  two layers, written by pipeline/20_build_city.py). */
export function buildingMask(foot: Uint16Array, n: number, step: number): Uint8Array {
  const RES = 2, W = Math.round(Math.sqrt(foot.length / 2)), HALF = (W * RES) / 2, half = ((n - 1) * step) / 2;
  const m = new Uint8Array(n * n), r = Math.ceil(step / RES);
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
    const c0 = Math.floor((-half + i * step + HALF) / RES), r0 = Math.floor((-half + j * step + HALF) / RES);
    search: for (let dr = -r; dr <= r; dr++) for (let dc = -r; dc <= r; dc++) {
      const c = c0 + dc, rr = r0 + dr; if (c < 0 || rr < 0 || c >= W || rr >= W) continue;
      if (foot[rr * W + c] || foot[W * W + rr * W + c]) { m[j * n + i] = 1; break search; }
    }
  }
  return m;
}

// Ground shaped round the landmark models (2026-11-27): a model's retaining walls, terraces and stairs are measured on
// the 0.5 m LiDAR, but the terrain here is a 2–4 m grid, so a wall's foot reads as a slope that climbs over the wall's
// lower courses. The build scripts write, per model, strips along each wall: in front (the low side) the ground is cut
// down to the wall's foot (`max`), behind it filled up to the top (`min`); under a paved terrace it is lowered a little
// (`drop`) so the model's paving shows. The model decides, the ground gives way. File: models/landmarks/ground_edits.json
export interface GroundEdit { poly: [number, number][]; max?: number; min?: number; drop?: number; from?: number; lift?: number }
// lift: how far the model's walking surface (paving, a ramp) stands over the ground left under it – added to the height people,
// benches and props are given there (the mesh keeps the lower ground, hidden under the slab). A `drop` lifts by drop + 0.04.
// An edit with `from` belongs to a structure built that year (a lungarno's wall and road): before it the ground keeps its own
// softened shape (a sloping bank), from it the edit holds. Those go to a second height array, chosen per vertex by year.
function inPoly(x: number, z: number, p: [number, number][]) {
  let c = false;
  for (let i = 0, j = p.length - 1; i < p.length; j = i++) {
    const [xi, zi] = p[i], [xj, zj] = p[j];
    if ((zi > z) !== (zj > z) && x < ((xj - xi) * (z - zi)) / (zj - zi) + xi) c = !c;
  }
  return c;
}
const applied = new WeakMap<Float32Array, Dated>();
function applyTo(g: TerrainGrid, h: Float32Array, edits: GroundEdit[], yr?: Float32Array, touched?: Uint8Array, lift?: Float32Array) {
  const half = ((g.n - 1) * g.step) / 2;
  const order = (e: GroundEdit) => (e.min !== undefined ? 0 : e.max !== undefined ? 1 : 2);   // fill, then cut (the low side wins), then lower
  for (const e of [...edits].sort((a, b) => order(a) - order(b))) {
    let x0 = Infinity, x1 = -Infinity, z0 = Infinity, z1 = -Infinity;
    for (const [x, z] of e.poly) { x0 = Math.min(x0, x); x1 = Math.max(x1, x); z0 = Math.min(z0, z); z1 = Math.max(z1, z); }
    const i0 = Math.max(0, Math.floor((x0 + half) / g.step)), i1 = Math.min(g.n - 1, Math.ceil((x1 + half) / g.step));
    const j0 = Math.max(0, Math.floor((z0 + half) / g.step)), j1 = Math.min(g.n - 1, Math.ceil((z1 + half) / g.step));
    for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) {
      if (!inPoly(-half + i * g.step, -half + j * g.step, e.poly)) continue;
      const k = j * g.n + i, was = h[k]; if (touched) touched[k] = 1;
      if (lift && (e.lift !== undefined || e.drop)) lift[k] = e.lift ?? e.drop! + 0.04;
      if (e.min !== undefined) h[k] = Math.max(h[k], e.min);
      else if (e.max !== undefined) h[k] = Math.min(h[k], e.max);
      else if (e.drop) h[k] -= e.drop;
      if (yr && h[k] !== was) yr[k] = Math.min(yr[k], e.from ?? 0);
    }
  }
}
/** Applies the undated edits to the grid in place; returns the dated ones' result: `h2` (the ground once they are built)
 *  and `yr` (per vertex, the year from which h2 holds; 99999 where they change nothing). */
export interface Dated { h2: Float32Array; yr: Float32Array; lift: Float32Array }
export function applyGroundEdits(g: TerrainGrid, edits: GroundEdit[], near?: { mask: Uint8Array; n: number }): Dated {
  const done = applied.get(g.h); if (done) return done;
  const yr = new Float32Array(g.h.length).fill(99999), touched = new Uint8Array(g.h.length), lift = new Float32Array(g.h.length);
  applyTo(g, g.h, edits.filter(e => e.from === undefined), undefined, touched, lift);
  const h2 = new Float32Array(g.h); applyTo(g, h2, edits.filter(e => e.from !== undefined), yr, touched);
  if (near) for (const h of [g.h, h2]) relaxNear(g, h, touched, near.mask, near.n);
  const res = { h2, yr, lift }; applied.set(g.h, res); return res;
}
/** Round a landmark the softening's wide blur is held back (markEdits), so what the LiDAR caught between its walls and the
 *  open ground – hedges, banks, steps cut in the slope – would stand up as sharp peaks. Once the edits are in, the ground
 *  there that no edit touched is relaxed (four passes, at most 1.5 m a point), the edited ground holding still as its edge. */
function relaxNear(g: TerrainGrid, h: Float32Array, touched: Uint8Array, mask: Uint8Array, ns: number) {
  const n = g.n, up = Math.round((n - 1) / (ns - 1)), orig = new Float32Array(h);
  const free = (i: number, j: number) => { const k = j * n + i; return !touched[k] && mask[Math.round(j / up) * ns + Math.round(i / up)] === 2; };
  const idx: number[] = [];
  for (let j = 1; j < n - 1; j++) for (let i = 1; i < n - 1; i++) if (free(i, j)) idx.push(j * n + i);
  for (let pass = 0; pass < 4; pass++) {
    const src = new Float32Array(h);
    for (const k of idx) {
      const b = (4 * src[k] + 2 * (src[k - 1] + src[k + 1] + src[k - n] + src[k + n]) + src[k - n - 1] + src[k - n + 1] + src[k + n - 1] + src[k + n + 1]) / 16;
      h[k] = orig[k] + Math.max(-1.5, Math.min(1.5, b - orig[k]));
    }
  }
}

/** Is (x, z) on a built surface of a landmark model – a lungarno's road, a paved terrace (the edits that raise the ground to
 *  a road, or lower it under a slab)? Trees are not planted there. Polygons bucketed in 20 m cells. */
export function surfaceTest(edits: GroundEdit[]) {
  const C = 20, cells = new Map<number, GroundEdit[]>();
  for (const e of edits) {
    if (e.min === undefined && !e.drop) continue;
    let x0 = Infinity, x1 = -Infinity, z0 = Infinity, z1 = -Infinity;
    for (const [x, z] of e.poly) { x0 = Math.min(x0, x); x1 = Math.max(x1, x); z0 = Math.min(z0, z); z1 = Math.max(z1, z); }
    if (e.min !== undefined && (x1 - x0) * (z1 - z0) < 1) continue;
    for (let i = Math.floor(x0 / C); i <= Math.floor(x1 / C); i++) for (let j = Math.floor(z0 / C); j <= Math.floor(z1 / C); j++) {
      const k = i * 100000 + j; let l = cells.get(k); if (!l) cells.set(k, (l = [])); l.push(e);
    }
  }
  return (x: number, z: number) => {
    const l = cells.get(Math.floor(x / C) * 100000 + Math.floor(z / C)); if (!l) return false;
    for (const e of l) if (inPoly(x, z, e.poly)) return true;
    return false;
  };
}
