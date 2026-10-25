# 9. The API exposes every operation; the CLI and MCP are doors onto it

- Status: accepted
- Date: 2026-10-24

## Context

Oaken Mail keeps one operation registry. Its HTTP API exposes every operation, its CLI is a thin client
of that API, and its MCP server is generated from the same registry (its ADR 0002, 0004 and 0006).
Trunk is a separate project and copies the shape rather than importing it (ADR 0002).

## Decision

- Every capability is one registered operation with a typed input schema. The **HTTP API** exposes all of
  them, so nothing is reachable any other way.
- The **CLI** (`steamer`, in the core wheel) is a thin client of the API and holds
  no logic. A generic `steamer operation NAME --json '{...}'` reaches any operation without a release,
  hand-written verbs are the friendly front end for daily ones, and flags are generated from each
  operation's input schema (a secret field has no value flag, only `--NAME-stdin`).
- An **in-process adapter** drives the same registry without a daemon, for tests and for one-shot use.
- The **MCP server** is generated from the same registry and is a second door, subject to the caller-class
  policy in ADR 0008 and `docs/architecture/ai-safety.md`.
- Plugins contribute operations, reachable as `steamer PLUGIN VERB`.
- Exit codes are a contract: 0 ok, 1 error, 2 usage, 3 not running, 4 auth, 5 needs confirmation.

## Consequences

A new operation is immediately usable from the API and the CLI. Whether a model can reach it is a separate,
explicit policy decision. The CLI depends on the API, not on core internals, except through the in-process
adapter, which import-linter permits as the one seam.
