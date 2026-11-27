# San Miniato al Monte: the basilica, the bell tower, the Bishops' Palace and the monastery

Model: `blender/scripts/build_miniato.py` → `web/public/models/landmarks/miniato.glb`, in absolute scene coordinates,
geometry from `pipeline/45_chiese.py` → `blender/data/chiese.json`. Register row [M31](../DATA-SOURCES.md#M31).
Library page: [/library/san-miniato/](/library/san-miniato/).

The Romanesque basilica on the hill above Piazzale Michelangelo, with the Olivetan monastery and the Bishops' Palace on its
right and the unfinished bell tower behind. The model works in the front's own frame: `a` along the front from the corner by
the Bishops' Palace, `o` inwards along the nave. The terrace, its stairs, the cemetery of the Porte Sante and the bastions of
1553 stay with the city model.

## Measured
| Item | Value | Source |
|---|---|---|
| Outlines | church (way 184781037); the bell tower and the houses at the side (ways 91660049, 91660050, 184781035, 91606488); the monastery and the Bishops' Palace have no OSM outline: a polygon traced in the frame (a −48…0, o −6…62) on the 2017 orthophoto and the DSM | [OSM](https://www.openstreetmap.org/way/184781037), orthophoto 2017 |
| Front | the OSM front 21.6 m; the church's axis 1.4 m off its middle (a 9.4): the front is centred on the axis; terrace ground 95.1 m (scene) | OSM, LiDAR 2023 DSM |
| Nave | a 2.9–15.9, o 1.5–50; eaves ≈16.5 m, ridge ≈20.3 m above the terrace | DSM sections |
| Aisles | out to a −1.1 and 19.9, ≈12–13 m | DSM |
| Apse | to o ≈55, its roof ≈14.5 m | DSM |
| Bell tower | ≈7 m square at a 27.8, o 42.6; top ≈32.7 m | DSM peak |
| Bishops' Palace | along the front, a −48…−6, o 2–12, ≈16–17 m | DSM |
| Monastery | wings ≈12–13 m round a court a −35…−8, o 14–34; the back wing (o 40–50) ≈16–17 m | DSM |

## What the model shows (from photographs)
Photographs used (credited in `docs/materials` and on the [library page](/library/san-miniato/)): the front (Elisa
Marianini, 2018), the front from the stairs (Txllxt TxllxT, 2010), the apse and the bell tower (Zairon, 2023), the apse
wall (Elisa Marianini, 2018).

- **Front:** white marble with green serpentine. Below, five round arches on half-columns with white capitals, the arches
  ringed in green, panels in green bands, three doors in the middle arches, little inlaid triangles between the arches,
  two bands over the arcade. Above, the nave's front between four pilasters: two panels with a wheel roundel and framed
  rectangles, in the middle the mosaic of Christ between the Virgin and St Minias over a small window in a pedimented
  aedicule with a diamond lattice beside it; the entablature, the pediment with a frieze of little arches, the copper
  eagle of the Arte di Calimala on its pinnacle. The aisles' sloping fronts carry a diamond lattice.
- **Body:** stone walls, small round-headed windows in the nave's upper walls and the aisles, lean-to aisle roofs.
- **Apse:** a half-cylinder of stone with three pilaster strips, two windows closed with thin marble slabs, a half-cone roof.
- **Bell tower (1523–):** pietra forte with corner pilasters, a cornice under the belfry, an arched opening a face with its
  bell, a round window in a stone ring above, the top left ragged.
- **Cloister:** arches on columns with an upper floor of windows, in the monastery's court (form *inferred*: no photograph used).
- **Bishops' Palace and monastery:** buildings massed from the DSM raster; the palace in stone.

## Phases
| Years | Part | Basis |
|---|---|---|
| 1018 | the church begun for a Benedictine abbey, on the grave of St Minias | [en.wikipedia](https://en.wikipedia.org/wiki/San_Miniato_al_Monte), Britannica |
| 1060–1207 | the building and the marble front (shown from 1207, *inferred*; a rough front before) | buffaloah.com |
| 13th century | the front's mosaic (shown from 1260, *inferred*); 1207 the inlaid floor inside | aviewoncities.com |
| from 1288 | the Arte di Calimala looks after the church: its eagle on the front | buffaloah.com |
| 1295 | the Bishops' Palace (Andrea dei Mozzi) | en.wikipedia (Palazzo dei Vescovi) |
| 1373 | the Olivetans take over the monastery (to check) | general knowledge, not checked here |
| 1443–c. 1455 | the cloister (planned 1426) | en.wikipedia |
| 1499 | the old bell tower falls (shown 1100–1499, size *inferred*) | buffaloah.com |
| 1523 | Baccio d'Agnolo's new bell tower, never finished | museionline, Reid's guides |
| 1553 | the fortress walls round the hill (city model) | general knowledge, not checked here |
| 1574 | the Bishops' Palace joins the monastery | en.wikipedia |

## Where the sources disagree
- **The bell tower:** 1523 (most guides, museionline) or 1518 (techno-science.net, mega.it).
- **The front's date:** "11th–12th century" in older accounts, "completed in the early 13th century" elsewhere; the model
  takes 1207 (the floor's date) as the end.

## Review list
- The cloister's form and the monastery's wings are not from photographs.
- The aisles' windows and the nave's upper windows are *inferred* in number.
- The front's inlay is simplified: the patterns of the lower panels and of the pediment are stand-ins.
- The old bell tower (to 1499) is a guess.
- The houses at the side of the church (OSM ways 91660049, 91660050, 184781035, 91606488) stay city records.
