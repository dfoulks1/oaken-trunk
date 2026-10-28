# S3 and SQS spool

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/PLUGIN.md`.
**Depends on:** [PLUGIN_directory-spool](PLUGIN_directory-spool.md), [CORE_plugin-host](CORE_plugin-host.md).
**Lift:** M
**Delivers:** S3 bodies, SQS visibility timeouts as leases

## Goal

`oaken_trunk_spool_s3_sqs`.

## Steps

1. One S3 object per body; one SQS queue per device (ADR 0013), visibility timeouts as leases; multipart
   upload from the chunk stream. A body is deleted when no queue holds it; an S3 lifecycle rule is the backstop.
2. SQS keeps a message at most 14 days, and mail must not expire: re-enqueue entries before retention ends,
   or say why another design is needed. Verify the limit.
3. Credentials from the environment or instance role, never config.
4. Passes the spool contract suite against a fake; tests never use AWS.

## Acceptance criteria

- Contract suite passes.
- `ruff check`, `ruff format --check`, `mypy`, `lint-imports` and `pytest` pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Checkpoint

Use the report format from `CONTEXT.md`, then stop.
