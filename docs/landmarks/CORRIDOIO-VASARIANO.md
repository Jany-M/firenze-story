# Corridoio Vasariano (the Vasari Corridor)

Model v1 (`blender/scripts/build_corridoio.py` → `web/public/models/landmarks/corridoio.glb`; geometry from
`pipeline/41_corridoio.py` → `blender/data/corridoio.json`), register row [M19](../DATA-SOURCES.md#M19).
Library page: [/library/vasari-corridor/](/library/vasari-corridor/).
The stretch over the bridge is part of the [Ponte Vecchio](PONTE-VECCHIO.md) model; the stretch inside the Uffizi is the
Uffizi's own top floor ([UFFIZI.md](UFFIZI.md)). This model holds the rest, and Torre dei Mannelli.

## Route and measurements
| Stretch | Length | How it is placed | Source |
|---|---|---|---|
| Overpass on Via della Ninna (Uffizi ↔ Palazzo Vecchio) | ≈8 m span, 6.8 m wide | OSM outline; arch springing ≈8 m above the street, windows at the Uffizi's second floor (*inferred* from photographs) | [OSM relation 21744601](https://www.openstreetmap.org/relation/21744601) |
| Head at the Uffizi | the loggia ends in a block 7.5 m long, as wide as the corridor plus the street beside it, reaching the Uffizi's south-west front (OSM way 477279033, (−32.0, 418.0) → (1.3, 435.5)): a great arch over the street on its east and west faces, a small arched door at the end of the river-side portico, two barred windows a face, string course, cornice, hipped roof | photograph by Dimitris Kamaras (2016, from the Uffizi), OSM |
| Uffizi west end on the Lungarno (where the corridor leaves the gallery for the loggia) | wedge ≈33 × 25 m, roof ≈38 m | the part of OSM way 477279033 west of the Uffizi model's wings; LiDAR roof | [OSM way 477279033](https://www.openstreetmap.org/way/477279033), LiDAR 2023 |
| Loggia on the Lungarno degli Archibusieri | ≈96 m, 19 bays of ≈4.9 m | OSM outline; roof ≈22.6 m on the DSM; centre line 0.6 m towards the river, where the DSM ridge is | OSM, LiDAR 2023 |
| Corner over the bridge head (to the bridge corridor) | ≈4 m | meets the corridor of the Ponte Vecchio model | – |
| Oltrarno, bridge → Boboli | ≈289 m | OSM strip (relations 21744599/600), centre line every 2 m; eave from the lower envelope of the DSM where the corridor stands free (18.7–24.6 m, rising to Boboli), bridged by interpolation where taller houses stand over it; ground from the app's terrain | [OSM relation 21744599](https://www.openstreetmap.org/relation/21744599), LiDAR 2023 |

The whole corridor is about 750–760 m long from Palazzo Vecchio to Palazzo Pitti
([it.wikipedia](https://it.wikipedia.org/wiki/Corridoio_Vasariano): ≈760 m; many guides say 750 m, some "about 1 km").

## What the model shows (from photographs)
Photographs used (all credited in `docs/materials` and on the [library page](/library/vasari-corridor/)): the Lungarno seen
from the river and from a corridor window (Sailko, 2010–13), the loggia still walled up before 1890, the overpass on Via
della Ninna (Francesco Bini; Ray in Manila), Torre dei Mannelli (Yair Haklai, 2019), the stretch over Via de' Bardi (Francesco
Bini, 2021), Santa Felicita and the Arco dei Rossi (Sailko 2006–08; Francesco Bini 2021), the Boboli stretch (Sailko, 2007),
Via de' Guicciardini before 1944 (1890s), Buonsignori's map of 1584.

- **The gallery:** plastered walls on a brick string course, a plastered cornice, a tiled roof with a ridge; pietra serena
  window frames. On the Lungarno rectangular windows face the river and round oculi the city, as
  [it.wikipedia](https://it.wikipedia.org/wiki/Corridoio_Vasariano) describes ("oculi towards the city, rectangular towards
  the river"); in Oltrarno rectangular windows on the street side and oculi on the other.
- **Lungarno degli Archibusieri:** a loggia of round arches on plain piers on both faces (a walkway under the corridor), a
  pietra serena archivolt on each arch, the river face down to the embankment in stone.
- **Via della Ninna:** a round arch across the street, three framed windows on each face, an entablature and a low roof.
- **Torre dei Mannelli:** the corridor runs round the tower's street side on stepped pietra serena corbels (*beccatelli*) with
  small arches between them; the tower in rough stone with a few arched openings and a later top floor under deep eaves.
- **Via de' Bardi:** the corridor on two arches over the street openings.
- **Santa Felicita:** the Arco dei Rossi over the lane, then Vasari's portico of four arches on pietra serena columns with the
  corridor storey on top (five windows towards the piazza); the church front closes it behind.
- **Boboli:** the corridor on a wall, carried over its garden face on a row of corbels, small square windows and oculi.
- Between these stretches the corridor runs over, behind and through houses that are already in the city model (from the
  Via de' Bardi arch through the block to Santa Felicita, and on to the gardens). There it is drawn as the gallery alone, and
  the city houses are cut open above its floor inside its footprint, so the whole route shows: the model writes its centre
  line, width and floor to `web/public/models/landmarks/corridoio_path.json`, and `setCorridorCut()` in `web/src/scene/city.ts`
  turns that into a floor-height raster the city material tests (from 1565). The cut keeps 12 cm inside the corridor's
  walls, on a 25 cm raster, so its edge hides behind them instead of leaving a jagged gap in the houses' roofs.

## Phases
| Years | Part | Basis |
|---|---|---|
| 1249– | Torre dei Mannelli | first recorded as "nova" on 16 August 1249 – [it.wikipedia](https://it.wikipedia.org/wiki/Torre_dei_Mannelli) (the city record had it from 1955: fixed by the model) |
| 1565– | the corridor (all stretches) | begun 12 March, main works finished 17 December 1565, window frames December 1568 – [it.wikipedia](https://it.wikipedia.org/wiki/Corridoio_Vasariano) |
| 1572–1885 | Lungarno loggia closed into shops, rooms overhanging the river on struts | shops by 1572; the 1864 flood damaged the overhangs, mostly demolished 1884–85 – it.wikipedia; a photograph shows the arches still walled up before 1890 |
| 1565 – 4 Aug 1944 | the Via de' Bardi stretch, arch on the street 8 m (*inferred*) | the German mines of 3–4 August 1944 – [it.wikipedia](https://it.wikipedia.org/wiki/Torre_dei_Mannelli) (the Palazzetto Mannelli at the head of Via de' Bardi was lost) |
| 1950– | the Via de' Bardi stretch rebuilt, the arch 4 m wider and flatter | reopened 1950, arch widened by 4 m for traffic; cracks consolidated 1971 – it.wikipedia |

Not shown as separate phases: the window into Santa Felicita (1589, inside), the church's rebuilding by Ruggieri
(1736–39, the city record), the 1993 Georgofili bomb (damage inside the Uffizi stretch), the closures (1944–73, 2016–2024).

## Where the sources disagree
- **The three big windows over Ponte Vecchio.** A widespread story says Mussolini had them opened for Hitler's visit in May
  1938. [it.wikipedia](https://it.wikipedia.org/wiki/Corridoio_Vasariano) calls this a legend: the central opening goes
  back to a terrace of 1860 (for Vittorio Emanuele II to watch the San Giovanni fires); in 1938 the side openings were only
  plastered, and they were reopened after the war. The [Ponte Vecchio](PONTE-VECCHIO.md) page used "1939"; the model of
  the bridge does not draw them yet.
- **Damage in 1944.** it.wikipedia says the corridor was "gravely damaged" and partly rebuilt but names only the Via de'
  Bardi overpass; other accounts stress that the corridor stayed passable during the battle (the only crossing, as in
  Rossellini's *Paisà*). The model removes only the Via de' Bardi stretch from 4 August 1944 to 1950.
- **Reopening.** After the war: April 1973 (it.wikipedia) or 1974 (en.wikipedia, with the self-portrait collection).
  Most recently: 21 December 2024 after the works begun in 2016 ([Italia.it](https://www.italia.it/it/toscana/firenze/corridoio-vasariano)).
- **Length:** ≈760 m (it.wikipedia), 750 m (most guides), "about 1 km" (Visit Florence).

## Sources
- Photographs of the corridor after the 2024 reopening (no free licence stated, so linked rather than shown): [FirenzeToday](https://www.firenzetoday.it/attualita/corridoio-vasariano-riapertura-tutti.html), [Finestre sull'Arte](https://www.finestresullarte.info/en/museums/florence-vasari-corridor-reopens-accessible-to-all-for-the-first-time)
- Wikipedia (it): [Corridoio Vasariano](https://it.wikipedia.org/wiki/Corridoio_Vasariano) – dates, route, materials, 1572 shops, 1864 flood, 1860 terrace, Via de' Bardi 1950/1971, reopening 2024
- Wikipedia (it): [Torre dei Mannelli](https://it.wikipedia.org/wiki/Torre_dei_Mannelli) – 1249, the beccatelli, the 1944 mines, Nello Baroni's restoration 1944–46
- Wikipedia (en): [Vasari Corridor](https://en.wikipedia.org/wiki/Vasari_Corridor) – route, reopening 1974
- Wikipedia (en): [Santa Felicita](https://en.wikipedia.org/wiki/Santa_Felicita,_Florence) – Ruggieri's church 1736–39, the corridor across the front
- Gallerie degli Uffizi: [Corridoio Vasariano – storia](https://www.uffizi.it/corridoio-vasariano/storia)
- F. Funis, *Il Corridoio Vasariano. Una strada sopra la città* (Sillabe / Gallerie degli Uffizi, 2018) – [sample](https://shop.uffizi.it/wp-content/uploads/2022/04/9788833400563-corridoioVASARIANO_assaggio.pdf)
- A. Rossano, [*Continuità fragile: le ricostruzioni novecentesche del Corridoio Vasariano*](https://oaj.fupress.net/index.php/ra/article/view/19086), Restauro Archeologico 2025
- Brown University, Florentine gazetteer: [square 66](https://cds.library.brown.edu/projects/florentine_gazetteer/map_page.php?p=66) – the corridor across Santa Felicita 1565, the window 1589
- OpenStreetMap relations [21744598](https://www.openstreetmap.org/relation/21744598)–[21744601](https://www.openstreetmap.org/relation/21744601); LiDAR 2023 ([S03](../DATA-SOURCES.md#S03))

## Review list
- Places along the run are read off the DSM profile and photographs: the two Via de' Bardi arches, the Arco dei Rossi and the
  portico (s ≈ 124–152 m from the bridge) are *inferred*; the 1565 arch on Via de' Bardi (8 m) is the 1950 width minus 4 m.
- The Lungarno loggia has 19 equal bays; the real arches and the corner over the bridge head may differ.
- The corridor inside the Uffizi and its stretch over San Pier Scheraggio are not drawn apart from the Uffizi model.
- Before 1565 the Lungarno site is left empty (the houses there are not reconstructed).
- The end at Boboli stops where OSM stops, by the Grotta del Buontalenti, against the north rondò; the passage inside the rondò into Palazzo Pitti is not drawn.
- Round the corridor near Piazza Pitti the city houses' roofs (LiDAR roof planes with overhangs) have stepped edges and the
  Palazzo Guicciardini garden shows as paving: city-model limits, listed in the plan.
- Torre dei Mannelli: size (7 m square) and openings are simplified.
- The head block at the Uffizi follows one photograph from above; the arch's width is set by the street width in OSM (≈3 m), narrower than it looks in the photograph – check the Uffizi front line there.
- The Uffizi's west end on the Lungarno is a plain block (windows on a regular grid, ground-floor arches *inferred*); check against photographs.
