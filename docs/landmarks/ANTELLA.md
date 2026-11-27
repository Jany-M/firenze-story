# Palazzo dell'Antella

Model: `blender/scripts/build_antella.py` → `web/public/models/landmarks/antella.glb` (absolute scene coordinates), its
front painted from a straightened photograph, `web/public/models/landmarks/img/antella_facade.jpg`. Register row
[M38](../DATA-SOURCES.md#M38). Library page: [/library/antella/](/library/antella/).

The palace on the south side of Piazza Santa Croce (nos. 20–22) whose whole front over the square is painted.

## Measured
| Item | Value | Source |
|---|---|---|
| Front on the square | 32.4 m, from (499.3, 337.7) to (470.7, 322.4) in scene metres | [OSM way 307104291](https://www.openstreetmap.org/way/307104291) |
| Depth | ≈ 13.4 m to the back of the outline | OSM |
| Eave over the square | ≈ 14.5 m (LiDAR 15.6 m at the roof's edge, the eaves projecting) | LiDAR 2023 DSM, sampled every 2 m along the front (`_dev/tmp/antella_probe.py`) |
| Overhang (sporto) | 1.2–1.8 m out over the square, on 13 stone brackets | DSM; the panorama below |
| Heights on the front | overhang underside 3.85 m; string courses at 5.2 and 9.3 m; attic windows ≈ 13.2–14.0 m | the straightened panorama, 32.4 m wide |

## What the model shows
- **The painted front**, from the overhang to the eaves: the 2021 panorama by Ricardalovesmonuments (Wikimedia Commons,
  CC BY-SA 4.0, taken square to the front) straightened onto a 32.4 × 10.6 m rectangle – the four corners of the painted
  wall picked by hand, a perspective warp (`_dev/tmp/antella_tex.py`), a 3072 × 1005 px texture. So every painting is
  where it is: the allegories in grisaille between the arched windows of the piano nobile, under red painted drapes; the
  frieze of framed scenes in colour (octagons and roundels) between grisaille putti and garlands; the attic's small panels;
  the band of cartouches under the lower windows with Chiarissimo Fancelli's bust of Cosimo II in the middle.
- **The overhang** on stone brackets stepping out in three courses, a pietra serena sill along its edge.
- **The ground floor**: shop fronts, barred windows and doors in stone frames, the portal with the dell'Antella arms
  (positions from the panorama).
- **The eaves** on a wide wooden overhang, the roof, and on it the altana and two terraces with railings (seen in every
  photograph; their dates are *inferred*).
- The texture is a photograph: its windows reflect the sky of that afternoon and its colours are today's, faded.

## Phases
| Years | Part | Basis |
|---|---|---|
| 1300 → 1618 | the medieval houses on the square, already overhanging it on brackets; plain plaster front | *inferred* (the sporti of the square are medieval) |
| 1619 | Giulio Parigi joins the houses into one palace for Niccolò dell'Antella | it.wikipedia "Palazzo dell'Antella" |
| 1620 → | the front painted in 1619–20 by Giovanni da San Giovanni with about a dozen painters, said to have taken 27 days | it.wikipedia; Paatz |
| 1850 → | altana and terraces on the roof | *inferred* |

## Your photographs
Jany Martelli's photographs of 2026 (`_dev/images/`, four of them in the library gallery) were used to check the
straightened front: the drapes over the allegories, the frames of the frieze, the attic panels. The photographs of Santa
Croce and of Ponte Vecchio from the Carraia in the same folder are kept for later refinements.
