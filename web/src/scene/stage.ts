// Renderer (WebGPU with automatic WebGL2 fallback), camera + controls, sun/sky by hour and era, tilt-shift post.
// Detail follows the device tier (quality.ts). Against flicker: the near plane follows the zoom (depth precision where the
// eye is), and the sun's shadow box shrinks with the zoom and is snapped to its own texel grid, so shadows do not crawl
// while the camera moves.
import * as THREE from 'three/webgpu';
import { pass, uniform, mix, smoothstep, abs, screenUV, vec2, float } from 'three/tsl';
import { gaussianBlur } from 'three/addons/tsl/display/GaussianBlurNode.js';
import { MapControls } from 'three/addons/controls/MapControls.js';
import type { Quality } from '../quality';

export const uTilt = uniform(1);          // 0..1 tilt-shift strength
export const uFocusY = uniform(0.5);      // screen-space focus band centre
export const DEFAULT_HOUR = 10.5;         // the app's one lighting; only events set another hour, for as long as they last

export async function createStage(container: HTMLElement, q: Quality) {
  const qs = new URLSearchParams(location.search);
  const forceWebGL = qs.has('gl');                                         // ?gl=1 forces the WebGL2 backend
  const renderer = new THREE.WebGPURenderer({ antialias: q.antialias, forceWebGL, powerPreference: q.tier === 'high' ? 'high-performance' : 'default' } as any);
  renderer.setPixelRatio(q.dpr);
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.shadowMap.enabled = q.shadows; renderer.shadowMap.type = THREE.PCFShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
  container.appendChild(renderer.domElement);
  await renderer.init();

  const scene = new THREE.Scene();
  scene.fog = new THREE.Fog(0xd9d2c2, 2500, 9000);           // near/far re-set every frame from the zoom (main.ts)
  const camera = new THREE.PerspectiveCamera(32, container.clientWidth / container.clientHeight, 2, 30000);
  camera.position.set(-520, 620, 820);
  const controls = new MapControls(camera, renderer.domElement);
  controls.target.set(0, 0, 60); controls.enableDamping = true; controls.dampingFactor = 0.08;
  // touch screens: no inertia – the view stops the moment the fingers lift (damping only for the mouse)
  renderer.domElement.addEventListener('pointerdown', e => { controls.enableDamping = e.pointerType === 'mouse'; }, { capture: true });
  controls.maxPolarAngle = 1.15; controls.minDistance = 25; controls.maxDistance = 11000; controls.screenSpacePanning = false;

  const hemi = new THREE.HemisphereLight(0xdfe8f2, 0x8a7a62, 1.15); scene.add(hemi);
  const sun = new THREE.DirectionalLight(0xfff1d8, 2.6); sun.castShadow = q.shadows;
  sun.shadow.mapSize.set(q.shadowSize, q.shadowSize);
  const sc = sun.shadow.camera as THREE.OrthographicCamera; sc.near = 10; sc.far = 3200;
  let half = 0;
  const setHalf = (h: number) => { if (h === half) return; half = h; sc.left = -h; sc.right = h; sc.top = h; sc.bottom = -h; sc.updateProjectionMatrix();
    const texel = (2 * h) / q.shadowSize; sun.shadow.bias = -0.0002; sun.shadow.normalBias = Math.max(0.15, texel * 1.6); };
  setHalf(700);
  scene.add(sun, sun.target);

  // post: tilt-shift = blend sharp/blurred by distance from a horizontal focus band (miniature look, style A)
  const pipeline = new THREE.RenderPipeline(renderer);
  const scenePass = pass(scene, camera);
  const col = scenePass.getTextureNode('output');
  if (q.tilt) {
    const blurred = gaussianBlur(col, vec2(1.6), 4);
    const band = smoothstep(float(0.12), float(0.42), abs(screenUV.y.sub(uFocusY))).mul(uTilt);
    pipeline.outputNode = mix(col, blurred, band);
  } else pipeline.outputNode = col;

  const L = new THREE.Vector3(), R = new THREE.Vector3(), U = new THREE.Vector3(), up = new THREE.Vector3(0, 1, 0), snapped = new THREE.Vector3();
  function setSun(hour: number, year: number) {
    // simple solar path for Florence (~43.8°N, midsummer-ish arc); azimuth from east to west
    const t = (hour - 6) / 12; const az = Math.PI * (1 - t) - Math.PI / 2; const el = Math.max(0.05, Math.sin(Math.PI * Math.min(Math.max(t, 0), 1)) * 1.15);
    L.set(Math.cos(az) * Math.cos(el), Math.sin(el), Math.sin(az) * Math.cos(el)).normalize();
    // shadow box sized to the view (tighter = sharper when close), in steps so it does not resize every frame
    const d = camera.position.distanceTo(controls.target);
    setHalf(Math.min(700, Math.max(90, Math.ceil(d * 1.25 / 30) * 30)));
    // snap the light's target to the shadow-map texel grid (in light space): no shimmering while panning
    R.crossVectors(up, L).normalize(); U.crossVectors(L, R);
    const texel = (2 * half) / q.shadowSize, tg = controls.target;
    const a = Math.round(tg.dot(R) / texel) * texel, b = Math.round(tg.dot(U) / texel) * texel, c = tg.dot(L);
    snapped.copy(R).multiplyScalar(a).addScaledVector(U, b).addScaledVector(L, c);
    sun.target.position.copy(snapped); sun.position.copy(snapped).addScaledVector(L, 1500);
    const warm = 1 - Math.min(1, el / 0.6);
    sun.color.setHSL(0.09, 0.6 + warm * 0.3, 0.86 - warm * 0.18); sun.intensity = 0.6 + 2.2 * Math.min(1, el / 0.5);
    hemi.intensity = 0.5 + 0.8 * Math.min(1, el / 0.5);
    const sky = new THREE.Color().setHSL(0.58 - warm * 0.5, 0.35, 0.62 + 0.18 * Math.min(1, el)).lerp(new THREE.Color(0xe8dcc4), year < 1900 ? 0.35 : 0.15);
    scene.background = sky; (scene.fog as THREE.Fog).color.copy(sky);
  }
  /** Near/far planes follow the zoom: depth precision goes where the eye is (no z-fighting on small details). */
  function fitClip(fogFar: number) {
    const d = camera.position.distanceTo(controls.target);
    const near = Math.min(20, Math.max(0.5, d * 0.03)), far = Math.max(4000, fogFar * 1.25 + 1500);
    if (Math.abs(near - camera.near) > 0.05 * camera.near || Math.abs(far - camera.far) > 0.05 * camera.far) { camera.near = near; camera.far = far; camera.updateProjectionMatrix(); }
  }
  function resize() { camera.aspect = container.clientWidth / container.clientHeight; camera.updateProjectionMatrix(); renderer.setSize(container.clientWidth, container.clientHeight); }
  addEventListener('resize', resize);
  return { renderer, scene, camera, controls, sun, pipeline, setSun, fitClip, backend: (renderer as any).backend?.isWebGPUBackend ? 'WebGPU' : 'WebGL2 (fallback)' };
}
