// Run-time governor (2026-11-28): the tier (quality.ts) is a guess made before anything loads; this watches what the device
// actually manages. Every 4 s it looks at the mean frame time and, where the browser tells (Chrome), the share of the JS
// heap in use. Falling behind (frames over 45 ms, ≈ 22 fps, or the heap over 80 % of its limit) thins the crowds by a
// quarter and, lower down, the pixel ratio; doing well again (under 24 ms and 60 %) gives back a little every 12 s, never
// above the tier's own settings. Nothing is reloaded: the city, the landmarks and the ground stay as they are.
import type { Quality } from './quality';

interface Crowd { setBudget(base: number, cap: number): void }
export function createGovernor(q: Quality, renderer: { setPixelRatio(r: number): void },
  crowds: { crowd: Crowd; base: number; cap: number }[]) {
  let level = 1, acc = 0, frames = 0, sinceUp = 0, held = false;
  const apply = () => {
    const l = held ? 0 : level;                       // held: the city's tiles first, the crowds after
    for (const c of crowds) c.crowd.setBudget(c.base * l, Math.max(c.base * l, c.cap * Math.max(l, 0.5)));
    renderer.setPixelRatio(Math.max(1, q.dpr * (level < 0.6 ? Math.max(0.6, level + 0.2) : 1)));
  };
  return {
    get level() { return level; },
    /** Hold the walkers back while the city is still streaming in (small devices: the buildings come first). */
    hold(v: boolean) { if (v !== held) { held = v; apply(); } },
    tick(dt: number) {
      acc += dt; frames++; sinceUp += dt;
      if (acc < 4) return;
      const ms = (acc / frames) * 1000; acc = 0; frames = 0;
      const pm = (performance as any).memory, heap = pm ? pm.usedJSHeapSize / pm.jsHeapSizeLimit : 0;
      if ((ms > 45 || heap > 0.8) && level > 0.3) { level = Math.max(0.3, level * 0.75); sinceUp = 0; apply(); }
      else if (ms < 24 && heap < 0.6 && level < 1 && sinceUp > 12) { level = Math.min(1, level * 1.15); sinceUp = 0; apply(); }
    },
  };
}
