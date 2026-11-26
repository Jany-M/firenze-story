// Device check before anything heavy loads: picks a detail tier from the GPU, memory, cores and screen, so phones and
// tablets get a city they can hold in memory and draw, and only capable machines get the full detail and shadows.
// ?q=low|mid|high forces a tier (?lite is the old name for low).

export type Tier = 'low' | 'mid' | 'high';
export interface Quality {
  tier: Tier; reason: string;
  dpr: number;               // device-pixel-ratio cap
  antialias: boolean;
  shadows: boolean; shadowSize: number;
  tilt: boolean;             // tilt-shift post pass
  cityRadius: number;        // city tiles farther than this from the view's centre are not loaded (0 = all, streamed nearest first)
  people: number; riverPeople: number;
  treeShare: number;         // share of the trees drawn
  anisotropy: number;
  landmarks: boolean;        // hand-built landmark models
}

const TIERS: Record<Tier, Omit<Quality, 'tier' | 'reason'>> = {
  high: { dpr: 2, antialias: true, shadows: true, shadowSize: 4096, tilt: true, cityRadius: 0, people: 280, riverPeople: 40, treeShare: 1, anisotropy: 8, landmarks: true },
  mid: { dpr: 1.5, antialias: true, shadows: true, shadowSize: 2048, tilt: true, cityRadius: 1800, people: 160, riverPeople: 25, treeShare: 0.6, anisotropy: 4, landmarks: true },
  low: { dpr: 1, antialias: true, shadows: false, shadowSize: 1024, tilt: false, cityRadius: 800, people: 70, riverPeople: 12, treeShare: 0.3, anisotropy: 2, landmarks: true },
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
  const tier: Tier = forced && forced in TIERS ? forced : score >= 2.5 ? 'high' : score >= 1 ? 'mid' : 'low';
  const q: Quality = { tier, reason: forced ? 'set by ?q' : (why.join(', ') || (gpu.split(' ').slice(0, 3).join(' ') || 'desktop')), ...TIERS[tier] };
  q.dpr = Math.min(devicePixelRatio || 1, q.dpr);
  return q;
}
