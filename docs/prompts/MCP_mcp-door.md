# MCP door

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/MCP.md`.
**Depends on:** [CORE_operation-registry](CORE_operation-registry.md), [CORE_system-operations](CORE_system-operations.md), [CORE_http-listener](CORE_http-listener.md).
**Not part of 0.1.**
**Lift:** L
**Delivers:** Optional MCP door for diagnostics: off by default, each read-only operation enabled by name. Not part of 0.1

## Goal

An optional MCP door that lets a model read diagnostics and nothing else (ADR 0008), on the shape of
oaken-mail's per-operation MCP allow-list.

## Steps

1. Generate MCP tools from every registry operation; the mount fixes the caller class `mcp`, which a client cannot declare or raise.
2. Each operation declares `mcp = off | never`. Read-only diagnostic operations (`status`, `stats`,
   `doctor`, `devices`, `refusals`, `trace`) are `off`; everything that changes state or touches mail, keys or
   tokens is `never`. The operator enables operations one by one: `[mcp] allowed = ["status", "doctor"]`. A
   `never` operation in the list is a startup error.
3. Nothing is enabled by default, and the door itself is off by default.
4. No message body, envelope field, token or key is ever returned. Addresses follow `log.envelope`.
5. Off by default; its own token and signing key; audited on every call. Requests follow the signed-request rules of the security prompt (CORE_security-hardening).
6. Streamable HTTP transport, and a stdio bridge command as oaken-mail has.

## Acceptance criteria

- With an empty allow-list no tool is exposed. A `never` operation in `allowed` refuses to start. A new
  operation is `never` unless it declares otherwise.
- A test proves no response contains a message body, envelope field, token or key.
- A client cannot raise its caller class by any header or parameter.
- `ruff check`, `ruff format --check`, `mypy`, `lint-imports` and `pytest` pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Checkpoint

Use the report format from `CONTEXT.md`, then stop.
