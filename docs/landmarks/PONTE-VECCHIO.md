# Ponte Vecchio – landmark model

Status: **v1 for review** (2026-11-23). Script: `blender/scripts/build_ponte_vecchio.py` on the shared
`landmark_kit.py`. Output `web/public/models/landmarks/ponte_vecchio.glb`. The model covers the 1345 bridge; the
earlier bridges on the site (Roman timber bridge, the 1177 stone bridge) stay parametric in `web/src/scene/bridges.ts`,
and the rope ferry runs in the gap 1333–1345. It replaces every city record whose centre lies on the bridge
(`clear` polygon in `landmarks.ts`), because the shops are unnamed records with estimated dates.

## Measurements (LiDAR 2023 DSM/DTM 0.5 m, sections across the axis every 4 m; OSM way 24999532)
| Measure | Value (m above the scene datum, 40 m a.s.l.) |
|---|---|
| Axis | scene (−128.8, 379.8) → (−174.3, 471.1), 102 m; model origin at its middle |
| River | ≈1.6 |
| Street on the bridge | 9–10.5, humped towards mid-bridge |
| West (downstream) shops | tops ≈16–17.5, back rooms to ≈12 m from the axis |
| East (upstream) shops + Vasari Corridor | ≈22.4, corridor about 4 m wide on the river side |
| Centre | open terraces between t 42 and 58 m; the corridor crosses on an arcade |
| Banks | t ≈2 and ≈96 m: three arches over ≈94 m |

## Parts and dates
| Part | Shown | Basis |
|---|---|---|
| bridge: three segmental arches 27 + 30 + 27 m, piers 6 m with cutwaters, terraces | 1345 | rebuilt after the 1333 flood (attributed to Neri di Fioravanti / Taddeo Gaddi) |
| shops, west side and east side | 1345 | butchers' and tanners' shops; goldsmiths after the 1593 decree of Ferdinando I (same buildings) |
| east shops below the corridor | 1565 | rebuilt under the corridor (*inferred*) |
| Vasari Corridor, with the arcade over the centre | 1565 | Vasari, for Cosimo I, built in five months in 1565 |
| back rooms (*retrochetti*) on timber struts over the river | 1600 | added from the late 16th–17th century (*inferred* single date) |
| Benvenuto Cellini bust on the west terrace | 1901 | Raffaello Romanelli (stand-in figure) |

## Known limits of v1 (review list)
- Shop widths, heights and colours are randomised within the measured envelope, not surveyed shop by shop.
- The corridor's run around the Torre dei Mannelli on corbels and its windows over the central arcade
  (the three large windows of 1939) are not modelled; the corridor ends at the bridge.
- The clock and sundial, the inscriptions of the 1333 flood and the padlock fence around the bust are missing.
- 1944: the bridge was spared, but its approaches were mined; the destroyed blocks at both ends are handled by the
  city records, not by this model.
