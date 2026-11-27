// Crowd: animated figures walking the OSM street graph, filtered by era (walled city, castrum), plus static roles
// (vendors, customers, spectators, players, boatmen) requested by scenes. Bodies are the Mixamo "Xbot" figure;
// period clothes come from the Blender costume kit (blender/scripts/build_characters.py), skinned to the same
// skeleton so every animation drives them. Outfits by era and role; colours from the era palettes.
import * as THREE from 'three/webgpu';
import { walk } from './walk';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import * as SkeletonUtils from 'three/addons/utils/SkeletonUtils.js';
import { clothingFor } from '../data/history';

interface Graph { nodes: number[][]; edges: number[][]; zone: number[]; adj: number[][] }
type Role = 'walker' | 'static' | 'runner';
interface Agent {
  obj: THREE.Object3D; mixer: THREE.AnimationMixer; actions: Record<string, THREE.AnimationAction>; body: THREE.MeshStandardMaterial;
  skin: THREE.MeshStandardMaterial[]; bones: Record<string, THREE.Bone>; rig: THREE.Object3D; worn: Record<string, THREE.Mesh>; outfit: string;
  role: Role; a: number; b: number; t: number; len: number; speed: number; cur: string; target?: THREE.Vector3; busy: boolean; blockedN?: number;
  pose?: Pose; rod?: { g: THREE.Group; line: THREE.Line; tip: THREE.Vector3; waterY: number; ph: number };
}
/** Static poses layered on top of the idle clip (bones set after the mixer): seated, or holding a fishing rod. */
export type Pose = 'sit' | 'rod' | 'sitrod';
// Xbot / Mixamo rig in T-pose: thigh forward = UpLeg.x −90°, shin down = Leg.x +90°; arm forward = Arm.y ±, down = Arm.z ±
const POSE_BONES: Record<string, [string, number, number, number][]> = {
  sit: [['LeftUpLeg', -1.5, 0, -0.08], ['RightUpLeg', -1.5, 0, 0.08], ['LeftLeg', 1.45, 0, 0], ['RightLeg', 1.45, 0, 0]],
  rod: [['RightArm', 0, 1.3, 0.55], ['LeftArm', 0, -1.15, -0.5], ['RightForeArm', 0, 0.35, 0], ['LeftForeArm', 0, -0.55, 0]],
};
const rodMat = new THREE.MeshStandardMaterial({ color: 0x5a4630, roughness: 0.8 }), lineMat = new THREE.LineBasicMaterial({ color: 0xd8d4c8, transparent: true, opacity: 0.6 });
const tmp = new THREE.Vector3();
// outfits: garment / hat names from the costume kit
export const OUTFITS: Record<string, string[]> = {
  roman_m: ['g_tunic', 'g_boots'], roman_f: ['g_robe', 'g_bodice', 'h_hood'],
  medieval_m: ['g_tunic', 'g_hose', 'g_boots', 'h_hood'], medieval_f: ['g_skirt', 'g_bodice', 'h_hood'],
  renaissance_m: ['g_doublet', 'g_hose', 'g_boots', 'h_beret'], renaissance_elite: ['g_robe', 'g_doublet', 'h_beret'],
  renaissance_f: ['g_skirt', 'g_bodice'], early_modern_m: ['g_doublet', 'g_breeches', 'g_hose', 'g_boots', 'h_brim'],
  early_modern_f: ['g_skirt', 'g_bodice', 'g_apron'], c19_m: ['g_doublet', 'g_hose', 'g_boots', 'h_tophat'], c19_f: ['g_skirt', 'g_bodice'],
  modern_m: ['g_shirt', 'g_hose', 'g_boots'], modern_f: ['g_shirt', 'g_skirt', 'g_boots'],
  calcio_1530: ['g_doublet', 'g_breeches', 'g_hose'], calcio_modern: ['g_breeches', 'g_hose'],
  guard: ['g_doublet', 'g_hose', 'g_boots', 'h_helmet'], vendor: ['g_tunic', 'g_hose', 'g_apron', 'h_hood'],
  boatman: ['g_shirt', 'g_breeches'], fisher: ['g_shirt', 'g_breeches', 'h_brim'],
};
const SKIN = ['#e3b796', '#d6a47f', '#c99373', '#b98260', '#e8c2a3', '#a8714f'];
export function outfitFor(year: number, female: boolean, rich = false): string {
  if (year < 500) return female ? 'roman_f' : 'roman_m';
  if (year < 1400) return female ? 'medieval_f' : 'medieval_m';
  if (year < 1600) return female ? 'renaissance_f' : rich ? 'renaissance_elite' : 'renaissance_m';
  if (year < 1800) return female ? 'early_modern_f' : 'early_modern_m';
  if (year < 1945) return female ? 'c19_f' : 'c19_m';
  return female ? 'modern_f' : 'modern_m';
}

export async function createPeople(scene: THREE.Scene, streets: any, max = 200, opts: { walkers?: boolean } = {}) {
  const walkers = opts.walkers ?? true;
  const loader = new GLTFLoader();
  const [gltf, kit, hatKit] = await Promise.all([loader.loadAsync('./models/Xbot.glb'),
    loader.loadAsync('./models/costumes.glb').catch(() => null), loader.loadAsync('./models/hats.glb').catch(() => null)]);
  const garmentSrc: Record<string, THREE.SkinnedMesh> = {}, hatSrc: Record<string, THREE.Mesh> = {};
  kit?.scene.traverse((o: any) => { if (o.isSkinnedMesh) garmentSrc[o.name] = o; });
  hatKit?.scene.traverse((o: any) => { if (o.isMesh) hatSrc[o.name] = o; });
  const clips = Object.fromEntries(gltf.animations.map(c => [c.name, c]));
  const adj: number[][] = streets.nodes.map(() => []);
  for (const [a, b] of streets.edges) { adj[a].push(b); adj[b].push(a); }
  const G: Graph = { nodes: streets.nodes, edges: streets.edges, zone: streets.zone, adj };
  const group = new THREE.Group(); group.name = 'people'; scene.add(group);
  const agents: Agent[] = [];
  for (let i = 0; i < max; i++) {
    const obj = SkeletonUtils.clone(gltf.scene);
    let body: THREE.MeshStandardMaterial | null = null; const skin: THREE.MeshStandardMaterial[] = [];
    const bones: Record<string, THREE.Bone> = {}; let rig: THREE.Object3D = obj;
    obj.traverse((o: any) => {
      if (o.isBone) bones[o.name] = o;
      if (o.isMesh) {
        o.castShadow = true; o.frustumCulled = false;
        o.material = o.material.clone(); o.material.metalness = 0; o.material.roughness = 0.85; skin.push(o.material);
        if (!/Joints/i.test(o.material.name)) { body = o.material; rig = o.parent; }   // Xbot: 'Beta_Joints_MAT' + body
      }
    });
    const mixer = new THREE.AnimationMixer(obj);
    const actions: Record<string, THREE.AnimationAction> = {};
    for (const k of ['idle', 'walk', 'run', 'agree', 'headShake']) if (clips[k]) actions[k] = mixer.clipAction(clips[k]);
    obj.visible = false; group.add(obj);
    agents.push({ obj, mixer, actions, body: body!, skin, bones, rig, worn: {}, outfit: '', role: 'walker', a: 0, b: 0, t: 0, len: 1, speed: 1.3, cur: '', busy: false });
  }
  /** Bind a garment (skinned to the same Mixamo skeleton) or a hat (on the head) to an agent, once; then toggle. */
  function wear(ag: Agent, name: string): THREE.Mesh | null {
    if (ag.worn[name]) return ag.worn[name];
    if (name.startsWith('h_')) {
      const src = hatSrc[name], head = ag.bones['mixamorigHeadTop_End'] ?? ag.bones['mixamorigHead']; if (!src || !head) return null;
      const m = new THREE.Mesh(src.geometry, (src.material as THREE.MeshStandardMaterial).clone());
      ag.obj.updateMatrixWorld(true);
      const ws = new THREE.Vector3(), wq = new THREE.Quaternion(); head.getWorldScale(ws); head.getWorldQuaternion(wq);
      const oq = new THREE.Quaternion(); ag.obj.getWorldQuaternion(oq);
      m.scale.setScalar(ag.obj.scale.x / ws.x); m.quaternion.copy(wq.invert().multiply(oq));        // upright in the rest pose
      m.castShadow = true; head.add(m); ag.worn[name] = m; return m;
    }
    const src = garmentSrc[name]; if (!src) return null;
    const sk = new THREE.Skeleton(src.skeleton.bones.map(b => ag.bones[b.name]), src.skeleton.boneInverses);
    const m = new THREE.SkinnedMesh(src.geometry, (src.material as THREE.MeshStandardMaterial).clone());
    m.position.copy(src.position); m.quaternion.copy(src.quaternion); m.scale.copy(src.scale);
    m.bind(sk, src.bindMatrix); m.frustumCulled = false; m.castShadow = true;
    ag.rig.add(m); ag.worn[name] = m; return m;
  }
  /** Dress an agent: outfit by era/role, era palette for the main cloth, optional colour (team livery). */
  function dress(ag: Agent, outfit: string, color?: string) {
    const items = OUTFITS[outfit] ?? [];
    for (const [k, m] of Object.entries(ag.worn)) m.visible = items.includes(k);
    const pal = clothingFor(year), pick = () => pal[(Math.random() * pal.length) | 0];
    const main = new THREE.Color(color ?? pick()), alt = new THREE.Color(color && /calcio/.test(outfit) ? color : pick()).multiplyScalar(0.75);
    for (const it of items) {
      const m = wear(ag, it); if (!m) continue; m.visible = true;
      const mat = m.material as THREE.MeshStandardMaterial, slot = mat.name;
      if (slot === 'cloth_main') mat.color.copy(main); else if (slot === 'cloth_alt') mat.color.copy(alt);
      else if (slot === 'linen') mat.color.setHSL(0.1, 0.25, 0.78 + Math.random() * 0.1);
      else if (slot === 'leather') mat.color.setHSL(0.07, 0.4, 0.15 + Math.random() * 0.1);
    }
    ag.outfit = outfit;
    const s = new THREE.Color(SKIN[(Math.random() * SKIN.length) | 0]);
    for (const m of ag.skin) m.color.copy(Object.keys(garmentSrc).length ? s : new THREE.Color(color ?? pick()));
  }
  const play = (ag: Agent, name: string) => {
    if (ag.cur === name || !ag.actions[name]) return;
    ag.actions[ag.cur]?.fadeOut(0.25); ag.actions[name].reset().fadeIn(0.25).play(); ag.cur = name;
    ag.actions[name].time = Math.random() * ag.actions[name].getClip().duration;
  };
  let year = 1490, centre = new THREE.Vector3(), radius = 380, enabled = false;
  const minZone = () => (year < 1172 ? 2 : year < 1865 ? 1 : 0);
  const allowed = (n: number) => G.zone[n] >= minZone();
  const near: number[] = [];
  function refreshNear() {
    near.length = 0;
    G.nodes.forEach((p, i) => { if (allowed(i) && G.adj[i].length && Math.hypot(p[0] - centre.x, p[2] - centre.z) < radius) near.push(i); });
  }
  function place(ag: Agent) {
    if (!near.length) { ag.obj.visible = false; return; }
    for (let k = 0; k < 8; k++) {                       // start on an open stretch of street
      ag.a = near[(Math.random() * near.length) | 0]; nextEdge(ag);
      if (ag.b !== ag.a && edgeFree(ag.a, ag.b)) break;
    }
    ag.t = Math.random() * ag.len; ag.obj.visible = true;
  }
  /** An edge is walkable if no standing building, tree or prop sits on it (historic houses can stand on today's streets). */
  const edgeFree = (a: number, b: number) => { const A = G.nodes[a], B = G.nodes[b];
    for (const f of [0.25, 0.5, 0.75]) if (walk.blocked(A[0] + (B[0] - A[0]) * f, A[2] + (B[2] - A[2]) * f, 0.2)) return false; return true; };
  function nextEdge(ag: Agent) {
    const all = G.adj[ag.a].filter(allowed), free = all.filter(b => edgeFree(ag.a, b)), opts = free.length ? free : all;
    ag.b = opts.length ? opts[(Math.random() * opts.length) | 0] : ag.a;
    const A = G.nodes[ag.a], B = G.nodes[ag.b]; ag.len = Math.max(0.5, Math.hypot(B[0] - A[0], B[2] - A[2])); ag.t = 0;
  }
  function tint(ag: Agent, color?: string, outfit?: string) {
    dress(ag, outfit ?? outfitFor(year, Math.random() < 0.45, Math.random() < 0.12), color);
  }
  /** Re-seed walkers around the focus. Scene roles (busy agents) survive unless all = true. */
  function reset(all = false) {
    refreshNear();
    for (const ag of agents) {
      if (ag.busy && !all) continue;
      ag.busy = false; ag.role = 'walker'; ag.speed = 1.0 + Math.random() * 0.6; tint(ag); if (enabled && walkers && year >= -60) place(ag); else ag.obj.visible = false; play(ag, 'walk');
    }
  }
  /** Reserve an agent for a static/runner role at a position (used by event scenes). */
  function claim(pos: THREE.Vector3, face: THREE.Vector3, role: Role, anim: string, color?: string, outfit?: string, placed = false): Agent | null {
    const ag = agents.find(a => !a.busy); if (!ag) return null;
    if (!placed) {                                   // placed: the scene moves the figure itself every frame (a procession)
      const ok = walk.nearestFree(pos.x, pos.z, 6, 0.3, role !== 'static'); if (!ok) return null;   // never inside a wall or a trunk
      if (ok[0] !== pos.x || ok[1] !== pos.z) pos = pos.clone().set(ok[0], pos.y, ok[1]);
    }
    ag.busy = true; ag.role = role; ag.obj.visible = true; ag.obj.position.copy(pos); ag.obj.lookAt(face.x, pos.y, face.z);
    tint(ag, color, outfit); play(ag, anim); return ag;
  }
  function release(ag: Agent) { setPose(ag, null); ag.busy = false; ag.obj.visible = false; }
  /** Seat an agent (seat height = its position + 0.45 m: put the agent's position at ground level), and/or give it a rod
   *  whose line drops to waterY (world). The rod sways and now and then is lifted (a bite or a re-cast). */
  function setPose(ag: Agent, pose: Pose | null, waterY = 0) {
    ag.pose = pose ?? undefined;
    if (ag.rod) { ag.obj.remove(ag.rod.g); ag.rod = undefined; }
    if (!pose) { for (const k of ['LeftUpLeg', 'RightUpLeg', 'LeftLeg', 'RightLeg', 'RightArm', 'LeftArm', 'RightForeArm', 'LeftForeArm']) ag.bones['mixamorig' + k]?.rotation.set(0, 0, 0); return; }
    if (pose === 'rod' || pose === 'sitrod') {
      const g = new THREE.Group();                         // seated or not, the upper body keeps its height in the agent frame
      const hand = new THREE.Vector3(0.05, 1.12, 0.42), dir = new THREE.Vector3(0, 0.55, 1).normalize(), L = 3.4;
      const c = new THREE.Mesh(new THREE.CylinderGeometry(0.006, 0.016, L, 5), rodMat); c.castShadow = true;
      c.position.copy(hand).addScaledVector(dir, L / 2); c.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir); g.add(c);
      const tip = hand.clone().addScaledVector(dir, L);
      const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints([tip, tip.clone().setY(0)]), lineMat); line.frustumCulled = false; g.add(line);
      ag.obj.add(g); ag.rod = { g, line, tip, waterY, ph: Math.random() * 20 };
    }
  }
  const lift = new THREE.Vector3();
  function applyPose(ag: Agent, t: number) {
    const p = ag.pose!; const parts = p === 'sitrod' ? ['sit', 'rod'] : [p];
    for (const k of parts) for (const [n, x, y, z] of POSE_BONES[k]) ag.bones['mixamorig' + n]?.rotation.set(x, y, z);
    const r = ag.rod; if (!r) return;
    // sway, and every ~25 s a short lift of the rod tip (a bite, or pulling the line in to cast again)
    const ph = (t + r.ph) % 25, pull = ph < 1.6 ? Math.sin((ph / 1.6) * Math.PI) : 0;
    r.g.rotation.set(-pull * 0.35 + Math.sin(t * 0.7 + r.ph) * 0.02, Math.sin(t * 0.31 + r.ph) * 0.05, 0);
    r.g.updateMatrix(); lift.copy(r.tip).applyMatrix4(r.g.matrix);                 // tip in the agent's frame
    const wy = (r.waterY - ag.obj.position.y) / ag.obj.scale.y;                      // water level in the agent's frame
    const a = r.line.geometry.getAttribute('position') as THREE.BufferAttribute;
    a.setXYZ(0, r.tip.x, r.tip.y, r.tip.z); a.setXYZ(1, r.tip.x, r.tip.y - (lift.y - wy) - 0.02 + pull * 0.6, r.tip.z + 0.4); a.needsUpdate = true;
  }
  let clock = 0;
  function update(dt: number) {
    if (!enabled) return;
    clock += dt;
    for (const ag of agents) {
      ag.mixer.update(dt);
      if (!ag.obj.visible) continue;
      if (ag.pose) applyPose(ag, clock);
      if (ag.role === 'walker') {
        ag.t += ag.speed * dt;
        if (ag.t >= ag.len) { ag.a = ag.b; nextEdge(ag); if (Math.random() < 0.02) { place(ag); continue; } }
        const A = G.nodes[ag.a], B = G.nodes[ag.b], f = ag.t / ag.len;
        // keep to the right side of the street a little, so crowds do not all walk on the centre line
        const dx = B[0] - A[0], dz = B[2] - A[2], l = Math.hypot(dx, dz) || 1, off = 1.4;
        tmp.set(A[0] + dx * f - (dz / l) * off, A[1] + (B[1] - A[1]) * f, A[2] + dz * f + (dx / l) * off);
        if (walk.blocked(tmp.x, tmp.z, 0.25)) {           // too close to a wall or a stall: walk the middle, or turn back
          tmp.set(A[0] + dx * f, tmp.y, A[2] + dz * f);
          if (walk.blocked(tmp.x, tmp.z, 0.2)) {         // the street is built over in this year: start again elsewhere
            ag.blockedN = (ag.blockedN ?? 0) + 1;
            if (ag.blockedN > 2) { ag.blockedN = 0; place(ag); } else { const a0 = ag.a; ag.a = ag.b; ag.b = a0; ag.t = ag.len - ag.t; }
            continue;
          }
          ag.blockedN = 0;
        }
        ag.obj.position.copy(tmp); ag.obj.rotation.y = Math.atan2(dx, dz);
        if (Math.hypot(tmp.x - centre.x, tmp.z - centre.z) > radius * 1.15) place(ag);
      } else if (ag.role === 'runner' && ag.target) {
        const d = tmp.subVectors(ag.target, ag.obj.position); d.y = 0; const L = d.length();
        const pace = (ag as any).pace as number | undefined;                       // scenes may set a walking pace (m/s)
        if (L > 0.6) { d.multiplyScalar(Math.min(L, (pace ?? 5.5) * dt) / L); walk.steer(ag.obj.position, d); ag.obj.position.add(d); ag.obj.rotation.y = Math.atan2(d.x, d.z); play(ag, pace && pace < 2.5 ? 'walk' : 'run'); }
        else play(ag, 'idle');
      }
    }
  }
  return {
    group, claim, release, update, agents, setPose, anim: play,
    get year() { return year; },
    setEnabled(v: boolean) { const was = enabled; enabled = v; group.visible = v; if (v && !was) reset(true); },   // re-enabling must not drop scene crowds
    setContext(y: number, c: THREE.Vector3, r = 380) { const changed = Math.abs(y - year) >= 1 || c.distanceTo(centre) > 120; year = y; centre.copy(c); radius = r; if (changed && enabled) reset(); return changed; },
    reset,
  };
}
export type People = Awaited<ReturnType<typeof createPeople>>;
