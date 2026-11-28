# Palazzo Vecchio – landmark model

Status: **v1 for review** (2026-11-23). Script: `blender/scripts/build_palazzo_vecchio.py` on the shared
`landmark_kit.py`. Output `web/public/models/landmarks/palazzo_vecchio.glb`. It replaces the LiDAR shell of the whole
complex (one OSM record, Arnolfo block to Via dei Leoni).

## Measurements (LiDAR 2023 DSM 0.5 m, OSM way 361442652 and relation 1461712)
| Measure | Value |
|---|---|
| Model origin | tower axis, scene x 73.5 / z 276.5 (highest DSM cell, 95.0 m above the piazza) |
| Arnolfo block | trapezoid, west façade ≈45 m on the piazza, north side ≈29 m, turned ≈10° east of north |
| Crenellations | ≈41 m; inner roofs 34 m (south ranges, around the courtyard) and 42–43 m (north range) |
| Courtyard | open, about 10 × 13 m, in the south half |
| Tower | shaft ≈7.4 m; machicolated gallery ≈10.5 m wide at 63–73 m; belfry to ≈84 m; cupola and Marzocco to 95 m |
| East wings | 30–36 m, to Via dei Leoni |

## Parts and dates
| Part | Shown | Basis |
|---|---|---|
| Torre dei Foraboschi ("della Vacca"), 30 m stump | 1150 → 1310 | *conjectural* height and date; Arnolfo's tower stands on it |
| Arnolfo block: ground floor, portal | 1299 | begun 1299 |
| piano nobile with bifore | 1304 | *inferred* stage |
| top floor, ballatoio on corbels, square (Guelph) merlons, roofs | 1310 | finished c. 1310–14 |
| Torre d'Arnolfo: shaft, gallery with swallowtail (Ghibelline) merlons, belfry, bell, cupola, Marzocco | 1310 | |
| clock dial on the tower | 1353 | public clock from 1353; present dial and movement 17th c. |
| arengario (speakers' platform along the façade) | 1323 → 1812 | then reduced to today's steps (*inferred* dates) |
| David | 1504 | original moved to the Accademia 1873, copy from 1910 (the gap 1873–1910 empty); both from Scan the World's 3D scan of the marble ([M44](../DATA-SOURCES.md#M44), CC BY-SA 4.0), 5.17 m on a plain pedestal |
| Hercules and Cacus | 1534 | Bandinelli |
| Salone dei Cinquecento range | 1495 | Cronaca |
| ducal wings to Via dei Leoni | 1588 | Vasari 1555–72 and Buontalenti 1588–96, one date in v1 (*inferred*) |
| medieval houses on those lots | 1220 → 1495 / 1588 | *conjectural* plots, 3–5 storeys |

Pietra forte throughout, no bare-brick phase. The stone uses the shared `pietra_forte` texture with a warmer, brighter
tint than the city shader (the palace stone reads golden in daylight).

## Known limits of v1 (review list)
- Façade rhythm is regular (real bifore spacing is not); no coats of arms under the gallery, no painted vaults.
- Hercules and Cacus is a stand-in (plinth and block figure; look for a scan first, Scan the World); the David's pedestal is a plain block; the Marzocco, Judith and the Neptune fountain are not modelled.
- Interior courtyard (Michelozzo, 1453–) and the inner ranges are not modelled; the east wings are generic masses
  with plaster fronts.
- The Duke of Athens' fortifications (1342–43) and the 1540 move of Cosimo I are not shown as separate phases.
