# Palazzo Medici Riccardi

Model v1 (`blender/scripts/build_medici_riccardi.py` → `web/public/models/landmarks/medici_riccardi.glb`), register row [M18](../DATA-SOURCES.md#M18).
Library page: [/library/medici-riccardi/](/library/medici-riccardi/).

## Measured
| Item | Value | Source |
|---|---|---|
| Via Larga (Via Cavour) front | 76.3 m = 17 bays of 4.49 m: Michelozzo's 10 and the Riccardi's 7 | OSM relation 1379977; bay counts from the [Biblioteca Riccardiana](https://www.riccardiana.firenze.sbn.it/?p=4038) and [ACC Publishing](https://issuu.com/accpublishinggroup/docs/palazzo_medici_riccardi) |
| Via de' Gori front | ≈40 m, 9 bays, then the battlemented garden wall to Via de' Ginori | OSM; ACC Publishing |
| Cornice | ≈25.5–27.3 m, roofs ≈28 m | LiDAR 2023 DSM |
| Courtyard | ≈10 × 10 m open, arcade round it | OSM inner ring, LiDAR |

Storeys (graded rustication: boldest on the ground floor, flatter on the piano nobile, smooth above –
[it.wikipedia](https://it.wikipedia.org/wiki/Palazzo_Medici_Riccardi)): ground floor to 8.6 m, piano nobile to 16.8 m, top floor to 25.5 m (*inferred* from the DSM).

## What the model shows (from photographs)
Photographs used: Via Cavour fronts and the corner (Txllxt TxllxT, 2010; Francesco Bini, 2021–25), the kneeling window
(Sailko, 2008), the courtyard (Zairon, 2023) and the garden fronts (Sailko, Francesco Bini) – in `docs/materials` and on the
[library page](/library/medici-riccardi/).

- **Ground floor:** huge rusticated pietra forte bosses in irregular courses, the stone bench (*panca di via*) along the base,
  great round arches of radiating voussoirs for the portals (Via Larga, Via de' Gori) and for the corner loggia, small square
  barred windows high up, iron rings.
- **Corner loggia:** open arches with their vault until 1517, then walled up with the kneeling windows on consoles, with
  sill, grille and pediment.
- **Upper floors:** flatter rustication on the piano nobile, smooth stone above, string courses with dentils; bifore under
  voussoir arches with a colonnette, two small arches and a tondo in the lunette.
- **Cornice:** dentils, egg-and-dart, modillions and a corona projecting 2.7 m.
- **Medici arms** on the corner of the piano nobile (palle on a gilded field) and the corner lantern bracket.
- **Courtyard:** three arches a side on composite columns, sgraffito frieze with tondi, bifore on the first floor, windows on the
  second and an open loggia on top; the Riccardi courtyard with windows and an arcade.
- **Garden:** battlemented wall on Via de' Gori and Via de' Ginori with its gate, lawn and trees.

## Phases
| Years | Part | Basis |
|---|---|---|
| until 1445 | houses on Via Larga and Via de' Gori (conjectural) | – |
| 1445–1452 | Michelozzo's palace being built (walls to the piano nobile) | begun c. 1444 for Cosimo il Vecchio – [Visit Tuscany](https://www.visittuscany.com/en/attractions/palazzo-medici-riccardi/) |
| 1452 | the palace finished; corner loggia open, courtyard, garden wall | [it.wikipedia](https://it.wikipedia.org/wiki/Palazzo_Medici_Riccardi): 1444–1452 or 1460; [en.wikipedia](https://en.wikipedia.com/wiki/Palazzo_Medici) gives 1444–1484 – **sources disagree**, the model takes 1452 |
| 1517 | corner loggia walled up with Michelangelo's kneeling windows | it.wikipedia |
| 1659 | sold to the Riccardi (28 March, 40,000 scudi) | it.wikipedia, [Biblioteca Riccardiana](https://www.riccardiana.firenze.sbn.it/?p=4038) |
| 1689 | the extension along Via Larga (7 bays) and the wing on Via de' Ginori | see below |

**Where the sources disagree.** The Riccardi extension: [en.wikipedia (Pier Maria Baldi)](https://en.wikipedia.org/wiki/Pier_Maria_Baldi) has Baldi designing it
1670–84; the Kunsthistorisches Institut's photo records ([Deutsche Digitale Bibliothek](https://www.deutsche-digitale-bibliothek.de/item/E6UESZZIUWTJCLBJUOOUTNADEHBDB253?lang=en))
date the work 1679–82 and 1687–89 (Baldi, then Foggini); [yourwaytoflorence.com](https://yourwaytoflorence.com/db/musei/medric.htm) gives 1715 for the
façade. The model shows it from 1689. The sale to the state: it.wikipedia says 1810.

## Review list
- The Riccardi part repeats Michelozzo's front exactly (as built); its inner courtyard (Cortile dei Muli) is not modelled.
- The Medici arms are simplified (six palle on a gilded field); the Riccardi arms are not drawn.
- The Via de' Ginori wing and the garden are blocks.
