// Images from docs/materials (maps, drawings, paintings, photographs – each credited, free licences only) as a strip of
// thumbnails in a card, opening a lightbox: image, caption, author, licence and source, ← → to browse, Esc to close.
// materials.json is built by pipeline/50_materials.py; prepare.py copies docs/materials to web/public/materials.

export interface Material {
  topic: string; subjects: string[]; caption: string; src_file: string; img: string; thumb: string; w: number; h: number;
  author: string; date: string; license: string; license_url: string; page: string;
}
const BASE = './materials/';
let all: Material[] = [];
fetch(BASE + 'materials.json').then(r => r.ok ? r.json() : []).then((m: Material[]) => { all = m; }).catch(() => {});
const esc = (s: string) => s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]!));

/** Materials for any of the subjects ("rec:<name>", "event:<title>", "map"), in manifest order. */
export const materialsFor = (subjects: string[]) => all.filter(m => m.subjects.some(s => subjects.includes(s)));

/** HTML of the thumbnail strip ('' when there is nothing); call wireGallery(container) after inserting it. */
export function galleryHtml(subjects: string[]) {
  const ms = materialsFor(subjects); if (!ms.length) return '';
  return `<div class="gallery" data-subjects="${esc(JSON.stringify(subjects))}">${ms.map((m, i) =>
    `<button class="gthumb" data-i="${i}" title="${esc(m.caption)}"><img loading="lazy" src="${BASE + m.thumb}" alt="${esc(m.caption)}"></button>`).join('')}</div>`;
}
export function wireGallery(root: ParentNode) {
  root.querySelectorAll<HTMLElement>('.gallery').forEach(g => {
    const ms = materialsFor(JSON.parse(g.dataset.subjects!));
    g.querySelectorAll<HTMLButtonElement>('.gthumb').forEach(b => b.onclick = () => open(ms, +b.dataset.i!));
  });
}

// ---- lightbox
let box: HTMLDivElement | null = null, list: Material[] = [], at = 0;
function show() {
  const m = list[at]; if (!box || !m) return;
  const lic = m.license_url ? `<a href="${esc(m.license_url)}" target="_blank" rel="noopener">${esc(m.license)}</a>` : esc(m.license);
  box.querySelector('.lb-img')!.innerHTML = `<img src="${BASE + m.img}" alt="${esc(m.caption)}">`;
  box.querySelector('.lb-cap')!.innerHTML = `<p>${esc(m.caption)}</p><p class="muted small">${esc(m.author)}${m.date ? ' · ' + esc(m.date) : ''} · ${lic}
    ${m.page ? ` · <a href="${esc(m.page)}" target="_blank" rel="noopener">source</a>` : ''}</p>`;
  box.querySelector('.lb-n')!.textContent = list.length > 1 ? `${at + 1} / ${list.length}` : '';
  (box.querySelector('.lb-prev') as HTMLElement).hidden = (box.querySelector('.lb-next') as HTMLElement).hidden = list.length < 2;
}
function step(d: number) { at = (at + d + list.length) % list.length; show(); }
function close() { if (box) box.hidden = true; }
export function open(ms: Material[], i = 0) {
  list = ms; at = i;
  if (!box) {
    box = document.createElement('div'); box.id = 'lightbox';
    box.innerHTML = `<button class="lb-x" title="close (Esc)">×</button><button class="lb-prev" title="previous (←)">‹</button>
      <div class="lb-img"></div><button class="lb-next" title="next (→)">›</button><div class="lb-cap glass"></div><span class="lb-n"></span>`;
    document.body.appendChild(box);
    (box.querySelector('.lb-x') as HTMLElement).onclick = close;
    (box.querySelector('.lb-prev') as HTMLElement).onclick = () => step(-1);
    (box.querySelector('.lb-next') as HTMLElement).onclick = () => step(1);
    box.onclick = e => { if (e.target === box || (e.target as HTMLElement).classList.contains('lb-img')) close(); };
    // capture phase: while the lightbox is open the arrow keys browse images instead of stepping the year
    addEventListener('keydown', e => {
      if (!box || box.hidden) return;
      if (e.key === 'Escape') close(); else if (e.key === 'ArrowLeft') step(-1); else if (e.key === 'ArrowRight') step(1); else return;
      e.preventDefault(); e.stopImmediatePropagation();
    }, true);
    let x0 = 0;   // swipe on touch screens
    box.addEventListener('touchstart', e => { x0 = e.touches[0].clientX; }, { passive: true });
    box.addEventListener('touchend', e => { const dx = e.changedTouches[0].clientX - x0; if (Math.abs(dx) > 50) step(dx < 0 ? 1 : -1); });
  }
  box.hidden = false; show();
}
