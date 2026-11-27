"""Le Murate – convent, prison, quarter (v1).

Run:  python pipeline/47_moderni.py ; blender -b --python blender/scripts/build_murate.py → web/public/models/landmarks/murate.glb
Frame: a along Via Ghibellina from the west corner (OSM relation 1609313), o inwards (north).
Measured (LiDAR 2023 DSM; ground 7.1 m scene): wings of ≈10–17 m round several courtyards; front ≈102 m.
History: the community of recluse women of the Rubaconte bridge (1370s) moved in 1424 to a house on Via Ghibellina, the
monastery of the Santissima Annunziata funded by Giovanni de' Benci (en.wikipedia; FAI); turned into the city's prison
(works from 1845, prison 1883–1985); recovered from 2001 on a plan by Renzo Piano (visittuscany.com, italia.it). The wings
are massed as they stand today; their phases before 1883 are not known in detail (*inferred*: the convent from 1424).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from landmark_kit import *
import landmark_kit as K
from landmark_church import Site, extra_materials
K.reset()
MAT["plaster"] = material("plaster_murate", None, (0.88, 0.8, 0.64), 0.9)
MAT["serena"] = material("pietra_serena", "pietra_serena", (0.5, 0.5, 0.48), 0.7, 0.5)
extra_materials()
NOW = K.NOW
S = Site("murate", "moderni")
def phase(a, o, k): return ("murate", 1424)
def detail(part): return {"roof": "hip", "windows": True, "mat": "plaster"}
print("massing", S.raster(phase, detail=detail))
K.export("murate")
