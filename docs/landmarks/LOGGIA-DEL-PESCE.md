# Loggia del Pesce

Model: `blender/scripts/build_loggia_pesce.py` → `web/public/models/landmarks/loggia_pesce.glb`, in absolute scene
coordinates. Register row [M26](../DATA-SOURCES.md#M26). Library page: [/library/loggia-del-pesce/](/library/loggia-del-pesce/).

One model, two places by date: in the Mercato Vecchio from 1569 to 1889, in Piazza dei Ciompi since 1955. In the app the
loggia takes over the record the city data had traced from the 1830s cadastre in the Mercato Vecchio (a "medieval house",
1150–1888), renamed "Loggia del Pesce" and dated from 1569 with no end; the search therefore flies to its old place.

The rest of the Mercato Vecchio before the demolitions (the Beccheria, the churches of San Tommaso and Santa Maria in
Campidoglio, the towers, the "corona" of shops) is still the city data's traced blocks; a model of it is in the plan.

## Measured
| Item | Value | Source |
|---|---|---|
| Size | 32.4 × 6.2 m | [OSM way 204145494](https://www.openstreetmap.org/way/204145494) (Piazza dei Ciompi) |
| Height | roof ≈9.4 m above the square | LiDAR 2023 DSM |
| Mercato Vecchio | the lone rectangle on the market's west side in the 1830s cadastre: x −115.6 … −109.4, z 1.8 … 34.2 (scene), long side north–south – the same 32.4 × 6.2 m | Catasto Generale Toscano (the app's cadastre map) |
| Ground | Mercato Vecchio 9.2 m, Ciompi 7.7 m (scene) | app terrain |
| Arches | nine a side, two on each short end; springing at 3.2 m, eaves 7.6 m – *inferred* | photographs |

## What the model shows (from photographs)
Photographs used (credited in `docs/materials` and on the [library page](/library/loggia-del-pesce/)): the loggia in the
Mercato Vecchio before 1880 and before 1885 (public domain), Piazza dei Ciompi in 2018 (Manuelarosi).

- A double row of round arches on Tuscan columns of pietra serena with piers at the corners, a middle row of columns.
- A medallion over every column (the fish tondi), the Medici and Grascia arms at the corners, the cartouche in the middle.
- A plain band over the arches, a stone cornice and a hipped tiled roof on deep eaves.
- Inside, a flat ceiling stands for the domed vaults.

## Phases
| Years | Part | Basis |
|---|---|---|
| 1568–69 | built by Vasari for Cosimo I, 19 August 1568 – 22 February 1569, for the fishmongers moved off the Lungarno by the Vasari Corridor | [it.wikipedia](https://it.wikipedia.org/wiki/Loggia_del_Pesce) |
| 1699 | one arch added at each end – the model shows seven bays before and nine after | it.wikipedia (also "1669" on the same page) |
| 1889 | dismantled from May, in the Risanamento; the best pieces kept at the Museo di San Marco | it.wikipedia |
| 1955 | rebuilt in Piazza dei Ciompi (planned from 1950, Cassa di Risparmio, Giulio Cesare Lensi Orlandi Cardini) | it.wikipedia |

## Where the sources disagree
- **The enlargement:** 1699 in it.wikipedia's history, 1669 in its description of the end tondi. Whether the nine arches are
  the original count or the enlarged one is not said; the model takes seven + two.
- **When it was taken down:** May 1889 (it.wikipedia); some guides say 1880 or 1885, the years the market closed and the
  demolition was approved.
- **When it was rebuilt:** 1955 (it.wikipedia); 1956 in en.wikipedia and on the city's tourist site.
- **How much is original:** it.wikipedia says only the arms and the plaque were reused and the tondi are copies; other
  sources say it was rebuilt "with the original materials". The model is the same in both places.

## Review list
- The tondi are plain medallions, not the fish reliefs; the arms and the cartouche are flat shapes.
- The domed vaults are not drawn (flat ceiling).
- Its exact place and orientation in the Mercato Vecchio come from one cadastre rectangle; check against the 1880s
  photographs and plans of the market.
- The seven-bay state before 1699 is an interpretation.
- The Mercato Vecchio around it (Beccheria to 1881, churches, towers) is still the traced blocks.
