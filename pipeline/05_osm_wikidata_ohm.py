"""Fetch for the study area (walled city 1333, WGS84 bbox):
 - OSM buildings + historic/heritage/religious/amenity features  -> _dev/data/raw/osm/core_osm.json   (ODbL)
 - OpenHistoricalMap all features (walls, gates, dated buildings) -> _dev/data/raw/ohm/core_ohm.json   (CC0)
 - Wikidata items with coordinates in bbox (+inception, dissolution, architect, heritage) -> _dev/data/raw/wikidata/core_items.json (CC0)"""
import json, os, urllib.request, urllib.parse
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
S,W,N,E=43.755,11.235,43.785,11.275   # covers 1333 walls + Oltrarno
UA={"User-Agent":"firenze-story/0.1 (non-commercial cultural project)"}
def post(url,q):
    req=urllib.request.Request(url,data=urllib.parse.urlencode({"data":q}).encode(),headers=UA)
    return json.load(urllib.request.urlopen(req,timeout=300))
def save(sub,name,obj):
    d=os.path.join(ROOT,"_dev","data","raw",sub); os.makedirs(d,exist_ok=True)
    json.dump(obj,open(os.path.join(d,name),"w",encoding="utf-8"),ensure_ascii=False); print(sub,name,len(obj.get("elements",obj.get("results",{}).get("bindings",[]))))
bb=f"{S},{W},{N},{E}"
osm_q=f"""[out:json][timeout:240];(way["building"]({bb});relation["building"]({bb});nwr["historic"]({bb});nwr["heritage"]({bb});
nwr["amenity"~"place_of_worship|marketplace|fountain|theatre"]({bb});way["barrier"="city_wall"]({bb});nwr["wikidata"]({bb}););out body geom qt;"""
for url in ["https://overpass-api.de/api/interpreter","https://overpass.kumi.systems/api/interpreter"]:
    try: save("osm","core_osm.json",post(url,osm_q)); break
    except Exception as e: print("osm fail",url,e)
ohm_q=f"""[out:json][timeout:240];(nwr({bb}););out body geom qt;"""
try: save("ohm","core_ohm.json",post("https://overpass-api.openhistoricalmap.org/api/interpreter",ohm_q))
except Exception as e: print("ohm fail",e)
sparql=f"""SELECT ?item ?itemLabel ?coord ?inception ?dissolved ?architectLabel ?typeLabel ?heritage WHERE {{
 SERVICE wikibase:box {{ ?item wdt:P625 ?coord. bd:serviceParam wikibase:cornerSouthWest "Point({W} {S})"^^geo:wktLiteral.
   bd:serviceParam wikibase:cornerNorthEast "Point({E} {N})"^^geo:wktLiteral. }}
 OPTIONAL {{?item wdt:P571 ?inception}} OPTIONAL {{?item wdt:P576 ?dissolved}} OPTIONAL {{?item wdt:P84 ?architect}}
 OPTIONAL {{?item wdt:P31 ?type}} OPTIONAL {{?item wdt:P1435 ?heritage}}
 SERVICE wikibase:label {{ bd:serviceParam wikibase:language "it,en". }} }}"""
req=urllib.request.Request("https://query.wikidata.org/sparql?"+urllib.parse.urlencode({"query":sparql,"format":"json"}),headers=UA)
save("wikidata","core_items.json",json.load(urllib.request.urlopen(req,timeout=300)))
