// Responsive layout: header bar (#topbar), two docks between the header and the timeline, bottom timeline.
//   desktop (≥ 1100 px wide, ≥ 760 px high): left dock = event card + info card, right dock = Events / Landmarks / Sources panel;
//     panels shrink and scroll to share the height
//   laptop / tablet (< 1100 px wide or < 760 px high): same docks, one panel open per dock – the others fold to
//     their title line
//   phone (< 700 px wide): one bottom sheet above the timeline holding every panel, one open at a time;
//     dragging the map folds them all, tapping a title opens it
// Panels fold with their ▾ / ▸ button or by tapping their title (h3). The era chip in the header opens a popover
// with the era details; the ☰ menu holds the links and the view-controls help.
const $ = <T extends HTMLElement>(s: string) => document.querySelector(s) as T;
const PHONE = matchMedia('(max-width: 699px)');
const COMPACT = matchMedia('(max-width: 1099px), (max-height: 760px)');
const PANELS = ['#evcard', '#card', '#side', '#live', '#lmk'];

let dockL: HTMLElement, dockR: HTMLElement;
const panels = () => PANELS.map(s => $(s)).filter(Boolean);
const shown = (el: HTMLElement) => !el.hidden;

function setFold(el: HTMLElement, min: boolean) {
  el.classList.toggle('min', min);
  const b = el.querySelector<HTMLButtonElement>(':scope > .coll');
  if (b) { b.textContent = min ? '▸' : '▾'; b.setAttribute('aria-expanded', String(!min)); }
}
/** Unfold a panel; on compact screens fold the other open panels sharing its dock (on phones: all of them). */
function expand(el: HTMLElement) {
  setFold(el, false);
  if (!COMPACT.matches) return;
  for (const p of panels()) if (p !== el && shown(p) && (PHONE.matches || p.parentElement === el.parentElement)) setFold(p, true);
}
function ensureButton(el: HTMLElement) {
  if (el.querySelector(':scope > .coll')) return;
  const b = document.createElement('button'); b.className = 'coll'; b.title = 'fold / unfold';
  b.textContent = el.classList.contains('min') ? '▸' : '▾';
  b.onclick = e => { e.stopPropagation(); el.classList.contains('min') ? expand(el) : setFold(el, true); };
  const x = el.querySelector(':scope > .x');               // × first (rightmost), then ▾ beside it
  if (x) x.after(b); else el.prepend(b);
}
/** Mode panels live in the right dock, except on phones where everything shares one sheet. */
function place() {
  for (const s of ['#side', '#live', '#lmk']) { const el = $(s); const want = PHONE.matches ? dockL : dockR; if (el.parentElement !== want) want.appendChild(el); }
  document.body.classList.toggle('phone', PHONE.matches); document.body.classList.toggle('compact', COMPACT.matches);
  if (COMPACT.matches) {                                   // more than one open panel per dock: keep the last one open
    const open = panels().filter(p => shown(p) && !p.classList.contains('min'));
    for (const p of open.slice(0, -1)) if (PHONE.matches || open.some(o => o !== p && o.parentElement === p.parentElement && open.indexOf(o) > open.indexOf(p))) setFold(p, true);
  }
}
/** Header and timeline heights → CSS variables the docks, toasts and popovers use. */
function measure() {
  const top = $('#topbar').getBoundingClientRect().bottom, tl = innerHeight - $('#timeline').getBoundingClientRect().top;
  document.documentElement.style.setProperty('--top-h', `${Math.ceil(top)}px`);
  document.documentElement.style.setProperty('--tl-h', `${Math.ceil(tl)}px`);
}
function popover(btn: HTMLElement, pop: HTMLElement, align: 'left' | 'right') {
  const close = () => { pop.hidden = true; btn.setAttribute('aria-expanded', 'false'); };
  btn.onclick = e => {
    e.stopPropagation();
    for (const p of document.querySelectorAll<HTMLElement>('.pop')) if (p !== pop) p.hidden = true;
    pop.hidden = !pop.hidden; btn.setAttribute('aria-expanded', String(!pop.hidden));
    if (!pop.hidden && !PHONE.matches) {
      const r = btn.getBoundingClientRect();
      if (align === 'left') { pop.style.left = `${Math.round(r.left)}px`; pop.style.right = 'auto'; }
      else { pop.style.right = `${Math.round(innerWidth - r.right)}px`; pop.style.left = 'auto'; }
    } else if (!pop.hidden) { pop.style.left = ''; pop.style.right = ''; }
  };
  addEventListener('pointerdown', e => { if (!pop.hidden && !pop.contains(e.target as Node) && !btn.contains(e.target as Node)) close(); });
  addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
}

export const layout = {
  init() {
    dockL = $('#dock-l'); dockR = $('#dock-r');
    for (const el of panels()) {
      new MutationObserver(() => ensureButton(el)).observe(el, { childList: true }); ensureButton(el);
      el.addEventListener('click', e => {                   // tap the title to fold / unfold
        const t = e.target as HTMLElement;
        if (t.closest('a, button, input, select, summary')) return;
        if (t.closest('h3') && el.contains(t)) el.classList.contains('min') ? expand(el) : setFold(el, true);
      });
    }
    PHONE.addEventListener('change', place); COMPACT.addEventListener('change', place); place();
    new ResizeObserver(measure).observe($('#topbar')); new ResizeObserver(measure).observe($('#timeline'));
    addEventListener('resize', measure); measure();
    addEventListener('keydown', e => {                       // Esc closes the open info card
      if (e.key !== 'Escape' || (e.target as HTMLElement).tagName === 'INPUT') return;
      for (const s of ['#card', '#evcard']) { const x = $(s); if (!x.hidden) { x.querySelector<HTMLButtonElement>(':scope > .x')?.click(); return; } }
    });
    popover($('#era'), $('#hud'), 'left');
    popover($('#menu-btn'), $('#menu'), 'right');
    // search: an icon on phones that opens the field over the header
    const bar = $('#topbar'), input = $<HTMLInputElement>('#search');
    $('#search-btn').onclick = () => { bar.classList.add('searching'); input.focus(); };
    input.addEventListener('blur', () => setTimeout(() => { if (!input.value) bar.classList.remove('searching'); }, 200));
    input.addEventListener('keydown', e => { if (e.key === 'Escape') { input.value = ''; input.dispatchEvent(new Event('input')); input.blur(); bar.classList.remove('searching'); } });
    // phones: dragging the map folds the sheet to its title lines, so the view is free
    let p0: [number, number] | null = null, folded = false;
    const app = $('#app');
    app.addEventListener('pointerdown', e => { p0 = [e.clientX, e.clientY]; folded = false; });
    app.addEventListener('pointermove', e => {
      if (!p0 || folded || !PHONE.matches || Math.hypot(e.clientX - p0[0], e.clientY - p0[1]) < 10) return;
      folded = true; for (const p of panels()) if (shown(p)) setFold(p, true);
    });
    addEventListener('pointerup', () => (p0 = null));
  },
  /** Show a panel that the user just asked for (opened a card, picked an event, switched mode). */
  open(el: HTMLElement) { if (!el.hidden) expand(el); },
  fold: setFold,
  get phone() { return PHONE.matches; },
};
