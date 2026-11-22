// Bridges as structures: deck at the height of the lungarni, piers with cutwaters, arches by type and era.
// Plan (position, crossing direction, width) comes from the bridge polygons (S02 / OSM, pipeline 21); the elevation
// from BRIDGE_SPECS below (number of spans, arch form, width per historical phase – docs/RIVER-LANDSCAPE.md).
import * as THREE from 'three/webgpu';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { texture, triplanarTexture, float } from 'three/tsl';
import type { TexSet } from './assets';

type Arch = 'round' | 'segment' | 'ellipse' | 'flat' | 'trestle' | 'suspension';
interface Spec { spans: number; arch: Arch; width: number; pier: number; rise?: number; houses?: boolean }
/** By bridge and phase start year. Sources: Comune "Una città e il suo fiume" (R02), standard histories. */
export const BRIDGE_SPECS: Record<string, Record<number, Spec>> = {
  'Ponte Vecchio': { [-30]: { spans: 0, arch: 'trestle', width: 6, pier: 0.5 }, 1177: { spans: 5, arch: 'round', width: 9, pier: 4 },
    1345: { spans: 3, arch: 'segment', width: 18, pier: 6, rise: 4.4 } },
  'Ponte alle Grazie': { 1237: { spans: 9, arch: 'round', width: 9, pier: 3.2, houses: true }, 1957: { spans: 5, arch: 'segment', width: 18, pier: 2.5, rise: 2.2 } },
  'Ponte Santa Trinita': { 1252: { spans: 5, arch: 'round', width: 8, pier: 4 }, 1346: { spans: 5, arch: 'round', width: 8, pier: 4 },
    1569: { spans: 3, arch: 'ellipse', width: 10.6, pier: 7.6, rise: 4.6 }, 1958: { spans: 3, arch: 'ellipse', width: 10.6, pier: 7.6, rise: 4.6 } },
  'Ponte alla Carraia': { 1220: { spans: 5, arch: 'round', width: 8, pier: 4 }, 1337: { spans: 5, arch: 'round', width: 8, pier: 4 },
    1559: { spans: 5, arch: 'segment', width: 10, pier: 4.5, rise: 4.2 }, 1952: { spans: 5, arch: 'segment', width: 15, pier: 3, rise: 3.2 } },
  'Ponte Amerigo Vespucci': { 1957: { spans: 3, arch: 'segment', width: 20, pier: 2.5, rise: 1.6 } },
  // San Niccolò: Seguin suspension bridge "San Ferdinando" 1837, washed out 1844, rebuilt 1853; three-span metal bridge
  // 1890 (tram); mined 1944; Morandi's single reinforced-concrete arch: main span 87.5 m, 132 m long, 17.5 m wide (structurae);
  // opening year 1949 in most Florentine sources, structurae gives works 1955–60 – kept 1949, to verify on dated photos
  'Ponte San Niccolò': { 1837: { spans: 1, arch: 'suspension', width: 7, pier: 0 }, 1853: { spans: 1, arch: 'suspension', width: 7, pier: 0 },
    1890: { spans: 3, arch: 'flat', width: 9, pier: 2.5 }, 1949: { spans: 1, arch: 'segment', width: 17.5, pier: 0, rise: 6.0 } },
  // Vittoria: Leopoldo II's suspension bridge "San Leopoldo" 1835 (four pillars with marble lions); Ponte alla Vittoria 1931;
  // mined 1944; rebuilt 1946, 142 m long, 15.5 m wide (structurae). Span counts of 1931 and 1946 *inferred* – to verify on photos
  'Ponte alla Vittoria': { 1835: { spans: 1, arch: 'suspension', width: 7, pier: 0 }, 1931: { spans: 3, arch: 'segment', width: 15, pier: 3, rise: 2.4 },
    1946: { spans: 3, arch: 'segment', width: 15.5, pier: 3, rise: 2.4 } },
};
const DEFAULT: Record<string, Spec> = {
  wood: { spans: 0, arch: 'trestle', width: 6, pier: 0.5 }, stone: { spans: 5, arch: 'round', width: 8, pier: 4 },
  iron: { spans: 1, arch: 'suspension', width: 7, pier: 0 }, concrete: { spans: 3, arch: 'segment', width: 16, pier: 2.5, rise: 2 },
};
export function specFor(name: string, start: number, kind: string): Spec {
  const byName = Object.entries(BRIDGE_SPECS).find(([n]) => name.toLowerCase().includes(n.toLowerCase().replace('ponte ', '')))?.[1];
  return byName?.[start] ?? DEFAULT[kind] ?? DEFAULT.stone;
}

export function bridgeMaterials(tex: TexSet) {
  const tri = (n: keyof TexSet, s: number) => triplanarTexture(texture(tex[n].col), null, null, float(s)).rgb;
  const stone = new THREE.MeshStandardNodeMaterial({ roughness: 0.92 }); stone.colorNode = tri('pietra_forte', 0.35);
  const wood = new THREE.MeshStandardNodeMaterial({ roughness: 0.95 }); wood.colorNode = tri('wood', 0.8);
  const plaster = new THREE.MeshStandardNodeMaterial({ roughness: 0.95 }); plaster.colorNode = tri('intonaco', 0.3);
  return {
    stone, wood, plaster,
    iron: new THREE.MeshStandardNodeMaterial({ color: 0x3e4446, roughness: 0.5, metalness: 0.7 }),
    concrete: new THREE.MeshStandardNodeMaterial({ color: 0xb3ab9c, roughness: 0.9 }),
    roof: new THREE.MeshStandardNodeMaterial({ color: 0xa4553a, roughness: 0.85 }),
  };
}

/** One bridge phase → a merged geometry per material. pts: plan polygon (x, z); wl: water level; groundAt: terrain height. */
export function buildBridge(pts: [number, number][], spec: Spec, wl: number, groundAt: (x: number, z: number) => number) {
  // plan frame: u = crossing direction (longest axis), v = across the deck
  const cx = pts.reduce((s, p) => s + p[0], 0) / pts.length, cz = pts.reduce((s, p) => s + p[1], 0) / pts.length;
  let sxx = 0, szz = 0, sxz = 0; for (const [x, z] of pts) { sxx += (x - cx) ** 2; szz += (z - cz) ** 2; sxz += (x - cx) * (z - cz); }
  const ang = 0.5 * Math.atan2(2 * sxz, sxx - szz), u = [Math.cos(ang), Math.sin(ang)], v = [-u[1], u[0]];
  let u0 = Infinity, u1 = -Infinity; for (const [x, z] of pts) { const a = (x - cx) * u[0] + (z - cz) * u[1]; u0 = Math.min(u0, a); u1 = Math.max(u1, a); }
  const at = (a: number) => [cx + u[0] * a, cz + u[1] * a];
  const [ax0, az0] = at(u0 - 5), [ax1, az1] = at(u1 + 5);
  const deck = Math.max(groundAt(ax0, az0), groundAt(ax1, az1), wl + 7) + 0.2;      // road level of the lungarni
  const W = spec.width, thick = spec.arch === 'trestle' || spec.arch === 'suspension' ? 0.7 : 1.3;
  const bed = wl - 3, spring = wl + 0.4, L = u1 - u0, abut = Math.max(4, L * 0.05);
  const out: Record<string, THREE.BufferGeometry[]> = {};
  const add = (m: string, g: THREE.BufferGeometry) => (out[m] ??= []).push(g);
  // place a geometry built in the local frame (x = along u from u0, y = up, z = across, centred)
  const M = new THREE.Matrix4().makeBasis(new THREE.Vector3(u[0], 0, u[1]), new THREE.Vector3(0, 1, 0), new THREE.Vector3(v[0], 0, v[1]))
    .setPosition(cx + u[0] * u0, 0, cz + u[1] * u0);
  const place = (g: THREE.BufferGeometry) => g.applyMatrix4(M);
  const box = (m: string, x0: number, x1: number, y0: number, y1: number, z0: number, z1: number) => {
    const g = new THREE.BoxGeometry(x1 - x0, y1 - y0, z1 - z0); g.translate((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2); add(m, place(g));
  };
  const mat = spec.arch === 'trestle' ? 'wood' : spec.arch === 'suspension' ? 'iron' : (spec.rise != null && spec.width >= 14) ? 'concrete' : 'stone';
  if (spec.arch === 'trestle') {                                   // wooden deck on rows of piles
    box('wood', 0, L, deck - thick, deck, -W / 2, W / 2);
    for (let a = abut; a < L - abut; a += 7) for (const z of [-W / 2 + 0.4, 0, W / 2 - 0.4]) {
      const g = new THREE.CylinderGeometry(0.22, 0.25, deck - bed, 6); g.translate(a, (deck + bed) / 2, z); add('wood', place(g));
    }
    for (const s of [-1, 1]) box('wood', 0, L, deck, deck + 1.0, s * W / 2 - 0.12, s * W / 2);
    return out;
  }
  if (spec.arch === 'suspension') {                                // iron suspension bridge with two stone pylons
    box('iron', 0, L, deck - thick, deck, -W / 2, W / 2);
    for (const a of [abut, L - abut]) for (const s of [-1, 1]) box('stone', a - 1.2, a + 1.2, bed, deck + 9, s * (W / 2 + 0.6) - 1.0, s * (W / 2 + 0.6) + 1.0);
    for (const s of [-1, 1]) {                                     // cables (catenary) and hangers
      const P: THREE.Vector3[] = [];
      for (let i = 0; i <= 24; i++) { const t = i / 24, a = abut + (L - 2 * abut) * t; P.push(new THREE.Vector3(a, deck + 9 - 8 * (1 - (2 * t - 1) ** 2), s * (W / 2 + 0.6))); }
      add('iron', place(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(P), 48, 0.12, 4)));
      for (let i = 1; i < 24; i += 2) { const p = P[i]; const g = new THREE.CylinderGeometry(0.04, 0.04, p.y - deck, 3); g.translate(p.x, (p.y + deck) / 2, p.z); add('iron', place(g)); }
    }
    for (const s of [-1, 1]) box('iron', 0, L, deck, deck + 1.0, s * W / 2 - 0.08, s * W / 2);
    return out;
  }
  // masonry / concrete: elevation shape (deck + arches) extruded across the width
  const n = spec.spans, p = spec.pier, Lw = L - 2 * abut, s = (Lw - (n - 1) * p) / n;
  const maxRise = deck - thick - spring;
  const rise = Math.min(spec.arch === 'round' ? s / 2 : spec.rise ?? s / 4, maxRise);
  const sh = new THREE.Shape();
  sh.moveTo(0, bed); sh.lineTo(0, deck); sh.lineTo(L, deck); sh.lineTo(L, bed);
  let x = L - abut; sh.lineTo(x, bed);
  for (let k = 0; k < n; k++) {
    const xa = x, xb = x - s;
    sh.lineTo(xa, spring);
    for (let i = 1; i < 16; i++) {                                   // intrados from right to left
      const t = i / 16, xx = xa - s * t, q = 2 * t - 1;
      let yy: number;
      if (spec.arch === 'round' || spec.arch === 'segment') {
        const R = (s * s / 4 + rise * rise) / (2 * rise); yy = spring + rise - R + Math.sqrt(Math.max(R * R - (q * s / 2) ** 2, 0));
      } else if (spec.arch === 'ellipse') yy = spring + rise * Math.pow(Math.max(1 - q * q, 0), 0.38);   // flattened "basket" curve (Ammannati)
      else yy = spring + rise;
      sh.lineTo(xx, yy);
    }
    sh.lineTo(xb, spring); sh.lineTo(xb, bed);
    x = xb - p; if (k < n - 1) sh.lineTo(x, bed);
  }
  sh.lineTo(abut, bed); sh.lineTo(0, bed);
  const eg = new THREE.ExtrudeGeometry(sh, { depth: W, bevelEnabled: false, curveSegments: 1 }); eg.translate(0, 0, -W / 2);
  add(mat, place(eg));
  // cutwaters on both sides of each pier, up to just under the spring of the arches
  for (let k = 1; k < n; k++) {
    const xm = L - abut - k * s - (k - 0.5) * p, hgt = spring + rise * 0.55 - bed;
    for (const sd of [-1, 1]) {
      const g = new THREE.BoxGeometry(p * 0.72, hgt, p * 0.72); g.rotateY(Math.PI / 4); g.translate(xm, bed + hgt / 2, sd * W / 2); add(mat, place(g));
    }
  }
  // parapets; medieval Grazie had small houses / chapels on the piers (demolished 1876)
  for (const sd of [-1, 1]) box(mat, 0, L, deck, deck + 1.05, sd * W / 2 - 0.45, sd * W / 2);
  if (spec.houses) for (let k = 1; k < n; k++) {
    const xm = L - abut - k * s - (k - 0.5) * p;
    for (const sd of [-1, 1]) { box('plaster', xm - 2.2, xm + 2.2, deck, deck + 4.2, sd * (W / 2 + 1.6) - 1.6, sd * (W / 2 + 1.6) + 1.6);
      box('roof', xm - 2.4, xm + 2.4, deck + 4.2, deck + 4.6, sd * (W / 2 + 1.6) - 1.8, sd * (W / 2 + 1.6) + 1.8); }
  }
  return out;
}

export function mergeBridge(parts: Record<string, THREE.BufferGeometry[]>, mats: Record<string, THREE.Material>) {
  const grp = new THREE.Group();
  for (const [m, gs] of Object.entries(parts)) {
    const g = mergeGeometries(gs.map(x => x.index ? x.toNonIndexed() : x), false); g.computeVertexNormals();
    const mesh = new THREE.Mesh(g, mats[m]); mesh.castShadow = mesh.receiveShadow = true; grp.add(mesh);
  }
  return grp;
}
