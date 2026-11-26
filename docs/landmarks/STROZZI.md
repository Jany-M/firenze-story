# Palazzo Strozzi

Model: `blender/scripts/build_strozzi.py` → `web/public/models/landmarks/strozzi.glb`, in absolute scene coordinates,
geometry from `pipeline/43_centro.py` → `blender/data/centro.json`. Register row [M22](../DATA-SOURCES.md#M22).
Library page: [/library/palazzo-strozzi/](/library/palazzo-strozzi/).

## Measured
| Item | Value | Source |
|---|---|---|
| Outline | ≈57 × 44 m, the courtyard (≈15 × 8.5 m in the OSM ring) in the middle | [OSM relation 2951949](https://www.openstreetmap.org/relation/2951949) |
| Street level | 7.6–8.1 m (scene), the floor set at the highest point | app terrain |
| Top of the cornice | ≈33 m above the street; roof ≈41 m (scene) | LiDAR 2023 DSM (median 40.0, 90th percentile 41.5) |
| Storeys | ground floor to 12.4 m, piano nobile to 21.2 m, second floor to 29.6 m, cornice 3.6 m – *inferred* from photographs and the DSM | – |
| Bays | 13 on the long fronts (Via Strozzi, the south side), 9 on the short ones (Piazza Strozzi, Via Tornabuoni) – *inferred* | photographs |

## What the model shows (from photographs)
Photographs used (credited in `docs/materials` and on the [library page](/library/palazzo-strozzi/)): the north and west
fronts (MenkinAlRire, 2021), a 19th-century view of the front (Rijksmuseum, c. 1875–1900), the courtyard (Sailko, 2012),
a Caparra lantern (Sailko, 2007), the interrupted cornice on the south side (Sailko, 2007).

- **Fronts:** rustication in pietra forte, boldest on the ground floor and flatter on each floor above; small barred
  square windows high up on the ground floor, iron rings for horses; a round-arched portal in the middle of the three street
  fronts; string courses with dentils; two orders of bifore under voussoir arches with a small tondo between the lights.
- **Cornice:** Cronaca's great cornice on modillions on the north and east fronts and on half of the west front; the
  other half from 1938.
- **South side (Vicolo Strozzi):** left unfinished in 1538 – rough masonry, a few openings, no cornice – until the
  1938–40 restoration, which finished it like the other fronts (rustication and bifore, no portal, no bench). The great
  cornice turns the two corners and stops after a couple of metres; only its dentils and egg-and-dart frieze run on as a
  plain eave with a gutter, as in Sailko's photograph of the interrupted cornice (2007).
- **Ironwork:** Caparra's lanterns at the corners of the piano nobile.
- **Courtyard:** arches on pietra serena columns, round-headed windows on the first floor and rectangular ones above.
- **Stone bench** (*panca di via*) along the three fronts.

## Phases
| Years | Part | Basis |
|---|---|---|
| before 1489 | the Strozzi houses on the lot (the city data's shells) | [it.wikipedia](https://it.wikipedia.org/wiki/Palazzo_Strozzi): Filippo Strozzi bought and pulled down the houses from 1466 |
| 1489 | ground floor (foundation stone 6 August 1489) | it.wikipedia |
| 1495 | piano nobile – *inferred* (between the start and the cornice) | – |
| 1491–98 | Caparra's ironwork (shown from 1498) | it.wikipedia |
| 1502 | second floor and Cronaca's cornice | it.wikipedia |
| 1503 | the courtyard | it.wikipedia |
| 1538 | works stop: south front and half the Via Tornabuoni cornice unfinished | it.wikipedia |
| 1863–65 | the stone bench (Giuseppe Poggi) | it.wikipedia |
| 1938–40 | the Via Tornabuoni cornice completed by copying the other half, and the side on the lane finished (Ugo Giovannozzi) | it.wikipedia ("completò arbitrariamente il lato sul vicolo") |

## Where the sources disagree
- **Who designed it.** Vasari names Benedetto da Maiano; it.wikipedia thinks he probably never directed the works and
  credits Giuliano da Sangallo's wooden model (1489–90) for the first floor and Cronaca for everything from 1490 to 1504.
  The model follows the dates, not the attribution.
- **The Via Tornabuoni cornice.** it.wikipedia says work on that side resumed in 1533 and was finished in 1534–35, and also
  that half the cornice there was still missing in 1538 and was only completed in 1938–40. The model shows half the
  cornice from 1502 and the other half from 1938.
- **The storeys.** Sources speak of "three floors"; with the loggia on top some count four. The model has three storeys under
  the cornice.

## Review list
- The ground-floor windows, the portals and the bifore are generic; check bay by bay against photographs (the actual bay
  counts and the spacing of the corner bays).
- The rings, torch holders and the full set of Caparra lanterns are reduced to the corner lanterns and a few rings.
- The courtyard's loggia on the top floor and the details of its columns are simplified.
- The roof is a simple ring of pitched roofs; the LiDAR shows the 20th-century roof structures.
- The piano nobile date (1495) is inferred.
- The south side's 1938 finish is drawn like the other fronts; how far the restoration actually copied them (window count,
  rustication) is to check against photographs of Vicolo Strozzi, and so is the length of the cornice's returns (2.4 m).
