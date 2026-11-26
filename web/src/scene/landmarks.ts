// Hand-built landmark models (blender/scripts/build_<name>.py) that replace the LiDAR shell of their building.
// Each model is in its own frame (origin = a measured reference point, X east along the building axis, Y up) and every
// node is dated in its name: "<part>@<from>-<to>" – shown when from <= year < to. Materials come from
// models/landmarks/<name>_materials.json (same fs_* tables as the prop library, triplanar textures).
import * as THREE from 'three/webgpu';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { buildMaterials, type TexSet } from './assets';
import type { Rec } from './city';

export interface LandmarkDef {
  file: string; replaces: string[];            // names of the city records whose shell this model replaces
  at: [number, number]; rot: number;           // scene x/z of the model origin, rotation about Y (radians)
  ground?: number; source: string; from?: number;   // from: first year it stands (for search)
  clear?: [number, number][];                  // scene x/z polygon: every record whose centre lies inside is replaced too
  clearFile?: boolean;                         // more such polygons in models/landmarks/<file>_clear.json
  ids?: number[];                              // single records replaced by id (stray shells no outline catches)
  /** A model holding several buildings: nodes named "<key>@…" / "<key>_…" belong to the record `name` (its card on click). */
  members?: { key: string; name: string; from?: number; to?: number }[];
}
const inPoly = (x: number, z: number, P: [number, number][]) => {
  let c = false;
  for (let i = 0, j = P.length - 1; i < P.length; j = i++) {
    const [xi, zi] = P[i], [xj, zj] = P[j];
    if ((zi > z) !== (zj > z) && x < (xj - xi) * (z - zi) / (zj - zi) + xi) c = !c;
  }
  return c;
};
/** Registry: measured placement (see docs/landmarks/*.md). */
export const LANDMARKS: LandmarkDef[] = [
  { file: 'duomo', replaces: ['Cattedrale di Santa Maria del Fiore', 'Duomo di Firenze'], at: [138.5, -150.5], rot: -0.0336,
    source: 'Landmark model v1 (Blender, measured on LiDAR 2023; dated building phases)' },
  { file: 'campanile', replaces: ['Campanile di Giotto'], at: [38.3, -116.7], rot: 0.009,
    source: 'Landmark model v1 – Campanile (Blender, measured on LiDAR 2023; Giotto / Pisano / Talenti phases)' },
  { file: 'baptistery', replaces: ['Battistero di San Giovanni'], at: [-14.0, -149.0], rot: 0.023,
    source: 'Landmark model v1 – Baptistery (Blender, measured on LiDAR 2023; dated phases and doors)' },
  { file: 'palazzo_vecchio', replaces: ['Palazzo Vecchio'], at: [73.5, 276.5], rot: 0,
    source: 'Landmark model v1 – Palazzo Vecchio (Blender, measured on LiDAR 2023 + OSM outline; Arnolfo block, tower, Salone, ducal wings)' },
  { file: 'ponte_vecchio', replaces: [], at: [-151.55, 425.45], rot: 0, ground: 0,
    clear: [[-117.2, 386.7], [-160.0, 472.6], [-184.1, 460.6], [-141.3, 374.7]],
    source: 'Landmark model v1 – Ponte Vecchio 1345 with shops and Vasari Corridor (Blender, measured on LiDAR 2023)' },
  { file: 'santa_croce', replaces: ['Basilica di Santa Croce'], at: [576.5, 335.0], rot: -0.4960, ground: 7.6,
    clear: [[661.5, 406.5], [673.5, 406.5], [673.5, 418.5], [661.5, 418.5]],          // Baccani's bell tower (record misdated 1905)
    source: 'Landmark model v1 – Santa Croce (Blender, measured on LiDAR 2023 + OSM outline; Arnolfo church, Matas façade, Baccani tower)' },
  { file: 'santa_maria_novella', replaces: ['Basilica di Santa Maria Novella', 'Santa Maria Novella'], at: [-476.0, -254.6], rot: 0, ground: 5.9,
    clear: [[-503.5, -339.5], [-494.5, -339.5], [-494.5, -330.0], [-503.5, -330.0]],          // bell tower
    source: 'Landmark model v1 – Santa Maria Novella (Blender, measured on LiDAR 2023 + OSM outline; Gothic church, Alberti façade, Talenti tower)' },  { file: 'orsanmichele', replaces: ['Chiesa di Orsanmichele'], at: [-9.0, 121.6], rot: 0, ground: 10.0,
    source: 'Landmark model v1 – Orsanmichele (Blender, measured on LiDAR 2023 + OSM outline; loggia, granary floors, tabernacles)' },
  { file: 'bargello', from: 1255, replaces: ['Palazzo del Bargello', 'Museo Nazionale del Bargello', 'Bargello'], at: [226.6, 136.0], rot: 0, ground: 8.5,
    clear: [[223.2, 129.7], [222.9, 136.3], [217.5, 168.5], [236.6, 171.1], [285.3, 171.0], [286.2, 134.9], [244.4, 131.2], [230.9, 130.0]],   // OSM way 43837065
    source: 'Landmark model v1 – Bargello (Blender, measured on LiDAR 2023 + OSM outline; Volognana tower, wings 1255–1345, courtyard, Verone, staircase)' },
  { file: 'loggia_lanzi', from: 1382, replaces: ['Loggia dei Lanzi', 'Loggia della Signoria'], at: [22.8, 275.8], rot: -0.3696, ground: 9.6,
    clear: [[18.3, 288.8], [22.8, 275.8], [59.2, 289.9], [55.1, 301.4], [44.1, 297.2], [43.5, 298.7]],   // OSM way 43284457
    source: 'Landmark model v1 – Loggia dei Lanzi (Blender, measured on LiDAR 2023 + OSM outline; loggia 1376–82, Virtues, terrace, statues 1506–1865)' },
  { file: 'uffizi', from: 1560, replaces: ['Galleria degli Uffizi', 'Uffizi', 'Palazzo degli Uffizi'], at: [21.5, 437.5], rot: -0.2947, ground: 8.8,
    clear: [[-8.1, 442.1],  [47.4, 459.0],  [92.2, 311.6],  [36.7, 294.8]],   // OSM way 477279033 (the wings and the piazzale between them)
    source: 'Landmark model v1 – Uffizi (Blender, measured on LiDAR 2023 + OSM outline; wings 1565–80, Arno serliana, statues 1850, quarter and San Pier Scheraggio before 1560)' },
  // San Lorenzo and Palazzo Medici Riccardi: absolute scene coordinates (like the walls), heights above their ground
  { file: 'san_lorenzo', from: 393, replaces: ['Basilica di San Lorenzo', 'Cappella dei Principi'], at: [0, 0], rot: 0, ground: 7.8,
    clear: [[-131.8, -354.2], [-137.3, -329.8], [-144.5, -331.6], [-148.0, -313.2], [-129.1, -309.4], [-125.5, -321.5], [-108.8, -317.8],
      [-106.8, -326.9], [-72.3, -319.2], [-59.4, -316.7], [-52.5, -347.5], [-100.9, -358.3], [-100.3, -369.0], [-113.3, -371.7], [-110.9, -382.6],
      [-124.2, -385.4], [-141.6, -371.4], [-157.7, -374.7], [-179.6, -355.0], [-166.6, -333.9], [-150.4, -331.1]],   // OSM ways 599900778 + 24883267
    ids: [9862, 15265],   // the cloister / library shell and a "demolished" 1830s tracing inside the library range
    members: [{ key: 'principi', name: 'Cappella dei Principi', from: 1604 }],
    source: 'Landmark model v1 – San Lorenzo (Blender, measured on LiDAR 2023 + OSM outline; Old Sacristy 1428, church 1461, cloister, New Sacristy, Laurentian Library, Cappella dei Principi 1604–1640, bell tower 1740)' },
  { file: 'medici_riccardi', from: 1445, replaces: ['Palazzo Medici Riccardi', 'Palazzo Medici'], at: [0, 0], rot: 0, ground: 8.0,
    clear: [[-9.1, -361.0], [-5.6, -380.4], [-0.9, -399.3], [5.6, -431.0], [22.8, -425.4], [52.6, -415.5], [71.1, -408.5], [61.3, -384.5], [40.4, -338.7]],   // OSM relation 1379977
    source: 'Landmark model v1 – Palazzo Medici Riccardi (Blender, measured on LiDAR 2023 + OSM outline; Michelozzo 1445–52, kneeling windows 1517, Riccardi extension 1689)' },
  // Vasari Corridor beyond the bridge (the bridge stretch is in ponte_vecchio): absolute scene coordinates, heights in scene y
  { file: 'corridoio', from: 1565, replaces: ['Corridoio Vasariano'], at: [0, 0], rot: 0, ground: 0,
    ids: [3281, 3359, 2114, 1987, 1986, 1985, 2011, 3290, 3291],   // Lungarno loggia shell, Via de' Bardi stretch, Oltrarno strip pieces, Torre dei Mannelli
    members: [{ key: 'mannelli', name: 'Torre dei Mannelli', from: 1249 }],
    source: 'Landmark model v1 – Corridoio Vasariano (Blender; OSM outline, LiDAR 2023 heights; 1565, Lungarno shops 1572–1885, Via de\' Bardi stretch destroyed 1944 and rebuilt 1950, Torre dei Mannelli)' },
  // Palazzo Pitti (palace, rondò, Meridiana) and the Boboli garden with Forte Belvedere: absolute scene coordinates
  { file: 'pitti', from: 1458, replaces: ['Palazzo Pitti'], at: [0, 0], rot: 0, ground: 0,
    clear: [[-491.3, 783.4], [-503.8, 766.0], [-508.2, 768.9], [-512.1, 763.7], [-507.9, 761.0], [-512.6, 753.7], [-497.9, 743.5], [-472.1, 784.0], [-400.9, 738.0], [-327.2, 689.4], [-328.3, 687.9], [-354.6, 649.9], [-340.8, 640.8], [-336.7, 647.0], [-320.6, 671.4], [-319.3, 673.3], [-321.0, 674.5], [-317.3, 680.5], [-311.6, 688.8], [-302.4, 703.4], [-339.6, 728.2], [-324.1, 751.1], [-321.3, 755.3], [-334.3, 764.0], [-324.4, 779.0], [-343.7, 790.7], [-335.7, 803.4], [-336.5, 803.9], [-353.6, 814.6], [-355.3, 815.7], [-364.5, 820.6], [-371.9, 809.8], [-379.9, 814.6], [-391.6, 821.7], [-401.4, 807.3], [-413.0, 812.5], [-419.1, 803.0], [-420.9, 804.0], [-423.3, 805.4], [-461.9, 828.8], [-478.3, 801.5]],   // OSM relation 1637338
    ids: [3317, 15772],   // Palazzina della Meridiana, a tracing inside the palace
    members: [{ key: 'meridiana', name: 'Palazzina della Meridiana', from: 1776 }],
    source: 'Landmark model v1 – Palazzo Pitti (Blender; OSM outline, LiDAR 2023 heights; Luca Pitti 1458, Ammannati 1560, Parigi 1618–1640, rondò 1765/1783, Meridiana 1776)' },
  { file: 'boboli', from: 1550, replaces: ['Forte di Belvedere'], at: [0, 0], rot: 0, ground: 0,
    ids: [1990, 2009, 1988, 1989, 1644, 1573],   // fort and palazzina shells, amphitheatre shells, Grotta del Buontalenti, Kaffeehaus (misdated records)
    members: [{ key: 'grotta_buontalenti', name: 'Grotta del Buontalenti', from: 1583 }, { key: 'kaffeehaus', name: 'Kaffeehaus del Giardino di Boboli', from: 1776 },
      { key: 'forte_belvedere', name: 'Forte di Belvedere', from: 1590 }],
    source: 'Landmark model v1 – Boboli and Forte Belvedere (Blender; OSM outlines, LiDAR 2023; amphitheatre 1599–1637, Grotta del Buontalenti 1583, Kaffeehaus 1776, Neptune basin 1778, Forte Belvedere 1590)' },
  // the sixth circle of walls: absolute scene coordinates, one model for walls, towers, gates, bastions and the Fortezza
  { file: 'mura', replaces: ["Cerchia d'Arnolfo", 'Cerchia di Arnolfo', 'Baluardo del Mongibello', 'Baluardo della serpe', "Baluardo a' tre canti", 'Baluardo a San Gallo',
      // the earlier circles, drawn by the model on the ground line (the records stood on one height and sank into the slopes)
      'citywalls', 'mura carolinge', 'mura matildine', 'prima cerchia comunale', 'prima cerchia comunale 1172', 'prima cerchia comunale (ampliamento1260)'],
    at: [0, 0], rot: 0, ground: 0, clearFile: true, ids: [2462, 1362, 2108],   // stray LiDAR shells on the wall line (records of pipeline step 20)
    members: [
      { key: 'g_romana', name: 'Porta Romana', from: 1326 }, { key: 'g_frediano', name: 'Porta San Frediano', from: 1332 },
      { key: 'g_croce', name: 'Porta alla Croce', from: 1284 }, { key: 'g_prato', name: 'Porta al Prato', from: 1284 },
      { key: 'g_gallo', name: 'Porta San Gallo', from: 1285 }, { key: 'g_niccolo', name: 'Torre San Niccolò', from: 1324 },
      { key: 'g_giorgio', name: 'Porta San Giorgio', from: 1324 }, { key: 'g_zecca', name: 'Torre della Zecca', from: 1320 },
      { key: 'g_serpe', name: 'Torre della Serpe', from: 1320 }, { key: 'g_rosa', name: 'Torrino di Santa Rosa', from: 1324 },
      { key: 'g_miniato', name: 'Porta San Miniato', from: 1320 }, { key: 'g_pinti', name: 'Porta a Pinti', from: 1284, to: 1866 },
      { key: 'g_giustizia', name: 'Porta alla Giustizia', from: 1284, to: 1530 }, { key: 'g_arco', name: 'Arco di Trionfo', from: 1739 },
    ],
    source: 'Landmark model v1 – Le mura (Blender; OSM + OpenHistoricalMap lines, LiDAR 2023 heights; walls 1284–1333, towers lowered 1529, bastions, Fortezza da Basso, Poggi demolitions 1865–70)' },
];

export async function loadLandmarks(scene: THREE.Scene, tex: TexSet, recs: Rec[], base = './models/landmarks') {
  const group = new THREE.Group(); group.name = 'landmarks'; scene.add(group);
  const parts: { obj: THREE.Object3D; from: number; to: number }[] = [];
  const loader = new GLTFLoader();
  const items: { def: LandmarkDef; root: THREE.Object3D; rec?: Rec; members: { key: string; rec?: Rec }[] }[] = [];
  const clearIds: number[] = [];
  for (const def of LANDMARKS) {
    try {
      const [gltf, defs] = await Promise.all([loader.loadAsync(`${base}/${def.file}.glb`), fetch(`${base}/${def.file}_materials.json`).then(r => r.json())]);
      const mats = buildMaterials(defs, tex, THREE.DoubleSide);
      const root = gltf.scene;
      const polys = [...(def.clear ? [def.clear] : []),
        ...(def.clearFile ? await fetch(`${base}/${def.file}_clear.json`).then(r => r.json()).catch(() => []) as [number, number][][] : [])];
      const inside = recs.filter(r => polys.some(P => inPoly(r.c[0], r.c[1], P)) || def.ids?.includes(r.id));
      clearIds.push(...inside.map(r => r.id));
      // members: the record of each gate / tower (prefer the LiDAR shell over a mapped point), dated by the model
      const members = (def.members ?? []).map(m => {
        const rr = recs.filter(r => r.name === m.name).sort((a, b) => +(b.kind === 'building') - +(a.kind === 'building'))[0];
        if (rr && m.from != null) rr.start = m.from;
        if (rr && m.to != null) rr.end = m.to;
        if (rr && !rr.src.includes(def.source)) rr.src = [def.source, ...rr.src];
        return { key: m.key, rec: rr };
      });
      const rec = recs.find(r => r.name === def.replaces[0]) ?? inside.find(r => r.name) ?? inside[0];
      // a landmark found only by its outline takes its name and first year onto the record its card shows
      if (rec && def.replaces[0] && rec.name !== def.replaces[0] && !recs.some(r => r.name === def.replaces[0])) rec.name = def.replaces[0];
      if (rec && def.from != null && rec.name === def.replaces[0]) rec.start = def.from;
      root.position.set(def.at[0], def.ground ?? rec?.ground ?? 8.4, def.at[1]); root.rotation.y = def.rot;
      root.traverse((o: any) => {
        if (o.isMesh) { o.material = mats[o.material.name] ?? o.material; o.castShadow = o.receiveShadow = true; o.userData.mat0 = o.material; }
        // "part@1504_160-1873" – years, optionally with a day of the year (glTF loaders strip dots from node names)
        const m = /@(-?\d+)(?:_(\d+))?-(-?\d+)(?:_(\d+))?/.exec(o.name);
        if (m) parts.push({ obj: o, from: +m[1] + (m[2] ? (+m[2] - 1) / 366 : 0), to: +m[3] + (m[4] ? (+m[4] - 1) / 366 : 0) });
      });
      for (const r of [...recs.filter(r => def.replaces.includes(r.name)), ...inside]) if (!r.src.includes(def.source)) r.src = [def.source, ...r.src];
      group.add(root); items.push({ def, root, rec, members });
    } catch (e) { console.warn('landmark missing', def.file, e); }
  }
  let lastYear = NaN;
  function update(year: number) {
    if (year === lastYear) return; lastYear = year;
    for (const p of parts) p.obj.visible = year >= p.from && year < p.to;
  }
  // Sources view: paint the whole model in its record's period / confidence colour (null = real materials)
  const flat: Record<string, THREE.Material> = {};
  const painted = new Map<object, string | null>();
  function paint(colorOf: ((r: Rec) => string) | null) {
    for (const it of items) {
      const c = colorOf && it.rec ? colorOf(it.rec) : null; if (painted.has(it) && painted.get(it) === c) continue;
      const m = c ? (flat[c] ??= new THREE.MeshStandardNodeMaterial({ color: c, roughness: 0.8, side: THREE.DoubleSide })) : null;
      it.root.traverse((o: any) => { if (o.isMesh) o.material = m ?? o.userData.mat0; }); painted.set(it, c);
    }
  }
  /** Names of records whose LiDAR shell must not be drawn. */
  const replaced = new Set(items.flatMap(i => [...i.def.replaces, ...(i.def.members ?? []).map(m => m.name)]));
  const replacedIds = new Set(clearIds);
  /** The landmark model under the ray (only its parts standing in the current year) → its record id and distance. */
  const ray0: THREE.Object3D[] = [];
  function pick(ray: THREE.Raycaster): { id: number; dist: number } | null {
    ray0.length = 0;
    const visible = (o: THREE.Object3D) => { for (let p: THREE.Object3D | null = o; p; p = p.parent) if (!p.visible) return false; return true; };
    group.traverse(o => { if ((o as THREE.Mesh).isMesh && visible(o)) ray0.push(o); });
    const h = ray.intersectObjects(ray0, false)[0]; if (!h) return null;
    const it = items.find(i => { for (let p: THREE.Object3D | null = h.object; p; p = p.parent) if (p === i.root) return true; return false; });
    if (!it) return null;
    let rec = it.rec;
    for (let p: THREE.Object3D | null = h.object; p && p !== it.root; p = p.parent) {
      const m = it.members.find(m => p!.name.startsWith(m.key + '@') || p!.name.startsWith(m.key + '_'));
      if (m) { rec = m.rec ?? rec; break; }
    }
    return rec ? { id: rec.id, dist: h.distance } : null;
  }
  /** every year a landmark part appears or goes (for the timeline's fast-forward through quiet stretches) */
  const changes = parts.flatMap(p => [p.from, p.to]).filter(y => y < 9999);
  /** Parts standing now, with their world boxes (for the x-ray of close views, scene/xray.ts). */
  const boxes = new Map<THREE.Object3D, THREE.Box3>();
  function xrayParts() {
    const out: { obj: THREE.Object3D; box: THREE.Box3 }[] = [];
    for (const p of parts) {
      if (!p.obj.visible) continue;
      let b = boxes.get(p.obj); if (!b) { p.obj.updateWorldMatrix(true, true); b = new THREE.Box3().setFromObject(p.obj); boxes.set(p.obj, b); }
      if (!b.isEmpty()) out.push({ obj: p.obj, box: b });
    }
    return out;
  }
  return { group, update, paint, replaced, replacedIds, pick, changes, xrayParts };
}
