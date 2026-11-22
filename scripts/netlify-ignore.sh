#!/usr/bin/env bash
# Netlify ignore command: exit 0 = skip build, exit 1 = build.
# Skip when the push does not touch the web app or the docs site sources.
set -euo pipefail

# Always build the first deploy / when Git refs are missing
if [[ -z "${CACHED_COMMIT_REF:-}" || -z "${COMMIT_REF:-}" ]]; then
  echo "ignore: no commit refs — build"
  exit 1
fi
if [[ "$CACHED_COMMIT_REF" == "$COMMIT_REF" ]]; then
  echo "ignore: first compare — build"
  exit 1
fi

# Paths that affect what Netlify publishes (web/dist = Vite app + /docs/)
PATHS=(
  web/
  docs/
  mkdocs.yml
  CHANGELOG.md
  scripts/netlify-build.sh
  scripts/netlify-ignore.sh
  netlify.toml
)

if git diff --quiet "$CACHED_COMMIT_REF" "$COMMIT_REF" -- "${PATHS[@]}"; then
  echo "ignore: no changes in web app / docs paths — skip deploy"
  exit 0
fi

echo "ignore: relevant changes — build"
git diff --name-only "$CACHED_COMMIT_REF" "$COMMIT_REF" -- "${PATHS[@]}" | sed 's/^/  · /' || true
exit 1
