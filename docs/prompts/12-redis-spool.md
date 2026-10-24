# 12 - Redis spool

**Read first:** `docs/prompts/00-context.md`. **Depends on:** 03.

## Goal

`oaken_trunk_spool_redis`.

## Steps

1. Redis stream and consumer groups mapped to lease, ack, nack; AOF guidance in the docs.
2. Streams bodies in bounded chunks; no whole-message buffering.
3. Passes the spool contract suite using a fake or in-process server; tests never use a real Redis.

## Acceptance criteria

- Contract suite passes.
- `ruff check`, `ruff format --check`, `mypy`, `lint-imports` and `pytest` pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Checkpoint

Use the report format from `00-context.md`, then stop.
