# 01 - Bootstrap

**Read first:** `docs/prompts/00-context.md`. **Depends on:** nothing.

## Goal

A green, empty project with tooling and legal files.

## Steps

1. uv workspace: root package `oaken-trunk` (`src/oaken_trunk/__init__.py` holds `__version__` only) and `apps/cli` (`oaken-trunk-cli`, import `oaken_trunk_cli`), both with the version read from the one place (as oaken-mail's lockstep test does).
2. pyproject: hatchling, ruff (E,F,I,UP,B,ASYNC,S,CPY, line length 100), `mypy --strict`, pytest + pytest-asyncio, import-linter, detect-secrets, pre-commit, SPDX check.
3. `conftest.py` that gives every test its own `OAKEN_TRUNK_HOME` and drops other `OAKEN_TRUNK_*` variables.
4. Repo-wide tests: no sensitive files tracked, `.gitignore` coverage, version lockstep, import boundaries.
5. CI on Linux, macOS and Windows, Python 3.11 and 3.12, plus a secret-scan job. Pin actions by tag.
6. `oaken-trunk --version` works.

## Acceptance criteria

- `uv sync && ruff check && ruff format --check && mypy && lint-imports && pytest` pass; every `.py` has the SPDX header.
- `ruff check`, `ruff format --check`, `mypy`, `lint-imports` and `pytest` pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Checkpoint

Use the report format from `00-context.md`, then stop.
