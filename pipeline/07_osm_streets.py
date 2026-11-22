"""OSM street/pedestrian network + squares for the walled city (for walkable navigation graph) -> _dev/data/raw/osm/core_streets.json (ODbL)"""
import json, os, urllib.request, urllib.parse
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
bb="43.755,11.235,43.785,11.275"
q=f"""[out:json][timeout:240];(way["highway"]({bb});way["place"="square"]({bb});way["area:highway"]({bb});way["bridge"]({bb});way["man_made"="bridge"]({bb}););out body geom qt;"""
req=urllib.request.Request("https://overpass-api.de/api/interpreter",data=urllib.parse.urlencode({"data":q}).encode(),headers={"User-Agent":"firenze-story/0.1"})
import time
for url in ["https://overpass-api.de/api/interpreter","https://overpass.kumi.systems/api/interpreter","https://overpass-api.de/api/interpreter"]:
    try:
        req=urllib.request.Request(url,data=urllib.parse.urlencode({"data":q}).encode(),headers={"User-Agent":"firenze-story/0.1"}); d=json.load(urllib.request.urlopen(req,timeout=300)); break
    except Exception as e: print("retry",url,e); time.sleep(10)
json.dump(d,open(os.path.join(ROOT,"_dev","data","raw","osm","core_streets.json"),"w"),ensure_ascii=False); print(len(d["elements"]))
