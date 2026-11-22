# Firenze Story — Tech stack (v0.2, 21 Nov 2026)

Lean, DRY, reusable shared modules, standard formats, so other tools can plug in. Versions were checked on 21 Nov 2026; pin versions in `package.json`.

## 1. Runtime (browser)

| Concern | Choice | Why |
|---|---|---|
| 3D engine | **three.js** (current: r186, Sep 2026) with **WebGPURenderer** + **TSL** node materials | WebGPU now ships in Chrome/Edge, Firefox (Windows; macOS ARM from 145) and Safari 26 incl. iOS. WebGPURenderer falls back to WebGL2 automatically, and TSL compiles one shader to both WGSL and GLSL. |
| City streaming | **3DTilesRendererJS** (`3d-tiles-renderer/three`) | Open 3D Tiles; supports glTF `EXT_structural_metadata` / `EXT_mesh_features`, so each building can carry `start_year`/`end_year`/`confidence`; WMS/WMTS/XYZ overlays for historic maps. |
| Time filter | TSL vertex/fragment node reading per-feature metadata | Scrubbing the timeline never reloads geometry. Construction/demolition fades happen on the GPU. |
| Terrain | Quantized-mesh or heightmap tiles built from LiDAR 2023 DTM | Historic Arno banks get variant tiles. |
| Crowds | `InstancedMesh` / instanced skinning (e.g. `@three.ez/instanced-mesh`) or baked Vertex Animation Textures; LOD0 skinned near the camera, impostors far away | Thousands of agents in few draw calls. |
| Navigation | **recast-navigation-js** (`@recast-navigation/three`), WASM Recast/Detour | Navmesh per epoch, DetourCrowd for local avoidance, TileCache for temporary obstacles (stalls, event stands). |
| Simulation | ECS (miniplex or bitECS) in a **Web Worker** | Schedules (bells, markets), smart objects (stall, church door, well), event scripts. |
| Post-processing | three.js TSL post (DOF/tilt-shift, GTAO, bloom, colour grade per era; r186 also has volumetric fog) | Style A (miniature) and style B (cinematic) are mostly camera + post presets over the same scene. |
| Optional | three.js r186 native **Gaussian splats** (PLY/SPZ) | Good for "today" interiors or hero monuments from our own photogrammetry. |
| App shell | Vite + TypeScript, small UI layer (Svelte or plain web components), i18n IT/EN | Static hosting, no backend for v1. |
| Audio | WebAudio + positional audio (bells, market, hooves) | Optional. |

## 2. Data pipeline (offline, reproducible — `pipeline/`)

Python (pyproj, shapely/geopandas, numpy, Pillow) → **Blender headless** (procedural buildings per era, landmark phases, LODs) → **gltf-transform** (meshopt, KTX2) → **3D Tiles 1.1** tileset with metadata.

| Script | Status |
|---|---|
| `01_catalog_comune.py`: full Comune open-data catalogue (1,994 datasets) | done |
| `02_download_comune.py`: 26 CC-BY layers + MANIFEST | done |
| `03_lidar_tiles.py` / `04_lidar_core.py`: LiDAR 2023 DSM/DTM by HTTP range (Deflate64 zip), core 2×2 km as float32 npz | done |
| `05_osm_wikidata_ohm.py`: OSM, OpenHistoricalMap, Wikidata for the walled city | done |
| `06_historic_maps.py`: 11 georeferenced WMS mosaics (1830s cadastre, 1776–1834 Lorenese, 1837–1937 maps, ortho 2017) | done |
| next: `10_buildings_today.py` (OSM + Comune masses + DSM−DTM heights), `11_cadastre_1830s.py` (vectorise raster or use Comune vectors), `12_epochs.py` (start/end years), `20_blender_build`, `30_tiles` | to do |

Coordinates: ETRS89 / UTM 32N (EPSG:25832) as the working CRS. Comune vectors arrive in Monte Mario / Gauss-Boaga (EPSG:3003) and the WMS mosaics in EPSG:3857; everything is reprojected once in the pipeline. In the app, a local ENU origin sits at Piazza della Signoria.

## 2b. What v0.1 actually implements (21 Nov 2026)
- three.js **0.187** WebGPURenderer + TSL; `?gl=1` forces WebGL2, `?lite=1` disables shadows.
- **Data format v0.1:** instead of 3D Tiles, one merged indexed mesh (`structures.*.bin`: 1.88M vertices / 1.37M triangles, ~60 MB) plus per-structure float textures (start, end, ramp, ground, height, cap, flags). Time filtering, construction ramps and caps run in the TSL vertex stage. **3D Tiles** come later, when the area grows beyond the 2×2 km core.
- Facades are procedural (plaster palette, window grid, stone base). Roofs are LiDAR surfaces textured with the 2017 orthophoto blended with tiles. Hero landmarks keep LiDAR shapes; dedicated models come later.
- People: up to 200 placeholder figures (Xbot) on the OSM street graph, filtered by era (castrum before 1172, inside the walls before 1865). Scenes: the Mercato Vecchio market (1000–1885, 6–14 h) and calcio storico (17 Feb 1530, 24 Jun from 1930).
- Gaussian splats: `scene/splats.ts` (native `GaussianSplat`, PLY/SPZ/SPLAT/KSPLAT), with a registry at `public/data/splats.json` and drag-and-drop.

## 3. Later: playable first-person street level

Yes, and the architecture already supports it. The same scene, navmesh and simulation serve three camera modes:

1. **Overview** (isometric/orbit, style A)
2. **Live drone** (low follow-cam, style B)
3. **On foot** (first person or close third person)

What on-foot mode adds:

- **Player controller:** **Rapier** (WASM physics) kinematic character controller with colliders generated from the building and street geometry; pointer-lock mouse/keyboard, gamepad; touch joystick on mobile.
- **Ground-level fidelity:** facade LOD0 only within ~150 m (streamed via 3D Tiles), detail props (stalls, carts, benches, wells, signs), interiors only for hero buildings (Duomo, Orsanmichele, a bottega, a church). Splats or photogrammetry can serve interiors that still exist.
- **Interactions:** a proximity "interact" prompt on smart objects and NPCs. Talk shows short historically grounded dialogue cards (role, guild, era) and buy/look actions at stalls. Following a procession or joining the calcio crowd snaps you into the event choreography as a spectator.
- **Events unfold live:** the same timeline-driven event scripts the drone camera watches. On foot you simply experience them from inside.
- **Optional later:** LLM-driven NPC dialogue grounded in our historical notes, with strict guardrails and a "sources" button. Only if it stays accurate.
- **Performance budget:** at street level everything far away becomes impostors, so you see ~150–300 detailed agents and a city of billboards and instanced LODs beyond.

Nothing in v1 blocks this, provided v1 uses (a) one shared simulation in a worker, (b) collision-ready geometry exported from Blender alongside the visual LODs, and (c) a camera-mode abstraction from day one.

## 4. Not chosen (and why)
- **Unreal/Unity WebGL export:** heavy downloads, weak mobile web, less control over streaming open data.
- **CesiumJS as main engine:** excellent for globe/GIS, but less flexible for stylised post, crowds and game-like interaction. We still use the 3D Tiles format it popularised.
- **Google Photorealistic 3D Tiles as base:** terms forbid deriving content. At most an optional live "today" backdrop.
