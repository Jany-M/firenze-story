#!/usr/bin/env bash
# Netlify build: Zensical docs → web/public/docs, then Vite app → web/dist.
# Whole deploys are still skipped by scripts/netlify-ignore.sh when neither web nor docs changed.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Production docs URL (Netlify sets URL / DEPLOY_PRIME_URL)
DOCS_URL="${URL:-http://localhost:5173}/docs/"
DOCS_URL="${DOCS_URL%/}/"
if [[ "${CONTEXT:-}" == "deploy-preview" || "${CONTEXT:-}" == "branch-deploy" ]]; then
  DOCS_URL="${DEPLOY_PRIME_URL%/}/docs/"
fi

echo "docs: building with Zensical → $DOCS_URL"
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
p = Path("mkdocs.yml")
text = p.read_text(encoding="utf-8")
url = """${DOCS_URL}"""
text2, n = re.subn(r"(?m)^site_url:.*$", f"site_url: {url}", text, count=1)
if n != 1:
    raise SystemExit("mkdocs.yml: site_url line not found")
p.write_text(text2, encoding="utf-8")
print("site_url ->", url)
PY

zensical build --clean -f mkdocs.yml

cd web
npm ci --include=dev
npm run build
