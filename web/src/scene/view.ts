// View management on top of MapControls (left-drag pan · right-drag rotate · wheel zoom):
//   Ctrl + move mouse          rotate the view around the focus point (no button needed)
//   Ctrl + Shift + move mouse  move the point of view (pan over the ground)
//   W A S D                    move · Q / E rotate · R / F tilt · + / - zoom · N north-up · H help
import * as THREE from 'three/webgpu';
import type { MapControls } from 'three/addons/controls/MapControls.js';

export const VIEW_HELP = [
  ['Left drag', 'move'], ['Right drag', 'rotate'], ['Wheel', 'zoom'],
  ['Ctrl + mouse', 'rotate (no click)'], ['Ctrl + Shift + mouse', 'move (no click)'],
  ['W A S D', 'move'], ['Q / E', 'rotate'], ['R / F', 'tilt'], ['+ / −', 'zoom'], ['N', 'face north'], ['H', 'this help'],
];

export function createViewControls(camera: THREE.PerspectiveCamera, controls: MapControls, dom: HTMLElement) {
  const help = document.createElement('div'); help.className = 'view-help'; help.hidden = true;
  help.innerHTML = '<b>View</b>' + VIEW_HELP.map(([k, v]) => `<div><kbd>${k}</kbd><span>${v}</span></div>`).join('');
  help.onclick = () => (help.hidden = true); document.body.appendChild(help);
  const onHelp = () => (help.hidden = !help.hidden);
  const sph = new THREE.Spherical(), off = new THREE.Vector3(), right = new THREE.Vector3(), fwd = new THREE.Vector3();
  const keys = new Set<string>();

  function orbit(dTheta: number, dPhi: number) {
    off.copy(camera.position).sub(controls.target); sph.setFromVector3(off);
    sph.theta += dTheta;
    sph.phi = THREE.MathUtils.clamp(sph.phi + dPhi, controls.minPolarAngle + 0.02, controls.maxPolarAngle);
    off.setFromSpherical(sph); camera.position.copy(controls.target).add(off); camera.lookAt(controls.target);
  }
  function pan(dx: number, dz: number) {                       // dx, dz in screen units (right, forward), scaled by distance
    const dist = camera.position.distanceTo(controls.target);
    camera.getWorldDirection(fwd); fwd.y = 0; fwd.normalize(); right.crossVectors(fwd, camera.up).normalize();
    const v = right.multiplyScalar(dx * dist).add(fwd.multiplyScalar(dz * dist));
    camera.position.add(v); controls.target.add(v);
  }
  function zoom(f: number) {
    off.copy(camera.position).sub(controls.target);
    const len = THREE.MathUtils.clamp(off.length() * f, controls.minDistance, controls.maxDistance);
    camera.position.copy(controls.target).add(off.setLength(len));
  }

  // Ctrl (+Shift) + plain mouse movement
  dom.addEventListener('pointermove', e => {
    if (!e.ctrlKey || e.buttons) return;
    if (e.shiftKey) pan(-e.movementX * 0.0016, e.movementY * 0.0016);
    else orbit(-e.movementX * 0.005, -e.movementY * 0.004);
  });
  addEventListener('keydown', e => {
    const tag = (e.target as HTMLElement).tagName; if (tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA') return;
    const k = e.key.toLowerCase();
    if (k === 'shift') { keys.add(k); return; }
    if (k === 'h' || k === '?') { onHelp(); return; }
    if (k === 'n') { off.copy(camera.position).sub(controls.target); sph.setFromVector3(off); orbit(-sph.theta, 0); return; }   // camera south of target → north up
    if (k.length === 1 && 'wasdqerf+-='.includes(k) && !e.ctrlKey && !e.metaKey) { keys.add(k); e.preventDefault(); }
  });
  addEventListener('keyup', e => keys.delete(e.key.toLowerCase()));
  addEventListener('blur', () => keys.clear());

  /** Call every frame (continuous key movement). */
  function update(dt: number) {
    if (!keys.size) return;
    const s = dt * (keys.has('shift') ? 2 : 1);
    if (keys.has('w')) pan(0, 0.6 * s); if (keys.has('s')) pan(0, -0.6 * s);
    if (keys.has('a')) pan(-0.6 * s, 0); if (keys.has('d')) pan(0.6 * s, 0);
    if (keys.has('q')) orbit(1.2 * s, 0); if (keys.has('e')) orbit(-1.2 * s, 0);
    if (keys.has('r')) orbit(0, -0.6 * s); if (keys.has('f')) orbit(0, 0.6 * s);
    if (keys.has('+') || keys.has('=')) zoom(1 - 1.2 * s); if (keys.has('-')) zoom(1 + 1.2 * s);
  }
  return { update, orbit, pan, zoom, toggleHelp: onHelp };
}
