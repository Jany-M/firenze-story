// Device check before anything heavy loads: picks a detail tier from the GPU, memory, cores and screen, so phones and
// tablets get a city they can hold in memory and draw, and only capable machines get the full detail and shadows.
// ?q=min|low|mid|high forces a tier (?lite is the old name for low).
//
// Memory budget (2026-11-28, measured on a desktop at `high`: the tab holds ≈1 GB – city tiles ≈ 350 MB, landmark models
// ≈ 250 MB, the 2 m ground with its two heights ≈ 150 MB, people and props ≈ 150 MB, textures the rest). What each tier keeps:
//   high  everything: the whole city, all trees, 280 walkers, 2 m ground, 4096 shadows           (8 GB+ desktops)
//   mid   city within 1.8 km of the view, 60 % of the trees, 160 walkers, 2 m ground              (≈ 600–700 MB)
//   low   city within 800 m, 30 % of the trees, 70 walkers, 4 m ground, no shadows, DPR 1       (≈ 350–450 MB; 4 GB tablets)
//   min   city within 550 m, 15 % of the trees, 30 walkers, 4 m ground, no antialias, no tilt  (≈ 250 MB; 2–3 GB phones)
// After start-up a governor (perf.ts) watches the frame time and the JS heap and thins the crowds and the pixel ratio if
// the device falls behind, giving them back slowly when it recovers.

export type Tier = 'min' | 'low' | 'mid' | 'high';
export interface Quality {
  tier: Tier; reason: string;
  dpr: number;               // device-pixel-ratio cap
  antialias: boolean;
  shadows: boolean; shadowSize: number;
  tilt: boolean;             // tilt-shift post pass
  cityRadius: number;        // city tiles farther than this from the view's centre are not loaded (0 = all, streamed nearest first)
  people: number; riverPeople: number; squarePeople: number;   // people: walkers at street level; the other two: safety caps (made on demand)
  treeShare: number;         // share of the trees drawn
  anisotropy: number;
  landmarks: boolean;        // hand-built landmark models
  terrainUp: number;         // ground resampling: 2 = a 2 m grid (≈4× the vertices of the 4 m LiDAR grid), 1 = as measured
}

const TIERS: Record<Tier, Omit<Quality, 'tier' | 'reason'>> = {
  high: { dpr: 2, antialias: true, shadows: true, shadowSize: 4096, tilt: true, cityRadius: 0, people: 280, riverPeople: 120, squarePeople: 260, treeShare: 1, anisotropy: 8, landmarks: true, terrainUp: 2 },
  mid: { dpr: 1.5, antialias: true, shadows: true, shadowSize: 2048, tilt: true, cityRadius: 1800, people: 160, riverPeople: 80, squarePeople: 160, treeShare: 0.6, anisotropy: 4, landmarks: true, terrainUp: 2 },
  low: { dpr: 1, antialias: true, shadows: false, shadowSize: 1024, tilt: false, cityRadius: 800, people: 70, riverPeople: 40, squarePeople: 70, treeShare: 0.3, anisotropy: 2, landmarks: true, terrainUp: 1 },
  min: { dpr: 1, antialias: false, shadows: false, shadowSize: 512, tilt: false, cityRadius: 550, people: 30, riverPeople: 18, squarePeople: 30, treeShare: 0.15, anisotropy: 1, landmarks: true, terrainUp: 1 },
};

function webglRenderer(): string {
  try {
    const c = document.createElement('canvas'); const gl = (c.getContext('webgl2') || c.getContext('webgl')) as WebGLRenderingContext | null;
    if (!gl) return 'no webgl';
    const ext = gl.getExtension('WEBGL_debug_renderer_info');
    const r = ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER);
    (gl.getExtension('WEBGL_lose_context') as any)?.loseContext();
    return String(r);
  } catch { return ''; }
}

export async function detectQuality(): Promise<Quality> {
  const qs = new URLSearchParams(location.search);
  const forced = (qs.get('q') ?? (qs.has('lite') ? 'low' : '')) as Tier | '';
  const coarse = matchMedia('(pointer: coarse)').matches;
  const shortSide = Math.min(screen.width, screen.height);
  const phone = coarse && shortSide < 600, tablet = coarse && !phone;
  const mem: number | undefined = (navigator as any).deviceMemory;
  const cores = navigator.hardwareConcurrency ?? 4;
  let gpu = '', webgpu = !!(navigator as any).gpu, fallback = false, maxBuf = 0;
  if (webgpu) {
    try {
      const a: any = await (navigator as any).gpu.requestAdapter();
      if (!a) webgpu = false;
      else { gpu = [a.info?.vendor, a.info?.architecture, a.info?.description].filter(Boolean).join(' '); fallback = !!(a.isFallbackAdapter || a.info?.isFallbackAdapter); maxBuf = a.limits?.maxBufferSize ?? 0; }
    } catch { webgpu = false; }
  }
  if (!gpu) gpu = webglRenderer();
  const soft = /swiftshader|llvmpipe|software|basic render/i.test(gpu) || fallback;
  const mobileGpu = /mali|adreno|powervr|apple gpu|apple a\d|videocore/i.test(gpu);
  let score = 3; const why: string[] = [];
  if (phone) { score -= 2; why.push('phone'); } else if (tablet) { score -= 1; why.push('tablet'); }
  if (mem !== undefined) { if (mem <= 2) { score -= 2; why.push(`${mem} GB RAM`); } else if (mem <= 4) { score -= 1; why.push(`${mem} GB RAM`); } }
  else if (coarse) score -= 0.5;
  if (cores <= 4) { score -= 1; why.push(`${cores} cores`); }
  if (soft) { score -= 3; why.push('software GPU'); }
  else if (mobileGpu && !coarse) score -= 0.5;
  if (maxBuf && maxBuf < 512 * 1024 * 1024) { score -= 1; why.push('small GPU buffers'); }
  if (!webgpu) why.push('WebGL2');
  // a small memory decides on its own: 2 GB (or a phone that does not say and is not new) gets the smallest tier
  if (mem !== undefined && mem <= 2) { score = Math.min(score, -1); }
  if (phone && (mem ?? 3) <= 3) score = Math.min(score, -0.5);
  const tier: Tier = forced && forced in TIERS ? forced : score >= 2.5 ? 'high' : score >= 1 ? 'mid' : score >= 0 ? 'low' : 'min';
  const q: Quality = { tier, reason: forced ? 'set by ?q' : (why.join(', ') || (gpu.split(' ').slice(0, 3).join(' ') || 'desktop')), ...TIERS[tier] };
  q.dpr = Math.min(devicePixelRatio || 1, q.dpr);
  return q;
}
