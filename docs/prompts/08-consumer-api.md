# 08 - Consumer api

**Read first:** `docs/prompts/00-context.md`. **Depends on:** 05, 06.

## Goal

Lease, fetch, ack, nack over HTTP, with CLI parity.

## Steps

1. Operations `lease`, `fetch`, `ack`, `nack`, `delete`, `list`; consume token separate from ingest.
2. Long-poll or SSE wake-up backed by `watch()`.
3. Versioned contract and a documented example consumer (CLI and webhook relay). The Oaken Mail provider plugin is built in the oaken-mail repo.

## Acceptance criteria

- A fake consumer leases, crashes, and the message reappears after the lease expires.
- `ruff check`, `ruff format --check`, `mypy`, `lint-imports` and `pytest` pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Checkpoint

Use the report format from `00-context.md`, then stop.
