# River and landscape

Built by `pipeline/08_wide_area.py` (downloads) and `pipeline/21_build_env.py`; drawn by `web/src/scene/environment.ts`;
river life in `web/src/sim/river.ts` (table `RIVER_LIFE`). Confidence tags as in docs/DATA-SOURCES.md.

## 1. Terrain and land cover
| Layer | Extent / resolution | Source | Notes |
|---|---|---|---|
| Core terrain | 2 × 2 km, 4 m | LiDAR 2023 DTM (Comune di Firenze) | riverbed carved 1.6 m under the water surface |
| Wide terrain | 12 × 12 km, 40 m | Copernicus GLO-30 (30 m) | buildings and woods stripped by a 150 m morphological opening; aligned to the LiDAR datum on the river (offset +0.51 m); Fiesole, Arcetri, Bellosguardo hills |
| Land texture | 12 × 12 km, ~6 m | Sentinel-2 cloudless 2016 (EOX, CC BY 4.0) | today's colours; woods where it is dark green |
| Ground by era | – | dated city (urban raster: first year anything stood in each 8 m cell) | meadow and fields → beaten earth → stone paving (1230s) → today's surfaces (1880–1960); built-up land outside the core appears 1900–2000 |
| Vegetation | 64,874 trees | Comune trees (2,217, from 1880) + historic scatter in the core (8,732, removed when the ground is built on) + wide ring (53,925, woods/olive groves where green today; trees on today's built-up land vanish 1880–1960) | 4 species shapes; scatter is *conjectural* |

## 2. The Arno
- Surface: OSM water polygons over the whole 12 km (Arno + 37 ponds), split at the weirs into pools; each pool sits
  at its own level, stepping down at every weir going downstream: ~41.5 m a.s.l. through the city, ~2 m drop at
  San Niccolò, ~4–5 m at Santa Rosa. Levels: LiDAR inside the core, Copernicus (water-flattened) outside.
- Flowing ripples, Fresnel sky reflection, green-brown silty colour.

### Weirs (*pescaie*)
| Weir | Position | Shown from | Conf. | Source |
|---|---|---|---|---|
| San Niccolò ("della Giustizia") | upstream, by the San Niccolò tower | 1300 | inferred | Museo Galileo itineraries; mills of San Niccolò documented 1423 (Opera del Duomo archive); Leonardo, Codex Leicester |
| Santa Rosa (d'Ognissanti) | downstream, by the Cascine | 1300 | inferred | Museo Galileo; mills of Ognissanti documented 1417 |
| Isolotto, Rovezzano, Girone | outer pools | 1900 | conjectural | OSM geometry only, dates unknown |

The two city weirs fed the mills and fulling mills (*gualchiere*) and closed the river to enemy boats.
Until the 13th century a river port lay between today's Carraia and San Niccolò bridges.

### Bridges (dated phases, `NAMED` in 21_build_env.py; shapes in `web/src/scene/bridges.ts`)
| Bridge | Phases |
|---|---|
| Ponte Vecchio | Roman wooden bridge (-30 – 1177, *conjectural*) · stone 1177–1333 · rebuilt 1345 (landmark model with shops and corridor, docs/landmarks/PONTE-VECCHIO.md) |
| Carraia | 1220–1333 · 1337–1557 · 1559–1944 · 1952 |
| Santa Trinita | 1252–1333 · 1346–1557 · 1569–1944 (Ammannati) · 1958 |
| Rubaconte / alle Grazie | 1237–1944 (survived 1333) · 1957 |
| San Ferdinando / San Niccolò | iron suspension bridge 1837–1944 · 1949 |
| Vespucci | 1957 |
Rebuild years after 1333 and 1557 are *inferred*. Temporary 1944–46 bridges are not modelled yet.

Each phase is built in the browser from a small spec (number of arches, arch shape round / segmental / elliptical,
deck width, pier width, rise): the deck sits at the level of the lungarni at both ends (at least 7 m above the pool),
piers get pointed cutwaters, parapets run along both sides. Ponte Vecchio 1345: 3 segmental arches; Santa Trinita 1569:
Ammannati's 3 flattened arches (rebuilt as they were in 1958); Grazie 1237–1944: 9 small arches with chapels and houses
on the piers; Roman bridge: timber trestle; San Niccolò 1837: suspension bridge on two pylons. Arch counts and widths
come from historic views and maps (H01, H16) and are *inferred* for the medieval phases.

### Crossings where no bridge stood
Before Florentia the Arno is **forded** near today's Ponte Vecchio, where the Bologna–Fiesole–Impruneta route crossed
the river (A07, *inferred*); in Live mode people wade across. No ferries are shown while a bridge was down
(1333–45 Ponte Vecchio, 1557–69 Santa Trinita, 1557–59 Carraia): an earlier version had rope ferries there, but no source
places them, so they were removed (2026-11-23). Temporary wooden bridges and the 1944–46 Bailey bridges will be added
only from documents (to research).

## 3. Life on the river
Boats sit on the drawn water surface (sampled from the water mesh, which steps down at every weir), not on the
interpolated axis level.
 (`RIVER_LIFE`)
| Activity | Where | When | Source |
|---|---|---|---|
| Cargo boats (*navicelli*, sail + tow rope) | up to the old city port | -30 – 1300 | Comune 2019; meer.com |
| | to the port below the Santa Rosa weir (Ognissanti / Pignone) | 1300 – 1880 (end *conjectural*) | Comune 2019 |
| Renaioli (sand diggers) with flat boats and sand heaps on the *renai* | between the two weirs | 1700 – 1960 (documented 1829, 1846, 1847; active until the mid-20th c.) | Comune 2019; La Nazione |
| Fishermen on the banks | everywhere | all periods | Comune 2019 |
| Fishing boats | between the weirs only until 1586 (ban), outside them always | – | Comune 2019 |
| Landing stages (*scali*) | Porticciola (Piazza d'Arno / delle Travi) and Renai, between Carraia and Santa Trinita | from 1830 | Comune 2019 |
| | gora of the Renai mills, Lungarno Serristori | from 1846 | Comune 2019 |
| Ducks, herons, swallows | river | all periods | – |
| Deer | countryside 1.4–5 km out | before 1200 | *conjectural* |
| Iron Age (Villanovan) huts, palisade | north of the ford, towards Piazza della Signoria | -900 – -80 | Iron Age finds in the area (Piazza della Signoria excavations 1974–89); layout *conjectural* |

Not yet: mills and fulling mills on the weirs, the river festivals (San Giovanni fireworks from the Carraia, boat race
of Sant'Iacopo), public baths (Vagaloggia, Molina dei Renai), floods (1333, 1557, 1844, 1966).

## Sources
- Comune di Firenze, *Una città e il suo fiume: la vita lungo l'Arno* (2019), cultura.comune.fi.it
- Museo Galileo, Scientific itineraries: San Niccolò weir, Santa Rosa weir (brunelleschi.imss.fi.it)
- La Toscana di Leonardo: "L'Arno dalla pescaia della Giustizia e di San Niccolò alla pescaia di Santa Rosa"
- Opera di Santa Maria del Fiore, archive database (mills of Ognissanti 1417, of San Niccolò 1423)
- meer.com, "Firenze e l'Arno" (old river port, renaioli)
- La Nazione (renaioli in the first half of the 20th century)
- hmdb.org, Piazza della Signoria excavations marker; Wikipedia "Florentia (Roman city)"
- Copernicus DEM GLO-30 (© DLR / Airbus, ESA); Sentinel-2 cloudless 2016 by EOX (CC BY 4.0, contains modified Copernicus Sentinel data 2016); OpenStreetMap (ODbL)
