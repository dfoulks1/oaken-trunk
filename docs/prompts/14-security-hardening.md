# 14 - Security hardening

**Read first:** `docs/prompts/00-context.md`. **Depends on:** 05, 07, 08, 09.

## Goal

The dedicated pass.

## Steps

1. Injection and malformed-input suite across every ingestor (header injection, oversized lines, truncated DATA).
2. Auth tests: token separation, TLS-before-AUTH, no open relay, mTLS for consumers if built.
3. Audit review: no message body in any log or exception; spool permissions owner-only.
4. Dependency licence check: no GPL.

## Acceptance criteria

- Findings are fixed or recorded in an ADR.
- `ruff check`, `ruff format --check`, `mypy`, `lint-imports` and `pytest` pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Checkpoint

Use the report format from `00-context.md`, then stop.
