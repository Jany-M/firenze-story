"""List every Comune di Firenze dataset harvested on dati.toscana.it (CKAN) -> _dev/data/catalog/comune_firenze_catalog.csv"""
import json, urllib.request, urllib.parse, csv, os, sys
BASE="https://dati.toscana.it/api/3/action/package_search"
out=os.path.join(os.path.dirname(__file__),"..","_dev","data","catalog"); os.makedirs(out,exist_ok=True)
def q(params):
    with urllib.request.urlopen(BASE+"?"+urllib.parse.urlencode(params),timeout=60) as r: return json.load(r)["result"]
fq='harvest_source_title:"comune firenze"'
first=q({"fq":fq,"rows":0}); n=first["count"]; print("datasets:",n)
rows=[]
for start in range(0,n,100):
    for p in q({"fq":fq,"rows":100,"start":start})["results"]:
        for r in p.get("resources",[]) or [{}]:
            rows.append([p["name"],p.get("title",""),p.get("license_id",""),p.get("metadata_modified","")[:10],r.get("format",""),r.get("url",""),(p.get("notes") or "").replace("\n"," ")[:300]])
with open(os.path.join(out,"comune_firenze_catalog.csv"),"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["dataset","title","license","modified","format","url","description"]); w.writerows(rows)
print("resources:",len(rows))
