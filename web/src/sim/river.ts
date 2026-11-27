// Life on the Arno: cargo boats, renaioli (sand diggers), fishermen, ferries where no bridge stood, landing stages,
// ducks, herons, swallows; deer in the countryside before the city spread; Iron Age huts near the ford.
// Every activity has a date range and a source (docs/HISTORY.md, river section). Boats and animals show in every
// mode, and so do their crews and the pre-urban villagers (own small crowd, never reset by the event scenes).
import * as THREE from 'three/webgpu';
import type { Props } from '../scene/assets';
import { outfitFor, type People, type Pose } from './people';
import { walk } from './walk';

type Height = (x: number, z: number) => number;
type Axis = number[][];                     // [x, level, z centre, z north bank, z south bank], every 20 m, flow -> -x
const R = Math.random;

/** Date ranges (inclusive start, exclusive end) and the reaches where things happen. */
type Step = { dur?: number; poses?: Pose[]; every?: number; face?: THREE.Vector3; go?: THREE.Vector3; carry?: boolean };
export const RIVER_LIFE = {
  // weirs: San Niccolò (east) and Santa Rosa / Ognissanti (west), x from weirs.json
  navicelliCity: [-30, 1300],     // up to the old port between Carraia and San Niccolò "until the 13th century" (Comune 2019, meer.com)
  navicelliPort: [1300, 1880],    // afterwards they berth below the Santa Rosa weir (porto di Ognissanti / Pignone) – end date conjectural
  renaioli: [1700, 1960],         // sand diggers between the two weirs; documented 1829–1847, active until the mid-20th century
  fishingBoatsInCity: [-800, 1586], // boat fishing between the weirs banned from 1586 (Comune 2019)
  landings: [                     // scali (Comune 2019)
    { name: 'Porticciola (Piazza d’Arno / delle Travi)', from: 1830, between: ['carraia', 'trinita'], bank: 'N' },
    { name: 'Scalo dei Renai', from: 1830, between: ['carraia', 'trinita'], bank: 'S' },
    { name: 'Scalo alla gora dei mulini dei Renai', from: 1846, between: ['grazie', 'niccol'], bank: 'S' },
  ],
  ferries: [] as { site: string; from: number; to: number }[],   // removed 2026-11-23: no source places ferry barges in the
                                  // city reaches while a bridge was down; temporary wooden bridges (e.g. the 1944–46 Bailey
                                  // bridges) will be added only from documents – see docs/RIVER-LANDSCAPE.md
  ford: [-1000, -30],             // before the Roman bridge the Arno was forded near today's Ponte Vecchio (crossing of the
                                  // Bologna–Fiesole–Impruneta route: tuttatoscana.net, Caselli) – inferred
  canoes: [-1000, -30],           // dugouts carrying goods on the Arno (florencecity.it: goods moved by river) – inferred
  deer: [-900, 1200],
  // moorings (2026-11-28): the city port between Carraia and San Niccolò "until the 13th century" (meer.com) – spot on the
  // north bank inferred; then the port of the Pignone, used for goods to and from Pisa until the early 20th century
  // (meer.com; Comune 2019), rebuilt as the Leopoldine port found under Piazza Paolo Uccello (gonews 2021) – x from OSM
  cityPort: { years: [-30, 1300], between: ['vecchio', 'grazie'], bank: 'N' as 'N' | 'S' },
  pignone: { years: [1300, 1910], x: -1750, bank: 'S' as 'N' | 'S' },
  // washerwomen at the river's edge, upstream of San Niccolò and below Santa Rosa – common practice before piped water
  // and the public lavatoi (inferred, no Florentine source yet for the spots)
  washing: [1000, 1900],
  waders: [-1000, 1900],          // fishing knee-deep in the shallows: not in modern times
  // fornaciai: clay dug from the banks below the city for the brick kilns (river crafts listed by Agostini 2012) – spots inferred
  clay: [1300, 1900],
};

/** Villanovan and Etruscan Florence: sites from finds (docs/HISTORY.md "Before Florentia"). x/z in scene metres. */
export const ANCIENT_SITES = [
  { id: 'orsanmichele', name: 'Villanovan village (Orsanmichele)', x: -27, z: 109, from: -1000, to: -60, huts: 13, stilts: true, kilns: 2, pen: true,
    src: 'florencecity.it – first settlement under Orsanmichele, huts on stilts of wood, straw and mud (inferred layout)' },
  { id: 'badia', name: 'Orientalizing hut (Badia – Bargello)', x: 184, z: 151, from: -720, to: -60, huts: 3, stilts: true, kilns: 0, pen: false,
    src: 'tuttatoscana.net – hut floor with Orientalizing pottery between Badia Fiorentina and Bargello' },
  { id: 'sgiorgio', name: 'Settlement on Costa San Giorgio', x: -10, z: 712, from: -1000, to: -60, huts: 5, stilts: false, kilns: 1, pen: true,
    src: 'visittuscany.com – Villanovan settlement especially around Costa San Giorgio (inferred layout)' },
];
export const NECROPOLES = [
  { name: 'Villanovan necropolis (via Strozzi – via Porta Rossa)', x: -253, z: 96, from: -1000, to: -60, kind: 'urn_grave', n: 16,
    src: 'florencecity.it – cremation urns ~7 m below via Pellicceria, Porta Rossa, Campidoglio, Strozzi (19th-c. finds)' },
  { name: 'Archaic stelae (Piazza della Libertà)', x: 306, z: -1575, from: -600, to: -60, kind: 'stele', n: 4,
    src: 'tuttatoscana.net – archaic Etruscan stelae and Villanovan urns found under Piazza della Libertà (1865–71)' },
];

/** Height of the drawn Arno surface (reaches step down at the weirs), rasterised once from the water mesh on a 4 m grid. */
function waterGrid(geo: THREE.BufferGeometry | undefined) {
  if (!geo) return null;
  const P = geo.getAttribute('position') as THREE.BufferAttribute, I = geo.getIndex(); if (!I) return null;
  let x0 = Infinity, x1 = -Infinity, z0 = Infinity, z1 = -Infinity;
  for (let i = 0; i < P.count; i++) { const x = P.getX(i), z = P.getZ(i); x0 = Math.min(x0, x); x1 = Math.max(x1, x); z0 = Math.min(z0, z); z1 = Math.max(z1, z); }
  const C = 4, W = Math.ceil((x1 - x0) / C) + 1, H = Math.ceil((z1 - z0) / C) + 1, g = new Float32Array(W * H).fill(NaN);
  for (let t = 0; t < I.count; t += 3) {
    const a = I.getX(t), b = I.getX(t + 1), c = I.getX(t + 2);
    const ax = P.getX(a), az = P.getZ(a), bx = P.getX(b), bz = P.getZ(b), cx = P.getX(c), cz = P.getZ(c);
    const d = (bz - cz) * (ax - cx) + (cx - bx) * (az - cz); if (Math.abs(d) < 1e-9) continue;
    for (let gz = Math.floor((Math.min(az, bz, cz) - z0) / C); gz <= Math.ceil((Math.max(az, bz, cz) - z0) / C); gz++)
      for (let gx = Math.floor((Math.min(ax, bx, cx) - x0) / C); gx <= Math.ceil((Math.max(ax, bx, cx) - x0) / C); gx++) {
        const x = x0 + gx * C, z = z0 + gz * C;
        const l1 = ((bz - cz) * (x - cx) + (cx - bx) * (z - cz)) / d, l2 = ((cz - az) * (x - cx) + (ax - cx) * (z - cz)) / d, l3 = 1 - l1 - l2;
        if (l1 < -0.02 || l2 < -0.02 || l3 < -0.02 || gx < 0 || gz < 0 || gx >= W || gz >= H) continue;
        g[gz * W + gx] = l1 * P.getY(a) + l2 * P.getY(b) + l3 * P.getY(c);
      }
  }
  return (x: number, z: number) => { const gx = Math.round((x - x0) / C), gz = Math.round((z - z0) / C);
    return gx < 0 || gz < 0 || gx >= W || gz >= H ? NaN : g[gz * W + gx]; };
}

export function createRiver(scene: THREE.Scene, props: Props, people: People, height: Height, axis: Axis, bridges: { name: string; x: number }[], weirs: any[],
  waterGeo?: THREE.BufferGeometry, streetNodes: number[][] = []) {
  const group = new THREE.Group(); group.name = 'river-life'; scene.add(group);
  // Can somebody get here? A spot on the bank is reachable if a street lies within 30 m at about its level (not 6 m up a
  // lungarno wall), or if no street is near at all (the open fields and gravel banks outside the town).
  const cells = new Map<string, number[][]>();
  for (const n of streetNodes) { const k = `${Math.floor(n[0] / 20)},${Math.floor(n[2] / 20)}`; (cells.get(k) ?? cells.set(k, []).get(k)!).push(n); }
  function reachable(x: number, z: number, y = height(x, z)) {
    let near = false;
    for (let i = -3; i <= 3; i++) for (let j = -3; j <= 3; j++) for (const n of cells.get(`${Math.floor(x / 20) + i},${Math.floor(z / 20) + j}`) ?? []) {
      const d = Math.hypot(n[0] - x, n[2] - z);
      if (d < 60) near = true;
      if (d < 30 && Math.abs(n[1] - y) < 2.2) return true;
    }
    return !near;
  }
  /** Rest a prop on the ground: at the ground's height under it, tilted with the slope (nothing hangs in the air or sinks). */
  const _up = new THREE.Vector3(0, 1, 0), _n = new THREE.Vector3(), _q = new THREE.Quaternion();
  function settle(o: THREE.Object3D, sink = 0.04, r = 0.7) {
    const x = o.position.x, z = o.position.z, ry = o.rotation.y;
    const hx = (height(x + r, z) - height(x - r, z)) / (2 * r), hz = (height(x, z + r) - height(x, z - r)) / (2 * r);
    o.position.y = Math.min(height(x, z), height(x + r, z), height(x - r, z), height(x, z + r), height(x, z - r)) * 0.5 + height(x, z) * 0.5 - sink;
    _n.set(-hx, 1, -hz).normalize(); _q.setFromUnitVectors(_up, _n); o.quaternion.copy(_q); o.rotateY(ry);
  }
  const surface = waterGrid(waterGeo);
  const ax = axis.slice().sort((a, b) => a[0] - b[0]);
  const at = (x: number) => {               // interpolate the river axis at x
    let i = ax.findIndex(p => p[0] >= x); if (i <= 0) i = 1; if (i < 0) i = ax.length - 1;
    const a = ax[i - 1], b = ax[i], t = Math.min(1, Math.max(0, (x - a[0]) / ((b[0] - a[0]) || 1)));
    return a.map((v, k) => v + (b[k] - v) * t);
  };
  const xMin = ax[0][0], xMax = ax[ax.length - 1][0];
  const bx: Record<string, number> = {};
  for (const b of bridges) {
    const key = ['vecchio', 'trinita', 'carraia', 'grazie', 'vespucci', 'niccol'].find(k => b.name.toLowerCase().includes(k));
    if (key && !(key in bx)) bx[key] = b.x;
  }
  const wx = weirs.map((w: any) => ({ x: w.pts.reduce((s: number, p: number[]) => s + p[0], 0) / w.pts.length, name: w.name as string, start: w.start }));
  const rosa = wx.find(w => /rosa|ognissanti/i.test(w.name))?.x ?? -850, niccolo = wx.find(w => /niccol/i.test(w.name))?.x ?? 990;
  const inRange = (y: number, r: number[]) => y >= r[0] && y < r[1];

  // ---------- moving things ----------
  interface Mover { obj: THREE.Object3D; x: number; dir: number; speed: number; x0: number; x1: number; lane: number; crew: any[]; bob: number; kind: string; draft?: number; floor?: number }   // draft: how deep the hull sits, floor: floorboards above the keel (m)
  let movers: Mover[] = [], statics: THREE.Object3D[] = [], crew: any[] = [];
  let ducks: { obj: THREE.Object3D; x: number; lane: number; v: number }[] = [];
  let birds: THREE.InstancedMesh | null = null; const birdState: { c: THREE.Vector3; r: number; a: number; s: number; h: number }[] = [];
  let key = '', small: THREE.Object3D[] = [], viewK = '';
  let stoneMat: THREE.Material | undefined;

  function waterPos(x: number, lane: number) {       // lane -1 north bank .. 0 centre .. 1 south bank
    const p = at(x); const z = lane < 0 ? p[2] + (p[3] - p[2]) * -lane : p[2] + (p[4] - p[2]) * lane;
    const y = surface?.(x, z);                          // the drawn surface, not the interpolated axis (reaches step at the weirs)
    return new THREE.Vector3(x, y !== undefined && !Number.isNaN(y) ? y : p[1], z);
  }
  const FLOOR_SMALL = 0.15;                            // a barchetto floats 0.1 m deep; its floorboards (0.18 m up the side) clear the water
  function placeOnWater(name: string, x: number, lane: number, rot = 0) {
    const p = waterPos(x, lane); const o = props.place(name, p.x, p.y - 0.03, p.z, rot, group); if (o) statics.push(o); return o;   // small boats draw only a few cm, the sides well out
  }
  function onBank(x: number, north: boolean, out = 4) {
    const p = at(x), z = north ? p[3] - out : p[4] + out; return new THREE.Vector3(x, height(x, z), z);
  }

  /** The drawn water's edge at x: walk out from mid-river until the surface ends; `land` metres onto the bank. */
  function edge(x: number, north: boolean, land = 0.4) {
    const p = at(x), zb = north ? p[3] : p[4], dir = Math.sign(zb - p[2]) || 1;
    const wet = (z: number) => { const y = surface?.(x, z); return y !== undefined && !Number.isNaN(y) && y > height(x, z) + 0.02; };   // visible water, not the mesh under the bank
    let z = p[2];
    if (surface) {
      if (!wet(z)) for (let d = 1; d < 80; d++) { if (wet(p[2] - dir * d)) { z = p[2] - dir * d; break; } if (wet(p[2] + dir * d)) { z = p[2] + dir * d; break; } }   // the axis is off the drawn water here
      for (let k = 0; k < 160 && wet(z + dir * 0.5); k++) z += dir * 0.5;
    } else z = zb;
    const zl = z + dir * land;
    return { land: new THREE.Vector3(x, height(x, zl), zl), water: new THREE.Vector3(x, surface?.(x, z - dir * 0.6) ?? p[1], z - dir * 0.6), dir };
  }
  function clear() {
    for (const o of [...statics, ...movers.filter(m => m.kind !== 'wade').map(m => m.obj), ...ducks.map(d => d.obj), ...grazers.map(g => g.obj)]) group.remove(o);
    statics = []; movers = []; ducks = []; workers.length = 0; grazers = []; smoke.length = 0; ancientObjs = []; small = []; viewK = '';
    for (const c of crew) people.release(c); crew = [];
  }

  function rebuild(year: number, live: boolean) {
    clear();
    // cargo boats (navicelli): up to the city before the weirs, then only to the port below Santa Rosa
    const nav = inRange(year, RIVER_LIFE.navicelliCity) ? [xMin + 200, (bx.vecchio ?? 0) + 150] : inRange(year, RIVER_LIFE.navicelliPort) ? [xMin + 200, rosa - 80] : null;
    if (nav) for (let i = 0; i < 5; i++) {
      const o = props.place('navicello', 0, 0, 0, 0, group); if (!o) break;
      const m: Mover = { obj: o, x: nav[0] + R() * (nav[1] - nav[0]), dir: R() < 0.5 ? 1 : -1, speed: 0.9 + R() * 0.6, x0: nav[0], x1: nav[1], lane: (R() - 0.5) * 0.6, crew: [], bob: R() * 6, kind: 'nav', draft: 0.2, floor: 0.36 };
      if (live) for (let k = 0; k < 2; k++) { const a = people.claim(new THREE.Vector3(), new THREE.Vector3(1, 0, 0), 'static', k ? 'idle' : 'agree', undefined, 'boatman'); if (a) { m.crew.push(a); crew.push(a); } }
      movers.push(m);
    }
    // renaioli between the weirs: boats on the shoals near the banks + sand heaps on the renai
    if (inRange(year, RIVER_LIFE.renaioli)) for (let i = 0; i < 6; i++) {
      const x = rosa + 120 + (niccolo - rosa - 240) * (i + R() * 0.6) / 6, north = i % 2 === 0;
      const b = placeOnWater('barchetto', x, north ? -0.62 : 0.62, R() * 0.4 - 0.2);
      const h = onBank(x + 8, north, 3); const s = props.place('sandheap', h.x, h.y - 0.3, h.z, R() * 3, group); if (s) statics.push(s);
      if (live && b) for (let k = 0; k < 2; k++) {
        const p = waterPos(x - 1.5 + k * 2.4, north ? -0.62 : 0.62);
        const a = people.claim(p.clone(), new THREE.Vector3(x, 0, at(x)[2]), 'static', 'agree', undefined, 'boatman', true); if (a) { a.obj.position.copy(p).setY(p.y + FLOOR_SMALL); crew.push(a); }   // on the floorboards
      }
    }
    // fishermen: on the banks in every era – most sit on a stone with a rod, some stand; a few wade into the shallows;
    // boats between the weirs only until 1586, always outside them
    if (live) for (let i = 0; i < 9; i++) {
      let x = 0, north = false, p = new THREE.Vector3(), ok = false;
      for (let t = 0; t < 6 && !ok; t++) { x = (bx.carraia ?? -400) - 600 + R() * 1900; north = R() < 0.5; p = onBank(x, north, 1.2); ok = reachable(p.x, p.z, p.y); }
      if (!ok) continue;
      const w = waterPos(x, north ? -1 : 1);
      const seated = i % 3 !== 2;
      const a = people.claim(p.clone(), waterPos(x, 0), 'static', 'idle', undefined, 'fisher'); if (!a) continue;
      crew.push(a);
      if (seated) {                                     // on a stone ~0.42 m high: hips at the stone top, feet on the ground
        a.obj.position.y = p.y - 0.6; people.setPose(a, 'sitrod', w.y);
        stoneMat ??= new THREE.MeshStandardNodeMaterial({ color: 0xa39d90, roughness: 0.95, flatShading: true });
        const st = new THREE.Mesh(new THREE.IcosahedronGeometry(0.34, 1), stoneMat); st.scale.set(1, 0.62, 0.85); st.position.set(a.obj.position.x, p.y + 0.15, a.obj.position.z);
        st.rotation.y = a.obj.rotation.y; st.translateZ(-0.12); st.castShadow = true; group.add(st); statics.push(st);
      } else people.setPose(a, 'rod', w.y);
    }
    if (live && inRange(year, RIVER_LIFE.waders)) for (let i = 0; i < 2; i++) {   // wading knee-deep near the bank, rod out over the current
      const x = (bx.carraia ?? -400) - 300 + R() * 1400, north = R() < 0.5, p = waterPos(x, north ? -0.88 : 0.88);
      const a = people.claim(p.clone().setY(p.y - 0.45), waterPos(x, 0), 'static', 'idle', undefined, 'fisher'); if (!a) continue;
      a.obj.position.y = p.y - 0.45; people.setPose(a, 'rod', p.y); crew.push(a);
    }
    for (let i = 0; i < 3; i++) {   // fishing boats: in the city reach only before the 1586 ban, otherwise up- or downstream
      const inside = inRange(year, RIVER_LIFE.fishingBoatsInCity) && R() < 0.6;
      const x = inside ? rosa + 200 + R() * (niccolo - rosa - 400) : (R() < 0.5 ? rosa - 300 - R() * 1500 : niccolo + 200 + R() * 1200);
      const lane = (R() - 0.5) * 0.8, b = placeOnWater('barchetto', x, lane, R() * 6); if (b) b.children.forEach(c => { if (/sand/.test(c.name)) c.visible = false; });
      if (live && b) { const p = waterPos(x, lane); const a = people.claim(p.clone(), p.clone().add(new THREE.Vector3(0, 0, 5)), 'static', 'idle', undefined, 'fisher', true);
        if (a) { a.obj.position.set(b.position.x, p.y + FLOOR_SMALL, b.position.z); people.setPose(a, 'rod', p.y); crew.push(a); } }   // standing on the floorboards
    }
    // ferries where a bridge was down
    for (const f of RIVER_LIFE.ferries) if (inRange(year, [f.from, f.to]) && bx[f.site] !== undefined) {
      const o = props.place('scafa', 0, 0, 0, 0, group); if (!o) continue;
      const m: Mover = { obj: o, x: bx[f.site] + 12, dir: 1, speed: 0.6, x0: -0.75, x1: 0.75, lane: 0, crew: [], bob: 0, kind: 'ferry' };
      // the scafa ran along a rope stretched between the banks (passo di barca)
      const a = waterPos(m.x, -1.02), b = waterPos(m.x, 1.02); a.y += 1.6; b.y += 1.6;
      const rope = new THREE.Line(new THREE.BufferGeometry().setFromPoints([a, b]), new THREE.LineBasicNodeMaterial({ color: 0x3a2e22 }));
      group.add(rope); statics.push(rope);
      for (const q of [a, b]) { const post = props.place('palisade', q.x, q.y - 2.2, q.z, 0, group); if (post) { post.scale.set(0.05, 1.4, 1); statics.push(post); } }
      if (live) { const a = people.claim(new THREE.Vector3(), new THREE.Vector3(), 'static', 'agree', undefined, 'boatman'); if (a) { m.crew.push(a); crew.push(a); } }
      movers.push(m);
    }
    // landing stages, each with boats tied up alongside
    const moor = (x: number, north: boolean, boat: string, n: number, crewN: number) => {
      const p = waterPos(x, north ? -0.92 : 0.92);
      const o = props.place('scalo', p.x, p.y - 0.4, p.z, north ? Math.PI : 0, group); if (o) statics.push(o);
      const big = boat === 'navicello', lane = north ? (big ? -0.74 : -0.8) : (big ? 0.74 : 0.8);
      for (let k = 0; k < n; k++) {
        const bxk = x + (k - (n - 1) / 2) * (big ? 15 : 7.5), q = waterPos(bxk, lane);
        const b = props.place(boat, q.x, q.y - (big ? 0.2 : 0.03), q.z, 0, group); if (!b) continue; statics.push(b);
        const ah = waterPos(bxk + 5, lane); b.rotation.y = Math.atan2(-(ah.z - q.z), ah.x - q.x);
        if (big) b.children.forEach(c => { if (/sail/.test(c.name)) c.visible = false; });           // sail furled at the mooring
        else b.children.forEach(c => { if (/sand/.test(c.name)) c.visible = R() < 0.5; });
        if (live && k < crewN) {                        // unloading: one aboard, one on the landing
          const fl = q.clone().setY(q.y - (big ? 0.2 : 0.03) + (big ? 0.36 : 0.18));
          const a = people.claim(fl, p, 'static', 'agree', undefined, 'boatman', true); if (a) { a.obj.position.copy(fl); crew.push(a); }
          const d = p.clone().setY(p.y + 0.15).add(new THREE.Vector3((k - 0.5) * 2, 0, 0));
          const c2 = people.claim(d, q, 'static', R() < 0.5 ? 'idle' : 'agree', undefined, 'boatman', true); if (c2) { c2.obj.position.copy(d); crew.push(c2); }
        }
      }
    };
    for (const l of RIVER_LIFE.landings) if (year >= l.from && bx[l.between[0]] !== undefined && bx[l.between[1]] !== undefined)
      moor((bx[l.between[0]] + bx[l.between[1]]) / 2, l.bank === 'N', 'barchetto', 2, 1);
    { const cp = RIVER_LIFE.cityPort, pg = RIVER_LIFE.pignone;
      if (inRange(year, cp.years) && bx[cp.between[0]] !== undefined && bx[cp.between[1]] !== undefined) moor((bx[cp.between[0]] + bx[cp.between[1]]) / 2, cp.bank === 'N', 'navicello', 3, 2);
      if (inRange(year, pg.years) && pg.x > xMin + 30) { moor(pg.x, pg.bank === 'N', 'navicello', 3, 2); moor(pg.x + 60, pg.bank === 'N', 'navicello', 2, 1); } }
    // washerwomen kneeling at the water's edge, linen spread on the bank to dry
    // a stretch of open bank: slide along the river until no building of that year stands there (mills, the walls)
    const openBank = (x0: number, north: boolean, span: number, out: number) => {
      for (let k = 0; k < 12; k++) {
        const x = x0 + (k % 2 ? 1 : -1) * Math.ceil(k / 2) * 18;
        let ok = true; for (let d = -span / 2; d <= span / 2 && ok; d += 1.5) { const e = edge(x + d, north, out); if (walk.blocked(e.land.x, e.land.z, 0.6, false)) ok = false; }
        if (ok) { const e = edge(x, north, out); ok = reachable(e.land.x, e.land.z, e.land.y); }
        if (ok) return x;
      }
      return null;
    };
    if (inRange(year, RIVER_LIFE.washing)) for (const [x0, north] of [[((bx.grazie ?? 500) + niccolo) / 2, false], [niccolo + 220, true], [rosa - 150, true], [rosa - 330, false]] as [number, boolean][]) {
      const x = openBank(x0, north, 9, 0.55); if (x === null) continue;
      const e0 = edge(x, north, 0.2);
      // the slab slopes into the water (its front, +Z, towards the river); basket and spread linen behind on the bank
      const l = props.place('laundry', e0.land.x, Math.max(e0.land.y, e0.water.y) - 0.05, e0.land.z, e0.dir > 0 ? Math.PI : 0, group); if (l) { settle(l, 0.03, 0.9); l.position.y = Math.max(l.position.y, e0.water.y - 0.05); statics.push(l); }
      if (live) for (let k = 0; k < 3 + (R() * 3 | 0); k++) {
        const e = edge(x + (k - 2) * 1.5, north, 0.55), p = e.land;
        const knees = height(p.x, p.z + e.dir * 0.25), feet = height(p.x, p.z - e.dir * 0.35);         // kneeling across the slope: knees and toes on the ground
        const y = Math.max(Math.min(knees, feet) + 0.02, e.water.y + 0.05);
        const a = people.claim(p, e.water, 'static', k % 2 ? 'agree' : 'idle', undefined, outfitFor(year, true), true); if (!a) break;
        a.obj.position.set(p.x, y - 0.42, p.z); a.obj.lookAt(e.water.x, y - 0.42, e.water.z); people.setPose(a, 'kneel'); crew.push(a);
        // a round of three tasks, each woman at her own point in it: scrubbing on the slab, wringing, beating the linen
        workers.push({ ag: a, t: R() * 20, steps: [
          { dur: 7, poses: ['kneel', 'kneel2'], every: 0.7 }, { dur: 3.5, poses: ['wring'] }, { dur: 4.5, poses: ['beat', 'kneel'], every: 0.55 }] });
      }
    }
    // fornaciai digging clay from the bank below the city, bricks drying in rows
    if (inRange(year, RIVER_LIFE.clay)) for (const [x0, north] of [[rosa - 520, false], [rosa - 760, true]] as [number, boolean][]) {
      const x = openBank(x0, north, 16, 8); if (x === null) continue;
      const h = onBank(x, north, 6), b = onBank(x + 7, north, 9);
      const c = props.place('clayheap', h.x, h.y - 0.2, h.z, R() * 3, group); if (c) { settle(c, 0.15, 1.2); statics.push(c); }
      const k = props.place('bricks', b.x, b.y, b.z, north ? 0 : Math.PI, group); if (k) { settle(k, 0.02, 1.0); statics.push(k); }
      // the moulding table between the heap and the rows
      const tb = onBank(x + 3.5, north, 7.4);
      const tbl = props.place('table', tb.x, tb.y, tb.z, north ? 0 : Math.PI, group); if (tbl) { settle(tbl, 0.0, 1.0); statics.push(tbl); }
      if (live) {
        // three men, each with a round of his own, looped: the digger cuts clay at the face of the bank and takes it to the
        // heap; the moulder fetches clay from the heap and works it at the table; the carrier takes the moulded bricks from
        // the table to the drying rows (presets, the order of the work as on a brickfield – *inferred* for the Arno banks)
        const D = onBank(x - 2, north, 2.6), H = onBank(x + 1.0, north, 4.6), T = onBank(x + 3.5, north, 6.4), B = onBank(x + 7, north, 7.6);
        const plans: { at: THREE.Vector3; steps: Step[] }[] = [
          { at: D, steps: [{ dur: 6, poses: ['dig', 'lift'], every: 0.8, face: h }, { go: H, carry: true }, { dur: 1.6, poses: ['dig'] }, { go: D }] },
          { at: T, steps: [{ dur: 7, poses: ['knead', 'knead2'], every: 0.65, face: tb }, { go: H }, { dur: 1.8, poses: ['dig'] }, { go: T, carry: true }] },
          { at: T, steps: [{ dur: 2, poses: ['dig'], face: tb }, { go: B, carry: true }, { dur: 2.2, poses: ['dig', 'lift'], every: 1.1 }, { go: T }] },
        ];
        plans.forEach((pl, i) => {
          const p = i === 2 ? onBank(x + 4.6, north, 6.6) : pl.at;
          const a = people.claim(p, h, 'runner', 'idle', undefined, 'boatman', true);
          if (!a) return;
          a.obj.position.set(p.x, height(p.x, p.z), p.z); crew.push(a);
          workers.push({ ag: a, t: 0, steps: pl.steps, k: 0, st: i * 2.5 });
        });
      }
    }
    // ducks and herons (all periods)
    for (let g = 0; g < 9; g++) {
      const x0 = xMin + 400 + R() * (xMax - xMin - 800), lane = (R() - 0.5) * 1.4;
      for (let k = 0; k < 3 + (R() * 4 | 0); k++) {
        const o = props.place('duck', 0, 0, 0, R() * 6, group); if (!o) break; o.scale.setScalar(1.6);
        ducks.push({ obj: o, x: x0 + (R() - 0.5) * 8, lane: lane + (R() - 0.5) * 0.1, v: -0.15 - R() * 0.2 });
      }
    }
    for (let i = 0; i < 10; i++) {
      const x = xMin + 300 + R() * (xMax - xMin - 600), north = R() < 0.5, p = waterPos(x, north ? -0.97 : 0.97);
      const o = props.place('heron', p.x, p.y - 0.25, p.z, R() * 6, group); if (o) { o.scale.setScalar(1.4); statics.push(o); small.push(o); }
    }
    // deer in the countryside before the city spread
    if (inRange(year, RIVER_LIFE.deer)) for (let i = 0; i < 14; i++) {
      const a = R() * Math.PI * 2, r = 1400 + R() * 3600, x = Math.cos(a) * r, z = Math.sin(a) * r - 1500 * (R() < 0.6 ? 1 : 0);
      if (Math.abs(z - at(x)[2]) < 120) continue;
      for (let k = 0; k < 3; k++) { const o = props.place('deer', x + k * 3, height(x + k * 3, z + k), z + k, R() * 6, group); if (o) statics.push(o); }
    }
    // Villanovan / Etruscan plain: villages, kilns, hearths, livestock, graves, dugouts, the ford
    if (year < -30) { ancient(year, live); paint(); }
    // swallows over the water (spring–summer), one flock above the city reach
    if (!birds) {
      const src = props.lib['bird']?.children[0] as THREE.Mesh | undefined;
      if (src) {
        birds = new THREE.InstancedMesh(src.geometry, src.material as THREE.Material, 60); group.add(birds);
        for (let i = 0; i < 60; i++) birdState.push({ c: new THREE.Vector3((R() - 0.5) * 900, 0, 0), r: 20 + R() * 60, a: R() * 6.28, s: (R() < 0.5 ? 1 : -1) * (0.5 + R() * 0.7), h: 8 + R() * 25 });
      }
    }
  }

  // ---------- before Florentia ----------
  const smoke: { obj: THREE.Mesh; base: THREE.Vector3; t: number }[] = [];
  let smokeMat: THREE.Material | null = null;
  function puffs(x: number, y: number, z: number) {
    smokeMat ??= new THREE.MeshBasicNodeMaterial({ color: 0x9a948c, transparent: true, opacity: 0.22, depthWrite: false });
    const g = new THREE.SphereGeometry(0.7, 8, 6);
    for (let i = 0; i < 6; i++) { const m = new THREE.Mesh(g, smokeMat); group.add(m); smoke.push({ obj: m, base: new THREE.Vector3(x, y, z), t: i / 6 }); statics.push(m); }
  }
  const WHAT: Record<string, string> = {
    hut: 'Oval hut of wattle, daub and thatch', hut_stilt: 'Oval hut on a raised platform (marshy plain, floods)', kiln: 'Pottery kiln (updraft, clay dome)',
    hearth: 'Open hearth', palisade: 'Livestock pen', sheep: 'Sheep', pig: 'Pig', cow: 'Cattle', canoe: 'Dugout canoe with jars of goods',
    urn_grave: 'Cremation pit grave with biconical urn', stele: 'Archaic stele (Fiesolan type, horseshoe top)',
  };
  let curSite: { name: string; src: string; from: number; to: number } | null = null;
  function placeA(name: string, x: number, y: number, z: number, rot: number, parent: THREE.Object3D) {
    const o = props.place(name, x, y, z, rot, parent);
    if (o) {
      o.userData.src = 'A07'; ancientObjs.push(o);
      const s = curSite ?? { name: 'Arno valley, Iron Age', src: 'A07 – florencecity.it: goods moved by river, livestock and farming (inferred)', from: -1000, to: -30 };
      o.userData.site = { ...s, kind: WHAT[name] ?? name };
    }
    return o;
  }
  function ancient(year: number, live: boolean) {
    const hutName = (st: boolean) => st ? 'hut_stilt' : 'hut';
    for (const s of ANCIENT_SITES) if (inRange(year, [s.from, s.to])) {
      curSite = { name: s.name, src: s.src, from: s.from, to: s.to };
      const ring: THREE.Vector3[] = [];
      for (let i = 0; i < s.huts; i++) {                       // oval cluster, entrances towards the centre
        const a = i * 2.39996, r = 10 + Math.sqrt(i + 1) * 11, x = s.x + Math.cos(a) * r, z = s.z + Math.sin(a) * r * 0.8;
        const o = placeA(hutName(s.stilts), x, height(x, z), z, Math.atan2(s.x - x, s.z - z) + Math.PI, group); if (o) statics.push(o);
        ring.push(new THREE.Vector3(x, height(x, z), z));
        if (i % 3 === 0) { const hx = x + (s.x - x) * 0.25, hz = z + (s.z - z) * 0.25, h = placeA('hearth', hx, height(hx, hz), hz, 0, group);
          if (h) { statics.push(h); puffs(hx, height(hx, hz) + 0.6, hz); }
          if (live) { const p = new THREE.Vector3(hx + 1.4, height(hx + 1.4, hz), hz); const ag = people.claim(p, new THREE.Vector3(hx, p.y, hz), 'static', i % 2 ? 'idle' : 'agree'); if (ag) crew.push(ag); } }
      }
      for (let k = 0; k < s.kilns; k++) {                      // potters' kilns at the edge of the village
        const a = 0.8 + k * 2.6, x = s.x + Math.cos(a) * 62, z = s.z + Math.sin(a) * 48, y = height(x, z);
        const o = placeA('kiln', x, y, z, a, group); if (o) { statics.push(o); puffs(x, y + 2, z); }
        if (live) { const ag = people.claim(new THREE.Vector3(x + 2.5, y, z + 1), new THREE.Vector3(x, y, z), 'static', 'agree'); if (ag) crew.push(ag); }
      }
      if (s.pen) {                                             // livestock pen: palisade ring, sheep, pigs, cattle
        const px = s.x + 75, pz = s.z - 30;
        for (let i = 0; i < 8; i++) { const a = i / 8 * Math.PI * 2, x = px + Math.cos(a) * 16, z = pz + Math.sin(a) * 12;
          const o = placeA('palisade', x, height(x, z), z, -a + Math.PI / 2, group); if (o) { o.scale.set(1, 0.6, 1); statics.push(o); } }
        const herd: [string, number][] = [['sheep', 14], ['pig', 6], ['cow', 3]];
        for (const [n, c] of herd) for (let i = 0; i < c; i++) {
          const x = px + (R() - 0.5) * 22, z = pz + (R() - 0.5) * 16, o = placeA(n, x, height(x, z), z, R() * 6, group);
          if (o) grazers.push({ obj: o, x, z, a: R() * 6, cx: px, cz: pz, r: 9 });
        }
      }
      // flocks out on the fields with a shepherd, cattle at the plough
      const fx = s.x - 160, fz = s.z - 120;
      for (let i = 0; i < 20; i++) { const x = fx + (R() - 0.5) * 50, z = fz + (R() - 0.5) * 40, o = placeA('sheep', x, height(x, z), z, R() * 6, group);
        if (o) grazers.push({ obj: o, x, z, a: R() * 6, cx: fx, cz: fz, r: 30 }); }
      if (live) { const ag = people.claim(new THREE.Vector3(fx + 8, height(fx + 8, fz), fz), new THREE.Vector3(fx, 0, fz), 'static', 'idle'); if (ag) crew.push(ag); }
    }
    curSite = null;
    for (const n of NECROPOLES) if (inRange(year, [n.from, n.to])) for (let i = 0; i < n.n; i++) {
      curSite = { name: n.name, src: n.src, from: n.from, to: n.to };
      const x = n.x + (i % 4) * 5 + (R() - 0.5) * 2, z = n.z + Math.floor(i / 4) * 5 + (R() - 0.5) * 2;
      const o = placeA(n.kind, x, height(x, z), z, R() * 0.4 - 0.2 + (n.kind === 'stele' ? Math.PI : 0), group); if (o) statics.push(o);
    }
    curSite = null;
    // dugouts with jars of goods going up and down the river
    if (inRange(year, RIVER_LIFE.canoes)) for (let i = 0; i < 5; i++) {
      const o = placeA('canoe', 0, 0, 0, 0, group); if (!o) break;
      const m: Mover = { obj: o, x: xMin + 300 + R() * (xMax - xMin - 600), dir: R() < 0.5 ? 1 : -1, speed: 0.7 + R() * 0.5, x0: xMin + 200, x1: xMax - 200, lane: (R() - 0.5) * 0.8, crew: [], bob: R() * 6, kind: 'nav', draft: 0.1 };
      if (live) { const ag = people.claim(new THREE.Vector3(), new THREE.Vector3(1, 0, 0), 'static', 'agree'); if (ag) { m.crew.push(ag); crew.push(ag); } }
      movers.push(m);
    }
    // the ford near today's Ponte Vecchio: people and cattle wading across in the shallows (Live)
    if (live && inRange(year, RIVER_LIFE.ford)) for (let i = 0; i < 4; i++) {
      const ag = people.claim(new THREE.Vector3(), new THREE.Vector3(), 'static', 'walk'); if (!ag) break;
      const m: Mover = { obj: ag.obj, x: (bx.vecchio ?? -150) + (i - 1.5) * 3, dir: i % 2 ? 1 : -1, speed: 0, x0: -1.05, x1: 1.05, lane: -1 + i * 0.5, crew: [], bob: 0, kind: 'wade' };
      crew.push(ag); movers.push(m);
    }
  }
  // Sources mode: everything from source A07 (Etruscan – Villanovan) is painted in that source's colour
  let ancientObjs: THREE.Object3D[] = [], hlColor: string | null = null;
  const hlMats: Record<string, THREE.Material> = {};
  function paint() {
    const m = hlColor ? (hlMats[hlColor] ??= new THREE.MeshStandardNodeMaterial({ color: hlColor, emissive: hlColor, emissiveIntensity: 0.35, roughness: 0.8 })) : null;
    for (const o of ancientObjs) o.traverse((c: any) => {
      if (!c.isMesh) return; c.userData.mat0 ??= c.material; c.material = m ?? c.userData.mat0;
    });
  }
  function setHighlight(color: string | null) { if (color !== hlColor) { hlColor = color; paint(); } }
  let grazers: { obj: THREE.Object3D; x: number; z: number; a: number; cx: number; cz: number; r: number }[] = [];

  const M4 = new THREE.Matrix4(), Q = new THREE.Quaternion(), S = new THREE.Vector3(1.5, 1.5, 1.5), P = new THREE.Vector3(), up = new THREE.Vector3(0, 1, 0);
  let t = 0;
  /** Workers on the bank with a fixed round of steps, looped: a step either holds poses for a while (alternating every
   *  `every` s – two strokes of a spade, of kneading, of scrubbing) or walks to a point (with a load in the arms when
   *  `carry`). People stand on the ground as they go (height under their feet each frame). */
  const workers: { ag: any; t: number; steps: Step[]; k?: number; st?: number; load?: THREE.Object3D }[] = [];
  const loadGeo = new THREE.BoxGeometry(0.42, 0.22, 0.3), loadMat = new THREE.MeshStandardMaterial({ color: 0x9a6a48, roughness: 0.95 });
  function workerStep(dt: number) {
    for (const w of workers) {
      const ag = w.ag; if (!ag.obj.visible) continue;
      if (!w.steps.some(s => s.go)) {                         // kneeling crews: poses only, the position stays
        w.t += dt; const total = w.steps.reduce((a, s) => a + (s.dur ?? 0), 0); let ph = w.t % total;
        for (const s of w.steps) { if (ph < s.dur!) { const ps = s.poses!; people.setPose(ag, ps[Math.floor(ph / (s.every ?? 1e9)) % ps.length]); break; } ph -= s.dur!; }
        continue;
      }
      if ((w.st ?? 0) > 0) { w.st! -= dt; people.anim(ag, 'idle'); continue; }   // staggered starts
      const s = w.steps[w.k ?? 0];
      if (s.go) {
        if (!ag.target) { ag.target = s.go.clone(); (ag as any).pace = 1.05; people.setPose(ag, s.carry ? 'carry' : null); }
        if (s.carry && !w.load) { w.load = new THREE.Mesh(loadGeo, loadMat); w.load.position.set(0, 1.05, 0.38); ag.obj.add(w.load); }
        if (s.carry) people.setPose(ag, 'carry');
        if (Math.hypot(ag.obj.position.x - s.go.x, ag.obj.position.z - s.go.z) < 0.6) { ag.target = undefined; w.k = ((w.k ?? 0) + 1) % w.steps.length; w.t = 0; }
      } else {
        if (w.load) { ag.obj.remove(w.load); w.load = undefined; }
        if (w.t === 0) { people.anim(ag, 'idle'); if (s.face) ag.obj.lookAt(s.face.x, ag.obj.position.y, s.face.z); }
        w.t += dt; const ps = s.poses!; people.setPose(ag, ps[Math.floor(w.t / (s.every ?? 1e9)) % ps.length]);
        if (w.t >= s.dur!) { w.t = 0; w.k = ((w.k ?? 0) + 1) % w.steps.length; people.setPose(ag, null); }
      }
      ag.obj.position.y = height(ag.obj.position.x, ag.obj.position.z);
    }
  }
  /** alt: camera height over the view's target. Wide, high views drop the river life: the small animals first, then the
   *  boats (nothing of it would show but a few pixels, and it all costs draw calls). */
  const BOATS_ALT = 1400, SMALL_ALT = 450;
  function update(dt: number, year: number, live: boolean, alt = 0) {
    const k = `${Math.floor(year / 10)}:${live}`;
    if (k !== key) { key = k; rebuild(year, live); }
    group.visible = alt < BOATS_ALT;
    const vk = `${alt < SMALL_ALT}`;
    if (vk !== viewK) { viewK = vk; const on = alt < SMALL_ALT; for (const o of small) o.visible = on; for (const d of ducks) d.obj.visible = on; }
    if (!group.visible) return;
    t += dt;
    workerStep(dt);
    for (const m of movers) {
      if (m.kind === 'nav') {
        m.x += m.dir * m.speed * dt; if (m.x > m.x1 || m.x < m.x0) { m.dir *= -1; m.x = Math.min(m.x1, Math.max(m.x0, m.x)); }
        const p = waterPos(m.x, m.lane), ahead = waterPos(m.x + m.dir * 6, m.lane);
        const dr = m.draft ?? 0.25, floor = p.y - dr + (m.floor ?? 0.08);       // crew stands on the floorboards
        m.obj.position.set(p.x, p.y - dr + Math.sin(t * 1.3 + m.bob) * 0.04, p.z); m.obj.rotation.y = Math.atan2(-(ahead.z - p.z), ahead.x - p.x);
        const hx = ahead.x - p.x, hz = ahead.z - p.z, hl = Math.hypot(hx, hz) || 1;          // along the hull, not the world x axis
        m.crew.forEach((c, i) => { const back = dr < 0.2 ? 1.2 : 1.5 + i * 2.6; c.obj.position.set(p.x - (hx / hl) * back, floor, p.z - (hz / hl) * back); c.obj.rotation.y = m.obj.rotation.y + Math.PI / 2; });
      } else if (m.kind === 'wade') {             // wading across the ford, knee-deep
        m.lane += m.dir * dt * 0.012; if (m.lane > m.x1 || m.lane < m.x0) { m.dir *= -1; m.obj.rotation.y += Math.PI; }
        const p = waterPos(m.x, m.lane); m.obj.position.set(p.x, p.y - 0.55, p.z); m.obj.rotation.y = m.dir > 0 ? 0 : Math.PI;
      } else {                                   // ferry: shuttle bank to bank
        m.lane += m.dir * dt * 0.04; if (m.lane > m.x1 || m.lane < m.x0) m.dir *= -1;
        const p = waterPos(m.x, m.lane); m.obj.position.set(p.x, p.y - 0.25, p.z); m.obj.rotation.y = Math.PI / 2;
        m.crew.forEach(c => c.obj.position.set(p.x, p.y + 0.3, p.z + 2));
      }
    }
    for (const g of grazers) {                  // slow grazing wander inside a circle
      g.a += (R() - 0.5) * dt * 0.6; g.x += Math.cos(g.a) * dt * 0.15; g.z += Math.sin(g.a) * dt * 0.15;
      if (Math.hypot(g.x - g.cx, g.z - g.cz) > g.r) g.a = Math.atan2(g.cz - g.z, g.cx - g.x);
      g.obj.position.set(g.x, height(g.x, g.z), g.z); g.obj.rotation.y = -g.a;
    }
    for (const p of smoke) {                    // hearth / kiln smoke drifting up and east
      p.t = (p.t + dt * 0.08) % 1; const k = p.t;
      p.obj.position.set(p.base.x + k * 6, p.base.y + k * 14, p.base.z - k * 2); p.obj.scale.setScalar(0.5 + k * 2.2);
    }
    for (const d of ducks) {
      d.x += d.v * dt; if (d.x < xMin + 50) d.x = xMax - 50;
      const p = waterPos(d.x, d.lane); d.obj.position.set(p.x, p.y - 0.12, p.z);
    }
    if (birds) {
      const c0 = at(0);
      birdState.forEach((b, i) => {
        b.a += b.s * dt; const flap = Math.abs(Math.sin(t * 14 + i)) * 0.8 + 0.4;
        P.set(b.c.x + Math.cos(b.a) * b.r, c0[1] + b.h + Math.sin(t + i) * 2, c0[2] + Math.sin(b.a) * b.r * 0.6);
        Q.setFromAxisAngle(up, -b.a - Math.sign(b.s) * Math.PI / 2); S.set(1.6, 1.6, 1.6 * flap);
        M4.compose(P, Q, S); birds!.setMatrixAt(i, M4);
      });
      birds.instanceMatrix.needsUpdate = true; birds.visible = year > -10000 && alt < SMALL_ALT;
    }
  }
  /** Ancient object under the ray (its site record), for the inspector card. */
  function pickSite(ray: THREE.Raycaster) {
    const hit = ray.intersectObjects(ancientObjs, true)[0]; if (!hit) return null;
    let o: THREE.Object3D | null = hit.object; while (o && !o.userData.site) o = o.parent;
    return o ? { info: o.userData.site, dist: hit.distance } : null;
  }
  return { group, update, setHighlight, pickSite, ancientCount: () => ancientObjs.length };
}
