# Management UI: the app and its read-only pages

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/WEBUI.md`, ADR 0007.
**Depends on:** [CORE_system-operations](CORE_system-operations.md), [CORE_audit-and-jobs](CORE_audit-and-jobs.md), [CORE_http-listener](CORE_http-listener.md).
**Lift:** L
**Delivers:** Operator web app on its own port: status, queue, leases, failures, configuration and `doctor`, read only
**Track:** `WEBUI_`. Actions are WEBUI_operator-actions.

## Goal

A separate web app on its own port where the operator sees what Trunk is doing (ADR 0007). Nothing here
changes anything.

## Requirements

1. **App.** `apps/webui` as its own uv workspace member (`oaken-trunk-webui`, import `oaken_trunk_webui`),
   version read from the one shared place.
2. **Client only.** It calls the operation registry, adds no operation of its own, and never imports store
   or engine internals; import-linter enforces it.
3. **Access.** Own port and own token, separate from ingest and consume. Off by default; loopback unless the
   operator opts in; the token never reaches the browser.
4. **Pages.** Status, queue, leased messages, failures, configuration (read only), `doctor` results. Message
   bodies are never displayed or logged.

## Acceptance criteria

- With the UI off, nothing listens on its port. With it on, every page works against a `FakeSpool`.
- A test proves the UI cannot reach anything the CLI cannot.
- Standard checks pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
