# Santa Maria del Carmine: the church, the Corsini chapel and the convent

Model: `blender/scripts/build_carmine.py` → `web/public/models/landmarks/carmine.glb`, in absolute scene coordinates,
geometry from `pipeline/45_chiese.py` → `blender/data/chiese.json`. Register row [M29](../DATA-SOURCES.md#M29).
Library page: [/library/carmine/](/library/carmine/). Shared helpers: `blender/scripts/landmark_church.py`,
`blender/scripts/landmark_mass.py`.

The Carmelites' church on Piazza del Carmine in Oltrarno, the Corsini chapel at the end of its left transept, the first
cloister and the convent round it. The model works in the front's own frame: `a` along the church front (21.5 m) from its
west corner, `o` inwards (south) along the nave. Piazza del Carmine keeps its OSM / LiDAR ground (today a car park).

## Measured
| Item | Value | Source |
|---|---|---|
| Outlines | church; two blocks to the east and south-east; the convent | [OSM ways 118425485, 480493999, 118425492](https://www.openstreetmap.org/way/118425485), [relation 1632337](https://www.openstreetmap.org/relation/1632337) |
| Front | 21.5 m wide; ground 6.0 m (scene); the gable's top ≈31 m above the square | OSM, LiDAR 2023 DSM |
| Nave | a 0.7–20.8 to o 60; eaves ≈26.5 m, ridge ≈30.3 m | DSM sections across and along the axis |
| Transept | a −9.5…31, o 60–76; eaves ≈24 m, ridge ≈27.6 m | DSM |
| Crossing | an octagon ≈16 m across (apothem 8) on the crossing, its roof's top ≈37.7 m (the highest point of the church) | DSM peak at a 11.5, o 68.5 |
| Choir | a 5–17 to o 86, ridge ≈27.3 m | DSM |
| Corsini chapel | square base ≈15.5 m (a 31–42.5, o 60.5–74.5); octagonal drum to ≈21.5 m, apothem ≈4.6; the lantern's top ≈26.5 m | DSM, the lantern a 1 m spike at a 36.8, o 68.2 |
| Bell gable | a wall 1 m deep and 4.5 m wide at a −4, o 45–49.5, 22 m high, standing on the west chapels | DSM |
| Convent | the first cloister in the court a −30…−4, o 24–51 (the largest court of the OSM relation); wings ≈10–17 m | OSM, DSM |

## What the model shows (from photographs)
Photographs used (credited in `docs/materials` and on the [library page](/library/carmine/)): the front (Sailko, 2009), the
church from the Duomo (Yair Haklai, 2019) and from the west (Pufui PcPifpef, 2018), the back of the church (Francesco Bini,
2021), the Corsini chapel from the garden (Sailko, 2013), the first cloister (Oursana, 2013; Sailko, 2009).

- **Front:** never faced – rough rubble and brick under a plain gable with a small oculus and a cross; a tall round-headed
  window under the ghost of a larger arch; the portal in a moulded frame between pale stone blocks laid long and short; the
  lower part a little wider, with steps.
- **Flanks:** rubble walls with five big round-headed windows a side, a row of small arches on brackets, then a plastered band
  with small square windows under the eaves.
- **Transept and choir:** rubble with ashlar corners, gabled ends with an oculus; the choir's end with a tall window.
- **Over the crossing:** a plastered octagon with framed panels and small openings under a low tiled roof and a weathervane,
  on a square base whose tiled roof slopes up to it.
- **Corsini chapel:** a plastered base with a big lunette window, the octagonal drum with rectangular windows in grey stone
  frames, a low tiled roof and a lantern with columns, a small cupola, a gilded ball and a cross.
- **Bell gable:** two arched openings with their bells, facing west, under a small gable with a cross.
- **First cloister:** round arches on pietra serena columns, an open upper loggia (a parapet, columns and a timber ceiling
  under a lean-to roof), a lawn with paths and a well-head with an iron frame.
- **Convent and the side chapels:** buildings massed from the 1 m DSM raster (`landmark_mass.py`): hipped roofs at the
  measured ridge heights, walls, eaves cornices and windows.

## Phases
| Years | Part | Basis |
|---|---|---|
| 1268 | the Carmelites from Pisa found the church | [en.wikipedia](https://en.wikipedia.org/wiki/Santa_Maria_del_Carmine,_Florence), Comune di Firenze leaflet |
| to 1476 | the church finished; shown from 1300 (*inferred*) | feelflorence.it |
| 1423–c. 1428, 1480s | the Brancacci chapel's frescoes (Masolino, Masaccio, Filippino Lippi) – inside, at the end of the right transept | Comune di Firenze |
| 1597–1600, 1612 | the first cloister: the south loggia begun 6 March 1597 and finished by September 1600, the other three in 1612 | [Catalogo generale dei beni culturali](https://sigecweb.beniculturali.it/sigec/item/print/ICCD5159465) |
| 1675–83 | the Corsini chapel (Pier Francesco Silvani) | Comune di Firenze leaflet |
| 28 January 1771 | the fire destroys the inside of the church; the Brancacci and Corsini chapels and the old sacristy survive | Comune di Firenze, Cambridge UP (Dow 2024) |
| 1775–82 | Giuseppe Ruggieri's rebuilding (Giulio Mannaioni after Ruggieri's death in 1772); the front left unfinished | museionline, italia.it |

## Where the sources disagree
- **The finish of the medieval church:** 1476 (feelflorence) – other guides give no date; the model shows the church from 1300.
- **The octagon over the crossing:** no source here says when it was built. It is shown from the rebuilding of 1782
  (*inferred*); the earlier crossing is drawn under the transept's roofs.
- **Ruggieri's dates:** 1775–82 (museionline) and "in 1775" (italia.it); Ruggieri died in 1772 and Mannaioni went on.

## Review list
- The octagon's date and its earlier form are to check.
- The bell gable's date is unknown (shown with the church).
- The flanks' corbel table and plastered band are drawn the same on both sides; check the west flank over the convent.
- The Brancacci chapel has no outside of its own (it is inside the transept's west arm and the convent): massed from the DSM.
- The convent's second, 15th-century cloister (from 1469, now the Albergo Popolare side) is not drawn; its court is in the OSM relation.
- The two blocks east and south-east of the church (OSM ways 480493999, 118425492) are massed as convent buildings from 1500 (*inferred*).
