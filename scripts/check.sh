#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# One command to check the docs locally.
#
#   scripts/check.sh   build the site, check it, run the tooling tests
#
# Then open docs/index.html in a browser; the links are relative, so it works from file://.
set -euo pipefail
cd "$(dirname "$0")/.."

LASTRUN_FILE=".check.lastrun"
if [[ -f "$LASTRUN_FILE" ]]; then
    read -r _sha _ts < "$LASTRUN_FILE"
    _now=$(date +%s)
    _elapsed=$(( _now - _ts ))
    _h=$(( _elapsed / 3600 ))
    _m=$(( (_elapsed % 3600) / 60 ))
    _s=$(( _elapsed % 60 ))
    echo "==> last run: ${_sha} (${_h}h ${_m}m ${_s}s ago)"
fi

echo "==> sync"
uv sync --quiet

echo "==> build the site"
uv run python docs/tools/build_site.py

echo "==> check links, anchors, hosts and that two builds are identical"
uv run python docs/tools/check_docs.py

echo "==> tooling tests"
uv run pytest -q

echo "==> TODO(user) markers still to fill in"
grep -rn "TODO(user)" --include=*.md . --exclude-dir=.venv --exclude-dir=.git | grep -v "^./docs/tools/" || echo "none"

echo
echo "All checks passed."

echo "$(git rev-parse --short HEAD) $(date +%s)" > "$LASTRUN_FILE"
