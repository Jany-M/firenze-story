# San Marco: the basilica and the former convent

Model: `blender/scripts/build_san_marco.py` → `web/public/models/landmarks/san_marco.glb`, in absolute scene coordinates,
geometry from `pipeline/45_chiese.py` → `blender/data/chiese.json`. Register row [M28](../DATA-SOURCES.md#M28).
Library page: [/library/san-marco/](/library/san-marco/). Shared helpers: `blender/scripts/landmark_church.py`.

The church and the Dominican convent (today the Museo di San Marco) on the north-east side of Piazza San Marco. The model
works in the front's own frame: `a` along the church front (20.9 m) from its south-west corner, `o` along the nave.
The square itself keeps its LiDAR / OSM ground; the statue of Manfredo Fanti (1873) is a placeholder in the statue list.
The Casino Mediceo di San Marco across Via Cavour is not part of this model.

## Measured
| Item | Value | Source |
|---|---|---|
| Outlines | church; former convent | [OSM way 225706552](https://www.openstreetmap.org/way/225706552), [relation 1575764](https://www.openstreetmap.org/relation/1575764) |
| Front | 20.9 m wide; ≈29.5 m to the top of the cross; ground 10.5 m (scene) | OSM, LiDAR 2023 DSM, app terrain |
| Nave | ridge ≈22.7 m above the square for ≈34 m | DSM along the axis |
| Tribune | Silvani's tribune behind the nave, a 4–19, o 33.5–47.5, eaves ≈22.5 m, ridge ≈25.5 m; a lower room behind it (a 6–15, o 47.5–51.5, ≈17.5 m) | 0.5 m DSM sections |
| Bell tower | at a 16.6, o 45.6 (its square in the 0.5 m DSM, a 15–18, o 44–47), on the tribune's back corner; ≈35 m above the square | DSM peak 45.4 m (scene) |
| Convent | two cloisters (Sant'Antonino's by the church, San Domenico's behind), wings of two storeys: buildings massed from the 1 m DSM raster (`blender/scripts/landmark_mass.py`): hipped roofs at the measured ridge heights, walls, eaves cornices and windows | LiDAR 2023 |

## What the model shows (from photographs)
Photographs used (credited in `docs/materials` and on the [library page](/library/san-marco/)): the front on the square
(Sailko, 2022; Zairon, 2023) and from Giotto's tower (Zairon, 2023), the cloister of Sant'Antonino (Barnos, 2021),
Michelozzo's library (Francesco Bini, 2021).

- **Front (1777–78):** stucco in two tones (the wall lighter, the order darker); two orders of fluted Corinthian pilasters,
  doubled each side of the middle bay, on a stone plinth, each order with its entablature; the portal between two columns
  with a segmental pediment and the sculpted group over it; statues in arched niches under triangular pediments in the side
  bays; the upper order with a window between columns under a segmental pediment and round cartouches with hanging garlands
  at the sides; the attic between the paired pilasters with the relief panel, its flanks sweeping down in concave curves to
  urns with flames over the outer bays; the triangular pediment with a cartouche and the iron cross.
- **Convent front on the square:** two storeys of framed windows (barred on the ground floor), a string course, the eaves
  cornice and the pedimented door near the church.
- **Chapel on the left side:** a block with a hipped roof and a small lantern, seen from Giotto's tower – taken to be
  Giambologna's chapel of Sant'Antonino (1579–89) by its place (*inferred*).
- **Before 1778:** Michelozzo's plain gabled front with a door and an oculus (*inferred*).
- **Church:** the nave and Silvani's tribune by hand (the tribune under a hipped roof with two round-headed windows a side,
  *inferred*), the side chapels massed from the DSM; the bell tower with its belfry clear of the roofs and a tall pointed
  roof (its height from the DSM, ≈35 m; photograph from Giotto's tower, Zairon 2023).
- **Convent:** the cloisters and wings from the DSM.

### Convent and cloisters (from photographs and the DSM)
Photographs: the cloister of Sant'Antonino (Vsatinet, 2019), the cloister of San Domenico (Sailko, 2014).
- **Cloister of Sant'Antonino** (Michelozzo, before 1440): arches on columns with pulvini under a lean-to tiled roof, the
  wings behind with small windows, a lawn with paths.
- **Cloister of San Domenico:** arches on columns, two floors above with shuttered windows, a lawn with paths.
- The two cloisters sit in the two largest courts of the convent's OSM outline (relation 1575764); the rest of the convent
  is buildings massed from the 1 m DSM raster (`blender/scripts/landmark_mass.py`): hipped roofs at the measured ridge heights, walls, eaves cornices and windows.

### Piazza San Marco
Sources: [it.wikipedia: Piazza San Marco](https://it.wikipedia.org/wiki/Piazza_San_Marco_(Firenze)), OSM way 111797401, the
2017 orthophoto.
- **The garden:** the green beds traced from the 2017 orthophoto (the trees are the app's tree layer); shown from 1873,
  the year of the monument (*inferred* – the garden's date is not given).
- **The monument to Manfredo Fanti** (bronze by Papi from Pio Fedi's model, 1873): the figure on a marble pedestal inside its
  iron fence (OSM outline), benches round it. It replaces the placeholder of the statue list.

## Phases
| Years | Part | Basis |
|---|---|---|
| before 1300 | the Silvestrines' monastery and church (shown from 1300, *inferred*) | [it.wikipedia: Convento](https://it.wikipedia.org/wiki/Convento_di_San_Marco_(Firenze)), [Basilica](https://it.wikipedia.org/wiki/Basilica_di_San_Marco_(Firenze)) |
| 1437 | the Dominicans take over; Cosimo il Vecchio pays for the rebuilding | it.wikipedia |
| 1439–44 | Michelozzo rebuilds convent and church; the church consecrated at Epiphany 1443 (shown 1443), the convent shown 1444 | it.wikipedia |
| 1512 | the bell tower (Baccio d'Agnolo) | it.wikipedia |
| 1579–89 | Giambologna's chapels (inside) | it.wikipedia |
| from 1679 | Pier Francesco Silvani's tribune and ceiling | it.wikipedia |
| 1777–78 | the front (fra' Giovan Battista Paladini, from its inscription) | it.wikipedia |
| 1866, 1869 | the convent confiscated; the museum opens | it.wikipedia |

The city data dated the convent's record 1869 (the museum) and the church's 1401; the model shows them from 1444 and 1300.

## Where the sources disagree
- **The Dominicans' arrival:** 1436 in many guides, 1437 on it.wikipedia (1436 there is the year of an Angelico painting).
- **Michelozzo's works:** "1437–1452" in older accounts; it.wikipedia has 1439–44 with the consecration in 1443.
- **The front:** 1777–78 (it.wikipedia, from the inscription); 1777–80 elsewhere.
- **Silvani:** 1678 or 1679.

## Review list
- The front's statues, the sculpted group over the portal, the relief and the garlands are stand-in shapes.
- Which chapel the hipped-roof block on the left side is (Sant'Antonino or the Serragli chapel) is to check.
- Michelozzo's front before 1778 is a guess (plain gable, door, oculus).
- The chapels, the library and the cells are generic buildings massed from the DSM: refine from photographs.
- The tribune's windows and roof form are *inferred*; check against a photograph of its sides.
- The garden beds are traced from the 2017 orthophoto and include some tree shade; the garden's history is not documented here.
- The Fanti figure is a stand-in shape.
- The Silvestrine church before 1443 is a guess.
- The bell tower's belfry and roof are simplified.
