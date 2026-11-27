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
  role: Role; a: number; b: number; t: number; len: number; speed: number; cur: string; target?: THREE.Vector3; busy: boolean; blockedN?: number; h?: number;   // h: the way the figure faces and walks (undefined: set it at once)
  female: boolean; face: THREE.Mesh[]; talk?: Talk; pose?: Pose; rod?: { g: THREE.Group; line: THREE.Line; tip: THREE.Vector3; waterY: number; ph: number };
}
/** Static poses layered on top of the idle clip (bones set after the mixer): seated, or holding a fishing rod. */
export type Pose = 'sit' | 'rod' | 'sitrod' | 'kneel';
// Xbot / Mixamo rig in T-pose: thigh forward = UpLeg.x −90°, shin down = Leg.x +90°; arm forward = Arm.y ±, down = Arm.z ±
const POSE_BONES: Record<string, [string, number, number, number][]> = {
  sit: [['LeftUpLeg', -1.5, 0, -0.08], ['RightUpLeg', -1.5, 0, 0.08], ['LeftLeg', 1.45, 0, 0], ['RightLeg', 1.45, 0, 0]],
  kneel: [['LeftUpLeg', -0.35, 0, -0.08], ['RightUpLeg', -0.35, 0, 0.08], ['LeftLeg', 1.9, 0, 0], ['RightLeg', 1.9, 0, 0],   // kneeling, leaning over the water
    ['Spine', 0.35, 0, 0], ['Spine1', 0.25, 0, 0], ['RightArm', 0, 1.0, 0.95], ['LeftArm', 0, -1.0, -0.95], ['RightForeArm', 0, 0.4, 0], ['LeftForeArm', 0, -0.4, 0]],
  rod: [['RightArm', 0, 1.3, 0.55], ['LeftArm', 0, -1.15, -0.5], ['RightForeArm', 0, 0.35, 0], ['LeftForeArm', 0, -0.55, 0]],
};
// Talking hands: arm poses from the T-pose (as POSE_BONES), blended over whatever clip plays. Florentines talk with their
// hands – regularly, not wildly: an open palm offered, both hands open, the pinched "mano a borsa" lifted and shaken,
// pointing, beats in time with the words, a shrug, a hand on the chest. Right-handed poses, mirrored at random.
type ArmPose = [string, number, number, number][];
// (axes checked on the figure: Arm z lowers the arm, Arm y swings it forward; ForeArm y bends the elbow, ForeArm z −
// swings the forearm out to the side; x only twists)
// (axes checked on the figure: Arm z lowers the arm, Arm y swings it forward; ForeArm y bends the elbow, ForeArm z −
// swings the forearm out to the side; x only twists)
const GESTURES: { arms: ArmPose; beat?: [string, number]; dur: [number, number] }[] = [
  { arms: [['RightArm', 0, 0.5, 1.0], ['RightForeArm', 0, 0.9, -0.8]], dur: [1.2, 2.2] },                                // open hand offered
  { arms: [['RightArm', 0, 0.5, 1.0], ['RightForeArm', 0, 0.9, -0.8], ['LeftArm', 0, -0.5, -1.0], ['LeftForeArm', 0, -0.9, 0.8]], dur: [1.2, 2.0] },   // both hands open
  { arms: [['RightArm', 0, 0.35, 1.15], ['RightForeArm', 0, 2.1, -0.2]], beat: ['RightForeArm', 0.25], dur: [1.0, 1.8] }, // mano a borsa, shaken
  { arms: [['RightArm', 0, 1.3, 0.35], ['RightForeArm', 0, 0.1, 0]], dur: [0.9, 1.5] },                                  // pointing
  { arms: [['RightArm', 0, 0.45, 1.1], ['RightForeArm', 0, 1.5, -0.4]], beat: ['RightForeArm', 0.3], dur: [1.4, 2.6] },  // beats in time with the words
  { arms: [['RightArm', 0, 0.25, 0.95], ['RightForeArm', 0, 0.7, -1.1], ['LeftArm', 0, -0.25, -0.95], ['LeftForeArm', 0, -0.7, 1.1]], dur: [0.8, 1.3] },   // shrug
  { arms: [['RightArm', 0, 0.3, 1.25], ['RightForeArm', 0, 2.4, 0.2]], dur: [1.2, 2.0] },                                 // hand on the chest
];
if (typeof location !== 'undefined' && location.hostname === 'localhost') (globalThis as any).__gest = GESTURES;   // dev: tune poses live
interface Talk { level: number; g: number; mirror: boolean; t: number; dur: number; rest: number; w: number }
const qT = new THREE.Quaternion(), eT = new THREE.Euler();
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
// Heads (Blender kit, hats.glb): face shapes, hair styles and beards; colours weighted for a Tuscan population (inferred)
const HAIR_COL: [string, number][] = [['#1b1714', 15], ['#2e2119', 38], ['#4a3324', 22], ['#6b4128', 8], ['#7d3b22', 3], ['#8c6a43', 6], ['#b8935b', 2], ['#8d8a86', 5], ['#cfccc6', 1]];
const IRIS = ['#2a1a10', '#2a1a10', '#3b2414', '#3b2414', '#4d3a1e', '#55603a', '#3e5a74'];
const pickW = <T,>(l: [T, number][]) => { let r = Math.random() * l.reduce((a, b) => a + b[1], 0); for (const [v, w] of l) if ((r -= w) <= 0) return v; return l[0][0]; };
/** Hair and beard for a person of this era and sex (period fashions from portraits; shares *inferred*). */
export function headFor(year: number, female: boolean): { hair: string; beard: string | null } {
  const H = (l: [string, number][]) => pickW(l);
  if (female) {
    if (year < 500) return { hair: H([['hair_bun', 6], ['hair_long', 2]]), beard: null };
    if (year < 1900) return { hair: H([['hair_bun', 5], ['hair_long', 4], ['hair_bob', year < 1400 ? 0 : 1]]), beard: null };
    return { hair: H([['hair_long', 4], ['hair_bob', 3], ['hair_bun', 2], ['hair_short', 1], ['hair_curly', 1]]), beard: null };
  }
  let hair: string, beard: [string | null, number][];
  if (year < 500) { hair = H([['hair_crop', 4], ['hair_short', 3], ['hair_curly', 3]]); beard = [[null, 7], ['beard_short', 2], ['beard_full', 1]]; }
  else if (year < 1400) { hair = H([['hair_bob', 4], ['hair_short', 4], ['hair_crop', 2]]); beard = [[null, 5], ['beard_full', 3], ['beard_short', 2]]; }
  else if (year < 1600) { hair = H([['hair_bob', 4], ['hair_short', 4], ['hair_curly', 2]]); beard = year < 1520 ? [[null, 9], ['beard_short', 1]] : [[null, 5], ['beard_full', 3], ['beard_short', 2]]; }
  else if (year < 1800) { hair = H(year >= 1680 ? [['hair_long', 5], ['hair_short', 3], ['hair_bob', 2]] : [['hair_bob', 4], ['hair_short', 4], ['hair_long', 2]]); beard = year < 1660 ? [[null, 6], ['beard_moustache', 2], ['beard_short', 2]] : [[null, 9], ['beard_moustache', 1]]; }
  else if (year < 1945) { hair = H([['hair_short', 5], ['hair_crop', 3], ['hair_balding', 2]]); beard = [[null, 4], ['beard_moustache', 3], ['beard_full', 2], ['beard_short', 1]]; }
  else { hair = H([['hair_crop', 4], ['hair_short', 4], ['hair_curly', 1], ['hair_balding', 1]]); beard = [[null, 7], ['beard_short', 2], ['beard_full', 1]]; }
  return { hair, beard: pickW(beard) };
}
const HEAD_ITEM = /^(h|f|hair|beard)_/;
export function outfitFor(year: number, female: boolean, rich = false): string {
  if (year < 500) return female ? 'roman_f' : 'roman_m';
  if (year < 1400) return female ? 'medieval_f' : 'medieval_m';
  if (year < 1600) return female ? 'renaissance_f' : rich ? 'renaissance_elite' : 'renaissance_m';
  if (year < 1800) return female ? 'early_modern_f' : 'early_modern_m';
  if (year < 1945) return female ? 'c19_f' : 'c19_m';
  return female ? 'modern_f' : 'modern_m';
}

/** Camera height over the view's target above which no people are drawn (they would be a few pixels; boats stay longer). */
export const PEOPLE_ALT = 340;
/** A crowd. `base`: walkers on the streets round the view when the camera is down at street level (fewer as it rises,
 *  none above PEOPLE_ALT). Figures are made on demand – for walkers and for whatever scenes, squares and the river ask
 *  for in the area in view – and reused; `cap` is only a safety limit. */
export async function createPeople(scene: THREE.Scene, streets: any, base = 200, opts: { walkers?: boolean; cap?: number } = {}) {
  const walkers = opts.walkers ?? true, cap = opts.cap ?? 600;
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
  function makeAgent(): Agent | null {
    if (agents.length >= cap) return null;
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
    const ag: Agent = { obj, mixer, actions, body: body!, skin, bones, rig, worn: {}, outfit: '', female: false, face: [], role: 'walker', a: 0, b: 0, t: 0, len: 1, speed: 1.3, cur: '', busy: false };
    agents.push(ag); return ag;
  }
  /** Bind a garment (skinned to the same Mixamo skeleton) or a hat (on the head) to an agent, once; then toggle. */
  function wear(ag: Agent, name: string): THREE.Mesh | null {
    if (ag.worn[name]) return ag.worn[name];
    if (HEAD_ITEM.test(name)) {
      const src = hatSrc[name], head = ag.bones['mixamorigHeadTop_End'] ?? ag.bones['mixamorigHead']; if (!src || !head) return null;
      const m = new THREE.Mesh(src.geometry, (src.material as THREE.MeshStandardMaterial).clone());
      if (name.startsWith('h_')) (m.material as THREE.Material).side = THREE.DoubleSide;   // hoods and helmets are open at the face
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
    ag.female = /_f$|^roman_f/.test(outfit);
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
    // head: one of three face shapes, eyes, lips, brows; hair and beard by era and sex; a veil, hood or helmet hides the hair
    if (!hatSrc['f_face0']) return;
    const hd = headFor(year, ag.female), covered = items.includes('h_hood') || items.includes('h_helmet');
    const hc = new THREE.Color(pickW(HAIR_COL)); if (Math.random() < 0.3) hc.offsetHSL(0, -0.05, (Math.random() - 0.5) * 0.06);
    ag.face = [];
    for (const k of [`f_face${(Math.random() * 3) | 0}`, 'f_eyes', 'f_iris', 'f_lips', 'f_brows', covered ? '' : hd.hair, hd.beard ?? '']) {
      if (!k) continue; const m = wear(ag, k); if (!m) continue; m.visible = true;
      const mat = m.material as THREE.MeshStandardMaterial;
      if (mat.name === 'skin') { mat.color.copy(s); m.scale.set(0.94 + Math.random() * 0.14, 1, 0.95 + Math.random() * 0.1); }
      else if (mat.name === 'hair') mat.color.copy(hc);
      else if (mat.name === 'iris') mat.color.set(IRIS[(Math.random() * IRIS.length) | 0]);
      else if (mat.name === 'lips') mat.color.copy(s).lerp(new THREE.Color(ag.female ? '#9c4a46' : '#8a5048'), ag.female ? 0.45 : 0.3);
      if (k.startsWith('f_')) ag.face.push(m);
    }
  }
  const play = (ag: Agent, name: string) => {
    if (ag.cur === name || !ag.actions[name]) return;
    ag.actions[ag.cur]?.fadeOut(0.25); ag.actions[name].reset().fadeIn(0.25).play(); ag.cur = name;
    ag.actions[name].time = Math.random() * ag.actions[name].getClip().duration;
  };
  let year = 1490, centre = new THREE.Vector3(), radius = 380, enabled = false, epoch = 0;
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
    ag.t = Math.random() * ag.len; ag.obj.visible = true; ag.h = undefined;
  }
  /** An edge is walkable if no standing building, tree or prop sits on it (historic houses can stand on today's streets). */
  const edgeFree = (a: number, b: number) => { const A = G.nodes[a], B = G.nodes[b];
    for (const f of [0.25, 0.5, 0.75]) if (walk.blocked(A[0] + (B[0] - A[0]) * f, A[2] + (B[2] - A[2]) * f, 0.2)) return false; return true; };
  function nextEdge(ag: Agent, from = -1) {
    const all = G.adj[ag.a].filter(allowed), free0 = all.filter(b => edgeFree(ag.a, b));
    const free = free0.length > 1 ? free0.filter(b => b !== from) : free0, opts = free.length ? free : all;   // go on, not back (unless a dead end)
    ag.b = opts.length ? opts[(Math.random() * opts.length) | 0] : ag.a;
    const A = G.nodes[ag.a], B = G.nodes[ag.b]; ag.len = Math.max(0.5, Math.hypot(B[0] - A[0], B[2] - A[2])); ag.t = 0;
  }
  function tint(ag: Agent, color?: string, outfit?: string) {
    dress(ag, outfit ?? outfitFor(year, Math.random() < 0.45, Math.random() < 0.12), color);
  }
  /** Re-seed walkers around the focus. Scene roles (busy agents) survive unless all = true. */
  function reset(all = false) {
    if (all) epoch++;                                   // scene-held figures were taken back
    refreshNear();
    for (const ag of agents) {
      if (ag.busy && !all) continue;
      if (ag.busy) setPose(ag, null);
      ag.busy = false; ag.role = 'walker'; ag.obj.visible = false;      // walkers come back round the new focus in fill()
    }
  }
  /** Bring the walkers round the view to the number wanted at this camera height: reuse hidden figures first, make new
   *  ones a few a frame (a clone and its clothes cost a little), hide the extra ones. */
  let alt = 0;
  function walkerWant() {
    if (!walkers || !enabled || year < -60) return 0;
    const k = alt < 70 ? 1 : Math.max(0, Math.min(1, (PEOPLE_ALT - alt) / (PEOPLE_ALT - 70)));
    return Math.round(base * k);
  }
  function startWalker(ag: Agent) {
    ag.role = 'walker'; ag.speed = 1.0 + Math.random() * 0.6; tint(ag); play(ag, 'walk'); place(ag);
  }
  function fill() {
    const want = walkerWant();
    let active = 0; for (const ag of agents) if (!ag.busy && ag.obj.visible) active++;
    if (active > want) {
      for (let i = agents.length - 1; i >= 0 && active > want; i--) { const ag = agents[i]; if (!ag.busy && ag.obj.visible) { ag.obj.visible = false; active--; } }
      return;
    }
    let reuse = 30, make = 5;
    for (const ag of agents) { if (active >= want || !reuse) break; if (!ag.busy && !ag.obj.visible) { startWalker(ag); if (ag.obj.visible) active++; reuse--; } }
    while (active < want && make-- > 0) { const ag = makeAgent(); if (!ag) break; startWalker(ag); if (ag.obj.visible) active++; }
  }
  /** Reserve an agent for a static/runner role at a position (used by event scenes). */
  function claim(pos: THREE.Vector3, face: THREE.Vector3, role: Role, anim: string, color?: string, outfit?: string, placed = false): Agent | null {
    const ag = agents.find(a => !a.busy && !a.obj.visible) ?? agents.find(a => !a.busy) ?? makeAgent(); if (!ag) return null;
    if (!placed) {                                   // placed: the scene moves the figure itself every frame (a procession)
      const ok = walk.nearestFree(pos.x, pos.z, 6, 0.3, role !== 'static'); if (!ok) return null;   // never inside a wall or a trunk
      if (ok[0] !== pos.x || ok[1] !== pos.z) pos = pos.clone().set(ok[0], pos.y, ok[1]);
    }
    ag.busy = true; ag.role = role; ag.obj.visible = true; ag.obj.position.copy(pos); ag.obj.lookAt(face.x, pos.y, face.z); ag.h = undefined;
    tint(ag, color, outfit); play(ag, anim); return ag;
  }
  function release(ag: Agent) { setPose(ag, null); ag.talk = undefined; ag.busy = false; ag.obj.visible = false; }
  /** Seat an agent (seat height = its position + 0.45 m: put the agent's position at ground level), and/or give it a rod
   *  whose line drops to waterY (world). The rod sways and now and then is lifted (a bite or a re-cast). */
  function setPose(ag: Agent, pose: Pose | null, waterY = 0) {
    ag.pose = pose ?? undefined;
    if (ag.rod) { ag.obj.remove(ag.rod.g); ag.rod = undefined; }
    if (!pose) { for (const k of ['LeftUpLeg', 'RightUpLeg', 'LeftLeg', 'RightLeg', 'RightArm', 'LeftArm', 'RightForeArm', 'LeftForeArm', 'Spine', 'Spine1']) ag.bones['mixamorig' + k]?.rotation.set(0, 0, 0); return; }
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
  /** level 1: speaking (gestures often), 0.3: listening (now and then), 0: still hands. */
  function setTalk(ag: Agent, level: number) {
    if (level <= 0) { ag.talk = undefined; return; }
    if (ag.talk) { ag.talk.level = level; return; }
    ag.talk = { level, g: 0, mirror: false, t: 0, dur: 0, rest: Math.random() * 1.5, w: 0 };
  }
  function gesture(ag: Agent, dt: number) {
    const k = ag.talk!;
    if (k.dur <= 0) {                                    // resting between gestures
      k.w = Math.max(0, k.w - dt * 3);
      if ((k.rest -= dt) <= 0) {
        if (Math.random() < 0.35 + 0.6 * k.level) {
          k.g = (Math.random() * GESTURES.length) | 0; k.mirror = Math.random() < 0.35;
          const d = GESTURES[k.g].dur; k.dur = d[0] + Math.random() * (d[1] - d[0]); k.t = 0;
        }
        k.rest = (k.level >= 1 ? 0.4 : 2.0) + Math.random() * (k.level >= 1 ? 1.4 : 4.0);
      }
    } else {
      k.t += dt; k.w = Math.min(1, k.t / 0.35, (k.dur - k.t) / 0.35 + 0.0001); if (k.t >= k.dur) { k.dur = 0; }
    }
    if (k.w <= 0.001) return;
    const G = GESTURES[k.g], amp = k.level >= 1 ? 1 : 0.6;
    for (const [n, x, y, z] of G.arms) {
      let name = n, yy = y * amp, zz = z, xx = x;
      if (k.mirror) { name = n.startsWith('Right') ? 'Left' + n.slice(5) : 'Right' + n.slice(4); yy = -yy; zz = -zz; }
      if (G.beat && n === G.beat[0]) yy += (k.mirror ? -1 : 1) * G.beat[1] * Math.sin(k.t * 9);
      const b = ag.bones['mixamorig' + name]; if (!b) continue;
      qT.setFromEuler(eT.set(xx, yy, zz)); b.quaternion.slerp(qT, k.w);
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
  /** People only ever walk forwards: the heading turns towards where they are going at a limited rate (a tight curve), and
   *  they slow down while the turn is sharp – a U-turn is a quick turn on the spot, never a step backwards. */
  const TURN = 5;                                           // rad/s
  const mv = new THREE.Vector3();
  function turnMove(ag: Agent, want: number, step: number, dt: number, steer = false) {
    if (ag.h === undefined) ag.h = want;
    let da = want - ag.h; da = Math.atan2(Math.sin(da), Math.cos(da));
    ag.h += Math.sign(da) * Math.min(Math.abs(da), TURN * dt);
    const k = Math.max(0.12, Math.cos(Math.min(Math.abs(da), Math.PI / 2)));   // sharp turn: small steps while turning
    mv.set(Math.sin(ag.h), 0, Math.cos(ag.h)).multiplyScalar(step * k);
    if (steer) walk.steer(ag.obj.position, mv);
    ag.obj.position.add(mv); ag.obj.rotation.y = ag.h;
  }
  /** A walker follows its point on the street; a jump (just placed elsewhere) is taken at once. */
  function follow(ag: Agent, p: THREE.Vector3, speed: number, dt: number, edgeH: number) {
    const dx = p.x - ag.obj.position.x, dz = p.z - ag.obj.position.z, L = Math.hypot(dx, dz);
    if (ag.h === undefined || L > 6) { ag.obj.position.copy(p); ag.h = edgeH; ag.obj.rotation.y = edgeH; return; }
    if (L > 0.05) turnMove(ag, Math.atan2(dx, dz), Math.min(L, speed * dt), dt);
    ag.obj.position.y = p.y;
  }
  let clock = 0, lodT = 0;
  const eye = new THREE.Vector3(1e9, 0, 0);
  function update(dt: number, cam?: THREE.Vector3) {
    if (!enabled) return;
    clock += dt;
    if (cam) {
      eye.copy(cam); alt = cam.y - centre.y;
      const r = Math.max(160, Math.min(380, 140 + alt * 1.6));          // walkers close round the view when the camera is low
      if (walkers && Math.abs(r - radius) > 40) { radius = r; refreshNear(); }
    }
    group.visible = alt < PEOPLE_ALT;                     // too high to see anyone: draw and animate nobody
    if (!group.visible) return;
    fill();
    if ((lodT -= dt) <= 0) {                             // small facial features only near the camera (draw calls)
      lodT = 0.4;
      for (const ag of agents) if (ag.obj.visible) { const near = ag.obj.position.distanceToSquared(eye) < 60 * 60; for (const m of ag.face) m.visible = near; }
    }
    for (const ag of agents) {
      if (!ag.obj.visible) continue;
      ag.mixer.update(dt);
      if (ag.talk && !ag.pose) gesture(ag, dt);
      if (ag.pose) applyPose(ag, clock);
      if (ag.role === 'walker') {
        ag.t += ag.speed * dt;
        if (ag.t >= ag.len) { const prev = ag.a; ag.a = ag.b; nextEdge(ag, prev); if (Math.random() < 0.02) { place(ag); continue; } }
        const A = G.nodes[ag.a], B = G.nodes[ag.b], f = ag.t / ag.len;
        // keep to the right side of the street a little, so crowds do not all walk on the centre line
        const dx = B[0] - A[0], dz = B[2] - A[2], l = Math.hypot(dx, dz) || 1, off = 1.4;
        const fa = Math.min(1, f + 0.9 / l);                // the point followed: a step ahead on the street
        tmp.set(A[0] + dx * fa - (dz / l) * off, A[1] + (B[1] - A[1]) * f, A[2] + dz * fa + (dx / l) * off);
        if (walk.blocked(tmp.x, tmp.z, 0.25)) {           // too close to a wall or a stall: walk the middle, or turn back
          tmp.set(A[0] + dx * f, tmp.y, A[2] + dz * f);
          if (walk.blocked(tmp.x, tmp.z, 0.2)) {         // the street is built over in this year: start again elsewhere
            ag.blockedN = (ag.blockedN ?? 0) + 1;
            if (ag.blockedN > 2) { ag.blockedN = 0; place(ag); } else { const a0 = ag.a; ag.a = ag.b; ag.b = a0; ag.t = ag.len - ag.t; }
            continue;
          }
          ag.blockedN = 0;
        }
        follow(ag, tmp, ag.speed * 1.25, dt, Math.atan2(dx, dz));
        if (Math.hypot(tmp.x - centre.x, tmp.z - centre.z) > radius * 1.15) place(ag);
      } else if (ag.role === 'runner' && ag.target) {
        const d = tmp.subVectors(ag.target, ag.obj.position); d.y = 0; const L = d.length();
        const pace = (ag as any).pace as number | undefined;                       // scenes may set a walking pace (m/s)
        if (L > 0.6) { turnMove(ag, Math.atan2(d.x, d.z), Math.min(L, (pace ?? 5.5) * dt), dt, true); play(ag, pace && pace < 2.5 ? 'walk' : 'run'); }
        else play(ag, 'idle');
      }
    }
  }
  return {
    group, claim, release, update, agents, setPose, setTalk, anim: play,
    get year() { return year; }, get epoch() { return epoch; },
    setVisible(v: boolean) { if (!v) group.visible = false; },   // hidden for a moment (the timeline playing); update() shows them again
    setEnabled(v: boolean) { const was = enabled; enabled = v; if (!v) group.visible = false; if (v && !was) reset(true); },   // re-enabling must not drop scene crowds
    setContext(y: number, c: THREE.Vector3, _r = 380) { const changed = Math.abs(y - year) >= 1 || c.distanceTo(centre) > 120; year = y; centre.copy(c); if (changed && enabled) reset(); return changed; },
    get made() { return agents.length; },
    reset,
  };
}
export type People = Awaited<ReturnType<typeof createPeople>>;
