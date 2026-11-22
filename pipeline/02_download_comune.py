"""Download selected Comune di Firenze open-data layers (CC-BY 4.0) listed in _dev/data/catalog/comune_firenze_catalog.csv
-> _dev/data/raw/comune/<slug>.<ext>, writes _dev/data/raw/comune/MANIFEST.csv (title, url, licence, bytes, sha1, date)."""
import csv, os, re, hashlib, urllib.request, datetime, sys
ROOT=os.path.join(os.path.dirname(__file__),"..")
OUT=os.path.join(ROOT,"_dev","data","raw","comune"); os.makedirs(OUT,exist_ok=True)
WANT={ # exact catalogue titles -> register id
 "Antropico - Cassone Edilizio":"S01","Antropico - Manufatto Edilizio":"S02","Antropico - Particolare Architettonico":"S02",
 "Antropico - Muro o Divisione in Spessore":"S02","Antropico -  Ponte/Viadotto/Cavalcavia (sede viaria)":"S02",
 "Antropico - Ponte/Viadotto/Cavalcavia (sapplette)":"S02","Antropico - Argini con geometria PolygonZ":"S02",
 "Antropico - Muro di Sostegno e Ritenuta del Terreno":"S02","Antropico - Localizzazione di Manufatto Edilizio o Arredo/Igiene Urbana":"S02",
 "Viabilità - Area di Circolazione Pedonale con geometria PolygonZ":"S02","Viabilità - Area di Circolazione Veicolare con geometria PolygonZ":"S02",
 "Aree stradali":"S02","Corso d'acqua (Sistema delle Acque)":"S02","Orografia - Punti Quotati":"S03","Orografia - Scarpate":"S03",
 "Alberi":"S06","Accessori - Siti Alberi":"S06","Dati archeologici del centro storico di Firenze":"A03",
 "Perimetrazione centro storico UNESCO":"C01","Stradario storico":"C02","Mercati Storici":"C03","Esercizi storici":"C04",
 "Quartieri Storici":"C05","Fontane monumentali":"C06","Architettura e Monumenti":"C07",
 "Targhe delle alluvioni storiche verificatesi nella città di Firenze":"C08"}
rows=list(csv.DictReader(open(os.path.join(ROOT,"_dev","data","catalog","comune_firenze_catalog.csv"),encoding="utf-8")))
man_path=os.path.join(OUT,"MANIFEST.csv"); done={r["file"] for r in csv.DictReader(open(man_path,encoding="utf-8"))} if os.path.exists(man_path) else set()
man=open(man_path,"a",newline="",encoding="utf-8"); w=csv.writer(man)
if not done: w.writerow(["register_id","title","file","url","license","bytes","sha1","downloaded"])
picked={}
for r in rows:
    t=r["title"].strip()
    if t in WANT and r["format"].upper() in ("SHP","ZIP","GEOJSON"):
        # prefer SHP zip, then GeoJSON
        rank={"SHP":0,"ZIP":1,"GEOJSON":2}[r["format"].upper()]
        if t not in picked or rank<picked[t][0]: picked[t]=(rank,r)
for t,(rank,r) in picked.items():
    slug=re.sub(r"[^a-z0-9]+","_",t.lower()).strip("_")[:60]
    ext="geojson" if r["format"].upper()=="GEOJSON" else "zip"
    fn=f"{slug}.{ext}"
    if fn in done: print("skip",fn); continue
    try:
        req=urllib.request.Request(r["url"],headers={"User-Agent":"firenze-story/0.1 (cultural non-commercial project)"})
        data=urllib.request.urlopen(req,timeout=600).read()
        open(os.path.join(OUT,fn),"wb").write(data)
        w.writerow([WANT[t],t,fn,r["url"],r["license"],len(data),hashlib.sha1(data).hexdigest(),datetime.date.today().isoformat()]); man.flush()
        print("ok",fn,len(data))
    except Exception as e: print("FAIL",t,e)
missing=set(WANT)-set(picked); print("not in catalogue:",missing)
