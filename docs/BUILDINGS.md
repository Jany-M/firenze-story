# Buildings: how the city is made

All dated structures are built by `pipeline/20_build_city.py` into one mesh (`web/public/data/structures.*`); the
shader (`web/src/scene/city.ts`) shows each one only between its start and end year and draws façades and roofs
from per-building data. Numbers below are from the current build (2026-11-21).

## 1. What is in the model

| Group | Count | Geometry from | Dates from |
|---|---:|---|---|
| Present-day buildings | 6,352 | OSM footprint + LiDAR 2023 (DTM ground, DSM roof) | §2 |
| Demolished buildings (land register, 1830s) | 1,453 | Catasto Generale Toscano parcels vectorised from the Comune WMS | absent on later maps → end year |
| Demolished blocks (1843 map) | 849 | Fantozzi 1843 blocks where the cadastre is not digitised | same |
| Walls, towers, churches | 49 | OpenHistoricalMap | OHM start/end dates |
| Gates | 21 | OSM / OHM | historiography |
| Roman remains (excavated) | 42 groups | Comune archaeology layer | Roman period |
| Roman insulae (conjectural) | 301 | grid inside the castrum walls | 30 BC – 5th c. |
| **Total** | **9,067** | 2.8 M vertices, 1.8 M triangles | |

## 2. Dating (first match wins)
1. Curated landmark list (historiography; e.g. Duomo 1296, dome 1420–36) – *documented*
2. OSM `start_date` – *documented*
3. Wikidata *inception* – *documented*
4. Inside the Risanamento area (Mercato Vecchio & ghetto, rebuilt 1885–95) → 1890 – *inferred*
5. Present on the 1830s cadastre / 1843 map → start estimated by zone: Roman castrum (medieval fabric) 1150 · inside the
   1172 walls 1220 · inside the 1284–1333 walls 1320 · outside 1550 – *conjectural*
6. First on the 1873 map → 1865 · first on the 1937 map → 1905 · otherwise 1955 – *inferred*

Result: 116 documented, 989 inferred, 5,247 conjectural. Conjectural starts are grey in the timeline histogram.

## 3. Roofs (`pipeline/roofs.py`)

| Method | Footprints | How |
|---|---:|---|
| Planes fitted to the scan | 2,673 | Up to 5 planes per footprint fitted to the 0.5 m DSM (RANSAC, ≤ 45°). Gable, hip, pyramid, shed and flat roofs are the lower envelope of their planes, so each plane owns the part of the footprint where it is lowest: exact faces, crisp ridges and hips. Accepted if ≥ 50% of the scan points fit and RMS ≤ 0.95 m. |
| Hip from the scan's heights | 3,552 | When several roofs share one OSM footprint or the scan is noisy: a hip roof over the footprint's oriented rectangle, eaves at the scan's 20th percentile, pitch from its 95th percentile (0.25–0.7); terraces stay flat. |
| Scanned surface | 141 | Landmarks (domes, lanterns, towers, loggias) keep the smoothed LiDAR surface. |
| Synthetic Tuscan hip (~23°) | 2,612 | Demolished buildings and Roman insulae (no scan exists). |
| Flat | 357 | Walls, gates, excavated Roman structures. |

Details on every reconstructed roof:
- **Eaves (*gronda*)**: the roof overhangs ~0.85 m only where the edge faces a street, square or courtyard (never over a neighbour), with a soffit underneath.
- **Chimneys (*comignoli*)**: 1–3 per roof, plastered, with a stone cap.
- **Tiles** run down the slope (roof UVs); colour = the building's median roof colour on the 2017 orthophoto.

## 4. Façades (per-building style written by the pipeline, drawn by the shader)

| Built | Floors (ground / upper) | Window bay | Windows | Ground floor | Shutters |
|---|---|---|---|---|---|
| before 1400 | 4.0–4.8 / 3.9–4.6 m | 3.0–3.8 m | arched (70%) or Gothic two-light; remodelled to framed rectangles between 1480 and 1800 (75% of buildings) | shop arches (55%), rusticated on large palazzi | from 1750 |
| 1400–1600 | palazzo 5.2 / 4.8–5.2, house 4.2 / 3.9–4.3 | 3.3–4.7 m | framed rectangle; arched on half of the palazzi | rusticated (palazzi), shop arches (40%) | from 1750 |
| 1600–1850 | 4.3 / 3.7–4.1 | 3.2–3.6 m | framed rectangle | shop arches (35%) | from 1750 |
| 1850–1945 | 4.6 / 3.9–4.2 | 3.3–3.6 m | framed rectangle; **balconies** with iron railings on street fronts (60% of buildings taller than 10 m; 3-bay balconies on palazzi) | shopfronts (50%) | green / brown |
| after 1945 | 3.8 / 3.1 | 2.9–3.3 m | modern wide | shopfronts | grey rollers |

Plus: churches have no domestic windows; landmark materials (marble bichrome, pietra forte ashlar, bare brick,
plaster with pietra serena pilasters – docs/MATERIALS.md §3); string courses after 1400; stone plinth; rising damp; the
window grid fades into an average tone when it gets smaller than a few pixels (no moiré).

Current counts (present-day buildings): windows 3,614 arched · 1,536 two-light · 845 rectangular · 276 modern · 81 none
(before remodelling) · ground floors 2,864 shop arches · 2,461 plain · 639 shopfronts · 388 rusticated · 318 buildings
with balconies · 64 landmark materials.

## 5. Known limits and next steps
- Façade layouts are rules by era, not surveys of each building: windows do not match the real ones yet.
- Landmarks are footprints + scan + material, not models: the Duomo, Baptistery, Campanile, Palazzo Vecchio, Santa Croce,
  Ponte Vecchio need hand-built or photogrammetric models (Blender, from open photographs and drawings) – planned.
- The Comune's 3D mesh / Digital Twin (requested, docs/DATA-SOURCES.md S08) would give real façade geometry.
- Medieval features not modelled yet: *sporti* (jettied upper floors), tower-house groups, loggias of families.
