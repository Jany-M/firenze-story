# The lungarni: river walls and parapets, and the flood of 1966

Model: `blender/scripts/build_lungarni.py` → `web/public/models/landmarks/lungarni.glb`, in absolute scene coordinates; the
wall's line from `pipeline/46_lungarni.py` → `blender/data/lungarni.json`. Register row [M32](../DATA-SOURCES.md#M32).
Library page: [/library/lungarni/](/library/lungarni/). The 1966 flood scene is `web/src/sim/flood.ts` (section
[The flood of 4 November 1966](#the-flood-of-4-november-1966)).

The *lungarni* are the streets along the Arno. On the river side each one stands on a high wall (the *muraglione*) with a
low parapet on top (the *spalletta*). They were not built at once: the oldest stretches on the right bank go back to the
1280s–90s, the rest came in the 19th century, most of them with Giuseppe Poggi's works for Florence as capital (1865–72).
Where houses stood in the river (Borgo San Jacopo; Via de' Bardi until the Lungarno Torrigiani) there was no wall.

## Measured
| Item | Value | Source |
|---|---|---|
| Line of each wall | every 20 m along the river: where the ground rises from the river to the street (the face on the first river-level vertex of the 4 m ground), street level (70th percentile of the ground 30–70 m from the bank), the foot | LiDAR 2023 DTM (the app's `terrain.f32`), `river.json` |
| Street over the river | ≈5–6 m (Corsini, Guicciardini), ≈7–8 m (Acciaiuoli to the Grazie), ≈8–11 m (Zecca, Serristori, Torrigiani, Cellini), scene heights | the same |
| Parapet | ≈1 m high, 0.6 m thick, with a stone coping | photographs (below); *inferred* sizes |

## What the model shows (from photographs)
Photographs used (credited in `docs/materials` and on the [library page](/library/lungarni/)): the Lungarno Torrigiani and the
Lungarno Corsini from the river (Sailko, 2013), the Lungarno della Zecca Vecchia (Txllxt TxllxT, 2010), Zocchi's view of the
Lungarno Corsini (c. 1744).

- **The wall:** a vertical face of squared pietra forte, its courses drawn as joint lines, from the foot by the water up to
  the street. The road is carried flat from the wall to the street's edge.
- **The parapet:** red brick under a stone coping on both banks (the brick band is clear in both of Sailko's photographs).
- **The dates:** each stretch appears in the year its wall is first documented (table below).
- **The breaks:** the Lungarno Corsini's parapet is missing from 1966 to 1968; on the Lungarno Torrigiani the top 2.5 m of the
  wall and the parapet are missing from 25 May 2016 to 2017, then rebuilt.

## Phases
| Stretch | Wall from | Basis |
|---|---|---|
| Lungarno delle Grazie (right bank, Rubaconte → Cavalleggeri) | 1287 | the lungarno with a wall from the Rubaconte bridge, 1287 (*documented* in the chronicles; to cite page by page) |
| Lungarni degli Archibusieri, Medici, Diaz (Ponte Vecchio → Grazie) | 1290 | lungarno from Ponte Vecchio to the Rubaconte, 1290 |
| Lungarno degli Acciaiuoli | 1290 | the oldest lungarno, named for the Acciaiuoli palace ([panorama-photo.net](https://www.panorama-photo.net/panorama.php?pid=14406), [Palazzo Acciaiuoli](https://en.wikipedia.org/wiki/Palazzo_Acciaiuoli)) |
| Lungarno Corsini | 1300 *inferred* | continues the Acciaiuoli; walled in Zocchi's view of c. 1744 |
| Lungarno Guicciardini (left bank) | 1600 *inferred* | walled in Zocchi's view of c. 1744 |
| Lungarno Vespucci, Lungarno Soderini | 1850 *inferred* | before Poggi's works, not in their list |
| Lungarno della Zecca Vecchia | 1865 | wall built in the river bed with Poggi's plan; opened as Lungarno della Torricella after the resolution of 1867 ([en.wikipedia](https://en.wikipedia.org/wiki/Lungarno_della_Zecca_Vecchia)) |
| Lungarno Serristori | 1870 | built over the Renai mill race; Palazzo Serristori's new front on it in 1873 ([Museo Galileo](https://brunelleschi.imss.fi.it/itineraries/place/PalazzoSerristoriGarden.html)) |
| Lungarno Torrigiani | 1872 | built in place of the houses of Via de' Bardi on the river (Donato Pineider's photograph "after some demolitions", late 19th century, on Commons) |
| Lungarno Benvenuto Cellini | 1872 | Poggi's works |
| Lungarno Pecori Giraldi | 1890 *inferred* | reaches the Ponte di Ferro by the end of the century |
| Lungarno Corsini: parapet down | 1966–68 | the flood of 4 November 1966 knocked it down (Galleria Bazzanti's account); the stretch's place and the repair year are *inferred* |
| Lungarno Torrigiani: collapse | 25 May 2016 – 2017 | a burst water main undermined ≈200 m of the road, 7 m wide; the wall was deformed and shored with a 120 m retaining wall and piles by September 2016 ([Il Post](https://www.ilpost.it/2016/05/25/e-crollato-un-pezzo-di-lungarno-a-firenze/), [MeteoWeb](https://www.meteoweb.eu/2016/10/firenze-lungarno-torrigiani-conclusi-in-anticipo-i-lavori/763028/), [EGU 2020](https://meetingorganizer.copernicus.org/EGU2020/EGU2020-6857.html)) |

## Standing on the ground
The 4 m ground model turns a vertical wall into a slope. The face is put on the first river-level vertex of each grid column
(so the slope stays behind it), the road is carried flat over the slope to the street, and `pipeline/21_build_env.py` holds the
ground at the wall's foot from under that road to 25 m out (it reads the line from `lungarni.json`; `46_lungarni.py` reads the
ground before that hold, `_dev/data/build/terrain_raw.f32`).

## The flood of 4 November 1966
A Live scene (Events tab, 4 November 1966): the Arno rises in its bed through the night, comes over the parapets about 5 a.m.,
fills the lungarni and Santa Croce, reaches Piazza del Duomo by 9:45, stands highest in the afternoon, falls from 8 p.m., and
the streets clear on 6 November. A clock at the top of the screen names the hour and the stage.

- **Height of the water:** a sloping surface calibrated on two records – 4.92 m on the plaque in Via dei Neri (Santa Croce) and
  ≈1.8 m ("at least six feet") in Piazza del Duomo – falling in a straight line with the distance from the river's axis
  (*inferred*). The result: ≈4.3 m in Piazza Santa Croce, ≈1.2 m in Piazza della Signoria, ≈1.7 m in Piazza del Duomo; Palazzo
  Pitti's piazza and the hills stay dry.
- **Where:** every place whose ground is lower than that surface. The 4 m ground draws kerbs and building lines as low ridges,
  so the water is not routed street by street.
- **When:** each place floods after 5 a.m. at a speed that brings the water from the bank to the Duomo by 9:45.
- Sources: the Via dei Neri plaque (Protezione Civile, [alluvione-firenze.pdf](https://servizio-nazionale.protezionecivile.gov.it/static/4019da085c64ebd948af0693ce73176e/alluvione-firenze.pdf));
  Piazza del Duomo at 9:45 ([en.wikipedia](https://en.wikipedia.org/wiki/1966_flood_of_the_Arno)) and around 9 ([Il Post](https://www.ilpost.it/2016/11/04/alluvione-firenze-1966/));
  "at least six feet" in Piazza del Duomo, the water falling from 8 p.m. (Yahoo News, "On this day"); the streets clear on 6
  November ([Internazionale](https://www.internazionale.it/foto/2015/11/04/alluvione-firenze-anniversario)); the break of the
  parapet at Piazza Cavalleggeri ([Sky TG24](https://tg24.sky.it/cronaca/approfondimenti/Alluvione-firenze-1966)).

## Where the sources disagree
- **How deep in Santa Croce:** 4.92 m on the Via dei Neri plaque; "about five metres", "over 5 m" in the press; "six metres" in
  one account of the Pope's visit (ilpostalista.it); "over 22 ft" (6.7 m) in Yahoo News. The model uses the plaque.
- **Piazza del Duomo:** "around nine" (Il Post, meteo.it) or 9:45 (en.wikipedia). The model uses 9:45.
- **Lungarno della Zecca Vecchia:** the wall in 1865 (the works) or the street opened after 1867 (en.wikipedia). The model
  shows the wall from 1865.
- **The Lungarno Corsini's parapet in 1966:** which stretch fell is not given; the model's 120 m is *inferred*.

## Review list
- The medieval dates (1287, 1290) come from the chronicles as summarised in guides; find the primary citations (Villani).
- The Lungarno Guicciardini, Corsini, Vespucci and Soderini dates are *inferred*.
- The flood is one surface, not a routed flow; the 1966 flood maps of the Comune (water heights street by street) would let
  the surface follow the real marks. The 1333 and 1844 floods have no animation.
- The landings (scali), the Renai's mill race and the stairs down to the river are not drawn on the walls.
