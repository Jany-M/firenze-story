# Piazza della Repubblica: the Palazzo dell'Arcone

Model: `blender/scripts/build_repubblica.py` → `web/public/models/landmarks/repubblica.glb`, in absolute scene coordinates,
geometry from `pipeline/43_centro.py` → `blender/data/centro.json`. Register row [M23](../DATA-SOURCES.md#M23).
Library page: [/library/piazza-della-repubblica/](/library/piazza-della-repubblica/). In the app the model takes over the
block's unnamed LiDAR record (dated 1890) and shows it as "Palazzo dell'Arcone di Piazza", from 1895.

The other sides of the square (Palazzo Levi with Paszkowski and Gilli to the north, the Savoy and Trianon blocks to the east,
the Giubbe Rosse block to the south) stay LiDAR shells for now. The Colonna dell'Abbondanza (1431–1890, back since 1956) and
Vittorio Emanuele II's equestrian statue (1890–1932) are placeholders in the statue list ([STATUES.md](../STATUES.md)); the
king now stands on the axis of the Arcone, in the middle of the square.

## Measured
| Item | Value | Source |
|---|---|---|
| Block | the whole block between the square, Via Pellicceria, Via de' Brunelleschi and Via degli Anselmi; 113 m along the square | [OSM relation 1593627](https://www.openstreetmap.org/relation/1593627) |
| Via degli Strozzi under the arch | 11 m wide (scene z 32–43) | OSM outline (the notch in the block) |
| Street level | 8.3–8.8 m (scene) | app terrain |
| Eaves | ≈26.4 m above the street; DSM median 35.1 m (scene) | LiDAR 2023 DSM |
| Central body | 20 m wide, the attic ≈30 m above the street; arch springing at 13.5 m, crown ≈19 m – *inferred* from photographs | – |
| Portico | 5.2 m deep, bays of ≈4.6 m – *inferred* | photographs |

## What the model shows (from photographs)
Photographs used (credited in `docs/materials` and on the [library page](/library/piazza-della-repubblica/)): the arch from
Via degli Strozzi (Zairon, 2023), the square towards the arch (Txllxt TxllxT, 2010), the portico (Manuelarosi, 2023), the
square in 1895 (public domain).

- **Side bodies:** an arcaded portico along the whole square front on piers; above it three storeys of windows with cornice
  pediments, string courses, the main entablature, quoins at the ends.
- **Central body:** the great arch over Via degli Strozzi in radiating voussoirs, the ground storey in banded rustication,
  paired giant columns on pedestals, windows between them, the entablature with MDCCCXCV in the frieze, the attic with the
  inscription "L'ANTICO CENTRO DELLA CITTÀ / DA SECOLARE SQUALLORE / A VITA NUOVA RESTITUITO" in real letters (dark on a
  white panel, as today; Blender's default typeface, not the carved one), four statues of the arts
  over the columns and the balustrade on top.
- **Until 1904:** the group of Italy with Art and Science crowning the arch.
- A barrel vault under the arch, the back of the arch on Via degli Strozzi.

## Phases
| Years | Part | Basis |
|---|---|---|
| before 1885–95 | the Mercato Vecchio and the Ghetto (the city data's "demolished" blocks from the 1830s cadastre, ending 1888) | city data |
| 1895 | the Palazzo dell'Arcone, Vincenzo Micheli | [en.wikipedia: Palazzo dell'Arcone di Piazza](https://en.wikipedia.org/wiki/Palazzo_dell%27Arcone_di_Piazza), [feelflorence.it](https://feelflorence.it/en/node/16768) |
| 1895–1904 | the crowning group of Italy with Art and Science | en.wikipedia |
| 1931 | Piacentini's plan to pull the arch down – never carried out | en.wikipedia |

## Where the sources disagree
- **The year.** The city data dates the block 1890 (the square's own inauguration, with the king's statue, 20 September 1890);
  the building and its frieze say 1895. The model stands from 1895; between 1890 and 1895 the site shows nothing on that side.
- **The style.** en.wikipedia's infobox says Mannerist; its text says critics called it un-Florentine, "Roman". Not a modelling
  question.
- **When the square was cleared.** Demolitions from 1885 (most sources) or "from 1883" (en.wikipedia); the city data ends the
  old blocks in 1888.

## Review list
- The figures (the four arts, the crowning group, the winged Victories in the spandrels) are stand-in blocks.
- The window surrounds, the balconies over the portico and the two side bodies' last overhanging bay are simplified; the
  overhangs over Via Pellicceria and Via de' Brunelleschi are not drawn.
- The other three sides of the square, the 1909 lampposts and the portico floors (c. 1938) are not modelled.
- The 1890–95 gap: the western side of the square stands empty in those years.
- The lettering uses Blender's default typeface; the real one is a Roman capital – a carved-letter font would be closer.
- The Loggia del Pesce (Vasari, 1568–69) stood in the Mercato Vecchio until the demolitions and is not modelled yet; it
  was rebuilt in Piazza dei Ciompi in 1955–56 (plan, PROJECT-DRAFT §12 item 4b).
