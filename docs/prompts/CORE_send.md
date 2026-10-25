# Send

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CORE.md`.
**Depends on:** [CORE_consumer-api](CORE_consumer-api.md), [CORE_request-guard](CORE_request-guard.md).
**Delivers:** Outbound spool, the Sender plugin kind, DKIM signing

## Goal

Outbound spool and the Sender plugin kind.

## Steps

1. DKIM signing per ADR 0011: RSA-2048 and Ed25519, body hash from a streaming pass over the spooled file, signature added at send time, keys owner-only.
2. Submission through HTTP, CLI and SMTP 587 into an outbound spool with its own quota.
3. Bulk bodies stored once, per-recipient envelopes referencing them.
4. Drain with per-domain concurrency and rate limits, connection reuse, backoff with jitter, bounces; domain-hash sharding across workers.
5. Decide and record DSN format and the retry schedule in an ADR.

## Acceptance criteria

- A test submits tens of thousands of synthetic messages and a fake sender drains them under per-domain limits.
- `ruff check`, `ruff format --check`, `mypy`, `lint-imports` and `pytest` pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Checkpoint

Use the report format from `CONTEXT.md`, then stop.
