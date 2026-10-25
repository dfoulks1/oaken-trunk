#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Build the docs site and run all doc checks.
#
#   scripts/docs_check.sh
#
set -euo pipefail
cd "$(dirname "$0")/.."

uv run scripts/run_check.py .docs_check.lastrun "docs" -- \
    "sync"                  uv sync --quiet                             -- \
    "build the site"        uv run python docs/tools/build_site.py     -- \
    "check links/anchors"   uv run python docs/tools/check_docs.py     -- \
    "tooling tests"         uv run pytest -q
