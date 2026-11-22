// HUD, mode switch, Sources panel (colour modes, legend with counts, map overlays), live controls, events list,
// inspector card, search, credits, toasts. Plain DOM, no framework.
import { state, set, fmtYear, type Mode } from '../state';
import { epochAt, EVENTS, PERIODS, CONF_COLORS, MAP_OVERLAYS, CREDITS, SOURCE_LAYERS } from '../data/history';
import { ANCIENT_SITES, NECROPOLES } from '../sim/river';
import { isAlive, type Rec } from '../scene/city';
import { linkSource, sceneToLatLon, streetNameIn, fmtNo, DATASET, A07_PAGES, type Addresses, type SourceLink, type AddrRec } from '../data/sources';

const $ = <T extends HTMLElement>(s: string, r: ParentNode = document) => r.querySelector(s) as T;
const esc = (s: string) => s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]!));

export function createPanels(recs: Rec[], hooks: { flyTo: (x: number, z: number, dist?: number) => void; event: (i: number) => void; backend: string; layerCount?: (id: string) => number; addresses?: Addresses; highlightStreet?: (code: string | null) => void }) {
  const hud = $('#hud'), modes = $('#modes'), side = $('#side'), card = $('#card'), live = $('#live');
  modes.innerHTML = (['overview', 'live', 'sources'] as Mode[]).map(m => `<button data-m="${m}">${{ overview: 'Timeline', live: 'Live', sources: 'Sources' }[m]}</button>`).join('');
  modes.onclick = ev => { const m = (ev.target as HTMLElement).dataset.m as Mode; if (m) set({ mode: m, color: m === 'sources' ? (state.color === 'real' ? 'period' : state.color) : 'real' }); };

  // ---- Sources side panel ----
  side.innerHTML = `
    <h4>Colour buildings by</h4>
    <div class="seg" id="cm"><button data-c="real">Realistic</button><button data-c="period">Construction period</button><button data-c="confidence">Confidence</button></div>
    <div id="legend"></div>
    <h4>Historic map on the ground</h4>
    <select id="ov">${MAP_OVERLAYS.map(o => `<option value="${o.id}">${o.name}</option>`).join('')}</select>
    <label class="row">opacity <input id="ovo" type="range" min="0" max="1" step="0.05"></label>
    <h4>Events</h4><div id="events"></div>
    <details><summary>Credits & data</summary><ul>${CREDITS.map(c => `<li>${esc(c)}</li>`).join('')}</ul><p class="muted">Renderer: ${hooks.backend}. Drop a Gaussian splat (.ply/.spz/.splat/.ksplat) onto the page to place it at the focus point.</p></details>`;
  $('#cm', side).onclick = ev => { const c = (ev.target as HTMLElement).dataset.c; if (c) set({ color: c as any }); };
  const ov = $<HTMLSelectElement>('#ov', side), ovo = $<HTMLInputElement>('#ovo', side);
  ov.value = state.overlay; ovo.value = String(state.overlayOpacity);
  ov.onchange = () => set({ overlay: ov.value }); ovo.oninput = () => set({ overlayOpacity: +ovo.value });
  $('#events', side).innerHTML = EVENTS.map((e, i) => `<button data-i="${i}"><b>${fmtYear(e.year)}</b> ${esc(e.title)}${e.live ? ' <span class="tag">live</span>' : ''}</button>`).join('');
  $('#events', side).onclick = ev => { const b = (ev.target as HTMLElement).closest('button'); if (b) hooks.event(+b.dataset.i!); };

  // ---- Live controls ----
  live.innerHTML = `
    <label>Date <input id="dt" type="text" maxlength="5" placeholder="MM-DD"></label>
    <label>Hour <input id="hr" type="range" min="5" max="21" step="0.25"></label>
    <label class="row"><input id="ts" type="checkbox"> tilt-shift</label>
    <div class="muted" id="livenote"></div>
    <h4>Events</h4><div id="levents" class="events"></div>`;
  const dt = $<HTMLInputElement>('#dt', live), hr = $<HTMLInputElement>('#hr', live), ts = $<HTMLInputElement>('#ts', live);
  dt.onchange = () => { if (/^\d\d-\d\d$/.test(dt.value)) set({ date: dt.value }); };
  hr.oninput = () => set({ hour: +hr.value }); ts.onchange = () => set({ tiltShift: ts.checked });
  // every event with its year (and day for the yearly ones): a click moves the timeline and the camera there
  const evList = EVENTS.map((e, i) => ({ e, i })).sort((a, b) => a.e.year - b.e.year);
  $('#levents', live).innerHTML = evList.map(({ e, i }) => `<button data-i="${i}"><b>${fmtYear(e.year)}</b>${(e as any).date ? ` <span class="muted">${(e as any).date}</span>` : ''} ${esc(e.title)}${e.live ? ' <span class="tag">live</span>' : ''}</button>`).join('');
  $('#levents', live).onclick = ev => { const b = (ev.target as HTMLElement).closest('button'); if (b) hooks.event(+b.dataset.i!); };

  // ---- search: buildings, streets (every recorded name), events, pre-urban sites – any era ----
  const search = $<HTMLInputElement>('#search'), results = $('#results');
  const fold = (t: string) => t.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[’']/g, ' ')
    .replace(/\b(de|dei|degli|del|della|delle|dello|de')\b/g, 'd').replace(/\s+/g, ' ').trim();
  type Hit = { kind: 'Building' | 'Street' | 'Event' | 'Site'; label: string; key: string; from: number | null; to: number | null;
    alias?: [number, string]; go: (alias?: [number, string]) => void };
  const index: Hit[] = [];
  for (const r of recs) if (r.name && !r.name.startsWith('Roman ')) index.push({ kind: 'Building', label: r.name, key: fold(r.name), from: r.start, to: r.end ?? null,
    go: () => { set({ selected: r.id, year: isAlive(r, state.year) ? state.year : r.start + Math.max(r.ramp, 1) }); hooks.flyTo(r.c[0], r.c[1], 260); } });
  const A = hooks.addresses;
  if (A) for (const [code, st] of Object.entries(A.streets)) {
    if (!st.c) continue;
    const first = st.h.length ? st.h[0][0] : st.since;
    index.push({ kind: 'Street', label: st.n, key: fold(st.n), from: first ?? null, to: null, go: alias => {
      const y = alias ? alias[0] : (first ?? state.year);           // first year the street is known to exist
      set({ selected: -1, year: y }); hooks.flyTo(st.c![0], st.c![1], 320); showStreet(code);
    } });
  }
  EVENTS.forEach((e, i) => index.push({ kind: 'Event', label: e.title, key: fold(e.title + ' ' + (e.place ?? '')), from: e.year, to: e.year, go: () => hooks.event(i) }));
  for (const s of [...ANCIENT_SITES, ...NECROPOLES]) index.push({ kind: 'Site', label: s.name, key: fold(s.name), from: s.from, to: s.to, go: () => {
    set({ selected: -1, year: state.year >= s.from && state.year < s.to ? state.year : s.from + 100 }); hooks.flyTo(s.x, s.z, 260);
    showSite({ name: s.name, kind: 'kind' in s ? (s.kind === 'stele' ? 'Archaic stelae' : 'Cremation graves') : 'Village of huts, kilns and livestock', from: s.from, to: s.to, src: s.src });
  } });
  let hits: Hit[] = [];
  const when = (h: Hit) => {
    const y = Math.round(state.year), span = `${h.kind === 'Street' ? 'recorded from ' : ''}${h.from != null ? fmtYear(h.from) : '?'}${h.kind === 'Event' ? '' : h.to != null ? '–' + fmtYear(h.to) : ' → today'}`;
    const note = h.kind === 'Event' ? '' : h.from != null && y < h.from ? (h.kind === 'Street' ? ` · no record by ${fmtYear(y)}` : ` · not yet in ${fmtYear(y)}`) : h.to != null && y >= h.to ? ` · gone by ${fmtYear(y)}` : '';
    return `<span class="muted">${span}${note}</span>`;
  };
  search.oninput = () => {
    const q = fold(search.value); if (q.length < 2) { results.innerHTML = ''; hits = []; return; }
    const words = q.split(' ');
    const scored: [number, Hit][] = [];
    for (const h of index) {
      if (words.every(w => h.key.includes(w))) { scored.push([h.key.startsWith(q) ? 0 : 1, h]); continue; }
      if (h.kind === 'Street' && A) {                          // historic names of the street
        const st = Object.values(A.streets).find(x => x.n === h.label);
        const m = st?.h.find(a => words.every(w => fold(a[1]).includes(w)));
        if (m) scored.push([2, { ...h, alias: [m[0], m[1]] }]);
      }
    }
    const order = { Street: 0, Building: 1, Site: 2, Event: 3 };
    hits = scored.sort((a, b) => a[0] - b[0] || order[a[1].kind] - order[b[1].kind] || a[1].label.localeCompare(b[1].label)).slice(0, 12).map(x => x[1]);
    results.innerHTML = hits.map((h, i) => `<button data-i="${i}"><span class="kind">${h.kind}</span> ${esc(h.label)} ${when(h)}${h.alias
      ? `<span class="alias">recorded ${h.alias[0]} as «${esc(h.alias[1].length > 90 ? h.alias[1].slice(0, 88) + '…' : h.alias[1])}»</span>` : ''}</button>`).join('')
      || '<div class="muted none">nothing found</div>';
  };
  results.onclick = ev => { const b = (ev.target as HTMLElement).closest('button'); if (!b) return; const h = hits[+b.dataset.i!];
    results.innerHTML = ''; search.value = ''; h.go(h.alias); };
  search.onkeydown = e => { if (e.key === 'Enter' && hits[0]) { const h = hits[0]; results.innerHTML = ''; search.value = ''; h.go(h.alias); } };

  /** Street card: its name in the selected year, all dated records, origin of the name. */
  let streetOpen: string | null = null;
  function showStreet(code: string | null) {
    streetOpen = code; const st = code && A ? A.streets[code] : undefined; if (!st) return;
    siteOpen = true; card.hidden = false; hooks.highlightStreet?.(code);
    const nb = stripItems(code).length;
    const era = streetNameIn(st, Math.round(state.year));
    card.innerHTML = `<button class="x" title="close">×</button><h3>${esc(st.n)}</h3>
      <span class="tag">street</span><span class="tag">${st.h.length ? 'first record ' + st.h[0][0] : 'no dated record'}</span>
      ${nb ? `<p><button class="strip-open">See the buildings side by side (${nb})</button></p>` : ''}
      <dl><dt>Name in ${fmtYear(Math.round(state.year))}</dt><dd>${esc(era.name)} <span class="muted">(${esc(era.note)})</span></dd>
      ${st.o ? `<dt>Origin</dt><dd>${esc(st.o)}</dd>` : ''}
      <dt>Records</dt><dd><ul class="att">${st.h.map(h => `<li><b>${h[0]}</b> ${esc(h[1])}${h[2] ? ` <span class="muted">(${esc(h[2])})</span>` : ''}</li>`).join('') || '<li class="muted">none</li>'}</ul></dd>
      ${dataHtml([{ text: DATASET.stradario.label, id: DATASET.stradario.id, url: DATASET.stradario.url }])}</dl>`;
    wireData();
    $('.x', card).onclick = () => { streetOpen = null; showSite(null); hooks.highlightStreet?.(null); closeStrip(); };
    const so = card.querySelector<HTMLButtonElement>('.strip-open'); if (so) so.onclick = () => openStrip(code!);
  }

  // ---- street strip: both sides of the street, buildings face-on, numbered, coloured by construction period ----
  const strip = document.createElement('div'); strip.id = 'strip'; strip.className = 'glass'; strip.hidden = true; document.body.appendChild(strip);
  let stripCode: string | null = null;
  function closeStrip() { strip.hidden = true; stripCode = null; }
  /** buildings on a street: those addressed on it, plus corner buildings that also carry numbers on it */
  function stripItems(code: string) {
    const out: { r: Rec; a: AddrRec; pos: [number, number, number]; no: string[] }[] = [];
    for (const [id, a] of Object.entries(A!.recs)) {
      const r = recs[+id]; if (!r) continue;
      if (a.s === code && a.pos) out.push({ r, a, pos: a.pos, no: a.no ?? [] });
      else { const al = a.alt?.find(x => x[0] === code && x[2]); if (al) out.push({ r, a, pos: al[2]!, no: al[1] }); }
    }
    return out;
  }
  /** "2, 4 · 16–28r": black numbers, then the red (shop) range */
  const shortNo = (no: string[]) => { const f = no.map(fmtNo), bl = f.filter(n => !/r$/.test(n)), rd = f.filter(n => /r$/.test(n));
    return [bl.slice(0, 2).join(', ') + (bl.length > 2 ? '…' : ''), rd.length > 1 ? `${rd[0].slice(0, -1)}–${rd[rd.length - 1]}` : rd[0] ?? ''].filter(Boolean).join(' · '); };
  function openStrip(code: string) {
    stripCode = code; const st = A!.streets[code]; const y = Math.round(state.year);
    const items = stripItems(code).filter(x => isAlive(x.r, y)).map(x => ({ ...x, a: { ...x.a, pos: x.pos, no: x.no } }));
    const L = Math.max(30, ...items.map(x => x.a.pos![0] + x.a.pos![2] / 2)), L0 = Math.min(0, ...items.map(x => x.a.pos![0] - x.a.pos![2] / 2));
    const Wpx = Math.min(innerWidth - 80, 1500), sx = (Wpx - 40) / (L - L0), sy = Math.min(2.2, sx * 1.6), row = 46 * 2.2 + 26;
    const colorOf = (r: Rec) => PERIODS[Math.max(0, PERIODS.findIndex(p => r.start <= p.to))]?.color ?? '#999';
    const label = (a: AddrRec) => y >= 1866 ? shortNo(a.no ?? []) : y >= 1808 && a.fr?.length ? a.fr[0][0] : '';
    const fit = (t: string, w: number) => t.length * 5.4 <= w + 4 ? t : (t.split(' · ').pop()!.split('–')[0] + (t.includes('–') ? '…' : '')).slice(0, Math.max(0, Math.floor((w + 4) / 5.4)));
    const historic = (r: Rec) => !!r.name || r.start < 1700;
    const g = (side: number, base: number) => items.filter(x => x.a.pos![1] === side).sort((p, q) => p.a.pos![0] - q.a.pos![0]).map(({ r, a }) => {
      const [along, , w] = a.pos!; const x = 20 + (along - w / 2 - L0) * sx, ww = Math.max(2, w * sx - 1), hh = Math.min(r.h, 46) * sy;
      return `<g class="b" data-id="${r.id}"><rect x="${x.toFixed(1)}" y="${(base - hh).toFixed(1)}" width="${ww.toFixed(1)}" height="${hh.toFixed(1)}" fill="${colorOf(r)}"${historic(r) ? ' class="hist"' : ''}/>
        <text x="${(x + ww / 2).toFixed(1)}" y="${base + 11}" text-anchor="middle">${esc(fit(label(a), ww))}</text>
        ${r.name ? `<text class="nm" x="${(x + ww / 2).toFixed(1)}" y="${(base - hh - 4).toFixed(1)}" text-anchor="middle">${esc(r.name.length > 26 ? r.name.slice(0, 25) + '…' : r.name)}</text>` : ''}
        <title>${esc(r.name || 'Building')} · ${fmtYear(r.start)}${r.end ? '–' + fmtYear(r.end) : ''} · ${r.h.toFixed(0)} m${a.no?.length ? ' · n. ' + a.no.map(fmtNo).join(', ') : ''}</title></g>`;
    }).join('');
    const H = row * 2 + 20;
    strip.innerHTML = `<div class="strip-head"><b>${esc(streetNameIn(st, y).name)}</b> <span class="muted">· ${items.length} buildings standing in ${fmtYear(y)} · left side above, right side below · numbers ${y >= 1866 ? 'today' : y >= 1808 ? '1808 (French)' : 'not yet in use'}</span>
      <button class="x" title="close">×</button></div>
      <svg width="${Wpx}" height="${H}" viewBox="0 0 ${Wpx} ${H}">
        <line x1="10" x2="${Wpx - 10}" y1="${row - 14}" y2="${row - 14}" class="gl"/><line x1="10" x2="${Wpx - 10}" y1="${2 * row}" y2="${2 * row}" class="gl"/>
        ${g(-1, row - 14)}${g(1, 2 * row)}</svg>
      <div class="muted small">Colour = construction period · outlined = historic or named building · heights ×${(sy / sx).toFixed(1)} · click a building to open it</div>`;
    strip.hidden = false;
    $('.x', strip).onclick = closeStrip;
    strip.querySelector('svg')!.onclick = ev => { const b = (ev.target as Element).closest('g.b') as SVGGElement | null; if (!b) return;
      const r = recs[+b.dataset.id!]; set({ selected: r.id }); hooks.flyTo(r.c[0], r.c[1], 180); };
  }

  // source layers that are not buildings (only listed while something of theirs stands in the current year)
  const layers = (col: (l: typeof SOURCE_LAYERS[number]) => string) => SOURCE_LAYERS.map(l => ({ l, n: hooks.layerCount?.(l.id) ?? 0 })).filter(x => x.n > 0)
    .map(({ l, n }) => `<div class="lg"><i style="background:${col(l)}"></i>${esc(l.name)}<span>${n.toLocaleString()}</span></div>`).join('');
  function legend() {
    const L = $('#legend', side); const y = state.year;
    if (state.color === 'period') {
      const cnt = PERIODS.map(() => 0); recs.forEach(r => { if (isAlive(r, y)) cnt[PERIODS.findIndex(p => r.start <= p.to)]++; });
      L.innerHTML = layers((l) => l.color) + PERIODS.map((p, i) => `<div class="lg"><i style="background:${p.color}"></i>${p.name}<span>${cnt[i].toLocaleString()}</span></div>`).join('');   // oldest first
    } else if (state.color === 'confidence') {
      const cnt: Record<string, number> = { documented: 0, inferred: 0, conjectural: 0 }; recs.forEach(r => { if (isAlive(r, y)) cnt[r.conf]++; });
      const txt: Record<string, string> = { documented: 'surveyed / dated by a source', inferred: 'from historic maps & data', conjectural: 'estimated (typology, zone)' };
      L.innerHTML = Object.keys(cnt).map(k => `<div class="lg"><i style="background:${CONF_COLORS[k]}"></i>${k} <em>${txt[k]}</em><span>${cnt[k].toLocaleString()}</span></div>`).join('');
      L.innerHTML = layers((l) => CONF_COLORS[l.conf]) + L.innerHTML;
    } else L.innerHTML = '<p class="muted">Facades are procedural (v1); roofs are the 2017 orthophoto; heights from LiDAR 2023.</p>';
  }

  /** Sources folded under "Data" so the card opens compact; the open/closed choice is kept between cards. */
  let dataOpen = false;
  const dataHtml = (L: SourceLink[]) => `<dt>Data</dt><dd><details class="data"${dataOpen ? ' open' : ''}><summary>${L.length} source${L.length === 1 ? '' : 's'}</summary><ul class="src">${srcHtml(L)}</ul><p class="muted small">Ids refer to docs/DATA-SOURCES.md.</p></details></dd>`;
  const wireData = () => card.querySelectorAll<HTMLDetailsElement>('details.data').forEach(d => d.ontoggle = () => { dataOpen = d.open; });
  const srcHtml = (L: SourceLink[]) => L.map(l => `<li>${l.id ? `<span class="sid">${l.id}</span> ` : ''}${l.url
    ? `<a target="_blank" rel="noopener" href="${esc(l.url)}">${esc(l.text)}</a>` : esc(l.text)}</li>`).join('');

  /** Address block: street name in the selected year, today's numbers, the 1808 French number with its documents. */
  function addressHtml(id: number, y: number): { html: string; links: SourceLink[] } {
    const A = hooks.addresses; const a = A?.recs[String(id)]; if (!A || !a) return { html: '', links: [] };
    const links: SourceLink[] = []; let html = '';
    const st = a.s ? A.streets[a.s] : undefined;
    if (st) {
      const era = streetNameIn(st, Math.round(y));
      const nums = a.no?.length ? ' ' + a.no.map(fmtNo).join(', ') : '';
      html += `<dt>Street in ${fmtYear(Math.round(y))}</dt><dd>${esc(era.name)} <span class="muted">(${esc(era.note)})</span></dd>`;
      html += `<dt>Address today</dt><dd>${a.ap ? '<span class="muted">near</span> ' : ''}${esc(st.n)}${esc(nums)}${(a.alt ?? []).map(([c, n]) => `<br><span class="muted">also</span> ${esc(A.streets[c]?.n ?? '')} ${esc(n.map(fmtNo).join(', '))}`).join('')}</dd>`;
      if (st.h.length || st.o) html += `<dt>Street name</dt><dd><details><summary>${st.h.length} dated records${st.since ? `, present name since ${st.since}` : ''}</summary>
        ${st.o ? `<p class="muted">${esc(st.o)}</p>` : ''}<ul class="att">${st.h.map(h => `<li><b>${h[0]}</b> ${esc(h[1])}${h[2] ? ` <span class="muted">(${esc(h[2])})</span>` : ''}</li>`).join('')}</ul></details></dd>`;
      links.push({ text: DATASET.stradario.label, id: DATASET.stradario.id, url: DATASET.stradario.url });
      if (a.no?.length) links.push({ text: DATASET.civici.label, id: DATASET.civici.id, url: DATASET.civici.url });
    }
    if (a.fr?.length) {
      const inUse = y >= 1808 && y < 1866;
      html += `<dt>Number 1808–1865</dt><dd>${a.fr.map(f => `n. <b>${esc(f[0])}</b> · ${esc(f[1])}${inUse ? ' <span class="tag">in use</span>' : ''}
        <br><span class="muted">${esc(f[2])}</span>${f[3].length ? '<br>' + f[3].map((u, i) => `<a target="_blank" rel="noopener" href="${esc(u)}">document ${i + 1}</a>`).join(' · ') : ''}`).join('<hr>')}
        <br><span class="muted">city-wide Napoleonic numbering; replaced by per-street numbers in the 1860s · matched by distance</span></dd>`;
      links.push({ text: DATASET.francesi.label + (a.fr[0][4] ? ` (${a.fr[0][4]})` : ''), id: DATASET.francesi.id, url: DATASET.francesi.url });
    }
    return { html, links };
  }

  function showCard(id: number) {
    if (id < 0) { if (!siteOpen) card.hidden = true; return; }
    siteOpen = false; streetOpen = null;
    const r = recs[id]; card.hidden = false;
    const title = r.name || ({ building: 'Building', demolished: 'Demolished building', ohm: 'Historic structure', gate: 'City gate', roman: 'Roman structure' } as any)[r.kind];
    const wiki = r.wiki ? `https://it.wikipedia.org/wiki/${encodeURIComponent(r.wiki.replace(/ /g, '_'))}` : '';
    const ll = sceneToLatLon(r.c[0], r.c[1]);
    const addr = addressHtml(id, state.year);
    const links = [...r.src.map(t => linkSource(t, { lat: ll.lat, lon: ll.lon, qid: r.qid })), ...addr.links];
    card.innerHTML = `<button class="x" title="close">×</button><h3>${esc(title)}</h3>
      <span class="tag ${r.conf}">${r.conf}</span><span class="tag">${fmtYear(r.start)} → ${r.end ? fmtYear(r.end) : 'today'}</span>
      <dl>${addr.html}<dt>Height</dt><dd>${r.h.toFixed(1)} m${r.kind === 'building' ? ' (LiDAR 2023)' : ' (estimate)'}</dd>
      ${r.sub ? `<dt>Type</dt><dd>${esc(r.sub)}</dd>` : ''}
      ${dataHtml(links)}</dl>
      <p>${r.qid ? `<a target="_blank" rel="noopener" href="https://www.wikidata.org/wiki/${r.qid}">Wikidata ${r.qid}</a> ` : ''}${wiki ? `<a target="_blank" rel="noopener" href="${wiki}">Wikipedia</a> ` : ''}<a target="_blank" rel="noopener" href="https://www.openstreetmap.org/#map=19/${ll.lat.toFixed(6)}/${ll.lon.toFixed(6)}">Map</a></p>
`;
    $('.x', card).onclick = () => set({ selected: -1 }); wireData();
  }

  /** Card for things placed from a source rather than from the building data (huts, kilns, graves, …). */
  let siteOpen = false;
  function showSite(info: { name: string; kind: string; from: number; to: number; src: string; conf?: string } | null) {
    if (!info) { siteOpen = false; streetOpen = null; card.hidden = true; return; }
    siteOpen = true; streetOpen = null; card.hidden = false;
    const page = A07_PAGES.find(([r]) => r.test(info.src))?.[1] ?? DATASET.a07.url;
    card.innerHTML = `<button class="x" title="close">×</button><h3>${esc(info.name)}</h3>
      <span class="tag ${info.conf ?? 'inferred'}">${info.conf ?? 'inferred'}</span><span class="tag">${fmtYear(info.from)} → ${fmtYear(info.to)}</span>
      <dl><dt>What</dt><dd>${esc(info.kind)}</dd>
      <dt>Placement</dt><dd class="muted">Site from the finds; layout of huts, kilns and animals reconstructed.</dd>
      <dt>Layer</dt><dd>${esc(SOURCE_LAYERS[0].name)}: ${esc(SOURCE_LAYERS[0].note)}</dd>
      ${dataHtml([{ text: info.src, id: 'A07', url: page }])}</dl>`;
    wireData();
    $('.x', card).onclick = () => showSite(null);
  }

  let lastYear = NaN;
  function update(changed: any) {
    const e = epochAt(state.year);
    if (Math.round(state.year) !== lastYear || 'color' in changed) {
      lastYear = Math.round(state.year);
      const alive = recs.reduce((n, r) => n + (r.kind !== 'roman' && isAlive(r, state.year) ? 1 : 0), 0);
      hud.innerHTML = `<div class="era">${esc(e.name)}</div><div class="kv"><div>Government<b>${esc(e.gov)}</b></div><div>Population<b>${esc(e.pop)}</b></div><div>Structures standing<b>${alive.toLocaleString()}</b></div></div>`;
      legend();
      if (state.selected >= 0 && !('selected' in changed)) showCard(state.selected);   // street name follows the year
      else if (streetOpen && state.selected < 0) showStreet(streetOpen);
      if (stripCode) openStrip(stripCode);
    }
    modes.querySelectorAll('button').forEach(b => b.classList.toggle('on', (b as HTMLElement).dataset.m === state.mode));
    side.querySelectorAll('#cm button').forEach(b => b.classList.toggle('on', (b as HTMLElement).dataset.c === state.color));
    side.hidden = state.mode !== 'sources'; live.hidden = state.mode !== 'live';
    if (document.activeElement !== dt) dt.value = state.date; hr.value = String(state.hour); ts.checked = state.tiltShift;
    if ('selected' in changed) showCard(state.selected);
  }
  return { update, showSite, legend: () => { if (state.mode === 'sources') legend(); }, liveNote: (t: string) => ($('#livenote', live).textContent = t) };
}

export function toast(msg: string) {
  const t = document.createElement('div'); t.className = 'toast'; t.textContent = msg; document.body.appendChild(t);
  setTimeout(() => t.remove(), 3500);
}
