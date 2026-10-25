+++
title = "API and CLI"
subtitle = "One registry, one API, every door"
lead = "Every capability is one operation. The HTTP API exposes all of them; the CLI and the MCP server are doors onto it."
badges = [["text-bg-warning", "Pre-alpha"]]
description = "How the operation registry, the HTTP API, the CLI and MCP fit together."
group = "concepts"
order = 15
+++

## The shape

```
   CLI (steamer)      management UI        MCP clients
          \                   |                  /
           +------- HTTP API (every operation) --+
                            |
                  operation registry  <-- plugins add operations
                            |
                          core
```

Decisions are in [ADR 0009](repo:docs/adr/0009-the-api-is-the-one-door.md).

## The CLI

A thin client with no logic of its own, built like Oaken Mail's:

- **argparse from the standard library**, lazy imports, so `--help` is fast.
- **Every operation is reachable**: `steamer operation NAME --json '{...}'` runs any of them, and
  `steamer operation` lists them. Hand-written verbs cover the daily ones (`status`, `submit`, `lease`,
  `ack`, `nack`, `list`, `doctor`, `init`, `start`, `stop`).
- **Flags come from the operation's input schema.** `foo_bar` becomes `--foo-bar`, a list is a repeated
  flag, an enum limits the choices. A secret field gets no value flag (it would land in shell history), only
  `--NAME-stdin`.
- **Plugin operations** appear as `steamer PLUGIN VERB`.
- `--json` on any command gives machine-readable output.
- **In-process mode** drives the registry without a daemon, for tests and one-shot use.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | ok |
| 1 | error |
| 2 | usage |
| 3 | trunk is not running |
| 4 | authentication failed |
| 5 | needs confirmation (re-run with `--yes`) |

## The MCP door

Generated from the same registry, so it never drifts from the API. What a model may call is a policy,
not a side effect of an operation existing: see [AI safety](ai-safety.md).
