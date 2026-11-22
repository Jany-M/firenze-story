# Campanile and Baptistery – landmark models

Status: **v1 for review** (2026-11-23). Scripts: `blender/scripts/build_campanile.py`, `build_baptistery.py`, both on the
shared kit `blender/scripts/landmark_kit.py` (same as the Duomo). Outputs `web/public/models/landmarks/{campanile,baptistery}.glb`,
previews in `blender/renders/{campanile,baptistery}/`. Each model replaces the LiDAR shell of its record.

## Campanile di Giotto
| Measure (LiDAR 2023 DSM, 0.5 m) | Value |
|---|---|
| Centre | scene x 38.3 / z −116.7 (cells above 70 m) |
| Plan | 15.0 m square at the crown (walls 13.7 m + corner buttresses) |
| Top | platform 85–86 m above the piazza (parapet included) |

| Part | Shown from | Basis |
|---|---|---|
| base: hexagon and lozenge relief bands (blue majolica ground), plinth | 1337 | Giotto 1334–37 |
| niches with statues, blind panelled storey | 1348 | Andrea Pisano 1337–48 |
| first bifore storey | 1352 | Francesco Talenti 1350–59 (storey dates approximate) |
| second bifore storey | 1355 | |
| trifora storey, frieze, crown on corbels, parapet | 1359 | the planned spire was never built |
The tower was clad as it rose, so it has no bare-brick phase. Octagonal corner buttresses run the full height.

## Baptistery of San Giovanni
| Measure | Value |
|---|---|
| Centre | scene x −14.0 / z −149.0 (lantern top) |
| Octagon | apothem 16 m over the pilasters, flats facing the cardinal points |
| Heights | lower order 10.2 m, upper order 18.6 m, attic edge 23.4 m, roof pyramid 33.8 m at the lantern, cross 39.3 m |
| Scarsella | west, 7.7 × 9.2 m, roof at 12.6–14 m |

| Part | Shown | Basis |
|---|---|---|
| lower order (brick → marble) | 1059 → 1090 | consecrated 1059; revetment 1059–1128 (cladding years conjectural) |
| upper order (brick → marble) | 1080 → 1110 | |
| attic (brick → striped marble) | 1110 → 1128 | striped corner treatment trad. Arnolfo c. 1293 (not separated in v1) |
| marble roof pyramid | 1128 | |
| lantern, ball and cross | 1150 | |
| scarsella | 1202 | |
| doors: wood → bronze | south 1336 (Andrea Pisano), north 1424 (Ghiberti), east 1452 (Ghiberti, gilded) | |

## Known limits of v1 (review list)
- Campanile: relief panels are geometric stand-ins (no figures); the niches hold blocks, not statues; the three storeys
  of the Talenti part are equal in pattern; the door on the north side is not modelled.
- Baptistery: the lower order's geometric marble patterns are simplified to framed panels; window aedicules are
  generic; the bronze statue groups above the doors (Rustici, Danti, Sansovino) and the porphyry columns are missing;
  the earlier church on the site (before 1059) is not modelled.
