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
  ground?: number; source: string;
  clear?: [number, number][];                  // scene x/z polygon: every record whose centre lies inside is replaced too
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
];

export async function loadLandmarks(scene: THREE.Scene, tex: TexSet, recs: Rec[], base = './models/landmarks') {
  const group = new THREE.Group(); group.name = 'landmarks'; scene.add(group);
  const parts: { obj: THREE.Object3D; from: number; to: number }[] = [];
  const loader = new GLTFLoader();
  const items: { def: LandmarkDef; root: THREE.Object3D; rec?: Rec }[] = [];
  for (const def of LANDMARKS) {
    try {
      const [gltf, defs] = await Promise.all([loader.loadAsync(`${base}/${def.file}.glb`), fetch(`${base}/${def.file}_materials.json`).then(r => r.json())]);
      const mats = buildMaterials(defs, tex, THREE.DoubleSide);
      const root = gltf.scene; const inside = def.clear ? recs.filter(r => inPoly(r.c[0], r.c[1], def.clear!)) : [];
      const rec = recs.find(r => r.name === def.replaces[0]) ?? inside.find(r => r.name) ?? inside[0];
      root.position.set(def.at[0], def.ground ?? rec?.ground ?? 8.4, def.at[1]); root.rotation.y = def.rot;
      root.traverse((o: any) => {
        if (o.isMesh) { o.material = mats[o.material.name] ?? o.material; o.castShadow = o.receiveShadow = true; o.userData.mat0 = o.material; }
        // "part@1504_160-1873" – years, optionally with a day of the year (glTF loaders strip dots from node names)
        const m = /@(-?\d+)(?:_(\d+))?-(-?\d+)(?:_(\d+))?/.exec(o.name);
        if (m) parts.push({ obj: o, from: +m[1] + (m[2] ? (+m[2] - 1) / 366 : 0), to: +m[3] + (m[4] ? (+m[4] - 1) / 366 : 0) });
      });
      for (const r of [...recs.filter(r => def.replaces.includes(r.name)), ...inside]) if (!r.src.includes(def.source)) r.src = [def.source, ...r.src];
      group.add(root); items.push({ def, root, rec });
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
  const replaced = new Set(items.flatMap(i => i.def.replaces));
  const replacedIds = new Set(items.flatMap(i => i.def.clear ? recs.filter(r => inPoly(r.c[0], r.c[1], i.def.clear!)).map(r => r.id) : []));
  return { group, update, paint, replaced, replacedIds };
}
