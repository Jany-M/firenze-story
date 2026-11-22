// Street highlight on the map: a glowing ribbon draped on the terrain along the street's centre lines.
import * as THREE from 'three/webgpu';
import { uniform, sin, float, color, mix } from 'three/tsl';
import type { Street } from '../data/sources';

export function createStreetHighlight(scene: THREE.Scene, height: (x: number, z: number) => number) {
  const uT = uniform(0);
  const mat = new THREE.MeshBasicNodeMaterial({ transparent: true, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -4 });
  mat.colorNode = mix(color(0xffc86b), color(0xffffff), sin(uT.mul(3)).mul(0.5).add(0.5).mul(0.35));
  mat.opacityNode = float(0.85);
  // second pass drawn through buildings, faint, so narrow streets stay visible from above
  const xray = new THREE.MeshBasicNodeMaterial({ transparent: true, depthWrite: false, depthTest: false });
  xray.colorNode = color(0xffc86b);
  xray.opacityNode = sin(uT.mul(3)).mul(0.12).add(0.38);
  let mesh: THREE.Mesh | null = null, ghost: THREE.Mesh | null = null;
  function show(st: Street | null) {
    if (mesh) { scene.remove(mesh, ghost!); mesh.geometry.dispose(); mesh = ghost = null; }
    if (!st?.g) return;
    const pos: number[] = [], idx: number[] = []; const W = 2.6;
    for (const line of st.g) {
      // densify to ~2 m so the ribbon follows the ground
      const pts: [number, number][] = [];
      for (let i = 0; i < line.length - 1; i++) {
        const [ax, az] = line[i], [bx, bz] = line[i + 1], n = Math.max(1, Math.ceil(Math.hypot(bx - ax, bz - az) / 2));
        for (let k = 0; k < n; k++) pts.push([ax + (bx - ax) * k / n, az + (bz - az) * k / n]);
      }
      pts.push(line[line.length - 1]);
      const base = pos.length / 3;
      pts.forEach(([x, z], i) => {
        const [px, pz] = pts[Math.max(0, i - 1)], [nx, nz] = pts[Math.min(pts.length - 1, i + 1)];
        let tx = nx - px, tz = nz - pz; const l = Math.hypot(tx, tz) || 1; tx /= l; tz /= l;
        for (const s of [-1, 1]) { const qx = x - tz * W * s, qz = z + tx * W * s; pos.push(qx, height(qx, qz) + 0.35, qz); }
        if (i > 0) { const a = base + (i - 1) * 2; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); }
      });
    }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx);
    mesh = new THREE.Mesh(g, mat); mesh.renderOrder = 5;
    ghost = new THREE.Mesh(g, xray); ghost.renderOrder = 6; scene.add(mesh, ghost);
  }
  return { show, update: (dt: number) => { uT.value += dt; } };
}
