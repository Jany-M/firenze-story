"""Download Comune di Firenze WMS layers (historic maps, Catasto Generale Toscano 1830s, Catasto Lorenese, orthophoto 2017)
as z17 Web-Mercator tiles over the walled-city bbox and stitch them into PNG mosaics + .pgw world files (EPSG:3857).
Output: _dev/data/raw/historic_maps/<layer>.png (+ .pgw, .json meta).  Licence: CC-BY 4.0 Comune di Firenze (verify per layer)."""
import math, os, io, json, urllib.request, urllib.parse, concurrent.futures as cf
from PIL import Image
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
OUT=os.path.join(ROOT,"_dev","data","raw","historic_maps"); os.makedirs(OUT,exist_ok=True)
S,W,N,E=43.755,11.235,43.785,11.275; Z=17; R=20037508.342789244
LAYERS=["cartestoriche:1837_PiantaTopograficaEVedutaGeneraleDiFirenzeGugliantiniAngioliniRosaspina","cartestoriche:1843_PiantaGeometricaDiFirenzeFantozzi",
 "cartestoriche:1855_PiantaCittaDiFirenzePozzi","cartestoriche:1861_PiantaDiFirenzeESuoiContorni","cartestoriche:1865_1870_MappaCittaDiFirenzeIGM",
 "cartestoriche:1873_PiantaDiFirenzeEDintorniIGM","cartestoriche:1937_MappaCittaDiFirenze","cartestoriche:CatastoLorenese_ComFi",
 "catasto_generale_toscano:catasto_generale_toscano_fabbricati","catasto_generale_toscano:catasto_generale_toscano_particelle","sfondi:Ortofoto2017_COL_2K_CoFi"]
def xt(lon): return int((lon+180)/360*2**Z)
def yt(lat): return int((1-math.log(math.tan(math.radians(lat))+1/math.cos(math.radians(lat)))/math.pi)/2*2**Z)
x0,x1,y0,y1=xt(W),xt(E),yt(N),yt(S); s=2*R/2**Z
def tile(lay,x,y):
    bb=(-R+x*s, R-(y+1)*s, -R+(x+1)*s, R-y*s)
    p={"SERVICE":"WMS","VERSION":"1.1.1","REQUEST":"GetMap","LAYERS":lay,"STYLES":"","SRS":"EPSG:3857","BBOX":",".join(map(str,bb)),
       "WIDTH":256,"HEIGHT":256,"FORMAT":"image/png","TILED":"true","TRANSPARENT":"true"}
    for _ in range(3):
        try: return x,y,Image.open(io.BytesIO(urllib.request.urlopen("https://tms.comune.fi.it/tiles/service/wms?"+urllib.parse.urlencode(p),timeout=60).read())).convert("RGBA")
        except Exception: pass
    return x,y,None
for lay in LAYERS:
    name=lay.split(":")[1]; png=os.path.join(OUT,name+".png")
    if os.path.exists(png): continue
    im=Image.new("RGBA",((x1-x0+1)*256,(y1-y0+1)*256)); miss=0
    with cf.ThreadPoolExecutor(6) as ex:
        for x,y,t in ex.map(lambda a: tile(lay,*a),[(x,y) for x in range(x0,x1+1) for y in range(y0,y1+1)]):
            if t is None: miss+=1
            else: im.paste(t,((x-x0)*256,(y-y0)*256))
    im.save(png,optimize=True)
    px=s/256; ulx=-R+x0*s; uly=R-y0*s
    open(png[:-4]+".pgw","w").write(f"{px}\n0\n0\n{-px}\n{ulx+px/2}\n{uly-px/2}\n")
    json.dump({"layer":lay,"source":"https://tms.comune.fi.it/tiles/service/wms","crs":"EPSG:3857","zoom":Z,"bbox_wgs84":[W,S,E,N],"missing_tiles":miss},open(png[:-4]+".json","w"))
    print("ok",name,im.size,"missing",miss,flush=True)
