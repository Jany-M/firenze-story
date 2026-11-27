// All dated structures (buildings, demolished blocks, walls, gates, Roman remains) in ONE mesh.
// Per-structure data lives in two float textures; a TSL vertex program hides/raises structures by year,
// so scrubbing the timeline never touches geometry on the CPU.
import * as THREE from 'three/webgpu';
import {
  Fn, attribute, uniform, texture, textureLoad, ivec2, int, float, vec2, vec3, vec4, If, select, mix, min, max, clamp, fract, step,
  smoothstep, positionLocal, positionWorld, hash, varyingProperty, abs, floor, length, normalize, cameraPosition, pow, sin, fwidth,
  dFdx, dFdy, cross, dot,
} from 'three/tsl';
import { cityKeep } from './xray';
import { PERIODS, CONF_COLORS } from '../data/history';
import type { TexSet } from './assets';

export interface Rec {
  id: number; kind: string; name: string; start: number; end: number | null; ramp: number; conf: string; src: string[];
  qid: string; wiki: string; ground: number; h: number; phases: number[][]; roof: string; c: [number, number]; sub?: string;
  hidden?: boolean;                              // shell replaced by a landmark model: not drawn, not picked
  of?: string; about?: string; also?: string[]; virtual?: boolean;   // a part of a landmark with no record of its own (cloisters): its building, a few facts
  style?: { gf: number; fh: number; sp: number; win: number; grd: number; shut: number; mat: number; balc?: number }; rgb?: number[];
}
const TEXW = 256;
export const uYear = uniform(1490);
export const uColorMode = uniform(0);      // 0 real, 1 period, 2 confidence
export const uPeriodPick = uniform(-1);    // period mode: the one period left in colour (-1 all)
export const uSelected = uniform(-1);
export const uOrtho = uniform(1);          // 1 = tint roofs with their 2017 orthophoto colour
export const uSky = uniform(new THREE.Color(0xb8c8d6));   // sky colour (set every frame), reflected by glass and water
// Corridor cut: where a raised passage (the Vasari Corridor) runs through or over city houses, the houses are cut open above
// its floor inside its footprint, so the whole route shows. Raster of the floor height (NaN-free: −1e4 = no corridor).
const cutBlank = new THREE.DataTexture(new Float32Array([-1e4]), 1, 1, THREE.RedFormat, THREE.FloatType); cutBlank.needsUpdate = true;
const cutTex = texture(cutBlank);
const uCutBox = uniform(new THREE.Vector4(0, 0, 1, 1));   // x0, z0, width, depth (m)
const uCutFrom = uniform(99999);
/** Build the cut raster from corridor runs (centre line, floor per point, width), shown from year `from`. */
export function setCorridorCut(runs: { pts: [number, number][]; floor: number[]; w: number }[], from: number, res = 0.25, margin = -0.12) {   // the cut stays just inside the corridor's walls, so its edge hides behind them
  let x0 = Infinity, z0 = Infinity, x1 = -Infinity, z1 = -Infinity;
  for (const r of runs) for (const [x, z] of r.pts) { x0 = Math.min(x0, x - r.w); z0 = Math.min(z0, z - r.w); x1 = Math.max(x1, x + r.w); z1 = Math.max(z1, z + r.w); }
  const W = Math.ceil((x1 - x0) / res), H = Math.ceil((z1 - z0) / res), d = new Float32Array(W * H).fill(-1e4);
  for (const r of runs) {
    const hw = r.w / 2 + margin;
    for (let i = 0; i < r.pts.length - 1; i++) {
      const [ax, az] = r.pts[i], [bx, bz] = r.pts[i + 1], dx = bx - ax, dz = bz - az, L2 = dx * dx + dz * dz || 1;
      const c0 = Math.max(0, Math.floor((Math.min(ax, bx) - hw - x0) / res)), c1 = Math.min(W - 1, Math.ceil((Math.max(ax, bx) + hw - x0) / res));
      const r0 = Math.max(0, Math.floor((Math.min(az, bz) - hw - z0) / res)), r1 = Math.min(H - 1, Math.ceil((Math.max(az, bz) + hw - z0) / res));
      for (let rr = r0; rr <= r1; rr++) for (let cc = c0; cc <= c1; cc++) {
        const px = x0 + (cc + 0.5) * res, pz = z0 + (rr + 0.5) * res;
        const t = Math.max(0, Math.min(1, ((px - ax) * dx + (pz - az) * dz) / L2));
        if (Math.hypot(px - ax - dx * t, pz - az - dz * t) > hw) continue;
        const f = r.floor[i] + (r.floor[i + 1] - r.floor[i]) * t, k = rr * W + cc;
        d[k] = d[k] < -1e3 ? f : Math.min(d[k], f);
      }
    }
  }
  const tex = new THREE.DataTexture(d, W, H, THREE.RedFormat, THREE.FloatType);
  tex.minFilter = tex.magFilter = THREE.NearestFilter; tex.needsUpdate = true;
  cutTex.value = tex; uCutBox.value.set(x0, z0, W * res, H * res); uCutFrom.value = from;
}
/** Mask: false inside a corridor's footprint above its floor (from its year). */
const corridorKeep = Fn(() => {
  const uv = vec2(positionWorld.x.sub(uCutBox.x).div(uCutBox.z), positionWorld.z.sub(uCutBox.y).div(uCutBox.w));
  const inBox = uv.x.greaterThan(0).and(uv.x.lessThan(1)).and(uv.y.greaterThan(0)).and(uv.y.lessThan(1));
  const f = cutTex.sample(uv).r;
  const cut = inBox.and(f.greaterThan(-1000)).and(positionWorld.y.greaterThan(f.add(0.05))).and(uYear.greaterThanEqual(uCutFrom));
  return cut.not();
});

/** A tile's bytes: tiles ship gzipped (.bin.gz); inflate in the browser unless the server already did (gzip magic 1f 8b). */
async function fetchTile(url: string): Promise<ArrayBuffer> {
  const raw = await (await fetch(url)).arrayBuffer();
  const b = new Uint8Array(raw, 0, Math.min(2, raw.byteLength));
  if (b[0] !== 0x1f || b[1] !== 0x8b) return raw;
  return await new Response(new Blob([raw]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();
}
/** Tiles of the city mesh (pipeline/23_city_tiles.py): loaded round the camera as it moves, nearest first. */
interface TileInfo { f: string; i: number; j: number; x0: number; z0: number; q: number; big: boolean; nv: number; nt: number; i32: boolean }

export async function loadCity(base: string, orthoTex: THREE.Texture, tex: TexSet,
  opts: { radius?: number; center?: [number, number]; first?: number; low?: boolean } = {}) {
  const LOW = !!opts.low;   // small devices: flat wall colours (no wall textures), the window grid only close up
  void orthoTex;   // roofs are tinted per building from the orthophoto in the pipeline (no per-pixel photo smear)
  const [meta, tindex] = await Promise.all([fetch(`${base}/structures.json`).then(r => r.json()), fetch(`${base}/tiles/index.json`).then(r => r.json())]);
  const recs: Rec[] = meta.items;
  const TILE: number = tindex.tile, YOFF: number = tindex.yoff, tiles: TileInfo[] = tindex.tiles;
  // one box per record, filled in as its tile arrives (the x-ray of close views, scene/xray.ts)
  const boxes = new Float32Array(recs.length * 6);
  for (let i = 0; i < recs.length; i++) boxes.set([Infinity, Infinity, Infinity, -Infinity, -Infinity, -Infinity], i * 6);
  const group = new THREE.Group(); group.name = 'city';
  async function tileMesh(t: TileInfo) {
    const buf = await fetchTile(`${base}/tiles/${t.f}`), nv = t.nv;
    let o = 0; const take = <T>(C: new (b: ArrayBuffer, o: number, n: number) => T, n: number, bytes: number) => { const a = new C(buf, o, n); o += n * bytes; return a; };
    const q16 = take(Int16Array, nv * 3, 2), n8 = take(Int8Array, nv * 4, 1), b16 = take(Uint16Array, nv, 2);
    if (o % 4) o += 4 - (o % 4);                                            // never needed (nv*6+nv*4+nv*2 = 12·nv), kept for safety
    const U1 = take(Float32Array, nv, 4), V1 = take(Float32Array, nv, 4);
    const I = t.i32 ? take(Uint32Array, t.nt * 3, 4) : take(Uint16Array, t.nt * 3, 2);
    const P3 = new Float32Array(nv * 3), N3 = new Float32Array(nv * 3), B1 = new Float32Array(nv), k = 1 / t.q;
    for (let v = 0; v < nv; v++) {
      const x = t.x0 + q16[v * 3] * k, y = q16[v * 3 + 1] * k - YOFF, z = t.z0 + q16[v * 3 + 2] * k, id = b16[v];
      P3[v * 3] = x; P3[v * 3 + 1] = y; P3[v * 3 + 2] = z; B1[v] = id;
      N3[v * 3] = n8[v * 4] / 127; N3[v * 3 + 1] = n8[v * 4 + 1] / 127; N3[v * 3 + 2] = n8[v * 4 + 2] / 127;
      const b = id * 6;
      if (x < boxes[b]) boxes[b] = x; if (y < boxes[b + 1]) boxes[b + 1] = y; if (z < boxes[b + 2]) boxes[b + 2] = z;
      if (x > boxes[b + 3]) boxes[b + 3] = x; if (y > boxes[b + 4]) boxes[b + 4] = y; if (z > boxes[b + 5]) boxes[b + 5] = z;
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(P3, 3));
    g.setAttribute('normal', new THREE.BufferAttribute(N3, 3));
    g.setAttribute('bid', new THREE.BufferAttribute(B1, 1));
    g.setAttribute('fu', new THREE.BufferAttribute(U1, 1));
    g.setAttribute('fv', new THREE.BufferAttribute(V1, 1));
    g.setIndex(new THREE.BufferAttribute(I, 1));
    g.computeBoundingSphere(); g.computeBoundingBox();
    const m = new THREE.Mesh(g, mat); m.castShadow = m.receiveShadow = true; m.name = t.f;
    return m;
  }
  // per-structure data textures
  const rows = Math.ceil(recs.length / TEXW);
  const d0 = new Float32Array(TEXW * rows * 4), d1 = new Float32Array(TEXW * rows * 4);
  const d2 = new Float32Array(TEXW * rows * 4), d3 = new Float32Array(TEXW * rows * 4);   // facade layout · roof tint + material
  const kindCode: Record<string, number> = { building: 0, demolished: 1, ohm: 2, gate: 3, roman: 4 };
  const confCode: Record<string, number> = { documented: 0, inferred: 1, conjectural: 2 };
  for (const r of recs) {
    const o = r.id * 4, ph = r.phases?.[0];
    d0[o] = r.start; d0[o + 1] = r.end ?? 99999; d0[o + 2] = Math.max(r.ramp, 1); d0[o + 3] = r.ground;
    d1[o] = r.h; d1[o + 1] = ph ? ph[0] : -99999; d1[o + 2] = ph ? ph[1] : 0;
    d1[o + 3] = (kindCode[r.kind] ?? 0) + 8 * (confCode[r.conf] ?? 2) + 32 * (r.roof === 'ortho' ? 1 : 0);
    const st = r.style ?? { gf: 4, fh: 3.8, sp: 3.3, win: 0, grd: 0, shut: 1, mat: 0 };
    d2[o] = st.gf; d2[o + 1] = st.fh; d2[o + 2] = st.sp; d2[o + 3] = st.win + 8 * st.grd + 32 * st.shut;
    const c = r.rgb ?? [168, 96, 70]; d3[o] = c[0] / 255; d3[o + 1] = c[1] / 255; d3[o + 2] = c[2] / 255; d3[o + 3] = st.mat;
  }
  const mk = (d: Float32Array) => { const t = new THREE.DataTexture(d, TEXW, rows, THREE.RGBAFormat, THREE.FloatType); t.needsUpdate = true; return t; };
  const T0 = mk(d0), T1 = mk(d1), T2 = mk(d2), T3 = mk(d3);

  const mat = new THREE.MeshStandardNodeMaterial({ roughness: 0.9, metalness: 0 });
  const aBid = floor(attribute('bid', 'float').add(0.5)),   // rounded: interpolation jitter would flip per-building hashes per pixel
     aFu = attribute('fu', 'float'), aFv = attribute('fv', 'float');
  const coord = ivec2(int(aBid).mod(int(TEXW)), int(aBid).div(int(TEXW)));
  const t0 = textureLoad(texture(T0), coord), t1 = textureLoad(texture(T1), coord);
  const start = t0.x, end = t0.y, ramp = t0.z, ground = t0.w, hFull = t1.x, capY = t1.y, capV = t1.z, flags = t1.w;

  // ---- vertex: existence, construction ramp, dated height caps ----
  const rel = positionLocal.y.sub(ground);
  const vRel = varyingProperty('float', 'vRel');
  const vFlags = varyingProperty('float', 'vFlags');
  const vStart = varyingProperty('float', 'vStart');
  const vTop = varyingProperty('float', 'vTop');
  mat.positionNode = Fn(() => {
    const p = positionLocal.toVar();
    const grow = clamp(uYear.sub(start).div(ramp), 0, 1);
    const top = max(hFull.mul(1.35), float(6)).mul(grow).toVar();
    // capV > 0: cap before capY (e.g. Duomo without dome) · capV < 0: cap after capY (towers cut down)
    If(capV.greaterThan(0).and(uYear.lessThan(capY)), () => { top.assign(min(top, capV)); });
    If(capV.lessThan(0).and(uYear.greaterThanEqual(capY)), () => { top.assign(min(top, capV.negate())); });
    const r = min(rel, top);
    p.y.assign(ground.add(r));
    const alive = uYear.greaterThanEqual(start).and(uYear.lessThan(end));
    If(alive.not(), () => { p.assign(vec3(0, -500, 0)); });   // collapse hidden structures (degenerate tris)
    // while a building is still going up (long estimated ramps), show the rising walls without the roof: a roof squashed
    // onto a low wall read as orange patches on the ground
    If(grow.lessThan(0.999).and(aFu.lessThan(0)).and(aFu.greaterThan(-500)), () => { p.assign(vec3(0, -500, 0)); });
    vRel.assign(r); vFlags.assign(flags); vStart.assign(start); vTop.assign(top);
    return p;
  })();

  // ---- fragment: facades, roofs, colour modes ----
  const periodTex = paletteTexture(PERIODS.map(p => p.color));
  const confCols = [CONF_COLORS.documented, CONF_COLORS.inferred, CONF_COLORS.conjectural].map(c => new THREE.Color(c));
  const t2 = textureLoad(texture(T2), coord), t3 = textureLoad(texture(T3), coord);
  const T = (n: keyof TexSet, uv: any) => texture(tex[n].col).sample(uv).rgb;
  const V3 = (r: number, g: number, b: number) => vec3(r, g, b);
// colour pick as a blend weight (keeps the node graph simple and typed)
const SX = (c: any, a: any, b: any): any => mix(b, a, select(c, float(1), float(0)));
  mat.colorNode = Fn(() => {
    // varyings arrive as 9.9999 / 10.0001: round before decoding bit fields, or the category flips per pixel
    const flg = floor(vFlags.add(0.5));
    const kind = flg.mod(8), conf = floor(flg.div(8)).mod(4);
    const h = hash(aBid), h2 = hash(aBid.add(7)), h3 = hash(aBid.add(3));
    const isRoof = aFu.lessThan(0).and(aFu.greaterThan(-500));
    const isStone = aFu.lessThanEqual(-1000).and(aFu.greaterThan(-1500));
    const isIron = aFu.lessThanEqual(-2000).and(aFu.greaterThan(-2500));
    const isPlaster = aFu.lessThanEqual(-3000);
    // guards: structures without a façade layout carry zeros, and u/0 = NaN survives every blend as a sparkling pixel
    const gf = t2.x, fh = max(t2.y, 2.5), sp = max(t2.z, 1.5), code = t2.w;
    const win0 = code.mod(8), grd = floor(code.div(8)).mod(4), shut = floor(code.div(32)), mtl = t3.w;
    // most medieval fronts were remodelled (16th–19th c.): arches / bifore become framed rectangles after a per-building year;
    // about a quarter keep their medieval openings, landmarks always do
    const remodel = float(1480).add(hash(aBid.add(19)).mul(320));
    const keepOld = hash(aBid.add(23)).lessThan(0.25).or(mtl.greaterThan(0.5));
    const win = select(win0.greaterThan(0.5).and(win0.lessThan(2.5)).and(uYear.greaterThan(remodel)).and(keepOld.not()), float(0), win0);
    const u = aFu, rel = vRel, wuv = vec2(u, rel);
    // size of one screen pixel on the wall (metres): fine detail and then the window grid fade out as it shrinks (no moire)
    // (also measured on the world position: small rooftop pieces – chimneys, altane – whose u is constant along a face would
    // otherwise get full detail, slats and sills aliasing into flickering stripes)
    const pxm0 = max(max(fwidth(u), fwidth(rel)), length(fwidth(positionWorld)).mul(0.7));
    const pxm = select(fwidth(u).lessThan(fwidth(rel).mul(0.02)), float(1), pxm0);   // a face along which u does not run: plain wall
    const near = LOW ? float(0) : smoothstep(0.1, 0.035, pxm);   // slats, glazing bars, planks
    const mid = LOW ? smoothstep(0.2, 0.09, pxm) : smoothstep(0.32, 0.14, pxm);   // windows: below ~4 px each (low tier: ~7 px) they average into the wall
    const thin = LOW ? float(0) : smoothstep(0.09, 0.04, pxm);   // frames, sills, string courses (~15 cm): only when wider than ~2 px
    // ---------- wall materials ----------
    const palette = mix(mix(V3(0.86, 0.75, 0.56), V3(0.93, 0.88, 0.76), h), mix(V3(0.78, 0.72, 0.6), V3(0.84, 0.64, 0.5), h2), step(0.62, h3));
    const intonaco = LOW ? vec3(1) : mix(vec3(1), T('intonaco', wuv.div(4)).mul(1.1), mix(float(0.25), float(0.55), near));
    const plaster = palette.mul(intonaco);
    const forte = LOW ? V3(0.6, 0.49, 0.36) : T('pietra_forte', wuv.div(vec2(3.2, 2.4)));
    const serena = LOW ? V3(0.5, 0.5, 0.48) : T('pietra_serena', wuv.div(2.2));
    const cotto = LOW ? V3(0.64, 0.38, 0.28) : T('cotto', wuv.div(1.2));
    // marble bichrome (Baptistery, Duomo, Campanile, Santa Croce, SMN): white Carrara fields framed by green Prato bands
    const px = fract(u.div(2.6)), py = fract(rel.div(3.2));
    const band = step(px, 0.09).add(step(0.91, px)).add(step(py, 0.08)).add(step(0.92, py)).min(1);
    const inner = step(0.3, px).mul(step(px, 0.7)).mul(step(0.3, py)).mul(step(py, 0.7));
    const marble = mix(mix(V3(0.9, 0.88, 0.83), V3(0.95, 0.93, 0.88), noiseLike(wuv)), V3(0.2, 0.3, 0.26), band.max(inner.mul(0.85)));
    const medievalStone = mtl.lessThan(0.5).and(vStart.lessThan(1350)).and(h2.lessThan(0.35));
    const m = floor(mtl.add(0.5));
    const pilaster = mix(plaster, serena, step(0.9, fract(u.div(sp))).add(step(fract(u.div(sp)), 0.1)).min(1));
    let wall = mix(plaster, forte, SX(medievalStone, float(1), float(0)));
    wall = mix(wall, forte, step(0.5, m).mul(step(m, 1.5)));
    wall = mix(wall, marble, step(1.5, m).mul(step(m, 2.5)));
    wall = mix(wall, cotto, step(2.5, m).mul(step(m, 3.5)));
    wall = mix(wall, pilaster, step(3.5, m));
    // ---------- upper floors: window grid from the pipeline (gf, fh, sp), types by era ----------
    const yU = rel.sub(gf), k = floor(yU.div(fh)), ly = yU.sub(k.mul(fh));
    const cx = fract(u.div(sp)).sub(0.5).mul(sp);
    const ww = select(win.equal(3), float(1.7), select(win.equal(2), float(1.5), float(1.15)));
    const wh = min(fh.mul(0.56), select(win.equal(3), float(1.7), float(2.35)));
    const sill = float(0.95), top = sill.add(wh), r = ww.div(2);
    const above = yU.greaterThan(0).and(rel.lessThan(vTop.sub(0.9))).and(win.lessThan(3.5)).and(kind.lessThan(1.5)).and(isRoof.not());
    const archY = top.sub(r), arched = win.equal(1).or(win.equal(2));
    const inRect = abs(cx).lessThan(r).and(ly.greaterThan(sill)).and(ly.lessThan(select(arched, archY, top)));
    const inArch = arched.and(ly.greaterThanEqual(archY)).and(length(vec2(cx, ly.sub(archY))).lessThan(r));
    const opening = inRect.or(inArch).and(above);
    const colonnette = win.equal(2).and(abs(cx).lessThan(0.09)).and(opening);
    const frameD = 0.17;
    const inRectF = abs(cx).lessThan(r.add(frameD)).and(ly.greaterThan(sill.sub(frameD))).and(ly.lessThan(select(arched, archY, top.add(frameD))));
    const inArchF = arched.and(ly.greaterThanEqual(archY)).and(length(vec2(cx, ly.sub(archY))).lessThan(r.add(frameD)));
    const frame = inRectF.or(inArchF).and(above).and(opening.not()).and(win.notEqual(3));
    const sillBand = above.and(abs(cx).lessThan(r.add(0.22))).and(ly.greaterThan(sill.sub(0.14))).and(ly.lessThan(sill.sub(frameD).add(0.02)));
    // glass: dark interior, sky reflected at grazing angles, some curtains
    const V = normalize(cameraPosition.sub(positionWorld));
    const wid = hash(floor(u.div(sp)).add(k.mul(17)).add(aBid.mul(0.13)));
    const interior = mix(V3(0.05, 0.055, 0.06), V3(0.42, 0.36, 0.3), step(0.8, wid).mul(0.6));
    const glass = mix(interior, uSky.mul(0.85), pow(float(1).sub(abs(V.y)), 3).mul(0.55).add(0.1));
    const panes: any = step(0.93, fract(cx.add(r).div(ww.div(2)))).add(step(0.95, fract(ly.div(0.6)))).min(1).mul(select(win.lessThan(2.5), float(1), float(0))).mul(near);
    const glassC = mix(glass, V3(0.2, 0.16, 0.12), panes.mul(0.8));
    // shutters (persiane): from 1750 (wooden, green or brown), grey rollers from 1945; closed / half / open per window
    const shutOn = shut.greaterThan(0.5).and(select(shut.greaterThan(2.5), uYear.greaterThanEqual(1945), uYear.greaterThanEqual(1750)));
    const shutCol = SX(shut.lessThan(1.5), V3(0.21, 0.3, 0.2), SX(shut.lessThan(2.5), V3(0.33, 0.22, 0.14), V3(0.56, 0.56, 0.54)));
    const slats = mix(shutCol.mul(0.88), mix(shutCol, shutCol.mul(0.7), step(0.55, fract(ly.div(0.07)))), near);
    const closed = shutOn.and(wid.lessThan(0.32)).and(opening);
    const half = shutOn.and(wid.greaterThanEqual(0.32)).and(wid.lessThan(0.5)).and(opening).and(cx.lessThan(0));
    const openLeaf = shutOn.and(wid.greaterThanEqual(0.5)).and(shut.lessThan(2.5)).and(above).and(opening.not())
      .and(abs(cx).greaterThan(r.add(frameD))).and(abs(cx).lessThan(r.add(frameD).add(r))).and(ly.greaterThan(sill)).and(ly.lessThan(top));
    let facade = wall;
    facade = mix(facade, SX(vStart.lessThan(1450), forte.mul(1.05), serena.mul(1.05)), SX(frame.or(sillBand), thin, float(0)));
    facade = SX(opening, SX(colonnette.and(thin.greaterThan(0.5)), serena, glassC), facade);
    facade = SX(closed.or(half).or(openLeaf), slats, facade);
    // string course (marcapiano) at the first floor and the shadow / cornice under the eaves
    const stringC = above.not().and(rel.greaterThan(gf.sub(0.18))).and(rel.lessThan(gf)).and(vStart.greaterThan(1400)).and(kind.lessThan(1.5));
    facade = mix(facade, serena, SX(stringC, thin, float(0)));
    // ---------- ground floor ----------
    const gnd = rel.lessThan(gf).and(kind.lessThan(1.5)).and(isRoof.not());
    const cell = floor(u.div(sp)), ch = hash(cell.add(aBid.mul(0.7)));
    // botteghe: round-headed shop arches with pietra forte voussoirs, doors open (dark) or shut (planks)
    const ah = min(gf.sub(0.6), float(3.4)), aw = sp.mul(0.36);
    const ay = ah.sub(aw);
    const inShop = abs(cx).lessThan(aw).and(rel.lessThan(ay)).or(length(vec2(cx, rel.sub(ay))).lessThan(aw).and(rel.greaterThanEqual(ay)));
    const voussoir = length(vec2(cx, rel.sub(ay))).lessThan(aw.add(0.35)).and(rel.greaterThanEqual(ay)).and(inShop.not()).or(abs(abs(cx).sub(aw.add(0.17))).lessThan(0.17).and(rel.lessThan(ay)));
    const planks = mix(V3(0.34, 0.23, 0.14), mix(V3(0.3, 0.2, 0.12), V3(0.38, 0.26, 0.16), step(0.5, fract(cx.mul(3)))), near);
    const shopC = SX(ch.lessThan(0.45), V3(0.06, 0.05, 0.05), planks);
    // doors on plain ground floors
    const door = ch.lessThan(0.28).and(abs(cx).lessThan(0.7)).and(rel.lessThan(2.7)).and(rel.greaterThan(0.15));
    // shopfronts (19th–20th c.)
    const shopfront = abs(cx).lessThan(sp.mul(0.42)).and(rel.greaterThan(0.35)).and(rel.lessThan(min(gf.sub(0.9), float(3.2))));
    const sign = abs(cx).lessThan(sp.mul(0.45)).and(rel.greaterThan(min(gf.sub(0.8), float(3.3)))).and(rel.lessThan(min(gf.sub(0.3), float(3.8))));
    let ground = SX(grd.equal(1), forte, wall);
    ground = SX(grd.equal(2).and(voussoir), forte.mul(1.04), ground);
    ground = SX(grd.equal(2).and(inShop), shopC, ground);
    ground = SX(grd.equal(0).and(door), planks.mul(0.85), ground);
    ground = SX(grd.equal(3).and(shopfront), mix(glassC, V3(0.15, 0.15, 0.16), step(0.92, fract(cx.div(1.2)))), ground);
    ground = SX(grd.equal(3).and(sign), V3(0.16, 0.17, 0.16), ground);
    ground = SX(rel.lessThan(0.5).and(grd.notEqual(3)), forte.mul(0.9), ground);                       // plinth
    facade = SX(gnd, ground, facade);
    // far away: replace the (sub-pixel) window grid by its average tone
    facade = SX(above.or(gnd), mix(mix(wall, V3(0.1, 0.09, 0.08), 0.22), facade, mid), facade);
    // weathering: rising damp at the base, darker under the eaves
    facade = facade.mul(mix(float(0.82), float(1), smoothstep(0, 1.4, rel))).mul(mix(float(1), float(0.72), smoothstep(vTop.sub(1.2), vTop.sub(0.2), rel)));
    // walls, gates, Roman remains (no windows)
    facade = SX(kind.greaterThan(1.5).and(kind.lessThan(3.5)), forte, SX(kind.greaterThan(3.5), SX(mtl.greaterThan(2.5), cotto, plaster), facade));
    // ---------- roofs: coppi running down the slope, tinted with the building's own roof colour ----------
    // tile courses follow each roof face: the face's own slope (from screen derivatives, so every pitch of a hip or a
    // LiDAR roof gets its direction) gives the downhill axis; v runs down the slope in true length, u along the eaves
    const fN0 = normalize(cross(dFdx(positionWorld), dFdy(positionWorld)));
    const fN = SX(fN0.y.lessThan(0), fN0.negate(), fN0);
    const gH = length(vec2(fN.x, fN.z)), down = vec2(fN.x, fN.z).div(max(gH, float(1e-4))), along = vec2(down.y.negate(), down.x);
    const Pw = vec2(positionWorld.x, positionWorld.z);
    const slopeUV = vec2(dot(Pw, along), dot(Pw, down).div(max(fN.y, float(0.25))));
    const ruv = SX(gH.greaterThan(0.06), slopeUV, Pw);
    const tiles = T('coppi', ruv.div(4));
    const tint = t3.xyz.div(V3(0.62, 0.38, 0.27));
    const roof = tiles.mul(mix(vec3(1), tint, SX(uOrtho.greaterThan(0.5), float(0.85), float(0)))).mul(mix(float(0.92), float(1.06), h));
    // ---------- ornaments ----------
    let real = SX(isRoof, roof, facade);
    // small pieces with a material code in place of a façade coordinate (chimneys, caps, balcony slabs): their u is the code,
    // a constant, so the wall textures would be sampled along one line and shimmer; they take world-space coordinates
    // (along each face: a box turned at 45° has faces along which x + z does not change, and a cap's top has no y – the
    // texture was then read along a single line and flickered; now u runs along the face and tops take x, z)
    const cN = fN0, cT = vec2(cN.z.negate(), cN.x).div(max(length(vec2(cN.x, cN.z)), float(1e-4)));
    const cuv = select(abs(cN.y).greaterThan(0.7), vec2(positionWorld.x, positionWorld.z), vec2(dot(vec2(positionWorld.x, positionWorld.z), cT), positionWorld.y));
    // (small pieces: the texture fades to its mean tone as they shrink on screen – a 0.6 m chimney drawn with a grainy
    // texture sparkled at every movement of the view)
    const pxS = length(fwidth(positionWorld)), grain = smoothstep(0.035, 0.008, pxS);
    const serenaC = LOW ? V3(0.5, 0.5, 0.48) : mix(V3(0.5, 0.5, 0.48), T('pietra_serena', cuv.div(2.2)), grain);
    const plasterC = LOW ? palette : palette.mul(mix(vec3(1), T('intonaco', cuv.div(4)).mul(1.1), grain.mul(0.18)));
    real = SX(isStone, serenaC.mul(1.05), real);
    // balcony railings (5 cm bars) seen from afar are thinner than a pixel: black and white flickered on every altana and
    // balcony; past ~2 px per bar they fade to the grey of bars against the wall behind
    real = SX(isIron, mix(V3(0.1, 0.1, 0.11), V3(0.5, 0.48, 0.45), smoothstep(0.02, 0.07, pxS)), real);
    real = SX(isPlaster, plasterC.mul(0.95), real);
    // near-vertical faces of a LiDAR roof are its chimneys, dormers and parapets caught by the scan: plastered, not tiled (the
    // tiles and the orthophoto's tint stretched down a vertical face read as grey-white grain that sparkled as the view moved)
    real = SX(isRoof.and(fN.y.lessThan(0.45)), palette.mul(0.93), real);

    // ---------- colour modes ----------
    const pIdx = periodIndex(vStart);
    const per = textureLoad(texture(periodTex), ivec2(int(pIdx), int(0))).rgb;
    const cc = SX(conf.lessThan(0.5), vec3(confCols[0].r, confCols[0].g, confCols[0].b),
      SX(conf.lessThan(1.5), vec3(confCols[1].r, confCols[1].g, confCols[1].b), vec3(confCols[2].r, confCols[2].g, confCols[2].b)));
    const shade = select(isRoof, float(1), float(0.82));
    // one period picked in the legend: the others in grey
    const grey = vec3(dot(per, vec3(0.299, 0.587, 0.114)).mul(0.55).add(0.32));
    const perC = SX(uPeriodPick.lessThan(0).or(abs(float(pIdx).sub(uPeriodPick)).lessThan(0.5)), per, grey);
    const col = SX(uColorMode.lessThan(0.5), real, SX(uColorMode.lessThan(1.5), perC.mul(shade), cc.mul(shade)));
    const sel = abs(aBid.sub(uSelected)).lessThan(0.5);
    return vec4(SX(sel, mix(col, vec3(1.0, 0.72, 0.25), 0.55), col), 1);
  })();
  mat.maskNode = (cityKeep(aBid) as any).and(corridorKeep());
  mat.roughnessNode = select(aFu.lessThan(0).and(aFu.greaterThan(-500)), float(0.78), float(0.92));

  // ---- streaming: the tiles within `radius` of the view's centre (all of them when radius is 0), nearest first; far
  // tiles are dropped again on small devices
  const R = opts.radius || Infinity, loaded = new Map<string, THREE.Mesh>(), pending = new Set<string>();
  const dist = (t: TileInfo, x: number, z: number) => t.big ? 0 : Math.hypot(Math.max(0, Math.abs(x - (t.i + 0.5) * TILE) - TILE / 2), Math.max(0, Math.abs(z - (t.j + 0.5) * TILE) - TILE / 2));
  let busy = 0; let cx = opts.center?.[0] ?? 0, cz = opts.center?.[1] ?? 0;
  function pump() {
    while (busy < 3) {
      const next = tiles.filter(t => !loaded.has(t.f) && !pending.has(t.f) && dist(t, cx, cz) <= R).sort((a, b) => dist(a, cx, cz) - dist(b, cx, cz))[0];
      if (!next) return;
      busy++; pending.add(next.f);
      tileMesh(next).then(m => { loaded.set(next.f, m); group.add(m); }).catch(e => console.warn('tile', next.f, e))
        .finally(() => { busy--; pending.delete(next.f); pump(); });
    }
  }
  /** Follow the view: call with the camera target (cheap; loads and drops tiles as needed). */
  function follow(x: number, z: number) {
    if (Math.hypot(x - cx, z - cz) < 40) return;
    cx = x; cz = z;
    if (R < Infinity) for (const [f, m] of loaded) {
      const t = tiles.find(t => t.f === f)!;
      if (dist(t, x, z) > R * 1.6) { group.remove(m); m.geometry.dispose(); loaded.delete(f); }
    }
    pump();
  }
  // the first view waits for the tiles right round it, the rest stream in
  const first = tiles.filter(t => dist(t, cx, cz) <= Math.min(R, opts.first ?? 450));
  await Promise.all(first.map(async t => { pending.add(t.f); const m = await tileMesh(t); loaded.set(t.f, m); group.add(m); pending.delete(t.f); }));
  pump();
  const mesh = group;
  /** Hide the shells of structures that a landmark model replaces (they stay pickable and keep their record). */
  function hide(names: Set<string>, ids: Set<number> = new Set()) {
    for (const r of recs) if (names.has(r.name) || ids.has(r.id)) { d0[r.id * 4] = 99998; d0[r.id * 4 + 1] = 99999; r.hidden = true; }
    T0.needsUpdate = true;
  }
  return { mesh, recs, hide, boxes, follow, tileCount: () => loaded.size };
}

/** Cheap 2D noise for material variation (0..1). */
function noiseLike(p: any) { return fract(sin(p.x.mul(12.9898).add(p.y.mul(78.233))).mul(43758.5453)).mul(0.25).add(sin(p.x.mul(0.7)).mul(sin(p.y.mul(0.9))).mul(0.25).add(0.5)); }

const PERIOD_ENDS = PERIODS.map(p => p.to);
function periodIndex(y: any) {
  let idx: any = float(PERIOD_ENDS.length - 1);
  for (let i = PERIOD_ENDS.length - 2; i >= 0; i--) idx = select(y.lessThanEqual(PERIOD_ENDS[i]), float(i), idx);
  return idx;
}
function paletteTexture(cols: string[]) {
  const d = new Float32Array(cols.length * 4);
  cols.forEach((c, i) => { const k = new THREE.Color(c); d.set([k.r, k.g, k.b, 1], i * 4); });
  const t = new THREE.DataTexture(d, cols.length, 1, THREE.RGBAFormat, THREE.FloatType); t.needsUpdate = true; return t;
}

export const isAlive = (r: Rec, y: number) => y >= r.start && y < (r.end ?? 99999);
export const periodOf = (y: number) => PERIODS.findIndex(p => y <= p.to);

/** CPU pick: first visible structure under the ray (geometry is static, visibility by year). */
export function pick(mesh: THREE.Object3D, recs: Rec[], ray: THREE.Raycaster, year: number): number { return pickHit(mesh, recs, ray, year).id; }
/** Nearest standing structure under the ray (hidden landmark shells are skipped), with its distance. */
export function pickHit(mesh: THREE.Object3D, recs: Rec[], ray: THREE.Raycaster, year: number): { id: number; dist: number } {
  const hits = ray.intersectObject(mesh, true);
  for (const h of hits) {
    const bidA = (h.object as THREE.Mesh).geometry.getAttribute('bid') as THREE.BufferAttribute;
    const id = Math.round(bidA.getX(h.face!.a));
    const r = recs[id];
    if (r.hidden || !isAlive(r, year)) continue;
    // reject hits above the structure's current height (during construction / caps)
    if (h.point.y > r.ground + r.h * 1.4 + 2) continue;
    return { id, dist: h.distance };
  }
  return { id: -1, dist: Infinity };
}
