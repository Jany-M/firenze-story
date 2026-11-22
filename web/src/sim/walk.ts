// Where people may stand and walk: streets, squares, fields – never inside a building, a tree trunk or a placed prop.
// Buildings come from the footprint grid written by pipeline/20_build_city.py (2 m cells, record id + 1, two layers:
// present-day and historic) and are solid only in the years their record stands. Trees and scene props are added here.
import * as THREE from 'three/webgpu';
import { isAlive, type Rec } from '../scene/city';

const RES = 2, HALF = 1000, W = (2 * HALF) / RES, CELL = 4;
let recs: Rec[] = [], foot: Uint16Array | null = null, trees: Float32Array | null = null, year = 2026;
const treeGrid = new Map<number, number[]>();            // 4 m cells → tree indices
let boxes: { x0: number; x1: number; z0: number; z1: number }[] = [];
const key = (cx: number, cz: number) => cx * 100003 + cz;

function building(x: number, z: number) {
  if (!foot) return false;
  const c = Math.floor((x + HALF) / RES), r = Math.floor((z + HALF) / RES);
  if (c < 0 || r < 0 || c >= W || r >= W) return false;
  for (let L = 0; L < 2; L++) {
    const id = foot[L * W * W + r * W + c];
    if (id && recs[id - 1] && isAlive(recs[id - 1], year)) return true;
  }
  return false;
}
function tree(x: number, z: number, r: number) {
  if (!trees) return false;
  const cx = Math.floor(x / CELL), cz = Math.floor(z / CELL);
  for (let dx = -1; dx <= 1; dx++) for (let dz = -1; dz <= 1; dz++) {
    for (const i of treeGrid.get(key(cx + dx, cz + dz)) ?? []) {
      const s = i * 7; if (year < trees[s + 5] || year >= trees[s + 6]) continue;
      if (Math.hypot(trees[s] - x, trees[s + 2] - z) < 0.6 + r) return true;
    }
  }
  return false;
}

export const walk = {
  init(r: Rec[], f: Uint16Array | null, t: Float32Array | null) {
    recs = r; foot = f && f.length === 2 * W * W ? f : null; trees = t; treeGrid.clear();
    if (t) for (let i = 0; i < t.length / 7; i++) {
      const k = key(Math.floor(t[i * 7] / CELL), Math.floor(t[i * 7 + 2] / CELL));
      (treeGrid.get(k) ?? treeGrid.set(k, []).get(k)!).push(i);
    }
  },
  setYear(y: number) { year = Math.round(y); },
  get ready() { return !!foot; },
  /** Solid at (x, z) for a body of radius r? */
  blocked(x: number, z: number, r = 0.3, props = true) {
    if (building(x, z) || building(x + r, z) || building(x - r, z) || building(x, z + r) || building(x, z - r)) return true;
    if (tree(x, z, r)) return true;
    if (props) for (const b of boxes) if (x > b.x0 - r && x < b.x1 + r && z > b.z0 - r && z < b.z1 + r) return true;
    return false;
  },
  /** Nearest free spot within `max` metres (spiral search), or null. */
  nearestFree(x: number, z: number, max = 8, r = 0.3, props = true): [number, number] | null {
    if (!this.blocked(x, z, r, props)) return [x, z];
    for (let d = 0.8; d <= max; d += 0.8) for (let k = 0; k < 12; k++) {
      const a = (k / 12) * Math.PI * 2 + d, px = x + Math.cos(a) * d, pz = z + Math.sin(a) * d;
      if (!this.blocked(px, pz, r, props)) return [px, pz];
    }
    return null;
  },
  /** Step `d` from `p`, turning up to ±120° around an obstacle; returns the step taken (zero if boxed in). */
  steer(p: THREE.Vector3, d: THREE.Vector3, r = 0.3) {
    const L = Math.hypot(d.x, d.z); if (L < 1e-6) return d;
    for (const a of [0, 0.5, -0.5, 1.0, -1.0, 1.6, -1.6, 2.1, -2.1]) {
      const c = Math.cos(a), s = Math.sin(a), x = d.x * c - d.z * s, z = d.x * s + d.z * c;
      if (!this.blocked(p.x + x * 1.6, p.z + z * 1.6, r)) return d.set(x, d.y, z);
    }
    return d.set(0, d.y, 0);
  },
  /** Props placed by scenes (stalls, stands, the cart…) become solid boxes until clearProps(). */
  addProp(o: THREE.Object3D, pad = 0.2) {
    const b = new THREE.Box3().setFromObject(o); if (b.isEmpty()) return;
    boxes.push({ x0: b.min.x - pad, x1: b.max.x + pad, z0: b.min.z - pad, z1: b.max.z + pad });
  },
  clearProps() { boxes = []; },
};
