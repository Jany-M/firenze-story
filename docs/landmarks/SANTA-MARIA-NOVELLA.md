# Santa Maria Novella – landmark model

Status: **v1 for review** (2026-11-23). Script: `blender/scripts/build_santa_maria_novella.py` on the shared
`landmark_kit.py`. Output `web/public/models/landmarks/santa_maria_novella.glb`. Replaces the records "Basilica di
Santa Maria Novella" and "Santa Maria Novella" (OHM) and the bell-tower record (small `clear` square). The cloisters
and the convent stay city records; the earlier church of Santa Maria delle Vigne keeps its own record.

## Measurements (LiDAR 2023 DSM 0.5 m, sections every 4 m; OSM way 449369047)
| Measure | Value (above the 5.9 m datum ground) |
|---|---|
| Origin / axis | façade centre, scene (−476.0, −254.6); the nave runs due north (no rotation) |
| Façade | 33 m wide; side parts ≈18 m, pediment apex ≈34 m |
| Nave | 16 m wide, ridge ≈30.5 m, to t ≈79 m; aisles 8 m, roofs ≈17.5 m |
| Transept | t 79–92 m, ridge ≈28 m; lower chapels on both arms |
| Main chapel | to t 103 m, ≈26 m |
| Bell tower | north-west, ≈6.5 m square, top 63.9 m |

## Parts and dates
| Part | Shown | Basis |
|---|---|---|
| transept, chapels, main chapel | 1300 | church begun 1279 from the east end (*inferred* stage date) |
| nave, east bays | 1330 | (*inferred*) |
| nave, west bays | 1357 | nave finished c. 1357–60 |
| bell tower | 1330 | Fra Jacopo Talenti, finished in the 1330s |
| lower marble façade: avelli, side doors, bands, frieze | 1360 | Gothic lower order (*inferred* date) |
| upper façade: rough wall with the rose window | 1360 → 1470 | |
| Alberti's upper façade: attic, temple front, volutes, pediment with the Rucellai sun, central portal | 1470 | Leon Battista Alberti for Giovanni Rucellai, 1458–70 |

## Known limits of v1 (review list)
- Façade inlay patterns are generic; the inscription in the frieze, the sundials and armillary spheres (1572–74) and
  the Rucellai sails are missing.
- The cloisters (Chiostro Verde, Chiostro Grande), the Spanish Chapel and the Strozzi/Rucellai chapels are not modelled.
- Flanks are regular; the avelli along the east side towards the piazza are not modelled.
