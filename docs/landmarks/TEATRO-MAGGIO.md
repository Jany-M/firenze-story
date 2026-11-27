# Teatro del Maggio Musicale Fiorentino

Model: `blender/scripts/build_teatro_maggio.py` → `web/public/models/landmarks/teatro_maggio.glb`, in absolute scene coordinates, frame from
`pipeline/47_moderni.py` → `blender/data/moderni.json`; shared helpers `blender/scripts/landmark_volume.py`. Register row [M37](../DATA-SOURCES.md#M37). Library page: [/library/teatro-maggio/](/library/teatro-maggio/).

The opera house of the Maggio Musicale Fiorentino on Piazza Vittorio Gui, between the Leopolda and the Cascine.

Frame: a along the south-west side from the west corner (OSM relation 3609352), growing east-south-east; o inwards.

## Measured
| Item | Value | Source |
|---|---|---|
| Outline | ≈ 159 × 133 m, two arms reaching to a ≈ 166; a courtyard a 94..111, o 92..120 | [OSM relation 3609352](https://www.openstreetmap.org/relation/3609352) |
| West block | 16–20 m, a 0..36 | LiDAR 2023 DSM, read in the frame (`_dev/tmp/asc_tea.txt`) |
| Great hall (white block) | 32–34 m, a 36..72, o 0..30 | DSM |
| Fly tower | 34–38 m, a 40..70, o 30..66 | DSM |
| Inclined base | two arms o 0..18 and o 65..86, from 12–14 m at a 70 to the ground at a 140–166 | DSM |
| Cavea | seats rising from 16–18 m (a 76) to 24–26 m (a 134), closed by a wall at a 136 | DSM |
| Rear wing | 12–14 m round the courtyard | DSM |

## What the model shows
- **The great hall:** a block of pale stone with a slightly slanted top, a long band window on a deep slab, two square
  windows, the name on a dark panel at its top corner.
- **The foyer** below it, glazed between white piers carrying the red letters of MAGGIO.
- **The fly tower** in dark glazed terracotta with fine horizontal lines.
- **The inclined base:** two stone arms falling to the square, paved and railed on top – the public walks over them to
  the terraces.
- **The cavea:** the open-air theatre on the roof, its seats rising east, its stage before the fly tower's dark wall.
- **The west block and the rear wing** with rows of slot windows; **the square** with lamp posts.

## Phases
| Years | Part | Basis |
|---|---|---|
| 2011 → | designed by Paolo Desideri (ABDR); inaugurated 21 December 2011 with Beethoven's Ninth under Zubin Mehta | [maggiofiorentino.com](https://www.maggiofiorentino.com/en/theater-of-the-maggio), [risorgimentofirenze.it](https://risorgimentofirenze.it/teatro-del-maggio) |
| 2014 | the first full season | [facarospauls.com](https://www.facarospauls.com/apps/florence-art-and-culture/4382/opera-di-firenze-teatro-del-maggio-musicale) |

The fly tower is 35 m tall (risorgimentofirenze.it); every volume but the fly tower can be walked over on its roof, the
building's skin turning into square, stone garden, terrace and cavea, and the fly tower is clad in glazed terracotta
(Desideri in [artribune.com](https://www.artribune.com/?p=40752)).

## Where the sources disagree
- **Built in 2011 or 2014:** visittuscany.com says "built in 2014"; the theatre opened in December 2011 and was
  completed in stages to 2014.

## Review list
- The great hall's top slant and the exact layout of the foyer and the stair to the terraces are drawn from a few photographs.
- The golden hemisphere of the lobby and the interiors are not drawn.
