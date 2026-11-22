// Single app state + tiny pub/sub + URL-hash persistence (shareable moments).
export type Mode = 'overview' | 'live' | 'sources';
export type ColorMode = 'real' | 'period' | 'confidence';
export interface State {
  year: number; date: string; hour: number; playing: boolean; speed: number;  // speed = years per second
  mode: Mode; color: ColorMode; overlay: string; overlayOpacity: number; tiltShift: boolean;
  selected: number; cam: number[];
}
const defaults: State = { year: 1490, date: '06-24', hour: 10.5, playing: false, speed: 25, mode: 'overview', color: 'real',
  overlay: 'none', overlayOpacity: 0.85, tiltShift: true, selected: -1, cam: [] };

type Listener = (s: State, changed: Partial<State>) => void;
const listeners: Listener[] = [];
export const state: State = { ...defaults, ...readHash() };

export function set(p: Partial<State>) {
  Object.assign(state, p);
  for (const l of listeners) l(state, p);
  scheduleHash();
}
export const on = (l: Listener) => { listeners.push(l); };

function readHash(): Partial<State> {
  const out: Partial<State> = {};
  const q = new URLSearchParams(location.hash.slice(1));
  if (q.has('y')) out.year = +q.get('y')!;
  if (q.has('d')) out.date = q.get('d')!;
  if (q.has('h')) out.hour = +q.get('h')!;
  if (q.has('m')) out.mode = q.get('m') as Mode;
  if (q.has('c')) out.color = q.get('c') as ColorMode;
  if (q.has('o')) out.overlay = q.get('o')!;
  if (q.has('cam')) out.cam = q.get('cam')!.split(',').map(Number);
  return out;
}
let t: any = 0;
function scheduleHash() {
  clearTimeout(t);
  t = setTimeout(() => {
    const q = new URLSearchParams({ y: String(Math.round(state.year)), d: state.date, h: state.hour.toFixed(1), m: state.mode, c: state.color, o: state.overlay });
    if (state.cam.length) q.set('cam', state.cam.map(v => v.toFixed(0)).join(','));
    history.replaceState(null, '', '#' + q.toString());
  }, 300);
}
export const fmtYear = (y: number) => (y < 0 ? `${Math.abs(Math.round(y))} BC` : `${Math.round(y)}`);
