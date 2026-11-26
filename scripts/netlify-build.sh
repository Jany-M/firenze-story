#!/usr/bin/env bash
# Netlify build: Zensical docs + library → web/public/{docs,library}, then Vite app → web/dist.
# Whole deploys are still skipped by scripts/netlify-ignore.sh when neither web nor docs changed.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Production site URLs (Netlify sets URL / DEPLOY_PRIME_URL)
BASE_URL="${URL:-http://localhost:5173}"
BASE_URL="${BASE_URL%/}"
if [[ "${CONTEXT:-}" == "deploy-preview" || "${CONTEXT:-}" == "branch-deploy" ]]; then
  BASE_URL="${DEPLOY_PRIME_URL%/}"
fi
DOCS_URL="${BASE_URL}/docs/"
LIBRARY_URL="${BASE_URL}/library/"

echo "docs: building with Zensical → $DOCS_URL"
echo "library: building with Zensical → $LIBRARY_URL"
python3 -m pip install --upgrade pip
python3 -m pip install zensical

python3 - <<'PY'
from pathlib import Path
root = Path(".")
src, dst = root / "CHANGELOG.md", root / "docs" / "changelog.md"
text = src.read_text(encoding="utf-8")
text = text.replace("](docs/", "](").replace("[docs/", "[")
text = text.replace(
    "](pipeline/README.md)",
    "](https://github.com/Jany-M/firenze-story/blob/main/pipeline/README.md)",
)
dst.write_text(
    "<!-- Generated from ../CHANGELOG.md by scripts/netlify-build.sh — edit the root file. -->\n\n" + text,
    encoding="utf-8",
)
print("synced", dst)
PY

python3 - <<PY
from pathlib import Path
import re

def set_site_url(path: str, url: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    text2, n = re.subn(r"(?m)^site_url:.*$", f"site_url: {url}", text, count=1)
    if n != 1:
        raise SystemExit(f"{path}: site_url line not found")
    p.write_text(text2, encoding="utf-8")
    print(path, "site_url ->", url)

set_site_url("mkdocs.yml", """${DOCS_URL}""")
set_site_url("mkdocs.library.yml", """${LIBRARY_URL}""")
PY

# Gallery HTML + events/maps pages for the library site
python3 pipeline/52_encyclopedia.py

# Shared CSS/logo/JS into encyclopedia/assets (library docs_dir)
python3 - <<'PY'
import shutil
from pathlib import Path
src, dst = Path("docs/assets"), Path("docs/encyclopedia/assets")
shutil.copytree(src, dst, dirs_exist_ok=True)
print("synced", dst)
PY

# App + library galleries both use /materials/ from web/public/materials
python3 - <<'PY'
import shutil
from pathlib import Path
src, dst = Path("docs/materials"), Path("web/public/materials")
if (src / "materials.json").exists():
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("manifest.json", "*.md"))
    print("copied materials →", dst)
else:
    print("! docs/materials/materials.json missing — gallery images will 404")
PY

zensical build --clean -f mkdocs.yml
zensical build --clean -f mkdocs.library.yml

cd web
npm ci --include=dev
npm run build
