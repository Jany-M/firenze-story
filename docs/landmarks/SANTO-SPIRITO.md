# Santo Spirito

Model: `blender/scripts/build_santo_spirito.py` → `web/public/models/landmarks/santo_spirito.glb`, in absolute scene
coordinates, geometry from `pipeline/45_chiese.py` → `blender/data/chiese.json`. Register row [M27](../DATA-SOURCES.md#M27).
Library page: [/library/santo-spirito/](/library/santo-spirito/). Shared helpers: `blender/scripts/landmark_church.py`.

The church, Giuliano da Sangallo's sacristy, the Cenacolo (the old refectory) and the convent with its cloisters. The
model works in the front's own frame: `a` along the front (30.6 m) from its south-west corner, `o` along the church's axis.

## Measured
| Item | Value | Source |
|---|---|---|
| Outlines | church, sacristy, Cenacolo, convent | [OSM way 24881563](https://www.openstreetmap.org/way/24881563), [relation 7101376](https://www.openstreetmap.org/relation/7101376), [way 493525529](https://www.openstreetmap.org/way/493525529), [relation 1631265](https://www.openstreetmap.org/relation/1631265) |
| Front | 30.6 m wide, centred on the church's axis (a 12.5 – the nave's ridge and the lantern in the DSM, 2.8 m off the middle of the OSM front segment); ground 8.1 m (scene) | OSM, LiDAR, app terrain |
| Aisles and chapels | aisles under lean-to roofs ≈16–18 m above the square, the outer chapels ≈13–14 m | DSM cross-sections |
| Nave | ridge ≈28 m above the square for ≈60 m; the choir to o ≈87 | LiDAR 2023 DSM along the axis |
| Crossing and dome | o 60–75; drum ≈7 m radius; the lantern ≈45 m above the square | DSM (peak 52.9 m scene at a 12.5, o 67.5) |
| Bell tower | at a −27.6, o 47.5; ≈65 m above the square | DSM peak 73.4 m (scene) |
| Interior | 97 × 32 m, 58 m at the crossing (no units given) | [it.wikipedia](https://it.wikipedia.org/wiki/Basilica_di_Santo_Spirito_(Firenze)) |
| Everything else | Cenacolo, the sacristy's vestibule and rooms, convent: buildings massed from the 1 m DSM raster (`blender/scripts/landmark_mass.py`): hipped roofs at the measured ridge heights, walls, eaves cornices and windows; roofs lean against the church, the bell tower and the sacristy | LiDAR 2023 |

## What the model shows (from photographs)
Photographs used (credited in `docs/materials` and on the [library page](/library/santo-spirito/)): the front (Giaccai,
2014); the church, dome and bell tower from Giotto's tower (Zairon, 2023) and from the Duomo (Luca Aless, 2014); the bell
tower from the square (Pufui PcPifpef, 2018).

- **Front:** the plain plastered front on a stone plinth and steps; the central portal in a pietra serena frame and two
  smaller doors; the curved gable – the middle rising to a small pediment over a ledge, its flanks falling in two volutes to
  the aisle cornices – a big oculus in a moulded ring and a small one under the pediment. In bare stone until it was
  plastered in the 18th century.
- **Church:** ochre plaster with pietra serena corner pilasters and cornices; the nave's clerestory with a tall round-headed
  window a bay; aisles and the lower outer chapels under lean-to roofs; the transept with two windows an arm and its two ends
  gabled as pediments with an oculus, two tall windows and a blind arch; the choir end with a pediment and one window.
- **Dome:** a low drum ringed with fourteen small oculi and a cornice, the tiled dome with stone ribs, the lantern with eight
  little columns, a cap and the gilded ball.
- **Bell tower** (pietra forte): two tiers each with a great arched opening on every face, between cornices; the belfry set
  back behind a balustrade, with scroll buttresses on the corner pedestals, a pillared arch a face and a ring of small
  round holes in the archivolt; the frieze with the inscription AVSPICIIS COSMI; the small bell stage with pinnacles; the tall
  stone spire with a ball and a cross.
- **Before 1481:** the Augustinians' medieval church, a lower hall (size *inferred*).

### Convent, cloisters and the back of the church (from photographs and the DSM)
Photographs: the Chiostro dei Morti (Sailko, 2017), the Chiostro Grande (Sailko, 2009).
- **The church all round:** the aisles and the band of chapels continue round the transept arms and the choir, as in
  Brunelleschi's plan, under hipped roofs at the DSM heights (aisles ≈16.8 m, chapels ≈12.6 m above the square); the
  transept and choir walls above them carry the clerestory windows and the pediment ends.
- **Giuliano da Sangallo's sacristy** (shown 1495): an octagon with pietra serena corner pilasters under a ribbed dome with a
  lantern, placed and sized on the sacristy's highest DSM cells.
- **Chiostro dei Morti** (Giulio and Alfonso Parigi, c. 1620): arches on columns with pulvini, the cornice, the upper floor
  with plain framed windows, a lawn with paths and the round basin in the middle (photograph).
- **Chiostro Grande** (Bartolomeo Ammannati, 1564–69): wider arches on Tuscan columns, the upper floor with round-headed
  windows between pilaster strips, the lawn and a well with its iron frame (photograph).
- The two cloisters sit in the two courts of the convent's OSM outline (relation 1631265); the rest of the convent is
  buildings massed from the 1 m DSM raster (`blender/scripts/landmark_mass.py`): hipped roofs at the measured ridge heights, walls, eaves cornices and windows.
- **Bell tower:** free-standing as built; the city data's 60 m LiDAR shell round it (record dated 1865) is taken over by the model.
- **Front:** the pediment over the middle is as wide as the nave (8.8–21.8 m along the front) and its ledge at the nave's eaves
  (≈24.7 m), so it hides the nave roof's end; the apex ≈28.9 m, the small oculus at ≈26.4 m.

### Piazza Santo Spirito
Sources: [it.wikipedia: Piazza Santo Spirito](https://it.wikipedia.org/wiki/Piazza_Santo_Spirito), photographs of the
fountain (Francesco Bini, 2025; Rufus46, 2014), OSM relation 1631844.
- **Garden beds of 1869** (Luigi Del Sarto, Attilio Pucci), on the outlines OSM gives for today's beds, with a stone curb and
  a low iron railing; the square's trees are the app's tree layer (Comune trees).
- **The fountain** (completed 1660, traditionally Ferdinando Tacca; in the convent's first cloister until Giuseppe Del Rosso
  moved it to the square in 1812): an octagonal pietra serena basin on three steps, a marble shaft with two basins (breccia
  medicea below, white marble above), a small trough on one side. Shown in the square from 1812.
- **The monument to Cosimo Ridolfi** (Raffaello Romanelli, finished 1893, unveiled 4 March 1898): a white marble figure on a
  granite pedestal at the south end of the square, facing Via delle Caldaie. Shown from 1898.

## Phases
| Years | Part | Basis |
|---|---|---|
| 1250–69 | land given in 1250, a church dedicated 1252; the Augustinians begin a church on the site in 1269 – shown 1269–1481 | it.wikipedia |
| c. 1300 | the convent (*inferred*) | – |
| c. 1350 | the Cenacolo, the old refectory (*inferred*) | – |
| 1444–81 | Brunelleschi's church begun 1444 (designed c. 1434), dome 1479–81, consecrated 1481; the old church burnt in 1471 | it.wikipedia |
| 1483–87 | the inner front – the church complete | it.wikipedia |
| 1489 | Giuliano da Sangallo's sacristy begun (shown 1495, *inferred*) | it.wikipedia |
| 1503–70 | Baccio d'Agnolo's bell tower (shown 1570) | it.wikipedia |
| 1564–69, c. 1620 | Ammannati's great cloister, the Parigi's Chiostro dei Morti (inside the convent raster) | it.wikipedia |
| 18th century | the bare stone front plastered (shown 1750, *inferred*) | it.wikipedia |

## Where the sources disagree
- **The foundation:** 1250 (the gift), 1252 (dedication) or 1269 (the Augustinians start building).
- **Brunelleschi's commission:** works overseer named in 1428, Brunelleschi's design "around 1434", building from 1444.
- **The bell tower:** 1503–1570 on it.wikipedia; 1503–1517 in other accounts.
- **The plastered front:** "18th century" with no year.

## Review list
- The volutes' exact curve, the oculus and door sizes come from one photograph.
- The 40 semicircular chapels round the church are hidden in a straight outer wall (as they are outside, except at the
  transept ends and the choir); window counts per face come from photographs from above, their exact places are generic.
- The bell tower's scroll buttresses and the belfry's columns are simplified shapes.
- The dome's number of drum oculi (fourteen) is read from photographs from far.
- The cloisters' bay counts are derived from the court sizes and the photographs (≈2.9 m and ≈4.9 m bays); check them.
- Which of the two courts is which cloister is read from their size and place (the smaller, near the church, as the
  Chiostro dei Morti); check against a plan of the convent.
- The square's garden beds are today's; the 1869 layout had more (two central ones removed in 1976) – not drawn.
- The fountain before 1812 (in the cloister) and the earlier fountain of 1556–1812 at the side of the refectory are not drawn.
- The Cenacolo and the rest of the convent are generic buildings massed from the DSM: refine roofs and windows from photographs.
- The sacristy's vestibule (Cronaca, 1494) and the Corsini chapel are inside the massing, not drawn by hand.
- The medieval church's size and the 1750 date of the plastering are inferred.
