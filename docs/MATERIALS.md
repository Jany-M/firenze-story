# Materials and patterns

**Living register.** Every material, texture and procedural pattern used by the app or the Blender library has a row
here: what it represents, where it is defined, where it is used and what it is based on. Add a row whenever one is
created or changed.

One texture set serves everything: `pipeline/30_textures.py` writes tileable maps to `web/public/textures/`; the
Blender library (`blender/scripts/build_assets.py`) binds the same maps; the props are exported without images and
rebuilt in the browser from `web/public/models/materials.json` (written by the same script). Façade, roof, ground
and water patterns are computed in the shaders from per-building data written by the pipeline.

Status: `in-use` · `placeholder` (works, to be replaced) · `planned`.

## 1. Tileable textures (`web/public/textures/<name>_{col,nrm,rgh}.jpg`, 1024², seamless)

| Name | Represents | Used for | Reference | Status |
|---|---|---|---|---|
| `intonaco` | Lime plaster with mottling, fine grain and weathered patches | All plastered façades (tinted per building), chimneys | Florentine *intonaco a calce*; colours from the palette in §3 | in-use |
| `pietra_forte` | Brown-ochre sandstone, rusticated ashlar (*bugnato*), irregular courses | Ground floors of palazzi, medieval stone houses and towers, city walls and gates, window frames before 1450, plinths, weirs | Palazzo Vecchio, Strozzi, Pitti, Bargello | in-use |
| `pietra_serena` | Grey-blue sandstone, finely dressed blocks | Window frames from 1450, string courses, balcony slabs, soffits, colonnettes, pilasters (Brunelleschi style) | Spedale degli Innocenti, San Lorenzo interior | in-use |
| `coppi` | Tuscan curved roof tiles (*coppo* over *embrice*), lichen | Every roof; UVs run down the slope on reconstructed roofs; tinted per building | Roofs of the centre seen from Piazzale Michelangelo / 2017 orthophoto | in-use |
| `lastrico` | Large irregular *pietra forte* paving slabs | Streets and squares from the 1230s (paving campaign) to 1880 | *Lastricato* of the medieval centre | in-use |
| `cotto` | Terracotta brick with lime mortar | Roman remains, bare-brick façades (San Lorenzo, Santo Spirito, Ognissanti) | Roman brick; unfinished church fronts | in-use |
| `wood` | Weathered oak planks | Stalls, carts, stands, boats, landing stages, palisades, benches | – | in-use |
| `canvas` | Undyed linen / hemp weave | Awnings, sails, cargo covers, drapes (tinted) | – | in-use |

## 2. Blender material library (`fs_*`, `blender/firenze_assets.blend`, mirrored in `models/materials.json`)

| Material | Base texture / colour | Used by |
|---|---|---|
| `fs_wood`, `fs_wood_dark` | `wood` (dark: tinted) | stalls, barrels, tables, tribune, Brindellone wheels, boats, scalo, palisade |
| `fs_canvas`, `fs_canvas_red`, `fs_canvas_blu` | `canvas` tinted | stall awnings, tribune drape, navicello sail and cargo |
| `fs_cloth_bolt` | `canvas` tinted purple | bolts of cloth on the cloth stall |
| `fs_terracotta` | `cotto` | oil jars (*orci*) |
| `fs_wicker` | colour | baskets |
| `fs_iron`, `fs_gold`, `fs_red_paint`, `fs_white` | colour (+ metal) | hoops, Brindellone gilding and paint, colombina |
| `fs_produce_*`, `fs_bread` | colour | goods on stalls, tavern food |
| `fs_sand` | colour | renaioli boats' load, sand heaps on the *renai* |
| `fs_thatch`, `fs_daub` | colour | Iron Age hut roof (thatch) and wattle-and-daub wall |
| `fs_feather_white`, `fs_feather_grey`, `fs_duck_brown`, `fs_bird_dark`, `fs_fur_deer` | colour | wildlife |

## 3. City shader materials (`web/src/scene/city.ts`, data from `pipeline/20_build_city.py`)

| Material / pattern | Rule | Based on |
|---|---|---|
| Plaster palette | 8 tones (ochre, cream, pale yellow, sand, grey-green, salmon, …) × `intonaco`, chosen per building | Colours of the centre today (orthophoto, street photos) |
| Medieval stone house | 35% of plaster buildings dated before 1350 show `pietra_forte` instead | Surviving case-torri and medieval fronts |
| `mat 1` pietra forte ashlar | Whole building | Palazzo Vecchio, Bargello, Strozzi, Pitti, Medici Riccardi, Davanzati, Gondi, Antinori, Rucellai, Orsanmichele, Loggia dei Lanzi, towers, gates |
| `mat 2` marble bichrome | White Carrara fields framed by green Prato serpentine bands (2.6 × 3.2 m panels) | Baptistery, Duomo, Campanile, Santa Croce, Santa Maria Novella, San Miniato – *pattern simplified* |
| `mat 3` bare brick | `cotto` | San Lorenzo, Santo Spirito, Ognissanti façades – *whole building, not only the front* |
| `mat 4` plaster + pietra serena pilasters | Pilaster bands at every window bay | Innocenti, Uffizi, Mercato Nuovo |
| Windows | Grid from the pipeline per building: ground-floor height `gf`, floor height `fh`, bay `sp`. Types: framed rectangle · arched (*centinata*) · Gothic two-light (*bifora*, colonnette) · modern wide · none | Era rules in docs/BUILDINGS.md |
| Window frames and sills | `pietra_forte` before 1450, `pietra_serena` after | Florentine practice |
| Glass | Dark interior, sky reflection by view angle, some curtains; glazing bars up close | – |
| Shutters (*persiane*) | Wooden slats, green or brown, from 1750; grey rollers from 1945; closed / half / open per window | Typical of the centre since the 18th c. |
| Ground floors | Plain + doors · rusticated `pietra_forte` · shop arches (*botteghe*) with voussoirs and plank doors · 19th–20th c. shopfronts with sign band; stone plinth | Medieval botteghe, palazzo bases, 19th-c. fronts |
| String course (*marcapiano*) | `pietra_serena` band at the first floor, buildings after 1400 | Renaissance palazzi |
| Weathering | Rising damp at the base, shadow under the eaves | – |
| Roof tiles | `coppi` along the slope, tinted with the building's median roof colour from the 2017 orthophoto (demolished buildings: weathered terracotta palette) | Comune orthophoto 2017 |
| Trim codes | Stone (`pietra_serena`): balcony slabs, soffits, chimney caps · Iron: balcony railings · Plaster: chimneys | – |

## 4. Landscape shader materials (`web/src/scene/environment.ts`)

| Material / pattern | Rule | Based on |
|---|---|---|
| Meadow | Value-noise greens with dry patches | Tuscan pasture |
| Fields | 60 × 22 m parcels on a slightly rotated grid: wheat, ploughed earth, vines (rows), meadow | Pre-modern agrarian landscape around the walls |
| Woods / olive groves | Where Sentinel-2 is dark green today | Sentinel-2 cloudless 2016 (EOX) |
| Beaten earth → paving → today | Urban ground once the 8 m cell is first built; `lastrico` from 1230–1300; orthophoto surfaces 1880–1960 | Urban raster from the dated city (docs/BUILDINGS.md) |
| Gardens and parks: no paving | Paths inside OSM parks and gardens (`leisure=park/garden`: Boboli, the Cascine, Bardini, Semplici, Torrigiani…) are not drawn as street paving, nor are paths, tracks or ways with an unpaved surface tag anywhere (gravel, fine gravel, compacted, ground, grass); only roads with a paved surface cross a park paved. Named squares inside a park stay unpaved. Paving is laid only where there is a road or a square (2026-11-28) | `pipeline/21_build_env.py` (`is_paved`, `PARKS`) |
| Today's countryside | Sentinel-2 colour; built-up land appears 1900–2000 | Sentinel-2 cloudless 2016 |
| Arno water | Green-brown silty body, flowing ripples (normals), sky reflection by Fresnel | – |
| Weir (*pescaia*) | `pietra_forte` crest and slope with animated foam | Pescaia di San Niccolò, Santa Rosa |
| Bridges | Wood · stone · iron (suspension bridge 1837) · concrete, per dated phase | docs/RIVER-LANDSCAPE.md |
| Trees | 4 species shapes (broadleaf, cypress, olive, poplar), two-tone crowns, wind sway | – |

## 5. Costume kit (`blender/scripts/build_characters.py` → `models/costumes.glb`, `hats.glb`)

Garments are cut from the shared Mixamo body, so every animation drives them. Material names are tint slots.

| Slot | Tinted with | Garments |
|---|---|---|
| `cloth_main` | era palette (`clothingFor`) or livery / team colour | tunic, doublet (*farsetto*), robe (*lucco*), bodice, skirt (*gamurra*), beret |
| `cloth_alt` | darker palette colour (team colour for calcio) | hose (*calze*) / trousers, breeches (*brache*), cloak, hood (*cappuccio*), top hat |
| `linen` | off-white | shirt (*camicia*), apron |
| `leather` | browns | shoes / boots, wide-brimmed hat |
| `metal` | steel | helmet (*bacinetto*) |
| Skin | 6 skin tones | the body (Xbot) under the clothes – *placeholder figure* |

Outfits by era and role (`OUTFITS` in `web/src/sim/people.ts`): Roman, medieval, Renaissance (+ elite robe),
early modern, 19th century, modern; calcio 1530 (shirt + breeches + hose) and modern (bare chest, team breeches);
guard, vendor, boatman, fisher. Costume research: docs/EVENTS-COSTUMES.md.

## Planned
- Normal maps on walls (rustication relief) and roofs; per-landmark textures from open photographs.
- Marble patterns traced per building (Baptistery, Campanile, Duomo flanks) instead of the generic panel grid.
- Realistic period characters (MPFB / MakeHuman base, CC0, Mixamo-compatible skeleton) replacing the Xbot body.

## Landmark marbles (v0.4)
| Texture | Stone | Used on |
|---|---|---|
| `marble_white` | Carrara / Lunigiana white marble, fine grey veins | Duomo revetment, ribs, lantern; later Campanile, Baptistery |
| `marble_green` | Prato serpentine (*verde di Prato*) | green frames and bands of the revetment |
| `marble_red` | Monsummano / Maremma red marble | inner panels, façade accents |

Landmark materials are defined by each `blender/scripts/build_<landmark>.py` and exported to
`web/public/models/landmarks/<landmark>_materials.json` (fs_marble_white, fs_marble_green, fs_marble_red, fs_dome_tiles,
fs_roof_tiles, fs_window_glass, fs_bronze, fs_gilt_copper, fs_rough_masonry, fs_lunette_mosaic).

## Street surfaces by era (v0.4)
Ground shader: `web/src/scene/environment.ts`; textures: `pipeline/30_textures.py` (tile size in brackets).

| Years | Surface | Texture | Basis |
|---|---|---|---|
| before Florentia, outside the castrum, unbuilt | beaten earth with ruts, gravel, damp patches; grey-brown (not orange, so it never reads as roof tile), with grass coming through where few walk | `terra` (8 m) + meadow | – |
| c. 30 BC – 550, inside the castrum | earth blocks; cardo, decumanus and a ~36 m street grid in polygonal *basoli* | `basoli` (4 m) | castrum walls from A03; street pattern simplified (*inferred*) |
| 550 – 1237 | beaten earth | `terra` | – |
| 1237 – 1339 | streets paved patch by patch (each 40 m patch has its own year); ~30 % in brick herring-bone | `ammattonato` (2.4 m), `lastrico` (5 m) | first paving in the 13th c.; "all streets paved by 1339" (popular claim, to verify) – *conjectural* |
| 1339 – c. 1860 | irregular pietra forte slabs (*lastrico*); brick streets re-laid in stone 1450–1550 | `lastrico` | *conjectural* timing |
| c. 1840 → today, historic city | rectangular slabs of pietra forte (grey-brown) and pietra serena (blue-grey) in courses, light grey mortar joints; tops dressed with parallel grooves, herring-bone chiselling or punched dots, older slabs worn smooth. By 40 m patch: neat courses ~55 %, older irregular courses ~30 %, square slabs in herring-bone dressing laid on the diagonal ~15 % | `lastrico_filari` (4 m), `lastrico` (5 m), `lastrico_spina` (4 m, rotated 45°) | the centre was relaid in stone 1841–46 (Grand Duchy) and later; appearance from Jany's photographs (Nov 2026) – shares *inferred* |
| quarters built after 1850 | earth / macadam, then from 1925–60 today's ground from the 2017 orthophoto (roads, yards, gardens), lightly tinted with `asfalto` | `terra`, orthophoto (S02) | *inferred* |

Meadows: greens varying at ~10 m and ~1 m, clover hollows, dry straw patches, tufts, scattered flowers and stones.
Buildings still going up (start year plus their estimated ramp) show their walls rising without the roof.

Not yet: sidewalks and curbs, slab rows following each street's direction, drains and gutters, mud and puddles by
season, the urban raster (8 m) is coarse at street edges.

## Ground that is not paved (2026-11-28)
`pipeline/21_build_env.py` writes two more rasters for the ground shader:
- **`wild.u8`** – the open share of parks, gardens, the fort's bastions, river banks and the hillsides. Inside these zones no
  street paving is laid: OSM footpaths are no longer burnt in as street (they had been drawn 10 m wide), and the fort's single
  building outline no longer counts as roofed ground. What shows there is lawn, earth and gravel by the orthophoto's green.
- **`cemetery.u8`** – the cemeteries (`landuse=cemetery`, `amenity=grave_yard` only) with their opening year: Porte Sante 1848,
  the English cemetery 1828, the Jewish cemetery 1777, the Misericordia 1747. From that year grave slabs are drawn on a
  1.5 × 2.8 m grid; the Comune's pedestrian polygons inside them are not paved.
- Street widths now follow the OSM type (primary 6 px of 2 m … footways 1 px); the Comune's circulation polygons whose surface
  code starts with `02` (unpaved) are skipped.
- Asphalt is drawn a mid grey near the stone setts' tone (the texture lifted ×1.5 + 0.11, faint repair patches), on the
  ground and on the lungarni (tint 3.3) – Florence's asphalt is not black.
- After 1850 the street ground is asphalt or stone; the orthophoto colour is used only in yards (it had brought shadows and
  roof edges into the streets as blue-white patches).
- The Comune's surface codes (`acPedFon`, `acVeiFon`) are read on Florence's own data only: the 2017 orthophoto inside
  each polygon (`_dev/tmp/fon_check.py`): 0101 / 0102 / 0505 / 0506 grey (paved, ≤ 4 % green), 0201 / 0202 yellow-grey with
  17 % green (earth and grass, left out).
