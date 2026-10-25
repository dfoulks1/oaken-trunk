# Security hardening

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CORE.md`.
**Depends on:** [PLUGIN_lmtp-ingest](PLUGIN_lmtp-ingest.md), [CORE_consumer-api](CORE_consumer-api.md), [CORE_http-listener](CORE_http-listener.md).
**Delivers:** Injection, auth and open-relay test pass across every ingestor

## Goal

The dedicated pass.

## Steps

1. Injection and malformed-input suite across every ingestor (header injection, oversized lines, truncated DATA).
2. Auth tests: unsigned, badly signed, stale, replayed and cross-surface requests are refused before any route; TLS-before-AUTH; no open relay; every first-party authenticator passes `AuthenticatorContract`.
3. Audit review: no message body in any log or exception; spool permissions owner-only.
4. Log audit per ADR 0012: sentinel content sent through every ingestor never appears in any log, error or response.
5. Dependency licence check: no GPL.

## Acceptance criteria

- Findings are fixed or recorded in an ADR.
- `ruff check`, `ruff format --check`, `mypy`, `lint-imports` and `pytest` pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Checkpoint

Use the report format from `CONTEXT.md`, then stop.
