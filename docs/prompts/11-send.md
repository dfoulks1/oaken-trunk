# 11 - Send

**Read first:** `docs/prompts/00-context.md`. **Depends on:** 08.

## Goal

Outbound spool and the Sender plugin kind.

## Steps

1. Submission through HTTP, CLI and SMTP 587 into an outbound spool with its own quota.
2. Bulk bodies stored once, per-recipient envelopes referencing them.
3. Drain with per-domain concurrency and rate limits, connection reuse, backoff with jitter, bounces; domain-hash sharding across workers.
4. Decide and record DSN format and the retry schedule in an ADR.

## Acceptance criteria

- A test submits tens of thousands of synthetic messages and a fake sender drains them under per-domain limits.
- `ruff check`, `ruff format --check`, `mypy`, `lint-imports` and `pytest` pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Checkpoint

Use the report format from `00-context.md`, then stop.
