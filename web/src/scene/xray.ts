// "X-ray" for close views near the ground: a building that stands between the camera and the point being looked at
// (controls.target) fades out with a screen-door dither, inside a soft disc round the middle of the screen. Nothing fades
// just because it is in front of the camera: a few rays from the camera through the middle of the screen look for
// structures they pass right through, well short of the target (entering in the first 45 %, leaving before 65 % of the
// way, above their own ground). Those, and only those, fade: city buildings by record id, landmark parts by object.
import * as THREE from 'three/webgpu';
import { Fn, uniform, positionWorld, cameraPosition, dot, smoothstep, screenUV, screenSize, screenCoordinate, vec2, length, floor, float, abs } from 'three/tsl';
import { isAlive, type Rec } from './city';

export const uXray = uniform(0);                                  // 0 off … 1 full (camera height near the ground)
export const uXrayDepth = uniform(0);                             // view depth of the target minus a margin
export const uCamFwd = uniform(new THREE.Vector3(0, 0, -1));      // camera forward (world)
const MAXOCC = 12;
const uOcc = Array.from({ length: MAXOCC }, () => uniform(-1));   // record ids of the city buildings that fade
const uOccW = Array.from({ length: MAXOCC }, () => uniform(0));   // and how far each has faded (eased: no popping, no flicker)

const fadeAmount = Fn(() => {
  const depth = dot(positionWorld.sub(cameraPosition), uCamFwd);
  const c = screenUV.sub(0.5).mul(vec2(screenSize.x.div(screenSize.y), 1));
  const inFront = float(1).sub(smoothstep(uXrayDepth.sub(8), uXrayDepth, depth));
  const centre = float(1).sub(smoothstep(float(0.3), float(0.65), length(c)));
  return inFront.mul(centre).mul(uXray).mul(0.9);
});
// ordered (Bayer 4×4) dither: an even screen-door pattern that reads as transparency; white-noise dither sparkled as the
// fade eased in and out while the camera moved
const dither = Fn(() => {
  const p = floor(screenCoordinate.xy);
  const x0 = p.x.mod(2), y0 = p.y.mod(2), x1 = floor(p.x.div(2)).mod(2), y1 = floor(p.y.div(2)).mod(2);
  const m0 = abs(x0.sub(y0)).mul(2).add(y0), m1 = abs(x1.sub(y1)).mul(2).add(y1);
  return m0.mul(4).add(m1).add(0.5).div(16);
});

/** City mask: keep the fragment unless its building is one of the current occluders. */
export function cityKeep(bid: any) {
  return Fn(() => {
    let w: any = abs(bid.sub(uOcc[0])).lessThan(0.5).select(uOccW[0], float(0));
    for (let i = 1; i < MAXOCC; i++) w = w.add(abs(bid.sub(uOcc[i])).lessThan(0.5).select(uOccW[i], float(0)));
    return (dither() as any).greaterThanEqual((fadeAmount() as any).mul(w));
  })();
}
/** Mask for landmark materials while their part is an occluder (swapped in, see below). */
const landmarkKeep = Fn(() => (dither() as any).greaterThanEqual(fadeAmount() as any));
const fadeClones = new WeakMap<THREE.Material, THREE.Material>();
function fadeClone(m: THREE.Material) {
  let c = fadeClones.get(m);
  if (!c) { c = m.clone(); (c as any).maskNode = landmarkKeep(); fadeClones.set(m, c); }
  return c;
}

export interface LandmarkPart { obj: THREE.Object3D; box: THREE.Box3 }

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
  const faded = new Set<THREE.Object3D>();
  // rays: the middle of the screen and a ring of 8 round it
  const SAMPLES: [number, number][] = [[0, 0], ...Array.from({ length: 8 }, (_, k) => [Math.cos(k * Math.PI / 4) * 0.28, Math.sin(k * Math.PI / 4) * 0.4] as [number, number])];
  let acc = 0;
  const restore = (o: THREE.Object3D) => o.traverse((m: any) => { if (m.isMesh && m.userData.preFade) { m.material = m.userData.preFade; m.userData.preFade = null; } });

  function scan(year: number) {
    occCity.clear(); occParts.clear();
    const d = camera.position.distanceTo(target), cam = camera.position;
    const parts = landmarkParts();
    for (const [sx, sy] of SAMPLES) {
      ndc.set(sx, sy); rc.setFromCamera(ndc, camera); const dir = rc.ray.direction;
      // how far this ray has to go to reach what is being looked at: the target's level, capped near the target distance
      const D = dir.y < -1e-3 ? Math.min((cam.y - target.y) / -dir.y, d * 1.3) : d * 1.3;
      const isOcc = (t: [number, number] | null, groundY: number) => {
        if (!t) return false; const [a, b] = t;
        return a < D * 0.45 && b < D * 0.65 && cam.y + dir.y * b > groundY + 1;   // passes through, well short of the target
      };
      for (let i = 0, n = city.recs.length; i < n; i++) {
        const r = recs[i]; if (r.hidden || !isAlive(r, year)) continue;
        const o = i * 6; if (B[o] === Infinity) continue;
        const cx = (B[o] + B[o + 3]) / 2, cz = (B[o + 2] + B[o + 5]) / 2;
        if (Math.abs(cx - cam.x) > D || Math.abs(cz - cam.z) > D) continue;          // cheap reject
        if (isOcc(slab(cam, dir, [B[o], B[o + 1], B[o + 2]], [B[o + 3], B[o + 4], B[o + 5]]), B[o + 1])) occCity.add(i);
      }
      for (const p of parts) {
        if (!isOcc(slab(cam, dir, [p.box.min.x, p.box.min.y, p.box.min.z], [p.box.max.x, p.box.max.y, p.box.max.z]), p.box.min.y)) continue;
        // a big part (a whole stretch of wall) only fades if the ray really hits it that close
        const h = rc.intersectObject(p.obj, true)[0];
        if (h && h.distance < D * 0.45) occParts.add(p.obj);
      }
    }
    // a building stays a candidate for 0.8 s after its last hit: the ray tests flip on and off while the camera moves
    const now = performance.now();
    for (const i of occCity) seen.set(i, now);
    for (const [i, t] of seen) if (now - t > 800 && (weight.get(i) ?? 0) <= 0) seen.delete(i);
    // landmark parts: swap in the fading copy of their materials, put the originals back when they stop blocking
    for (const o of [...faded]) if (!occParts.has(o)) { restore(o); faded.delete(o); }
    for (const o of occParts) if (!faded.has(o)) { o.traverse((m: any) => { if (m.isMesh) { m.userData.preFade = m.material; m.material = fadeClone(m.material); } }); faded.add(o); }
  }
  const seen = new Map<number, number>(), weight = new Map<number, number>();
  /** Ease each building's fade towards 1 while it blocks the view, back to 0 when it stops (≈0.3 s), and fill the slots. */
  function ease(dt: number, cam: THREE.Vector3) {
    const now = performance.now();
    for (const i of new Set([...seen.keys(), ...weight.keys()])) {
      const on = now - (seen.get(i) ?? -1e9) <= 800, w = (weight.get(i) ?? 0) + (on ? dt : -dt) * 3.5;
      if (w <= 0) weight.delete(i); else weight.set(i, Math.min(1, w));
    }
    const ids = [...weight.keys()].sort((a, b) => Math.hypot(recs[a].c[0] - cam.x, recs[a].c[1] - cam.z) - Math.hypot(recs[b].c[0] - cam.x, recs[b].c[1] - cam.z));
    for (let k = 0; k < MAXOCC; k++) { uOcc[k].value = ids[k] ?? -1; uOccW[k].value = ids[k] != null ? weight.get(ids[k])! : 0; }
  }
  function clear() { for (let k = 0; k < MAXOCC; k++) { uOcc[k].value = -1; uOccW[k].value = 0; } seen.clear(); weight.clear(); for (const o of faded) restore(o); faded.clear(); }

  /** Every frame. Works only near the ground: camera under ~45 m above the target, full at ~25 m. */
  function update(dt: number, year: number) {
    const h = camera.position.y - target.y, d = camera.position.distanceTo(target);
    uXray.value = 1 - THREE.MathUtils.smoothstep(h, 25, 45);
    camera.getWorldDirection(uCamFwd.value);
    uXrayDepth.value = d * uCamFwd.value.dot(target.clone().sub(camera.position).normalize()) - Math.max(6, d * 0.08);
    if (uXray.value <= 0) { if (faded.size || uOcc[0].value >= 0) clear(); return; }
    ease(dt, camera.position);
    if ((acc += dt) < 0.15) return; acc = 0;
    scan(year);
  }
  return { update, clear };
}
