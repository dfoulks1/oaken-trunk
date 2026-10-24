# 13 - S3 sqs spool

**Read first:** `docs/prompts/00-context.md`. **Depends on:** 03.

## Goal

`oaken_trunk_spool_s3_sqs`.

## Steps

1. S3 objects for bodies, SQS visibility timeouts for leases; multipart upload from the chunk stream.
2. Credentials from the environment or instance role, never config.
3. Passes the spool contract suite against a fake; tests never use AWS.

## Acceptance criteria

- Contract suite passes.
- `ruff check`, `ruff format --check`, `mypy`, `lint-imports` and `pytest` pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Checkpoint

Use the report format from `00-context.md`, then stop.
