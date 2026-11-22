#!/usr/bin/env bash
# Netlify build: Vite app → web/dist, with /docs/ from Zensical when docs sources changed.
# If docs did not change, reuse the previous docs tree restored by netlify-plugin-cache.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

docs_changed() {
  # First deploy / missing refs → treat as changed
  if [[ -z "${CACHED_COMMIT_REF:-}" || -z "${COMMIT_REF:-}" || "$CACHED_COMMIT_REF" == "$COMMIT_REF" ]]; then
    return 0
  fi
  ! git diff --quiet "$CACHED_COMMIT_REF" "$COMMIT_REF" -- \
    docs/ mkdocs.yml CHANGELOG.md scripts/netlify-build.sh
}

# Production docs URL (Netlify sets URL / DEPLOY_PRIME_URL)
DOCS_URL="${URL:-http://localhost:5173}/docs/"
DOCS_URL="${DOCS_URL%/}/"
if [[ "${CONTEXT:-}" == "deploy-preview" || "${CONTEXT:-}" == "branch-deploy" ]]; then
  DOCS_URL="${DEPLOY_PRIME_URL%/}/docs/"
fi

need_docs=0
if docs_changed; then
  need_docs=1
  echo "docs: sources changed — rebuild with Zensical"
elif [[ ! -f web/public/docs/index.html ]]; then
  need_docs=1
  echo "docs: no cached site — rebuild with Zensical"
else
  echo "docs: unchanged — keeping cached web/public/docs/"
fi

if [[ "$need_docs" -eq 1 ]]; then
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
fi

cd web
npm ci --include=dev
npm run build
