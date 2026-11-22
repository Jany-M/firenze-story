# 02 — Data sources for a 4D Florence (research of 21 Nov 2026)

Legend: ✅ confirmed during research (page, metadata or catalogue seen) · 🔎 known source, URL or terms still to be verified · ⚠️ licensing or usage risk.
Licences: always re-check before shipping. Comune di Firenze open data is mostly CC-BY 4.0 / IODL 2.0. Regione Toscana Geoscopio is CC-BY.

---

## 1. Present-day geometry (the "end state" and the base for everything)

| Source | What | Notes |
|---|---|---|
| ✅ **Comune di Firenze – SIT / Open Data** `opendata.comune.fi.it`, `data.comune.fi.it`, downloads at `https://datigis.comune.fi.it/shp/<layer>.zip` | 1:500 *celerimetric* cartography, partly 3D. **Cassone edilizio** (building masses, ID 104/127), **Manufatto edilizio** with extrusion heights, **Particolare architettonico** (columns etc., 3D), **Muro in spessore** (ancient walls and bastions, 3D), road surfaces (vehicular, cycle, pedestrian, 3D), bridges (deck, piers, abutments, 3D), embankments, water bodies, public trees (3D points), green areas | Catalogue: "Catalogo strati informativi geografici", updated 31/12/2025 (PDF on amministrazionetrasparente.comune.firenze.it). Several layers are CC-BY 4.0. This is the best open base anywhere for the centre. |
| ✅ **Comune di Firenze – DTM/DSM** (dati.toscana.it harvests: `dtm_2007`, `dsm-hillshade`) | Terrain and surface models | Use the DTM for ground. DSM minus DTM gives building heights where the cassone lacks them. |
| ✅ **Comune di Firenze Digital Twin** | Whole city scanned by aerial LiDAR plus >80% mobile street scanning; a photorealistic 3D mesh and 3D Tiles/BIM (IFC) in their SDI | **Not clearly public.** Their own docs mention open-data, authenticated and reserved access levels. 🔎 **Action: write to opendata@comune.fi.it / SIT** to request the 3D mesh or point cloud of the centro storico for a cultural project. This would be a huge win for accuracy. |
| ✅ **Regione Toscana – Geoscopio** (`www502.regione.toscana.it/geoscopio/`) | LiDAR DTM/DSM 1×1 m (2007–2011, 2017, 2019–21), CTR 1:2000/1:10000, DB Topografico **unità volumetriche** (buildings with homogeneous height), WMS for orthophotos and **Fototeca** (historic flights, e.g. 1954, 1975–76, 1978…) | WMS: `wmsraster/com.rt.wms.RTmap/wms?map=wmsofc` (ortho), `map=wmsfotogrammi` (photo library). The Cartoteca handles downloads. CC-BY. |
| 🔎 **OpenStreetMap** (Geofabrik Centro Italia extract / Overpass) | Building footprints, `building:levels`, `height`, roof shapes, POIs, `wikidata=` tags, `start_date` | ODbL (share-alike on the derived DB). Good glue layer and wikidata linking. |
| ⚠️ **Google Photorealistic 3D Tiles** | Photoreal mesh of today's Florence | Policy forbids caching, extraction, deriving content, or tracing objects from it. Allowed **only** as an unmodified live backdrop with full attribution, e.g. an optional "2026 real view" toggle. Not usable for stylised or historical rebuilding. |
| 🔎 Cesium ion / OSM Buildings, Mapillary (CC-BY-SA street photos) | Alternative backdrop or texture references | Mapillary is useful for facade texture reference (not reuse). |

## 2. Historical cartography (dating the city fabric)

| Period | Source | Notes |
|---|---|---|
| ~1471–82 | ✅ **Veduta / Pianta della Catena** (attr. Francesco Rosselli). The Berlin Kupferstichkabinett woodcut; a 19th-c. painted copy is in Palazzo Vecchio | A Rijksmuseum print copy is **CC0** on Wikimedia Commons (RP-P-2018-1199). Earliest full city view. It is a perspective view: use for appearance, not for georeferencing. |
| 1584/1594 | ✅ **Buonsignori map** ("Nova pulcherrimae civitatis Florentiae topographia") | Axonometric, accurate enough to georeference. **Harvard Map Collection copy is Public Domain.** Brown University **Florentine Gazetteer** (R. Burr Litchfield): ~750 located items incl. all 225 "Luoghi notabili". |
| 1551/1561/1632 | ✅ **DECIMA** (Univ. Toronto, N. Terpstra; `decima-map.net`) | Census house-by-house georeferenced on Buonsignori: owners, tenants, occupations, rents, plus Savonarola soundscapes. Ideal for **populating** the city (who lived and worked where). Has also explored a 3D Buonsignori city. 🔎 Contact the team for data access and licence. |
| 1427 | ✅ Guido Carocci's 1900 reconstruction of **Mercato Vecchio in 1427** from the Catasto (block and property plan) | Exact plots of the market area demolished in 1885–95. |
| 1783 | ✅ Magnelli / Zocchi city plan | Late-18th-c. state. |
| 1820s–1834 | ✅ **Catasto Generale Toscano (Leopoldino)** via **CASTORE** (Regione Toscana, CASTORE_WMS, CC) + **Comune di Firenze vectorised layers**: *Catasto Leopoldino – Fabbricati / Linee / Mura* (ID 129–131), *Catasto Lorenese* 1776–1834 (ID 132) | **The single most important historical dataset:** every building footprint of pre-industrial Florence, vectorised. Also: Belli, Lucchesi, Raggi, *Firenze nella prima metà dell'Ottocento* (FUP 2022, **open access** on OAPEN), with critical georeferencing. |
| 1865–1900 | ✅ Comune **"Cronologia delle trasformazioni urbane"** (ID 191): cadastral variation maps, late 19th–early 20th c. | Poggi plan, walls demolition, Risanamento. |
| 19th–20th c. | 🔎 IGM historic sheets; RAF/USAAF 1943–45 recon photos (NCAP, Keele / Aerial Reconnaissance Archives); Regione Toscana Fototeca 1954 GAI flight | Pre- and post-war bridge state (bridges blown Aug 1944), post-war expansion. |
| All | ✅ **OpenHistoricalMap** | Already has Florence wall circuits with start/end dates (Roman gates `start_date 0015`, Matildine walls 1087–1172, 1172 circuit gates, etc.), plus state boundaries. Public domain (CC0). Reuse and contribute back. |
| All | 🔎 **Wikidata** SPARQL | Inception (P571), dissolution (P576), coordinates (P625), architect (P84), heritage IDs for every listed building. Gives start/end dates for hundreds of landmarks. |

## 3. Archaeology (Etruscan → Roman → Early Medieval)

| Source | What |
|---|---|
| ✅ **Comune di Firenze – Archeofi** (Ritrovamenti ID 18, Interventi ID 17), **Carte del potenziale archeologico** per period (ID 84–88), **Dati archeologici del centro storico** (ID 193) | Georeferenced finds and per-period potential maps. The backbone for 59 BC–1000 AD layers. |
| ✅ Roman Florentia | Castrum (~square, cardo = via Roma/Calimala, decumanus = via Strozzi/Corso). Hadrianic **theatre under Palazzo Vecchio** (visitable excavations), **amphitheatre** fossilised in the curve of via Torta / Palazzo Peruzzi, baths (via delle Terme), Capitolium/forum (Piazza della Repubblica), Roman bridge near Ponte Vecchio. Comune's "Plastico di Firenze romana"; Cataldi in *Urban Morphology* (centuriation); CNR/Salvini–Faralli *"Archeologia invisibile" a Firenze* (2020, open PDF). |
| ✅ Etruscan / pre-Roman | **Villanovan necropolis** found under Piazza della Repubblica; Etruscan kilns under ex-Cinema Apollo (via Nazionale); **Fiesole** (walls, temple, later Roman theatre and baths) as the Etruscan city on the hill, with Arno-plain settlements (Gonfienti, Sesto F.no tombs). Firenze itself was not an Etruscan city: show the **plain, river crossing, scattered huts, kilns and Fiesole on the hill**. That framing is honest. |
| ✅ Santa Reparata excavations (4th–5th c.) under the Duomo | Early Christian / medieval cathedral. |

## 4. Landmark 3D models and scans

| Source | Notes |
|---|---|
| ✅ **Florence As It Was** (Washington & Lee, G. Bent, D. Pfaff): 27 point clouds, 181 photogrammetry models (Orsanmichele, Badia, S. Croce, S. Lorenzo…) for Florence c. 1500 | 🔎 Ask for collaboration or licence. Academically strong and the right period. Workflow paper in *Heritage Science* (2022). |
| 🔎 Sketchfab (CC-BY photogrammetry of Duomo, Ponte Vecchio, Loggia…), Europeana 3D, Uffizi / Opera del Duomo digital projects | Check per-model licence. Usually best to **remodel heroes in Blender** using scans as reference. |
| ✅ Comune 1:500 "particolare architettonico" + DSM | Dimensional control for heroes. |

## 5. People, costume and daily life (realistic characters)

| Source | Use |
|---|---|
| ✅ **Cesare Vecellio, *Habiti antichi et moderni* (1590/1598)** | ~600 costume plates incl. Florentine nobles, young brides, matrons. Public domain scans: Met Open Access, NYPL, MFA. |
| 🔎 Met / Rijksmuseum / NGA / Europeana / Wikimedia Commons Open Access | Paintings as costume evidence by decade: Ghirlandaio's Tornabuoni chapel (Florentines in 1480s dress), Masaccio, Bronzino portraits, Zocchi 18th-c. *vedute* (street life), Macchiaioli and Alinari/Brogi photos (19th c.). |
| 🔎 Uffizi *Vanished Florence* online exhibition; Archivio Storico del Comune (Mercato Vecchio photos, Alinari ⚠️ licensed) | 19th-c. street scenes before demolitions. |
| ✅ DECIMA census | Real occupations and household distribution, so crowds can be data-driven (e.g. wool workers in S. Frediano, notaries near the Bargello). |
| 🔎 Costume scholarship: Carole Collier Frick, *Dressing Renaissance Florence*; Elisabetta Gnignera; Museo della Moda e del Costume (Palazzo Pitti) | Accuracy review. Ideally hire a costume historian as a consultant. |

## 6. Events and traditions (scripted "live" scenes)

See `03-history-timeline-events.md` for the full calendar. Sources: Comune *"Fiorentini in festa"* (cultura.comune.fi.it), *Traditional Florence* calendar (en.comune.fi.it), chronicles (Villani, Landucci, *Diario fiorentino*), Uffizi online exhibitions.

## 7. Technology references

| Topic | Reference |
|---|---|
| Streaming our own city | **3DTilesRendererJS** (NASA-AMMOS) on three.js; 3D Tiles 1.1 **metadata** to store `start_year`/`end_year` per feature. |
| Crowds | `@three.ez/instanced-mesh` (InstancedMesh2, skinning demo 3k–20k instances), Vertex Animation Textures, the "One Draw Call, Massive Crowd" thread on three.js forum. |
| Isometric-map precedent | cannoneyed.com/projects/isometric-nyc (pipeline write-up), isopolis.city. |
| Historical-3D ethics | DECIMA, *"Respecting Historical Spatial Integrity: Building a Historical 3D Florence and Avoiding the Video Game"* (Disegnarecon 2018). Must-read for showing uncertainty. |

---

## Priority acquisitions (next steps)

1. Download Comune 1:500 layers (cassone edilizio, manufatti, mura, ponti, strade, alberi) + Catasto Leopoldino vectors + archaeology layers. (Scriptable from `datigis.comune.fi.it/shp/`.)
2. Regione Toscana LiDAR DTM/DSM 1 m tiles for the comune.
3. Georeference Buonsignori (Harvard PD scan) and Catena (Rijksmuseum CC0) in QGIS.
4. Email the Comune SIT (3D mesh), DECIMA (census/3D) and Florence As It Was (scans).
5. Wikidata + OHM export of dated landmarks, walls and gates.
