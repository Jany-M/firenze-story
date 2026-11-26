"""Bring every generated asset up to date before the app starts (called by start.bat).

A step runs only when one of its inputs is newer than its outputs (or an output is missing):
  textures   pipeline/30_textures.py                          -> web/public/textures/*
  props      blender/scripts/*.py + textures                  -> web/public/models/*.glb, blender/*.blend
  city/env   pipeline/common.py, 20_build_city.py, 21_build_env.py (+ raw data in _dev/data) -> web/public/data/*
  docs       mkdocs.yml + docs/*.md + CHANGELOG.md            -> web/public/docs/  (Zensical; optional)
  library    mkdocs.library.yml + docs/encyclopedia + materials -> web/public/library/ (Zensical; optional)
Steps whose tools are missing (Blender, Python packages, raw data, zensical) are skipped with a warning; the app then uses the
files already in web/public.   Usage: python pipeline/prepare.py [--force]
"""
import glob, importlib.util, os, shutil, subprocess, sys

# The build scripts print "…", "×", accented street names: on a Windows console (cp1252) that raises UnicodeEncodeError
# and the step dies. Force UTF-8 for this process and for every child step.
os.environ["PYTHONIOENCODING"] = "utf-8"; os.environ["PYTHONUTF8"] = "1"
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda *p: os.path.join(ROOT, *p)
FORCE = "--force" in sys.argv
PY = sys.executable


def mtime(paths, newest=True):
    ts = [os.path.getmtime(p) for p in paths if os.path.exists(p)]
    if not ts: return 0.0 if newest else -1.0
    return max(ts) if newest else min(ts)


def stale(inputs, outputs):
    outs = [p for pat in outputs for p in glob.glob(pat)]
    if FORCE or not outs: return True
    return mtime([p for pat in inputs for p in glob.glob(pat)]) > mtime(outs, newest=False)


def have(*mods):
    missing = [m for m in mods if importlib.util.find_spec(m) is None]
    if missing: print(f"  ! missing Python packages: {' '.join(missing)}  ->  pip install -r pipeline/requirements.txt")
    return not missing


def run(cmd, label, quiet=False, keep=("ASSET", "Error", "Traceback", "error")):
    """Run a step; quiet=True prints only the lines that matter (Blender is very chatty)."""
    print(f"  > {label}", flush=True)
    if not quiet:
        r = subprocess.run(cmd, cwd=ROOT)
    else:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        for line in (r.stdout + r.stderr).splitlines():
            if any(k in line for k in keep): print("    " + line.strip())
    if r.returncode: print(f"  ! {label} failed (exit {r.returncode}) – keeping the previous files")
    return r.returncode == 0


def blender_exe():
    exe = os.environ.get("BLENDER_PATH") or shutil.which("blender")
    if exe and os.path.exists(exe): return exe
    found = sorted(glob.glob(r"C:\Program Files\Blender Foundation\Blender *\blender.exe"))
    return found[-1] if found else None


print("[prepare] checking generated assets")

# 1. tileable material textures
if stale([J("pipeline", "30_textures.py")], [J("web", "public", "textures", "*_col.jpg")]):
    if have("numpy", "PIL", "scipy"): run([PY, J("pipeline", "30_textures.py")], "textures")
else: print("  = textures up to date")

# 2. Blender asset library (props, costume kit) and landmark models – each script only when its own inputs changed.
# Blender's export is not byte-identical from run to run, so rebuilding everything on any script edit made every .blend/.glb
# show as modified in git without a real change.
TEXS = J("web", "public", "textures", "*_col.jpg")
def blender_target(script):
    stem = os.path.basename(script)[6:-3]                                   # build_<stem>.py
    if stem == "assets": return [script, TEXS], J("web", "public", "models", "materials.json")      # written last = build stamp
    if stem == "characters": return [script], J("web", "public", "models", "costumes.glb")
    return [script, J("blender", "scripts", "landmark_kit.py"), J("blender", "scripts", "landmark_detail.py"), TEXS,
            J("blender", "data", ("pitti" if stem == "boboli" else stem) + ".json")], J("web", "public", "models", "landmarks", stem + ".glb")     # + its geometry data, if any
def needs_build(script):
    ins, out = blender_target(script); return stale(ins, [out])
todo = [s for s in sorted(glob.glob(J("blender", "scripts", "build_*.py"))) if needs_build(s)]
if todo:
    exe = blender_exe()
    if not exe: print("  ! Blender not found (set BLENDER_PATH) – models not rebuilt")
    else:
        for s in todo:
            run([exe, "-b", "--factory-startup", "--python", s], f"blender {os.path.basename(s)}", quiet=True)
else: print("  = Blender props and landmark models up to date")

# 3. city + environment data (needs the raw data cache in _dev/data, see pipeline/README.md)
city_in = [J("pipeline", "common.py"), J("pipeline", "20_build_city.py")]
env_in = [J("pipeline", "common.py"), J("pipeline", "21_build_env.py")]
if not os.path.isdir(J("_dev", "data", "raw")):
    print("  = no raw data cache (_dev/data/raw) – using the shipped web/public/data")
else:
    pkgs = ("numpy", "PIL", "pyproj", "shapely", "cv2", "mapbox_earcut", "zipfile_deflate64", "scipy")
    if stale(city_in, [J("web", "public", "data", "structures.json")]):
        if have(*pkgs):
            if stale([J("pipeline", "19_resample_maps.py")], [J("_dev", "data", "build", "*_05.npy")]):
                run([PY, J("pipeline", "19_resample_maps.py")], "historic map rasters (19_resample_maps.py)")
            run([PY, J("pipeline", "20_build_city.py")], "city (20_build_city.py, ~2 min)")
    else: print("  = city data up to date")
    if stale(env_in, [J("web", "public", "data", "meta.json")]):
        if have(*pkgs): run([PY, J("pipeline", "21_build_env.py")], "environment (21_build_env.py)")
    else: print("  = environment data up to date")
    addr_in = [J("pipeline", "common.py"), J("pipeline", "22_addresses.py"), J("web", "public", "data", "structures.json")]
    if stale(addr_in, [J("web", "public", "data", "addresses.json")]):
        if have("numpy", "pyproj", "shapely", "scipy", "shapefile"): run([PY, J("pipeline", "22_addresses.py")], "addresses (22_addresses.py)")
    else: print("  = addresses up to date")

# 4. documentation site (Zensical → web/public/docs, served by Vite at /docs/)
def sync_docs_changelog():
    """Root CHANGELOG.md uses docs/… links for GitHub; the docs site needs paths without that prefix."""
    src, dst = J("CHANGELOG.md"), J("docs", "changelog.md")
    if not os.path.exists(src):
        return False
    text = open(src, encoding="utf-8").read()
    # GitHub-root links → docs-site-relative (URL and visible label)
    text = text.replace("](docs/", "](").replace("[docs/", "[")
    text = text.replace(
        "](pipeline/README.md)",
        "](https://github.com/Jany-M/firenze-story/blob/main/pipeline/README.md)",
    )
    header = "<!-- Generated from ../CHANGELOG.md by pipeline/prepare.py — edit the root file. -->\n\n"
    open(dst, "w", encoding="utf-8", newline="\n").write(header + text)
    return True


# 4a. materials (docs/materials: images with credits, pipeline/50_materials.py) → web/public/materials for the app's cards
mat_src, mat_dst = J("docs", "materials"), J("web", "public", "materials")
if os.path.exists(J(mat_src, "materials.json")) and stale([J(mat_src, "materials.json")], [J(mat_dst, "materials.json")]):
    shutil.copytree(mat_src, mat_dst, dirs_exist_ok=True, ignore=shutil.ignore_patterns("manifest.json", "*.md"))
    print("  + materials copied to web/public/materials")
else: print("  = materials up to date")

def zensical_exe():
    z = J(".venv", "Scripts", "zensical.exe") if os.name == "nt" else J(".venv", "bin", "zensical")
    if os.path.exists(z):
        return z
    return shutil.which("zensical")


docs_in = [J("mkdocs.yml"), J("CHANGELOG.md"), J("docs", "*.md"), J("docs", "landmarks", "*.md"),
           J("docs", "assets", "*")]
docs_out = [J("web", "public", "docs", "index.html")]
if stale(docs_in, docs_out):
    sync_docs_changelog()
    zensical = zensical_exe()
    if zensical:
        run([zensical, "build", "--clean", "-f", J("mkdocs.yml")], "docs site (zensical)")
    else:
        print("  ! zensical not found – skip docs site (python -m venv .venv && .venv\\Scripts\\pip install zensical)")
else:
    print("  = docs site up to date")

# 4a. the refinement list gathered from the landmark pages' review lists
if stale([J("docs", "landmarks", "*.md"), J("pipeline", "53_refinements.py")], [J("docs", "REFINEMENTS.md")]):
    run([sys.executable, J("pipeline", "53_refinements.py")], "refinement list (53_refinements.py)")
# 4b. fill encyclopedia gallery blocks + events/maps pages (needs materials.json + history.ts)
enc_gen_in = [J("pipeline", "52_encyclopedia.py"), J("docs", "materials", "materials.json"),
              J("web", "src", "data", "history.ts"), J("docs", "encyclopedia", "*.md")]
enc_gen_out = [J("docs", "encyclopedia", "events.md"), J("docs", "encyclopedia", "maps-and-images.md")]
if stale(enc_gen_in, enc_gen_out):
    run([PY, J("pipeline", "52_encyclopedia.py")], "encyclopedia galleries (52_encyclopedia.py)")
else:
    print("  = encyclopedia galleries up to date")

# 4c. library site (docs/encyclopedia → web/public/library at /library/; galleries use /materials/)
def sync_library_assets():
    """Zensical docs_dir is encyclopedia/; copy shared CSS/logo/JS into encyclopedia/assets for the build."""
    src, dst = J("docs", "assets"), J("docs", "encyclopedia", "assets")
    if not os.path.isdir(src):
        return False
    shutil.copytree(src, dst, dirs_exist_ok=True)
    return True


lib_in = [J("mkdocs.library.yml"), J("library-overrides", "*"), J("docs", "encyclopedia", "*.md"),
          J("docs", "materials", "materials.json"), J("docs", "assets", "*")]
lib_out = [J("web", "public", "library", "index.html")]
if stale(lib_in, lib_out):
    zensical = zensical_exe()
    if zensical:
        sync_library_assets()
        run([zensical, "build", "--clean", "-f", J("mkdocs.library.yml")], "library site (zensical)")
    else:
        print("  ! zensical not found – skip library site")
else:
    print("  = library site up to date")

print("[prepare] done")
