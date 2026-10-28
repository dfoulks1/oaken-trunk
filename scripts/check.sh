#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Run every check, in one go. This is the gate: there is no CI.
#
#   scripts/check.sh
#
set -euo pipefail
cd "$(dirname "$0")/.."

uv run scripts/run_check.py .check.lastrun "check" -- \
    "sync"          uv sync --locked --quiet       -- \
    "ruff check"    uv run ruff check .            -- \
    "ruff format"   uv run ruff format --check .   -- \
    "mypy"          uv run mypy                    -- \
    "lint-imports"  uv run lint-imports            -- \
    "pytest"        uv run pytest -q               -- \
    "docs"          uv run python docs/tools/check_docs.py
