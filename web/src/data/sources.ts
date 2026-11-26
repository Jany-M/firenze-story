// Every source line shown in the inspector card resolves to an entry of docs/DATA-SOURCES.md (register id) and,
// where one exists, a public URL: the dataset page, the map at this spot, the Wikidata item, or the project doc that
// explains an estimate. Only verified URLs are used; derived estimates point to the documentation.

/** Public repository (docs links). Change here if the repository gets another name. */
export const REPO = 'https://github.com/Jany-M/firenze-story/blob/main/';
const COMUNE = (id: string) => `https://data.comune.fi.it/datastore/dataset/${id}`;
const WMS = 'https://tms.comune.fi.it/tiles/service/wms?request=GetCapabilities&service=WMS';

export const DATASET = {
  stradario: { id: 'H20', label: 'Comune di Firenze – Stradario storico e amministrativo', url: COMUNE('a870a547-a3a3-4a4f-9380-8012074c8f77') },
  civici: { id: 'H21', label: 'Comune di Firenze – Civici (house numbers)', url: COMUNE('11430710-56eb-4444-bd6f-c5433155afc5') },
  francesi: { id: 'H22', label: 'Comune di Firenze – Numeri Civici Francesi', url: COMUNE('670f268a-832e-4c90-8045-2a343d54192d') },
  a07: { id: 'A07', label: 'Villanovan / Etruscan Florence (web syntheses)', url: 'https://www.florencecity.it/la-firenze-villanoviana-ed-etrusca/' },
};
/** Pages of the A07 syntheses, matched by the site name written in each source line. */
export const A07_PAGES: [RegExp, string][] = [
  [/florencecity/i, 'https://www.florencecity.it/la-firenze-villanoviana-ed-etrusca/'],
  [/tuttatoscana/i, 'https://tuttatoscana.net/storia-e-microstoria-2/gli-etruschi-fra-arno-e-appennino-prima-parte/'],
  [/visittuscany/i, 'https://www.visittuscany.com/it/itinerari/da-fiesole-a-firenze-testimonianze-etrusche/'],
  [/conoscifirenze/i, 'https://www.conoscifirenze.it/come-vivevamo-a-firenze/1576-i-primi-insediamenti.html'],
];

export interface SourceLink { text: string; id: string; url?: string }
type Ctx = { lat: number; lon: number; qid?: string };
const RULES: { re: RegExp; id: string; url: (m: RegExpMatchArray, c: Ctx) => string | undefined }[] = [
  { re: /^OSM footprint/i, id: 'S07', url: (_, c) => `https://www.openstreetmap.org/#map=19/${c.lat.toFixed(6)}/${c.lon.toFixed(6)}` },
  { re: /^LiDAR 2023/i, id: 'S03', url: () => COMUNE('dsm-lidar-2023') },
  { re: /Catasto Generale Toscano/i, id: 'H01', url: () => WMS },
  { re: /Fantozzi|IGM 1873|1937|1843|1873/i, id: 'H16', url: () => WMS },
  { re: /OpenHistoricalMap/i, id: 'H12', url: (_, c) => `https://www.openhistoricalmap.org/#map=18/${c.lat.toFixed(6)}/${c.lon.toFixed(6)}` },
  { re: /Wikidata (Q\d+)/i, id: 'H13', url: m => `https://www.wikidata.org/wiki/${m[1]}` },
  { re: /Dati archeologici/i, id: 'A03', url: () => COMUNE('92dd6b30-72eb-48e1-bd1d-d0b5219d8479') },
  { re: /historiography/i, id: 'H13', url: (_, c) => c.qid ? `https://www.wikidata.org/wiki/${c.qid}` : REPO + 'docs/HISTORY.md' },
  { re: /Landmark model v1 – Campanile/i, id: 'M05', url: () => REPO + 'docs/landmarks/CAMPANILE-BAPTISTERY.md' },
  { re: /Landmark model v1 – Baptistery/i, id: 'M05', url: () => REPO + 'docs/landmarks/CAMPANILE-BAPTISTERY.md' },
  { re: /Landmark model v1 – Palazzo Vecchio/i, id: 'M06', url: () => REPO + 'docs/landmarks/PALAZZO-VECCHIO.md' },
  { re: /Landmark model v1 – Ponte Vecchio/i, id: 'M07', url: () => REPO + 'docs/landmarks/PONTE-VECCHIO.md' },
  { re: /Landmark model v1 – Santa Croce/i, id: 'M08', url: () => REPO + 'docs/landmarks/SANTA-CROCE.md' },
  { re: /Landmark model v1 – Santa Maria Novella/i, id: 'M09', url: () => REPO + 'docs/landmarks/SANTA-MARIA-NOVELLA.md' },
  { re: /Landmark model v1 – Orsanmichele/i, id: 'M10', url: () => REPO + 'docs/landmarks/ORSANMICHELE.md' },
  { re: /Landmark model v1 – Bargello/i, id: 'M11', url: () => REPO + 'docs/landmarks/BARGELLO.md' },
  { re: /Landmark model v1 – San Lorenzo/i, id: 'M17', url: () => REPO + 'docs/landmarks/SAN-LORENZO.md' },
  { re: /Landmark model v1 – Palazzo Medici Riccardi/i, id: 'M18', url: () => REPO + 'docs/landmarks/MEDICI-RICCARDI.md' },
  { re: /Landmark model v1 – Corridoio Vasariano/i, id: 'M19', url: () => REPO + 'docs/landmarks/CORRIDOIO-VASARIANO.md' },
  { re: /Landmark model v1 – Palazzo Pitti/i, id: 'M20', url: () => REPO + 'docs/landmarks/PITTI-BOBOLI.md' },
  { re: /Landmark model v1 – Boboli/i, id: 'M21', url: () => REPO + 'docs/landmarks/PITTI-BOBOLI.md' },
  { re: /Landmark model v1 – Uffizi/i, id: 'M16', url: () => REPO + 'docs/landmarks/UFFIZI.md' },
  { re: /Landmark model v1 – Loggia dei Lanzi/i, id: 'M12', url: () => REPO + 'docs/landmarks/LOGGIA-DEI-LANZI.md' },
  { re: /Landmark model v1 – Le mura/i, id: 'M14', url: () => REPO + 'docs/landmarks/MURA.md' },
  { re: /Landmark model/i, id: 'M04', url: () => REPO + 'docs/landmarks/DUOMO.md' },
  { re: /Risanamento/i, id: 'H11', url: () => REPO + 'docs/HISTORY.md' },
  { re: /A07|florencecity|tuttatoscana|visittuscany|conoscifirenze/i, id: 'A07', url: m => A07_PAGES.find(([r]) => r.test(m.input ?? ''))?.[1] ?? DATASET.a07.url },
  { re: /estimat|typology|conjectural|absent|present|^end:|ground;|layout/i, id: 'D01–D03', url: () => REPO + 'docs/BUILDINGS.md' },
];
export function linkSource(text: string, c: Ctx): SourceLink {
  for (const r of RULES) { const m = text.match(r.re); if (m) return { text, id: r.id, url: r.url(m, c) }; }
  return { text, id: '' };
}

/** Scene metres (x east, z south of 681500 E / 4849000 N, EPSG:25832) -> WGS84 lat/lon (UTM zone 32 inverse). */
export function sceneToLatLon(x: number, z: number) {
  const E = x + 681500 - 500000, N = 4849000 - z;
  const a = 6378137, f = 1 / 298.257222101, e2 = f * (2 - f), k0 = 0.9996, ep2 = e2 / (1 - e2);
  const M = N / k0, mu = M / (a * (1 - e2 / 4 - 3 * e2 * e2 / 64 - 5 * e2 ** 3 / 256));
  const e1 = (1 - Math.sqrt(1 - e2)) / (1 + Math.sqrt(1 - e2));
  const p1 = mu + (3 * e1 / 2 - 27 * e1 ** 3 / 32) * Math.sin(2 * mu) + (21 * e1 * e1 / 16 - 55 * e1 ** 4 / 32) * Math.sin(4 * mu)
    + (151 * e1 ** 3 / 96) * Math.sin(6 * mu) + (1097 * e1 ** 4 / 512) * Math.sin(8 * mu);
  const s = Math.sin(p1), c = Math.cos(p1), t = Math.tan(p1);
  const N1 = a / Math.sqrt(1 - e2 * s * s), T1 = t * t, C1 = ep2 * c * c, R1 = a * (1 - e2) / (1 - e2 * s * s) ** 1.5, D = E / (N1 * k0);
  const lat = p1 - (N1 * t / R1) * (D * D / 2 - (5 + 3 * T1 + 10 * C1 - 4 * C1 * C1 - 9 * ep2) * D ** 4 / 24
    + (61 + 90 * T1 + 298 * C1 + 45 * T1 * T1 - 252 * ep2 - 3 * C1 * C1) * D ** 6 / 720);
  const lon = (D - (1 + 2 * T1 + C1) * D ** 3 / 6 + (5 - 2 * C1 + 28 * T1 - 3 * C1 * C1 + 8 * ep2 + 24 * T1 * T1) * D ** 5 / 120) / c;
  return { lat: lat * 180 / Math.PI, lon: 9 + lon * 180 / Math.PI };
}

// ---------------------------------------------------------------- addresses (pipeline/22_addresses.py)
export interface Street { n: string; o: string; since: number | null; h: [number, string, string][]; c?: [number, number]; g?: [number, number][][] }
export interface AddrRec { s?: string; no?: string[]; alt?: [string, string[], [number, number, number]?][]; fr?: [string, string, string, string[], string][]; pos?: [number, number, number]; ap?: 1 }
export interface Addresses { streets: Record<string, Street>; recs: Record<string, AddrRec> }

/** What the street was called in `year`: today's name once attested, else the latest earlier attestation. */
export function streetNameIn(st: Street, year: number): { name: string; note: string; attested?: [number, string, string] } {
  if (st.since != null && year >= st.since) return { name: st.n, note: `name recorded since ${st.since}` };
  const earlier = st.h.filter(a => a[0] <= year);
  if (earlier.length) { const a = earlier[earlier.length - 1]; return { name: `«${a[1]}»`, note: `recorded ${a[0]}${a[2] ? ' · ' + a[2] : ''}`, attested: a }; }
  if (st.h.length) return { name: st.n, note: `no record before ${st.h[0][0]} (today's name shown)` };
  return { name: st.n, note: "today's name (no dated record)" };
}
export const fmtNo = (n: string) => n.replace(/\s*R$/i, 'r').replace(/\s+/g, '');
