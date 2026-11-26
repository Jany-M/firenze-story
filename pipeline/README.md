# pipeline – Firenze Story data build

Python 3.10+ (`pip install -r pipeline/requirements.txt`). Run from the project root. Downloads and intermediate files
go to `_dev/data/` (work cache, not published); results go to `web/public/`. **`python pipeline/prepare.py`** (called by
`start.bat`) re-runs only the steps whose inputs changed; `--force` rebuilds everything that can be rebuilt.

| Step | Script | Output |
|---|---|---|
| 01 | `01_catalog_comune.py` | `_dev/data/catalog/comune_firenze_catalog.csv` (all Comune open datasets) |
| 02 | `02_download_comune.py` | `_dev/data/raw/comune/*.zip` + MANIFEST.csv |
| 03–04 | `03_lidar_tiles.py`, `04_lidar_core.py` (bbox from `common.py`) | `_dev/data/processed/lidar2023/{dsm,dtm}` (HTTP range reads of the 1 GB zips) |
| 05 | `05_osm_wikidata_ohm.py` | `_dev/data/raw/{osm,ohm,wikidata}` |
| 06 | `06_historic_maps.py` | `_dev/data/raw/historic_maps/*.png` (+ .pgw) |
| 07 | `07_osm_streets.py` | `_dev/data/raw/osm/core_streets.json`, `core_water.json` (Arno surface) |
| 08 | `08_wide_area.py` | `_dev/data/raw/wide/` Copernicus DEM tile, Sentinel-2 cloudless mosaic; `osm/wide_water.json`, `wide_weirs.json` |
| 19 | `19_resample_maps.py` | `_dev/data/build/*_05.npy` (historic maps + orthophoto on the 0.5 m grid, ~400 MB) |
| 20 | `20_build_city.py` (+ `roofs.py`) | `web/public/data/structures.*` – all dated structures, one merged mesh, façade styles, roof colours; `footprints.u16` – walkability grid (2 m cells, record id + 1, layer 0 present-day buildings, layer 1 historic; gates and city walls left open). Map tracings lying in today's river bed are skipped (~5 min) |
| 21 | `21_build_env.py` | `web/public/data/{terrain,wide,land_s2,water,weirs,river,bridges,streets,trees,urban,meta}` + map textures (~1 min) |
| 30 | `30_textures.py` | `web/public/textures/*_{col,nrm,rgh}.jpg` – tileable materials (docs/MATERIALS.md) |

Blender assets: `blender/scripts/build_assets.py` (props, river, wildlife, huts) and `build_characters.py` (costume kit)
write to `web/public/models/`; `prepare.py` runs them when a script or a texture changes (Blender found via
`BLENDER_PATH` or the default install folder).

Constants (study area, origin, datum) live in `common.py`: the study area is a square of ±`CORE_HALF` m (1800) around the
origin; steps 04–07 take their bbox from it, so changing it and re-running 04–22 rebuilds a larger or smaller city
(06 re-downloads a map only when the cached mosaic doesn't cover the area). Steps 20–21 read the raw data cache; without it the app
uses the shipped `web/public/data`.

### 22_addresses.py – addresses for the inspector card
Street name history (Stradario storico, H20), today's house numbers (Civici, H21) and the 1808 French numbering (H22)
→ `web/public/data/addresses.json`. Each house number goes to one building: the nearest OSM footprint within 6 m
(landmarks prefer the *piazza* and the lowest black number); records also get their position along the street
(`pos` = metres along, side, frontage) for the strip view, corner buildings also for the cross street, French numbers by distance (16 m). Run by `prepare.py`
when its inputs change. Needs `pyshp`.

### 40_walls.py – geometry for the city walls model
The sixth circle (OHM dated lines, OSM surviving stretches and gate footprints) with LiDAR ground and today's heights →
`blender/data/walls.json`, read by `blender/scripts/build_mura.py` (docs/landmarks/MURA.md). Run by hand after the raw
OSM / OHM data or the LiDAR change; the JSON is kept in the repository.
