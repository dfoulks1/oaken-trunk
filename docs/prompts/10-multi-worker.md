# 10 - Multi worker

**Read first:** `docs/prompts/00-context.md`. **Depends on:** 03, 05.

## Goal

Supervisor and workers.

## Steps

1. Supervisor opens sockets, spawns `workers` processes, restarts crashes.
2. `workers` (number or `auto`, cgroup and affinity aware), `max_workers`, `threads_per_worker`, `max_threads`; startup refuses a product above `max_threads`.
3. A supervisor counter service over a socketpair per worker: batched credits for `max_inflight`, spool quota and per-client rate limits; credits reclaimed when a worker dies; workers fail closed with a 4xx if the supervisor is unreachable. Control messages only, never message bytes.
4. Works on Linux, macOS and Windows (inherited sockets, not `SO_REUSEPORT`).

## Acceptance criteria

- A multi-worker test delivers many messages with no loss or duplicate lease, never exceeds global `max_inflight`, and a killed worker is replaced with its credits reclaimed.
- `ruff check`, `ruff format --check`, `mypy`, `lint-imports` and `pytest` pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Checkpoint

Use the report format from `00-context.md`, then stop.
