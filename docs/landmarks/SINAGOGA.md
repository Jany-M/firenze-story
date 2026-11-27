# The Synagogue (Tempio Maggiore Israelitico)

Model: `blender/scripts/build_sinagoga.py` → `web/public/models/landmarks/sinagoga.glb`, in absolute scene coordinates, frame from
`pipeline/47_moderni.py` → `blender/data/moderni.json`; shared helpers `blender/scripts/landmark_volume.py`. Register row [M35](../DATA-SOURCES.md#M35). Library page: [/library/sinagoga/](/library/sinagoga/).

The Great Synagogue of Florence on Via Farini, in its garden.

## Measured
| Item | Value | Source |
|---|---|---|
| Outline | front ≈23 m on the west, the hall ≈46 m deep | [OSM way 102979678](https://www.openstreetmap.org/way/102979678) |
| Heights | the hall's roof ≈24 m, the towers ≈27 m, the dome's top ≈45.7 m above the ground (9.5 m scene) | LiDAR 2023 DSM |

## What the model shows (from photographs)
Photographs (credited on the [library page](/library/sinagoga/)): Txllxt TxllxT 2010, Yair Haklai 2008 and 2019,
Rufus46 2014, Zairon 2023. Heights read in the frame from the DSM (`_dev/tmp/asc_sin.txt`): the building spans
28 m (a -5.5..22.5) and 49 m deep; the arms' round vaults 24–26 m along the middle; the cross arm 25–28 m; the dome's
top 48–50 m.
- **A Greek cross:** front and rear arms under round vaults, a cross arm over the whole width, lower side parts
  (16 m), a half-round apse and low annexes behind.
- **Bands** of white travertine and pink stone of Assisi over every wall.
- **The front** between two towers under a great round arch with a broad archivolt: a portico of three horseshoe
  arches on columns with walnut doors, a frieze, paired horseshoe windows, a three-light window, two single ones and a
  small rose in the arch.
- **The towers:** square and banded to the main cornice with Moorish cresting, an open belfry stage with paired arches,
  a small ribbed copper dome with a gilt ball.
- **The sides:** tall paired horseshoe windows, cresting along the cornices; each arm of the cross ends in the same
  great arch with a three-light window and a rose.
- **The drum** banded, with sixteen horseshoe windows between pilasters and a ring of small arches under its cornice;
  **the dome** in green ribbed copper, top ≈ 48 m with its finial.
- **The garden** before the front: the cast-iron railing on a stone base, the gate between lamp pillars, two palms.

## Phases
| Years | Part | Basis |
|---|---|---|
| 1870 | David Levi leaves his estate for a new synagogue | [en.wikipedia](https://en.wikipedia.org/wiki/Great_Synagogue_of_Florence) |
| 1874–82 | built to the design of Marco Treves, Mariano Falcini and Vincenzo Micheli; inaugurated 24 October 1882 (shown from 1882) | en.wikipedia; [meer.com](https://www.meer.com/it/57700-lo-stile-moresco); [La Nazione](https://www.lanazione.it/firenze/cosa-fare/firenze-la-sinagoga-e-il-museo-ebraico-aprono-le-porte-a-tre-visite-guidate-speciali-528ef532) |

The domes were gilded at first (La Nazione); the model shows the green copper of today.

## Review list
- The carved ornament (the archivolt's patterns, the friezes, the window grilles) is drawn as plain bands; the side buildings of the community are not drawn.
- The works of 1874–82 are not shown; the gilded domes of the first years are not drawn.
