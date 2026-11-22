// Timeline: non-linear year scale, construction histogram (Paris-style), epoch ticks, event pins, draggable knob.
import { state, set, fmtYear } from '../state';
import { EVENTS, PERIODS } from '../data/history';
import type { Rec } from '../scene/city';

// piecewise-linear scale: more room for recent, denser centuries
const SEG: [number, number][] = [[-800, 0], [-60, 0.06], [1000, 0.2], [1300, 0.36], [1500, 0.53], [1800, 0.74], [1900, 0.85], [2026, 1]];
export const yearToX = (y: number) => { for (let i = 1; i < SEG.length; i++) if (y <= SEG[i][0]) { const [y0, x0] = SEG[i - 1], [y1, x1] = SEG[i]; return x0 + ((y - y0) / (y1 - y0)) * (x1 - x0); } return 1; };
export const xToYear = (x: number) => { for (let i = 1; i < SEG.length; i++) if (x <= SEG[i][1]) { const [y0, x0] = SEG[i - 1], [y1, x1] = SEG[i]; return y0 + ((x - x0) / (x1 - x0)) * (y1 - y0); } return 2026; };

export function createTimeline(el: HTMLElement, recs: Rec[], onEvent: (i: number) => void) {
  el.innerHTML = `
    <div class="tl-top">
      <button class="play" title="Play / pause (space)">▶</button>
      <div class="yr"></div><div class="tl-date"></div>
      <label class="spd">speed <select>${[2, 10, 25, 60, 150].map(v => `<option value="${v}">${v} y/s</option>`).join('')}</select></label>
      <div class="tl-hint">drag the timeline · ← → step a year · shift ±25</div>
    </div>
    <div class="track"><canvas></canvas><div class="pins"></div><div class="knob"></div></div>`;
  const cv = el.querySelector('canvas')!, ctx = cv.getContext('2d')!, knob = el.querySelector('.knob') as HTMLElement;
  const playBtn = el.querySelector('.play') as HTMLButtonElement, sel = el.querySelector('select')!;
  sel.value = String(state.speed);
  sel.onchange = () => set({ speed: +sel.value });
  playBtn.onclick = () => set({ playing: !state.playing });
  // histogram of construction starts (buildings + monuments), coloured by period
  const bins = 240, counts = new Array(bins).fill(0), conj = new Array(bins).fill(0), col = new Array(bins).fill(0);
  for (const r of recs) {
    const b = Math.min(bins - 1, Math.max(0, Math.floor(yearToX(r.start) * bins)));
    if (r.conf === 'conjectural') conj[b]++; else { counts[b]++; col[b] = PERIODS.findIndex(p => r.start <= p.to); }
  }
  const pins = el.querySelector('.pins')!;
  EVENTS.forEach((e, i) => {
    const p = document.createElement('button'); p.className = 'pin'; p.style.left = `${yearToX(e.year) * 100}%`;
    p.title = `${fmtYear(e.year)} · ${e.title}`; p.onclick = ev => { ev.stopPropagation(); onEvent(i); }; pins.appendChild(p);
  });
  function draw() {
    const w = (cv.width = cv.clientWidth * devicePixelRatio), h = (cv.height = cv.clientHeight * devicePixelRatio);
    ctx.clearRect(0, 0, w, h);
    const mx = Math.max(...counts.map(c => Math.sqrt(c)), ...conj.map(c => Math.sqrt(c) * 0.5), 1);
    conj.forEach((c, i) => {   // conjectural start dates: faded, they are estimates by zone
      if (!c) return; const bh = ((Math.sqrt(c) * 0.5) / mx) * (h * 0.62);
      ctx.fillStyle = 'rgba(200,200,210,.22)'; ctx.fillRect((i / bins) * w, h * 0.7 - bh, w / bins - 1, bh);
    });
    counts.forEach((c, i) => {
      if (!c) return; const bh = (Math.sqrt(c) / mx) * (h * 0.62);
      ctx.fillStyle = PERIODS[col[i]]?.color ?? '#999'; ctx.globalAlpha = 0.85; ctx.fillRect((i / bins) * w, h * 0.7 - bh, w / bins - 1, bh);
    });
    ctx.globalAlpha = 1; ctx.fillStyle = 'rgba(255,255,255,.18)'; ctx.fillRect(0, h * 0.7, w, 2 * devicePixelRatio);
    ctx.fillStyle = 'rgba(255,255,255,.7)'; ctx.font = `${10 * devicePixelRatio}px Inter, system-ui`;
    for (const y of [-800, -59, 500, 1000, 1172, 1333, 1436, 1530, 1737, 1865, 1944, 2026]) {
      const x = yearToX(y) * w; ctx.fillRect(x, h * 0.7, 1, 6 * devicePixelRatio); ctx.fillText(fmtYear(y), Math.min(x + 3, w - 40 * devicePixelRatio), h * 0.97);
    }
  }
  const track = el.querySelector('.track') as HTMLElement;
  let drag = false;
  const toYear = (ev: PointerEvent) => { const r = track.getBoundingClientRect(); return Math.round(xToYear(Math.min(1, Math.max(0, (ev.clientX - r.left) / r.width)))); };
  track.onpointerdown = ev => { drag = true; track.setPointerCapture(ev.pointerId); set({ year: toYear(ev), playing: false }); };
  track.onpointermove = ev => { if (drag) set({ year: toYear(ev) }); };
  track.onpointerup = () => (drag = false);
  addEventListener('resize', draw); draw();
  return {
    update() {
      knob.style.left = `${yearToX(state.year) * 100}%`;
      (el.querySelector('.yr') as HTMLElement).textContent = fmtYear(state.year);
      (el.querySelector('.tl-date') as HTMLElement).textContent = state.mode === 'live' ? `${state.date.split('-').reverse().join('/')} · ${String(Math.floor(state.hour)).padStart(2, '0')}:${String(Math.round((state.hour % 1) * 60)).padStart(2, '0')}` : '';
      playBtn.textContent = state.playing ? '❚❚' : '▶';
    },
  };
}
