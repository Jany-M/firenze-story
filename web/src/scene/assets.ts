// Shared material textures + the Blender prop library (blender/scripts/build_assets.py → public/models/*.glb).
// GLBs carry no images: every fs_* material is rebuilt here from models/materials.json (same table Blender used),
// with box (triplanar) projection of the tileable textures in public/textures. One texture set for city and props.
import * as THREE from 'three/webgpu';
import { texture, triplanarTexture, float, vec3 } from 'three/tsl';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

export const TEXTURES = ['intonaco', 'pietra_forte', 'pietra_serena', 'coppi', 'lastrico', 'cotto', 'wood', 'canvas', 'marble_white', 'marble_green', 'marble_red',
  'terra', 'basoli', 'ammattonato', 'lastrico_filari', 'lastrico_spina', 'asfalto'] as const;
export type TexName = typeof TEXTURES[number];
export type TexSet = Record<TexName, { col: THREE.Texture; rgh: THREE.Texture }>;

export async function loadTextures(base = './textures', anisotropy = 8): Promise<TexSet> {
  const L = new THREE.TextureLoader();
  const get = (n: string, srgb: boolean) => L.loadAsync(`${base}/${n}.jpg`).then(t => {
    t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = anisotropy;
    t.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace; return t;
  });
  const out: any = {};
  await Promise.all(TEXTURES.map(async n => { out[n] = { col: await get(`${n}_col`, true), rgh: await get(`${n}_rgh`, false) }; }));
  return out;
}

interface MatDef { tex: TexName | null; color: number[]; tint: number[]; rough: number; scale: number; metal: number; img?: string }

/** fs_* materials from a materials.json table (written by the Blender scripts), triplanar-mapped. */
export function buildMaterials(defs: Record<string, MatDef>, tex: TexSet, side: THREE.Side = THREE.FrontSide, imgBase = './models/landmarks/img') {
  const mats: Record<string, THREE.Material> = {};
  for (const [name, d] of Object.entries(defs)) {
    const m = new THREE.MeshStandardNodeMaterial({ roughness: d.rough, metalness: d.metal, side, color: new THREE.Color().setRGB(d.color[0], d.color[1], d.color[2], THREE.LinearSRGBColorSpace) });
    if (d.img) {                                   // a painted façade: its own image, on the mesh's UVs (glTF: no flip)
      const t = new THREE.TextureLoader().load(`${imgBase}/${d.img}`); t.colorSpace = THREE.SRGBColorSpace; t.flipY = false; t.anisotropy = 8;
      m.map = t; m.color.set(0xffffff);
    } else if (d.tex && tex[d.tex]) {
      const s = float(d.scale);
      m.colorNode = triplanarTexture(texture(tex[d.tex].col), null, null, s).rgb.mul(vec3(d.tint[0], d.tint[1], d.tint[2]));
      m.roughnessNode = triplanarTexture(texture(tex[d.tex].rgh), null, null, s).r;
    }
    mats[name] = m;
  }
  return mats;
}

export async function loadProps(tex: TexSet, base = './models') {
  const defs: Record<string, MatDef> = await fetch(`${base}/materials.json`).then(r => r.json());
  const mats = buildMaterials(defs, tex);
  const names = ['barrel', 'basket', 'crate', 'jar', 'bench', 'table', 'stall_produce', 'stall_cloth', 'stall_bread', 'tribune', 'brindellone', 'colombina',
    'barchetto', 'navicello', 'scafa', 'scalo', 'sandheap', 'duck', 'heron', 'bird', 'deer', 'hut', 'palisade',
    'hut_stilt', 'kiln', 'hearth', 'canoe', 'sheep', 'pig', 'cow', 'urn_grave', 'stele', 'bench_stone', 'bench_park', 'laundry', 'clayheap', 'bricks',
    'garment_flat', 'garment_twist', 'garment_hang', 'handcart', 'claycart'];
  const loader = new GLTFLoader(); const lib: Record<string, THREE.Object3D> = {};
  await Promise.all(names.map(async n => {
    try {
      const g = (await loader.loadAsync(`${base}/${n}.glb`)).scene;
      g.traverse((o: any) => { if (o.isMesh) { o.material = mats[o.material.name] ?? o.material; o.castShadow = o.receiveShadow = true; } });
      lib[n] = g;
    } catch (e) { console.warn('prop missing', n, e); }
  }));
  /** A placed copy (shares geometry and materials). Front of every prop faces +Z. */
  function place(name: string, x: number, y: number, z: number, rotY = 0, parent?: THREE.Object3D) {
    const src = lib[name]; if (!src) return null;
    const o = src.clone(); o.position.set(x, y, z); o.rotation.y = rotY; parent?.add(o); return o;
  }
  return { place, lib };
}
export type Props = Awaited<ReturnType<typeof loadProps>>;
