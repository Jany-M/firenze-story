# Santa Felicita: the church, its bell tower, the nunnery and the column

Model: `blender/scripts/build_felicita.py` → `web/public/models/landmarks/felicita.glb`, in absolute scene coordinates,
geometry from `pipeline/45_chiese.py` → `blender/data/chiese.json`. Register row [M30](../DATA-SOURCES.md#M30).
Library page: [/library/santa-felicita/](/library/santa-felicita/). The portico and the corridor in front of the church are
part of the Vasari Corridor model ([CORRIDOIO-VASARIANO.md](CORRIDOIO-VASARIANO.md)).

The church on Piazza Santa Felicita, between the Ponte Vecchio and Palazzo Pitti. The Vasari Corridor runs across its front
(1565), on a portico, and opens into the church through the Medici's box. The model works in the front's own frame: `a`
along the front from its north corner, `o` inwards along the nave. The OSM corners of the front lie on the corridor's
centre line, so the frame runs 2 m behind it.

## Measured
| Item | Value | Source |
|---|---|---|
| Outlines | church; the block with the canonica; the former nunnery | [OSM way 159394659](https://www.openstreetmap.org/way/159394659), [way 321893761](https://www.openstreetmap.org/way/321893761), [relation 7224447](https://www.openstreetmap.org/relation/7224447) |
| Front | 16.5 m wide; ground 9.05 m (scene); the corridor's roof ≈10.9 m above the piazza | OSM, LiDAR 2023 DSM, corridor model |
| Nave | a 0–16.5 to o 42; eaves ≈19.8 m, ridge ≈23 m (a low roof) | DSM sections |
| Bell tower | ≈6.5 m square at a 3–9, o 43–49, behind the choir; its top ≈33 m | DSM |
| Canonica and nunnery | ≈20–25 m on the left (a −20…0, o 30–66); ≈10–19 m on the right | DSM |
| Column | OSM node 3116646971 in the piazza | OSM |

## What the model shows (from photographs)
Photographs used (credited in `docs/materials` and on the [library page](/library/santa-felicita/)): the church and its bell
tower over the roofs, from Palazzo Franceschi-Dragomanni (Sailko, 2013).

- **Front:** behind the corridor; above it, plaster between pietra serena corner pilasters, a string course over the corridor's
  roof, two round windows and a pediment with a cross (Ferdinando Ruggieri, 1736–39).
- **Flanks:** ochre plaster with four tall round-headed windows a side in pietra serena frames, the eaves cornice, a low tiled roof.
- **Bell tower:** bare stone, two tall arched openings a face at the top, a cornice and a low pyramid roof.
- **Column:** a granite shaft on a stone base with a marble capital; the glazed terracotta St Peter Martyr on it from 1484 to
  1723, then Montauti's statue to the 19th century (both stand-in shapes).
- **Canonica, nunnery:** buildings massed from the 1 m DSM raster; the cells under the corridor are left to the corridor model.

## Phases
| Years | Part | Basis |
|---|---|---|
| c. 400 | early Christian burials and a cemetery church (the city data's Roman layer) | religiana.com |
| 11th century | a new church (shown from 1000, *inferred*; size *inferred*) | [en.wikipedia](https://en.wikipedia.org/wiki/Santa_Felicita,_Florence) |
| 1244 | the victory over the Patarine heretics in the piazza, remembered by the column | HMdb (the piazza's plaque) |
| late 14th century | the column (shown from 1400); a terracotta St Peter Martyr on it from 1484 until it fell in 1723 | HMdb, en.wikipedia |
| 1564–65 | the Vasari Corridor passes across the front | ancient-history-sites, corridor model |
| 1736–39 | Ferdinando Ruggieri rebuilds the church as one nave for the Benedictine nuns | en.wikipedia, corvinus.nl |
| 1808–10 | the nunnery suppressed under Napoleon; the church becomes a parish | en.wikipedia |

## Where the sources disagree
- **The architect's name:** Ferdinando Ruggieri everywhere except one guide (firenze-oltrarno.net: "Federico Ruggeri").
- **The bell tower:** no date here; shown from 1300 (*inferred*).

## Review list
- The medieval church before 1739 is a guess (a plain hall in stone).
- The crossing's dome and the Capponi chapel's small dome are not seen outside in the DSM; not drawn.
- The front above the corridor is from the plan of the corridor works, not from a photograph of the front: to check.
- The column's height (≈7.5 m with its base) is *inferred*; the statues are stand-in shapes; Montauti's statue's end (1850) is *inferred*.
