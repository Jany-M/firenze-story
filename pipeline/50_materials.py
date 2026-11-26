"""Materials: freely licensed maps, drawings, paintings and photographs for the docs encyclopedia and the app's cards.

Input:  docs/materials/manifest.json  – the hand-picked list: {topic, file (Commons file name, or "prefix:…" / "search:…"),
        subjects ["rec:<record name>", "event:<event title>", "map", "history"], caption}
Output: docs/materials/<topic>/<slug>.jpg (1280 px), docs/materials/<topic>/thumbs/<slug>.jpg (360 px),
        docs/materials/materials.json – the same list resolved, with author, licence, date and the Commons page.
Only public-domain and CC-licensed files are taken (the licence is checked again here). Files already downloaded are kept.
Run by hand (network); prepare.py copies docs/materials to web/public/materials for the app.
"""
import os, sys, json, re, time, urllib.request, urllib.parse, io
from PIL import Image
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MAT = os.path.join(ROOT, "docs", "materials")
UA = {"User-Agent": "firenze-story/0.4 (open-source research project; https://github.com/Jany-M/firenze-story)"}
OK = re.compile(r"public domain|^pd|cc0|cc by|cc-by|no restrictions", re.I)

def clean_date(t):
    """Drop the Wikidata date code Commons appends to template dates ("circa 1617date QS:P571,+1617-…")."""
    return re.sub(r"\s*date QS:\S*", "", t or "").strip()

def api(**p):
    p.update(format="json", formatversion=2)
    for k in range(4):
        try: return json.load(urllib.request.urlopen(urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(p), headers=UA), timeout=60))
        except Exception as e: print("  retry", e); time.sleep(3 * (k + 1))
    raise SystemExit("Commons API unreachable")
def fetch(url):
    for k in range(4):
        try: return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
        except Exception as e: print("  retry", e); time.sleep(5 * (k + 1))
    raise SystemExit("download failed: " + url)
strip = lambda h: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", h or "")).strip()
def slug(s): return re.sub(r"[^a-z0-9]+", "-", re.sub(r"\.(jpe?g|png|tiff?)$", "", s.lower()))[:70].strip("-")

def resolve(f):
    if f.startswith("prefix:"):
        r = api(action="query", list="allimages", aifrom=f[7:], aiprefix=f[7:], ailimit=1)
        hits = r["query"]["allimages"]; return hits[0]["name"].replace("_", " ") if hits else None
    if f.startswith("search:"):
        r = api(action="query", generator="search", gsrsearch=f[7:], gsrnamespace=6, gsrlimit=8, prop="imageinfo", iiprop="extmetadata")
        for p in sorted(r.get("query", {}).get("pages", []), key=lambda p: p.get("index", 0)):
            lic = p["imageinfo"][0].get("extmetadata", {}).get("LicenseShortName", {}).get("value", "")
            if OK.search(lic) and not p["title"].lower().endswith((".pdf", ".djvu", ".svg")): return p["title"][5:]
        return None
    return f

man = json.load(open(os.path.join(MAT, "manifest.json"), encoding="utf-8"))
old = {m["src_file"]: m for m in json.load(open(os.path.join(MAT, "materials.json"), encoding="utf-8"))} if os.path.exists(os.path.join(MAT, "materials.json")) else {}
out = []
for m in man:
    if m["file"].startswith("local:"):      # our own image already in docs/materials (e.g. maps/circles-of-walls.jpg)
        rel = m["file"][6:]; im = Image.open(os.path.join(MAT, rel)).convert("RGB"); d, f = os.path.split(rel)
        os.makedirs(os.path.join(MAT, d, "thumbs"), exist_ok=True); t = im.copy(); t.thumbnail((360, 360))
        t.save(os.path.join(MAT, d, "thumbs", f), quality=78, optimize=True)
        out.append({"topic": m["topic"], "subjects": m["subjects"], "caption": m["caption"], "src_file": m["file"], "img": rel,
                    "thumb": f"{d}/thumbs/{f}", "w": im.width, "h": im.height, "author": m["author"], "date": clean_date(m.get("date", "")),
                    "license": m["license"], "license_url": m.get("license_url", ""), "page": m.get("page", ""), "credit": ""})
        continue
    name = resolve(m["file"])
    if not name: print("!! not found", m["file"]); continue
    if name in old and os.path.exists(os.path.join(MAT, old[name]["img"])):
        out.append({**old[name], "topic": m["topic"], "subjects": m["subjects"], "caption": m["caption"], "date": clean_date(old[name].get("date", ""))}); continue
    r = api(action="query", titles="File:" + name, prop="imageinfo", iiprop="extmetadata|url|size", iiurlwidth=1280)
    p = r["query"]["pages"][0]
    if "imageinfo" not in p: print("!! no info", name); continue
    ii = p["imageinfo"][0]; md = ii.get("extmetadata", {}); lic = md.get("LicenseShortName", {}).get("value", "")
    if not OK.search(lic): print("!! licence", lic, name); continue
    s = slug(name); d = os.path.join(MAT, m["topic"]); os.makedirs(os.path.join(d, "thumbs"), exist_ok=True)
    im = Image.open(io.BytesIO(fetch(ii.get("thumburl") or ii["url"]))).convert("RGB")
    im.thumbnail((1280, 1280)); im.save(os.path.join(d, s + ".jpg"), quality=82, optimize=True)
    t = im.copy(); t.thumbnail((360, 360)); t.save(os.path.join(d, "thumbs", s + ".jpg"), quality=78, optimize=True)
    out.append({"topic": m["topic"], "subjects": m["subjects"], "caption": m["caption"], "src_file": name,
                "img": f"{m['topic']}/{s}.jpg", "thumb": f"{m['topic']}/thumbs/{s}.jpg", "w": im.width, "h": im.height,
                "author": strip(md.get("Artist", {}).get("value"))[:160] or "unknown", "date": clean_date(strip(md.get("DateTimeOriginal", {}).get("value")))[:60],
                "license": lic, "license_url": md.get("LicenseUrl", {}).get("value", ""), "page": ii["descriptionurl"],
                "credit": strip(md.get("Credit", {}).get("value"))[:200]})
    print(f"ok {m['topic']:10s} {lic:14s} {name[:70]}")
    time.sleep(0.5)
json.dump(out, open(os.path.join(MAT, "materials.json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
print(len(out), "materials")
