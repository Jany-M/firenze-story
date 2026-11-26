// Placeholder statues: plain stone stand-ins (base + figure, column, basin, obelisk) shown for the years they stood.
// They mark where the real models will go (docs/STATUES.md); each is a few dozen triangles.
import * as THREE from 'three/webgpu';
import { STATUES, type Statue } from '../data/statues';

export function createStatues(scene: THREE.Scene, height: (x: number, z: number) => number) {
  const stone = new THREE.MeshStandardNodeMaterial({ color: 0xcfc8b8, roughness: 0.85 });
  const bronze = new THREE.MeshStandardNodeMaterial({ color: 0x4f5a48, roughness: 0.55, metalness: 0.4 });
  const water = new THREE.MeshStandardNodeMaterial({ color: 0x6f8f9a, roughness: 0.15 });
  const group = new THREE.Group(); group.name = 'statues'; scene.add(group);
  const add = (o: THREE.Object3D, g: THREE.BufferGeometry, m: THREE.Material, x: number, y: number, z: number) => {
    const me = new THREE.Mesh(g, m); me.position.set(x, y, z); me.castShadow = me.receiveShadow = true; o.add(me); return me;
  };
  function build(s: Statue) {
    const o = new THREE.Group(), h = s.h;
    switch (s.kind) {
      case 'equestrian': add(o, new THREE.BoxGeometry(2.4, h * 0.45, 4.2), stone, 0, h * 0.225, 0);
        add(o, new THREE.BoxGeometry(1.1, h * 0.25, 3), bronze, 0, h * 0.58, 0); add(o, new THREE.CapsuleGeometry(0.35, h * 0.15, 3, 6), bronze, 0, h * 0.83, 0); break;
      case 'figure': add(o, new THREE.BoxGeometry(1.2, h * 0.45, 1.2), stone, 0, h * 0.225, 0); add(o, new THREE.CapsuleGeometry(0.35, h * 0.3, 3, 6), bronze, 0, h * 0.72, 0); break;
      case 'monument': add(o, new THREE.BoxGeometry(2.2, h * 0.5, 2.2), stone, 0, h * 0.25, 0); add(o, new THREE.CapsuleGeometry(0.5, h * 0.3, 3, 6), stone, 0, h * 0.75, 0); break;
      case 'column': add(o, new THREE.BoxGeometry(1.6, 1.2, 1.6), stone, 0, 0.6, 0); add(o, new THREE.CylinderGeometry(0.32, 0.38, h - 2.2, 10), stone, 0, 1.2 + (h - 2.2) / 2, 0);
        add(o, new THREE.CapsuleGeometry(0.3, 0.6, 3, 6), bronze, 0, h - 0.5, 0); break;
      case 'cross': add(o, new THREE.CylinderGeometry(0.25, 0.3, h - 1, 8), stone, 0, (h - 1) / 2, 0); add(o, new THREE.BoxGeometry(1.4, 1, 0.4), stone, 0, h - 0.5, 0); break;
      case 'obelisk': add(o, new THREE.BoxGeometry(2.4, 1.6, 2.4), stone, 0, 0.8, 0); add(o, new THREE.CylinderGeometry(0.35, 0.8, h - 1.6, 4), stone, 0, 1.6 + (h - 1.6) / 2, 0).rotation.y = Math.PI / 4; break;
      case 'fountain': { const r = Math.max(2, h * 0.6);
        add(o, new THREE.CylinderGeometry(r, r, 0.8, 16), stone, 0, 0.4, 0); add(o, new THREE.CylinderGeometry(r * 0.92, r * 0.92, 0.1, 16), water, 0, 0.75, 0);
        add(o, new THREE.CapsuleGeometry(0.45, Math.max(0.5, h - 2), 3, 6), h > 5 ? stone : bronze, 0, 0.8 + Math.max(0.5, h - 2) / 2 + 0.45, 0); break; }
    }
    o.position.set(s.at[0], height(s.at[0], s.at[1]), s.at[1]);
    o.userData.statue = s; group.add(o); return o;
  }
  const items = STATUES.map(s => ({ s, o: build(s) }));
  return {
    group,
    update(year: number) { for (const { s, o } of items) o.visible = year >= s.from && year < (s.to ?? 99999); },
  };
}
