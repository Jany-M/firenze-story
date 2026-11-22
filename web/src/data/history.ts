// Historical reference data used by the UI and the simulation.
// Dates follow standard historiography; every entry carries a source note. Verify before publishing.

export interface Epoch { from: number; to: number; name: string; gov: string; pop: string }
export const EPOCHS: Epoch[] = [
  { from: -800, to: -60, name: 'Etruscan & pre-Roman plain', gov: 'Etruscan Faesulae (Fiesole) on the hill', pop: 'scattered huts & kilns' },
  { from: -59, to: 284, name: 'Roman colony of Florentia', gov: 'Rome (colonia, trad. 59 BC; archaeology: c. 30–15 BC)', pop: '~ 10,000 (est.)' },
  { from: 285, to: 799, name: 'Late antiquity', gov: 'Late Empire · Ostrogoths · Byzantines · Lombards', pop: 'declining' },
  { from: 800, to: 1114, name: 'Carolingian & Matildine town', gov: 'Carolingian counts · March of Tuscany', pop: '~ 15,000 (est.)' },
  { from: 1115, to: 1249, name: 'Commune of the towers', gov: 'Comune (consuls, podestà)', pop: '~ 30,000–50,000' },
  { from: 1250, to: 1347, name: 'Guild republic', gov: 'Primo Popolo · Priori delle Arti', pop: '~ 100,000 (before 1348)' },
  { from: 1348, to: 1433, name: 'After the Black Death', gov: 'Republic (oligarchy, Albizzi)', pop: '~ 40,000–60,000' },
  { from: 1434, to: 1529, name: 'Renaissance republic', gov: 'Republic under Medici influence · Savonarola 1494–98', pop: '~ 60,000–70,000' },
  { from: 1530, to: 1736, name: 'Medici Duchy & Grand Duchy', gov: 'Medici dukes / grand dukes', pop: '~ 60,000–70,000' },
  { from: 1737, to: 1864, name: 'Lorraine Tuscany', gov: 'Habsburg-Lorraine grand dukes (French rule 1799–1814)', pop: '~ 80,000–115,000' },
  { from: 1865, to: 1870, name: 'Firenze Capitale', gov: 'Kingdom of Italy – capital', pop: '~ 150,000' },
  { from: 1871, to: 1943, name: 'Risanamento & modern city', gov: 'Kingdom of Italy', pop: '~ 170,000–320,000' },
  { from: 1944, to: 1999, name: 'War, reconstruction, flood', gov: 'Italian Republic (from 1946)', pop: '~ 360,000–450,000' },
  { from: 2000, to: 2100, name: 'Today', gov: 'Comune di Firenze', pop: '~ 360,000' },
];
export const epochAt = (y: number) => EPOCHS.find(e => y >= e.from && y <= e.to) ?? EPOCHS[EPOCHS.length - 1];

export interface HistEvent { year: number; date?: string; hour?: number; title: string; place: string; at: [number, number]; live?: string; note: string }
// at = local scene coords [x, z] (metres from origin 681500E/4849000N, z = south)
export const EVENTS: HistEvent[] = [
  { year: -800, title: 'Villanovan village by the Arno ford', place: 'Orsanmichele', at: [-27, 109], note: 'Oval huts on stilts, hearths and kilns, flocks; cremation graves to the west (inferred layout, source A07).' },
  { year: -700, title: 'Orientalizing hut between Badia and Bargello', place: 'Badia – Bargello', at: [184, 151], note: 'Hut floor with Orientalizing pottery, some vases from Asia Minor (A07).' },
  { year: -59, title: 'Foundation of Florentia (traditional date)', place: 'Castrum', at: [-93, 37], note: 'Roman colony; archaeology points to c. 30–15 BC.' },
  { year: 1296, date: '09-08', title: 'Foundation stone of Santa Maria del Fiore', place: 'Duomo', at: [113, -150], note: 'Arnolfo di Cambio; replaces Santa Reparata.' },
  { year: 1333, date: '11-04', title: 'Great flood of the Arno', place: 'Arno', at: [-155, 427], note: 'Destroys Ponte Vecchio and other bridges.' },
  { year: 1348, title: 'Black Death', place: 'City-wide', at: [0, 0], note: 'Population roughly halved.' },
  { year: 1436, date: '03-25', title: 'Consecration of the Duomo with Brunelleschi’s dome', place: 'Duomo', at: [113, -150], note: 'Dome built 1420–1436.' },
  { year: 1478, date: '04-26', title: 'Pazzi conspiracy', place: 'Duomo', at: [113, -150], note: 'Giuliano de’ Medici killed during Mass.' },
  { year: 1497, date: '02-07', title: 'Bonfire of the Vanities', place: 'Piazza della Signoria', at: [39, 243], note: 'Savonarola.' },
  { year: 1498, date: '05-23', title: 'Execution of Savonarola', place: 'Piazza della Signoria', at: [39, 243], note: '' },
  { year: 1504, date: '05-14', title: 'The David leaves the Opera del Duomo', place: 'Opera del Duomo → Piazza della Signoria', at: [232, -150], live: 'david', note: 'At sunset the wall over the yard gate is broken open; 40+ men move the statue in a timber frame on greased beams, the marble hung free inside. Four days, ≈600 m; arrives 18 May (Landucci; Opera di Santa Maria del Fiore). Route presumed.' },
  { year: 1504, date: '06-08', title: 'The David set on the ringhiera', place: 'Piazza della Signoria', at: [64, 269], note: 'Placed where Donatello’s Judith stood, by the door of the palace; unveiled 8 September 1504.' },
  { year: 1873, title: 'The David moved to the Accademia', place: 'Piazza della Signoria → Galleria dell’Accademia', at: [64, 269], note: 'Taken indoors to protect it from the weather; the square stays without it until the copy of 1910.' },
  { year: 1910, title: 'A marble copy of the David in Piazza della Signoria', place: 'Piazza della Signoria', at: [64, 269], note: 'Copy by Luigi Arrighetti at the original place.' },
  { year: 1530, date: '02-17', title: 'Calcio during the siege', place: 'Piazza Santa Croce', at: [507, 304], live: 'calcio', note: 'Played in defiance of the imperial army besieging the city.' },
  { year: 1550, date: '05-14', title: 'A market morning in Mercato Vecchio', place: 'Mercato Vecchio', at: [-90, 14], live: 'market', note: 'Daily market around the Colonna dell’Abbondanza (until 1885).' },
  { year: 1622, date: '03-27', title: 'Scoppio del Carro – the new Brindellone', place: 'Piazza del Duomo', at: [-1, -135], live: 'scoppio', note: 'Easter Sunday: the colombina runs along a wire from the altar and lights the cart (cart built 1622).' },
  { year: 1865, title: 'Florence capital of Italy · walls demolished (Poggi plan)', place: 'Viali', at: [0, 0], note: '1865–1871.' },
  { year: 1888, title: 'Mercato Vecchio & ghetto demolished', place: 'Piazza della Repubblica', at: [-90, 14], note: 'Risanamento 1885–1895.' },
  { year: 1944, date: '08-03', hour: 23, title: 'The Night of the Bridges', place: 'Arno', at: [-155, 427], live: 'ponti1944', note: 'From the evening of 3 August to dawn on the 4th the retreating German army blows up every bridge but Ponte Vecchio; Por Santa Maria, Via de\' Bardi, Borgo San Jacopo and Via Guicciardini are mined to block its approaches.' },
  { year: 1966, date: '11-04', title: 'The great flood', place: 'Santa Croce', at: [507, 304], note: 'Water up to ~5 m in Santa Croce.' },
  { year: 2026, date: '04-05', title: 'Scoppio del Carro (Easter)', place: 'Piazza del Duomo', at: [-1, -135], live: 'scoppio', note: 'Fire struck from the Holy Sepulchre flints at Santi Apostoli; the colombina flies at 11.' },
  { year: 2026, date: '06-24', title: 'Calcio Storico final (San Giovanni)', place: 'Piazza Santa Croce', at: [507, 304], live: 'calcio', note: 'Modern revival (since 1930).' },
];

// Construction-period palette (Sources view), Paris-style
export const PERIODS: { to: number; name: string; color: string }[] = [
  { to: 499, name: 'Roman & late antique', color: '#7b5ea7' },
  { to: 1249, name: 'Early medieval & communal', color: '#3f6fb5' },
  { to: 1399, name: 'Gothic / guild republic', color: '#4aa3c7' },
  { to: 1529, name: 'Renaissance', color: '#5fb08a' },
  { to: 1736, name: 'Medici (grand) duchy', color: '#b7c15a' },
  { to: 1864, name: 'Lorraine Tuscany', color: '#e6c35c' },
  { to: 1899, name: 'Capital & Risanamento', color: '#e89a4f' },
  { to: 1945, name: '1900 – WWII', color: '#d9653b' },
  { to: 9999, name: 'Post-war & contemporary', color: '#b8322e' },
];
// Non-building source layers painted in the Sources view (props placed from a source, not from the building data)
export const SOURCE_LAYERS = [
  { id: 'A07', name: 'Etruscan – Villanovan', note: 'huts, kilns, graves, stelae, livestock, dugouts (A07, inferred)', color: '#c2603d', conf: 'inferred' },
];
export const CONF_COLORS: Record<string, string> = { documented: '#6fbf73', inferred: '#e0b84f', conjectural: '#7f93ad' };

// Clothing palettes per era (placeholder figures are tinted until costumed characters exist)
export const CLOTHING: { to: number; colors: string[] }[] = [
  { to: -60, colors: ['#8a7356', '#6e5b44', '#a08a68', '#5d4b38'] },
  { to: 499, colors: ['#e8e0cc', '#c9b892', '#8c3b2e', '#d8cdb2', '#6b5844'] },          // tunics, togas
  { to: 1349, colors: ['#6b4a35', '#8c2f28', '#3f4f6b', '#7a6a4a', '#5e5e52'] },
  { to: 1529, colors: ['#9b1c1c', '#2b2b2b', '#1f3a5f', '#6a4a2e', '#c8b78e', '#4a5a2a'] }, // lucco red, black, blue, brown
  { to: 1736, colors: ['#1a1a1a', '#5a1e1e', '#2f3b52', '#6b5b3e', '#c9bfa5'] },
  { to: 1899, colors: ['#2b2b2b', '#4a3b2e', '#6b6b6b', '#d8cfbf', '#3a4a5a'] },
  { to: 1960, colors: ['#3b3b3b', '#5b5b5b', '#2f3f5f', '#8a7a6a', '#d0c8b8'] },
  { to: 9999, colors: ['#1f4f8f', '#d8d8d8', '#2b2b2b', '#c84b3b', '#7a8a5a', '#e0b84f'] },
];
export const clothingFor = (y: number) => (CLOTHING.find(c => y <= c.to) ?? CLOTHING[CLOTHING.length - 1]).colors;

export const MAP_OVERLAYS = [
  { id: 'none', name: 'No map' },
  { id: 'map_cadastre1830s.png', name: 'Catasto Generale Toscano 1830s (partial)' },
  { id: 'map_1843.jpg', name: 'Fantozzi map 1843' },
  { id: 'map_1873.jpg', name: 'IGM map 1873' },
  { id: 'map_1937.jpg', name: 'City map 1937' },
  { id: 'ortho2017.jpg', name: 'Orthophoto 2017' },
];

export const CREDITS = [
  'Comune di Firenze – open data (CC-BY 4.0): LiDAR 2023, 1:500 cartography, archaeology, historic maps & cadastre (WMS)',
  '© OpenStreetMap contributors (ODbL)', 'OpenHistoricalMap contributors (CC0)', 'Wikidata (CC0)',
  'Placeholder figure: three.js example “Xbot” (Mixamo) – to be replaced by period characters',
];
