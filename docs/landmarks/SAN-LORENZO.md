# San Lorenzo, the Medici Chapels and the Laurentian Library

Model v1 (`blender/scripts/build_san_lorenzo.py` → `web/public/models/landmarks/san_lorenzo.glb`), register row [M17](../DATA-SOURCES.md#M17).
Library page: [/library/san-lorenzo/](/library/san-lorenzo/).

## Measured
| Item | Value | Source |
|---|---|---|
| Axis | from the façade (scene −56.0 / −332.1) towards the Cappella dei Principi, 12.6° north of west | OSM way 599900778 |
| Façade | 31.6 m wide | OSM |
| Nave / aisles / chapels | ridge ≈27.6 m, aisle roofs ≈17.6 m, chapels ≈12 m; nave ≈12 m wide, aisles to ±11 m, chapels to ±15.8 m | LiDAR 2023 DSM |
| Crossing | centre 67 m from the façade; dome ≈36.4 m | LiDAR |
| Old Sacristy | ≈12 m square, dome ≈26.9 m | OSM way 599900777, LiDAR |
| New Sacristy | ≈13 m square, lantern ≈33.7 m | OSM way 599900772, LiDAR |
| Cappella dei Principi | octagon apothem ≈19 m, lantern ≈61 m above the piazza | OSM way 24883267, LiDAR; [it.wikipedia](https://it.wikipedia.org/wiki/Cappella_dei_Principi) gives 28 m for the interior and 59 m for the dome |
| Bell tower | ≈50 m | LiDAR; [it.wikipedia](https://it.wikipedia.org/wiki/Basilica_di_San_Lorenzo_(Firenze)) gives 54 m |
| Cloister and canons' block | garth ≈25 × 26 m, ranges ≈12 m high | OSM relation 4101358, LiDAR |

Ground: the model stands on Piazza San Lorenzo (47.8 m a.s.l.); the walls go 1.5 m below it because the ground falls to
Piazza Madonna degli Aldobrandini (46.5 m) at the Cappella dei Principi.

## What the model shows (from photographs)
Photographs used: the façade and the north flank from Piazza San Lorenzo (Zairon, 2023; Txllxt TxllxT, 2010), the Cappella dei
Principi from outside (2022 restoration), the cloister (Zairon, 2023), the Old and New Sacristy (Sailko, Francesco Bini), the
Ruggieris' 18th-century model of the chapel's exterior – all in `docs/materials` and on the [library page](/library/san-lorenzo/).

- **Façade:** rubble masonry in rough courses (a few bricks, put-log holes), the great brick relieving arch high in the middle,
  a small window in the gable, three portals with panelled doors, stone frames, brick relieving arches and iron gates; the
  steps run along the whole front and turn along the north flank.
- **Flanks:** the side-chapel wall in pietra forte ashlar with one tall blind arch per chapel, recessed between piers with
  pilaster strips, under a cornice; tile lean-to roofs; the aisle wall with an oculus per bay and a brick band; the clerestory
  with round-headed windows in pietra serena frames under a serena entablature; a side door on the north flank.
- **Crossing:** a square tiburio over the roofs with an arcaded loggia (four arches a side) and a low hipped roof with ball
  and cross – the crossing dome is inside it.
- **Old Sacristy:** ashlar block with corner pilasters, entablature and oculi; a cylindrical drum with twelve small oculi and
  a conical tiled roof with a small columned lantern.
- **New Sacristy:** ashlar block with pilasters, a great round-headed window, an oculus and a door on the north face; a drum
  with framed windows, a ribbed tiled dome and Michelangelo's columned lantern with ball and cross.
- **Cappella dei Principi:** pietra forte octagon with white marble pilaster panels and window frames, half-domed niches on
  the diagonal faces, a tall framed window and a panel on the main faces, crypt lights; a drum with paired white pilasters
  and great arched windows in scrolled marble frames; ribbed dome and an eight-column lantern.
- **Bell tower:** ashlar shaft with cornices, belfry arches with a balustrade, an upper stage, lead cupola, ball and cross.
- **Cloister:** arches on pietra serena columns with white spandrels, a trabeated upper loggia on slender columns, wooden
  eaves, ochre walls with doors and barred windows behind; the garth with box hedges and an orange tree.
- **Laurentian Library:** reading-room windows with cornices and mezzanine lights, serena string course and entablature;
  the ricetto rising above it.

## Phases
| Years | Part | Basis |
|---|---|---|
| 393–1059 | first church (conjectural mass) | consecrated 393 – [it.wikipedia](https://it.wikipedia.org/wiki/Basilica_di_San_Lorenzo_(Firenze)) |
| 1059–1450 | the enlarged church of 1059, with its bell tower (extent *inferred*) | same |
| 1428 | Old Sacristy (Brunelleschi, 1421–28) | same |
| 1440 | transept and choir (Brunelleschi's works from 1421; year *inferred*) | same |
| 1461 | nave, aisles, chapels, crossing dome; the bare façade | high altar consecrated 1461 with the church "almost finished" – same |
| 1460 | cloister (Manetti, 1457–60) and the canons' ranges | same |
| 1524 | New Sacristy (Michelangelo, c. 1521–34; the dome year is *inferred*) | same |
| 1571 | Laurentian Library (Michelangelo, from 1524; year it opened, *inferred* for the building) | same |
| 1604 | Cappella dei Principi walls (Nigetti, first stone 6 April 1604) | [it.wikipedia](https://it.wikipedia.org/wiki/Cappella_dei_Principi), [michelangelobuonarrotietornato.com](https://michelangelobuonarrotietornato.com/2024/04/06/6-aprile-1604-la-posa-della-prima-pietra-della-cappella-dei-principi/) |
| 1640 | its drum and dome | [en.wikipedia](https://en.wikipedia.org/wiki/Cappella_dei_Principi): "Nigetti completed the mausoleum in 1640" – **sources disagree**, see below |
| 1740 | bell tower (Ferdinando Ruggieri) | [it.wikipedia](https://it.wikipedia.org/wiki/Basilica_di_San_Lorenzo_(Firenze)) |

**Where the sources disagree.** The Cappella dei Principi: en.wikipedia says Nigetti finished it in 1640; [aviewoncities.com](https://aviewoncities.com/?p=3240)
says the dome was only completed in 1743 under Anna Maria Luisa de' Medici; it.wikipedia only says payments were still
being made in 1743. A window cartouche dated 1642 and the exterior design by Ferdinando and Giuseppe Ruggieri (18th
century) point to a structure standing by the 1640s and an exterior finished a century later. The model shows the dome from
1640. The bell tower: 54 m in it.wikipedia, about 50 m on the LiDAR (cross and finial too thin for the scan).

Not modelled: Michelangelo's façade (designed 1518, never built), the interiors, the crypt, the Medici tombs, the statue of
Giovanni delle Bande Nere on the piazza (1540, statues pass).

## Review list
- Number of chapels per flank (8 here) and the exact bay rhythm against a plan.
- The 1059 church and its tower are plausible masses only; the first church is a placeholder.
- The ricetto's façade towards the cloister and Michelangelo's window frames are simplified.
- The statue of Giovanni delle Bande Nere (1540) on the piazza is left to the statues pass.
