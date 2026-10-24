# 05 - Http ingest

**Read first:** `docs/prompts/00-context.md`. **Depends on:** 03, 04.

## Goal

`oaken_trunk_http`: `/v1/send` as submission into the spool.

## Steps

1. Starlette + uvicorn as in oaken-mail's ADR 0005; streaming request body into the engine.
2. Bearer ingest token (separate from consume token), token file mode 0600.
3. Backpressure codes from `docs/architecture/ingestion.md`; `Retry-After` from `retry_after_seconds`.
4. The route table is generated from the operation registry.

## Acceptance criteria

- Tests post a large body, an oversized body (413), and overload (503 + Retry-After) without the network.
- `ruff check`, `ruff format --check`, `mypy`, `lint-imports` and `pytest` pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Checkpoint

Use the report format from `00-context.md`, then stop.
