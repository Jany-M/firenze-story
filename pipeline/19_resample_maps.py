"""Resample the Web-Mercator WMS mosaics (06_historic_maps.py) onto the 0.5 m UTM grid of the study area -> _dev/data/build/*_05.npy
(cadastre with nearest-neighbour to keep its flat colours; others bilinear). Needed by 20_build_city.py."""
import sys, os, numpy as np, cv2
sys.path.insert(0, os.path.dirname(__file__))
from common import *
os.makedirs(BUILD, exist_ok=True)
for nm in ["catasto_generale_toscano_fabbricati", "1843_PiantaGeometricaDiFirenzeFantozzi", "1873_PiantaDiFirenzeEDintorniIGM",
           "1937_MappaCittaDiFirenze", "Ortofoto2017_COL_2K_CoFi"]:
    r = resample_3857(os.path.join(SRC, "data/raw/historic_maps", nm + ".png"), 0.5, cv2.INTER_NEAREST if "catasto" in nm else cv2.INTER_LINEAR)
    np.save(os.path.join(BUILD, nm + "_05.npy"), r); print(nm, r.shape)
