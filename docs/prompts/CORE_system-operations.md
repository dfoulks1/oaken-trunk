# System operations: the operator's basics

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CORE.md`, `docs/architecture/api-and-cli.md`,
`docs/architecture/logging.md`.
**Depends on:** [CORE_daemon](CORE_daemon.md), [CORE_supervisor](CORE_supervisor.md).
**Track:** `CORE_`. Model: oaken-mail's `core/operations/builtin/` and `core/config_edit.py`.
**Delivers:** `init`, `doctor`, `status`, `stats` and the config operations

## Goal

An operator can set Trunk up, see what it is doing, and see what is wrong, using only operations.

## Decided

- `init`, `doctor` and `version` work offline. The rest need the daemon.
- Logs and message content are never returned by any operation (ADR 0012).
- The CLI holds no logic of its own, so every verb here is an operation first.

## Not in scope

The audit store and jobs (CORE_audit-and-jobs). Keys (CORE_request-guard). Consumer verbs (CORE_consumer-api). Anything a plugin adds.

## Requirements

1. **`init`** (offline). Write a documented `config.toml` from `config.example.toml`, create the directories
   owner-only, never overwrite an existing config.
2. **`doctor`.** Check the config, permissions, listeners, spool path and free space, plugin health, and each
   surface's guard. Report each problem with the fix. Works offline for the checks that need no daemon.
3. **`status`.** Queue depth, bytes, quota, leases, listeners, plugin health, version, uptime.
4. **`stats`.** In-memory counters: accepted, refused (by reason), bytes, leases, acks, nacks. Reset on start.
5. **Config.** `get_config` (secrets absent), `check_config` (validate a candidate, report errors), `save_config`
   (validate, write atomically, reload what is reloadable, say what needs a restart).
6. **Sections and checks.** `status` and `doctor` are built from sections and checks that each subsystem
   registers. One that is not configured yet shows as `not configured`, not an error. CORE_plugin-host and
   later prompts add theirs.
7. **Redaction.** One redaction helper used by every operation here. A secret never leaves in an output.
8. **Exit codes.** Each failure maps to the CLI codes of `api-and-cli.md`.
9. **Docs.** Reference pages come from the registry. Softmap, status table.

## Acceptance criteria

- `init` on an empty home gives a config that `check_config` accepts and `doctor` passes, offline. A second
  `init` changes nothing.
- `doctor` names a world-writable directory, an unreachable spool path and a surface with no keys.
- `save_config` with a secret-named key is refused. A valid change reloads without a restart where marked.
- `get_config` and `status` never contain a configured secret (sentinel test).
- `stats` counts a refused message under its reason. Standard checks pass.

## Open questions (defaults in bold)

1. Which config keys reload live? **Limits and log level. Listeners and paths need a restart.**
2. Are counters persisted? **No. CORE_audit-and-jobs persists a rollup.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
