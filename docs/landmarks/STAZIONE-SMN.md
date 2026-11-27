# Santa Maria Novella station

Model: `blender/scripts/build_stazione_smn.py` → `web/public/models/landmarks/stazione_smn.glb`, in absolute scene coordinates, frame from
`pipeline/47_moderni.py` → `blender/data/moderni.json`; shared helpers `blender/scripts/landmark_volume.py`. Register row [M33](../DATA-SOURCES.md#M33). Library page: [/library/stazione-smn/](/library/stazione-smn/).

The passenger building of Florence's main station on Piazza della Stazione, its tracks and platforms, the Palazzina Reale
beside it, and the Maria Antonia station that stood here before it.

Frame: a along the front from its west corner (-636, -437 scene), growing east; o inwards (north, along the tracks).

## Measured
| Item | Value | Source |
|---|---|---|
| Front | at o ≈ 3; a low band 7–9 m (a -10..30) | LiDAR 2023 DSM, read in the frame (`_dev/tmp/asc_smn*.txt`) |
| Clock block | 13–14 m, a -10..4, o 24..50 | DSM |
| Glass cascade | 9–13 m, a 4..30 | DSM |
| High block | 14–15 m, a 30..116, o 12..50; its front swings back north-east from a 62 to a 116 (o 12 → 31) | DSM |
| Canopy | 5–6 m, about 11 m deep in front of the high block, and along the east side | DSM |
| East wing (Via Valfonda) | 12–14 m, leaning with the tracks: a ≈ 116 − 0.21·(o − 30) | DSM |
| West wing (Via Alamanni) | 10–13 m, 16–18 m on its outer side | DSM |
| Platforms | canopies 3–4 m from o ≈ 66 | DSM |
| Palazzina Reale | 9–12 m; outline turned with the tracks (≈13°), the exedra's curve north of it, the portico strip and a small wing along Via Valfonda; the same outline carries the offices along the tracks to o ≈ 368 | [OSM relation 13782297](https://www.openstreetmap.org/relation/13782297), DSM |
| Maria Antonia station | front ≈ 40 m south of today's, the shed running north | map of 1873 (`web/public/data/map_1873.jpg`) |

## What the model shows
From photographs (credited on the library page) and the measured heights:
- **The front (1935):** the clock block at the west end, with its square clock of white figures on dark glass, behind
  a low band of the same stone; then the **cascade** – frosted glass in two tiers, the lower one standing forward on a
  stone base with doors, the upper one rising to the blocks' tops – and the high blind block, whose front swings back
  north-east above the flat **canopy** with its deep fascia and shop fronts.
- **The walls:** pietra forte in long, even courses (drawn as joints), thin copings, almost no openings.
- **The sides:** the long blind east wall along Via Valfonda with the taxi-rank canopy; the west wing along Via
  Alamanni with three floors of windows and its rounded corner towards the square.
- **The gallery** at the head of the tracks under a glazed roof, and **nine platforms** with flat canopies on one row
  of posts, eighteen tracks with buffer stops; the tracks run on into the yard.
- **The Palazzina Reale (1935):** white marble at the north end of the east wing, turned with the tracks; a grid of
  windows on the exedra side, a tall glazed entrance under the portico of honour on slim piers along Via Valfonda, a small
  wing joining Palazzo di Valfonda, the curved exedra with Italo Griselli's group in its basin. The city's shell for
  this outline (record 9939, a generic building cutting through the Palazzina) is replaced.
- **The offices** north of the Palazzina along the tracks, on the same outline.
- **The Maria Antonia station (1848–1934):** a two-storey block with arched openings and a clock turret, lower wings
  either side, a long train shed with a glazed lantern over its four tracks (*inferred* sizes).

## Phases
| Years | Part | Basis |
|---|---|---|
| 1848–1934 | the Maria Antonia station, opened 3 February 1848, four tracks, behind the apse of Santa Maria Novella | [Museo Galileo](https://brunelleschi.imss.fi.it/itineraries/place/FormerLeopoldaStationOfFlorenceMuseumOfRailwayObjects.html); map of 1873; photograph c. 1900 |
| 1932 | competition won by the Gruppo Toscano (Baroni, Berardi, Gamberini, Guarnieri, Lusanna, led by Giovanni Michelucci) | [mugellotoscana.it](https://www.mugellotoscana.it/en/itineraries/in-treno/da-borgo-s-lorenzo-a-firenze/37-itinerari/in-treno/254-stazione-firenze-s-maria-novella.html) |
| 1935 → | the passenger building, inaugurated 30 October 1935; the Palazzina Reale, inaugurated October 1935 | [arttrav.com](https://www.arttrav.com/florence/santa-maria-novella-michelucci/), [fondazionefs.it](https://www.fondazionefs.it/en/Historical-Spaces/firenze-santa-maria-novella.html) |

## Where the sources disagree
- **Built 1932–34 or 1933–35:** manchesterhistory.net gives 1932–1934; the inauguration was in 1935.
- **Who built the Maria Antonia:** Museo Galileo names Brunel's company with Benjamin Herschel Babbage; Wikipedia credits
  Brunel himself.

## Review list
- The Maria Antonia's end date (1934) is *inferred*: the old station was cleared while the new one rose (1933–35).
- The platform count and the tracks are drawn evenly (nine platforms, eighteen tracks); the real layout differs in detail.
- Not drawn: the heating plant and the other service buildings by Angiolo Mazzoni, the old platform roofs, the
  underground passages.
