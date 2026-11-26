# Le mura – the city walls, gates and towers

Status: **v1 for review** (2026-11-26). Geometry: `pipeline/40_walls.py` → `blender/data/walls.json`. Model:
`blender/scripts/build_mura.py` on the shared `landmark_kit.py` → `web/public/models/landmarks/mura.glb` (+ `mura_clear.json`,
the gate footprints whose LiDAR shells the model replaces). Register row [M14](../DATA-SOURCES.md#M14).

One model for the sixth (Arnolfian) circle: the walls on both banks, the towers along them, the gates, the 16th-century
bastions and the Fortezza da Basso. It is placed in absolute scene coordinates. Each gate and tower is a separate
member, so clicking it opens its own card. Clicking a wall or one of the plain towers opens "Cerchia d'Arnolfo".

## How the model changes over time
| Years | What you see | Basis |
|---|---|---|
| 1284 → | North-bank walls with their wall-walk, square (Guelph) merlons and a tower about every 115 m (200 braccia). The gates of the north bank stand as tall towers with merlons. | Circuit begun 1284 (Arnolfo di Cambio), finished 1333; walls 20 braccia (≈11.6 m), towers 40 braccia (≈23 m): Villani via the secondary literature. Line: OpenHistoricalMap |
| c. 1320 → | Oltrarno walls from Santa Rosa round to San Niccolò; San Miniato (1320), San Niccolò and San Giorgio (1324), Porta Romana (1326), San Frediano (1332). | Gate dates: visittuscany.com, it.wikipedia; the Oltrarno stretches are dated c. 1320 (*inferred*) |
| 1529 | Towers and gates cut down to about the height of the walls (the siege of 1529–30). San Niccolò keeps its full height. | visittuscany.com (Porta alla Croce); it.wikipedia (Torre San Niccolò, "l'unica torre di Firenze non scapitozzata") |
| 1530 | Porta alla Giustizia gone (the Mongibello bastion takes its place). | OpenHistoricalMap 1284–1520; bastion 1531 |
| 1531–1554 | Bastions at Mongibello (by the Zecca), San Gallo, the "tre canti" and the Serpe. | OpenHistoricalMap dates; Michelangelo / Antonio da Sangallo the Younger |
| 1534 | Fortezza da Basso, brick curtains on a stone plinth with a stone cordon and an earth rampart inside. Porta a Faenza stays inside it. | Built 1534–37; outline OSM way 1489561765 |
| 1590 | The old wall over the Boboli hill gives way to the Forte di Belvedere (its own model is planned with Pitti). | OpenHistoricalMap 1333–1595 |
| 1739 | Arco di Trionfo dei Lorena by Porta San Gallo (Jean-Nicolas Jadot, 1739–45). | it.wikipedia "Arco di Trionfo (Firenze)" |
| 1866–1870 | North-bank walls, towers and bastions pulled down for Poggi's viali; Porta a Pinti demolished. Porta alla Croce, San Gallo, al Prato, the Zecca and the Serpe stay, standing alone in their squares. The short wall from San Niccolò down to the river goes with Piazza Poggi. | Poggi's plan (Firenze capitale) |
| today | Oltrarno walls stand along via di Belvedere, Boboli, viale Petrarca / Ariosto and from San Frediano to Santa Rosa, with their towers cut down. | OSM `barrier=city_wall`, heights from the LiDAR 2023 DSM |

## Gates and towers
| Member | Footprint (OSM) | Height today (DSM) | Before 1529 | Notes |
|---|---|---|---|---|
| Porta Romana | way 167972690, 19 × 13 m | 22.9 m | 33 m (*conjectural*) | 1326–28; original wooden doors; stone lily over the outer arch; fresco lunette on the city side |
| Porta San Frediano | way 118932420 (gate with its forecourt; tower modelled 20 × 14.5 m) | 24.6 m | the same | 1332–34, attributed to Andrea Pisano; never finished in height, so never cut down; stone arms on the city side |
| Porta alla Croce | way 72905107, 15 × 13 m | 17.3 m | 32 m (*conjectural*) | 1284; cut down 1529–30; alone in Piazza Beccaria since Poggi |
| Porta al Prato | way 72915039 | 18.9 m | 32 m (*conjectural*) | 1284; named after the open field before it |
| Porta San Gallo | way 72905103, 15 × 16 m | 21.0 m | 33 m (*conjectural*) | begun 1285 (inscription 1284); fresco lunette |
| Torre San Niccolò | way 72915036, 16 × 13 m | 44.7 m | the same | 1324; the only tower not cut down; open towards the city (floors on beams), parapet on corbels, hipped roof |
| Porta San Giorgio | way 707346991, 9 × 10 m | 10.6 m | the same | 1324; St George relief outside (a copy), Bicci di Lorenzo's Madonna inside |
| Porta San Miniato | node 1536508532 | – | – | 1320; an arch through the wall, no tower |
| Torre della Zecca | way 72905106, 10 × 9 m | 24.6 m | 31 m (*conjectural*) | end tower on the river (Piazza Piave); restored 2014–16 |
| Torre della Serpe | way 72915046 | 17.1 m | 23 m (*conjectural*) | corner tower by Porta al Prato |
| Torrino di Santa Rosa | way 119009554 | 18.4 m | the same | river tower west of San Frediano |
| Torre della Verzaia | way 464120152 (unnamed tower) | 12.3 m | the same | between San Frediano and Santa Rosa |
| Porta a Faenza | way 866278404 | 17.6 m | 32 m (*conjectural*) | absorbed into the Fortezza 1534; still visible from outside |
| Porta a Pinti | OHM node | – | 32 m (*conjectural*) | 1284 → demolished 1866 (*inferred* year in 1865–70) |
| Porta alla Giustizia | OHM node | – | 30 m (*conjectural*) | 1284 → 1530 |

Each gate is a tower over a pointed (San Frediano: round) passage arch. The city side is open above the arch, with
wooden floors on joists, as the surviving gates and San Niccolò show. The gates cut down in 1529 have a single-pitch
tile roof that slopes towards the city.

## Walls
- **North bank:** OpenHistoricalMap ways 198777547 and 198777726, 1284–1868. The lines are coarse (25 + 3 points) but
  follow today's viali. Height 11.6 m, thickness 2.2 m.
- **Oltrarno:** OSM `barrier=city_wall` ways where the wall stands today. The height of the standing wall is taken
  from the DSM across a 3 m swath and clamped to 5.5–13 m, since trees and houses are built against it. OpenHistoricalMap
  or straight joins fill the gaps (*conjectural*, listed in `walls.json` with their source).
- **Towers:** generated every 115 m along every wall line, none within 40 m of a gate. Each is 8 m along the wall and
  projects 6 m outward, with arrow slits and merlons until 1529. After that it is cut down to the wall-walk with a
  stone coping. 66 in all.
- **Bastions:** OpenHistoricalMap outlines raised as earth platforms faced in stone, about 10 m high.

## Earlier circles
The Carolingian, Matilda's (1078), the 1172–75 and the 1260 extension circles come from OpenHistoricalMap ways (ids 198777552–563, 571–573), drawn lower (7–9 m) and without towers' details, and valid from their start year until the sixth circle replaces them. The records for them are hidden by the model (`replaces`).

## Ground
Every wall sample is placed on the app's terrain mesh (`terrain.f32`, bilinear), not on the 0.5 m DTM: the two differ by up to 4 m on the Oltrarno slopes, which made stretches sink. `_dev/tmp/check_walls.py` checks it (difference ≤ 0.02 m).

## Review list
- Pre-1529 heights of the gates (all *conjectural*: Villani's 40 braccia for the towers, about +10 m for the gates).
- Exact course of the north-bank wall near the river at the Prato end, and of the wall from San Niccolò down to the Arno.
- Merlons are shown on every stretch, also where today's wall has lost them.
- The gates' frescoes, doors and arms are stand-ins: panels at their places and sizes.
- Fortezza da Basso: outer curtains only. The Mastio, the inner buildings and the bastion faces at their true angles are still to do.
