# MCP door

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/MCP.md`.
**Depends on:** [CORE_operation-registry](CORE_operation-registry.md), [CORE_system-operations](CORE_system-operations.md), [CORE_http-listener](CORE_http-listener.md).
**Not part of 0.1.**
**Lift:** L
**Delivers:** Optional MCP door gated by caller class. Not part of 0.1

## Goal

An optional MCP door generated from the whole registry and gated by caller class (ADR 0008).

## Steps

1. Generate MCP tools from every registry operation; the mount fixes the caller class `mcp`, which a client cannot declare or raise.
2. Policy in code: statistics tier by default (`status`, queue depth, spool usage and quota, lease and failure counts, worker health, `doctor`); wider tiers are an explicit operator setting.
3. State-changing operations go through the two-phase confirm gate. `submit`, `send`, `delete`, `lease`, `fetch`, `ack` and `nack` are never exposed.
4. No message body and no envelope field is returned without a tier change that has its own ADR. Any mail-derived text is wrapped as untrusted.
5. Off by default; its own token and signing key; audited on every call. Requests follow the signed-request rules of the security prompt (CORE_security-hardening).
6. Streamable HTTP transport, and a stdio bridge command as oaken-mail has.

## Acceptance criteria

- A test lists the exposed tools and fails if any never-exposed operation appears or a new operation appears without the policy admitting it.
- A test proves no response contains a message body or envelope field at the default tier.
- A client cannot raise its caller class by any header or parameter.
- `ruff check`, `ruff format --check`, `mypy`, `lint-imports` and `pytest` pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Checkpoint

Use the report format from `CONTEXT.md`, then stop.
