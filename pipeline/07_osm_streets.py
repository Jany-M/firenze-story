"""OSM street/pedestrian network + squares for the walled city (for walkable navigation graph) -> _dev/data/raw/osm/core_streets.json (ODbL)"""
import json, os, urllib.request, urllib.parse
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
import sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import wgs_bbox
bb=",".join(map(str,wgs_bbox()))
q=f"""[out:json][timeout:240];(way["highway"]({bb});way["place"="square"]({bb});way["area:highway"]({bb});way["bridge"]({bb});way["man_made"="bridge"]({bb}););out body geom qt;"""
req=urllib.request.Request("https://overpass-api.de/api/interpreter",data=urllib.parse.urlencode({"data":q}).encode(),headers={"User-Agent":"firenze-story/0.1"})
import time
for url in ["https://overpass-api.de/api/interpreter","https://overpass.kumi.systems/api/interpreter","https://overpass-api.de/api/interpreter"]:
    try:
        req=urllib.request.Request(url,data=urllib.parse.urlencode({"data":q}).encode(),headers={"User-Agent":"firenze-story/0.1"}); d=json.load(urllib.request.urlopen(req,timeout=300)); break
    except Exception as e: print("retry",url,e); time.sleep(10)
else: raise SystemExit("streets query failed on all mirrors - core_streets.json not updated")
json.dump(d,open(os.path.join(ROOT,"_dev","data","raw","osm","core_streets.json"),"w",encoding="utf-8"),ensure_ascii=False); print(len(d["elements"]))
# Arno surface for the same bbox (natural=water / water=river / riverbank) -> core_water.json (S07c)
wq=f"""[out:json][timeout:180];(way["natural"="water"]({bb});relation["natural"="water"]({bb});way["waterway"="riverbank"]({bb});relation["waterway"="riverbank"]({bb});way["water"="river"]({bb});relation["water"="river"]({bb}););out body geom;"""
for url in ["https://overpass-api.de/api/interpreter","https://overpass.kumi.systems/api/interpreter"]:
    try:
        req=urllib.request.Request(url,data=urllib.parse.urlencode({"data":wq}).encode(),headers={"User-Agent":"firenze-story/0.1"}); w=json.load(urllib.request.urlopen(req,timeout=300)); break
    except Exception as e: print("retry",url,e); time.sleep(10)
else: raise SystemExit("water query failed on all mirrors - core_water.json not updated")
json.dump(w,open(os.path.join(ROOT,"_dev","data","raw","osm","core_water.json"),"w",encoding="utf-8"),ensure_ascii=False); print("water",len(w["elements"]))
