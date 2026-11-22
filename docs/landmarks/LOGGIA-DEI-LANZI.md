# Loggia dei Lanzi – landmark model

Status: **v1 for review** (2026-11-23). Script: `blender/scripts/build_loggia_lanzi.py` on the shared `landmark_kit.py`.
Output `web/public/models/landmarks/loggia_lanzi.glb`. Replaces the record "Loggia dei Lanzi" and anything inside its
OSM outline.

Also called the Loggia della Signoria (or dei Priori, or dell'Orcagna): built for the public ceremonies of the
Republic, named "dei Lanzi" after Cosimo I's landsknecht guard, an open-air sculpture gallery since the 16th century.

## Measurements (LiDAR 2023 DSM 0.5 m; OSM way 43284457)
| Measure | Value (above the piazza, DTM 49.6 m a.s.l. = scene ground 9.6) |
|---|---|
| Origin | west front corner, scene (22.8, 275.8); model rotated −0.3696 rad (front at 21.2° to the grid) |
| Plan | front ≈39 m on the piazza, depth ≈13 m; three arches on the front, one on the east side (Piazzale degli Uffizi) |
| Height | roof terrace ≈21.3 m, balustrade ≈22.4 m |
| Arches | spans ≈10 m on 2.2 m composite piers, springing ≈11.9 m (*inferred* from the overall height) |

## Parts and dates
| Part | Shown | Basis |
|---|---|---|
| loggia: raised floor and steps, composite piers, round arches, cross vaults, frieze and cornice | 1376 | built 1376–82, Benci di Cione and Simone Talenti |
| the Virtues in quatrefoils between the arches | 1384 | designs by Agnolo Gaddi, 1384–89 |
| roof terrace with balustrade | 1585 | linked to the Uffizi works under Buontalenti (*inferred* date) |
| Donatello's Judith under the right arch | 1506 → 1582 | moved out when the Sabines came (*inferred* place and years) |
| Cellini's Perseus under the left arch | 1554 | placed 1554 |
| Giambologna's Rape of the Sabines under the right arch | 1583 | installed 1583 for Francesco I |
| Medici lions by the steps; Roman matrons along the back wall | 1789 | lions from the Villa Medici in Rome (one Roman, one by Flaminio Vacca 1598), brought 1789 |
| Menelaus with Patroclus | 1838 | Roman group; year *inferred* ("19th century") |
| Giambologna's Hercules and the Centaur Nessus | 1841 | made 1599, placed in the 19th century (year *inferred*) |
| Pio Fedi's Rape of Polyxena | 1865 | 1865 |

Sources: Wikipedia "Loggia dei Lanzi" (1376–82, builders, Agnolo Gaddi's Virtues); Visit Tuscany (Perseus 1554,
Sabines 1583, Hercules and Nessus 1599 placed in the 19th century, lions moved 1789); italia.it (Perseus under the
left arch, Giambologna's groups under the right arch); ermakvagus.com (Polyxena 1865, the Roman matrons);
benjielayug.com (the two lions, Flaminio Vacca 1598).

## Known limits of v1 (review list)
- Statues are stand-in masses at their places and sizes: replace with proper figures (Perseus holding Medusa's head,
  the spiral Sabines group, Polyxena's group), and check each position on photos.
- Piers are plain blocks: the real ones are clustered (composite) piers with Gothic capitals; vaults are simplified to
  ribs under a flat soffit.
- The terrace date and the original top (before the balustrade) need a source.
- Not shown: the Judith's earlier and later places (ringhiera 1495–1506, Palazzo Vecchio), the replaced originals
  (Perseus restored 1996–2000), the 1990s copies.
