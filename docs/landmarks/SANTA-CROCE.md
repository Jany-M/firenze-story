# Santa Croce – landmark model

Status: **v1 for review** (2026-11-23). Script: `blender/scripts/build_santa_croce.py` on the shared `landmark_kit.py`.
Output `web/public/models/landmarks/santa_croce.glb`. Replaces the record "Basilica di Santa Croce" and the bell-tower
record (unnamed, misdated 1905) through a small `clear` square. The Pazzi Chapel and the cloisters stay city records.

## Measurements (LiDAR 2023 DSM 0.5 m, sections across the nave every 4 m; OSM way 777563049)
| Measure | Value (above the 7.6 m datum ground) |
|---|---|
| Origin / axis | façade centre, scene (576.5, 335.0); nave towards (680, 391), turned −0.496 rad |
| Façade | 41.6 m wide, gable ≈42 m; four pilasters split it into three bays |
| Nave | ≈20 m wide, eaves ≈33.5 m, ridge ≈38.4 m; the high roof runs on over the crossing |
| Aisles | to ±20.5 m from the axis, lean-to roofs 22.5–25.5 m; seven bays of ≈13 m |
| Transept | t 93–114 m, from −31 (north, end chapels to −39.6) to +30 m (south), ridge ≈31.4 m |
| Main chapel | half-octagon to t 121 m |
| Bell tower | t 116.7 / o +25.5 (south-east), ≈6.5 m square, top 76.9 m |

## Parts and dates
| Part | Shown | Basis |
|---|---|---|
| transept, east chapels, main chapel | 1300 | Arnolfo's church, begun 1294/95 from the east end (*inferred* stage date) |
| nave and aisles, east bays | 1320 | built westwards (*inferred*) |
| middle bays | 1350 | (*inferred*) |
| west bays, rough façade (masonry, oculus, three doors) | 1385 | nave finished c. 1385; consecrated 1443 |
| marble façade (white, green and red panels, pilasters with spires, gabled portals, rose window, Star of David) | 1863 | Niccolò Matas, 1857–63 |
| bell tower | 1865 | Gaetano Baccani, 1842–65 |

## Known limits of v1 (review list)
- The first, smaller Franciscan church (c. 1228) and the medieval bell tower (damaged 1512) are not modelled.
- Façade ornament is simplified: no statues, lunette mosaics or the full Gothic tracery; panel pattern is generic.
- Flanks: buttresses and lancets are regular; the north-side loggia and the 19th-century additions are missing.
- Interior, the cloisters and the Pazzi Chapel (Brunelleschi) are not part of this model.
