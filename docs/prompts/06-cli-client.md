# 06 - Cli client

**Read first:** `docs/prompts/00-context.md`. **Depends on:** 03, 04.

## Goal

The `oaken-trunk` command, a thin client of the operation registry.

## Steps

1. argparse from the standard library, lazy imports, a thin client of the HTTP API with no logic of its own (ADR 0009). `oaken-trunk operation NAME --json '{...}'` reaches every operation; flags are generated from each operation's input schema, and a secret field has only `--NAME-stdin`. Plugin operations appear as `oaken-trunk PLUGIN VERB`.
2. Hand-written verbs for the daily operations; `submit` reads stdin (qmail pipe target).
3. Exit codes 0 ok, 1 error, 2 usage, 3 not running, 4 auth, 5 needs confirmation.
4. `init` writes a documented config and creates folders; `doctor` explains what is wrong; `status` shows queue, bytes, quota.
5. Runs in-process against the spool when no daemon is up; talks HTTP otherwise.
6. Exit codes and `--json` output; add a row to the CLI audit table for anything an operator runs.

## Acceptance criteria

- A person who has never read the code can `init`, `start`, `submit` and see the message in `status`.
- `ruff check`, `ruff format --check`, `mypy`, `lint-imports` and `pytest` pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Checkpoint

Use the report format from `00-context.md`, then stop.
