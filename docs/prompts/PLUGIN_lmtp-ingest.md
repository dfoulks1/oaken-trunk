# LMTP ingest

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/PLUGIN.md`.
**Depends on:** [CORE_plugin-host](CORE_plugin-host.md), [CORE_daemon](CORE_daemon.md).
**Lift:** M
**Delivers:** LMTP over a Unix socket: the Postfix delivery target

## Goal

`oaken_trunk_lmtp`: the Postfix delivery target.

## Steps

1. LMTP over a Unix socket (and optional TCP); per-recipient replies as the protocol requires.
2. Stream DATA into the engine; map backpressure to 451/452/552.
3. Docs deliverable: Postfix `virtual_transport` snippet and the qmail pipe line.

## Acceptance criteria

- An in-process LMTP client delivers to the spool; Postfix snippet documented and `check_commands`-style verified.
- `ruff check`, `ruff format --check`, `mypy`, `lint-imports` and `pytest` pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Checkpoint

Use the report format from `CONTEXT.md`, then stop.
