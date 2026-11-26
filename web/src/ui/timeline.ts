// Timeline: non-linear year scale, construction histogram (Paris-style), epoch ticks, event pins, draggable knob.
import { state, set, fmtYear, fmtDay } from '../state';
import { EVENTS, PERIODS } from '../data/history';
import type { Rec } from '../scene/city';

// piecewise-linear scale: more room for recent, denser centuries
const SEG: [number, number][] = [[-800, 0], [-60, 0.06], [1000, 0.2], [1300, 0.36], [1500, 0.53], [1800, 0.74], [1900, 0.85], [2026, 1]];
export const yearToX = (y: number) => { for (let i = 1; i < SEG.length; i++) if (y <= SEG[i][0]) { const [y0, x0] = SEG[i - 1], [y1, x1] = SEG[i]; return x0 + ((y - y0) / (y1 - y0)) * (x1 - x0); } return 1; };
export const xToYear = (x: number) => { for (let i = 1; i < SEG.length; i++) if (x <= SEG[i][1]) { const [y0, x0] = SEG[i - 1], [y1, x1] = SEG[i]; return y0 + ((x - x0) / (x1 - x0)) * (y1 - y0); } return 2026; };

export function createTimeline(el: HTMLElement, recs: Rec[], onEvent: (i: number) => void) {
  el.innerHTML = `
    <div class="tl-ctl">
      <button class="play" title="Play / pause (space) · ← → step a year, shift ±25">▶</button>
      <div class="yr"></div>
      <select class="spd" title="playback speed">${[2, 10, 25, 60, 150].map(v => `<option value="${v}">${v} y/s</option>`).join('')}</select>
    </div>
    <div class="track" title="drag to change the year"><canvas></canvas><div class="pins"></div><div class="knob"></div></div>`;
  // phones: the year sits apart, centred under the header (the timeline row keeps the play button and the track)
  const yrTop = document.createElement('div'); yrTop.className = 'yr-top pill'; document.body.appendChild(yrTop);
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
    p.title = `${fmtYear(e.year)}${e.date ? ' · ' + fmtDay(e.date) : ''} · ${e.title}`;
    p.onpointerdown = ev => ev.stopPropagation();                 // not a drag of the timeline: the event moves it
    p.onclick = ev => { ev.stopPropagation(); onEvent(i); }; pins.appendChild(p);
  });
  // on narrow timelines dots that would overlap merge into one numbered dot; tapping it lists its events
  const pinEls = [...pins.querySelectorAll<HTMLButtonElement>('.pin')];
  const list = document.createElement('div'); list.className = 'pin-list glass'; list.hidden = true; el.appendChild(list);
  addEventListener('pointerdown', e => { if (!list.hidden && !list.contains(e.target as Node)) list.hidden = true; });
  function cluster() {
    pins.querySelectorAll('.pin.group').forEach(g => g.remove()); pinEls.forEach(p => (p.hidden = false)); list.hidden = true;
    const W = pins.clientWidth, minGap = matchMedia('(pointer: coarse)').matches ? 22 : 15;
    const order = EVENTS.map((e, i) => ({ i, x: yearToX(e.year) * W })).sort((a, b) => a.x - b.x);
    const groups: { i: number; x: number }[][] = [];
    for (const o of order) { const g = groups[groups.length - 1]; if (g && o.x - g[g.length - 1].x < minGap) g.push(o); else groups.push([o]); }
    for (const g of groups) {
      if (g.length < 2) continue;
      g.forEach(o => (pinEls[o.i].hidden = true));
      const b = document.createElement('button'); b.className = 'pin group'; b.textContent = String(g.length);
      b.style.left = `${(g.reduce((s, o) => s + o.x, 0) / g.length / W) * 100}%`;
      b.title = g.map(o => `${fmtYear(EVENTS[o.i].year)} · ${EVENTS[o.i].title}`).join('\n');
      b.onpointerdown = ev => ev.stopPropagation();
      b.onclick = ev => {
        ev.stopPropagation();
        list.innerHTML = g.map(o => `<button data-i="${o.i}"><b>${fmtYear(EVENTS[o.i].year)}</b> ${EVENTS[o.i].title}</button>`).join('');
        list.hidden = false;
        const r = b.getBoundingClientRect(), er = el.getBoundingClientRect();
        list.style.left = `${Math.max(0, Math.min(er.width - list.offsetWidth, r.left - er.left - list.offsetWidth / 2))}px`;
      };
      pins.appendChild(b);
    }
  }
  list.onclick = ev => { const b = (ev.target as HTMLElement).closest('button'); if (b) { list.hidden = true; onEvent(+b.dataset.i!); } };
  new ResizeObserver(cluster).observe(pins);
  function draw() {
    const w = (cv.width = cv.clientWidth * devicePixelRatio), h = (cv.height = cv.clientHeight * devicePixelRatio);
    ctx.clearRect(0, 0, w, h);
    const mx = Math.max(...counts.map(c => Math.sqrt(c)), ...conj.map(c => Math.sqrt(c) * 0.5), 1);
    conj.forEach((c, i) => {   // conjectural start dates: faded, they are estimates by zone
      if (!c) return; const bh = ((Math.sqrt(c) * 0.5) / mx) * (h * 0.62);
      ctx.fillStyle = 'rgba(120,100,100,.22)'; ctx.fillRect((i / bins) * w, h * 0.7 - bh, w / bins - 1, bh);
    });
    counts.forEach((c, i) => {
      if (!c) return; const bh = (Math.sqrt(c) / mx) * (h * 0.62);
      ctx.fillStyle = PERIODS[col[i]]?.color ?? '#999'; ctx.globalAlpha = 0.85; ctx.fillRect((i / bins) * w, h * 0.7 - bh, w / bins - 1, bh);
    });
    ctx.globalAlpha = 1; ctx.fillStyle = 'rgba(158,11,35,.35)'; ctx.fillRect(0, h * 0.7, w, 2 * devicePixelRatio);
    ctx.fillStyle = 'rgba(42,32,32,.75)'; ctx.font = `${10 * devicePixelRatio}px Inter, system-ui`;
    let lastEnd = -1e9;
    for (const y of [-800, -59, 500, 1000, 1172, 1333, 1436, 1530, 1737, 1865, 1944, 2026]) {
      const x = yearToX(y) * w, t = fmtYear(y), tx = Math.min(x + 3, w - ctx.measureText(t).width - 2);
      ctx.fillRect(x, h * 0.7, 1, 6 * devicePixelRatio);
      if (tx > lastEnd + 6 * devicePixelRatio) { ctx.fillText(t, tx, h * 0.97); lastEnd = tx + ctx.measureText(t).width; }   // skip labels that would overlap (narrow screens)
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
      (el.querySelector('.yr') as HTMLElement).textContent = yrTop.textContent = fmtYear(state.year);
      playBtn.textContent = state.playing ? '❚❚' : '▶';
    },
  };
}
