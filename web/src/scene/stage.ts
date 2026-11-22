// Renderer (WebGPU with automatic WebGL2 fallback), camera + controls, sun/sky by hour and era, tilt-shift post.
import * as THREE from 'three/webgpu';
import { pass, uniform, mix, smoothstep, abs, screenUV, vec2, float } from 'three/tsl';
import { gaussianBlur } from 'three/addons/tsl/display/GaussianBlurNode.js';
import { MapControls } from 'three/addons/controls/MapControls.js';

export const uTilt = uniform(1);          // 0..1 tilt-shift strength
export const uFocusY = uniform(0.5);      // screen-space focus band centre

export async function createStage(container: HTMLElement) {
  const qs = new URLSearchParams(location.search);
  const forceWebGL = qs.has('gl');
  const lite = qs.has('lite');                                            // ?lite=1: no shadows, 1x pixel ratio   // ?gl=1 forces the WebGL2 backend
  const renderer = new THREE.WebGPURenderer({ antialias: true, forceWebGL });
  renderer.setPixelRatio(lite ? 1 : Math.min(devicePixelRatio, 2));
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.shadowMap.enabled = !lite; renderer.shadowMap.type = THREE.PCFShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
  container.appendChild(renderer.domElement);
  await renderer.init();

  const scene = new THREE.Scene();
  scene.fog = new THREE.Fog(0xd9d2c2, 2500, 9000);           // near/far re-set every frame from the zoom (main.ts)
  const camera = new THREE.PerspectiveCamera(32, container.clientWidth / container.clientHeight, 2, 30000);
  camera.position.set(-520, 620, 820);
  const controls = new MapControls(camera, renderer.domElement);
  controls.target.set(0, 0, 60); controls.enableDamping = true; controls.dampingFactor = 0.08;
  controls.maxPolarAngle = 1.15; controls.minDistance = 25; controls.maxDistance = 11000; controls.screenSpacePanning = false;

  const hemi = new THREE.HemisphereLight(0xdfe8f2, 0x8a7a62, 1.15); scene.add(hemi);
  const sun = new THREE.DirectionalLight(0xfff1d8, 2.6); sun.castShadow = true;
  sun.shadow.mapSize.set(4096, 4096);
  const sc = sun.shadow.camera as THREE.OrthographicCamera; sc.left = -700; sc.right = 700; sc.top = 700; sc.bottom = -700; sc.near = 10; sc.far = 3000;
  sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.6;
  scene.add(sun, sun.target);

  // post: tilt-shift = blend sharp/blurred by distance from a horizontal focus band (miniature look, style A)
  const pipeline = new THREE.RenderPipeline(renderer);
  const scenePass = pass(scene, camera);
  const col = scenePass.getTextureNode('output');
  const blurred = gaussianBlur(col, vec2(1.6), 4);
  const band = smoothstep(float(0.12), float(0.42), abs(screenUV.y.sub(uFocusY))).mul(uTilt);
  pipeline.outputNode = mix(col, blurred, band);

  function setSun(hour: number, year: number) {
    // simple solar path for Florence (~43.8°N, midsummer-ish arc); azimuth from east to west
    const t = (hour - 6) / 12; const az = Math.PI * (1 - t) - Math.PI / 2; const el = Math.max(0.05, Math.sin(Math.PI * Math.min(Math.max(t, 0), 1)) * 1.15);
    const d = 1500; sun.position.set(controls.target.x + Math.cos(az) * Math.cos(el) * d, Math.sin(el) * d, controls.target.z + Math.sin(az) * Math.cos(el) * d);
    sun.target.position.copy(controls.target);
    const warm = 1 - Math.min(1, el / 0.6);
    sun.color.setHSL(0.09, 0.6 + warm * 0.3, 0.86 - warm * 0.18); sun.intensity = 0.6 + 2.2 * Math.min(1, el / 0.5);
    hemi.intensity = 0.5 + 0.8 * Math.min(1, el / 0.5);
    const sky = new THREE.Color().setHSL(0.58 - warm * 0.5, 0.35, 0.62 + 0.18 * Math.min(1, el)).lerp(new THREE.Color(0xe8dcc4), year < 1900 ? 0.35 : 0.15);
    scene.background = sky; (scene.fog as THREE.Fog).color.copy(sky);
  }
  function resize() { camera.aspect = container.clientWidth / container.clientHeight; camera.updateProjectionMatrix(); renderer.setSize(container.clientWidth, container.clientHeight); }
  addEventListener('resize', resize);
  return { renderer, scene, camera, controls, sun, pipeline, setSun, backend: (renderer as any).backend?.isWebGPUBackend ? 'WebGPU' : 'WebGL2 (fallback)' };
}
