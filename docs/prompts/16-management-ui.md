# 16 - Management UI

**Read first:** `docs/prompts/00-context.md`. **Depends on:** 06, 08, 18.

## Goal

A separate web app on its own port for the operator: queue depth, spool usage and quota, leases, failures,
and the actions the CLI already offers (ADR 0007).

## Steps

1. `apps/webui` as its own uv workspace member (`oaken-trunk-webui`, import `oaken_trunk_webui`), version read from the one shared place.
2. It is a client of the operation registry. It adds no operation of its own and never imports spool or engine internals; import-linter enforces it.
3. Own port and own token, separate from ingest and consume. Off by default; binds to loopback unless the operator opts in; the token never reaches the browser.
4. Pages: status, queue, leased messages, failures, configuration (read-only), `doctor` results. Message bodies are never displayed or logged.
5. Every action in the UI maps to an operation that has a CLI command.

## Acceptance criteria

- With the UI off, nothing listens on its port. With it on, every page works against a `FakeSpool`.
- A test proves the UI cannot reach anything the CLI cannot.
- `ruff check`, `ruff format --check`, `mypy`, `lint-imports` and `pytest` pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Checkpoint

Use the report format from `00-context.md`, then stop.
