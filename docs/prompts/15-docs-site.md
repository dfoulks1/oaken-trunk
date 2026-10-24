# 15 - Docs site

**Read first:** `docs/prompts/00-context.md`. **Depends on:** 01.

## Goal

The documentation site tooling, as oaken-mail's prompt 01a.

## Steps

1. Port `docs/tools` (build, render, check_docs, softmap) and `docs/softmap.toml` checking.
2. Generated pages for the CLI reference, API reference and plugin contracts.
3. `check_docs.py` in CI. Re-add `check_commands.py` (copied from oaken-mail, pointed at `oaken_trunk_cli`) once the CLI exists, so `<!-- check -->` commands run for real. The `gen_*` reference generators are likewise re-added as the code they read lands (plugin contracts, operations, CLI, API).
3. Already done by hand before the code existed: the build, render, check and software-map tooling, templates and brand assets are ported, and `uv run python docs/tools/build_site.py` builds the site.

## Acceptance criteria

- `uv run --group docs python docs/tools/check_docs.py` passes.
- `ruff check`, `ruff format --check`, `mypy`, `lint-imports` and `pytest` pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Checkpoint

Use the report format from `00-context.md`, then stop.
