// Rounder ground: the LiDAR terrain is a 4 m grid, so slopes read as straight facets meeting at sharp corners. Here it is
//  1. softened – each point moves part of the way to its neighbours' weighted mean, but only where that mean is within a
//     metre of it: gentle slopes and hill shoulders round off, while the river's bed, the lungarni's walls, terraces and
//     steps (real breaks of more than a metre) are kept exactly as measured;
//  2. resampled at half the step with Catmull-Rom splines through the measured points (clamped to each cell's own range,
//     so a wall's foot never rings above or below it): the surface passes through the softened heights, curving between.
// The same grid is used for the mesh and for every height lookup (people, props, boats), so nothing floats or sinks.

export interface TerrainGrid { h: Float32Array; n: number; step: number }

export function refineTerrain(h0: Float32Array, n: number, step: number, up = 2, keep = 1.0, amount = 0.6): TerrainGrid {
  // 1. soften
  const h = new Float32Array(h0);
  for (let j = 1; j < n - 1; j++) for (let i = 1; i < n - 1; i++) {
    const k = j * n + i;
    const b = (4 * h0[k] + 2 * (h0[k - 1] + h0[k + 1] + h0[k - n] + h0[k + n]) + h0[k - n - 1] + h0[k - n + 1] + h0[k + n - 1] + h0[k + n + 1]) / 16;
    const d = b - h0[k];
    if (Math.abs(d) < keep) h[k] = h0[k] + d * amount;
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
export function terrainGrid(src: Float32Array, n: number, step: number, up: number): TerrainGrid {
  if (cached && cached.src.length === src.length && cached.src[12345] === src[12345] && cached.grid.step === step / Math.max(1, up)) return cached.grid;
  const grid = refineTerrain(src, n, step, up); cached = { src, grid }; return grid;
}
