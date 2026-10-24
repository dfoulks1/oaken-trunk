# 8. The MCP door is generated from the whole registry and gated by caller class

- Status: accepted
- Date: 2026-10-24

## Context

Oaken Mail generates its MCP server from its operation registry and decides what a model may do with a
caller class set by the mount, not by the client (its ADR 0004). Trunk's operations also touch mail in
flight, and the text of a message (sender, recipient, subject) is untrusted and can carry prompt injection.

## Decision

The MCP door is generated from every operation in the registry, so it never drifts from the API. What a
model can call is decided by a caller-class policy in code:

- The mount fixes the caller class `mcp`. A client cannot declare or raise it.
- **Default tier is statistics**: counts, depths, usage, health and `doctor` results. Wider tiers are an
  explicit operator opt-in and are described in the AI safety page.
- Anything that changes state needs the two-phase confirm gate in code, never a prompt.
- `submit`, `send`, `delete`, `lease`, `fetch`, `ack` and `nack` are never exposed over MCP.
- Message bodies and envelope fields are never returned without a deliberate tier change and an ADR.
- Off by default, its own signing key, audited on every call. It may share the management UI's listener on its
  own path, because the guard is per surface; it is always authenticated and, by default, local-only
  (`mcp.local_only = true` refuses non-loopback peers even with a valid signature).

## Consequences

A new operation is available on the API and CLI at once, and invisible to MCP until the policy admits it.
The policy and its tests live in core, not in a separate process. Raising the default tier needs an ADR.
