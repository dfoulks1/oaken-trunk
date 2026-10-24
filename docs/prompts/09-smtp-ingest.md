# 09 - Smtp ingest

**Read first:** `docs/prompts/00-context.md`. **Depends on:** 07.

## Goal

`oaken_trunk_smtp`: SMTP on 25 and 587.

## Steps

1. STARTTLS; AUTH PLAIN/LOGIN only after TLS; credentials from secrets, never config.
2. Recipient allowlist (`accept_domains`); empty means refuse all, no open relay.
3. Streaming DATA, size limit before the 250, 4xx on overload.

## Acceptance criteria

- Tests prove no relaying for unlisted domains and no AUTH offered before STARTTLS.
- `ruff check`, `ruff format --check`, `mypy`, `lint-imports` and `pytest` pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Checkpoint

Use the report format from `00-context.md`, then stop.
