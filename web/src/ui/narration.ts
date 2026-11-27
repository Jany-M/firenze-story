// The line at the top of the view that tells what an event shows: play-by-play for the scenes that have steps, the main
// facts for the others (kept up while the event is on, not a toast that fades after a few seconds). The flood has its own
// clock line in the same place (sim/flood.ts).
export function createNarration() {
  const el = document.createElement('div'); el.id = 'narration';
  el.innerHTML = '<b></b><span></span>';
  document.body.appendChild(el);
  const [b, sp] = [el.querySelector('b')!, el.querySelector('span')!];
  let cur = '';
  return {
    set(n: { title: string; text: string } | null) {
      const k = n ? n.title + '|' + n.text : '';
      if (k === cur) return; cur = k;
      if (!n) { el.classList.remove('on'); return; }
      b.textContent = n.title; sp.textContent = n.text;
      el.classList.remove('on'); void el.offsetWidth; el.classList.add('on');       // fade the new line in
    },
  };
}
