# Firenze Story

Florence urban history in 4D: a city that grows from the Iron Age huts to today, with a playable timeline, a street-level Live mode (people in period dress, markets, calcio storico, the Scoppio del Carro, life on the Arno) and a Sources view that shows the era of every  building and source data.

## Support this Project if you like it

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-shambix-FFDD00?style=flat-square&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/shambix) or [![Sponsor this on GitHub](https://img.shields.io/github/sponsors/Jany-M?label=Sponsor&logo=githubsponsors&logoColor=white&color=EA4AAA)](https://github.com/sponsors/Jany-M)


## Check out the Live App

🔗 [firenzestory.netlify.app](https://firenzestory.netlify.app/)

[![Netlify Status](https://api.netlify.com/api/v1/badges/87ac5e9f-ddc6-4dc3-a1fc-65b3bea10b28/deploy-status)](https://app.netlify.com/projects/firenzestory/deploys)

## Highlights
- **18,784 dated structures** in a 3.6 × 3.6 km study area (Cascine to Piazza Ferrucci, Ponte alla Vittoria to Ponte San Niccolò): 14,173 present-day buildings (OSM + LiDAR 2023), about 4,200 demolished buildings and blocks traced from the 1830s land register and the 1843 map, walls, gates, towers, Roman remains and the conjectural Roman grid. Every structure has a start/end year, a confidence level and its sources.
- **Real roofs** reconstructed from the laser scan (fitted planes, ridges and hips), Florentine eaves, chimneys; façades by era (window types, shutters from 1750, shop arches, rusticated palazzi, 19th-century balconies) and landmark materials.
- **The valley around it**: 12 × 12 km of terrain (Fiesole, Arcetri, Bellosguardo), fields, meadows and woods that give way to the city as it is built, ~65,000 trees.
- **The Arno**: river pools stepping down at the San Niccolò and Santa Rosa weirs, dated bridge phases (Roman wooden bridge, the 1333 and 1557 floods, the 1837 suspension bridge, 1944), cargo boats, renaioli, fishermen, ferries, landing stages, ducks, herons, swallows.
- **Live mode**: Roman forum and Mercato Vecchio markets, calcio storico on the axis of Piazza Santa Croce (1530 and today), Scoppio del Carro on Easter Sunday; figures dressed from a costume kit (Roman to modern, liveries, guards).
- **Controls**: drag / right-drag / wheel, **Ctrl + mouse rotate, Ctrl + Shift + mouse move** (no click), W A S D, Q / E, R / F, + / −, N, H for help; Space plays the timeline, ← / → step a year.

## Documentation
| Doc | What's in it |
|---|---|
| [docs/encyclopedia/](docs/encyclopedia/) | Reader encyclopedia (landmarks, events, maps & pictures) — built site at `/library/` |
| [CHANGELOG.md](CHANGELOG.md) | Project history (with links to the docs below when a change touches one) |
| [docs/DATA-SOURCES.md](docs/DATA-SOURCES.md) | Register of every dataset: use, period, licence, status, local path |
| [docs/BUILDINGS.md](docs/BUILDINGS.md) | How buildings are made: counts, dating rules, roof reconstruction, façade rules by era, limits |
| [docs/MATERIALS.md](docs/MATERIALS.md) | Every material and pattern (pietra forte, pietra serena, intonaco, coppi, marble, …): definition, use, reference |
| [docs/landmarks/DUOMO.md](docs/landmarks/DUOMO.md) | Landmark models: the Duomo – measurements from LiDAR, dated building phases, materials, review list |
| [docs/landmarks/CAMPANILE-BAPTISTERY.md](docs/landmarks/CAMPANILE-BAPTISTERY.md) | Landmark models: Giotto's Campanile and the Baptistery – measurements, phases, review list |
| [docs/landmarks/PALAZZO-VECCHIO.md](docs/landmarks/PALAZZO-VECCHIO.md) | Landmark model: Palazzo Vecchio – measurements, phases, review list |
| [docs/landmarks/PONTE-VECCHIO.md](docs/landmarks/PONTE-VECCHIO.md) | Landmark model: Ponte Vecchio 1345, shops and Vasari Corridor – measurements, phases, review list |
| [docs/landmarks/SANTA-CROCE.md](docs/landmarks/SANTA-CROCE.md) | Landmark model: Santa Croce – measurements, phases, review list |
| [docs/landmarks/SANTA-MARIA-NOVELLA.md](docs/landmarks/SANTA-MARIA-NOVELLA.md) | Landmark model: Santa Maria Novella – measurements, phases, review list |
| [docs/landmarks/ORSANMICHELE.md](docs/landmarks/ORSANMICHELE.md) | Landmark model: Orsanmichele – measurements, phases, review list |
| [docs/landmarks/BARGELLO.md](docs/landmarks/BARGELLO.md) | Landmark model: Bargello – measurements, phases, review list |
| [docs/landmarks/LOGGIA-DEI-LANZI.md](docs/landmarks/LOGGIA-DEI-LANZI.md) | Landmark model: Loggia dei Lanzi and its statues – measurements, phases, review list |
| [docs/landmarks/MURA.md](docs/landmarks/MURA.md) | Landmark model: the city walls, gates and towers over the eras – sources, dates, review list |
| [docs/landmarks/UFFIZI.md](docs/landmarks/UFFIZI.md) | Landmark model: the Uffizi – measurements, phases, conflicting sources, review list |
| [docs/landmarks/SAN-LORENZO.md](docs/landmarks/SAN-LORENZO.md) | Landmark model: San Lorenzo with its sacristies, cloister, library and Cappella dei Principi |
| [docs/landmarks/MEDICI-RICCARDI.md](docs/landmarks/MEDICI-RICCARDI.md) | Landmark model: Palazzo Medici Riccardi |
| [docs/landmarks/CORRIDOIO-VASARIANO.md](docs/landmarks/CORRIDOIO-VASARIANO.md) | Landmark model: the Vasari Corridor beyond the bridge and Torre dei Mannelli |
| [docs/landmarks/PITTI-BOBOLI.md](docs/landmarks/PITTI-BOBOLI.md) | Landmark models: Palazzo Pitti, the Boboli garden and Forte Belvedere |
| [docs/landmarks/STROZZI.md](docs/landmarks/STROZZI.md) | Landmark model: Palazzo Strozzi |
| [docs/landmarks/REPUBBLICA.md](docs/landmarks/REPUBBLICA.md) | Landmark model: Piazza della Repubblica, the Palazzo dell'Arcone |
| [docs/landmarks/MERCATO-CENTRALE.md](docs/landmarks/MERCATO-CENTRALE.md) | Landmark model: the Mercato Centrale |
| [docs/landmarks/SANTO-SPIRITO.md](docs/landmarks/SANTO-SPIRITO.md) | Landmark model: Santo Spirito with its sacristy, Cenacolo and convent |
| [docs/landmarks/SAN-MARCO.md](docs/landmarks/SAN-MARCO.md) | Landmark model: San Marco, church and former convent |
| [docs/landmarks/CARMINE.md](docs/landmarks/CARMINE.md) | Landmark model: Santa Maria del Carmine, the Corsini chapel and the convent |
| [docs/landmarks/SANTA-FELICITA.md](docs/landmarks/SANTA-FELICITA.md) | Landmark model: Santa Felicita, its bell tower, the nunnery and the column |
| [docs/landmarks/SAN-MINIATO.md](docs/landmarks/SAN-MINIATO.md) | Landmark model: San Miniato al Monte, the bell tower, the Bishops' Palace and the monastery |
| [docs/landmarks/LOGGIA-DEL-PESCE.md](docs/landmarks/LOGGIA-DEL-PESCE.md) | Landmark model: the Loggia del Pesce, in the Mercato Vecchio and in Piazza dei Ciompi |
| [docs/landmarks/ANNUNZIATA.md](docs/landmarks/ANNUNZIATA.md) | Landmark model: Piazza Santissima Annunziata (Innocenti, Loggia dei Servi, the church) |
| [docs/REFINEMENTS.md](docs/REFINEMENTS.md) | Refinement list: the open points of every landmark model, gathered from their review lists |
| [docs/STATUES.md](docs/STATUES.md) | Statues, columns and fountains in the squares: dated placeholders and the list to refine |
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
| `docs/` | Markdown sources (table above); technical site → `web/public/docs/` (`mkdocs.yml`); library → `web/public/library/` (`mkdocs.library.yml`) via [Zensical](https://zensical.org/) |
| `mkdocs.yml` | Zensical / MkDocs config for the technical docs (`/docs/`) |
| `mkdocs.library.yml` | Zensical / MkDocs config for the encyclopedia library (`/library/`) |
| `library-overrides/` | Theme overrides for the library site only |
| `netlify.toml` | Autodeploy on push (skips if neither `web/` nor docs/library configs changed) |

## Development

**Run it locally:** copy the project locally then double-click `start.bat`. It rebuilds whatever is out of date (textures, Blender props and costumes, city and landscape data, docs site), installs the web dependencies the first time, and opens http://localhost:5173.

**Docs in the app:** [http://localhost:5173/docs/](http://localhost:5173/docs/) (technical docs) and [http://localhost:5173/library/](http://localhost:5173/library/) (encyclopedia library — pages at `/library/duomo/`, not `/library/encyclopedia/…`). First time: `python -m venv .venv` then `.venv\Scripts\pip install zensical`.

## License

[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) — free to reuse and adapt with attribution for non-commercial purposes. Commercial use requires prior written permission from the [author](mailto:info@shambix.com).

See [LICENSE](LICENSE) for details.

## Author

Jany Martelli

## Need a custom web / mobile / cloud / AI app developed?

See tech firm [Shambix](https://www.shambix.com/?utm_source=florence-story&utm_medium=referral&utm_campaign=projects&utm_content=github-readme) services or email [info@shambix.com](mailto:info@shambix.com).
