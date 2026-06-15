#!/usr/bin/env bash
# build.sh — Generate the DevOps Mastery docs site (dochub) from the course Markdown.
#
# Renders every lecture/chapter/topic Markdown file under content/ into a
# self-contained, themed, searchable static HTML site at dochub/ (repo root).
# No node_modules, no framework — just Python + the `markdown` package.
#
# Usage (from the repo root):
#   ./scripts/build.sh                  # build / refresh the whole dochub
#   ./scripts/build.sh --serve          # build, then serve at http://localhost:8000
#   ./scripts/build.sh --serve 9000     # build, then serve on a custom port
#   ./scripts/build.sh --only-complete  # hide topics whose frontmatter status != complete
#   ./scripts/build.sh --open           # build, then open dochub/index.html in the browser
#
# Env overrides:
#   PYTHON=python3.12 ./scripts/build.sh   # pick a specific interpreter
#   NO_PIP=1 ./scripts/build.sh            # never auto-install deps (fail if missing)
#
# Layout:
#   content/   all course Markdown (read-only input)
#   scripts/   this script + build_dochub.py + dochub_assets/
#   dochub/    generated static site (output; safe to delete + regenerate)

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"          # scripts/
REPO_ROOT="$(cd "$HERE/.." && pwd)"            # repo root
PY="${PYTHON:-python3}"
GEN="$HERE/build_dochub.py"
OUT="$REPO_ROOT/dochub"

# ---- parse flags ----
SERVE=0
PORT=8000
OPEN=0
export DOCHUB_ONLY_COMPLETE="${DOCHUB_ONLY_COMPLETE:-}"
while [ $# -gt 0 ]; do
  case "$1" in
    --serve)         SERVE=1; if [[ "${2:-}" =~ ^[0-9]+$ ]]; then PORT="$2"; shift; fi ;;
    --open)          OPEN=1 ;;
    --only-complete) export DOCHUB_ONLY_COMPLETE=1 ;;
    -h|--help)       sed -n '2,22p' "$0"; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

# ---- sanity: interpreter + generator present ----
command -v "$PY" >/dev/null 2>&1 || { echo "ERROR: '$PY' not found. Set PYTHON=… or install Python 3." >&2; exit 1; }
[ -f "$GEN" ] || { echo "ERROR: generator not found at $GEN" >&2; exit 1; }

# ---- ensure the one dependency (`markdown`) is available ----
if ! "$PY" -c 'import markdown' >/dev/null 2>&1; then
  if [ "${NO_PIP:-}" = "1" ]; then
    echo "ERROR: Python 'markdown' package missing and NO_PIP=1 set." >&2
    echo "       Install it with:  $PY -m pip install markdown" >&2
    exit 1
  fi
  echo "• Installing the 'markdown' package (one-time)…"
  "$PY" -m pip install --quiet --user markdown \
    || "$PY" -m pip install --quiet markdown
fi

# ---- build ----
"$PY" "$GEN"

# ---- optional open / serve ----
if [ "$OPEN" = "1" ]; then
  ( command -v open >/dev/null 2>&1 && open "$OUT/index.html" ) \
    || ( command -v xdg-open >/dev/null 2>&1 && xdg-open "$OUT/index.html" ) \
    || echo "Open manually: $OUT/index.html"
fi

if [ "$SERVE" = "1" ]; then
  echo ""
  echo "Serving dochub at http://localhost:${PORT}  (Ctrl-C to stop)"
  exec "$PY" -m http.server -d "$OUT" "$PORT"
fi
