// Landscape: core terrain (LiDAR) + 12 km ring (Copernicus), ground by era (fields, meadows, earth, paving, today's
// surfaces), the Arno with its reaches and pescaie, dated bridge phases, vegetation that disappears when the ground
// gets built on. Everything year-dependent is decided on the GPU from uYear.
import * as THREE from 'three/webgpu';
import {
  Fn, uniform, texture, vec2, vec3, vec4, mix, positionWorld, positionLocal, dot, select, float, smoothstep, hash, fract, step,
  floor, sin, abs, max, length, attribute, cameraPosition, normalize, pow, instanceIndex, transformNormalToView,
} from 'three/tsl';
import { uYear, uSky } from './city';
export { uSky };
import type { TexSet } from './assets';
import { buildBridge, mergeBridge, bridgeMaterials, specFor } from './bridges';

export const uOverlayOpacity = uniform(0);
export const uTime = uniform(0);

const bin = async (u: string, T: any): Promise<any> => new T(await (await fetch(u)).arrayBuffer());

/** Value noise 0..1 (cheap, GPU). */
const noise2: any = Fn(([p]: any) => {
  const i: any = floor(p), f: any = fract(p), u = f.mul(f).mul(float(3).sub(f.mul(2)));
  const a = hash(i.x.add(i.y.mul(57))), b = hash(i.x.add(1).add(i.y.mul(57))), c = hash(i.x.add(i.y.add(1).mul(57))), d = hash(i.x.add(1).add(i.y.add(1).mul(57)));
  return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
});
const fbm = (p: any): any => noise2(p).mul(0.55).add(noise2(p.mul(2.03)).mul(0.3)).add(noise2(p.mul(4.1)).mul(0.15));

export async function loadEnvironment(base: string, meta: any, ortho: THREE.Texture, blank: THREE.Texture, tex: TexSet, opts: { treeShare?: number; anisotropy?: number } = {}) {
  const group = new THREE.Group();
  const coreHalf = ((meta.terrain.n - 1) * meta.terrain.step) / 2;           // 1000 m
  const W = meta.wide, wideHalf = W.half;
  const land = await new THREE.TextureLoader().loadAsync(`${base}/${W.land}`);
  land.colorSpace = THREE.SRGBColorSpace; land.flipY = false; land.anisotropy = opts.anisotropy ?? 8;
  // urban raster: first year something stood in each 8 m cell of the core
  const U = meta.urban;
  const urbanTex = new THREE.DataTexture(await bin(`${base}/urban.f32`, Float32Array), U.n, U.n, THREE.RedFormat, THREE.FloatType);
  urbanTex.needsUpdate = true; urbanTex.minFilter = urbanTex.magFilter = THREE.NearestFilter;
  // yards: open ground inside the blocks (not street, not building), 4 m cells – a garden where the 2017 orthophoto is green
  const Y = meta.yards;
  const yardTex = Y ? new THREE.DataTexture(await bin(`${base}/yards.u8`, Uint8Array), Y.n, Y.n, THREE.RedFormat, THREE.UnsignedByteType) : blank;
  if (Y) { yardTex.needsUpdate = true; yardTex.minFilter = yardTex.magFilter = THREE.LinearFilter; }
  const ovTex = texture(blank);   // swapped at runtime via ovTex.value

  // ---------- ground colour (shared by the core and the wide ring) ----------
  const ground = Fn(() => {
    const P = positionWorld.xz;
    // the sharp orthophoto fades into the 10 m Sentinel-2 land cover over a wide, wobbly ring, not along the square edge
    // of the orthophoto tile (which read as a lit rectangle on the map from far away)
    const sq = step(abs(P.x), coreHalf - 1).mul(step(abs(P.y), coreHalf - 1));
    const rr = length(P).add(fbm(P.mul(0.0045)).sub(0.5).mul(coreHalf * 0.16));
    const inCore = float(1).sub(smoothstep(coreHalf * 0.74, coreHalf * 0.99, rr)).mul(sq);
    const uvC = P.add(coreHalf).div(coreHalf * 2);
    const uvW = P.add(wideHalf).div(wideHalf * 2);
    const s2 = texture(land).sample(uvW).rgb;
    const o = mix(s2, texture(ortho).sample(uvC).rgb, inCore);
    const lum = dot(o, vec3(0.299, 0.587, 0.114));
    const n1 = fbm(P.mul(0.08)), n2 = fbm(P.mul(0.9));
    // meadow / pasture (spring-summer Tuscan greens, drier in patches)
    // meadow: greens varying over ~10 m and ~1 m, dry straw patches, darker clover, and small details (tufts, flowers, stones)
    const n3 = fbm(P.mul(0.27)), n4 = fbm(P.mul(3.1)), cellD = floor(P.mul(3.0)), hD = hash(cellD.x.add(cellD.y.mul(57.3)));
    let meadow: any = mix(mix(vec3(0.2, 0.28, 0.12), vec3(0.3, 0.36, 0.16), n1), vec3(0.42, 0.4, 0.22), smoothstep(0.62, 0.8, n2).mul(0.45));
    meadow = mix(meadow, vec3(0.16, 0.24, 0.1), smoothstep(0.58, 0.75, n3).mul(0.55));                // clover / damp hollows
    meadow = mix(meadow, vec3(0.48, 0.45, 0.28), smoothstep(0.66, 0.82, n3.mul(0.6).add(n4.mul(0.4))).mul(0.5)); // dry grass
    meadow = meadow.mul(n4.mul(0.22).add(0.89));                                                       // tufts
    meadow = select(hD.greaterThan(0.992), vec3(0.85, 0.78, 0.35), select(hD.greaterThan(0.986), vec3(0.86, 0.86, 0.8),
      select(hD.lessThan(0.004), vec3(0.5, 0.48, 0.44), meadow)));                                       // flowers, daisies, stones
    // farmland parcels (wheat, ploughed earth, vines, olive groves) on a slightly rotated 60 x 22 m grid
    const q = vec2(P.x.mul(0.94).add(P.y.mul(0.34)), P.y.mul(0.94).sub(P.x.mul(0.34)));
    const cell = floor(q.div(vec2(60, 22))), hc = hash(cell.x.add(cell.y.mul(131)));
    const rows = step(0.5, fract(q.y.div(2.2)));
    const field = select(hc.lessThan(0.25), mix(vec3(0.5, 0.43, 0.24), vec3(0.57, 0.5, 0.29), n2),               // wheat
      select(hc.lessThan(0.45), mix(vec3(0.33, 0.29, 0.23), vec3(0.41, 0.37, 0.29), rows),                          // ploughed (brown, not orange)
        select(hc.lessThan(0.7), mix(vec3(0.26, 0.31, 0.15), vec3(0.34, 0.32, 0.2), rows),                           // vines
          meadow)));
    // woods today (dark green in Sentinel-2) were woods / olive groves before too
    const green = o.y.div(o.x.add(o.y).add(o.z).add(0.001));
    const wood = smoothstep(0.34, 0.37, green).mul(smoothstep(0.36, 0.28, lum));
    let open = mix(mix(meadow, field, smoothstep(0.25, 0.65, n1).mul(0.8)), mix(vec3(0.12, 0.18, 0.09), vec3(0.18, 0.23, 0.12), n2), wood);
    // river gravel beaches near water level handled by the water mesh; open land outside the core = countryside
    // urban ground (core), by era (docs/MATERIALS.md "Street surfaces"):
    //  beaten earth → first paved streets 1237–1339 (each 40 m patch gets its own year; ~30 % brick herring-bone,
    //  re-laid in stone 1450–1550) → irregular pietra forte slabs (lastrico) → regular slabs in rows from 1860 →
    //  quarters built after 1850: earth/macadam, asphalt 1925–1960. Roman castrum: earth with basoli on cardo and decumanus.
    // the 8 m cells read with a noisy offset of about one cell, so built ground and gardens meet in irregular edges
    // instead of square steps
    const jit = vec2(fbm(P.mul(0.11)).sub(0.5), fbm(P.mul(0.11).add(37.0)).sub(0.5)).mul(U.cell * 1.6 / (coreHalf * 2));
    const urbanStart = texture(urbanTex).sample(uvC.add(jit)).r;
    const built = sq.mul(smoothstep(urbanStart.sub(15), urbanStart.add(15), uYear));
    const T = (n: keyof TexSet, size: number) => texture(tex[n].col).sample(P.div(size)).rgb;
    const terra = T('terra', 8), lastr = T('lastrico', 5).mul(0.95), amm = T('ammattonato', 2.4), filari = T('lastrico_filari', 4), asf = T('asfalto', 6);
    const pc = floor(P.div(40)), ph = (k: number) => hash(pc.x.mul(127.1).add(pc.y.mul(311.7)).add(k));
    const paved = step(float(1237).add(ph(1).mul(102)), uYear);
    const brick = step(ph(2), 0.3).mul(step(uYear, float(1450).add(ph(3).mul(100))));
    // unpaved earth streets: grass grows where few walk (patches and edges), so the earth blends into the meadows
    const grassy = smoothstep(0.55, 0.78, fbm(P.mul(0.35))).mul(0.55).add(smoothstep(0.7, 0.9, n4).mul(0.3));
    const earth = mix(terra, meadow, grassy);
    let street: any = mix(earth, mix(lastr, amm, brick), paved);
    // relaid from the 1840s in pietra forte / pietra serena slabs in courses with dressed tops (grooves, punched dots,
    // herring-bone chiselling); by 40 m patch: neat courses ~55 %, older irregular courses ~30 %, square slabs dressed in
    // herring-bone laid on the diagonal ~15 % (squares, e.g. Piazza Donatello) – shares *inferred*
    const Pd = vec2(P.x.add(P.y), P.y.sub(P.x)).mul(0.7071);
    const spina = texture(tex.lastrico_spina.col).sample(Pd.div(4)).rgb;
    const modern = select(ph(6).lessThan(0.55), filari, select(ph(6).lessThan(0.85), lastr, spina));
    street = mix(street, modern, step(float(1860).add(ph(4).mul(50)), uYear));
    const newQuarter = step(1850, urbanStart);
    // …then today's ground from the 2017 orthophoto (real roads, yards and gardens) instead of a flat asphalt fill, which
    // drew dark squares around the detached villas of the outer belt (asphalt texture tints it slightly)
    const nowGround = mix(o.mul(1.04), asf, 0.15);
    street = mix(street, mix(terra, nowGround, step(float(1925).add(ph(5).mul(35)), uYear)), newQuarter);
    // gardens and orti inside the blocks: lawn and planted beds with gravel paths where the yard is green in the photo
    const yard = Y ? texture(yardTex).sample(uvC).r : float(0);
    const greenO = o.y.div(o.x.add(o.y).add(o.z).add(0.001));
    const gardenK = smoothstep(0.55, 0.9, yard).mul(smoothstep(0.345, 0.375, greenO));
    const lawn = mix(vec3(0.27, 0.36, 0.17), vec3(0.34, 0.42, 0.2), n2).mul(mix(float(0.85), float(1.08), fbm(P.mul(0.6))));
    const gravel = T('terra', 3).mul(1.15);
    const garden = mix(lawn, gravel, smoothstep(0.62, 0.7, fbm(P.mul(0.12))).mul(0.6));
    const urbanGround = mix(street, garden, gardenK);
    // Roman Florentia (c. 30 BC – 6th c.): castrum box from the excavated walls (A03), cardo (via Roma–Calimala) and
    // decumanus (via Strozzi–Speziali–Corso) crossing at the forum; streets every ~1 actus in basoli
    const inCastrum = step(-300, P.x).mul(step(P.x, 125)).mul(step(-170, P.y)).mul(step(P.y, 232));
    const romanEra = step(-30, uYear).mul(step(uYear, 550));
    const gx = abs(fract(P.x.add(93).div(36)).sub(0.5)).mul(36), gz = abs(fract(P.y.sub(37).div(36)).sub(0.5)).mul(36);
    const roadR = max(step(abs(P.x.add(93)), 5), step(abs(P.y.sub(37)), 5)).add(max(step(gx, 2.5), step(gz, 2.5)).mul(0.85)).min(1);
    const romanGround = mix(terra, T('basoli', 4), roadR);
    // wide ring: today's built-up land (reddish/grey in S2) appears 1880-1990; vegetated land shows S2 colour today
    const builtToday = smoothstep(1.0, 1.08, o.x.div(o.y.add(0.001))).mul(float(1).sub(inCore));
    const modernWide = mix(open, s2.mul(1.08), smoothstep(1900, 2000, uYear).mul(builtToday).add(smoothstep(1950, 2010, uYear).mul(0.55).mul(float(1).sub(builtToday))));
    const t = smoothstep(1880, 1960, uYear);
    const countryside = mix(modernWide, mix(open, o.mul(1.05), t.mul(0.6)), inCore);
    let base: any = mix(countryside, urbanGround, built);
    base = mix(base, romanGround, inCastrum.mul(romanEra));
    const ov = ovTex.sample(uvC);
    return vec4(mix(base, ov.rgb, ov.a.mul(uOverlayOpacity).mul(sq)), 1);
  })();
  const groundMat = new THREE.MeshStandardNodeMaterial({ roughness: 1, metalness: 0 });
  groundMat.colorNode = ground;

  // ---------- core terrain (4 m) with a skirt that hides the seam to the 40 m ring ----------
  const h = await bin(`${base}/terrain.f32`, Float32Array);
  const n = meta.terrain.n, size = coreHalf * 2;
  const tg = new THREE.PlaneGeometry(size, size, n - 1, n - 1); tg.rotateX(-Math.PI / 2);
  const p = tg.getAttribute('position') as THREE.BufferAttribute;
  for (let i = 0; i < p.count; i++) p.setY(i, h[i]);
  tg.computeVertexNormals();
  const terrain = new THREE.Mesh(tg, groundMat); terrain.receiveShadow = true; terrain.name = 'terrain';
  group.add(terrain);
  {
    const sk: number[] = [], idx: number[] = []; const e = [] as number[][];
    for (let i = 0; i < n; i++) e.push([i, 0]); for (let j = 1; j < n; j++) e.push([n - 1, j]);
    for (let i = n - 2; i >= 0; i--) e.push([i, n - 1]); for (let j = n - 2; j > 0; j--) e.push([0, j]);
    e.forEach(([i, j], k) => { const x = -coreHalf + i * meta.terrain.step, z = -coreHalf + j * meta.terrain.step, y = h[j * n + i];
      sk.push(x, y, z, x, y - 8, z); const a = k * 2, b = ((k + 1) % e.length) * 2; idx.push(a, b, a + 1, b, b + 1, a + 1); });
    const sg = new THREE.BufferGeometry(); sg.setAttribute('position', new THREE.Float32BufferAttribute(sk, 3)); sg.setIndex(idx); sg.computeVertexNormals();
    group.add(new THREE.Mesh(sg, groundMat));
  }
  // ---------- wide ring (40 m), core cells removed ----------
  const hw = await bin(`${base}/wide.f32`, Float32Array);
  const nW = W.n;
  const wg = new THREE.PlaneGeometry(wideHalf * 2, wideHalf * 2, nW - 1, nW - 1); wg.rotateX(-Math.PI / 2);
  const wp = wg.getAttribute('position') as THREE.BufferAttribute;
  for (let i = 0; i < wp.count; i++) wp.setY(i, hw[i] - 0.4);
  const wi = wg.getIndex()!.array as ArrayLike<number>, keep: number[] = [];
  for (let t = 0; t < wi.length; t += 3) {         // the 40 m grid is aligned to the core square: drop cells inside it
    const a = wi[t], b = wi[t + 1], c = wi[t + 2];
    const cx = (wp.getX(a) + wp.getX(b) + wp.getX(c)) / 3, cz = (wp.getZ(a) + wp.getZ(b) + wp.getZ(c)) / 3;
    if (!(Math.abs(cx) < coreHalf && Math.abs(cz) < coreHalf)) keep.push(a, b, c);
  }
  wg.setIndex(keep); wg.computeVertexNormals();
  const wide = new THREE.Mesh(wg, groundMat); wide.receiveShadow = true; wide.name = 'wide-terrain';
  group.add(wide);

  // ---------- Arno: one surface per reach, sloping downstream, plus pescaie ----------
  const wpos = await bin(`${base}/water.pos.bin`, Float32Array), widx = await bin(`${base}/water.idx.bin`, Uint32Array);
  const rg = new THREE.BufferGeometry(); rg.setAttribute('position', new THREE.BufferAttribute(wpos, 3)); rg.setIndex(new THREE.BufferAttribute(widx, 1));
  rg.computeVertexNormals();
  const wm = new THREE.MeshStandardNodeMaterial({ roughness: 0.12, metalness: 0.0, transparent: true });
  const wave = (P: any) => {          // flow towards -x (west); small cross ripples
    const a = sin(P.x.mul(0.35).add(uTime.mul(1.6)).add(P.y.mul(0.12))), b = sin(P.y.mul(0.9).add(P.x.mul(0.21)).sub(uTime.mul(0.9)));
    const c = noise2(P.mul(vec2(0.25, 0.6)).add(vec2(uTime.mul(0.45), 0)));
    return a.mul(0.35).add(b.mul(0.25)).add(c.mul(0.6));
  };
  wm.normalNode = Fn(() => {
    const P = positionWorld.xz, e = 0.6;
    const dx = wave(P.add(vec2(e, 0))).sub(wave(P.sub(vec2(e, 0)))), dz = wave(P.add(vec2(0, e))).sub(wave(P.sub(vec2(0, e))));
    return transformNormalToView(normalize(vec3(dx.mul(-0.25), 1, dz.mul(-0.25))));
  })();
  wm.colorNode = Fn(() => {
    const V = normalize(cameraPosition.sub(positionWorld));
    const fres = pow(float(1).sub(max(V.y, 0)), 4);
    const body = mix(vec3(0.1, 0.16, 0.12), vec3(0.2, 0.24, 0.17), noise2(positionWorld.xz.mul(0.02)));   // Arno: green-brown, silty
    const sparkle = smoothstep(0.85, 1, wave(positionWorld.xz.mul(1.7))).mul(0.06);
    return vec4(mix(body, uSky.mul(0.8), fres.mul(0.45)).add(sparkle), 1);
  })();
  wm.opacityNode = float(0.94);
  const water = new THREE.Mesh(rg, wm); water.receiveShadow = true; water.name = 'arno'; group.add(water);

  const weirs: { mesh: THREE.Mesh; start: number; end: number }[] = [];
  const weirData: any[] = await (await fetch(`${base}/weirs.json`)).json();
  const weirMat = new THREE.MeshStandardNodeMaterial({ roughness: 0.6 });
  weirMat.colorNode = Fn(() => {
    const v = attribute('weirV', 'float');                                // 0 crest .. 1 toe
    const foam = smoothstep(0.55, 0.9, noise2(vec2(positionWorld.x.mul(0.6), v.mul(6).sub(uTime.mul(2.2))).add(positionWorld.z.mul(0.3))));
    const stone = texture(tex.pietra_forte.col).sample(positionWorld.xz.div(3)).rgb.mul(0.8);
    return vec4(mix(mix(stone, vec3(0.62, 0.66, 0.6), 0.55), vec3(0.93, 0.95, 0.93), foam.mul(0.85).add(v.mul(0.15))), 1);
  })();
  for (const w of weirData) {
    // crest line at the upstream level, toe 8 m downstream (west) at the lower level
    const pos: number[] = [], vv: number[] = [], I: number[] = [];
    w.pts.forEach(([x, z]: number[], i: number) => {
      pos.push(x + 1.2, w.up + 0.08, z, x, w.up + 0.08, z, x - 8, w.down + 0.05, z); vv.push(0, 0.08, 1);
      if (i) { const a = (i - 1) * 3, b = i * 3; for (let k = 0; k < 2; k++) I.push(a + k, b + k, a + k + 1, b + k, b + k + 1, a + k + 1); }
    });
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    g.setAttribute('weirV', new THREE.Float32BufferAttribute(vv, 1)); g.setIndex(I); g.computeVertexNormals();
    const m = new THREE.Mesh(g, weirMat); m.receiveShadow = true; m.userData = w; group.add(m);
    weirs.push({ mesh: m, start: w.start, end: w.end ?? 99999 });
  }

  // ---------- bridges: dated phases built as structures (scene/bridges.ts) ----------
  const bpos = await bin(`${base}/bridges.pos.bin`, Float32Array);
  const axis: number[][] = (await (await fetch(`${base}/river.json`)).json()).axis;
  const levelAt = (x: number) => { let i = 0; while (i < axis.length - 2 && axis[i + 1][0] < x) i++;
    const [a, b2] = [axis[i], axis[i + 1]], t = Math.min(1, Math.max(0, (x - a[0]) / (b2[0] - a[0]))); return a[1] + (b2[1] - a[1]) * t; };
  const groundAt = makeHeight(meta, h, hw);
  const bmats = bridgeMaterials(tex) as Record<string, THREE.Material>;
  const bridges: { mesh: THREE.Object3D; x: number; start: number; end: number; name: string; kind: string }[] = [];
  for (const b of meta.streets.bridges) {
    if (/vecchio/i.test(b.name) && b.start >= 1345) continue;      // the 1345 bridge with its shops is a landmark model (landmarks.ts)
    const pts: [number, number][] = [];
    for (let i = 0; i < b.count; i++) pts.push([bpos[(b.base + i) * 3], bpos[(b.base + i) * 3 + 2]]);
    const cx = pts.reduce((s2, q) => s2 + q[0], 0) / pts.length;
    const m = mergeBridge(buildBridge(pts, specFor(b.name, b.start, b.kind), levelAt(cx), groundAt), bmats);
    m.name = `${b.name} ${b.start}`;
    bridges.push({ mesh: m, x: cx, start: b.start, end: b.end ?? 99999, name: b.name, kind: b.kind }); group.add(m);
  }

  // ---------- vegetation: 4 species, each instance lives [start, end) – decided on the GPU ----------
  const T = await bin(`${base}/trees.bin`, Float32Array), S = 7, N = T.length / S;
  const species = [
    { crown: new THREE.IcosahedronGeometry(1, 1), sx: 0.26, sy: 0.27, lift: 0.7, hk: 0.85, col: [0x4c6635, 0x5f7a3e] },    // broadleaf (oak, plane, lime)
    { crown: new THREE.ConeGeometry(1, 1, 7, 2), sx: 0.09, sy: 0.9, lift: 0.53, hk: 0.95, col: [0x2f4429, 0x3a5230] },     // cypress
    { crown: new THREE.IcosahedronGeometry(1, 1), sx: 0.38, sy: 0.26, lift: 0.62, hk: 0.55, col: [0x7d8a62, 0x8f9a72] },    // olive
    { crown: new THREE.IcosahedronGeometry(1, 1), sx: 0.13, sy: 0.5, lift: 0.6, hk: 0.95, col: [0x587a3c, 0x6b8a45] },     // poplar
  ];
  const trunkG = new THREE.CylinderGeometry(0.1, 0.16, 1, 5);
  const trees: THREE.InstancedMesh[] = [];
  const M = new THREE.Matrix4(), q = new THREE.Quaternion(), s = new THREE.Vector3(), v = new THREE.Vector3();
  species.forEach((sp, ty) => {
    const share = opts.treeShare ?? 1;   // small devices draw a thinned forest (quality.ts); the same trees every time
    const ids: number[] = []; for (let i = 0; i < N; i++) if (T[i * S + 4] === ty && (share >= 1 || ((Math.imul(i, 2654435761) >>> 0) / 4294967296) < share)) ids.push(i);
    if (!ids.length) return;
    const life = new Float32Array(ids.length * 2);
    const mk = (geo: THREE.BufferGeometry, isCrown: boolean) => {
      const mat = new THREE.MeshStandardNodeMaterial({ roughness: 1, flatShading: isCrown });
      const L = attribute('life', 'vec2');
      mat.positionNode = Fn(() => {
        const alive = step(L.x, uYear).mul(step(uYear, L.y));
        // a light breeze: the crown bends from its foot (local y -1, on the trunk), never slides off it
        const sway = isCrown ? sin(uTime.mul(0.9).add(hash(instanceIndex).mul(6.28))).mul(0.012).mul(positionLocal.y.add(1).max(0)) : float(0);
        return positionLocal.add(vec3(sway, 0, sway.mul(0.6))).mul(alive);
      })();
      const c0 = new THREE.Color(isCrown ? sp.col[0] : 0x4a3a2c), c1 = new THREE.Color(isCrown ? sp.col[1] : 0x5a4636);
      mat.colorNode = mix(vec3(c0.r, c0.g, c0.b), vec3(c1.r, c1.g, c1.b), hash(instanceIndex.add(isCrown ? 7 : 3)));
      const g2 = geo.clone(); g2.setAttribute('life', new THREE.InstancedBufferAttribute(life, 2));
      const im = new THREE.InstancedMesh(g2, mat, ids.length);
      im.castShadow = isCrown; im.frustumCulled = false; return im;
    };
    const crown = mk(sp.crown, true), trunk = mk(trunkG, false);
    ids.forEach((i, k) => {
      // heights: LiDAR canopy in the core, typical species heights outside; olives are kept low (4–8 m), crowns narrower
      const [x, y, z] = [T[i * S], T[i * S + 1], T[i * S + 2]], ht = Math.min(T[i * S + 3] * sp.hk, ty === 1 ? 20 : 16);
      life[k * 2] = T[i * S + 5]; life[k * 2 + 1] = T[i * S + 6];
      const rx = ht * sp.sx, ry = ht * sp.sy, rot = (i * 2.399) % 6.28;
      q.setFromAxisAngle(v.set(0, 1, 0), rot);
      M.compose(v.set(x, y + ht * sp.lift, z), q, s.set(rx, ry, rx)); crown.setMatrixAt(k, M);
      M.compose(v.set(x, y + ht * 0.25, z), q, s.set(0.8, ht * 0.5, 0.8)); trunk.setMatrixAt(k, M);
    });
    group.add(crown, trunk); trees.push(crown, trunk);
  });

  function update(year: number) {
    for (const b of bridges) b.mesh.visible = year >= b.start && year < b.end;
    for (const w of weirs) w.mesh.visible = year >= w.start && year < w.end;
  }
  return { group, terrain, wide, water, update, bridges, weirs, overlayNode: ovTex, wideHalf, treeData: T };
}

/** Terrain height lookup for agents and props: LiDAR core grid, 40 m ring outside it. */
export function makeHeight(meta: any, h: Float32Array, hw?: Float32Array) {
  const sample = (g: Float32Array, n: number, step: number, x: number, z: number) => {
    const half = ((n - 1) * step) / 2, fx = (x + half) / step, fz = (z + half) / step;
    const i = Math.max(0, Math.min(n - 2, Math.floor(fx))), j = Math.max(0, Math.min(n - 2, Math.floor(fz)));
    const tx = Math.min(1, Math.max(0, fx - i)), tz = Math.min(1, Math.max(0, fz - j));
    const a = g[j * n + i], b = g[j * n + i + 1], c = g[(j + 1) * n + i], d = g[(j + 1) * n + i + 1];
    return (a * (1 - tx) + b * tx) * (1 - tz) + (c * (1 - tx) + d * tx) * tz;
  };
  const core = ((meta.terrain.n - 1) * meta.terrain.step) / 2;
  return (x: number, z: number) => (Math.abs(x) <= core && Math.abs(z) <= core) || !hw
    ? sample(h, meta.terrain.n, meta.terrain.step, x, z) : sample(hw, meta.wide.n, meta.wide.step, x, z);
}
