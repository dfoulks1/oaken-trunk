# 04 - Plugin host

**Read first:** `docs/prompts/00-context.md`. **Depends on:** 02.

## Goal

Entry-point discovery and lifecycle for ingestors, spools and senders.

## Steps

1. Base classes `BaseIngestor`, `BaseSpool`, `BaseSender` in `oaken_trunk.plugins.base` per `docs/plugins.md` and ADR 0006: `ctx`, lifecycle, health, lenient return coercion with readable errors, capabilities inferred from the methods a plugin overrides.
2. Contract suites `SpoolContract`, `IngestorContract`, `SenderContract` in `oaken_trunk.testing.contracts`, including the streaming and memory test.
3. Groups `oaken_trunk.ingestors`, `oaken_trunk.spools`, `oaken_trunk.senders`; first-party plugins register as a third party's would.
4. Plugin settings from `[ingest.<name>]` and `[spool.<name>]`; secrets from the environment or files, never `config.toml`.
5. Capabilities, health, and `doctor` hooks; a plugin error never stops core.
6. import-linter contracts: core never imports a plugin or client; plugins depend only on the contract layer.

## Acceptance criteria

- A fake third-party plugin registers and runs; a failing plugin is reported by `doctor` and does not stop the daemon.
- `ruff check`, `ruff format --check`, `mypy`, `lint-imports` and `pytest` pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Checkpoint

Use the report format from `00-context.md`, then stop.
