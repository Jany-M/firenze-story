// Statues, columns and fountains in the squares: dated placeholders until each one gets its own model (refinement list,
// docs/STATUES.md). Positions are from OpenStreetMap (scene x = east, z = south, metres from the origin) unless the note
// says otherwise. conf follows the app's confidence scale.
export type StatueKind = 'equestrian' | 'figure' | 'column' | 'fountain' | 'obelisk' | 'monument' | 'cross';
export interface Statue { name: string; place: string; at: [number, number]; from: number; to?: number; kind: StatueKind; h: number; conf: 'documented' | 'inferred' | 'speculative'; note?: string }

export const STATUES: Statue[] = [
  { name: 'Fountain of Neptune', place: 'Piazza della Signoria', at: [72.2, 244.5], from: 1565, kind: 'fountain', h: 9, conf: 'documented', note: 'Ammannati; giant unveiled 1565, fountain finished 1574.' },
  { name: 'Cosimo I', place: 'Piazza della Signoria', at: [76.5, 219.5], from: 1594, kind: 'equestrian', h: 9, conf: 'documented', note: 'Giambologna, bronze on a marble base.' },
  { name: 'Marzocco', place: 'Piazza della Signoria', at: [70.0, 257.1], from: 1420, kind: 'figure', h: 3, conf: 'documented', note: 'Donatello\'s lion on the ringhiera; a copy since 1885.' },
  { name: 'Colonna dell\'Abbondanza', place: 'Mercato Vecchio / Piazza della Repubblica', at: [-59.0, 27.9], from: 1431, to: 1890, kind: 'column', h: 12, conf: 'documented', note: 'Removed with the Mercato Vecchio demolition.' },
  { name: 'Colonna dell\'Abbondanza (put back)', place: 'Piazza della Repubblica', at: [-59.0, 27.9], from: 1956, kind: 'column', h: 12, conf: 'documented' },
  { name: 'Vittorio Emanuele II', place: 'Piazza Vittorio Emanuele (Repubblica)', at: [-30, 10], from: 1890, to: 1932, kind: 'equestrian', h: 10, conf: 'inferred', note: 'Position in the middle of the square inferred; moved to the Cascine in 1932.' },
  { name: 'Vittorio Emanuele II', place: 'Piazzale Vittorio Veneto (Cascine)', at: [-1639.5, -475.1], from: 1932, kind: 'equestrian', h: 10, conf: 'documented' },
  { name: 'Porcellino', place: 'Mercato Nuovo', at: [-71.1, 216.8], from: 1640, kind: 'figure', h: 2, conf: 'documented', note: 'Pietro Tacca\'s bronze boar.' },
  { name: 'Colonna della Giustizia', place: 'Piazza Santa Trinita', at: [-308.9, 195.7], from: 1565, kind: 'column', h: 15, conf: 'documented', note: 'Column from the Baths of Caracalla; Justice on top from 1581.' },
  { name: 'Colonna di San Zanobi', place: 'Piazza San Giovanni', at: [-22.4, -171.2], from: 1384, kind: 'column', h: 7, conf: 'documented' },
  { name: 'Giovanni delle Bande Nere', place: 'Piazza San Lorenzo', at: [-21.8, -354.4], from: 1850, kind: 'monument', h: 5, conf: 'documented', note: 'Bandinelli 1540; set up in the square in 1850.' },
  { name: 'Croce al Trebbio', place: 'Piazza del Trebbio', at: [-386.5, -133.1], from: 1338, kind: 'cross', h: 6, conf: 'documented' },
  { name: 'Ferdinando I', place: 'Piazza Santissima Annunziata', at: [416.4, -519.0], from: 1608, kind: 'equestrian', h: 8, conf: 'documented', note: 'Giambologna and Tacca.' },
  { name: 'Fountain of the sea monsters (east)', place: 'Piazza Santissima Annunziata', at: [441, -523.1], from: 1629, kind: 'fountain', h: 3, conf: 'documented', note: 'Pietro Tacca.' },
  { name: 'Fountain of the sea monsters (west)', place: 'Piazza Santissima Annunziata', at: [413.1, -545.8], from: 1629, kind: 'fountain', h: 3, conf: 'documented', note: 'Pietro Tacca.' },
  { name: 'Manfredo Fanti', place: 'Piazza San Marco', at: [269.8, -678.2], from: 1873, kind: 'monument', h: 6, conf: 'documented' },
  { name: 'Monument to the Fallen of Independence', place: 'Piazza dell\'Unità Italiana', at: [-391.7, -332.2], from: 1882, kind: 'obelisk', h: 12, conf: 'documented' },
  { name: 'Dante', place: 'Piazza Santa Croce', at: [582.0, 311.7], from: 1865, kind: 'monument', h: 9, conf: 'documented', note: 'Stood in the middle of the square 1865–1968, then moved beside the church steps; placeholder at today\'s spot.' },
  { name: 'Fountain of Piazza Santa Croce', place: 'Piazza Santa Croce', at: [457.4, 284.2], from: 1816, kind: 'fountain', h: 3, conf: 'inferred' },
  { name: 'Bettino Ricasoli', place: 'Piazza dell\'Indipendenza', at: [-101.8, -950.1], from: 1898, kind: 'monument', h: 6, conf: 'documented' },
  { name: 'Ubaldino Peruzzi', place: 'Piazza dell\'Indipendenza', at: [-158.2, -850.1], from: 1897, kind: 'monument', h: 6, conf: 'documented' },
  { name: 'Giuseppe Garibaldi', place: 'Piazza Garibaldi', at: [-1149.5, -178.4], from: 1890, kind: 'monument', h: 7, conf: 'documented' },
  { name: 'Colonna di San Felice', place: 'Piazza San Felice', at: [-549.3, 754.2], from: 1572, kind: 'column', h: 8, conf: 'documented' },
  { name: 'Colonna di Santa Felicita', place: 'Piazza Santa Felicita', at: [-217.4, 526.5], from: 1381, kind: 'column', h: 7, conf: 'inferred' },
  { name: 'Fontana dello Sprone', place: 'Borgo San Jacopo / Via dello Sprone', at: [-418.3, 419.2], from: 1608, kind: 'fountain', h: 3, conf: 'documented', note: 'Buontalenti.' },
  { name: 'Monument to the fallen of Mentana', place: 'Piazza Mentana', at: [219.9, 498.4], from: 1902, kind: 'monument', h: 6, conf: 'documented' },
  { name: 'Girolamo Savonarola', place: 'Piazza Savonarola', at: [911.4, -1140.6], from: 1920, kind: 'monument', h: 6, conf: 'documented', note: 'Pazzi 1882, in Palazzo Vecchio until 1920.' },
];
