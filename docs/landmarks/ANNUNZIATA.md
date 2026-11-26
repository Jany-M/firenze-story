# Piazza della Santissima Annunziata

Model: `blender/scripts/build_annunziata.py` → `web/public/models/landmarks/annunziata.glb`, in absolute scene coordinates,
geometry from `pipeline/44_annunziata.py` → `blender/data/annunziata.json`. Register row [M25](../DATA-SOURCES.md#M25).
Library page: [/library/santissima-annunziata/](/library/santissima-annunziata/).

One model for the three sides of the square: the Spedale degli Innocenti (south-east), the Loggia dei Servi di Maria
(north-west, facing it) and the Basilica della Santissima Annunziata with its portico (north-east end). Ferdinando I's
equestrian statue (1608) and Tacca's two sea-monster fountains (1641) are placeholders in the statue list
([STATUES.md](../STATUES.md)). Palazzo Budini Gattai (Grifoni) on the corner of Via dei Servi is not modelled yet.

The model works in the square's own frame: `a` runs along the Innocenti front from its south-west end towards the church,
`o` across the square from the Innocenti front (0) to the Loggia dei Servi front (61).

## Measured
| Item | Value | Source |
|---|---|---|
| Innocenti front | 73.8 m (nine arches of ≈5.84 m and two end bays of ≈10.6 m); it.wikipedia gives ≈71 m | [OSM relation 7085758](https://www.openstreetmap.org/relation/7085758), [it.wikipedia](https://it.wikipedia.org/wiki/Spedale_degli_Innocenti) |
| Loggia dei Servi | front from a 5 to 77 (72 m), twelve arches; ≈21 m to the eaves | DSM profile across the square, [OSM relation 7021619](https://www.openstreetmap.org/relation/7021619) |
| Church portico | a 82–90, o 8–48 (40 m wide, ≈8 m deep) | DSM, [OSM way 234428743](https://www.openstreetmap.org/way/234428743) |
| Nave | a 104–152, o 17.5–31.5, ridge ≈23.6 m above the square; side chapels o 5.5–17.5 (≈9–13 m) and o 31.5–37.5 (≈11–12 m) | DSM |
| Tribuna | centre a 164, o 21; round wall r ≈14 m up to ≈26.5 m, a ring of roof to the dome's foot at ≈28 m, dome r ≈10 m to ≈34 m | DSM radial profiles |
| Bell gable | a narrow peak ≈37 m above the square where the tribuna meets the nave on the north side | DSM; [it.wikipedia: Basilica](https://it.wikipedia.org/wiki/Basilica_della_Santissima_Annunziata_(Firenze)) ("campanile a vela" with five openings on the rear drum) |
| Chiostrino dei Voti | a 90.5–104, o 17–33, covered ≈10 m above the square | DSM |
| Ground | the square 9.3 m (scene, median); fronts on their highest point along the front: Innocenti 10.0, Servi 10.6, church 9.3 | app terrain |
| Arches | the three porticoes' arches spring at the same height (the church's columns are set higher to match) | [it.wikipedia: Basilica](https://it.wikipedia.org/wiki/Basilica_della_Santissima_Annunziata) |
| Behind the fronts | wards, cloisters, the houses over the Loggia dei Servi, chapels and convent rooms: buildings massed from a 1 m raster of the DSM inside the OSM outlines (`blender/scripts/landmark_mass.py`): hipped roofs at the measured ridge heights, walls, cornices and windows | LiDAR 2023 |

Column height (5.6 m), steps (1.4 m on the Innocenti side), portico depths and the end bays' width are *inferred* from photographs.

## What the model shows (from photographs)
Photographs used (credited in `docs/materials` and on the [library page](/library/santissima-annunziata/)): the Innocenti
front (Ricardalovesmonuments, 2021), a della Robbia tondo (Sailko, 2016), the Loggia dei Servi (Sailko, 2020), the church
front (Txllxt TxllxT, 2010), the square in a panorama (Gryffindor, 2008), Giuseppe Zocchi's view of the square (18th century).

- **Innocenti:** a long flight of steps; nine round arches on pietra serena columns with their pulvini; Andrea della
  Robbia's blue tondi in the spandrels (two more, by Pasqui, at the ends from 1845); an entablature; the upper floor
  with a pedimented window over each arch; the two closed end bays with fluted pilasters and a portal, an oculus on the
  left one; a plain tiled roof.
- **Loggia dei Servi:** the same order copied across the square, twelve arches on steps, tondi; the three arches at the
  south-west end walled up with windows (1720); the upper floor with pedimented windows and shutters.
- **Church:** Caccini's portico of seven arches, the middle one wider under a curved canopy, between two pilastered ends;
  the frieze with the Pucci inscription (ALEXANDER ET ROBERTVS PVCCII FRATRES DEI GENITRICI) in real letters; a low attic
  with urns; three doors behind. Behind it the Chiostrino dei Voti with an arcade on each long side under its iron and
  glass roof; Michelozzo's nave with a round-headed window over each side chapel (*inferred*), the chapels under
  lean-to roofs; the Chiostrino dei Voti with arcades on all four sides on Corinthian columns, the church's doors under the
  far side, an upper floor of ochre panels with small paired windows and tondi, and the iron-and-glass roof with its
  cresting over the open court (photographs: Sailko; Bernoud c. 1865); the round tribuna with pietra serena pilaster strips, its ring of roof, the ribbed dome and lantern, and
  the bell gable with five openings (its face and the order of the openings *inferred*).

## Phases
| Years | Part | Basis |
|---|---|---|
| 1250 | the Servites' church (first stone 25 March 1250), a lower nave in the model | [it.wikipedia: Basilica](https://it.wikipedia.org/wiki/Basilica_della_Santissima_Annunziata) |
| 1419–27 | Innocenti: portico begun 1419 (first column January 1421), portico, church and wards largely built by 1427 – shown from 1427 | [it.wikipedia: Spedale](https://it.wikipedia.org/wiki/Spedale_degli_Innocenti) |
| after 1435 | Innocenti upper floor and end bays (Francesco della Luna) – shown from 1439 (*inferred*) | it.wikipedia ("after 1435" / 1436) |
| 1444–77 | Michelozzo's tribuna begun 18 October 1444, inaugurated 1477 | it.wikipedia |
| 1445 | the Innocenti open (25 January) | it.wikipedia |
| 1447 | Chiostrino dei Voti begun – the block in front of the church shown from 1455 (*inferred*) | it.wikipedia |
| 1460 | the middle bay of the church portico, attributed to Antonio Manetti (*inferred* year: Manetti took over the works in 1460) | it.wikipedia |
| 1481 | the nave completed | it.wikipedia |
| 1850 | the Chiostrino dei Voti closed with an iron and glass roof under Leopold II (*inferred* year, before the 1857 restoration) | [ermakvagus.com](https://www.ermakvagus.com/Europe/Italy/florence/voti.html) |
| 1487 | Andrea della Robbia's tondi | it.wikipedia |
| 1516–25 | Loggia dei Servi (Antonio da Sangallo the Elder, Baccio d'Agnolo) | [it.wikipedia: Loggiato dei Serviti](https://it.wikipedia.org/wiki/Loggiato_dei_Serviti) |
| by 1574 | its upper floor | it.wikipedia |
| 1601 | the church portico (Giovanni Battista Caccini, paid by the Pucci) | it.wikipedia |
| 1608 | Ferdinando I (placeholder) | statue list |
| 1641 | Tacca's fountains (placeholders) | [en.wikipedia](https://en.wikipedia.org/wiki/Fontana_dei_mostri_marini), [Flore (UniFi)](https://flore.unifi.it/handle/2158/1284611) |
| 1720 | the last three arches of the Loggia dei Servi walled up | it.wikipedia |
| 1845 | the two end tondi (Leopoldo Pasqui, after the 1842 earthquake) | it.wikipedia |

The city data had the Innocenti ending in 1875 (the year the foundling wheel was walled up, picked up by the map test) and
the Loggia dei Servi starting in 1320; the model takes over all three records with the dates above.

## Where the sources disagree
- **The Innocenti's length.** OSM measures 73.8 m, it.wikipedia says about 71 m; the model follows OSM.
- **The Innocenti's upper floor:** "after 1435" and 1436 on the same page; whether it was in Brunelleschi's design is debated.
- **The church portico:** "the last decades of the 16th century" or 1601 (Caccini); the middle bay older, attributed to
  Manetti; some guides credit Michelozzo or Antonio da Sangallo with it. The model: the middle bay from 1460, the rest 1601.
- **Tacca's fountains:** made c. 1627–29 (many catalogues date them 1629, and italia.it puts them in the square that year),
  set in the square in 1641 (en.wikipedia, the UniFi study). The model uses 1641.
- **The Loggia dei Servi:** "1516–25" for a building whose upper floor was finished by 1574 and whose last arches were closed
  in 1720.

## Review list
- The church portico's ends, the canopy and the urns are simplified; Pontormo's and others' lunettes, the Ghirlandaio
  mosaic and the doors are not drawn.
- The Innocenti's end-bay portals, the foundling window (walled up 1875) and Luigi Fusi's attic (1895) are not drawn.
- The Loggia dei Servi's houses behind and the 1720 walling are generic; the bays at the north-east end (Via dei Servi)
  differ in photographs.
- The tribuna's outside (marble and pietra serena dressing of 1668, Silvani and Malavisti) is plain plaster with stone
  strips; the nave windows and the bell gable's face are *inferred*.
- The side chapels, the Chiostro dei Morti's walks, the wards and cloisters of the Innocenti and the houses over the
  Loggia dei Servi are generic buildings massed from the DSM: refine roofs, windows and cloister arcades from photographs.
- Palazzo Budini Gattai and the square's other corner houses are not modelled.
- The Ferdinando I statue and the two fountains are placeholders.
