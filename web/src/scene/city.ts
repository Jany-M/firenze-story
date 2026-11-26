// All dated structures (buildings, demolished blocks, walls, gates, Roman remains) in ONE mesh.
// Per-structure data lives in two float textures; a TSL vertex program hides/raises structures by year,
// so scrubbing the timeline never touches geometry on the CPU.
import * as THREE from 'three/webgpu';
import {
  Fn, attribute, uniform, texture, textureLoad, ivec2, int, float, vec2, vec3, vec4, If, select, mix, min, max, clamp, fract, step,
  smoothstep, positionLocal, positionWorld, hash, varyingProperty, abs, floor, length, normalize, cameraPosition, pow, sin, fwidth,
} from 'three/tsl';
import { PERIODS, CONF_COLORS } from '../data/history';
import type { TexSet } from './assets';

export interface Rec {
  id: number; kind: string; name: string; start: number; end: number | null; ramp: number; conf: string; src: string[];
  qid: string; wiki: string; ground: number; h: number; phases: number[][]; roof: string; c: [number, number]; sub?: string;
  hidden?: boolean;                              // shell replaced by a landmark model: not drawn, not picked
  style?: { gf: number; fh: number; sp: number; win: number; grd: number; shut: number; mat: number; balc?: number }; rgb?: number[];
}
const TEXW = 256;
export const uYear = uniform(1490);
export const uColorMode = uniform(0);      // 0 real, 1 period, 2 confidence
export const uSelected = uniform(-1);
export const uOrtho = uniform(1);          // 1 = tint roofs with their 2017 orthophoto colour
export const uSky = uniform(new THREE.Color(0xb8c8d6));   // sky colour (set every frame), reflected by glass and water

export async function loadCity(base: string, orthoTex: THREE.Texture, tex: TexSet) {
  void orthoTex;   // roofs are tinted per building from the orthophoto in the pipeline (no per-pixel photo smear)
  const bin = async (n: string) => (await fetch(`${base}/structures.${n}.bin`)).arrayBuffer();
  const [meta, pos, nrm, bid, fu, fv, idx] = await Promise.all([
    fetch(`${base}/structures.json`).then(r => r.json()), bin('pos'), bin('nrm'), bin('bid'), bin('fu'), bin('fv'), bin('idx')]);
  const recs: Rec[] = meta.items;

  // normals: int8 x4 -> float32 x3
  const n8 = new Int8Array(nrm), nv = n8.length / 4, n32 = new Float32Array(nv * 3);
  for (let i = 0; i < nv; i++) { n32[i * 3] = n8[i * 4] / 127; n32[i * 3 + 1] = n8[i * 4 + 1] / 127; n32[i * 3 + 2] = n8[i * 4 + 2] / 127; }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(pos), 3));
  g.setAttribute('normal', new THREE.BufferAttribute(n32, 3));
  g.setAttribute('bid', new THREE.BufferAttribute(new Float32Array(bid), 1));
  g.setAttribute('fu', new THREE.BufferAttribute(new Float32Array(fu), 1));
  g.setAttribute('fv', new THREE.BufferAttribute(new Float32Array(fv), 1));
  g.setIndex(new THREE.BufferAttribute(new Uint32Array(idx), 1));
  g.computeBoundingSphere(); g.computeBoundingBox();

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
    const pxm = max(fwidth(u), fwidth(rel));
    const near = smoothstep(0.1, 0.035, pxm);                     // slats, glazing bars, planks
    const mid = smoothstep(0.32, 0.14, pxm);                      // windows: below ~4 px each they average into the wall
    const thin = smoothstep(0.09, 0.04, pxm);                     // frames, sills, string courses (~15 cm): only when wider than ~2 px
    // ---------- wall materials ----------
    const palette = mix(mix(V3(0.86, 0.75, 0.56), V3(0.93, 0.88, 0.76), h), mix(V3(0.78, 0.72, 0.6), V3(0.84, 0.64, 0.5), h2), step(0.62, h3));
    const intonaco = mix(vec3(1), T('intonaco', wuv.div(4)).mul(1.1), mix(float(0.25), float(0.55), near));
    const plaster = palette.mul(intonaco);
    const forte = T('pietra_forte', wuv.div(vec2(3.2, 2.4)));
    const serena = T('pietra_serena', wuv.div(2.2));
    const cotto = T('cotto', wuv.div(1.2));
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
    const hasUV = aFv.notEqual(0);
    const ruv = SX(hasUV, vec2(aFu.negate().sub(1), aFv), vec2(positionWorld.x, positionWorld.z));
    const tiles = T('coppi', ruv.div(4));
    const tint = t3.xyz.div(V3(0.62, 0.38, 0.27));
    const roof = tiles.mul(mix(vec3(1), tint, SX(uOrtho.greaterThan(0.5), float(0.85), float(0)))).mul(mix(float(0.92), float(1.06), h));
    // ---------- ornaments ----------
    let real = SX(isRoof, roof, facade);
    real = SX(isStone, serena.mul(1.05), real);
    real = SX(isIron, V3(0.1, 0.1, 0.11), real);
    real = SX(isPlaster, plaster.mul(0.95), real);
    // ---------- colour modes ----------
    const pIdx = periodIndex(vStart);
    const per = textureLoad(texture(periodTex), ivec2(int(pIdx), int(0))).rgb;
    const cc = SX(conf.lessThan(0.5), vec3(confCols[0].r, confCols[0].g, confCols[0].b),
      SX(conf.lessThan(1.5), vec3(confCols[1].r, confCols[1].g, confCols[1].b), vec3(confCols[2].r, confCols[2].g, confCols[2].b)));
    const shade = select(isRoof, float(1), float(0.82));
    const col = SX(uColorMode.lessThan(0.5), real, SX(uColorMode.lessThan(1.5), per.mul(shade), cc.mul(shade)));
    const sel = abs(aBid.sub(uSelected)).lessThan(0.5);
    return vec4(SX(sel, mix(col, vec3(1.0, 0.72, 0.25), 0.55), col), 1);
  })();
  mat.roughnessNode = select(aFu.lessThan(0).and(aFu.greaterThan(-500)), float(0.78), float(0.92));

  const mesh = new THREE.Mesh(g, mat);
  mesh.frustumCulled = false;
  mesh.castShadow = true; mesh.receiveShadow = true;
  /** Hide the shells of structures that a landmark model replaces (they stay pickable and keep their record). */
  function hide(names: Set<string>, ids: Set<number> = new Set()) {
    for (const r of recs) if (names.has(r.name) || ids.has(r.id)) { d0[r.id * 4] = 99998; d0[r.id * 4 + 1] = 99999; r.hidden = true; }
    T0.needsUpdate = true;
  }
  return { mesh, recs, hide };
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
export function pick(mesh: THREE.Mesh, recs: Rec[], ray: THREE.Raycaster, year: number): number { return pickHit(mesh, recs, ray, year).id; }
/** Nearest standing structure under the ray (hidden landmark shells are skipped), with its distance. */
export function pickHit(mesh: THREE.Mesh, recs: Rec[], ray: THREE.Raycaster, year: number): { id: number; dist: number } {
  const hits = ray.intersectObject(mesh, false);
  const bidA = mesh.geometry.getAttribute('bid') as THREE.BufferAttribute;
  for (const h of hits) {
    const id = Math.round(bidA.getX(h.face!.a));
    const r = recs[id];
    if (r.hidden || !isAlive(r, year)) continue;
    // reject hits above the structure's current height (during construction / caps)
    if (h.point.y > r.ground + r.h * 1.4 + 2) continue;
    return { id, dist: h.distance };
  }
  return { id: -1, dist: Infinity };
}
