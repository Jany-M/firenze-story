// "X-ray" for close views near the ground: a building that stands between the camera and the point being looked at
// (controls.target) is taken out of the view, whole, as in a game – not faded into a see-through pattern. A few rays from the
// camera through the middle of the screen look for structures they pass right through, well short of the target (entering
// in the first 45 %, leaving before 65 % of the way, above their own ground). Those, and only those, go: city buildings by
// record id, landmark parts by object. Never the building being looked at: a structure whose box holds the target stays,
// and for a landmark the box is the whole building's (zooming onto the Duomo, the Baptistery or Pitti never opens them up).
// A structure stays hidden 0.8 s after its last hit, so it does not blink while the camera moves.
import * as THREE from 'three/webgpu';
import { Fn, uniform, float, abs } from 'three/tsl';
import { isAlive, type Rec } from './city';

export const uXray = uniform(0);                                  // 0 off … 1 full (camera height near the ground)
export const uXrayDepth = uniform(0);                             // view depth of the target minus a margin (kept for callers)
export const uCamFwd = uniform(new THREE.Vector3(0, 0, -1));      // camera forward (world)
const MAXOCC = 12;
const uOcc = Array.from({ length: MAXOCC }, () => uniform(-1));   // record ids of the city buildings taken out of the view
const uOccW = Array.from({ length: MAXOCC }, () => uniform(0));   // 1 while hidden
const MAXMAN = 6;                                                 // buildings hidden by hand (right click), any height
const uMan = Array.from({ length: MAXMAN }, () => uniform(-1));

/** City mask: keep the fragment unless its building is one of the current occluders. */
export function cityKeep(bid: any) {
  return Fn(() => {
    let w: any = abs(bid.sub(uOcc[0])).lessThan(0.5).select(uOccW[0], float(0));
    for (let i = 1; i < MAXOCC; i++) w = w.add(abs(bid.sub(uOcc[i])).lessThan(0.5).select(uOccW[i], float(0)));
    let m: any = abs(bid.sub(uMan[0])).lessThan(0.5).select(float(1), float(0));
    for (let i = 1; i < MAXMAN; i++) m = m.add(abs(bid.sub(uMan[i])).lessThan(0.5).select(float(1), float(0)));
    return w.mul(uXray).add(m).lessThan(0.5);
  })();
}
/** Landmark parts in the way: their materials swapped for invisible copies while hidden. */
const fadeClones = new WeakMap<THREE.Material, THREE.Material>();
function fadeClone(m: THREE.Material) {
  let c = fadeClones.get(m);
  if (!c) { c = m.clone(); c.visible = false; fadeClones.set(m, c); }
  return c;
}

export interface LandmarkPart { obj: THREE.Object3D; box: THREE.Box3; whole?: THREE.Box3; root?: THREE.Object3D }

export function createXray(camera: THREE.PerspectiveCamera, target: THREE.Vector3, city: { boxes: Float32Array; recs: Rec[] }, landmarkParts: () => LandmarkPart[]) {
  // one box per city record (from its triangles), filled in by the city as its tiles load
  const B = city.boxes, recs = city.recs;
  /** ray (origin o, unit dir d) against box → [tEnter, tExit] or null */
  const slab = (o: THREE.Vector3, d: THREE.Vector3, mn: number[], mx: number[]): [number, number] | null => {
    let t0 = 0, t1 = Infinity; const O = [o.x, o.y, o.z], D = [d.x, d.y, d.z];
    for (let k = 0; k < 3; k++) {
      if (Math.abs(D[k]) < 1e-9) { if (O[k] < mn[k] || O[k] > mx[k]) return null; continue; }
      let a = (mn[k] - O[k]) / D[k], b = (mx[k] - O[k]) / D[k]; if (a > b) [a, b] = [b, a];
      t0 = Math.max(t0, a); t1 = Math.min(t1, b); if (t0 > t1) return null;
    }
    return [t0, t1];
  };
  const rc = new THREE.Raycaster(), ndc = new THREE.Vector2(), occCity = new Set<number>(), occParts = new Set<THREE.Object3D>();
  const faded = new Set<THREE.Object3D>(), hits = new Map<number, number>();
  // rays: the middle of the screen and a ring of 8 round it
  const SAMPLES: [number, number][] = [[0, 0], ...Array.from({ length: 8 }, (_, k) => [Math.cos(k * Math.PI / 4) * 0.28, Math.sin(k * Math.PI / 4) * 0.4] as [number, number])];
  let acc = 0;
  const restore = (o: THREE.Object3D) => o.traverse((m: any) => { if (m.isMesh && m.userData.preFade) { if (!m.userData.preHide) m.material = m.userData.preFade; m.userData.preFade = null; } });

  /** Is the target inside this box (1.5 m of slack: a target on a front lies on the box's face)? */
  const inBox = (x0: number, y0: number, z0: number, x1: number, y1: number, z1: number) =>
    target.x > x0 - 1.5 && target.x < x1 + 1.5 && target.y > y0 - 1.5 && target.y < y1 + 1.5 && target.z > z0 - 1.5 && target.z < z1 + 1.5;
  function scan(year: number) {
    occCity.clear(); occParts.clear(); hits.clear();
    const d = camera.position.distanceTo(target), cam = camera.position;
    const parts = landmarkParts();
    for (const [sx, sy] of SAMPLES) {
      ndc.set(sx, sy); rc.setFromCamera(ndc, camera); const dir = rc.ray.direction;
      // how far this ray has to go to reach what is being looked at: the target's level, capped near the target distance
      const D = dir.y < -1e-3 ? Math.min((cam.y - target.y) / -dir.y, d * 1.3) : d * 1.3;
      const isOcc = (t: [number, number] | null, groundY: number) => {
        if (!t) return false; const [a, b] = t;
        return a < D * 0.35 && b < D * 0.5 && cam.y + dir.y * b > groundY + 1;    // passes through, well short of the target
      };
      for (let i = 0, n = city.recs.length; i < n; i++) {
        const r = recs[i]; if (r.hidden || !isAlive(r, year)) continue;
        const o = i * 6; if (B[o] === Infinity) continue;
        const cx = (B[o] + B[o + 3]) / 2, cz = (B[o + 2] + B[o + 5]) / 2;
        if (Math.abs(cx - cam.x) > D || Math.abs(cz - cam.z) > D) continue;          // cheap reject
        if (inBox(B[o], B[o + 1], B[o + 2], B[o + 3], B[o + 4], B[o + 5])) continue;   // the building being looked at
        if (isOcc(slab(cam, dir, [B[o], B[o + 1], B[o + 2]], [B[o + 3], B[o + 4], B[o + 5]]), B[o + 1])) hits.set(i, (hits.get(i) ?? 0) + (sx === 0 && sy === 0 ? 3 : 1));
      }
      for (const p of parts) {
        const w = p.whole ?? p.box;
        if (inBox(w.min.x, w.min.y, w.min.z, w.max.x, w.max.y, w.max.z)) continue;   // the landmark being looked at, whole
        if (!isOcc(slab(cam, dir, [p.box.min.x, p.box.min.y, p.box.min.z], [p.box.max.x, p.box.max.y, p.box.max.z]), p.box.min.y)) continue;
        // a big part (a whole stretch of wall) only fades if the ray really hits it that close
        const h = rc.intersectObject(p.obj, true)[0];
        if (h && h.distance < D * 0.35) occParts.add(p.obj);
      }
    }
    // a building goes only if the middle ray or at least three of the ring pass through it (a box grazed by one ray at the
    // edge of the screen is not in the way)
    for (const [i, n] of hits) if (n >= 3) occCity.add(i);
    // a landmark model goes whole: every part of the model the blocking part belongs to (not the city-wide walls)
    for (const o of [...occParts]) { const r = parts.find(q => q.obj === o)?.root; if (r) for (const q of parts) if (q.root === r) occParts.add(q.obj); }
    // a building stays a candidate for 0.8 s after its last hit: the ray tests flip on and off while the camera moves
    const now = performance.now();
    for (const i of occCity) seen.set(i, now);
    for (const [i, t] of seen) if (now - t > 800 && (weight.get(i) ?? 0) <= 0) seen.delete(i);
    // landmark parts: swap in invisible copies of their materials, put the originals back 0.8 s after they stop blocking
    for (const o of occParts) seenPart.set(o, now);
    for (const o of [...faded]) if (!occParts.has(o) && now - (seenPart.get(o) ?? 0) > 800) { restore(o); faded.delete(o); seenPart.delete(o); }
    for (const o of occParts) if (!faded.has(o)) { o.traverse((m: any) => { if (m.isMesh && !m.userData.preHide) { m.userData.preFade = m.material; m.material = fadeClone(m.material); } }); faded.add(o); }
  }
  const seen = new Map<number, number>(), weight = new Map<number, number>(), seenPart = new Map<THREE.Object3D, number>();
  /** A building goes at once while it blocks the view and comes back 0.8 s after it stops; fill the slots. */
  function ease(_dt: number, cam: THREE.Vector3) {
    const now = performance.now();
    for (const i of new Set([...seen.keys(), ...weight.keys()])) {
      if (now - (seen.get(i) ?? -1e9) <= 800) weight.set(i, 1); else weight.delete(i);
    }
    const ids = [...weight.keys()].sort((a, b) => Math.hypot(recs[a].c[0] - cam.x, recs[a].c[1] - cam.z) - Math.hypot(recs[b].c[0] - cam.x, recs[b].c[1] - cam.z));
    for (let k = 0; k < MAXOCC; k++) { uOcc[k].value = ids[k] ?? -1; uOccW[k].value = ids[k] != null ? weight.get(ids[k])! : 0; }
  }
  function clear() { for (let k = 0; k < MAXOCC; k++) { uOcc[k].value = -1; uOccW[k].value = 0; } seen.clear(); weight.clear(); seenPart.clear(); for (const o of faded) restore(o); faded.clear(); }

  /** Every frame. Works only near the ground: camera under ~30 m above the target, full at ~18 m. */
  function update(dt: number, year: number) {
    manualStep();
    const h = camera.position.y - target.y, d = camera.position.distanceTo(target);
    uXray.value = 1 - THREE.MathUtils.smoothstep(h, 18, 30);
    camera.getWorldDirection(uCamFwd.value);
    uXrayDepth.value = d * uCamFwd.value.dot(target.clone().sub(camera.position).normalize()) - Math.max(6, d * 0.08);
    if (uXray.value <= 0) { if (faded.size || uOcc[0].value >= 0) clear(); return; }
    ease(dt, camera.position);
    if ((acc += dt) < 0.15) return; acc = 0;
    scan(year);
  }
  // ---- hidden by hand (right click on a building seen up close): until the camera is 20 m further away than when it was
  // hidden (or 30 m, whichever is more), or rises 20 m over its top
  const manual: { kind: 'city' | 'obj'; i: number; obj?: THREE.Object3D; box: THREE.Box3; d0: number }[] = [];
  const tmpB = new THREE.Box3();
  function refreshMan() { for (let k = 0; k < MAXMAN; k++) uMan[k].value = manual.filter(m => m.kind === 'city')[k]?.i ?? -1; }
  function hideCity(i: number) {
    const o = i * 6; if (B[o] === Infinity || manual.some(m => m.kind === 'city' && m.i === i)) return;
    const box = new THREE.Box3(new THREE.Vector3(B[o], B[o + 1], B[o + 2]), new THREE.Vector3(B[o + 3], B[o + 4], B[o + 5]));
    if (manual.filter(m => m.kind === 'city').length >= MAXMAN) unhide(manual.find(m => m.kind === 'city')!);
    manual.push({ kind: 'city', i, box, d0: box.distanceToPoint(camera.position) }); refreshMan(); onChange?.(manual.length);
  }
  function hideObject(obj: THREE.Object3D) {
    if (manual.some(m => m.obj === obj)) return;
    obj.updateWorldMatrix(true, true); const box = tmpB.setFromObject(obj).clone();
    obj.traverse((m: any) => { if (m.isMesh) { m.userData.preHide = m.userData.preFade ?? m.material; m.userData.preFade = null; m.material = fadeClone(m.userData.preHide); } });
    manual.push({ kind: 'obj', i: -1, obj, box, d0: box.distanceToPoint(camera.position) }); onChange?.(manual.length);
  }
  function unhide(m: typeof manual[number]) {
    manual.splice(manual.indexOf(m), 1);
    if (m.obj) { m.obj.traverse((o: any) => { if (o.isMesh && o.userData.preHide) { o.material = o.userData.preHide; o.userData.preHide = null; } }); faded.delete(m.obj); }
    refreshMan(); onChange?.(manual.length);
  }
  function manualStep() {
    for (const m of [...manual]) {
      const far = m.box.distanceToPoint(camera.position) > Math.max(30, m.d0 + 20);
      const above = camera.position.y > m.box.max.y + 20;
      if (far || above) unhide(m);
    }
  }
  let onChange: ((n: number) => void) | null = null;
  return { update, clear, hideCity, hideObject, showAll: () => { for (const m of [...manual]) unhide(m); }, onHidden: (f: (n: number) => void) => (onChange = f), get hiddenCount() { return manual.length; } };
}
