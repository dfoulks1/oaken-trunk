# 8. The MCP door is generated from the whole registry and gated by caller class

- Status: accepted, amended 2026-10-28 (diagnostics only, per-operation allow-list)
- Date: 2026-10-24

## Context

Oaken Mail generates its MCP server from its operation registry and decides what a model may do with a
caller class set by the mount, not by the client (its ADR 0004). Trunk's operations also touch mail in
flight, and the text of a message (sender, recipient, subject) is untrusted and can carry prompt injection.

## Decision

The MCP door is generated from every operation in the registry, so it never drifts from the API. What a
model can call is decided by a caller-class policy in code:

- The mount fixes the caller class `mcp`. A client cannot declare or raise it.
- **Diagnostics only, enabled one by one**, as oaken-mail does: each operation is `mcp = off` (the operator
  may enable it by name in `[mcp] allowed`) or `never`. Only read-only diagnostic operations are `off`.
  Nothing is enabled by default.
- Anything that changes state, or touches mail, keys or tokens, is `never` and cannot be enabled.
- Message bodies, envelope fields, tokens and keys are never returned.
- Off by default, its own signing key, audited on every call. It may share the management UI's listener on its
  own path, because the guard is per surface; it is always authenticated and, by default, local-only
  (`mcp.local_only = true` refuses non-loopback peers even with a valid signature).

## Consequences

A new operation is available on the API and CLI at once, and invisible to MCP until the policy admits it.
The policy and its tests live in core, not in a separate process. Making any operation that changes state
reachable over MCP needs a new ADR.
