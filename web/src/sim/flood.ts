// The flood of 4 November 1966 as a Live scene: the Arno rises in its bed through the night, comes over the parapets and
// through the breaches at about 5 a.m., runs through the streets and squares, stands highest in the afternoon, begins to
// fall at about 8 p.m. and leaves the streets on 6 November.
// The water's surface is calibrated on two records: 4.92 m on the plaque in Via dei Neri (Santa Croce; Protezione Civile)
// and "at least six feet" (≈1.8 m) in Piazza del Duomo; between them it falls away from the river in a straight line with
// the distance from its axis (*inferred*). Ground lower than that surface is flooded; the water reaches
// each place after 5 a.m. at the speed that brings it from the bank to Piazza del Duomo by 9:45 (en.wikipedia), so the
// lungarni and Santa Croce fill first. Times (all sources in docs/landmarks/LUNGARNI.md, "1966"): banks give way ≈5:00, Duomo
// 9:45, highest in the afternoon, falling from 20:00, the streets clear on 6 November.
import * as THREE from 'three/webgpu';
import { Fn, attribute, uniform, float, clamp, select, positionLocal, vec3 } from 'three/tsl';

type Height = (x: number, z: number) => number;
const STEP = 8, X0 = -1700, X1 = 1700, Z0 = -720, Z1 = 1100;
const NERI = { x: 250, z: 315, depth: 4.92 }, DUOMO = { x: 27, z: -139, depth: 1.8 };
const BREAK = 5.0, DUOMO_AT = 9.75, PEAK = 16.0, FALL = 20.0, DRY = 56.0;     // hours from 00:00 on 4 November
const START = 3.5;                                                             // the scene opens before dawn, the Arno high in its bed
// where the water first came into the city: over and through the parapet at Piazza Cavalleggeri, into Santa Croce (Sky TG24)
const CAVALLEGGERI = 560;

export function createFlood(root: THREE.Object3D, height: Height) {
  const uH = uniform(0);
  let probe: (x: number, z: number) => number[] = () => [];
  let mesh: THREE.Mesh | null = null, label: HTMLDivElement | null = null, t = 0;
  let breach = { x: CAVALLEGGERI, z: 0 };
  // the flooded area's bounding box by the hour (every quarter from the break to the peak): the camera fits it
  const EXT_H0 = BREAK, EXT_DH = 0.25; let ext: [number, number, number, number][] = [];

  async function build(base: string) {
    const axis: number[][] = (await (await fetch(`${base}/river.json`)).json()).axis;
    const ax = (x: number) => {                                                 // the river's section at x: [wl, zc, zn, zs]
      const i = Math.max(0, Math.min(axis.length - 2, Math.floor((x - axis[0][0]) / (axis[1][0] - axis[0][0]))));
      const a = axis[i], b = axis[i + 1], f = Math.max(0, Math.min(1, (x - a[0]) / (b[0] - a[0])));
      return [1, 2, 3, 4].map(k => a[k] + (b[k] - a[k]) * f);
    };
    const dist = (x: number, z: number) => Math.abs(z - ax(x)[1]);
    const sN = height(NERI.x, NERI.z) + NERI.depth, sD = height(DUOMO.x, DUOMO.z) + DUOMO.depth;
    const dN = dist(NERI.x, NERI.z), dD = dist(DUOMO.x, DUOMO.z), k = (sD - sN) / (dD - dN);
    const surface = (x: number, z: number) => sN + (dist(x, z) - dN) * k;
    const nx = Math.round((X1 - X0) / STEP) + 1, nz = Math.round((Z1 - Z0) / STEP) + 1, N = nx * nz;
    const G = new Float32Array(N), S = new Float32Array(N), A = new Float32Array(N).fill(Infinity), ch = new Uint8Array(N);
    for (let j = 0; j < nz; j++) for (let i = 0; i < nx; i++) {
      const x = X0 + i * STEP, z = Z0 + j * STEP, c = j * nx + i, [wl, , zn, zs] = ax(x);
      G[c] = height(x, z); S[c] = surface(x, z);
      if (z > zn + 2 && z < zs - 2) { ch[c] = 1; G[c] = Math.min(G[c], wl); A[c] = 0; }       // the river's bed: water from the start
    }
    // Every cell lower than the flood's surface is flooded: the 4 m terrain grid smooths kerbs and building lines into
    // false ridges, so a path search over it cuts off squares that were under water (Piazza del Duomo). The water reaches a
    // cell after the banks give way at a speed set by its distance from the nearer bank: Duomo at 9:45.
    const bank = (x: number, z: number) => { const [, , zn, zs] = ax(x); return z < zn ? zn - z : z > zs ? z - zs : 0; };
    const speed = bank(DUOMO.x, DUOMO.z) / (DUOMO_AT - BREAK);                // metres an hour
    // Piazza Cavalleggeri goes first: from there the water runs into Santa Croce ahead of the overflow along the other banks
    breach = { x: CAVALLEGGERI, z: ax(CAVALLEGGERI)[2] };
    for (let c = 0; c < N; c++) if (!ch[c] && G[c] < S[c]) {
      const x = X0 + (c % nx) * STEP, z = Z0 + ((c / nx) | 0) * STEP;
      A[c] = Math.min(BREAK + 0.5 + bank(x, z) / speed, BREAK + Math.hypot(x - breach.x, z - breach.z) / (speed * 1.6));
    }
    { // extent of the water outside the river's bed at each quarter hour
      const n = Math.ceil((PEAK - EXT_H0) / EXT_DH) + 1; ext = [];
      for (let q = 0; q < n; q++) {
        const h = EXT_H0 + q * EXT_DH; let x0 = Infinity, x1 = -Infinity, z0 = Infinity, z1 = -Infinity;
        for (let c = 0; c < N; c++) if (!ch[c] && A[c] <= h) {
          const x = X0 + (c % nx) * STEP, z = Z0 + ((c / nx) | 0) * STEP;
          if (x < x0) x0 = x; if (x > x1) x1 = x; if (z < z0) z0 = z; if (z > z1) z1 = z;
        }
        ext.push(isFinite(x0) ? [x0, x1, z0, z1] : [breach.x - 60, breach.x + 60, breach.z - 60, breach.z + 20]);
      }
    }
    probe = (x, z) => { const c = Math.round((z - Z0) / STEP) * nx + Math.round((x - X0) / STEP); return [G[c], S[c], A[c], ch[c]]; };
    // the mesh: one quad a cell, vertices carry ground, surface and arrival time
    const pos = new Float32Array(N * 3), ga = new Float32Array(N), sa = new Float32Array(N), aa = new Float32Array(N);
    for (let j = 0; j < nz; j++) for (let i = 0; i < nx; i++) {
      const c = j * nx + i; pos[c * 3] = X0 + i * STEP; pos[c * 3 + 1] = G[c]; pos[c * 3 + 2] = Z0 + j * STEP;
      ga[c] = G[c]; sa[c] = S[c]; aa[c] = isFinite(A[c]) ? (ch[c] ? -6 : A[c]) : 999;
    }
    const idx: number[] = [];
    for (let j = 0; j < nz - 1; j++) for (let i = 0; i < nx - 1; i++) {
      const c = j * nx + i, cs = [c, c + 1, c + nx, c + nx + 1];
      if (cs.every(v => aa[v] >= 999)) continue;
      idx.push(c, c + nx, c + 1, c + 1, c + nx, c + nx + 1);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('g0', new THREE.BufferAttribute(ga, 1));
    g.setAttribute('s1', new THREE.BufferAttribute(sa, 1)); g.setAttribute('arr', new THREE.BufferAttribute(aa, 1));
    g.setIndex(idx); g.computeVertexNormals(); g.computeBoundingSphere();
    const mat = new THREE.MeshStandardNodeMaterial({ color: 0x55707a, roughness: 0.22, metalness: 0.08 });   // grey-blue, a little silt
    mat.positionNode = Fn(() => {
      const g0 = attribute('g0', 'float'), s1 = attribute('s1', 'float'), arr = attribute('arr', 'float');
      const rise = clamp(uH.sub(arr).div(float(PEAK).sub(arr).max(1)), 0, 1);
      const fall = float(1).sub(clamp(uH.sub(FALL).div(DRY - FALL), 0, 1));
      const depth = s1.sub(g0).max(0).mul(rise).mul(fall);
      const wet = uH.greaterThanEqual(arr).and(depth.greaterThan(0.03));
      return vec3(positionLocal.x, select(wet, g0.add(depth), float(-500)), positionLocal.z);
    })();
    mesh = new THREE.Mesh(g, mat); mesh.name = 'flood-1966'; mesh.frustumCulled = false; mesh.receiveShadow = true; root.add(mesh);
    label = document.createElement('div'); label.id = 'flood-clock';
    label.style.cssText = 'position:fixed;top:64px;left:50%;transform:translateX(-50%);padding:4px 12px;border-radius:12px;background:rgba(255,255,255,.85);font:600 13px system-ui;color:#5a1c1c;z-index:20;pointer-events:none';
    document.body.appendChild(label);
  }
  /** Played once in 100 s: 03:30 → 22:00 on 4 November in 70 s, then the fall to 08:00 on 6 November, a pause. */
  const hourAt = (t: number) => t < 70 ? START + t / 70 * (22 - START) : t < 95 ? 22 + (t - 70) / 25 * (DRY - 22) : DRY;
  function update(dt: number, len = 100) {
    if (!mesh) return;
    t = Math.min(len, t + dt);
    const h = hourAt(t);
    uH.value = h;
    if (label) {
      const day = 4 + Math.floor(h / 24), hh = Math.floor(h % 24), mm = Math.floor((h % 1) * 60 / 15) * 15;
      const what = h < BREAK ? 'the Arno rises in its bed' : h < DUOMO_AT ? 'over the parapets, into Santa Croce' : h < PEAK ? 'Piazza del Duomo under water' : h < FALL ? 'the highest water' : h < DRY ? 'the water falls' : 'the streets clear';
      label.textContent = `${day} November 1966 · ${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')} · ${what}`;
    }
  }
  function clear() { if (mesh) { mesh.geometry.dispose(); root.remove(mesh); mesh = null; } label?.remove(); label = null; t = 0; }
  /** Jump the loop to an hour of 4 November (debug and the timeline). */
  function seek(h: number) { t = h <= 22 ? Math.max(0, h - START) / (22 - START) * 70 : 70 + (h - 22) / (DRY - 22) * 25; }
  /** The hour for the sun (the scene lights itself, from night to day and back). */
  // Sunrise in Florence in early November is ≈6:50, sunset ≈17:00. The night is drawn as a deep dawn and dusk so the
  // water stays readable: 03:30 opens at first light and brightens to day by 7:30.
  const lightHour = () => {
    if (!mesh) return null;
    const h = hourAt(t) % 24;
    if (h < 7.5) return 6.15 + Math.max(0, h - 3.5) / 4 * 1.35;
    if (h > 17.5) return 17.8;                                                    // the evening held at dusk
    return h;
  };
  /** Where the camera should look: close over the first break in the parapet, then out over the flooded quarters. */
  const ease = (a: number, b: number, h: number) => { const k = Math.min(1, Math.max(0, (h - a) / (b - a))); return k * k * (3 - 2 * k); };
  /** The flooded area at hour h: [x0, x1, z0, z1] (interpolated between quarter hours, fixed after the peak). */
  function extentAt(h: number) {
    if (!ext.length) return null;
    const f = Math.max(0, Math.min(ext.length - 1, (h - EXT_H0) / EXT_DH)), i = Math.min(ext.length - 2, Math.floor(f)), k = f - i;
    const a = ext[i], b = ext[Math.min(ext.length - 1, i + 1)];
    return a.map((v, j) => v + (b[j] - v) * k) as [number, number, number, number];
  }
  function camGoal(aspect = 1.6): [number, number, number, number, number] | null {
    if (!mesh) return null;
    const h = hourAt(t);
    // from the far bank, low, the parapet at Piazza Cavalleggeri in front and Santa Croce behind; as soon as the water is
    // out (5:00) the view rises and keeps drawing back as it spreads, so the whole flooded area stays in view (it is
    // fitted into the part of the screen the side panels leave free: `aspect`), and stays there to the end
    const x0 = 520, z0 = 445, d0 = 320, p0 = 1.33, a0 = 0.05;                                     // over the parapet (bank at z ≈565)
    const s = ease(BREAK, BREAK + 0.9, h), e = extentAt(Math.min(h, PEAK));
    if (!e || s <= 0) return [x0, z0, d0, p0, a0];
    const pitch = 0.78, az = 0.25;                                                                // from the south, looking north
    const w = (e[1] - e[0]) + 120, dep = (e[3] - e[2]) + 120, cx = (e[0] + e[1]) / 2, cz = (e[2] + e[3]) / 2;
    // vertical field 32°: the view is 0.573·d high and 0.573·d·aspect wide at distance d; the ground's depth is seen
    // foreshortened by the pitch, so it needs a little less height than its length
    const fov = 0.573, need = Math.max(w / (fov * aspect), dep * Math.cos(pitch) * 1.25 / fov, 420);
    return [x0 + (cx - x0) * s, z0 + (cz - z0) * s, d0 + (need - d0) * s, p0 + (pitch - p0) * s, a0 + (az - a0) * s];
  }
  const api = { build, update, clear, seek, lightHour, camGoal, probe: (x: number, z: number) => probe(x, z), get on() { return !!mesh; },
    duration: 100, get time() { return t; }, set time(v: number) { t = Math.max(0, Math.min(100, v)); } };
  (window as unknown as { __flood?: typeof api }).__flood = api;
  return api;
}
