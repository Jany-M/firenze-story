# Orsanmichele – landmark model

Status: **v1 for review** (2026-11-23). Script: `blender/scripts/build_orsanmichele.py` on the shared `landmark_kit.py`.
Output `web/public/models/landmarks/orsanmichele.glb`. Replaces the record "Chiesa di Orsanmichele".

## Measurements (LiDAR 2023 DSM 0.5 m; OSM way 442508011)
| Measure | Value (above the 10.0 m datum ground) |
|---|---|
| Origin | block centre, scene (−9.0, 121.6); no rotation |
| Plan | 34.5 m east–west × 24.4 m north–south; three bays on the long sides, two on the short sides |
| Height | cornice ≈41 m, low roof to ≈43 m |
| Passage to the Arte della Lana | across Via dell'Arte della Lana on the west, ≈15–18 m |

## Parts and dates
| Part | Shown | Basis |
|---|---|---|
| Arnolfo's open grain loggia (brick piers, timber roof) | 1290 → 1304 | burnt 1304; form *conjectural* |
| new loggia: piers, round arches, 14 tabernacle niches | 1337 | rebuilt from 1337 (Francesco Talenti, Neri di Fioravante, Benci di Cione) |
| first granary floor, temporary roof | 1357 → | (*inferred* split of the 1337–1404 works) |
| second floor, cornice on corbels, roof | 1404 | granary finished c. 1404 |
| arches walled, Gothic tracery windows | 1380 | Simone Talenti |
| guild statues in the tabernacles | 1416 | placed one by one 1399–1601 (one group in v1; originals now in the museum, copies outside) |
| covered passage to the Palazzo dell'Arte della Lana | 1569 | Buontalenti |

## Known limits of v1 (review list)
- Statues are stand-ins and appear together; each tabernacle should carry its own statue and date (Ghiberti's Baptist
  1412–16, Donatello's St George 1415–17, Verrocchio's Doubting Thomas 1483, Giambologna's St Luke 1601 …).
- Tabernacle architecture, the guild roundels (Della Robbia) and the tracery patterns are simplified.
- The older church of San Michele in Orto (before 1240) is not modelled.
