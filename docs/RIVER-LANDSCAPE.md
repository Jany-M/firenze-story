# River and landscape

Built by `pipeline/08_wide_area.py` (downloads) and `pipeline/21_build_env.py`; drawn by `web/src/scene/environment.ts`;
river life in `web/src/sim/river.ts` (table `RIVER_LIFE`). Confidence tags as in docs/DATA-SOURCES.md.

## 1. Terrain and land cover
| Layer | Extent / resolution | Source | Notes |
|---|---|---|---|
| Core terrain | 3.6 × 3.6 km, 4 m | LiDAR 2023 DTM (Comune di Firenze) | riverbed carved 1.6 m under the water surface |
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
interpolated axis level. The hulls are open, so they have floorboards a little above the waterline (otherwise the
river surface shows inside the boat and it looks swamped); crews stand on them. Figures on the bank are set at the
edge of the *visible* water (where the surface is above the ground), and slide along the bank off any building of the
year (the San Niccolò mills, the walls).
 (`RIVER_LIFE`)
| Activity | Where | When | Source |
|---|---|---|---|
| Cargo boats (*navicelli*, sail + tow rope) | up to the old city port | -30 – 1300 | Comune 2019; meer.com |
| | to the port below the Santa Rosa weir (Ognissanti / Pignone) | 1300 – 1880 (end *conjectural*) | Comune 2019 |
| Renaioli (sand diggers) with flat boats and sand heaps on the *renai* | between the two weirs | 1700 – 1960 (documented 1829, 1846, 1847; active until the mid-20th c.) | Comune 2019; La Nazione |
| Fishermen on the banks | everywhere: most seated on a stone with a rod, some standing; the rod sways and is lifted every ~25 s (a bite or a new cast) | all periods | Comune 2019 (poses *inferred*) |
| Fishermen wading knee-deep near the bank | two, anywhere | until 1900 (nobody stands in the river in modern times) | *inferred* |
| Fishing boats | between the weirs only until 1586 (ban), outside them always; the fisherman stands on the floorboards of his own boat | – | Comune 2019 |
| Moored cargo boats at a landing stage, unloading (one man aboard, one on the stage, sails furled) | the city port between the Ponte Vecchio and the Grazie, north bank (spot *inferred*) | -30 – 1300 | meer.com ("a port between the Carraia and San Niccolò until the 13th century") |
| | the port of the Pignone, south bank by today's Piazza Paolo Uccello (rebuilt as the Leopoldine port) | 1300 – 1910 | meer.com (used until the early 20th c.); Comune 2019 (the Pignone's boatbuilders); gonews.it 2021 (the Leopoldine port found under Piazza Paolo Uccello) |
| Washerwomen kneeling at the water's edge, a stone slab into the water, basket and linen spread on the bank | four stretches of open bank: the Renai, above San Niccolò, below Santa Rosa (spots *inferred*) | 1000 – 1900 | *inferred* (common practice before piped water and the public *lavatoi*) |
| Clay diggers (*fornaciai*): clay heaped on the bank, bricks drying in rows, a moulding table | two stretches below the city | 1300 – 1900 | Agostini 2012 (river crafts below Florence: navicellai, renaioli, fornaciai…); spots *inferred* |
| Landing stages (*scali*), each with two boats tied up | Porticciola (Piazza d'Arno / delle Travi) and Renai, between Carraia and Santa Trinita | from 1830 | Comune 2019 |
| | gora of the Renai mills, Lungarno Serristori | from 1846 | Comune 2019 |
| Ducks, herons, swallows | river | all periods | – |
| Deer | countryside 1.4–5 km out | before 1200 | *conjectural* |
| Iron Age (Villanovan) huts, palisade | north of the ford, towards Piazza della Signoria | -900 – -80 | Iron Age finds in the area (Piazza della Signoria excavations 1974–89); layout *conjectural* |

Not yet: mills and fulling mills on the weirs, the river festivals (San Giovanni fireworks from the Carraia, boat race
of Sant'Iacopo), public baths (Vagaloggia, Molina dei Renai), floods (1333, 1557, 1844, 1966).

## 4. Lighter when far (2026-11-28)
- People are made only where the camera looks and only when it is low: from 340 m up no people are drawn or moved; below
  that, walkers fill a circle round the view that grows with height, and agents not seen are reused elsewhere (no fixed pool).
- Herons and other small river life go from 450 m up, boats from 1400 m.
- The navicelli's crews stand along the hull's own heading (they had been set out along the x axis and some stood in the water).
- The river banks are earth and grass (see MATERIALS, "Ground that is not paved").

## 5. Who can get to the bank (2026-11-28)
- Fishermen, washerwomen and clay diggers only go where they can get to: a spot is reachable if a street lies within 30 m at
  about its level (not 6 m up a lungarno wall), or if no street is near at all (the fields and gravel banks outside the
  town). Otherwise another place is tried, or nobody is put there.
- The clay diggers work: one digs at the bank (bent over the spade, then straightening with the load), two carry clay to
  the drying rows and come back, pausing to load and unload. Their heaps and brick rows, and the washerwomen's linen and
  slab, rest on the ground and tilt with its slope; the washerwomen kneel with knees and toes on the ground.
- Since 2026-11-27 every bank worker has a round of tasks, looped (`web/src/sim/river.ts`, steps of poses or walks): the
  digger cuts clay at the bank's face and takes it to the heap; the moulder fetches clay from the heap and works it at a table;
  the carrier takes the moulded bricks to the drying rows; each walks with the load held in both arms. The washerwomen,
  kneeling, scrub on the slab (two strokes), wring and beat the linen, each at her own point of the round. The order of the
  work is that of a brickfield, *inferred* for the Arno's banks.
- Since 2026-11-28 the washerwomen move smoothly: their round mixes poses by weight (`people.setMix`) – each phase swings
  between two poses on a cosine and blends from the last over 0.7 s – and the linen is in their hands: a piece taken from
  the basket at her side and put back (`garment_hang`), rinsed and swished in the current, laid on the slab and scrubbed
  (`garment_flat`), wrung into a rope and beaten on the stone (`garment_twist`), placed each frame between or under her
  hands. A hand cart with a basket and folded linen stands on the bank behind them (`handcart`), the brickmakers' tip cart
  with clay and bricks by their heap (`claycart`); the clay heap is closed at the top. Assets in `build_assets.py`
  (*inferred* forms).
- The small boats ride higher: only a few centimetres of hull in the water (barchetti), the navicelli 0.2 m.
- Squares hold a little fewer people (about one per 27 m², at most 52).

## Sources
- Comune di Firenze, *Una città e il suo fiume: la vita lungo l'Arno* (2019), cultura.comune.fi.it
- Museo Galileo, Scientific itineraries: San Niccolò weir, Santa Rosa weir (brunelleschi.imss.fi.it)
- La Toscana di Leonardo: "L'Arno dalla pescaia della Giustizia e di San Niccolò alla pescaia di Santa Rosa"
- Opera di Santa Maria del Fiore, archive database (mills of Ognissanti 1417, of San Niccolò 1423)
- meer.com, "Firenze e l'Arno" (old river port, renaioli)
- La Nazione (renaioli in the first half of the 20th century)
- gonews.it (2021), "Quando Firenze aveva il porto sull'Arno" – the Leopoldine port found under Piazza Paolo Uccello
- I. Agostini, *Un territorio manufatto … il caso dell'Arno a valle di Firenze*, Polistampa 2012 (abstract, cris.unibo.it)
- E. Butelli, S. Gjyzelaj, "Porti, navi e altri elementi di approdo e commercio lungo l'Arno al tempo di Leonardo", FUP 2023
- hmdb.org, Piazza della Signoria excavations marker; Wikipedia "Florentia (Roman city)"
- Copernicus DEM GLO-30 (© DLR / Airbus, ESA); Sentinel-2 cloudless 2016 by EOX (CC BY 4.0, contains modified Copernicus Sentinel data 2016); OpenStreetMap (ODbL)

### Ponte San Niccolò and Ponte alla Vittoria (in the study area since 2026-11-23)
| Bridge | Phases |
|---|---|
| Ponte San Niccolò | suspension bridge "San Ferdinando" (Seguin) 1837–1844 (flood) · rebuilt 1853–1890 · three-span metal bridge 1890–1944 · Morandi single arch 1949 |
| Ponte alla Vittoria | suspension bridge "San Leopoldo" 1835–1931 (four lion pillars) · Ponte alla Vittoria 1931–1944 · rebuilt 1946 (142 m × 15.5 m) |
Sources: Museo Galileo (San Niccolò weir page), structurae.net, risorgimentofirenze.it; span counts of the 1931 and 1946
Vittoria bridges *inferred*. San Niccolò 1949: main span 87.5 m, 132 m long, 17.5 m wide (structurae; it gives works 1955–60,
most Florentine sources 1949 – kept 1949, to verify on dated photos); the 1890 bridge is drawn as iron girders on masonry piers.
Both were mined on 3–4 Aug 1944 and are blown up in the Night of the Bridges scene. Ponte da Verrazzano (1969) is still
outside (≈ 2.1 km east of the origin).
