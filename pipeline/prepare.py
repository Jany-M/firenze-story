"""Bring every generated asset up to date before the app starts (called by start.bat).

A step runs only when one of its inputs is newer than its outputs (or an output is missing):
  textures   pipeline/30_textures.py                          -> web/public/textures/*
  props      blender/scripts/*.py + textures                  -> web/public/models/*.glb, blender/*.blend
  city/env   pipeline/common.py, 20_build_city.py, 21_build_env.py (+ raw data in _dev/data) -> web/public/data/*
  docs       mkdocs.yml + docs/*.md + CHANGELOG.md            -> web/public/docs/  (Zensical; optional)
Steps whose tools are missing (Blender, Python packages, raw data, zensical) are skipped with a warning; the app then uses the
files already in web/public.   Usage: python pipeline/prepare.py [--force]
"""
import glob, importlib.util, os, shutil, subprocess, sys

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

# 2. Blender asset library (props, costume kit)
if stale([J("blender", "scripts", "*.py"), J("web", "public", "textures", "*_col.jpg")],
         [J("web", "public", "models", "materials.json")]):          # written last by build_assets.py = build stamp
    exe = blender_exe()
    if not exe: print("  ! Blender not found (set BLENDER_PATH) – props not rebuilt")
    else:
        for s in sorted(glob.glob(J("blender", "scripts", "build_*.py"))):
            run([exe, "-b", "--factory-startup", "--python", s], f"blender {os.path.basename(s)}", quiet=True)
else: print("  = Blender props up to date")

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


docs_in = [J("mkdocs.yml"), J("CHANGELOG.md"), J("docs", "*.md"), J("docs", "landmarks", "*.md")]
docs_out = [J("web", "public", "docs", "index.html")]
if stale(docs_in, docs_out):
    sync_docs_changelog()
    zensical = J(".venv", "Scripts", "zensical.exe") if os.name == "nt" else J(".venv", "bin", "zensical")
    if not os.path.exists(zensical):
        zensical = shutil.which("zensical")
    if zensical:
        run([zensical, "build", "--clean", "-f", J("mkdocs.yml")], "docs site (zensical)")
    else:
        print("  ! zensical not found – skip docs site (python -m venv .venv && .venv\\Scripts\\pip install zensical)")
else:
    print("  = docs site up to date")

print("[prepare] done")
