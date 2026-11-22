# Firenze Story

Florence in 4D: a city that grows from the Iron Age huts to today, with a playable timeline, a street-level Live mode (people in period dress, markets, calcio storico, the Scoppio del Carro, life on the Arno) and a Sources view that shows the era of every  building and source data.

**Run it:** copy the project locally then double-click `start.bat`. It rebuilds whatever is out of date (textures, Blender props and costumes, city and landscape data), installs the web dependencies the first time, and opens http://localhost:5173.

## Highlights
- **9,067 dated structures** in the 2 × 2 km historic core: 6,352 present-day buildings (OSM + LiDAR 2023), 2,302 demolished buildings and blocks traced from the 1830s land register and the 1843 map, walls, gates, towers, Roman remains and the conjectural Roman grid. Every structure has a start/end year, a confidence level and its sources.
- **Real roofs** reconstructed from the laser scan (fitted planes, ridges and hips), Florentine eaves, chimneys; façades by era (window types, shutters from 1750, shop arches, rusticated palazzi, 19th-century balconies) and landmark materials.
- **The valley around it**: 12 × 12 km of terrain (Fiesole, Arcetri, Bellosguardo), fields, meadows and woods that give way to the city as it is built, ~65,000 trees.
- **The Arno**: river pools stepping down at the San Niccolò and Santa Rosa weirs, dated bridge phases (Roman wooden bridge, the 1333 and 1557 floods, the 1837 suspension bridge, 1944), cargo boats, renaioli, fishermen, ferries, landing stages, ducks, herons, swallows.
- **Live mode**: Roman forum and Mercato Vecchio markets, calcio storico on the axis of Piazza Santa Croce (1530 and today), Scoppio del Carro on Easter Sunday; figures dressed from a costume kit (Roman to modern, liveries, guards).
- **Controls**: drag / right-drag / wheel, **Ctrl + mouse rotate, Ctrl + Shift + mouse move** (no click), W A S D, Q / E, R / F, + / −, N, H for help; Space plays the timeline, ← / → step a year.

## Documentation
| Doc | What's in it |
|---|---|
| [docs/DATA-SOURCES.md](docs/DATA-SOURCES.md) | Register of every dataset: use, period, licence, status, local path |
| [docs/BUILDINGS.md](docs/BUILDINGS.md) | How buildings are made: counts, dating rules, roof reconstruction, façade rules by era, limits |
| [docs/MATERIALS.md](docs/MATERIALS.md) | Every material and pattern (pietra forte, pietra serena, intonaco, coppi, marble, …): definition, use, reference |
| [docs/landmarks/DUOMO.md](docs/landmarks/DUOMO.md) | Landmark models: the Duomo – measurements from LiDAR, dated building phases, materials, review list |
| [docs/landmarks/CAMPANILE-BAPTISTERY.md](docs/landmarks/CAMPANILE-BAPTISTERY.md) | Landmark models: Giotto's Campanile and the Baptistery – measurements, phases, review list |
| [docs/landmarks/PALAZZO-VECCHIO.md](docs/landmarks/PALAZZO-VECCHIO.md) | Landmark model: Palazzo Vecchio – measurements, phases, review list |
| [docs/landmarks/PONTE-VECCHIO.md](docs/landmarks/PONTE-VECCHIO.md) | Landmark model: Ponte Vecchio 1345, shops and Vasari Corridor – measurements, phases, review list |
| [docs/landmarks/SANTA-CROCE.md](docs/landmarks/SANTA-CROCE.md) | Landmark model: Santa Croce – measurements, phases, review list |
| [docs/RIVER-LANDSCAPE.md](docs/RIVER-LANDSCAPE.md) | Terrain, land cover, vegetation, the Arno, weirs, bridges, crossings, river life, early settlement |
| [docs/HISTORY.md](docs/HISTORY.md) | Epochs, urban changes, recurring and one-off events, daily-life vignettes |
| [docs/EVENTS-COSTUMES.md](docs/EVENTS-COSTUMES.md) | Scoppio del Carro, carnival, police patrols, army, costume palette, interactions |
| [docs/SOURCES-SURVEY.md](docs/SOURCES-SURVEY.md) | The initial survey of all candidate sources (open data, LiDAR, maps, cadastre, archaeology, scans) |
| [docs/TECH-STACK.md](docs/TECH-STACK.md) | Technology choices, data pipeline, first-person mode plan |
| [web/README.md](web/README.md) | The web app: run, URL switches, controls, code map |
| [pipeline/README.md](pipeline/README.md) | The data build, step by step |

## Repository
| Path | What |
|---|---|
| `start.bat` | Run the app (calls `pipeline/prepare.py`, then the dev server) |
| `web/` | three.js app (WebGPU with WebGL2 fallback); `public/data` (city, landscape), `public/models` (props, costumes), `public/textures` |
| `pipeline/` | Reproducible build: downloads → city → landscape → textures; `prepare.py` rebuilds what is stale |
| `blender/` | Asset and costume library (`*.blend`) and the scripts that build it (`scripts/build_*.py`) |
| `docs/` | Documentation (table above) |

## License

[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) — free to reuse and adapt with attribution for non-commercial purposes. Commercial use requires prior written permission from the [author](mailto:info@shambix.com).

See [LICENSE](LICENSE) for details.

## Author

Jany Martelli

## Need a custom web / mobile / cloud / AI app developed?

See tech firm [Shambix](https://www.shambix.com/?utm_source=florence-story&utm_medium=referral&utm_campaign=projects&utm_content=github-readme) services or email [info@shambix.com](mailto:info@shambix.com).
