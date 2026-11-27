# Piazzale Michelangelo, the Loggia and the Rampe del Poggi

Model: `blender/scripts/build_piazzale.py` → `web/public/models/landmarks/piazzale.glb`, in absolute scene coordinates.
Register row [M41](../DATA-SOURCES.md#M41). Library page: [/library/piazzale/](/library/piazzale/).

Giuseppe Poggi's terrace over the city, built when Florence was the capital of Italy, with the monument to Michelangelo,
the Loggia above it and the Rampe – ramps, grottoes and fountains – climbing to it from the tower of San Niccolò.

## Measured
| Item | Value | Source |
|---|---|---|
| Terrace | 63–64 m (scene); its north wall 7.5 m (west) to 9 m (east) high, line from (745, 927) to (895, 957.5) with a step at x 845 | LiDAR 2023 DTM, sampled every 3–5 m (`_dev/tmp/piazzale_probe*.py`); [OSM way 233265215](https://www.openstreetmap.org/way/233265215) |
| Monument | at (818.5, 976.5) on a platform ≈ 12 m across, 1.1 m high; the statue thin in the scan (top caught at 71.7) | DSM, 1 m grid |
| Loggia | x 790..814, z 1069..1083, 9–10 m over its ground; the terrace wall before it at z ≈ 1050 | DSM |
| Rampe | levels at 8.6 (Piazza Poggi) and 13.8, the bends of Viale Poggi at 21.3 and 30.3, 34–39 above; walls at z ≈ 808, 829, 853, 869 | DTM; the Comune's carriageway and pedestrian polygons |

## What the model shows
- **The terrace's north wall** in rusticated pietra forte with a balustrade and lamp posts along it.
- **The monument to Michelangelo**: three marble steps ringed by posts and chains, the lower pedestal with red marble
  panels and the arms in bronze, the four bronze allegories of the Medici Chapel (Day, Night, Dawn, Dusk) reclining at its
  corners, the upper pedestal with the inscriptions, and the bronze David looking towards the hills (figures simplified).
- **The Loggia**: an arcade of three round arches between paired columns, closed end bays, a balustraded roof terrace, on a
  podium above the terrace wall with its inscription.
- **The Rampe**: retaining walls in courses of pietra forte with balustrades; the lower fountains behind the tower, the
  first level's fountain, the great grotto of three arches faced with spugne with its cascades and basin over the bend of
  Viale Poggi, and the upper fountain in its recess.
- The ramps and the Viale themselves are the terrain and the Comune's surveyed roads and paths.

## Phases
| Years | Part | Basis |
|---|---|---|
| 1869 → | the terrace | Wikipedia, [italia.it](https://www.italia.it/en/tuscany/florence/piazzale-michelangelo) ("built by Poggi in 1869"); [visittuscany.com](https://www.visittuscany.com/en/attractions/piazzale-michelangelo) has works from 1873, opened two years later – the model follows 1869 |
| 1873 → | the monument: Clemente Papi's bronze David set up on 25 June 1873, drawn up the hill by nine pairs of oxen | [michelangelobuonarrotietornato.com](https://michelangelobuonarrotietornato.com/2025/06/25/25-giugno-1873-linaugurazione-del-david-in-bronzo-del-papi-di-piazzale-michelangelo) |
| 1873 → | the Loggia, meant as a museum of Michelangelo's works, a café-restaurant from 1876 – building date *inferred* | visittuscany.com; [regione.toscana.it](https://www.regione.toscana.it/-/viale-dei-colli) |
| 1876 → | the Rampe, 1872–76 (visittuscany: 1871–76); their fountains dry for most of the 20th century, running again since 2019 | [gonews.it](https://www.gonews.it/?p=955744), [panorama.it](https://www.panorama.it/lifestyle/firenze-rampe-poggi-splendore-perduto) |

The city data dated the Loggia's building 1955 (record 3996); the model takes its place from 1873.
The Giardino delle Rose (1865) below the terrace is drawn by the ground: lawns and paths, no paving.
