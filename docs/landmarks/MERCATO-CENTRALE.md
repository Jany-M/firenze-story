# Mercato Centrale (Mercato di San Lorenzo)

Model: `blender/scripts/build_mercato_centrale.py` → `web/public/models/landmarks/mercato_centrale.glb`, in absolute scene
coordinates, geometry from `pipeline/43_centro.py` → `blender/data/centro.json`. Register row [M24](../DATA-SOURCES.md#M24).
Library page: [/library/mercato-centrale/](/library/mercato-centrale/).

## Measured
| Item | Value | Source |
|---|---|---|
| Outline | 82.7 × 70.3 m, long sides on Via dell'Ariento and Via Sant'Antonino | [OSM way 480015428](https://www.openstreetmap.org/way/480015428) |
| Street level | 4.2–7.0 m (scene): the floor at the highest point, a stone plinth down to the lowest | app terrain |
| Height | 14.5 m (OSM tag, the stone storey and side roofs); the central hall's walkway ≈24.6 m above the floor | OSM; LiDAR 2023 DSM (90th percentile 37.5 m scene) |
| Stone storey | 12.6 m to the cornice, with an attic above – *inferred* | photographs |
| Bays | 10 on the long sides (as it.wikipedia says of the loggia), 8 on the short ones – *inferred* | it.wikipedia, photographs |

## What the model shows (from photographs)
Photographs used (credited in `docs/materials` and on the [library page](/library/mercato-centrale/)): the corner on the
piazza (Sailko, 2016), Via dell'Ariento (Txllxt TxllxT, 2010), the halls from a terrace nearby (Sailko, 2012), the market at the
flower show of 1874 (wood engraving, public domain).

- **Stone storey:** rusticated pietra forte, tall round arches on piers with a panelled base, green louvred shutters and red
  iron fans in the arch heads, a heavy cornice and a low attic hiding the side roofs.
- **Iron halls:** side roofs with a glazed band; the central hall of red cast iron and glass, its gables glazed on the
  short ends, a roof on deep eaves with a walkway and railing along the top. The metal roofs are green, as today.

## Phases
| Years | Part | Basis |
|---|---|---|
| before 1874 | the city data's block on the site (record "Mercato di San Lorenzo", dated 1320 there – see below) | city data |
| 1870–74 | Giuseppe Mengoni; opened in 1874 with the International Horticultural Exhibition | [it.wikipedia](https://it.wikipedia.org/wiki/Mercato_Centrale_(Firenze)) |
| 1976–79 | the first-floor slab on a lattice beam (Odoardo Reali and Architetti Associati) and the underground car park – inside, not shown | it.wikipedia |
| 2014 | the first floor reopened as a food hall – inside, not shown | it.wikipedia |

## Where the sources disagree
- **The city record.** The city data has "Mercato di San Lorenzo" from 1320 (an estimate inside the 1284–1333 walls); the
  hall dates from 1874. The model takes over the record and dates it 1874. What stood on the lot before (houses, the
  Camaldoli convent garden) is not modelled.
- **1874 or 1875.** it.wikipedia says Mengoni's San Frediano market opened in 1875 and the Mercato Centrale in 1874; some
  guides give 1874 for the end of works and others place the opening in 1875. The model uses 1874.

## Review list
- The iron halls are simplified: the real side halls have their own clerestories and the central hall its fretwork and
  roof structure; check against photographs from above.
- The cast-iron colour (red) follows today's paint; the 1874 colour is not known.
- The shutters, the fans and the stone surrounds are generic; the doors in the middle of each side are not drawn.
- The walkway and railing on the roof may be later additions.
- The lot before 1874 is not modelled.
