// Gaussian splats (three.js r186+ native GaussianSplat, WebGPURenderer only).
// Registry: public/data/splats.json  [{ url, title, credit, position:[x,y,z], rotationY, scale, start, end }]
// Dev: drag & drop a .ply / .spz / .splat / .ksplat onto the page to place it at the current focus point.
import * as THREE from 'three/webgpu';
import { GaussianSplat } from 'three/addons/objects/GaussianSplat.js';
import { GaussianSplatPLYLoader } from 'three/addons/loaders/GaussianSplatPLYLoader.js';
import { SPZLoader } from 'three/addons/loaders/SPZLoader.js';
import { SPLATLoader } from 'three/addons/loaders/SPLATLoader.js';
import { KSPLATLoader } from 'three/addons/loaders/KSPLATLoader.js';

interface Entry { url: string; title?: string; credit?: string; position?: number[]; rotationY?: number; scale?: number; start?: number; end?: number }
const loaderFor = (name: string): any => {
  const ext = name.split('.').pop()!.toLowerCase();
  return ext === 'ply' ? new GaussianSplatPLYLoader() : ext === 'spz' ? new SPZLoader() : ext === 'ksplat' ? new KSPLATLoader() : ext === 'splat' ? new SPLATLoader() : null;
};

export function createSplats(scene: THREE.Scene, getFocus: () => THREE.Vector3, notify: (msg: string) => void) {
  const items: { obj: THREE.Object3D; e: Entry }[] = [];
  async function add(e: Entry, src?: string) {
    const loader = loaderFor(e.url); if (!loader) { notify('Unsupported splat format'); return; }
    const geo = await loader.loadAsync(src ?? e.url);
    const obj = new GaussianSplat(geo);
    const p = e.position ?? getFocus().toArray();
    obj.position.set(p[0], p[1], p[2]); obj.rotation.y = e.rotationY ?? 0; obj.scale.setScalar(e.scale ?? 1);
    scene.add(obj); items.push({ obj, e }); notify(`Splat loaded: ${e.title ?? e.url}`);
  }
  fetch('./data/splats.json').then(r => (r.ok ? r.json() : [])).then((list: Entry[]) => list.forEach(e => add(e).catch(err => console.warn(err)))).catch(() => {});
  addEventListener('dragover', ev => ev.preventDefault());
  addEventListener('drop', async ev => {
    ev.preventDefault(); const f = ev.dataTransfer?.files?.[0]; if (!f) return;
    if (!loaderFor(f.name)) { notify('Drop a .ply, .spz, .splat or .ksplat Gaussian splat'); return; }
    const url = URL.createObjectURL(f);
    try { await add({ url: f.name, title: f.name }, url); } catch (e) { console.error(e); notify('Could not load splat'); }
  });
  return { update(year: number) { for (const it of items) it.obj.visible = year >= (it.e.start ?? -99999) && year < (it.e.end ?? 99999); }, items };
}
