# Biblioteca Nazionale Centrale di Firenze

Model: `blender/scripts/build_biblioteca.py` → `web/public/models/landmarks/biblioteca.glb`, in absolute scene coordinates,
frame from `pipeline/47_moderni.py biblioteca` → `blender/data/moderni.json`; helpers `blender/scripts/landmark_volume.py`.
Register row [M40](../DATA-SOURCES.md#M40). Library page: [/library/biblioteca/](/library/biblioteca/).

The national library on Piazza dei Cavalleggeri, between Santa Croce and the Arno.

Frame: a along the front on the square from the west corner (by the rotunda on Via Magliabechi) to the east corner on
Via Tripoli, 132 m; o inwards (north).

## Measured
| Item | Value | Source |
|---|---|---|
| Outline | ≈ 140 × 43 m with the rotunda | [OSM way 102979687](https://www.openstreetmap.org/way/102979687) |
| Central block | a 58..98, 8.5 m forward of the wings, 20 m | LiDAR 2023 DSM in the frame |
| Towers | a 59..67 and 88.5..96.5, 33 m | DSM |
| Wings | 21–22 m to the roof; fronts 3 m (west) and 1.7 m (east) behind the line | DSM |
| Rotunda | half circle r ≈ 9.6 m on the west end, 27–28 m with its drum | DSM, OSM |
| Behind | distribution hall 18 m; rear blocks 13–20 m round light wells | DSM |

## What the model shows
- **The front**: the central block with the portico of three round arches on columns, the white arms of Florence and of
  Savoy at its corners, the dark name panel (BIBLIOTECA NAZIONALE CENTRALE) and the main cornice.
- **The two towers** ("the architect's ears"): an arched opening on each face, a bronze statue in the front one –
  Dante and Galileo, carved for a square on the Arno that was never made –, a deep cornice and a low tiled roof.
- **The wings** in pietra forte: a plinth, three storeys of windows in stone frames (paired on the main floor), string
  courses, a band of reddish panels under the cornice, low tiled roofs.
- **The rotunda** (the Tribuna dantesca e galileiana) with arched windows, its drum and low dome.
- Plain volumes for the rear blocks; which statue stands in which tower is not drawn (both are figures in bronze).

## Phases
| Years | Part | Basis |
|---|---|---|
| 1911 → 1934 | the works: a low shell (look *inferred*) | first stone 8 May 1911, works stopped by the war ([bncf.cultura.gov.it](https://bncf.cultura.gov.it/en/?p=13946)) |
| 1929 → | the rotunda (Tribuna dantesca e galileiana), the first part finished | [risorgimentofirenze.it](https://risorgimentofirenze.it/la-biblioteca-nazionale-centrale-di-firenze); bncf.cultura.gov.it gives 1930 for its opening |
| 1935 → | the library: moved from the Uffizi in 54 days, opened on 30 October 1935 | bncf.cultura.gov.it |
| 1962 → | Vincenzo Mazzei's west wing towards the Santa Croce cloisters – placed on the north-west block (*inferred*) | risorgimentofirenze.it |

Before 1911 the site was part of the Franciscan convent of Santa Croce; the wing on Corso dei Tintori became Cosimo I's
cavalry barracks in 1572 – hence Piazza dei Cavalleggeri (bncf.cultura.gov.it). The flood of 4 November 1966 filled the
basements and ground floor.
