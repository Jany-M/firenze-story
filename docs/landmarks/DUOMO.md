# Santa Maria del Fiore (Duomo) – landmark model

Status: **v1 for review** (2026-11-22). Script: `blender/scripts/build_duomo.py` → `web/public/models/landmarks/duomo.glb`
(+ `duomo_materials.json`), Blender file `blender/landmarks/duomo.blend`, previews `blender/renders/duomo/`
(`blender -b blender/landmarks/duomo.blend --python blender/scripts/render_landmark.py -- <year> <out> nw,se,north,facade`).

The model replaces the LiDAR shell of *Cattedrale di Santa Maria del Fiore* (and the OHM *Duomo di Firenze*) in the
city mesh; the record stays clickable and gains the source line "Landmark model v1".

## Measurements (Comune LiDAR DSM 2023, 0.5 m; OSM way 43768260)
| Element | Value | How |
|---|---|---|
| Origin | dome centre = lantern top, scene x 138.5 / z −150.5 | DSM maximum (114.1 m above the piazza) |
| Axis | 1.93° south of east | footprint principal axis |
| Façade | 107.5 m west of the dome centre, 44.1 m wide | footprint + DSM step |
| Nave | 4 bays, axis 3.8 m south of the dome centre; aisle walls 30.5 m; clerestory 44.5 m, ridge 47 m, 21 m wide | DSM cross-sections every 5 m |
| Drum | octagon, apothem 26.5 m, visible 41.5–55.5 m | DSM radial profile |
| Dome | springing 58 m at apothem 25.3 m; pointed (*quinto acuto*) arc radius 39.2 m; closing ring at 90.5 m | arc fitted to the DSM profile (±1.5 m) |
| Lantern | 10 m body, 7.5 m cone, ball 2.3 m, cross top ≈ 114 m | DSM + literature |
| Tribunes | 3 half-octagons (apothem 13 m, walls 35 m, roofs to 42 m), 5 chapels each (8.5 m deep, 18 m high) | DSM + footprint (ends at 48 m from the centre) |

## Dated parts (object name `part@from-to`)
| Part | Shown | Basis |
|---|---|---|
| nave bays 1–4 | 1300 / 1340 / 1357 / 1366 → | Arnolfo 1296; Talenti from 1357 (approximate bay dates) |
| nave roof | 1380 → | vaults closed c. 1378–80 |
| octagon base, north and south tribunes | 1380 / 1410 → | tribunes 1380s–1410s |
| east tribune | 1418 → | |
| drum with oculi | 1413 → | drum 1410–13 |
| dome (three stages) | 1420–28, 1428–36, 1436 → | Brunelleschi 1420–36 (consecration 25 March 1436) |
| exedrae (*tribune morte*) | 1445 → | 1439–45 |
| lantern | 1461 → | 1446–61 |
| gilded ball and cross | 1471 → | Verrocchio, 1471 |
| SE gallery (*ballatoio*) | 1515 → | Baccio d'Agnolo, 1507–15, only one face |
| Arnolfo's façade (marble lower third) + rough upper | 1310–1587 | dismantled 1587 |
| bare façade | 1587–1887 | painted only for festivities (not modelled) |
| De Fabris façade | 1887 → | 1876–87 |

## Bare brick before the marble (v1.1)
The structure is brick and pietra forte; the marble revetment followed each part years later (the restoration of the
north side found the white, green and pink marbles set against a terracotta ground; the irregular panel pattern of the
nave flanks reflects a long, interrupted cladding campaign, first two bays possibly before 1357). Every part therefore
has a `<part>_brick@built-clad` phase, then `<part>@clad-` with the revetment:

| Part | Built | Clad | Note |
|---|---|---|---|
| nave bays 1–4 | 1300 / 1335 / 1357 / 1366 | 1350 / 1357 / 1385 / 1395 | side portals decorated 1391–1423 |
| octagon base | 1380 | 1430 | conjectural |
| north / south tribunes | 1412 | 1420 | tribunes 1407–1420 |
| east tribune | 1420 | 1425 | marble corbels of the third tribune ordered 1422 |
| drum | 1413 | 1436 | conjectural (before the consecration) |
| façade | 1310 | lower third only (Arnolfo); upper part never clad until 1887 | |

## Materials
White Carrara marble, green Prato serpentine, red Monsummano/Maremma marble (new textures `marble_*` in
`pipeline/30_textures.py`), dome and roof tiles (coppi texture), bronze doors, gilt copper ball, mosaic lunettes,
rough pietra forte for the unfinished façade. Revetment is real geometry: green frames and red panels stand 2–4 cm
proud of the white wall.

## Reference models checked (not shipped)
- Sketchfab "Cathedral Of Santa Maria Del Fiore" (mohamedhussien, CC-BY 4.0): whole neighbourhood mesh, 2 × 2048² textures – shape check only.
- TurboSquid 2290589 "Florence Duomo photogrammetry" (Maxgood, 42 photos, 100k tris, **editorial use only**): façade relief reference only.
- 3D Warehouse "Florence Duomo" (`.skp`, Google-Earth-era block model): not used.

## Known limits of v1 (review list)
- Revetment pattern is a regular grid per bay; the real panels vary per bay and period (Arnolfo/Talenti vs 19th c.).
- Façade statues, mosaics and the many small pinnacles/aedicules are simplified to niches and gables.
- Windows are drawn on the wall face (no depth); tracery simplified; Porta della Mandorla relief not modelled.
- Dome tiles follow world-projected texture (courses not aligned to each sail); dome oculi and the marble "occhi" of the
  sails are missing; drum gallery only on the SE face (correct) but simplified.
- Campanile and Baptistery are still LiDAR shells (next landmarks).
