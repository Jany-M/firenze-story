# Palazzo Pitti, the Boboli garden and Forte Belvedere

Two models, both in absolute scene coordinates, geometry from `pipeline/42_pitti.py` → `blender/data/pitti.json`:
- `blender/scripts/build_pitti.py` → `web/public/models/landmarks/pitti.glb` – the palace, its rondò wings and the Palazzina
  della Meridiana, register row [M20](../DATA-SOURCES.md#M20);
- `blender/scripts/build_boboli.py` → `web/public/models/landmarks/boboli.glb` – the amphitheatre, the Grotta del
  Buontalenti, the Kaffeehaus, the Neptune basin and Forte Belvedere with its palazzina, register row [M21](../DATA-SOURCES.md#M21).

Library page: [/library/pitti-boboli/](/library/pitti-boboli/). The Vasari Corridor reaches the garden by the Grotta del
Buontalenti ([CORRIDOIO-VASARIANO.md](CORRIDOIO-VASARIANO.md)).

## Measured
| Item | Value | Source |
|---|---|---|
| Piazza front | ≈201 m, 23 bays of ≈8.74 m; central 13 bays on three storeys (roof ≈38.5 m above the piazza), five bays a side on two (≈26.5 m) | LiDAR 2023 DSM along the front; 23 window axes – [Storia di Firenze (D. Smalzi)](https://www.storiadifirenze.org/wp-content/uploads/kalins-pdf/singles/novembre-1618-la-progettazione-e-l%25e2%2580%2599ampliamento-di-palazzo-e-piazza-pitti.pdf) |
| Front block | ≈24 m deep | DSM |
| The rest of the palace | courtyard wings, garden front, the two rondò, the Meridiana: buildings massed from the 1 m DSM raster (`blender/scripts/landmark_mass.py`): hipped roofs at the measured ridge heights, walls, eaves cornices and windows, from a 1 m raster of the DSM inside the OSM outline | [OSM relation 1637338](https://www.openstreetmap.org/relation/1637338), [relation 7071160](https://www.openstreetmap.org/relation/7071160), LiDAR |
| Piazza | 17.0 m (scene), 57 m a.s.l. at the palace; it falls ≈9 m over ≈100 m to the street along the houses opposite | app terrain, sampled in the palace's frame (`ground` in `pitti.json`) |
| Amphitheatre | tiers from r ≈30 to 41 m round the obelisk, following the ground | [OSM way 473825738](https://www.openstreetmap.org/way/473825738), app terrain |
| Forte Belvedere | wall tops from the DSM along the OSM outline; palazzina ≈26 × 20 m, ≈17 m (*inferred* from the LiDAR shell) | [OSM way 24879633](https://www.openstreetmap.org/way/24879633) |

## What the models show (from photographs)
Photographs used (credited in `docs/materials` and on the [library page](/library/pitti-boboli/)): the front (Yair Haklai,
2019), a rondò wing (Ricardalovesmonuments, 2021), Ammannati's courtyard and a kneeling window (Sailko 2007, Francesco Bini
2022), the Meridiana (Sailko, 2007), Giusto Utens's lunette (c. 1599), the amphitheatre (Sailko, 2010), the Grotta del
Buontalenti (Sailko, 2013), the Kaffeehaus (Rufus46, 2014), the Neptune basin (Txllxt TxllxT, 2010), the fort's palazzina
(Sailko, 2013).

- **Front:** rough pietra forte rustication over the whole front, large round-arched windows under rusticated voussoirs on the
  piano nobile and (central 13 bays) on the second floor, a balustraded balcony along each floor, the central portal under a
  rusticated arch, small barred windows in blind arches on the ground floor. The two lateral doors of the 1458 front become
  kneeling windows with a pediment and consoles from 1560.
- **Courtyard (Ammannati):** arches on banded, rusticated columns, round-headed windows on the two upper orders, entablatures.
- **The rondò (both ends of the front):** a curved arcade of seven arches (≈3 m wide on 1.9 m piers) in rusticated stone,
  the yellow-plastered back wall of the loggia with its doors and barred windows, an end arch, rustication and a cornice on
  the outer face, a balustraded terrace on top; the north one mirrors the south one.
- **The end pavilions (1640):** the two-storey blocks where the low wings meet the rondò, with arched windows.
- **The forecourt on the hill:** the palace stands on a rise; the paved forecourt in front of it is held by battered walls of
  rough blocks with a stone coping, iron rails and bollards, which die into the ground where it reaches the forecourt's level
  (segments under 2.2 m are left out). The piazza is one sloping surface from the palace down to the street in front of the
  houses opposite, plain grey paving (no texture).
- **Rear, Meridiana:** massing from the LiDAR (pietra forte; the Meridiana plastered), tiled roofs.
- **Amphitheatre:** six stone tiers following the slope (a grass slope before 1599), the arena in gravel, edicules with
  statues and urns along the top (from 1634), the Egyptian obelisk (1790) and the granite basin.
- **Grotta del Buontalenti:** plastered block, the grotto mouth between two Tuscan columns, rock work (*spugne*) above.
- **Kaffeehaus:** green octagonal pavilion with a copper dome and lantern, side terraces (simplified).
- **Neptune basin:** stone rim, water, the rock in the middle with the statue.
- **Forte Belvedere:** sloping walls along the star outline with a cordon and a parapet, the terrace, and the white
  three-storey palazzina with stone quoins and windows on the outer axes.

## Phases
| Years | Part | Basis |
|---|---|---|
| 1458 | Luca Pitti's palace: 7 bays, 3 storeys, three doors | [it.wikipedia](https://it.wikipedia.org/wiki/Palazzo_Pitti) (Luca Fancelli; work stopped 1465, the family lived there from 1469) |
| 1549–50 | bought by Eleonora di Toledo; the garden begun by Tribolo | it.wikipedia ([Palazzo Pitti](https://it.wikipedia.org/wiki/Palazzo_Pitti), [Giardino di Boboli](https://it.wikipedia.org/wiki/Giardino_di_Boboli)) |
| 1560 | Ammannati: rear wings and courtyard, the lateral doors made into kneeling windows | it.wikipedia: 1558–1570, courtyard "1560"; [Lancaster University notes](https://www.lancaster.ac.uk/fass/ruskin/empi/notes/cpitti01.htm) |
| 1565 | the palazzina later inside the fort (*inferred*: "probably the 1560s", attributed to Ammannati) | [it.wikipedia: Forte di Belvedere](https://it.wikipedia.org/wiki/Forte_di_Belvedere) |
| 1583–93 | Grotta del Buontalenti (shown from 1583) | it.wikipedia (Boboli) |
| 1590–91 | Forte Belvedere, Buontalenti (first stone 28 October 1590) | it.wikipedia (Forte di Belvedere) |
| 1599 | stone tiers in the amphitheatre | it.wikipedia (Boboli) |
| 1618 / 1631 | the front lengthened by three bays to the north (Giulio Parigi) and to the south (Alfonso Parigi) | [en.wikipedia](https://en.wikipedia.org/wiki/Palazzo_Pitti) |
| 1640 | the outer five bays a side: 23 bays in all (*inferred* year, "in the 1640s"); the end pavilions, the forecourt's walls and the sloping piazza with them (*inferred*) | Storia di Firenze (D. Smalzi) |
| 1634 | edicules and urns on the amphitheatre (Parigi, c. 1630–34; inaugurated 1637) | it.wikipedia (Boboli) |
| 1765 | rondò delle Carrozze (south), Giuseppe Ruggieri | 1764–65 / 1764–66 – [Firenze University Press](https://books.fupress.com/isbn/9791221505276), [Flore (UniFi)](https://flore.unifi.it/handle/2158/1056695) |
| 1776 | Kaffeehaus (Zanobi del Rosso); Palazzina della Meridiana begun | it.wikipedia (Boboli, Palazzo Pitti) |
| 1777–78 | Neptune basin (statue by Stoldo Lorenzi, 1571) | it.wikipedia (Boboli) |
| 1783 | rondò di Bacco (north) – *inferred* | Lancaster notes: wings 1764–1783 |
| 1790 | the obelisk in the amphitheatre | it.wikipedia (Boboli) |
| 1840 | the granite basin by the obelisk – *inferred* | – |

The city records of the Kaffeehaus, the palazzina and the amphitheatre (all "1955") and of the Grotta del Buontalenti ("1220")
were dated by the 1937 map test; the models replace them with the dates above.

## Standing on the ground
Every piece is set on the app's own terrain (`web/public/data/terrain.f32`, 4 m grid), not on the raw DTM, so nothing sinks
or floats: the palace front stands on the highest point of the piazza along it (17.6 m) with its base 2 m below; the
courtyard on its own ground; the amphitheatre's tiers 0.35 m above the ground at each radius and the arena just above its
highest point; the Grotta del Buontalenti's front on the ground of its own wall; the Kaffeehaus, the palazzina and the
Neptune basin with their floor on the uphill side and a plinth down to the lowest ground; the fort's parapet 1.1 m above
the ground inside the walls and its scarp starting below the ground outside.

## Where the sources disagree
- **When the front reached 23 bays.** it.wikipedia has Giulio Parigi starting in 1618 and Alfonso finishing in 1631;
  en.wikipedia has the south bays only *begun* in 1631; Daniela Smalzi (Storia di Firenze) has the 23 axes reached by Alfonso
  "in the 1640s". The model shows the north bays from 1618, the south ones from 1631 and the low outer wings from 1640.
- **The rondò.** The Lancaster notes give 1764–1783 for both wings by Giuseppe Ruggieri; the recent studies of Pietro Matracchi
  (Firenze University Press) date the south rondò 1764–66 and leave the north one to Poccianti's 19th-century work.
  it.wikipedia credits Poccianti with the "rondò di testata" after the Lorraine returned. The model: south 1765, north 1783.
- **Forte Belvedere:** 1590–91 on it.wikipedia; many guides say 1590–95.
- **The Ammannati works:** 1558–70 (staircase, wings) with the courtyard dated 1560 on it.wikipedia; no single year elsewhere.

## Review list
- The rear of the palace and the Meridiana are generic buildings massed from the DSM (hipped roofs, cornices, plain windows);
  Poccianti's ashlar is not drawn. The rondò now have their arcades and terraces; the number of arches (seven) is from the
  photograph of the south wing, to check on the north one.
- The forecourt's walls follow a traced line; their height comes from the ground model (4 m), so where the ground is smooth
  the walls are low or missing. The date of the forecourt (shown with the 1640 wings) is *inferred*.
- The garden front (the courtyard's terrace towards the amphitheatre, the Fontana del Carciofo c. 1640) is massing only; the
  courtyard's orders are drawn only on the sides where the wing behind stands (the DSM 4 m back), so the low terrace side is open.
- Boboli pieces not modelled yet: the Isolotto (1618), the Viottolone (cypresses 1637), the Limonaia (c. 1778), the Casino del
  Cavaliere (c. 1700) and the Giardino del Cavaliere (1790–93), the original place of the Fontana dell'Oceano.
- The Kaffeehaus's long side wings are not drawn (only the domed pavilion).
- Pitti front: balconies, the kneeling windows' consoles and the central portal are generic; compare with photographs bay by bay.
- The fort's walls are vertical faces from the DSM; the batter, the bastion corners and the entrance with the Medici arms are
  simplified; the palazzina's size is inferred.
