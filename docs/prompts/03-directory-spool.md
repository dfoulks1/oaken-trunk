# 03 - Directory spool

**Read first:** `docs/prompts/00-context.md`. **Depends on:** 02.

## Goal

The default spool driver: `oaken_trunk_spool_dir`.

## Steps

1. Layout, store, lease, ack, nack, delete and recovery exactly as `docs/architecture/spool.md`.
2. Durability `strict`, `batched` (group commit: concurrent stores share one fsync) and `volatile`.
3. `max_spool_bytes` with per-worker counting and periodic rescan.
4. `watch()` with inotify where available and a polling fallback; works across processes.
5. Blocking file I/O through a bounded thread pool (`threads_per_worker`).
6. Passes the spool contract suite; crash tests that kill between steps and assert recovery.

## Acceptance criteria

- No accepted message is lost in `strict` and `batched` crash tests; two concurrent consumers never lease the same message.
- `ruff check`, `ruff format --check`, `mypy`, `lint-imports` and `pytest` pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Checkpoint

Use the report format from `00-context.md`, then stop.
