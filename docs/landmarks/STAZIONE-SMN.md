# Santa Maria Novella station

Model: `blender/scripts/build_stazione_smn.py` → `web/public/models/landmarks/stazione_smn.glb`, in absolute scene coordinates, geometry from
`pipeline/47_moderni.py` → `blender/data/moderni.json`. Register row [M33](../DATA-SOURCES.md#M33). Library page: [/library/stazione-smn/](/library/stazione-smn/).

The passenger building of Florence's main station, on Piazza della Stazione behind the apse of Santa Maria Novella.

## Measured
| Item | Value | Source |
|---|---|---|
| Outline | the whole complex (two outer rings, one courtyard) | [OSM relation 3324492](https://www.openstreetmap.org/relation/3324492) |
| Front | ≈71 m on the piazza; ground 8.3 m (scene) | OSM, app terrain |
| Heights | the entrance gallery ≈6 m, the ticket hall ≈15 m | LiDAR 2023 DSM (axis profile) |

## What the model shows
- The whole building massed from the DSM in pietra forte with flat roofs (`landmark_mass.py`, no punched windows).
- Along the front, the deep entrance canopy on slender piers and the glazed doors behind it.
- Over the entrance, the glazed "cascade" in six steps from the hall's roof down to the gallery.

## Phases
| Years | Part | Basis |
|---|---|---|
| 1848 | the Maria Antonia station, nearer the church (not drawn) | [en.wikipedia](https://en.wikipedia.org/wiki/Firenze_Santa_Maria_Novella_railway_station) |
| 1932 | national competition won by the Gruppo Toscano (Baroni, Berardi, Gamberini, Guarnieri, Lusanna, led by Giovanni Michelucci) | [area-arch.it](https://www.area-arch.it/en/?p=18246), [visittuscany.com](https://www.visittuscany.com/it/attrazioni/stazione-di-santa-maria-novella/) |
| 1933–35 | built; inaugurated 30 October 1935 (shown from 1935) | [arttrav.com](https://www.arttrav.com/florence/santa-maria-novella-michelucci/) |

## Where the sources disagree
- **Built 1932–34 or 1933–35:** manchesterhistory.net gives 1932–1934; the Michelucci foundation and the inauguration give 1935.

## Review list
- No free photograph found yet for the library page (the ones online are copyrighted); the front's details (the lettering,
  the clock, the long bands of glass) are not drawn.
- The Maria Antonia station (1848–1930s) and Michelucci's Palazzina Reale (white marble, 1935) are not modelled.
- The platforms' roofs and the train shed come from the DSM as flat masses.
