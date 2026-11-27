# Stazione Leopolda

Model: `blender/scripts/build_leopolda.py` → `web/public/models/landmarks/leopolda.glb`, in absolute scene coordinates, frame from
`pipeline/47_moderni.py` → `blender/data/moderni.json`; shared helpers `blender/scripts/landmark_volume.py`. Register row [M34](../DATA-SOURCES.md#M34). Library page: [/library/leopolda/](/library/leopolda/).

Florence's first railway terminus, just outside the walls at Porta al Prato.

Frame: a along the head from its north corner (OSM way 269666091), growing south; o inwards along the shed (west-north-west).

## Measured
| Item | Value | Source |
|---|---|---|
| Outline | ≈ 160 × 43–54 m | [OSM way 269666091](https://www.openstreetmap.org/way/269666091) |
| Head | 8–9 m in front (o 0..6), 11–13 m behind | LiDAR 2023 DSM, read in the frame (`_dev/tmp/asc_leo.txt`) |
| Shed | three parallel gabled roofs, ridges ≈ 11 m, valleys 8–9 m, each ≈ 15 m wide | DSM |
| South wing | 17–19 m for 44 m from the head, 8–10 m beyond | DSM |
| West end | 14–16 m, 17–19 m blocks at both corners, an attic 18–19 m on its end | DSM |

## What the model shows
- **The west end towards Livorno:** a rusticated block with three great arches for the tracks, a heavy attic, taller
  corner blocks, arched windows on two storeys at its sides, two small octagonal gatehouses before it (view of c. 1850).
- **The shed:** plastered walls with pilaster strips and a row of round windows under the eaves, three gabled roofs.
- **The south wing:** two tall storeys of windows near the head, one storey beyond.
- **The head:** 1848–1861 a plain two-storey front with arched doors; from 1861 the Exhibition's portico of seven
  arches between piers (still standing), with a pediment, an inscription band and statues (shown to 1900, *inferred*).
- **The side arcade** of the view of c. 1850: arches on piers along the north side (shown to 1900, *inferred*).
- **Today:** the forecourt's steel pergola on concrete piers (from 1997, *inferred*), and the tracks out of the
  portal shown while the station worked (1848–1860).

## Phases
| Years | Part | Basis |
|---|---|---|
| 1848 | opened 2 June 1848, by Enrico Presenti for Grand Duke Leopold II | [Museo Galileo](https://brunelleschi.imss.fi.it/itineraries/place/FormerLeopoldaStationOfFlorenceMuseumOfRailwayObjects.html) |
| 1860 | the last passenger train; the lines meet at the central station | [facarospauls.com](https://facarospauls.com/apps/florence-art-and-culture/4383/stazione-leopolda) |
| 1861 | restructured for the first National Exposition of Arts and Manufactures; Giuseppe Martelli's entrance | Museo Galileo |
| today | an exhibition and events hall | [feelflorence.it](https://feelflorence.it/en/node/12061) |

## Where the sources disagree
- **Which end is which:** the view of c. 1850 is titled "taken from the corner between East and North" but shows the
  tracks' portal at its left. The model puts the portal at the west end (the line ran west to Livorno) and the head
  towards the city, as the photograph of 1861 shows.

## Review list
- When the pediment of 1861 and the side arcade came down is not known (both shown to 1900, *inferred*).
- The south wing's tall part may be later than 1848; the pergola's date (1997) is *inferred*.
