# 06 - Cli client

**Read first:** `docs/prompts/00-context.md`. **Depends on:** 03, 04.

## Goal

The `oaken-trunk` command, a thin client of the operation registry.

## Steps

1. Every operation has a command; `submit` reads stdin (qmail pipe target).
2. `init` writes a documented config and creates folders; `doctor` explains what is wrong; `status` shows queue, bytes, quota.
3. Runs in-process against the spool when no daemon is up; talks HTTP otherwise.
4. Exit codes and `--json` output; add a row to the CLI audit table for anything an operator runs.

## Acceptance criteria

- A person who has never read the code can `init`, `start`, `submit` and see the message in `status`.
- `ruff check`, `ruff format --check`, `mypy`, `lint-imports` and `pytest` pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Checkpoint

Use the report format from `00-context.md`, then stop.
