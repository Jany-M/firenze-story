# Palazzo degli Uffizi

Model v1 (`blender/scripts/build_uffizi.py` → `web/public/models/landmarks/uffizi.glb`), register row [M16](../DATA-SOURCES.md#M16).

## Measured
| Item | Value | Source |
|---|---|---|
| Piazzale | 13.8 m wide, ≈139 m long, axis 16.9° east of north | OSM way 477279033 |
| West wing | ≈21 m deep | OSM + LiDAR |
| East wing | ≈29 m deep (takes in the church of San Pier Scheraggio) | OSM + LiDAR |
| Arno wing | 12 m deep, serliana through the middle | OSM + LiDAR |
| Roofs | ≈28 m above the piazzale | LiDAR 2023 DSM |

## What the model shows (from photographs)
The river front, redrawn from Oursana's photograph from across the Arno ([Commons](https://commons.wikimedia.org/wiki/File:Lungarno_Anna_Maria_Luisa_de%27_Medici_Uffizi.jpg),
2013, CC0), its heights scaled on the LiDAR eaves (26.2 m):
- **A pietra serena frame on pale plaster,** ±17.8 m round the piazzale's axis; plain plaster blocks with rows of windows
  beyond it, to the outer faces of the two wings.
- **Ground floor: an open loggia** through the whole Arno wing (12 m deep), with three openings on the river: Vasari's serliana
  in the middle (a round arch 6 m wide on Doric columns, flat side bays under an architrave, across the piazzale's width) and
  a big round arch each side (5 m wide, top ≈10.5 m), between piers with niches and statues (four). The loggia's back,
  behind the side arches, in shade.
- **Above:** the entablature (10.7–12 m); the piano nobile with three arched windows on balconies over the serliana and a
  pedimented window over each side arch, between pilasters; a band; the top loggia (1580) glazed in wide bays; the frame's
  corners up to the cornice; the cornice and the roof.
- **In front, on the Lungarno:** a stone balustrade instead of the brick parapet (lungarni model).

Storeys (*inferred* from the DSM and the elevation described by uffizi.it): portico to 7.6 m, mezzanine to 11.2 m, piano nobile to 18.4 m, top loggia to 25 m, cornice 26.2 m, ridge 28.5 m.

## Phases
| Years | What | Basis |
|---|---|---|
| until 1560 | houses, the Zecca (Mint) and the church of San Pier Scheraggio on the site | [it.wikipedia](https://it.wikipedia.org/wiki/Galleria_degli_Uffizi); masses *conjectural* |
| 1560 | Vasari begins for Cosimo I | [it.wikipedia](https://it.wikipedia.org/wiki/Galleria_degli_Uffizi), [uffizi.it](https://uffizi.it/en/artworks/ll-palazzo-degli-uffizi) |
| 1565 | west wing and Arno wing standing | [it.wikipedia](https://it.wikipedia.org/wiki/Galleria_degli_Uffizi) (the same page also gives 1575: **sources disagree**) |
| 1572 | east wing; the magistracies have moved in | [it.wikipedia](https://it.wikipedia.org/wiki/Galleria_degli_Uffizi) |
| 1574–80 | Buontalenti and Parigi finish: top loggia, cornice, roofs (shown from 1580) | [it.wikipedia](https://it.wikipedia.org/wiki/Galleria_degli_Uffizi) (October 1580), [en.wikipedia](https://en.wikipedia.org/wiki/Uffizi) and [historyofinformation](https://www.historyofinformation.com/detail.php?id=2661) (1581): **sources disagree** by a year |
| 1842–56 | 28 statues of famous Tuscans in the pier niches (shown from 1850, *inferred*; the page also says 1835 for the first plans) | [it.wikipedia](https://it.wikipedia.org/wiki/Galleria_degli_Uffizi) |

The Corridoio Vasariano outside the Uffizi (Via della Ninna, the Lungarno loggia, Oltrarno) is its own model since 2026-11-26: [CORRIDOIO-VASARIANO.md](CORRIDOIO-VASARIANO.md). Not modelled yet (in the plan): the Teatro Mediceo (1586, inside the east wing, no outside sign); Zanobi del Rosso's entrance (1769); the post office in the Arno wing (1866).

## Pictures
Credited pictures (courtyard, Arno front, Zocchi's 18th-century view, Callot's Teatro Mediceo, San Pier Scheraggio) are in
`docs/materials/manifest.json` with the subject `rec:Galleria degli Uffizi`: shown in the app's card and on the library page
[/library/uffizi/](/library/uffizi/).

## Review list
- Bay rhythm (niched pier, two columns, three windows) is simplified; compare with photographs of the piazzale front.
- The river front is scaled from one photograph (heights from the LiDAR); its widths (±17.8 m frame, 5 m side arches) are
  not measured on the ground. The arcade of the old landing in the river wall below the loggia is not drawn yet, and the
  river wall there is the lungarni's stone, not the plastered wall of the photograph.
- Top loggia is shown with dark openings; its arcading and glazing over time are not dated.
- Heights are measured on roofs, so the cornice and ridge levels are estimates.
- The old quarter, the Zecca and San Pier Scheraggio are plausible masses only.
