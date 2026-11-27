// Life in the squares and on the bridges near the camera (Live mode). Built only for the few squares and bridges the
// camera is close to, and taken down when it moves away, so the crowd never runs everywhere at once.
// Squares: benches by era (wooden benches; from the 15th c. the stone "panche di via" along palace fronts; cast-iron and
// slat benches from the mid-19th c.), people sitting and talking, groups chatting, couples strolling, stalls with a
// vendor and customers looking at the goods. Bridges: people leaning on the parapets, looking at the river.
// Shares, counts and placement are *inferred* (period views and photographs show squares as meeting places; no counts).
import * as THREE from 'three/webgpu';
import type { Props } from '../scene/assets';
import { walk } from './walk';
import type { People } from './people';

type Height = (x: number, z: number) => number;
interface Sq { name: string; c: number[]; ring: number[][]; len: number; wid: number; rot: number; park?: boolean | null }
interface Br { mesh: THREE.Object3D; x: number; start: number; end: number; name: string }
type Agent = any;
interface Act { ag: Agent; kind: 'chat' | 'stroll' | 'look'; next: number; home?: THREE.Vector3; pace?: number }
interface Site { key: string; x: number; z: number; grp: THREE.Group; ags: Agent[]; acts: Act[] }

const R = Math.random, V = (x: number, y: number, z: number) => new THREE.Vector3(x, y, z);
// squares opened late: no crowd there before (years from the city's history; the smaller modern squares *inferred*)
const OPENED: [RegExp, number][] = [
  [/repubblica/i, 1890], [/indipendenza/i, 1844], [/libert/i, 1865], [/beccaria/i, 1865], [/michelangiolo/i, 1873],
  [/piazzale degli uffizi/i, 1581], [/adua|unit. italiana|mentana|giudici|vasari|ghiberti|delle cure/i, 1870],
  [/costituzione|pratolini|zoli|beslan|barbieri|morales|pincherle|carlo levi|salvemini|bargellini|caduti/i, 1930],
];
const NOT_SQUARE = /^(via|viale|lungarno)\b/i;
const BRIDGE_RESERVE = 28;

export function createSquares(scene: THREE.Scene, props: Props, people: People, height: Height, squares: Sq[], bridges: Br[],
  graph?: { nodes: number[][]; edges: number[][] }) {
  const root = new THREE.Group(); root.name = 'square-life'; scene.add(root);
  const list = squares.filter(q => !NOT_SQUARE.test(q.name) && !q.park && q.ring?.length > 3)
    .map(q => ({ q, x: q.c[0], z: q.c[2], r: Math.max(q.len, q.wid) / 2, from: OPENED.find(([re]) => re.test(q.name))?.[1] ?? -9999 }));
  const sites = new Map<string, Site>();
  // Ponte Vecchio is a landmark model, not one of the dated bridge phases: its roadway comes from the street graph's bridge
  // edges between Santa Trinita and the Grazie (the only bridge there since Roman times)
  const cen = (re: RegExp) => { const b = bridges.find(b => re.test(b.name)); return b ? new THREE.Box3().setFromObject(b.mesh).getCenter(V(0, 0, 0)) : null; };
  const cT = cen(/trinita/i), cG = cen(/grazie/i);
  const pv = !cT || !cG ? [] : (graph?.edges ?? []).filter(e => e[2] === 1).map(e => [graph!.nodes[e[0]], graph!.nodes[e[1]]])
    .filter(([a, b]) => {
      const x = (a[0] + b[0]) / 2, z = (a[2] + b[2]) / 2, zr = cT.z + ((cG.z - cT.z) * (x - cT.x)) / (cG.x - cT.x);   // on the river line
      return x > cT.x + 40 && x < cG.x - 40 && Math.abs(z - zr) < 70;
    });
  const pvC = pv.length ? pv.reduce((c, [a, b]) => [c[0] + (a[0] + b[0]) / 2 / pv.length, c[1] + (a[2] + b[2]) / 2 / pv.length], [0, 0]) : null;
  let year = 2026, hour = 12, epoch = -1, era = '', check = 0, clock = 0;

  // ---- geometry helpers ----
  const inside = (ring: number[][], x: number, z: number) => {
    let c = false;
    for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
      const [xi, zi] = ring[i], [xj, zj] = ring[j];
      if ((zi > z) !== (zj > z) && x < ((xj - xi) * (z - zi)) / (zj - zi) + xi) c = !c;
    }
    return c;
  };
  const edgeDist = (ring: number[][], x: number, z: number) => {
    let d = Infinity;
    for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
      const [ax, az] = ring[j], [bx, bz] = ring[i], dx = bx - ax, dz = bz - az, L = dx * dx + dz * dz || 1;
      const t = Math.max(0, Math.min(1, ((x - ax) * dx + (z - az) * dz) / L)); d = Math.min(d, Math.hypot(x - ax - dx * t, z - az - dz * t));
    }
    return d;
  };
  function spot(q: Sq, margin: number, r: number): [number, number] | null {
    let x0 = Infinity, x1 = -Infinity, z0 = Infinity, z1 = -Infinity;
    for (const [x, z] of q.ring) { x0 = Math.min(x0, x); x1 = Math.max(x1, x); z0 = Math.min(z0, z); z1 = Math.max(z1, z); }
    for (let k = 0; k < 40; k++) {
      const x = x0 + R() * (x1 - x0), z = z0 + R() * (z1 - z0);
      if (inside(q.ring, x, z) && edgeDist(q.ring, x, z) > margin && !walk.blocked(x, z, r)) return [x, z];
    }
    return null;
  }
  const at = (x: number, z: number) => V(x, height(x, z), z);

  // ---- building a square ----
  function buildSquare(key: string, s: typeof list[number]): Site {
    const q = s.q, grp = new THREE.Group(); root.add(grp);
    const site: Site = { key, x: s.x, z: s.z, grp, ags: [], acts: [] };
    const put = (n: string, x: number, z: number, rot: number) => { const o = props.place(n, x, height(x, z), z, rot, grp); if (o) walk.addProp(o, 0.1, key); return o; };
    const claim = (p: THREE.Vector3, face: THREE.Vector3, anim: string, outfit?: string, placed = false) => {
      const a = people.claim(p, face, 'static', anim, undefined, outfit, placed); if (a) site.ags.push(a); return a;
    };
    const day = hour >= 7 && hour < 21 ? 1 : 0.3, area = q.len * q.wid * 0.75;
    const cap = Math.max(8, Math.floor((people.agents.length - BRIDGE_RESERVE) / 3));   // three squares at most, the bridges keep theirs
    const n = Math.round(Math.max(8, Math.min(64, cap, (area / 22) * day)));
    // benches along the edges of the square, facing in
    const bench = year < 1400 ? ['bench'] : year < 1850 ? ['bench_stone', 'bench_stone', 'bench'] : ['bench_park', 'bench_park', 'bench_stone'];
    let benches = Math.max(3, Math.min(14, Math.round(n / 4)));
    const ring = q.ring;
    for (let i = 0, j = ring.length - 1; i < ring.length && benches > 0; j = i++) {
      const [ax, az] = ring[j], [bx, bz] = ring[i], L = Math.hypot(bx - ax, bz - az); if (L < 7) continue;
      let nx = -(bz - az) / L, nz = (bx - ax) / L;                                  // the edge's normal, turned to the inside
      const mx = (ax + bx) / 2, mz = (az + bz) / 2; if (!inside(ring, mx + nx * 2, mz + nz * 2)) { nx = -nx; nz = -nz; }
      for (let f = 0.25; f < 1 && benches > 0; f += 9 / L) {
        if (R() < 0.35) continue;
        const x = ax + (bx - ax) * f + nx * 1.5, z = az + (bz - az) * f + nz * 1.5;
        if (walk.blocked(x, z, 1.0) || walk.blocked(x + nx * 2, z + nz * 2, 0.4)) continue;
        const kind = bench[(R() * bench.length) | 0], rot = Math.atan2(nx, nz);     // front (+Z) faces the inside
        if (!put(kind, x, z, rot)) continue; benches--;
        const seats = R() < 0.75 ? (R() < 0.45 ? 2 : 1) : 0, ex = (bx - ax) / L, ez = (bz - az) / L;
        for (let k = 0; k < seats; k++) {
          const o = seats === 2 ? (k ? 0.45 : -0.45) : (R() - 0.5) * 0.6, y = height(x, z);
          const p = V(x + ex * o + nx * 0.06, y - 0.49, z + ez * o + nz * 0.06);
          const look = seats === 2 ? V(x + ex * -o * 3 + nx * 2, y, z + ez * -o * 3 + nz * 2) : V(x + nx * 5, y, z + nz * 5);
          const a = claim(p, look, R() < 0.5 ? 'idle' : 'agree', undefined, true); if (!a) continue;
          a.obj.position.copy(p); people.setPose(a, 'sit');
          if (seats === 2) site.acts.push({ ag: a, kind: 'chat', next: R() * 4 });
        }
      }
    }
    let left = n - site.ags.length;
    // stalls: common before the 20th century (fruit, bread, cloth); afterwards now and then a flower or news stand
    const stalls = year < 1900 ? Math.max(1, Math.min(6, Math.round(n / 9))) : R() < 0.35 ? 1 : 0;
    const kinds = year < 500 ? ['stall_produce', 'stall_bread'] : ['stall_produce', 'stall_bread', 'stall_cloth'];
    for (let i = 0; i < stalls && left > 0; i++) {
      const sp = spot(q, 4, 2.2); if (!sp) break;
      const [x, z] = sp, rot = R() * Math.PI * 2, fx = Math.sin(rot), fz = Math.cos(rot);
      if (!put(year < 1900 ? kinds[(R() * kinds.length) | 0] : 'stall_cloth', x, z, rot)) continue;
      for (const sm of ['basket', 'crate']) if (R() < 0.6) put(sm, x - fx * 1.1 + (R() - 0.5) * 2, z - fz * 1.1 + (R() - 0.5) * 2, R() * 6);
      claim(at(x - fx * 1.2, z - fz * 1.2), at(x + fx * 4, z + fz * 4), R() < 0.5 ? 'agree' : 'idle', year >= 1300 && year < 1900 ? 'vendor' : undefined); left--;
      for (let k = 0, c = 1 + ((R() * 3) | 0); k < c && left > 0; k++, left--) {          // customers looking, haggling
        const ox = (k - (c - 1) / 2) * 0.9, sx = Math.cos(rot) * ox, sz = -Math.sin(rot) * ox;
        const a = claim(at(x + fx * (1.9 + R() * 0.4) + sx, z + fz * (1.9 + R() * 0.4) + sz), at(x, z), R() < 0.5 ? 'idle' : 'headShake');
        if (a) site.acts.push({ ag: a, kind: 'chat', next: 1 + R() * 5 });
      }
    }
    // groups talking: two to four in a small circle, taking turns
    while (left >= 2) {
      const sz = Math.min(left, 2 + ((R() * 3) | 0)), sp = spot(q, 2, 1.4); if (!sp) break;
      const [cx, cz] = sp, a0 = R() * 6.28;
      for (let k = 0; k < sz; k++) {
        const a = a0 + (k / sz) * Math.PI * 2, r = 0.55 + sz * 0.12, p = at(cx + Math.cos(a) * r, cz + Math.sin(a) * r);
        const ag = claim(p, at(cx, cz), k === 0 ? 'agree' : 'idle'); if (ag) site.acts.push({ ag, kind: 'chat', next: R() * 3 });
      }
      left -= sz;
      if (R() < 0.45 && left >= 2) {                     // a couple walking slowly round the square
        for (let k = 0; k < 2; k++) {
          const sp2 = spot(q, 2, 0.4); if (!sp2) break;
          const ag = people.claim(at(sp2[0] + k * 0.8, sp2[1]), at(s.x, s.z), 'runner', 'walk'); if (!ag) break;
          site.ags.push(ag); site.acts.push({ ag, kind: 'stroll', next: 0, pace: 0.9 + R() * 0.3 }); left--;
        }
      }
    }
    if (left > 0) { const sp = spot(q, 2, 0.4); if (sp) { const ag = claim(at(sp[0], sp[1]), at(s.x, s.z), 'idle'); if (ag) site.acts.push({ ag, kind: 'look', next: 2 + R() * 6 }); } }
    return site;
  }

  // ---- a bridge: people at the parapets ----
  const ray = new THREE.Raycaster(), down = V(0, -1, 0);
  function deckAt(b: Br, x: number, z: number, top: number) {
    ray.set(V(x, top, z), down); const h = ray.intersectObject(b.mesh, true)[0]; return h ? h.point.y : NaN;
  }
  function buildBridge(key: string, b: Br): Site {
    const grp = new THREE.Group(); root.add(grp);
    const box = new THREE.Box3().setFromObject(b.mesh), c = box.getCenter(V(0, 0, 0));
    const site: Site = { key, x: c.x, z: c.z, grp, ags: [], acts: [] };
    const top = box.max.y + 5, n = 6 + ((R() * 7) | 0);
    for (let i = 0; i < n; i++) {
      const z = box.min.z + 8 + R() * (box.max.z - box.min.z - 16);
      // the deck's centre line at this z (bridges run roughly north–south), then out to the edge of the roadway
      let xc = NaN, y0 = NaN;
      for (const dx of [0, -3, 3, -6, 6]) { const y = deckAt(b, c.x + dx, z, top); if (!Number.isNaN(y)) { xc = c.x + dx; y0 = y; break; } }
      if (Number.isNaN(y0)) continue;
      const side = R() < 0.5 ? -1 : 1; let hw = 0;
      for (let o = 0.5; o < 14; o += 0.5) { const y = deckAt(b, xc + side * o, z, top); if (Number.isNaN(y) || Math.abs(y - y0) > 0.4) break; hw = o; }
      if (hw < 1.5) continue;
      const p = V(xc + side * (hw - 0.45), y0, z), face = V(p.x + side * 5, y0, z);
      const ag = people.claim(p, face, 'static', R() < 0.3 ? 'agree' : 'idle', undefined, undefined, true); if (!ag) break;
      ag.obj.position.copy(p); ag.obj.lookAt(face); site.ags.push(ag);
      if (R() < 0.4) {                                   // a companion beside, half turned to talk
        const q2 = V(p.x - side * 0.1, y0, z + 0.7), ag2 = people.claim(q2, V(p.x, y0, p.z), 'static', 'agree', undefined, undefined, true);
        if (ag2) { ag2.obj.position.copy(q2); ag2.obj.lookAt(p.x + side * 3, y0, p.z - 1); site.ags.push(ag2); site.acts.push({ ag: ag2, kind: 'chat', next: R() * 3 }, { ag, kind: 'chat', next: 1 + R() * 3 }); }
      }
    }
    return site;
  }

  function buildVecchio(key: string): Site {
    const grp = new THREE.Group(); root.add(grp);
    const site: Site = { key, x: pvC![0], z: pvC![1], grp, ags: [], acts: [] };
    const n = 10 + ((R() * 8) | 0);
    for (let i = 0; i < n; i++) {
      const [a, b] = pv[(R() * pv.length) | 0], t = R(), dx = b[0] - a[0], dz = b[2] - a[2], L = Math.hypot(dx, dz) || 1;
      const side = R() < 0.5 ? -1 : 1, nx = (-dz / L) * side, nz = (dx / L) * side, mid = Math.hypot(a[0] + dx * t - site.x, a[2] + dz * t - site.z) < 14;
      const off = mid ? 3.2 : 2.4;                     // at the middle the parapet of the open terrace, elsewhere the shop windows
      // the deck: graph nodes sit at water level here, so cast down onto the landmark along the open centre of the roadway
      const cx = a[0] + dx * t, cz = a[2] + dz * t; ray.set(V(cx, 40, cz), down); ray.far = 60;
      const hit = ray.intersectObjects(scene.children.filter(o => o !== root && !/people|river|square/i.test(o.name)), true).filter(h => h.point.y > 5 && h.point.y < 20).sort((p, q) => p.point.y - q.point.y)[0];   // the deck, not the shop roofs or the Corridor above
      if (!hit) continue;
      const p = V(cx + nx * off, hit.point.y, cz + nz * off), face = V(p.x + nx * 4, p.y, p.z + nz * 4);
      const ag = people.claim(p, face, 'static', R() < 0.35 ? 'agree' : 'idle', undefined, undefined, true); if (!ag) break;
      ag.obj.position.copy(p); ag.obj.lookAt(face); site.ags.push(ag);
      if (R() < 0.35) site.acts.push({ ag, kind: 'look', next: R() * 4 });
    }
    return site;
  }
  function drop(s: Site) { for (const a of s.ags) if (a.busy) people.release(a); walk.clearProps(s.key); root.remove(s.grp); sites.delete(s.key); }
  function dropAll() { for (const s of [...sites.values()]) drop(s); }

  /** cam: camera position; target: what it looks at; avoid: where an event scene has its own crowd. */
  function update(dt: number, cam: THREE.Vector3, target: THREE.Vector3, y: number, h: number, live: boolean, avoid?: [number, number] | null) {
    clock += dt;
    const e = `${Math.floor(y / 10)}:${live}`;
    if (people.epoch !== epoch || e !== era) { dropAll(); epoch = people.epoch; era = e; check = 0; }
    year = y; hour = h;
    if (!live) return;
    if ((check -= dt) <= 0) {
      check = 0.5;
      const want = new Map<string, () => Site>();
      if (cam.y - target.y < 260) {
        const d = (x: number, z: number) => Math.min(Math.hypot(cam.x - x, cam.z - z), Math.hypot(target.x - x, target.z - z));
        list.filter(s => year >= s.from && d(s.x, s.z) < 140 + s.r && !(avoid && Math.hypot(avoid[0] - s.x, avoid[1] - s.z) < 90) && !walk.blocked(s.x, s.z, 0.5))
          .sort((a, b) => d(a.x, a.z) - d(b.x, b.z)).slice(0, 3)
          .forEach(s => want.set('sq:' + s.q.name + ':' + Math.round(s.x), () => buildSquare('sq:' + s.q.name + ':' + Math.round(s.x), s)));
        const seen = new Set<string>();
        bridges.filter(b => year >= b.start && year < b.end && b.mesh.visible)
          .map(b => ({ b, c: new THREE.Box3().setFromObject(b.mesh).getCenter(V(0, 0, 0)) }))
          .filter(o => d(o.c.x, o.c.z) < 220).sort((a, b) => d(a.c.x, a.c.z) - d(b.c.x, b.c.z))
          .filter(o => !seen.has(o.b.name) && seen.add(o.b.name)).slice(0, 2)
          .forEach(o => want.set('br:' + o.b.name + ':' + o.b.start, () => buildBridge('br:' + o.b.name + ':' + o.b.start, o.b)));
        if (pvC && year >= -30 && d(pvC[0], pvC[1]) < 220) want.set('br:Ponte Vecchio', () => buildVecchio('br:Ponte Vecchio'));
      }
      for (const s of [...sites.values()]) if (!want.has(s.key)) drop(s);
      for (const [k, make] of [...want].sort((a, b) => (a[0] < b[0] ? -1 : 1))) if (!sites.has(k)) sites.set(k, make());   // 'br:' first
    }
    // taking turns in a conversation, strolling on
    for (const s of sites.values()) for (const a of s.acts) {
      if (!a.ag.busy) continue;
      if (a.kind === 'stroll') {
        const ag = a.ag;
        if (!ag.target || ag.obj.position.distanceTo(ag.target) < 0.8) {
          if ((a.next -= dt) > 0) continue;
          const q = list.find(l => s.key.startsWith('sq:' + l.q.name))?.q; const sp = q && spot(q, 2, 0.4);
          if (sp) { ag.target = at(sp[0], sp[1]); ag.pace = a.pace; } a.next = 2 + R() * 6;
        }
        continue;
      }
      if ((a.next -= dt) > 0) continue;
      a.next = 2 + R() * 5;
      people.anim(a.ag, a.kind === 'look' ? (R() < 0.7 ? 'idle' : 'headShake') : ['agree', 'idle', 'idle', 'headShake'][(R() * 4) | 0]);
    }
  }
  return { update, clear: dropAll, get vecchio() { return pvC; }, get count() { let n = 0; for (const s of sites.values()) n += s.ags.length; return n; }, get sites() { return [...sites.keys()]; } };
}
