import * as THREE from 'three/webgpu';
import { state, set, on } from './state';
import { createStage, uTilt } from './scene/stage';
import { loadCity, uYear, uColorMode, uSelected, pickHit, periodOf } from './scene/city';
import { loadLandmarks, LANDMARKS } from './scene/landmarks';
import { createStreetHighlight } from './scene/streetview';
import { loadEnvironment, makeHeight, uOverlayOpacity, uTime, uSky } from './scene/environment';
import { createSplats } from './scene/splats';
import { loadTextures, loadProps } from './scene/assets';
import { createViewControls } from './scene/view';
import { createPeople } from './sim/people';
import { createScenes } from './sim/scenes';
import { createRiver } from './sim/river';
import { createTimeline } from './ui/timeline';
import { createPanels, toast } from './ui/panels';
import { layout } from './ui/layout';
import { open as openGallery, materialsFor } from './ui/gallery';
import { EVENTS, CONF_COLORS, SOURCE_LAYERS, PERIODS } from './data/history';
import { walk } from './sim/walk';
/** 'MM-DD' → fraction of the year, for parts dated to the day (landmark names "part@1504_160-…"). */
const dayFrac = (d: string) => { const [m, dd] = (d || '01-01').split('-').map(Number); return (([0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334][m - 1] ?? 0) + dd - 1) / 366; };

const DATA = './data';
const loading = document.getElementById('loading')!;
// loading screen: one line per step, ticked off with its time when the next one starts
const steps = document.createElement('ul'); steps.className = 'steps'; loading.querySelector('div')!.appendChild(steps);
let cur: { li: HTMLLIElement; t0: number } | null = null;
function done(extra = '') {
  if (!cur) return;
  cur.li.classList.add('ok'); cur.li.querySelector('i')!.textContent = `${extra ? extra + ' · ' : ''}${((performance.now() - cur.t0) / 1000).toFixed(1)} s`; cur = null;
}
const say = (t: string) => {
  done(); loading.querySelector('p')!.textContent = t;
  const li = document.createElement('li'); li.innerHTML = `<span></span><i>…</i>`; li.querySelector('span')!.textContent = t;
  steps.appendChild(li); cur = { li, t0: performance.now() };
};

async function main() {
  const stage = await createStage(document.getElementById('app')!);
  const { scene, camera, controls, renderer, pipeline } = stage;
  say('Materials and the 2017 orthophoto');
  const texLoader = new THREE.TextureLoader();
  const loadTex = (u: string) => texLoader.loadAsync(`${DATA}/${u}`).then(t => { t.flipY = false; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; t.generateMipmaps = true; return t; });
  const [ortho, mtex] = await Promise.all([loadTex('ortho2017.jpg'), loadTextures('./textures')]);
  const blank = new THREE.DataTexture(new Uint8Array([0, 0, 0, 0]), 1, 1); blank.needsUpdate = true;
  say('Study area and street network');
  const [meta, streets] = await Promise.all(['meta', 'streets'].map(n => fetch(`${DATA}/${n}.json`).then(r => r.json())));
  meta.streets = streets;
  done(`${((meta.bbox_utm[2] - meta.bbox_utm[0]) / 1000).toFixed(1)} × ${((meta.bbox_utm[3] - meta.bbox_utm[1]) / 1000).toFixed(1)} km, ${streets.edges.length.toLocaleString()} street segments`);
  say('Dated buildings and structures');
  const { mesh, recs, hide } = await loadCity(DATA, ortho, mtex);
  done(`${recs.length.toLocaleString()} structures`);
  say('Landmark models');
  const landmarks = await loadLandmarks(scene, mtex, recs); hide(landmarks.replaced, landmarks.replacedIds);
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
  const env = await loadEnvironment(DATA, meta, ortho, blank, mtex);
  scene.add(env.group);
  const [H, HW] = await Promise.all(['terrain', 'wide'].map(async n => new Float32Array(await (await fetch(`${DATA}/${n}.f32`)).arrayBuffer())));
  const height = makeHeight(meta, H, HW);
  done(`${meta.trees.count.toLocaleString()} trees`);
  say('People and costumes');
  const people = await createPeople(scene, streets, 280);
  const riverPeople = await createPeople(scene, streets, 40, { walkers: false });
  say('Props, boats and animals');
  const props = await loadProps(mtex, './models');
  const scenes = createScenes(scene, people, height, props, streets.squares);
  scenes.setBridges(env.bridges);
  // walkable ground: building footprints by year (pipeline 20), tree trunks, scene props – see sim/walk.ts
  say('Walkable ground');
  const foot = await fetch(`${DATA}/footprints.u16`).then(r => r.ok ? r.arrayBuffer() : null).catch(() => null);
  walk.init(recs, foot ? new Uint16Array(foot) : null, env.treeData); walk.setYear(state.year);
  if ((import.meta as any).env?.DEV || location.hostname === 'localhost') Object.assign(window as any, { __fs: { scene, scenes, people, camera, controls, walk } });   // dev-only debug handle
  const view = createViewControls(camera, controls, renderer.domElement);
  say('River life: boats, fishermen, birds');
  const riverAxis = (await (await fetch(`${DATA}/river.json`)).json()).axis;
  const river = createRiver(scene, props, riverPeople, height, riverAxis, env.bridges, env.weirs.map((w: any) => w.mesh.userData), env.water.geometry);
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
    controls.maxPolarAngle = live ? 1.45 : 1.15; controls.minDistance = live ? 8 : 25;
    uTilt.value = state.tiltShift && state.mode === 'overview' ? 1 : (state.tiltShift && live ? 0.35 : 0);
    people.setEnabled(live); riverPeople.setEnabled(true);   // river and pre-urban figures show in every mode
    if (live) {
      refreshLive(true, true);
    } else scenes.clear();
  }
  let pendingEvent: any = null;
  function refreshLive(force = false, frame = false) {
    if (state.mode !== 'live') return;
    const changed = people.setContext(Math.round(state.year), controls.target, 360);
    if (changed || force || pendingEvent) {
      const s = scenes.evaluate(state.year, state.date, state.hour, (x, z, az, dist, pitch) => flyTo(x, z, dist ?? 110, pitch ?? 0.82, az), pendingEvent ?? undefined, frame);
      if (frame && !s) flyTo(controls.target.x, controls.target.z, 110, 0.95);
      pendingEvent = null;
      panels.liveNote(s === 'calcio' ? 'Calcio storico in Piazza Santa Croce' : s === 'market' ? 'Market day in Mercato Vecchio' : s === 'scoppio' ? 'Scoppio del Carro in Piazza del Duomo'
        : s === 'david' ? 'The David on its way to Piazza della Signoria (14–18 May 1504, route presumed)' : s === 'davidWait' ? 'The David by the palace door, waiting to be raised onto the ringhiera (8 June 1504)'
        : s === 'ponti1944' ? 'The Night of the Bridges, 3–4 August 1944 (sequence compressed)' : 'Everyday streets');
    }
  }
  // a night event (e.g. the Night of the Bridges at 23:00) sets the clock to night; once the user moves on (another year,
  // date or mode) the previous daytime hour comes back
  let nightRestore: { hour: number; year: number; date: string } | null = null;
  function goEvent(i: number) {
    const e = EVENTS[i];
    const night = e.hour != null && (e.hour >= 20 || e.hour < 6);
    if (night) nightRestore = { hour: nightRestore?.hour ?? (state.hour >= 7 && state.hour <= 18 ? state.hour : 11), year: e.year, date: e.date ?? state.date };
    else if (nightRestore) { set({ hour: nightRestore.hour }); nightRestore = null; }
    set({ year: e.year, date: e.date ?? state.date, hour: e.hour ?? state.hour, playing: false, mode: e.live ? 'live' : state.mode });
    if (e.live) { pendingEvent = e; refreshLive(true); } else flyTo(e.at[0], e.at[1], 600, 0.85);
    panels.showEvent(i);
  }

  // ---- UI ----
  say('Street names and house numbers');
  const addresses = await fetch(`${DATA}/addresses.json`).then(r => r.ok ? r.json() : undefined).catch(() => undefined);
  const streetHL = createStreetHighlight(scene, height);
  const panels = createPanels(recs, { flyTo, event: goEvent, backend: stage.backend, layerCount: id => id === 'A07' ? river.ancientCount() : 0, addresses,
    highlightStreet: code => streetHL.show(code && addresses ? addresses.streets[code] : null), squares: streets.squares,
    landmarks: [
      ...LANDMARKS.filter(l => l.replaces[0] && !l.members).map(l => ({ name: l.replaces[0], x: l.at[0], z: l.at[1], from: l.from ?? 1300 })),
      // models holding several buildings (the walls): one entry per gate / tower, where its record stands
      ...LANDMARKS.flatMap(l => (l.members ?? []).map(m => { const r = recs.find(r => r.name === m.name); return r ? { name: m.name, x: r.c[0], z: r.c[1], from: m.from ?? r.start } : null; }))
        .filter((e): e is { name: string; x: number; z: number; from: number } => !!e),
    ] });
  const timeline = createTimeline(document.getElementById('timeline')!, recs, goEvent);
  on((s, ch) => {
    if (nightRestore && ((('year' in ch) && Math.round(s.year) !== nightRestore.year) || (('date' in ch) && s.date !== nightRestore.date) || (('mode' in ch) && s.mode !== 'live'))) {
      const h = nightRestore.hour; nightRestore = null; queueMicrotask(() => set({ hour: h }));
    }
    if ('year' in ch) { uYear.value = s.year; walk.setYear(s.year); env.update(s.year); splats.update(s.year); }
    if ('color' in ch) uColorMode.value = { real: 0, period: 1, confidence: 2 }[s.color];
    if ('selected' in ch) uSelected.value = s.selected;
    if ('overlay' in ch) {
      if (s.overlay === 'none') { env.overlayNode.value = blank; uOverlayOpacity.value = 0; }
      else loadTex(s.overlay).then(t => { env.overlayNode.value = t; uOverlayOpacity.value = s.overlayOpacity; });
    }
    if ('overlayOpacity' in ch && s.overlay !== 'none') uOverlayOpacity.value = s.overlayOpacity;
    if ('mode' in ch || 'tiltShift' in ch) applyMode();
    if (('date' in ch || 'hour' in ch) && s.mode === 'live') refreshLive(true);
    panels.update(ch); timeline.update();
  });

  // picking
  const ray = new THREE.Raycaster(); const ndc = new THREE.Vector2(); let down = [0, 0];
  renderer.domElement.addEventListener('pointerdown', e => (down = [e.clientX, e.clientY]));
  renderer.domElement.addEventListener('pointerup', e => {
    if (Math.hypot(e.clientX - down[0], e.clientY - down[1]) > 4) return;
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
    : 'Ctrl + mouse rotates, Ctrl + Shift + mouse moves · press H for all view controls');

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
    view.update(dt); controls.update(); uTime.value += dt;
    stage.setSun(state.mode === 'live' ? state.hour : 10.5, state.year); uSky.value.copy(scene.background as THREE.Color);
    { // haze scales with zoom: close views stay crisp, the whole valley only fades at the horizon
      const d = camera.position.distanceTo(controls.target), f = scene.fog as THREE.Fog;
      f.near = Math.max(900, d * 1.6); f.far = Math.max(5000, d * 7 + 3000); }
    river.update(dt, state.year, true); streetHL.update(dt); landmarks.update(Math.floor(state.year) + dayFrac(state.date));
    landmarks.paint(state.mode !== 'sources' || state.color === 'real' ? null : state.color === 'confidence' ? (r => CONF_COLORS[r.conf]) : (r => PERIODS[periodOf(r.start)]?.color ?? '#888'));
    river.setHighlight(state.mode === 'sources' && state.color !== 'real' ? (state.color === 'confidence' ? CONF_COLORS.inferred : SOURCE_LAYERS[0].color) : null);
    riverPeople.setContext(Math.round(state.year), controls.target, 2000); riverPeople.update(dt);
    if (state.mode === 'live') {
      refreshLive(); people.update(dt); scenes.update(dt);
      const f = scenes.follow();                       // keep a moving subject in view, the user still orbits and zooms
      if (f) { const k = Math.min(1, dt * 1.5), dx = (f.x - controls.target.x) * k, dz = (f.z - controls.target.z) * k;
        controls.target.x += dx; controls.target.z += dz; camera.position.x += dx; camera.position.z += dz; }
    }
    if ((camSave += dt) > 1) { camSave = 0; panels.legend(); state.cam = [...camera.position.toArray(), ...controls.target.toArray()].map(v => Math.round(v)); }
    pipeline.render();
  });
}
main().catch(e => { console.error(e); say('Error: ' + (e?.message ?? e)); });
