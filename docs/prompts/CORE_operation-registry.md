# Operation registry: the command path

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CORE.md`, `docs/architecture/api-and-cli.md`,
`docs/architecture/ai-safety.md`, ADR 0008 and 0009.
**Depends on:** [CORE_contracts-and-core](CORE_contracts-and-core.md).
**Track:** `CORE_`. Model: oaken-mail's `oaken/core/operations/` (`registry`, `gate`, `exposure`,
**Lift:** L
**Delivers:** Typed operations, surfaces, confirm gate, schemas, `submit` and `version`; the command path
`caller`, `context`, `client`). The registry imports no API, CLI or UI module.

## Goal

Define each capability once, as a typed operation. The API, CLI, UI and MCP are generated from the
registry, so they cannot drift. The safety rules live here, in code.

## Decided

- The registry lives in core and ships in the core wheel. It is the command path (the engine is the data path).
- Ingestors enter through the `submit` operation, called in-process. They never touch the spool.
- Plugins add operations with `@command` (CORE_plugin-host adapts them). A core name can never be overridden.
- Mail-flow successes are counted, not audited. Everything else is audited.
- An operation belongs to one **surface** (`ingest`, `consume`, `admin`) and a principal belongs to one.

## Not in scope

The daemon and the HTTP listener (CORE_daemon, CORE_http-listener). The plugin host and `@command` (CORE_plugin-host). The guard and keys (CORE_request-guard). The
operations themselves, except `version` and `submit` (CORE_system-operations, CORE_consumer-api).

## Requirements

1. **`Operation`.** `name`, `summary`, pydantic `Input` and `Output`, `surface`, `permission` (`read` or
   `mutate`), async `handler(ctx, input)`, `mcp` (`off` or `never`), `needs_daemon`, optional `preview`.
2. **Registry.** Register and look up by name. A duplicate name is refused. Plugin operations are namespaced
   `plugin.verb` and cannot collide with a core name.
3. **`OpContext`.** The narrow, typed services a handler gets (engine, spool, settings, plugins, audit, clock,
   caller). A handler never receives a secret.
4. **Caller class.** `local`, `remote`, `ui`, `mcp`, `plugin`. The door sets it. Nothing in the input can
   declare or raise it.
5. **Confirm gate.** A `mutate` operation from a caller that needs confirmation returns a proposal (what would
   change) and a short-lived single-use token. Only the second call with the token runs it.
6. **Schemas.** JSON Schema and an OpenAPI 3.1 fragment come from the models. A snapshot test fails when an
   operation's schema changes until the snapshot is regenerated.
7. **Streams.** An operation can take or return an async chunk stream (`submit`, `fetch`) with no buffering.
8. **Errors.** The registry maps the error table of CORE_contracts-and-core to each door's code. An unexpected exception becomes an
   `internal` error with a correlation id and no content.
9. **Audit hook.** Calls go to an `AuditSink` (a no-op here, SQLite in CORE_audit-and-jobs): operation, caller class,
   principal, outcome. Mail-flow successes (`submit`, `lease`, `ack`, `nack`) are counted in stats, not
   audited. Every other call and every refusal is audited. Never message content or a secret input.
10. **In-process call.** `Registry.call(name, input, caller)` serves ingestors, tests and offline use. An
    operation with `needs_daemon = true` is refused when there is no engine.
11. **First operations.** `version` (offline), `submit` (wired to `engine.ingest`), `reload` and `stop`
    (through a `Lifecycle` interface in `OpContext` that CORE_daemon implements).
12. **Docs.** `api-and-cli.md`, `docs/softmap.toml`, status table.

## Acceptance criteria

- A duplicate name is refused. A plugin operation named like a core one is refused.
- A `mutate` call without confirmation changes nothing and returns a proposal. The token works once, expires,
  and fails for a different input.
- `submit` streams 100 MiB through the registry into `FakeSpool` with the memory bound of CORE_contracts-and-core.
- An audit record is written for every audited call (control operations and every refusal). A sentinel placed in a message body and in a secret input never
  appears in it.
- No input field can change the caller class.
- A changed schema fails the snapshot test. An operation with `needs_daemon = true` is refused offline, and
  `version` runs.
- `lint-imports` shows the registry imports no API, CLI or UI module. Standard checks pass.

## Planned core operations

For the API layer. This prompt builds `version`, `submit`, `reload` and `stop`.

| Prompt | Operations |
|---|---|
| CORE_operation-registry | `version`, `submit`, `reload`, `stop` |
| CORE_system-operations | `init`, `doctor`, `status`, `stats`, `get_config`, `check_config`, `save_config` |
| CORE_supervisor | `list_workers`, `get_worker`, `add_worker`, `delete_worker`, `start_worker`, `stop_worker`, `restart_worker`, `run_on_worker` |
| CORE_plugin-host | `list_plugins`, `plugin_health`, `set_plugin_enabled` |
| CORE_audit-and-jobs | `audit`, `list_jobs` |
| CORE_consumer-api | `lease`, `fetch`, `ack`, `nack`, `renew`, `list`, `delete` |
| CORE_request-guard | `keys_add`, `keys_list`, `keys_revoke` |

## Open questions (defaults in bold)

1. Permission classes beyond `read` and `mutate`? **No. Per-operation `mcp` and `surface` carry the rest.**
2. Confirmation for the human CLI? **The CLI sends `--yes`; MCP always gets the two-phase flow.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
