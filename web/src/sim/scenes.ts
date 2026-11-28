// Live-mode scenes driven by the calendar: daily markets and scheduled events (calcio storico, Scoppio del Carro…).
// Props come from the Blender library (scene/assets.ts); every scene is built from the same few placed assets.
import * as THREE from 'three/webgpu';
import { freeTree, libraryOf } from './free';
import type { People } from './people';
import type { Props } from '../scene/assets';
import { createFX } from './fx';
import { walk } from './walk';
import { createFlood } from './flood';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

/** The David from Scan the World's 3D scan of the marble (CC BY-SA 4.0; blender/scripts/build_scan_glb.py, 5.17 m, front +Z),
 *  loaded the first time the scene is played and kept: its geometry is shared, never freed. */
let davidScan: Promise<THREE.BufferGeometry | null> | null = null;
function loadDavidScan() {
  davidScan ??= new GLTFLoader().loadAsync('./models/scans/david_stw.glb').then(g => {
    let geo: THREE.BufferGeometry | null = null;
    g.scene.traverse((o: any) => { if (o.isMesh && !geo) geo = o.geometry; });
    if (geo) { (geo as THREE.BufferGeometry).computeBoundingBox(); const b = (geo as THREE.BufferGeometry).boundingBox!; (geo as THREE.BufferGeometry).translate(-(b.min.x + b.max.x) / 2, -b.min.y, -(b.min.z + b.max.z) / 2); }   // centred in the frame
    return geo;
  }).catch(e => { console.warn('David scan missing', e); return null; });
  return davidScan;
}

type Height = (x: number, z: number) => number;
const V = (x: number, y: number, z: number) => new THREE.Vector3(x, y, z);
const R = Math.random;
// camera azimuth per scene (radians; camera placed on this side of the target, looking across the open square)
const CAM: Record<string, number> = { calcio: -1.9, market: 2.6, sanlorenzo: 0.62, scoppio: 0.15, david: -Math.PI / 2, davidWait: 2.6, ponti1944: 0.2, alluvione1966: 0.12 };   // the flood: from the south bank, looking north
// distance (m) and pitch (rad from vertical) of the opening shot; default 110 m / 0.82. The Night of the Bridges frames
// the whole reach from Ponte alla Vittoria (x ≈ −1670) to Ponte San Niccolò (x ≈ +1300) so every blast is in view.
const CAM_DIST: Record<string, [number, number]> = { sanlorenzo: [60, 0.7], ponti1944: [2950, 0.98], alluvione1966: [320, 1.33], david: [19, 1.0] };   // from the south, over Oltrarno
export const PLACES = { market: [-90, 14], sanlorenzo: [-190, -480], calcio: [513, 306], scoppio: [-1, -135], duomoDoor: [27, -139], david: [213.6, -148.5] } as const;
/** Presumed route of the David, 14–18 May 1504 (≈600 m; no street route is documented): out of the Opera del Duomo yard
 *  (wall above the gate broken open), along the south flank of the cathedral, down the Corso (Via dei Calzaiuoli) into
 *  Piazza della Signoria, to the ringhiera by the palace door (Landucci's diary, via Opera di Santa Maria del Fiore).
 *  The gate: in the Opera's west front facing the cathedral's apse across the street (x ≈ 213 in 1504: the 1843 map's
 *  outline, where the yard's entrance – today the museum's, Piazza del Duomo 9 – opens); the statue starts 10 m inside the
 *  yard, comes out square through it, crosses to the middle of the street and turns south along the apse. */
const GATE = { x: 213.6, z: -148.5, nx: -1, nz: 0 };                     // the gate's middle and the face's outward normal
const DAVID_ROUTE: [number, number][] = [[GATE.x + 10, GATE.z], [GATE.x, GATE.z], [GATE.x - 12, GATE.z], [200, -132],
  [200, -110], [100, -102], [40, -96], [14, -90], [13.8, -46], [13.6, 30], [13.5, 104], [16, 170], [35, 230], [55, 258], [64, 269]];
const DAVID_PACE = 2.2, DAVID_WAIT = 5, DAVID_HOLD = 10;               // m/s along the route (four days compressed), s before, s after

/** Easter Sunday 'MM-DD' (Julian computus before 1583, Gregorian after – Meeus/Jones/Butcher). */
export function easter(y: number) {
  let m: number, d: number;
  if (y < 1583) {
    const a = y % 4, b = y % 7, c = y % 19, e = (19 * c + 15) % 30, f = (2 * a + 4 * b - e + 34) % 7;
    m = Math.floor((e + f + 114) / 31); d = ((e + f + 114) % 31) + 1;
  } else {
    const a = y % 19, b = Math.floor(y / 100), c = y % 100, dd = Math.floor(b / 4), e = b % 4, f = Math.floor((b + 8) / 25),
      g = Math.floor((b - f + 1) / 3), h = (19 * a + b - dd - g + 15) % 30, i = Math.floor(c / 4), k = c % 4,
      l = (32 + 2 * e + 2 * i - h - k) % 7, mm = Math.floor((a + 11 * h + 22 * l) / 451);
    m = Math.floor((h + l - 7 * mm + 114) / 31); d = ((h + l - 7 * mm + 114) % 31) + 1;
  }
  return `${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
}

export function createScenes(scene: THREE.Scene, people: People, height: Height, props: Props, squares: any[] = []) {
  const square = (re: RegExp) => squares.find(q => re.test(q.name));
  const root = new THREE.Group(); root.name = 'scene-props'; scene.add(root);
  const keepLib = libraryOf(...Object.values(props.lib));   // the prop library's pieces are shared: never freed
  const sand = new THREE.MeshStandardMaterial({ color: 0xcdb58a, roughness: 1 });
  let active = '', t = 0, paused = false, activeAt: [number, number] | null = null;
  // calcio state
  let ball = V(0, 0, 0), ballVel = V(0, 0, 0), runners: any[] = [], pitch = { cx: 0, cz: 0, w: 0, d: 0 };
  // scoppio state
  let dove: THREE.Object3D | null = null, wireA = V(0, 0, 0), wireB = V(0, 0, 0), cartAt = V(0, 0, 0), fwNext = 0;
  const fxRoot = new THREE.Group(); fxRoot.name = 'scene-fx'; scene.add(fxRoot); const fx = createFX(fxRoot);
  const flood = createFlood(fxRoot, height);     // 4 November 1966
  // 1944 state: the Night of the Bridges
  let bridgeList: { mesh: THREE.Object3D; start: number; end: number; name: string }[] = [], blasts: { at: THREE.Vector3[]; t: number; mesh?: THREE.Object3D; done: boolean }[] = [];
  // david state
  let davidFrame: THREE.Group | null = null, crew: { ag: any; lx: number; lz: number }[] = [], ropes: THREE.Line[] = [], davidMoving = false, davidD = -1;
  const routeLen: number[] = [0];
  for (let i = 1; i < DAVID_ROUTE.length; i++) routeLen.push(routeLen[i - 1] + Math.hypot(DAVID_ROUTE[i][0] - DAVID_ROUTE[i - 1][0], DAVID_ROUTE[i][1] - DAVID_ROUTE[i - 1][1]));
  const routeAt = (d: number) => {
    d = Math.max(0, Math.min(routeLen[routeLen.length - 1] - 0.01, d));
    let i = 1; while (routeLen[i] < d) i++;
    const [ax, az] = DAVID_ROUTE[i - 1], [bx, bz] = DAVID_ROUTE[i], f = (d - routeLen[i - 1]) / (routeLen[i] - routeLen[i - 1]);
    return { x: ax + (bx - ax) * f, z: az + (bz - az) * f, h: Math.atan2(bx - ax, bz - az) };
  };

  function restoreBridges() { for (const b of bridgeList) b.mesh.visible = lastYear >= b.start && lastYear < b.end; blasts = []; }
  let lastYear = 2026;
  function clear() { if (blasts.length) restoreBridges(); flood.clear(); for (const c of [...root.children]) freeTree(c, keepLib); root.clear(); fx.clear(); walk.clearProps(); active = ''; runners = []; shoppers = []; dove = null; t = 0; paused = false; davidFrame = null; crew = []; ropes = []; davidD = -1; }
  const SOLID = /stall|tribune|brindellone|bench|table|scalo|crate|barrel/;      // props people walk around
  const put = (n: string, x: number, z: number, rot = 0) => { const o = props.place(n, x, height(x, z), z, rot, root); if (o && SOLID.test(n)) walk.addProp(o, 0.1); return o; };

  /** Mercato Vecchio (until 1885) around the Colonna dell'Abbondanza: stalls, vendors, customers. */
  function market(cx: number, cz: number, y0 = 1500) {
    const roman = y0 < 500;
    // Colonna dell'Abbondanza at its original spot (today's Piazza della Repubblica, NW part)
    const kx = cx - 6, kz = cz + 11;
    const col = new THREE.Mesh(new THREE.CylinderGeometry(0.45, 0.55, 11, 12), new THREE.MeshStandardMaterial({ color: 0xbfb5a2 }));
    col.position.set(kx, height(kx, kz) + 5.5, kz); col.castShadow = true; if (y0 >= 1431) root.add(col);   // Colonna dell'Abbondanza erected 1431
    const kinds = roman ? ['stall_produce', 'stall_bread'] : ['stall_produce', 'stall_bread', 'stall_cloth'], small = roman ? ['jar', 'jar', 'basket', 'crate'] : ['barrel', 'basket', 'crate', 'jar'];
    for (let row = 0; row < 3; row++) for (let i = 0; i < 6; i++) {
      const x = cx - 17 + i * 6.8, z = cz - 9 + row * 8, s = row === 1 ? -1 : 1, rot = s > 0 ? 0 : Math.PI;
      put(kinds[(i + row) % 3], x, z, rot);
      for (let k = 0; k < 2 + (R() * 3 | 0); k++) put(small[R() * 4 | 0], x + (R() - 0.5) * 3.4, z - s * (1.0 + R() * 0.6), R() * 6.28);   // stock behind the counter
      if (R() < 0.3) put('basket', x + 1.6, z + s * 0.9, R() * 6.28);
      const ven = people.claim(V(x, height(x, z), z - s * 1.2), V(x, 0, z + s * 5), 'static', R() < 0.5 ? 'idle' : 'agree', undefined, y0 >= 1300 ? 'vendor' : undefined); // vendor
      if (ven) people.setTalk(ven, 1);                                     // praising the goods, with the hands
      const cus = R() < 0.85 ? people.claim(V(x + (R() - 0.5), height(x, z), z + s * 1.9), V(x, 0, z - s * 5), 'static', R() < 0.6 ? 'idle' : 'headShake') : null; // customer
      if (cus) people.setTalk(cus, 0.5);                                   // haggling
    }
    for (let i = 0; i < 4; i++) put('bench', kx + 4 + i * 2.5, kz + 3, 0);   // resting by the column
  }

  /** The San Lorenzo market: after the Mercato Vecchio was cleared (1885–95) the city's market life moved round
   *  Mengoni's covered market (1874): stalls line both sides of Via dell'Ariento (OSM ways 772387238/9) along the hall's
   *  east side, vendors behind their counters, people walking the lane between them. Goods by era (*inferred*): food and
   *  household wares at first, clothes and leather goods through the 20th century to today. */
  const ARIENTO: [number, number][] = [[-140.1, -410.2], [-174.5, -459.7], [-178.3, -465.3], [-201.3, -496.9], [-220.7, -523.1], [-234.7, -542.4]];
  let shoppers: { ag: any; lane: [number, number][]; i: number; dir: number; wait: number }[] = [];
  function sanLorenzo(y: number) {
    const kinds = y < 1950 ? ['stall_produce', 'stall_bread', 'stall_cloth'] : ['stall_cloth', 'stall_cloth', 'stall_produce'];
    const small = ['basket', 'crate', 'barrel', 'jar'];
    let k = 0;
    /** Two facing rows of stalls along a polyline; returns the lane's stop points (one per stall pair). */
    const rows = (line: [number, number][], half = 3.6) => {
      const stops: [number, number][] = [];
      for (let i = 0; i < line.length - 1; i++) {
        const [x0, z0] = line[i], [x1, z1] = line[i + 1], L = Math.hypot(x1 - x0, z1 - z0);
        const tx = (x1 - x0) / L, tz = (z1 - z0) / L, nx = -tz, nz = tx;                     // across the lane
        for (let d = 3; d < L - 2; d += 5.2) {
          const lx = x0 + tx * d, lz = z0 + tz * d; let any = false;
          for (const side of [-1, 1]) {
            const x = lx + nx * side * half, z = lz + nz * side * half;
            if (walk.blocked(x, z, 0.8)) continue;
            any = true;
            put(kinds[k++ % kinds.length], x, z, Math.atan2(-nx * side, -nz * side));        // the counter faces the lane
            if (R() < 0.6) put(small[R() * 4 | 0], x + nx * side * 1.2 + (R() - 0.5), z + nz * side * 1.2 + (R() - 0.5), R() * 6.28);
            const vx = x + nx * side * 1.1, vz = z + nz * side * 1.1;
            const ven = people.claim(V(vx, height(vx, vz), vz), V(lx, 0, lz), 'static', R() < 0.5 ? 'idle' : 'agree', undefined, y < 1950 ? 'vendor' : undefined);
            if (ven) people.setTalk(ven, 1);                                                   // calling out, showing the goods
            if (R() < 0.4) { const cx = x - nx * side * 1.9 + (R() - 0.5), cz = z - nz * side * 1.9 + (R() - 0.5);
              const cus = people.claim(V(cx, height(cx, cz), cz), V(x, 0, z), 'static', R() < 0.6 ? 'idle' : 'headShake'); if (cus) people.setTalk(cus, 0.5); }
          }
          if (any) stops.push([lx, lz]);
        }
      }
      return stops;
    };
    const lanes: [number, number][][] = [rows(ARIENTO)];
    // Until January 2014 the stalls also stood round the basilica, on Piazza San Lorenzo (La Nazione); laid out here as
    // one double row along the square's long axis (*inferred* arrangement).
    const sq = y < 2014 ? square(/^piazza san lorenzo$/i) : null;
    if (sq) { const c = Math.cos(sq.rot), sn = Math.sin(sq.rot), h = Math.min(sq.len * 0.3, 45);
      lanes.push(rows([[sq.c[0] - c * h, sq.c[2] + sn * h], [sq.c[0] + c * h, sq.c[2] - sn * h]])); }
    // Shoppers stroll the lanes, stopping at the stalls.
    for (const lane of lanes) if (lane.length > 1) for (let n = 0; n < Math.min(14, lane.length); n++) {
      const i = R() * lane.length | 0, [x, z] = lane[i];
      const ag = people.claim(V(x, height(x, z), z), V(x + 1, 0, z), 'runner', 'walk');
      if (!ag) continue;
      ag.target = V(x, 0, z); (ag as any).pace = 1.05 + R() * 0.3;
      shoppers.push({ ag, lane, i, dir: R() < 0.5 ? -1 : 1, wait: R() * 3 });
    }
  }
  function shopperStep(dt: number) {
    for (const s of shoppers) {
      const p = s.ag.obj.position, t = s.ag.target; if (!t) continue;
      if (Math.hypot(t.x - p.x, t.z - p.z) > 0.7) continue;
      if ((s.wait -= dt) > 0) continue;
      let i = s.i + s.dir; if (i < 0 || i >= s.lane.length) { s.dir = -s.dir; i = s.i + s.dir; }
      s.i = i; const [x, z] = s.lane[i];
      t.set(x + (R() - 0.5) * 2.4, 0, z + (R() - 0.5) * 2.4);                                    // to one side or the other of the lane
      s.wait = R() < 0.45 ? 2 + R() * 5 : 0.3;                                                   // look at the stall, or walk on
    }
  }

  /** Calcio storico in Piazza Santa Croce: sand pitch along the square's axis in front of the basilica,
   *  wooden stands on the long sides and at the west end, two teams of 27, a full audience. */
  function calcio(cx: number, cz: number, year: number) {
    const sq = square(/santa croce/i);
    const rot = sq?.rot ?? -0.386; if (sq) { cx = sq.c[0]; cz = sq.c[2]; }
    const len = sq?.len ?? 133, wid = sq?.wid ?? 52;
    const w = Math.min(len - 34, 96), d = Math.min(wid - 16, 38), y = height(cx, cz);
    const c = Math.cos(rot), s_ = Math.sin(rot);
    const W = (lx: number, lz: number) => V(cx + lx * c + lz * s_, 0, cz - lx * s_ + lz * c);   // square frame -> world
    pitch = { cx, cz, w, d, rot } as any;
    const p = new THREE.Mesh(new THREE.BoxGeometry(w, 0.3, d), sand); p.position.set(cx, y + 0.15, cz); p.rotation.y = rot; p.receiveShadow = true; root.add(p);
    const stand = (lx: number, lz: number, r: number) => { const q = W(lx, lz); const o = props.place('tribune', q.x, y, q.z, rot + r, root); if (o) walk.addProp(o, 0); };
    for (const s of [-1, 1]) for (let i = 0; i < Math.floor(w / 6); i++) stand(-w / 2 + 3 + i * 6, s * (d / 2 + 2.2), s > 0 ? Math.PI : 0);
    for (let i = 0; i < Math.floor(d / 6); i++) stand(-w / 2 - 2.2, -d / 2 + 3 + i * 6, Math.PI / 2);          // curva at the west end
    const teams = year < 1700 ? ['#efe9dc', '#2f6b3a'] : ['#2b5fae', '#b8322e'];          // 1530: Bianchi vs Verdi · today: Azzurri vs Rossi
    for (let t = 0; t < 2; t++) for (let i = 0; i < 27; i++) {
      const pos = W((t ? 1 : -1) * (4 + R() * (w / 2 - 6)), (R() - 0.5) * d * 0.85); pos.y = y + 0.3;
      const ag = people.claim(pos, W(0, 0), 'runner', 'run', teams[t], year < 1700 ? 'calcio_1530' : 'calcio_modern');
      if (ag) { (ag as any).target = pos.clone(); runners.push(ag); }
    }
    let k = 0;
    for (const s of [-1, 1]) for (let tier = 0; tier < 4; tier++) for (let i = 0; i < 18; i++, k++) {    // seated crowd, long sides
      const lx = -w / 2 + 2 + R() * (w - 4), lz = s * (d / 2 + 2.2 + tier * 0.7 + 0.35);
      const q = W(lx, lz); q.y = y + 0.45 + tier * 0.45;
      people.claim(q, W(lx, 0), 'static', R() < 0.65 ? 'idle' : 'agree');
    }
    for (let i = 0; i < 16; i++) { const q = W(-w / 2 - 2.6 - R() * 2, (R() - 0.5) * d); q.y = y + 0.9; people.claim(q, W(0, 0), 'static', 'agree'); }
    ball.copy(W(0, 0)).setY(y + 0.5); ballVel.set(0, 0, 0);
  }

  /** Scoppio del Carro, Easter morning, between the Duomo and the Baptistery: the Brindellone, the wire, the colombina. */
  function scoppio(cx: number, cz: number) {
    const y = height(cx, cz);
    put('brindellone', cx, cz, Math.PI / 2);
    const [dx, dz] = PLACES.duomoDoor;
    wireA.set(dx, height(dx, dz) + 7, dz); wireB.set(cx, y + 6.5, cz);
    const wire = new THREE.Line(new THREE.BufferGeometry().setFromPoints([wireA, wireB]), new THREE.LineBasicMaterial({ color: 0x222222 }));
    root.add(wire);
    dove = put('colombina', dx, dz); if (dove) { dove.position.copy(wireA); dove.scale.setScalar(2.5); dove.visible = false; }
    cartAt.set(cx, y, cz);
    // crowd ring kept back by the cordon, plus the procession group from Santi Apostoli near the cart
    for (let i = 0; i < 120; i++) {
      const a = R() * Math.PI * 2, r = 14 + R() * 18, x = cx + Math.cos(a) * r, z = cz + Math.sin(a) * r * 0.7;
      if (Math.abs(z - dz) < 4 && x > cx) continue;                                       // keep the wire corridor clear
      people.claim(V(x, height(x, z), z), V(cx, 0, cz), 'static', R() < 0.75 ? 'idle' : 'agree');
    }
    for (let i = 0; i < 12; i++) people.claim(V(cx - 6 + (i % 6) * 2.4, y, cz + (i < 6 ? 7 : -7)), V(cx, 0, cz), 'static', 'idle', i % 3 ? '#8c1d1d' : '#e8e1d2', i % 3 ? 'guard' : 'renaissance_elite');
  }

  /** Moving Michelangelo's David, 14–18 May 1504: timber frame on greased beams, the marble hung inside, 40+ men. */
  function david(moving: boolean) {
    davidMoving = moving;
    const wood = new THREE.MeshStandardMaterial({ color: 0x7a5a3a, roughness: 0.9 }), marble = new THREE.MeshStandardMaterial({ color: 0xece6da, roughness: 0.5 });
    const g = new THREE.Group(); davidFrame = g; root.add(g);
    const beam = (w: number, h: number, d: number, x: number, y: number, z: number) => { const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), wood); m.position.set(x, y, z); m.castShadow = true; g.add(m); };
    for (const sx of [-1, 1]) for (const sz of [-1, 1]) beam(0.25, 6.4, 0.25, sx * 1.4, 3.5, sz * 1.4);            // corner posts
    for (const y of [0.45, 3.2, 6.6]) for (const s of [-1, 1]) { beam(3.1, 0.22, 0.22, 0, y, s * 1.4); beam(0.22, 0.22, 3.1, s * 1.4, y, 0); }
    for (const s of [-1, 1]) beam(0.22, 4.2, 0.22, s * 1.4, 2.0, 0);                                   // braces
    for (const s of [-1, 1]) { const m = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.3, 9), wood); m.position.set(s * 1.1, 0.15, 0); g.add(m); }   // greased runners
    const fig = new THREE.Group(); fig.position.y = 1.0; g.add(fig);                                               // the statue, hung free of the floor
    loadDavidScan().then(geo => {                                                     // the 3D scan, 5.17 m with its base, facing the way it goes
      if (!geo || davidFrame !== g) { marble.dispose(); return; }
      keepLib.add(geo); const m = new THREE.Mesh(geo, marble); m.castShadow = m.receiveShadow = true; fig.add(m);
    });
    for (let i = 0; i < 4; i++) { const r = new THREE.Line(new THREE.BufferGeometry().setFromPoints([V(0, 0, 0), V(0, 0, 0)]), new THREE.LineBasicMaterial({ color: 0x3b2f22 })); root.add(r); ropes.push(r); }
    // the men are placed by the scene round the frame every frame (claimed "placed": no free-ground search at the origin,
    // which used to refuse them all): haulers on four ropes ahead, pushers behind, carpenters re-laying the beams,
    // then the escort – the Opera's officials leading, guards in the Signoria's red on both flanks (stones were thrown at
    // the statue by night, and it was guarded; Landucci)
    crew = [];
    const man = (lx: number, lz: number, outfit: string, color?: string) => {
      const ag = people.claim(V(0, 0, 0), V(0, 0, 1), 'static', 'walk', color, outfit, true);
      if (ag) crew.push({ ag, lx, lz });
    };
    if (moving) {
      for (let i = 0; i < 44; i++) {
        const k = i % 4, row = Math.floor(i / 4);
        const lx = i < 28 ? (k - 1.5) * 1.3 : (R() - 0.5) * 4, lz = i < 28 ? 7 + row * 1.6 : i < 38 ? -3.2 - R() * 1.5 : 4 + R() * 2;
        man(lx, lz, R() < 0.15 ? 'renaissance_elite' : 'renaissance_m');
      }
      for (let i = 0; i < 6; i++) man((i % 2 ? 1 : -1) * 1.1, 21 + Math.floor(i / 2) * 1.6, 'renaissance_elite', i < 2 ? '#2a2a2a' : undefined);   // the Opera's officials
      for (let i = 0; i < 4; i++) man((i % 2 ? 1 : -1) * 1.4, 26.5 + Math.floor(i / 2) * 1.6, 'guard', '#8c1d1d');                   // two guards leading
      for (let i = 0; i < 12; i++) man((i % 2 ? 1 : -1) * 4.3, -7 + Math.floor(i / 2) * 4.2, 'guard', i % 4 < 2 ? '#8c1d1d' : '#e8e1d2');   // flanks
    }
    for (let i = 0; i < 60; i++) {                    // onlookers along the street
      const d = 40 + R() * (routeLen[routeLen.length - 1] - 60), p = routeAt(d), s2 = R() < 0.5 ? -1 : 1, off = 6 + R() * 3;
      const x = p.x + Math.cos(p.h) * off * s2, z = p.z - Math.sin(p.h) * off * s2;
      people.claim(V(x, height(x, z), z), V(p.x, 0, p.z), 'static', R() < 0.7 ? 'idle' : 'agree');
    }
    // the yard's gate, its wall broken open above it so the statue would pass: a dark opening in a stone frame
    const gy = height(GATE.x, GATE.z), rot = Math.atan2(GATE.nx, GATE.nz);
    const hole = new THREE.Mesh(new THREE.PlaneGeometry(4.6, 7.6), new THREE.MeshStandardMaterial({ color: 0x15120f, roughness: 1 }));
    hole.position.set(GATE.x + GATE.nx * 0.35, gy + 3.8, GATE.z + GATE.nz * 0.35); hole.rotation.y = rot; root.add(hole);
    const stone = new THREE.MeshStandardMaterial({ color: 0x8d8678, roughness: 0.9 });
    for (const [w, h, x, y] of [[0.5, 7.9, -2.55, 3.95], [0.5, 7.9, 2.55, 3.95], [5.6, 0.5, 0, 7.85]] as const) {
      const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, 0.4), stone); m.rotation.y = rot;
      m.position.set(GATE.x + GATE.nx * 0.4 + Math.cos(rot) * x, gy + y, GATE.z + GATE.nz * 0.4 - Math.sin(rot) * x); m.castShadow = true; root.add(m);
    }
    placeFrame(moving ? 0 : routeLen[routeLen.length - 1], true);
  }
  function placeFrame(d: number, snap = false) {
    if (!davidFrame) return;
    const p = routeAt(d); davidFrame.position.set(p.x, height(p.x, p.z), p.z); davidFrame.rotation.y = p.h;
    const c = Math.cos(p.h), s2 = Math.sin(p.h), W = (lx: number, lz: number) => V(p.x + lx * c + lz * s2, 0, p.z - lx * s2 + lz * c);
    const moved = !snap && davidD >= 0 && Math.abs(d - davidD) > 1e-3; davidD = d;
    for (const m of crew) { const q = W(m.lx, m.lz); q.y = height(q.x, q.z); m.ag.obj.position.copy(q); m.ag.obj.rotation.y = p.h; people.anim(m.ag, moved ? 'walk' : 'idle'); }
    ropes.forEach((r, k) => { const a = W((k - 1.5) * 0.7, 1.5), b = W((k - 1.5) * 1.3, 7 + 6 * 1.6); a.y = height(a.x, a.z) + 1.2; b.y = height(b.x, b.z) + 1.0;
      r.geometry.setFromPoints([a, b]); r.visible = davidMoving; });
  }

  /** Night of 3–4 August 1944: the retreating German army blows up every bridge but Ponte Vecchio, and the blocks at
   *  both ends of Ponte Vecchio (Por Santa Maria, Borgo San Jacopo, Via Guicciardini, Via de' Bardi). One blast after
   *  another (order and timing compressed into a loop; the sources give the night, not the hour of each mine). */
  function ponti1944() {
    const box = new THREE.Box3(), c = V(0, 0, 0), sz = V(0, 0, 0);
    const doomed = bridgeList.filter(b => b.end === 1944 && b.start < 1944);
    const order = ['grazie', 'trinita', 'carraia', 'niccol'];
    doomed.sort((a, b) => order.findIndex(k => a.name.toLowerCase().includes(k)) - order.findIndex(k => b.name.toLowerCase().includes(k)));
    blasts = doomed.map((b, i) => {
      b.mesh.visible = true; box.setFromObject(b.mesh); box.getCenter(c); box.getSize(sz);
      const along = sz.x > sz.z ? V(sz.x * 0.3, 0, 0) : V(0, 0, sz.z * 0.3), top = box.max.y - 1;
      return { at: [c.clone().setY(top), c.clone().add(along).setY(top), c.clone().sub(along).setY(top)], t: 4 + i * 7, mesh: b.mesh, done: false };
    });
    const n = blasts.length;                                    // Ponte Vecchio spared, its approaches mined
    for (const [k, [x, z]] of ([[-125, 368], [-178, 482], [-150, 488], [-196, 474]] as [number, number][]).entries())
      blasts.push({ at: [V(x, height(x, z) + 6, z)], t: 4 + n * 7 + k * 2.5, done: false });
  }

  /** Length (s) of the active scene's sequence, played once; 0 for the open-ended ones (market, calcio, the David waiting). */
  function duration() {
    if (active === 'david' && davidMoving) return DAVID_WAIT + routeLen[routeLen.length - 1] / DAVID_PACE + DAVID_HOLD;
    if (active === 'scoppio') return 24;
    if (active === 'ponti1944') return blasts.length ? Math.max(...blasts.map(b => b.t)) + 6 : 0;
    if (active === 'alluvione1966') return flood.duration;
    return 0;
  }
  /** Jump to a moment of the sequence: past steps are shown done (bridges down, statue further on), with no effects. */
  function seek(to: number) {
    const D = duration(); if (!D) return;
    t = Math.max(0, Math.min(D, to)); fx.clear();
    if (active === 'ponti1944') for (const b of blasts) { b.done = b.t < t; if (b.mesh) b.mesh.visible = !(b.t + 0.5 < t); }
    if (active === 'alluvione1966') { flood.time = t; flood.update(0, D); }
    if (active === 'scoppio' && dove) dove.visible = false;
    if (active === 'david') placeFrame(davidAt(t), true);
  }
  const davidAt = (tt: number) => Math.min(routeLen[routeLen.length - 1] - 0.01, Math.max(0, (tt - DAVID_WAIT) * DAVID_PACE));
  function update(dt: number) {
    if (paused) return;
    const D = duration();
    t += dt; if (D) t = Math.min(t, D);
    if (active === 'sanlorenzo') shopperStep(dt);
    if (active === 'calcio') {
      // ball wanders; players chase it, some hold positions
      ballVel.x += (R() - 0.5) * 6 * dt; ballVel.z += (R() - 0.5) * 6 * dt; ballVel.multiplyScalar(0.98);
      ball.addScaledVector(ballVel, dt);
      { // keep the ball inside the rotated pitch
        const r = (pitch as any).rot ?? 0, c = Math.cos(r), s = Math.sin(r), dx = ball.x - pitch.cx, dz = ball.z - pitch.cz;
        let lx = dx * c - dz * s, lz = dx * s + dz * c;
        lx = Math.max(-pitch.w / 2 + 3, Math.min(pitch.w / 2 - 3, lx)); lz = Math.max(-pitch.d / 2 + 3, Math.min(pitch.d / 2 - 3, lz));
        ball.x = pitch.cx + lx * c + lz * s; ball.z = pitch.cz - lx * s + lz * c; }
      runners.forEach((ag, i) => {
        if (R() < 0.02) {
          const chase = i % 3 !== 0;
          ag.target.set(chase ? ball.x + (R() - 0.5) * 12 : pitch.cx + (R() - 0.5) * pitch.d * 0.8, ball.y, chase ? ball.z + (R() - 0.5) * 8 : pitch.cz + (R() - 0.5) * pitch.d * 0.8);
        }
      });
    }
    if (active === 'david' && davidFrame && davidMoving) {
      // the four days compressed, once: 5 s in the yard, ≈4.5 min along the route, then at the palace door
      placeFrame(davidAt(t));
    }
    if (active === 'scoppio' && dove) {
      // once: 5 s wait · 4 s flight to the cart · ≈11 s of fireworks on the cart · flight back
      const c = t, fly = (k: number) => dove!.position.lerpVectors(wireA, wireB, k * k * (3 - 2 * k));
      dove.visible = c > 5 && c < 15;
      if (c > 5 && c < 9) fly((c - 5) / 4);
      else if (c > 11 && c < 15) fly(1 - (c - 11) / 4);
      if (c >= 9 && c < 9 + dt + 0.001) {                 // the colombina strikes the cart: the wheels start
        fwNext = 0;
        for (const s of [-1, 1]) fx.wheel(cartAt.clone().add(V(s * 1.6, 7.5, 0)), V(0, 0, 1), 8);
      }
      if (c >= 9 && c < 20) {                              // bangs and bursts at points on the cart, then it stops
        fwNext -= dt;
        if (fwNext <= 0) {
          fwNext = 0.25 + R() * 0.35;
          const at = cartAt.clone().add(V((R() - 0.5) * 3, 3 + R() * 7, (R() - 0.5) * 3));
          fx.burst(at, 40 + (R() * 50 | 0), 5 + R() * 5, R() < 0.5 ? [0xffd27a, 0xffffff] : [0xff7a3a, 0xffd27a, 0xfff0c0], 1.2);
          if (R() < 0.45) fx.puff(at, 2.2 + R() * 1.5, 9, 4);
        }
      }
    }
    if (active === 'ponti1944' && blasts.length) {
      const c = t;                                       // once: the night's blasts one after another
      for (const b of blasts) if (!b.done && c >= b.t) {
        b.done = true; b.at.forEach((p, i) => setTimeout(() => fx.explode(p, b.mesh ? 1.8 : 1.2), i * 180));
        if (b.mesh) setTimeout(() => { if (active === 'ponti1944') b.mesh!.visible = false; }, 500);
      }
    }
    if (active === 'alluvione1966') flood.update(dt, D);
    fx.update(dt);
  }

  /** Decide which scene should run for the given date/time and (re)build it. */
  function evaluate(year: number, date: string, hour: number, focus: (x: number, z: number, az?: number, dist?: number, pitch?: number) => void, at?: { live: string; at: [number, number] }, frame = false) {
    const y = Math.round(year);
    let want = '', pos: readonly [number, number] = [0, 0];
    if (at?.live) { want = at.live; pos = at.at; }
    else if ((y === 1530 && date === '02-17') || (y >= 1930 && date === '06-24')) { want = 'calcio'; pos = PLACES.calcio; }
    else if (y >= 1622 && date === easter(y) && hour >= 8 && hour < 13) { want = 'scoppio'; pos = PLACES.scoppio; }
    else if (y === 1944 && ((date === '08-03' && hour >= 20) || (date === '08-04' && hour < 6))) { want = 'ponti1944'; pos = [60, 230]; }   // the five mined bridges, framed a little east of centre so the Live panel does not hide San Niccolò
    else if (y === 1966 && (date === '11-04' || date === '11-05')) { want = 'alluvione1966'; pos = [520, 445]; }   // the flood: Santa Croce, the Uffizi, the Duomo in view
    else if (y === 1504 && date >= '05-14' && date < '06-08') { want = date <= '05-18' ? 'david' : 'davidWait'; pos = date <= '05-18' ? PLACES.david : [64, 269]; }
    else if (((y >= -30 && y < 450) || (y >= 1000 && y < 1885)) && hour >= 6 && hour < 14) { want = 'market'; pos = PLACES.market; }   // Roman forum, then Mercato Vecchio
    if (want === 'david' && at?.live && date > '05-18') { want = 'davidWait'; pos = [64, 269]; }
    lastYear = y; const key = `${want}:${y}`;
    if (key === active + ':' + y && want) { if (frame) focus(pos[0], pos[1], CAM[want], ...(CAM_DIST[want] ?? [])); return want; }
    clear(); people.reset(true);
    if (want === 'market') market(pos[0], pos[1], y);
    if (want === 'sanlorenzo') sanLorenzo(y);
    if (want === 'calcio') calcio(pos[0], pos[1], y);
    if (want === 'scoppio') scoppio(pos[0], pos[1]);
    if (want === 'ponti1944') ponti1944();
    if (want === 'alluvione1966') void flood.build('./data');
    if (want === 'david' || want === 'davidWait') { david(want === 'david'); const fr = davidFrame as THREE.Group | null; if (fr) pos = want === 'david' ? [GATE.x - 4, GATE.z] : [fr.position.x, fr.position.z]; }
    active = want; activeAt = want ? [pos[0], pos[1]] : null;
    if (want && (at?.live || frame)) focus(pos[0], pos[1], CAM[want], ...(CAM_DIST[want] ?? []));
    return want;
  }
  /** The line at the top while a scene plays: play-by-play where the sequence has steps, otherwise its main facts for as long
   *  as it runs. The flood keeps its own clock line. Sources: docs/EVENTS-COSTUMES.md (David: Landucci's diary and the Opera
   *  di Santa Maria del Fiore; Scoppio: Opera, visittuscany; Night of the Bridges: La Nazione, Uffizi, storiadifirenze). */
  function narration(): { title: string; text: string } | null {
    if (!active || active === 'alluvione1966') return null;
    const c = t;
    if (active === 'scoppio') {
      const title = `Scoppio del Carro · Easter Sunday ${lastYear}`;
      return { title, text: c < 5 ? 'The Brindellone, drawn here by white oxen, stands between the Duomo and the Baptistery, loaded with fireworks.'
        : c < 9 ? 'At the Gloria the archbishop lights the colombina at the high altar, with fire struck from the flints of the Holy Sepulchre.'
        : c < 11 ? 'The colombina runs down the wire out of the cathedral and sets the cart alight: rockets, wheels of fire, smoke.'
        : c < 15 ? 'It flies back along the wire to the altar – a smooth flight promises a good year for the harvest.'
        : 'The fireworks go on burning on the cart, one tier after another, over the crowd in the square.' };
    }
    if (active === 'david') {
      const d = davidAt(c), L = routeLen[routeLen.length - 1], f = d / L;
      return { title: 'The David leaves the Opera del Duomo · 14–18 May 1504', text: c < DAVID_WAIT ? 'Evening of 14 May: the wall over the Opera\'s yard gate is broken open to let the giant out.'
        : f < 0.3 ? 'In a timber frame, the marble hung free inside, it slides on greased beams, hauled by some forty men with windlasses.'
        : f < 0.65 ? 'Guards walk beside it: on the first night stones were thrown at it (Landucci). It goes a few hundred braccia a day.'
        : f < 0.999 ? 'Four days through the streets, about 600 m in all, towards Piazza della Signoria.'
        : '18 May: it reaches the palace. On 8 June it stands on the ringhiera; it is unveiled on 8 September 1504.' };
    }
    if (active === 'ponti1944') {
      const next = blasts.filter(b => b.t <= c).pop(), i = next ? blasts.indexOf(next) : -1;
      const name = next?.mesh ? bridgeList.find(b => b.mesh === next.mesh)?.name : null;
      return { title: 'The Night of the Bridges · 3–4 August 1944', text: !next ? 'The retreating German army has mined every bridge on the Arno; the people of the riverside streets were ordered out.'
        : name ? `${name} is blown up (the order of the blasts here is inferred).`
        : i < blasts.length - 1 ? 'Ponte Vecchio is spared, but the houses at both its ends are blown down to block it: Por Santa Maria, Via de\' Bardi, Borgo San Jacopo, Via Guicciardini.'
        : 'Dawn on 4 August: only Ponte Vecchio still stands, cut off by the ruins.' };
    }
    if (active === 'market') return lastYear < 500
      ? { title: 'Market morning in the forum of Florentia', text: 'Stalls of bread, oil, wine and produce in the forum, where Piazza della Repubblica is today; the cardo and the decumanus cross here.' }
      : { title: 'Market morning in the Mercato Vecchio', text: 'The daily market round the Colonna dell\'Abbondanza (1431): fruit, bread and cloth under awnings, the guild halls and towers around. It stood until it was cleared in 1885–95.' };
    if (active === 'sanlorenzo') return { title: 'Market day at San Lorenzo',
      text: lastYear < 1950 ? 'Round Giuseppe Mengoni\'s covered market of 1874, which took the food trade once the Mercato Vecchio was cleared (1885–95): stalls along Via dell\'Ariento, under the hall\'s iron and glass.'
        : 'Stalls along Via dell\'Ariento beside the Mercato Centrale (Mengoni, 1874): clothes, leather and souvenirs outside, food in the hall.' };
    if (active === 'calcio') return lastYear < 1600
      ? { title: 'Calcio during the siege · 17 February 1530', text: 'Two teams of 27 on a pitch in Piazza Santa Croce, played in defiance of the imperial army besieging the city.' }
      : { title: `Calcio storico · 24 June ${lastYear}`, text: 'The final for San Giovanni in Piazza Santa Croce: 27 a side on sand, the four quarters in their colours; revived in 1930.' };
    if (active === 'davidWait') return { title: 'The David on its way · May–June 1504', text: 'The statue stands in its frame in Piazza della Signoria while the ringhiera is made ready; it is set up on 8 June.' };
    return null;
  }
  /** A moving subject the camera should follow, or null (the David is framed by camGoal). */
  const follow = () => null as THREE.Vector3 | null;
  /** A scene that lights itself (the flood's clock): the hour for the sun, or null. */
  const lightHour = () => (active === 'alluvione1966' ? flood.lightHour() : null);
  /** A scene that moves the camera: [x, z, distance, pitch, heading] to ease towards, or null. `aspect` is the width/height
   *  of the part of the view left free by the side panels (the flood fits its spreading water into it). */
  const ease = (a: number, b: number, x: number) => { const k = Math.min(1, Math.max(0, (x - a) / (b - a))); return k * k * (3 - 2 * k); };
  function camGoal(aspect = 1.6): [number, number, number, number, number] | null {
    if (paused) return null;
    if (active === 'alluvione1966') return flood.camGoal(aspect);
    if (active === 'david' && davidFrame && davidMoving) {
      // in front of the gate, low, as the statue comes out of the yard; then up over it, following it from above
      const az = Math.atan2(GATE.nx, GATE.nz), up = ease(DAVID_WAIT + 9, DAVID_WAIT + 15, t), p = davidFrame.position;
      return [GATE.x - 4 + (p.x - GATE.x + 4) * up, GATE.z + (p.z - GATE.z) * up, 19 + 61 * up, 1.0 - 0.65 * up, az];   // the street to the apse is ≈22 m wide
    }
    return null;
  }
  return { evaluate, update, clear, follow, lightHour, camGoal, duration, seek, narration, setBridges(b: typeof bridgeList) { bridgeList = b; },
    get active() { return active; }, get activeAt() { return activeAt; }, get time() { return t; }, get paused() { return paused; }, set paused(v: boolean) { paused = v; } };
}
