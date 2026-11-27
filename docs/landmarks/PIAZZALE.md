# Piazzale Michelangelo, the Loggia and the Rampe del Poggi

Model: `blender/scripts/build_piazzale.py` → `web/public/models/landmarks/piazzale.glb`, in absolute scene coordinates.
Register row [M41](../DATA-SOURCES.md#M41). Library page: [/library/piazzale/](/library/piazzale/).

Giuseppe Poggi's terrace over the city, built when Florence was the capital of Italy, with the monument to Michelangelo,
the Loggia above it and the Rampe – ramps, grottoes and fountains – climbing to it from the tower of San Niccolò.

## Measured
| Item | Value | Source |
|---|---|---|
| Terrace | 63–64 m (scene); its walls traced on the LiDAR (below) | LiDAR 2023 DTM; [OSM way 233265215](https://www.openstreetmap.org/way/233265215) |
| Walls | every retaining wall of the terrace, the Viale below and the Rampe followed on the 0.5 m DTM: the steepest line within 1.5–3 m of a line read off a slope map, with its top and foot 1.5–2.5 m either side (`_dev/tmp/wall_snap.py` → `blender/data/piazzale_walls.json`). City side 5.5–7.5 m high, the Iris side (east) up to 9.5 m, the west 5.8 m | LiDAR 2023 DTM, 0.5 m |
| Great staircase | 40 steps ([OSM way 233265212](https://www.openstreetmap.org/way/233265212), sett) from the terrace (63.4) down to the lower terrace by the Belvedere (57.3), at the west end facing the city: x 736.5 → 720.5, 12 m wide (z 955.5–967.5) | DTM profile; OSM |
| Monument | at (818.5, 976.5) on a platform ≈ 12 m across, 1.1 m high; the statue thin in the scan (top caught at 71.7) | DSM, 1 m grid |
| Loggia | x 790..814, z 1069..1083, 9–10 m over its ground; the terrace wall before it at z ≈ 1050 | DSM |
| Rampe | levels at 8.6 (Piazza Poggi) and 13.8, the bends of Viale Poggi at 21.3 and 30.3, 34–39 above; walls at z ≈ 808, 829, 853, 869 | DTM; the Comune's carriageway and pedestrian polygons |

## What the model shows
- **The terrace's walls all round**: the city side (with its step at x 845), the Iris garden side (east) and the west,
  in rusticated pietra forte on their measured lines, with Poggi's balustrade along every edge: a stone base, squat Doric
  cast-iron balusters and a cast-iron rail, painted the colour of pietra forte (Fonderia di Follonica, 1865–75; restored
  2017–18 – [Comune di Firenze, relazione storico-tecnica 2018](https://affidamenti.comune.fi.it/sites/affidamenti.comune.fi.it/files/profilo/documenti-di-gara/20180320/Relazione%20Storico%20Tecnica.pdf),
  [Artribune 2017](https://www.artribune.com/?p=492993)); stone dados every 6 m (*inferred* spacing).
- **The great staircase** at the west end, down to the lower terrace by the Belvedere, between parapet walls with the
  balustrade stepping down, a lamp at each corner.
- **The lamps**: cast-iron candelabra – lion-paw tripod, twisted shaft, scrolled arms, four white globes (Otrębski's
  photograph on Commons) – along the balustrades every ≈ 24 m (*inferred* spacing) and at the staircase. The same lamp in
  every year (the older heads seen in the 1890s photographs are not drawn apart).
- **The ground of the terrace and of the square before the Loggia**: gravel until 1960 (the photographs of the 1870s–1900s),
  asphalt after (photographs of the 1990s on); the date of the change is *inferred*. The ground model is lowered under it.
- **The carriageway round the south side** (Viale Galileo into Viale Michelangiolo, the Comune's carriageway polygon) is left
  to the city's streets, so it runs on unbroken past both ends of the square; the terrace's paving stops at its edge
  (`pipeline/49_piazzale.py` → `blender/data/piazzale_ground.json`).
- **The garden before the Loggia**, between the carriageway and the Loggia's terrace wall: gravel paths (the Comune's
  pedestrian polygon), sixteen lawn beds edged in stone (its holes) and the oval fountain (OSM way 1093617565) with a jet
  (its form *inferred*); photographs: Sailko on Commons, localistorici.it.
- **The two ramps of Viale Poggi** that meet the terrace on the city side, read off the LiDAR: west of the step a 6 m road
  climbs along the outside of the city-side wall from 56 m (x 770) to the terrace's level (x ≈ 810); east of it the road
  goes down again, 8–12 m wide, to 54 m (x 900). The wall and its balustrade stop where a ramp reaches the terrace's
  level; a low stone parapet on each ramp's open side (*inferred*).
- **The monument stands on the terrace**: its steps start at the terrace's level round it (63.45 m, LiDAR 8–11 m out); the
  LiDAR's hump of the platform is cut out of the ground, and the paving leaves a hole for it.
- **The containing walls below**: along Viale Poggi's bends under the terrace and on the Iris garden side, with a low stone
  parapet (*inferred*), part `viale_muri`.
- **The monument to Michelangelo**: three marble steps ringed by posts and chains, the lower pedestal with red marble
  panels and the arms in bronze, the four bronze allegories of the Medici Chapel (Day, Night, Dawn, Dusk) reclining at its
  corners, the upper pedestal with the inscriptions, and the bronze David looking towards the hills (figures simplified).
- **The Loggia**: an arcade of three round arches between paired columns, closed end bays, a balustraded roof terrace, on a
  podium above the terrace wall with its inscription.
- **The Rampe**: retaining walls in courses of pietra forte with balustrades, every one on its measured line (until
  2026-11-27 they ran on straight lines of constant z and the ground covered parts of them); the lower fountains behind the tower, the
  first level's fountain, the great grotto of three arches faced with spugne with its cascades and basin over the bend of
  Viale Poggi, and the upper fountain in its recess.
- The ramps and the Viale themselves are the terrain and the Comune's surveyed roads and paths. The terrain gives way to
  the model: in front of each wall it is cut down to the wall's foot, behind it filled to the top
  (`models/landmarks/ground_edits.json`, applied to the app's ground grid, `web/src/scene/terrainRefine.ts`).
- Basins at the OSM fountains' places (ways 463430105, 690889344).

Still open (refinement pass): the statues of the monument as real figures (now blocks); the lower terrace's brick paving
and garden beds by the Belvedere; the round fountain basin seen in the 1900s postcards on the terrace (not dated yet).

## Phases
| Years | Part | Basis |
|---|---|---|
| 1869 → | the terrace | Wikipedia, [italia.it](https://www.italia.it/en/tuscany/florence/piazzale-michelangelo) ("built by Poggi in 1869"); [visittuscany.com](https://www.visittuscany.com/en/attractions/piazzale-michelangelo) has works from 1873, opened two years later – the model follows 1869 |
| 1873 → | the monument: Clemente Papi's bronze David set up on 25 June 1873, drawn up the hill by nine pairs of oxen | [michelangelobuonarrotietornato.com](https://michelangelobuonarrotietornato.com/2025/06/25/25-giugno-1873-linaugurazione-del-david-in-bronzo-del-papi-di-piazzale-michelangelo) |
| 1873 → | the Loggia, meant as a museum of Michelangelo's works, a café-restaurant from 1876 – building date *inferred* | visittuscany.com; [regione.toscana.it](https://www.regione.toscana.it/-/viale-dei-colli) |
| 1869 → | the walls, balustrades, lamps and the great staircase (with the terrace); the Viale's containing walls | as the terrace |
| 1869 → 1960 → | gravel, then asphalt | photographs (Sommer 1890s, Detroit Publishing 1897, 1990s); change year *inferred* |
| 1876 → | the Rampe, 1872–76 (visittuscany: 1871–76); their fountains dry for most of the 20th century, running again since 2019 | [gonews.it](https://www.gonews.it/?p=955744), [panorama.it](https://www.panorama.it/lifestyle/firenze-rampe-poggi-splendore-perduto) |

The city data dated the Loggia's building 1955 (record 3996); the model takes its place from 1873.
The Giardino delle Rose (1865) below the terrace is drawn by the ground: lawns and paths, no paving.
