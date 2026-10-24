# 15 - Docs site

**Read first:** `docs/prompts/00-context.md`. **Depends on:** 01.

## Goal

The documentation site tooling, as oaken-mail's prompt 01a.

## Steps

1. Port `docs/tools` (build, render, check_docs, softmap) and `docs/softmap.toml` checking.
2. Generated pages for the CLI reference, API reference and plugin contracts.
3. `check_docs.py` in CI; `<!-- check -->` commands run for real.

## Acceptance criteria

- `uv run --group docs python docs/tools/check_docs.py` passes.
- `ruff check`, `ruff format --check`, `mypy`, `lint-imports` and `pytest` pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Checkpoint

Use the report format from `00-context.md`, then stop.
