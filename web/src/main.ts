import * as THREE from 'three/webgpu';
import { state, set, on, touchHash } from './state';
import { createStage, uTilt, DEFAULT_HOUR } from './scene/stage';
import { detectQuality } from './quality';
import { createXray } from './scene/xray';
import { createStatues } from './scene/statues';
import { type Rec, loadCity, setCorridorCut, uYear, uColorMode, uPeriodPick, uSelected, pickHit, periodOf } from './scene/city';
import { loadLandmarks, LANDMARKS } from './scene/landmarks';
import { createStreetHighlight } from './scene/streetview';
import { loadEnvironment, makeHeight, uOverlayOpacity, uTime, uSky } from './scene/environment';
import { createSplats } from './scene/splats';
import { loadTextures, loadProps } from './scene/assets';
import { createViewControls } from './scene/view';
import { createPeople } from './sim/people';
import { createScenes } from './sim/scenes';
import { createSquares } from './sim/squares';
import { createRiver } from './sim/river';
import { createGovernor } from './perf';
import { createTimeline } from './ui/timeline';
import { createPanels, toast } from './ui/panels';
import { createNarration } from './ui/narration';
import { layout } from './ui/layout';
import { open as openGallery, materialsFor } from './ui/gallery';
import { EVENTS, EVENT_REFS, CONF_COLORS, SOURCE_LAYERS, PERIODS, overlayFor } from './data/history';
import { walk } from './sim/walk';

/** The Landmarks tab's sections, in this order; a model's kind, and the names that take another kind than their model's. */
const LMK_KINDS = ['Churches and places of worship', 'Palazzi', 'Squares, loggias and markets', 'Bridges and the river', 'Walls and gates', 'Gardens and forts', 'Public buildings'];
const LMK_KIND: Record<string, string> = {
  duomo: LMK_KINDS[0], campanile: LMK_KINDS[0], baptistery: LMK_KINDS[0], santa_croce: LMK_KINDS[0], santa_maria_novella: LMK_KINDS[0], san_lorenzo: LMK_KINDS[0],
  santo_spirito: LMK_KINDS[0], san_marco: LMK_KINDS[0], carmine: LMK_KINDS[0], felicita: LMK_KINDS[0], miniato: LMK_KINDS[0], sinagoga: LMK_KINDS[0], orsanmichele: LMK_KINDS[0],
  palazzo_vecchio: LMK_KINDS[1], bargello: LMK_KINDS[1], uffizi: LMK_KINDS[1], medici_riccardi: LMK_KINDS[1], pitti: LMK_KINDS[1], strozzi: LMK_KINDS[1],
  repubblica: LMK_KINDS[1], antella: LMK_KINDS[1], corridoio: LMK_KINDS[1], borsa: LMK_KINDS[1],
  annunziata: LMK_KINDS[2], loggia_lanzi: LMK_KINDS[2], loggia_pesce: LMK_KINDS[2], mercato_centrale: LMK_KINDS[2], piazza_smn: LMK_KINDS[2], piazzale: LMK_KINDS[2],
  ponte_vecchio: LMK_KINDS[3], lungarni: LMK_KINDS[3], canottieri: LMK_KINDS[3], mura: LMK_KINDS[4], boboli: LMK_KINDS[5],
  stazione_smn: LMK_KINDS[6], leopolda: LMK_KINDS[6], teatro_maggio: LMK_KINDS[6], murate: LMK_KINDS[6], biblioteca: LMK_KINDS[6],
};
/** Where to go for a model that holds no single building of its own (the river walls, the square's obelisks and lawns). */
const LMK_AT: Record<string, [number, number]> = { piazza_smn: [-466.75, -183], lungarni: [-100, 440], piazzale: [818.5, 976.5], canottieri: [30, 467] };
/** 'MM-DD' → fraction of the year, for parts dated to the day (landmark names "part@1504_160-…"). */
const dayFrac = (d: string) => { const [m, dd] = (d || '01-01').split('-').map(Number); return (([0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334][m - 1] ?? 0) + dd - 1) / 366; };

const DATA = './data';
const loading = document.getElementById('loading')!;
// loading screen: one line per step, ticked off with its time when the next one starts
const steps = document.createElement('ul'); steps.className = 'steps'; loading.querySelector('div')!.appendChild(steps);
let cur: { li: HTMLLIElement; t0: number } | null = null;
function done(extra = '') {
  if (!cur) return;
  cur.li.classList.add('ok');
  cur.li.querySelector('i')!.textContent = extra; cur.li.querySelector('b')!.textContent = `${((performance.now() - cur.t0) / 1000).toFixed(1)} s`; cur = null;
}
// label, details and time are separate boxes that wrap onto their own full-width lines when a row is too narrow (phones)
const say = (t: string) => {
  done(); loading.querySelector('p')!.textContent = t;
  const li = document.createElement('li'); li.innerHTML = `<em></em><span></span><i></i><b>…</b>`; li.querySelector('span')!.textContent = t;
  steps.appendChild(li); cur = { li, t0: performance.now() };
};

async function main() {
  say('Checking this device');
  const q = await detectQuality();
  done(`${q.tier} detail (${q.reason})`);
  const stage = await createStage(document.getElementById('app')!, q);
  const { scene, camera, controls, renderer, pipeline } = stage;
  say('Materials and map data');
  const texLoader = new THREE.TextureLoader();
  const loadTex = (u: string) => texLoader.loadAsync(`${DATA}/${u}`).then(t => { t.flipY = false; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = q.anisotropy; t.generateMipmaps = true; return t; });
  const [ortho, mtex] = await Promise.all([loadTex('ortho2017.jpg'), loadTextures('./textures', q.anisotropy)]);
  const blank = new THREE.DataTexture(new Uint8Array([0, 0, 0, 0]), 1, 1); blank.needsUpdate = true;
  say('Study area and street network');
  const [meta, streets] = await Promise.all(['meta', 'streets'].map(n => fetch(`${DATA}/${n}.json`).then(r => r.json())));
  meta.streets = streets;
  done(`${((meta.bbox_utm[2] - meta.bbox_utm[0]) / 1000).toFixed(1)} × ${((meta.bbox_utm[3] - meta.bbox_utm[1]) / 1000).toFixed(1)} km, ${streets.edges.length.toLocaleString()} street segments`);
  say('Dated buildings and structures');
  // the city streams in tiles round the view; small devices keep only those near it (quality.ts cityRadius)
  const c0: [number, number] = state.cam.length === 6 ? [state.cam[3], state.cam[5]] : [0, 60];
  const city = await loadCity(DATA, ortho, mtex, { radius: q.cityRadius, center: c0, first: q.tier === 'low' || q.tier === 'min' ? 350 : 600, low: q.tier === 'low' || q.tier === 'min' });
  const { mesh, recs, hide } = city;
  done(`${recs.length.toLocaleString()} structures`);
  say('Landmark models');
  const landmarks = await loadLandmarks(scene, mtex, recs); hide(landmarks.replaced, landmarks.replacedIds);
  fetch('./models/landmarks/corridoio_path.json').then(r => r.ok ? r.json() : null).then(c => { if (c) setCorridorCut(c.runs, c.from); }).catch(() => {});
  const xray = createXray(camera, controls.target, { boxes: city.boxes, recs }, landmarks.xrayParts);
  // Years where something visibly changes: a structure rising (start → start + ramp) or going, a landmark part, an event.
  // Playback rushes through the stretches in between, so nobody stares at decades where nothing moves.
  const busy: [number, number][] = [];
  for (const r of recs) { busy.push([r.start, r.start + Math.max(r.ramp, 1)]); if (r.end != null) busy.push([r.end - 1, r.end]); }
  for (const y of landmarks.changes) busy.push([y - 0.5, y + 0.5]);
  for (const e of EVENTS) busy.push([e.year - 1, e.year + 1]);
  busy.sort((a, b) => a[0] - b[0]);
  const spans: [number, number][] = [];
  for (const b of busy) { const l = spans[spans.length - 1]; if (l && b[0] <= l[1]) l[1] = Math.max(l[1], b[1]); else spans.push([...b]); }
  /** distance in years to the next change from y (0 inside a busy span) */
  const quietAhead = (y: number) => {
    let lo = 0, hi = spans.length;
    while (lo < hi) { const m = (lo + hi) >> 1; if (spans[m][1] <= y) lo = m + 1; else hi = m; }
    const s = spans[lo]; return !s ? 2026 - y : Math.max(0, s[0] - y);
  };
  const FAST = 50, QUIET = 8;   // a stretch of 8+ empty years plays at ≥ 50 years a second
  const tlEl = document.getElementById('timeline')!;
  scene.add(mesh);
  say('Terrain, river, bridges and trees');
  const env = await loadEnvironment(DATA, meta, ortho, blank, mtex, { treeShare: q.treeShare, anisotropy: q.anisotropy, terrainUp: q.terrainUp });
  scene.add(env.group);
  const HW = new Float32Array(await (await fetch(`${DATA}/wide.f32`)).arrayBuffer());
  const height = makeHeight({ ...meta, terrain: { n: env.grid.n, step: env.grid.step } }, env.grid.h, HW, { ...env.dated, year: () => state.year });   // the same rounded grid as the ground mesh
  const statues = createStatues(scene, height); statues.update(state.year);
  done(`${meta.trees.count.toLocaleString()} trees`);
  say('People and costumes');
  const people = await createPeople(scene, streets, q.people);
  // made on demand for the area in view (river crews, squares and bridges near the camera); none drawn above PEOPLE_ALT
  const riverPeople = await createPeople(scene, streets, 0, { walkers: false, cap: q.riverPeople });
  const squarePeople = await createPeople(scene, streets, 0, { walkers: false, cap: q.squarePeople });
  // the crowds thin if the device falls behind (perf.ts)
  const governor = createGovernor(q, renderer, [{ crowd: people, base: q.people, cap: 600 }, { crowd: riverPeople, base: 0, cap: q.riverPeople },
    { crowd: squarePeople, base: 0, cap: q.squarePeople }]);
  // what people stand on: the ground, or a bridge's deck where the street crosses one (a ray down onto the bridges standing
  // this year, cached per half metre)
  const deckRay = new THREE.Raycaster(), downV = new THREE.Vector3(0, -1, 0), deckCache = new Map<number, number>(); let deckYear = NaN;
  const walkY = (x: number, z: number, bridge: boolean) => {
    const g = height(x, z); if (!bridge) return g;
    const yr = Math.round(state.year); if (yr !== deckYear) { deckCache.clear(); deckYear = yr; }
    const k = Math.round(x * 2) * 100000 + Math.round(z * 2); const c = deckCache.get(k); if (c !== undefined) return c;
    deckRay.set(new THREE.Vector3(x, g + 60, z), downV); deckRay.far = 80;
    // the bridges drawn by the app and the landmark models (Ponte Vecchio, Santa Trinita…): the highest walkable face under
    // the ray, not a roof (the Corridor over Ponte Vecchio): the first hit below 12 m over the ground's level
    const shown = (o: THREE.Object3D) => { for (let p: THREE.Object3D | null = o; p; p = p.parent) if (!p.visible) return false; return true; };
    const hits = deckRay.intersectObjects([...env.bridges.filter(b => b.mesh.visible).map(b => b.mesh), landmarks.group], true);
    const hit = hits.find(h => shown(h.object) && h.point.y < g + 14 && (h.face?.normal.y ?? 1) > 0.3 && !(((h.object as THREE.Mesh).material as any)?.visible === false));
    const y = hit ? Math.max(g, hit.point.y) : g; deckCache.set(k, y); return y;
  };
  people.setGround(walkY);
  say('Props, boats and animals');
  const props = await loadProps(mtex, './models');
  const scenes = createScenes(scene, people, height, props, streets.squares);
  scenes.setBridges(env.bridges);
  const squareLife = createSquares(scene, props, squarePeople, height, streets.squares, env.bridges, streets);
  // walkable ground: building footprints by year (pipeline 20), tree trunks, scene props – see sim/walk.ts
  say('Walkable ground');
  const foot = env.foot;                                  // fetched once, by the environment (the ground's softening reads it too)
  walk.init(recs, foot ? new Uint16Array(foot) : null, env.treeData); walk.setYear(state.year);
  // free-standing monuments of the landmark models are solid: nobody walks through the Piazzale's David and its steps
  landmarks.group.updateMatrixWorld(true);
  landmarks.group.traverse((o: any) => { if (o.isMesh && /^monumento_/.test(o.name + ' ' + (o.parent?.name ?? ''))) walk.addProp(o, 0.3, 'landmark'); });
  if ((import.meta as any).env?.DEV || location.hostname === 'localhost') Object.assign(window as any, { __fs: { scene, scenes, people, camera, controls, walk, get squares() { return squareLife; }, squarePeople, riverPeople, env } });   // dev-only debug handle
  const view = createViewControls(camera, controls, renderer.domElement);
  say('River life: boats, fishermen, birds');
  const riverAxis = (await (await fetch(`${DATA}/river.json`)).json()).axis;
  const river = createRiver(scene, props, riverPeople, height, riverAxis, env.bridges, env.weirs.map((w: any) => w.mesh.userData), env.water.geometry, streets.nodes);
  if ((window as any).__fs) Object.assign((window as any).__fs, { river });
  const splats = createSplats(scene, () => controls.target.clone(), toast);

  // ---- camera helpers ----
  /** Smoothly frame a point: keeps the current heading, sets distance and pitch (radians from vertical). */
  function flyTo(x: number, z: number, dist = 420, pitch = 0.9, azimuth?: number) {
    const y = height(x, z); const from = controls.target.clone(), to = new THREE.Vector3(x, y, z);
    const dir = camera.position.clone().sub(controls.target); const az = azimuth ?? Math.atan2(dir.x, dir.z);
    const off = new THREE.Vector3().setFromSphericalCoords(dist, pitch, az);
    const camFrom = camera.position.clone(), camTo = to.clone().add(off); const t0 = performance.now();
    const step = () => { const t = Math.min(1, (performance.now() - t0) / 1600); const k = t * t * (3 - 2 * t);
      controls.target.lerpVectors(from, to, k); camera.position.lerpVectors(camFrom, camTo, k); if (t < 1) requestAnimationFrame(step); };
    step();
  }
  if (state.cam.length === 6) { camera.position.fromArray(state.cam.slice(0, 3)); controls.target.fromArray(state.cam.slice(3)); }

  function applyMode() {
    const live = state.mode === 'live';
    controls.maxPolarAngle = Math.PI / 2 - 0.01; controls.minDistance = live ? 8 : 12;   // down to the horizontal: fronts seen square on
    uTilt.value = state.tiltShift && (state.mode === 'overview' || state.mode === 'landmarks') ? 1 : (state.tiltShift && live ? 0.35 : 0);
    const crowd = state.mode !== 'sources';              // people in the streets in the timeline and landmark views too, not on the data view
    people.setEnabled(crowd); squarePeople.setEnabled(crowd); riverPeople.setEnabled(true);   // river and pre-urban figures show in every mode
    if (live) {
      refreshLive(true, true);
    } else scenes.clear();
  }
  let pendingEvent: any = null, sceneTitle = '';
  function refreshLive(force = false, frame = false) {
    if (state.mode !== 'live') return;
    const changed = people.setContext(Math.round(state.year), controls.target, 360);
    if (changed || force || pendingEvent) {
      const s = scenes.evaluate(state.year, state.date, state.hour, (x, z, az, dist, pitch) => flyTo(x, z, dist ?? 110, pitch ?? 0.82, az), pendingEvent ?? undefined, frame);
      if (frame && !s) flyTo(controls.target.x, controls.target.z, 110, 0.95);
      pendingEvent = null;
      panels.liveNote(s === 'calcio' ? 'Calcio storico in Piazza Santa Croce' : s === 'market' ? 'Market day in Mercato Vecchio' : s === 'sanlorenzo' ? 'Market day at San Lorenzo' : s === 'scoppio' ? 'Scoppio del Carro in Piazza del Duomo'
        : s === 'david' ? 'The David on its way to Piazza della Signoria (14–18 May 1504, route presumed)' : s === 'davidWait' ? 'The David by the palace door, waiting to be raised onto the ringhiera (8 June 1504)'
        : s === 'ponti1944' ? 'The Night of the Bridges, 3–4 August 1944 (sequence compressed)' : s === 'alluvione1966' ? 'The flood of 4 November 1966' : 'Everyday streets');
      sceneTitle = s === 'david' ? 'The David leaves the Opera del Duomo' : s === 'scoppio' ? 'Scoppio del Carro' : s === 'ponti1944' ? 'The Night of the Bridges'
        : s === 'alluvione1966' ? 'The great flood' : '';
    }
  }
  // One lighting for the whole app (DEFAULT_HOUR). An event with its own hour (the Night of the Bridges at 23:00) lights the
  // scene for that hour while it is on – played, paused or finished, so it can be played again – and goes back to the
  // default as soon as the user moves on: another event, another year or day, another mode.
  let eventLight: { year: number; date: string } | null = null;
  const endEventLight = () => { if (!eventLight) return; eventLight = null; if (state.hour !== DEFAULT_HOUR) queueMicrotask(() => set({ hour: DEFAULT_HOUR })); };
  if (state.hour !== DEFAULT_HOUR) set({ hour: DEFAULT_HOUR });
  const firstSentences = (t: string, n: number) => (t.match(/[^.!?]+[.!?]+(\s|$)/g) ?? [t]).slice(0, n).join('').trim();
  // an event picked from the list without a scene of its own: its facts stay at the top until the year or the date changes
  const narration = createNarration();
  let factEvent: { year: number; date?: string; title: string; text: string } | null = null, liveEvent = '';
  function goEvent(i: number) {
    const e = EVENTS[i];
    eventLight = null;
    liveEvent = e.live ?? '';
    factEvent = e.live ? null : { year: e.year, date: e.date, title: `${e.year < 0 ? -e.year + ' BC' : e.year}${e.date ? ' · ' + e.date.split('-').reverse().map(Number).join('/') : ''} · ${e.title}`, text: firstSentences(EVENT_REFS[e.title]?.sum ?? e.note, 2) };
    if (e.hour != null && e.hour !== DEFAULT_HOUR) eventLight = { year: e.year, date: e.date ?? state.date };
    set({ year: e.year, date: e.date ?? state.date, hour: eventLight ? e.hour! : DEFAULT_HOUR, playing: false, mode: e.live ? 'live' : state.mode });
    if (e.live) { pendingEvent = e; refreshLive(true); } else flyTo(e.at[0], e.at[1], 600, 0.85);
    panels.showEvent(i);
    if (e.live && scenes.duration() > 0) panels.foldLive();     // an animation runs: the Events box folds to its title and player
  }

  // ---- UI ----
  say('Street names and house numbers');
  const addresses = await fetch(`${DATA}/addresses.json`).then(r => r.ok ? r.json() : undefined).catch(() => undefined);
  const streetHL = createStreetHighlight(scene, height);
  const panels = createPanels(recs, { flyTo, event: goEvent, backend: stage.backend,
    // the scene player: play / pause (paused: the scene stands still and the camera is free), drag to move through it
    playToggle: () => { const D = scenes.duration(); if (!D) return; if (scenes.time >= D - 0.01) { scenes.seek(0); scenes.paused = false; } else scenes.paused = !scenes.paused; },
    seek: (f: number) => scenes.seek(f * scenes.duration()), layerCount: id => id === 'A07' ? river.ancientCount() : 0, addresses,
    highlightStreet: code => streetHL.show(code && addresses ? addresses.streets[code] : null), squares: streets.squares,
    landmarks: [
      ...LANDMARKS.filter(l => l.replaces[0] && !l.members).map(l => ({ name: l.replaces[0], x: l.at[0], z: l.at[1], from: l.from ?? 1300 })),
      // models holding several buildings (the walls): one entry per gate / tower, where its record stands
      ...LANDMARKS.flatMap(l => (l.members ?? []).map(m => { const r = recs.find(r => r.name === m.name); return r ? { name: m.name, x: r.c[0], z: r.c[1], from: m.from ?? r.start } : null; }))
        .filter((e): e is { name: string; x: number; z: number; from: number } => !!e),
    ],
    // the Landmarks tab: every hand-built model and each building it holds, with its record (card, place, years)
    kinds: LMK_KINDS,
    // one entry per model, under its kind: the model's own building first, the buildings it holds folded under it
    catalogue: LANDMARKS.flatMap(l => {
      const head = [l.title, ...l.replaces].find(n => n && recs.some(r => r.name === n)) ?? l.title ?? l.replaces[0];   // the model's own record (not its aliases)
      const names = [...new Set([head, ...(l.members ?? []).map(m => m.name)].filter(Boolean) as string[])];
      const items = [...new Set(names.map(n => recs.find(r => r.name === n)).filter((r): r is Rec => !!r))];
      const title = l.title ?? l.replaces[0] ?? items[0]?.name ?? l.file, at = l.at[0] || l.at[1] ? l.at : LMK_AT[l.file] ?? null;
      const subjects = [...new Set([title, title.split(':')[0], ...l.replaces, ...items.map(r => r.name)])].map(n => `rec:${n}`);
      if (!items.length && !at) return [];
      return [{ kind: LMK_KIND[l.file] ?? 'Public buildings', title, items, at, from: l.from ?? 1300, subjects, head: !!(items[0] && items[0].name === head) }];
    }) });
  const timeline = createTimeline(document.getElementById('timeline')!, recs, goEvent);
  let laidMap = '';                         // the overlay on the ground now ("auto" follows the year)
  on((s, ch) => {
    // set() reports every key it was given, changed or not: compare values, or picking an event (which passes the mode
    // along) ends its own lighting at once and the night scene with it
    if (factEvent && ((('year' in ch) && Math.round(s.year) !== factEvent.year) || (('date' in ch) && factEvent.date && s.date !== factEvent.date))) factEvent = null;
    if (eventLight && ((('year' in ch) && Math.round(s.year) !== eventLight.year) || (('date' in ch) && s.date !== eventLight.date) || (('mode' in ch) && s.mode !== 'live'))) endEventLight();
    if ('year' in ch) { uYear.value = s.year; statues.update(s.year); walk.setYear(s.year); env.update(s.year); splats.update(s.year); }
    if ('color' in ch) uColorMode.value = { real: 0, period: 1, confidence: 2 }[s.color];
    if ('selected' in ch) uSelected.value = s.selected;
    if ('overlay' in ch || ('year' in ch && s.overlay === 'auto')) {
      const id = overlayFor(s.overlay, s.year);
      if (id !== laidMap) {
        laidMap = id;
        if (id === 'none') { env.overlayNode.value = blank; uOverlayOpacity.value = 0; }
        else loadTex(id).then(t => { if (laidMap !== id) return; env.overlayNode.value = t; uOverlayOpacity.value = state.overlayOpacity; });
      }
    }
    if ('overlayOpacity' in ch && laidMap !== 'none') uOverlayOpacity.value = s.overlayOpacity;
    if ('mode' in ch || 'tiltShift' in ch) applyMode();
    if (('date' in ch || 'hour' in ch) && s.mode === 'live') refreshLive(true);
    panels.update(ch); timeline.update();
  });

  // the user's hand on the view: a scene that frames itself waits until 4 s after the last drag or wheel
  let camHeld = false, camHeldT = 0;
  const holdCam = () => { camHeld = true; clearTimeout(camHeldT); camHeldT = window.setTimeout(() => (camHeld = false), 4000); };
  renderer.domElement.addEventListener('pointerdown', holdCam); renderer.domElement.addEventListener('wheel', holdCam, { passive: true });
  // picking
  const ray = new THREE.Raycaster(); const ndc = new THREE.Vector2(); let down = [0, 0];
  renderer.domElement.addEventListener('pointerdown', e => (down = [e.clientX, e.clientY]));
  renderer.domElement.addEventListener('pointerup', e => {
    if (e.button !== 0) return;                                          // right button: pan or the hide button
    if (Math.hypot(e.clientX - down[0], e.clientY - down[1]) > 4) return;
    // with something selected, a click on the map only deselects; the next click picks again
    if (panels.hasSelection()) { panels.clearSelection(); return; }
    const r = renderer.domElement.getBoundingClientRect();
    ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1); ray.setFromCamera(ndc, camera);
    const hit = pickHit(mesh, recs, ray, state.year), lm = landmarks.pick(ray);
    const id = lm && lm.dist <= hit.dist + 0.5 ? lm.id : hit.id;          // landmark models are picked like buildings
    const site = river.pickSite(ray);
    if (site && (id < 0 || site.dist < Math.min(hit.dist, lm?.dist ?? Infinity))) { set({ selected: -1 }); panels.showSite(site.info); }
    else if (id >= 0) { panels.showSite(null); set({ selected: id }); }
    else {                                              // open ground: the street or square there, if it exists in this year
      const g = ray.intersectObject(env.terrain, false)[0];
      const code = g ? panels.streetAt(g.point.x, g.point.z, Math.round(state.year)) : null;
      if (code) panels.showStreet(code); else { panels.showSite(null); set({ selected: -1 }); }
    }
  });
  // right click on a building seen up close (camera under 60 m over the ground, the building within 80 m): a button that takes
  // it out of the view until the camera moves away (scene/xray.ts) – for a look at a detail across a narrow street
  const hidePop = document.getElementById('hide-pop')!, hideBtn = document.getElementById('hide-btn')!, hiddenChip = document.getElementById('hidden-chip')!;
  let rDown = [0, 0], hideTarget: (() => void) | null = null;
  renderer.domElement.addEventListener('pointerdown', e => { if (e.button === 2) rDown = [e.clientX, e.clientY]; hidePop.hidden = true; });
  renderer.domElement.addEventListener('contextmenu', e => {
    e.preventDefault();
    if (Math.hypot(e.clientX - rDown[0], e.clientY - rDown[1]) > 4) return;          // that was a pan
    const r = renderer.domElement.getBoundingClientRect();
    ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1); ray.setFromCamera(ndc, camera);
    const above = camera.position.y - height(camera.position.x, camera.position.z);
    const hit = pickHit(mesh, recs, ray, state.year), lm = landmarks.pick(ray);
    const useLm = lm && lm.dist <= hit.dist + 0.5, dist = useLm ? lm!.dist : hit.dist;
    if (above > 60 || dist > 80 || (!useLm && hit.id < 0)) return;
    hideTarget = useLm ? () => xray.hideObject(lm!.obj) : () => xray.hideCity(hit.id);
    hidePop.style.left = e.clientX + 'px'; hidePop.style.top = e.clientY + 'px'; hidePop.hidden = false;
  });
  hideBtn.onclick = () => { hideTarget?.(); hideTarget = null; hidePop.hidden = true; };
  xray.onHidden(n => { hiddenChip.hidden = n === 0; hiddenChip.textContent = n === 1 ? '1 building hidden · show it' : `${n} buildings hidden · show them`; });
  hiddenChip.onclick = () => xray.showAll();
  // compass: the rose turns with the view (north up when looking north); the camera's height over the ground under it
  const rose = document.getElementById('compass-rose')!, compH = document.getElementById('compass-h')!, fwd = new THREE.Vector3();
  let compT = 0;
  const compass = (dt: number) => {
    if ((compT += dt) < 0.08) return; compT = 0;
    camera.getWorldDirection(fwd);
    const head = Math.atan2(fwd.x, -fwd.z) * 180 / Math.PI;                       // 0 = looking north, 90 = east
    rose.setAttribute('transform', `rotate(${(-head).toFixed(1)})`);
    const hgt = camera.position.y - height(camera.position.x, camera.position.z);
    compH.textContent = `${hgt < 100 ? hgt.toFixed(0) : Math.round(hgt / 10) * 10} m`;
  };
  addEventListener('keydown', e => {
    if ((e.target as HTMLElement).tagName === 'INPUT') return;
    if (e.code === 'Space') { e.preventDefault(); set({ playing: !state.playing }); }
    if (e.code === 'ArrowRight' || e.code === 'ArrowLeft') set({ year: Math.min(2026, Math.max(-800, Math.round(state.year) + (e.code === 'ArrowRight' ? 1 : -1) * (e.shiftKey ? 25 : 1))) });
  });

  // initial apply
  set({ ...state, selected: -1, overlay: state.overlay });
  done(); loading.classList.add('done');
  layout.init();
  document.getElementById('menu-maps')!.onclick = () => { openGallery(materialsFor(['map'])); document.getElementById('menu')!.hidden = true; };
  document.getElementById('menu-help')!.onclick = () => { view.toggleHelp(); document.getElementById('menu')!.hidden = true; };
  toast(matchMedia('(pointer: coarse)').matches ? 'One finger moves · pinch to zoom · two fingers rotate · ☰ for help'
    : 'Ctrl + drag (or right-drag) rotates and tilts · press H for all view controls');

  /** Share of the view's width hidden by the left dock (0 on phones, where panels sit in a bottom sheet). */
  const dockL = document.getElementById('dock-l')!;
  function leftCover() {
    if (layout.phone) return 0;
    let r = 0;
    for (const el of Array.from(dockL.children) as HTMLElement[]) if (!el.hidden) { const b = el.getBoundingClientRect(); if (b.width > 0 && b.height > 40) r = Math.max(r, b.right); }
    return Math.min(0.5, r / innerWidth);
  }
  // ---- loop ----
  const timer = new THREE.Timer(); let camSave = 0;
  renderer.setAnimationLoop(() => {
    timer.update(); const dt = Math.min(timer.getDelta(), 0.1);
    if (state.playing) {
      const gap = quietAhead(state.year), fast = gap > QUIET && state.speed < FAST;
      tlEl.classList.toggle('fast', fast);
      // rush, but land a couple of years before the next change so it is seen at the chosen speed
      let y = state.year + (fast ? FAST : state.speed) * dt;
      if (fast) y = Math.min(y, state.year + gap - 2);
      if (y >= 2026) set({ year: 2026, playing: false }); else set({ year: y });
    } else tlEl.classList.remove('fast');
    view.update(dt); controls.update(); uTime.value += dt; city.follow(controls.target.x, controls.target.z);
    stage.setSun(state.mode === 'live' ? scenes.lightHour() ?? state.hour : state.hour, state.year); uSky.value.copy(scene.background as THREE.Color);
    { // haze scales with zoom: close views stay crisp, the whole valley only fades at the horizon
      const d = camera.position.distanceTo(controls.target), f = scene.fog as THREE.Fog;
      if (q.tier === 'low' || q.tier === 'min') { f.near = Math.max(120, d * 0.7); f.far = Math.min(q.cityRadius * 0.95, Math.max(600, d * 2.2 + 300)); }   // small devices: a tight circle of focus, the rest in haze
      else { f.near = Math.max(900, d * 1.6); f.far = Math.max(5000, d * 7 + 3000); }
      stage.fitClip(f.far); }
    xray.update(dt, state.year); compass(dt); if (!document.hidden && dt < 1) governor.tick(dt);
    river.update(dt, state.year, true, camera.position.y - controls.target.y); streetHL.update(dt); landmarks.update(Math.floor(state.year) + dayFrac(state.date));
    landmarks.paint(state.mode !== 'sources' || state.color === 'real' ? null : state.color === 'confidence' ? (r => CONF_COLORS[r.conf]) : (r => { const p = periodOf(r.start); return uPeriodPick.value >= 0 && p !== uPeriodPick.value ? '#a3a09b' : PERIODS[p]?.color ?? '#888'; }));   // a period picked in the legend: the others grey
    river.setHighlight(state.mode === 'sources' && state.color !== 'real' ? (state.color === 'confidence' ? CONF_COLORS.inferred : SOURCE_LAYERS[0].color) : null);
    riverPeople.setContext(Math.round(state.year), controls.target, 2000); riverPeople.update(dt, camera.position);
    squarePeople.setContext(Math.round(state.year), controls.target, 2000);
    const crowd = state.mode !== 'sources' && !state.playing;   // while the years run, nobody: the crowd would be rebuilt every year
    squareLife.update(dt, camera.position, controls.target, Math.round(state.year), state.hour, crowd, state.mode === 'live' ? scenes.activeAt : null);
    if (crowd && state.mode !== 'live') { people.setContext(Math.round(state.year), controls.target, 360); people.update(dt, camera.position); squarePeople.update(dt, camera.position); }
    people.setVisible?.(crowd); squarePeople.setVisible?.(crowd);
    if (state.mode === 'live') {
      refreshLive();
      if (!scenes.paused) { people.update(dt, camera.position); squarePeople.update(dt, camera.position); scenes.update(dt); }      // paused: everything stands still
      const f = scenes.follow();                       // keep a moving subject in view, the user still orbits and zooms
      if (f && !scenes.paused) { const k = Math.min(1, dt * 1.5), dx = (f.x - controls.target.x) * k, dz = (f.z - controls.target.z) * k;
        controls.target.x += dx; controls.target.z += dz; camera.position.x += dx; camera.position.z += dz; }
      // the left dock (event card, info card) covers part of the view on wide screens: a scene that frames itself is
      // fitted into the free part, and its subject shifted to that part's middle
      const free = leftCover(), aspect = camera.aspect * (1 - free);
      const g = scenes.camGoal(aspect);                // a scene that frames itself (the flood, the David): ease towards its view
      if (g && !camHeld) {
        const ax0 = g[4] ?? 0, right = new THREE.Vector3(Math.cos(ax0), 0, -Math.sin(ax0)), shift = 0.573 * g[2] * camera.aspect * free / 2;
        g[0] -= right.x * shift; g[1] -= right.z * shift;
        const k = Math.min(1, dt * 0.9), tgt = new THREE.Vector3(g[0], height(g[0], g[1]), g[1]);
        controls.target.lerp(tgt, k);
        const dir = camera.position.clone().sub(controls.target); let az = Math.atan2(dir.x, dir.z);
        if (g[4] != null) { let da = g[4] - az; da = Math.atan2(Math.sin(da), Math.cos(da)); az += da * k; }   // the scene's heading
        const want = controls.target.clone().add(new THREE.Vector3().setFromSphericalCoords(g[2], g[3], az));
        camera.position.lerp(want, k);
      }
    }
    // scripted scenes narrate while they play; open-ended ones (the market, calcio) only when picked from the events list
    { const n = state.mode === 'live' ? scenes.narration() : null, show = n && (scenes.duration() > 0 || scenes.active === liveEvent);
      narration.set(show ? n : factEvent); }
    { const D = scenes.duration(); panels.player(state.mode === 'live' && D > 0 ? { title: sceneTitle, t: scenes.time, dur: D, paused: scenes.paused } : null); }
    // the camera goes into the link (a quarter second after it settles): a shared link opens on the same view
    if ((camSave += dt) > 0.25) { camSave = 0; panels.legend();
      const c = [...camera.position.toArray(), ...controls.target.toArray()].map(v => Math.round(v * 10) / 10);
      if (c.some((v, i) => v !== state.cam[i])) { state.cam = c; touchHash(); } }
    { // never under the ground: with the tilt down to the horizontal the camera could sink into a slope
      const gy = height(camera.position.x, camera.position.z) + 1.7;
      if (camera.position.y < gy) camera.position.y = gy;
    }
    pipeline.render();
  });
}
main().catch(e => { console.error(e); say('Error: ' + (e?.message ?? e)); });
