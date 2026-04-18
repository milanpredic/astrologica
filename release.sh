#!/usr/bin/env bash
# release.sh — bump version, commit, push, tag, and create a GitHub release.
#
# Usage:
#   ./release.sh patch           # 0.1.0 → 0.1.1
#   ./release.sh minor           # 0.1.0 → 0.2.0
#   ./release.sh major           # 0.1.0 → 1.0.0
#   ./release.sh 0.5.0           # explicit version
#   ./release.sh --dry-run minor # preview, make no changes
#
# Preconditions:
#   - Clean working tree on 'main'
#   - 'gh' CLI installed and authenticated
#   - Pushing a tag 'vX.Y.Z' triggers .github/workflows/publish.yml,
#     which publishes to PyPI via OIDC (no token needed here).

set -euo pipefail

DRY_RUN=false
BUMP=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    patch|minor|major) BUMP="$1"; shift ;;
    -h|--help)
      sed -n '2,20p' "$0"; exit 0 ;;
    [0-9]*.[0-9]*.[0-9]*) BUMP="$1"; shift ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$BUMP" ]]; then
  echo "Usage: $0 [--dry-run] <patch|minor|major|X.Y.Z>" >&2
  exit 1
fi

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

# ---------- pre-flight ----------

command -v gh >/dev/null || { echo "gh CLI not found — install with 'brew install gh'" >&2; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "gh not authenticated — run 'gh auth login'" >&2; exit 1; }

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$BRANCH" != "main" ]]; then
  echo "Must be on 'main' (currently on '$BRANCH')" >&2
  exit 1
fi

git fetch --quiet origin main
LOCAL="$(git rev-parse @)"
REMOTE="$(git rev-parse @{u} 2>/dev/null || echo "")"
if [[ -n "$REMOTE" && "$LOCAL" != "$REMOTE" ]]; then
  BASE="$(git merge-base @ @{u})"
  if [[ "$LOCAL" == "$BASE" ]]; then
    echo "Local 'main' is behind origin — pull first." >&2; exit 1
  elif [[ "$REMOTE" != "$BASE" ]]; then
    echo "Local 'main' has diverged from origin — resolve before releasing." >&2; exit 1
  fi
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Working tree has uncommitted changes. Commit or stash first:" >&2
  git status --short >&2
  exit 1
fi

# ---------- compute versions ----------

CURRENT="$(python3 - <<'PY'
import re, pathlib, sys
t = pathlib.Path("pyproject.toml").read_text()
m = re.search(r'^version = "([^"]+)"', t, flags=re.M)
if not m:
    sys.exit("Could not find version line in pyproject.toml")
print(m.group(1))
PY
)"

NEW="$(CUR="$CURRENT" BUMP="$BUMP" python3 - <<'PY'
import os, re, sys
cur = os.environ["CUR"]
bump = os.environ["BUMP"]
if re.fullmatch(r"\d+\.\d+\.\d+", bump):
    print(bump); sys.exit(0)
if not re.fullmatch(r"\d+\.\d+\.\d+", cur):
    sys.exit(f"Current version '{cur}' is not X.Y.Z — bump manually.")
major, minor, patch = (int(x) for x in cur.split("."))
if bump == "patch":
    patch += 1
elif bump == "minor":
    minor += 1; patch = 0
elif bump == "major":
    major += 1; minor = 0; patch = 0
else:
    sys.exit(f"Unknown bump: {bump}")
print(f"{major}.{minor}.{patch}")
PY
)"

echo "Current version: $CURRENT"
echo "New version:     $NEW"

# ---------- tag existence guard ----------

if git rev-parse --verify "v$NEW" >/dev/null 2>&1; then
  echo "Tag v$NEW already exists locally." >&2; exit 1
fi
if git ls-remote --tags origin "v$NEW" | grep -q "refs/tags/v$NEW$"; then
  echo "Tag v$NEW already exists on origin." >&2; exit 1
fi

# ---------- dry-run short-circuit ----------

if $DRY_RUN; then
  cat <<EOF
DRY RUN — would:
  1. Update pyproject.toml version → $NEW
  2. uv build && twine check dist/*
  3. git add pyproject.toml && git commit -m "Release v$NEW"
  4. git push origin main
  5. git tag -a v$NEW -m "Release v$NEW"
  6. git push origin v$NEW   (triggers publish.yml → PyPI)
  7. gh release create v$NEW --generate-notes --title "v$NEW"
EOF
  exit 0
fi

# ---------- build sanity check (before we commit anything) ----------

echo "Running build + twine check..."
rm -rf dist
uv build >/dev/null
uv run --quiet --with twine twine check dist/* >/dev/null
echo "Build OK."

# ---------- bump pyproject.toml ----------

NEW="$NEW" python3 - <<'PY'
import os, pathlib, re, sys
new = os.environ["NEW"]
p = pathlib.Path("pyproject.toml")
t = p.read_text()
t2, n = re.subn(r'^version = "[^"]+"', f'version = "{new}"', t, count=1, flags=re.M)
if n != 1:
    sys.exit("Failed to rewrite version line in pyproject.toml")
p.write_text(t2)
PY

# ---------- commit + push ----------

git add pyproject.toml
git commit -m "Release v$NEW"
git push origin main

# ---------- tag + push ----------

git tag -a "v$NEW" -m "Release v$NEW"
git push origin "v$NEW"

# ---------- GitHub release ----------

gh release create "v$NEW" --generate-notes --title "v$NEW"

echo ""
echo "v$NEW released."
echo "Publish workflow: $(gh run list --workflow=publish.yml --limit=1 --json url --jq '.[0].url' 2>/dev/null || echo '(check Actions tab)')"
echo "Watch with: gh run watch"
