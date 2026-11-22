# Bargello – landmark model

Status: **v1 for review** (2026-11-23). Script: `blender/scripts/build_bargello.py` on the shared `landmark_kit.py`.
Output `web/public/models/landmarks/bargello.glb`. Replaces every record inside the OSM outline (the block was not
named in the building data).

The Palazzo del Capitano del Popolo, from 1261 the seat of the Podestà, from 1574 of the Bargello (chief of police)
and a prison, since 1865 the Museo Nazionale. The oldest public palace of the city.

## Measurements (LiDAR 2023 DSM 0.5 m; OSM way 43837065)
| Measure | Value (above the street, DTM 48.5 m a.s.l. = scene ground 8.5) |
|---|---|
| Origin | axis of the Torre Volognana, scene (226.6, 136.0); no rotation |
| Plan | whole block between Via del Proconsolo, Via della Vigna Vecchia, Via dell'Acqua and Via Ghibellina, ≈67 × 40 m |
| Front wing (Via del Proconsolo) | x 223–242, top of the battlements ≈28.5 m |
| Courtyard | open, ≈18 × 21 m (x 242–260, z 142–163) |
| Verone | ≈12 m roof along the north side of the courtyard |
| Other wings | ≈23.5–24.5 m |
| Tower | ≈8 m square at the north-west corner, top 54.9 m |

## Parts and dates
| Part | Shown | Basis |
|---|---|---|
| Boscoli tower before the palace | 1180 → 1255 | the palace took in the Boscoli tower (later called the Volognana); its earlier height and the start year are *conjectural* |
| Torre Volognana with corbelled crown and bell cell | 1255 → | crown shape simplified |
| front wing on Via del Proconsolo, two storeys, first roof | 1255 → 1340 | begun 1255 for the Capitano del Popolo (inscription); one study dates the lower storeys 1291–1308 – kept 1255 |
| courtyard paving, well, porticoes | 1280 | courtyard 1280–85 |
| wings on Via Ghibellina, Via dell'Acqua, Via della Vigna Vecchia | 1316 → | raised 1316–20 (Vigna Vecchia side 1320); one date for all three (*inferred*) |
| Verone (first-floor loggia over the north portico) | 1317 | 1317–20 |
| raising by Neri di Fioravante: upper storey, battlements on corbels, new roofs | 1340 | 1340–45 (hall of the General Council, later the Donatello hall; rooms vaulted against fire) |
| open staircase to the Verone | 1367 | Neri di Fioravante, 1345–67 (shown on completion) |

Sources: hmdb.org marker at the museum (1255, the Proconsolo wing with the tower, the Verone 1317–20);
ancient-history-sites.com (the block and the 1316–20 raisings, Neri di Fioravante 1340–45); Wikipedia "Bargello"
(courtyard 1280–85, staircase 1345–67); Catalogo generale dei Beni Culturali (ICCD 13108986, staircase by Neri di
Fioravante; ICCD 14428370, the Boscoli houses and tower bought for the site).

## Known limits of v1 (review list)
- Photo comparison still to do from fixed viewpoints (Via del Proconsolo, Piazza San Firenze, Via Ghibellina,
  the courtyard); window rhythm, the portal and the Ghibellina bifore are generic.
- The staircase side and the exact Verone span are read from the LiDAR heights (*inferred*): check on photos.
- Courtyard details missing: octagonal pillars, the Podestà coats of arms on the walls, the lion on the newel post.
- Prison years 1574–1857 (walled windows, partitions) and the 1857–65 restoration are not shown.
- The houses that stood on the eastern part of the block before 1316 are not modelled (the ground is open).
