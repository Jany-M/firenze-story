// Freeing what a scene or a rebuild made for itself (2026-11-28): geometries and materials created on the spot are disposed
// when they are taken away, so the tab's memory does not climb with every event played or every decade passed. Anything
// shared – the prop library's pieces, the people's kit – is in `keep` and left alone.
import * as THREE from 'three/webgpu';

export function libraryOf(...roots: (THREE.Object3D | undefined | null)[]) {
  const keep = new Set<object>();
  for (const r of roots) r?.traverse((o: any) => { if (o.geometry) keep.add(o.geometry); const m = o.material; if (m) (Array.isArray(m) ? m : [m]).forEach(x => keep.add(x)); });
  return keep;
}
/** Dispose the geometries and materials under `obj` that are not in `keep` (call after taking it out of the scene). */
export function freeTree(obj: THREE.Object3D, keep: Set<object>) {
  obj.traverse((o: any) => {
    if (o.isSkinnedMesh) return;                      // people: never here
    if (o.geometry && !keep.has(o.geometry)) o.geometry.dispose();
    const m = o.material; if (m) for (const x of Array.isArray(m) ? m : [m]) if (!keep.has(x)) x.dispose?.();
  });
}
