# 7. The management UI is a separate client on its own port

- Status: accepted
- Date: 2026-10-24

## Context

Trunk is server-side software run by an operator, who needs to see queue depth, spool usage, leases and
failures, and to act on them. Oaken Mail solved the same shape by keeping its web UI a separate client
of the core API (its ADR 0007). Trunk and Oaken Mail are separate projects, and some duplication between
them is accepted rather than coupling them.

## Decision

The management UI is its own app (`apps/webui`, package `oaken_trunk_webui`), served on its own port,
and a client of the same operation registry the CLI uses. Core stays headless and never imports it. Every
action in the UI is an operation that already has a CLI command. It is off by default, binds to loopback
unless the operator opts in, and has its own signing keys, separate from the ingest and consume keys. The MCP
door (ADR 0008) may share this listener on its own path, because each surface has its own guard, scheme and keys.

## Consequences

Core and the UI release and test independently. The UI needs no private access to the spool: anything it
shows is a registry operation, so it cannot do what the CLI cannot. Code shared in spirit with Oaken Mail
(site tooling, plugin base patterns) is copied, not imported.
