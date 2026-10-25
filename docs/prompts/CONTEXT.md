# Shared context and master list (read this before every prompt)

The contract for working here. If a prompt and this file disagree, **stop and report**.
To run, request or change a prompt, see [CONTRIBUTING.md](../../CONTRIBUTING.md#contributing-with-prompts).
[`TEMPLATE.md`](TEMPLATE.md) is the format for a new one.

## What we are building

**Oaken Trunk** is a small, stateless mail gateway. It takes mail in (SMTP, LMTP, HTTP, pipe), streams
it to a spool on disk, and lets consumers lease, process and ack it. It replaces the local *delivery*
step (the LDA role): no mailbox, no IMAP, no index. Light enough to run beside Postfix or qmail.
Oaken Mail is one consumer, through a plugin in its own repository. Apache-2.0.

```text
 ingestors (plugins)     HTTP submit    LMTP   SMTP   CLI stdin / pipe          PLUGIN_
            \                |             |      |        /
             +---------- core: authenticate, limits, stream to spool ----------+   CORE_
                                      |
              spool (plugin): directory (default), Redis, S3 + SQS               PLUGIN_
                                      |
          consumer API: lease -> fetch -> ack | nack (HTTP, CLI parity)          CORE_
                                      |
                       senders (plugin kind): outbound, later                    CORE_
```

## Master list and build order

In [INDEX.md](INDEX.md), generated from [`prompts.toml`](prompts.toml). Status words: **Built** (in `main`
with tests), **Open** (free to take), **Written** (a plan, waiting on its dependencies).

## How the files are named

`TRACK_name.md`. The name is the ID. It never changes when the order does. A prompt's file holds its
content. `prompts.toml` holds its dependencies and status. Write the plain name wherever you mention one.

| Track | Builds |
|---|---|
| `CORE_` | Contracts, engine, registry, daemon, plugin host, request guard, workers, send, mail authentication, hardening. A new plugin *kind*, core stage or operation is `CORE_`. |
| `PLUGIN_` | One first-party ingestor or spool. Changes core only at the touch points it lists. |
| `CLI_` | The `steamer` command. |
| `WEBUI_` | The management UI: its own app, never inside a core prompt. |
| `MCP_` | The optional MCP door. |
| `DOCS_` | The docs site and public docs. |

## Where things live

The code and tests are the truth about what exists. Then, in order:
[`docs/softmap.toml`](../softmap.toml) (built, partial or planned; never claim more),
[ADRs](../adr) (decisions costly to reverse), [architecture](../architecture/index.md)
(how each part behaves), [plugins](../plugins.md), [config.example.toml](../../config.example.toml),
[ROADMAP](../../ROADMAP.md), [CHANGELOG](../../CHANGELOG.md). A built prompt is history.
Checks: `scripts/check.sh`.

## Decided (every prompt)

What only one track needs is in [`context/`](context/CORE.md): one short file per track, named in each
prompt's "Read first".

- **Server side.** Network-facing, run by an operator. Secrets from files, the environment or a secret
  manager, never the OS keyring or `config.toml`. Hardened defaults.
- **Identity.** `OAKEN_TRUNK_HOME` (`<dir>/config/config.toml`, `<dir>/data`), env prefix `OAKEN_TRUNK_`,
  package `oaken_trunk`, CLI `steamer`, plugin groups `oaken_trunk.*`. Python 3.11+, uv, hatchling,
  ruff, `mypy --strict`, pytest, import-linter.
- **Standalone.** Trunk never imports oaken-mail; overlap and duplicated code are fine (ADR 0002).
- **A tool, not a project.** 0.1 works out of the box: `init` writes a config, `doctor` explains what is
  wrong, `status` shows the queue. Docs carry a Postfix snippet, a qmail pipe line and a systemd unit.
- **Coexistence.** LMTP (`virtual_transport = lmtp:unix:...`) and a pipe command.
- **Never a whole message in memory.** Bodies stream in fixed chunks, in every ingestor, spool and
  consumer path (ADR 0003).
- **One registry.** Every capability is an operation first. The HTTP API exposes all of them; the CLI,
  UI and MCP are doors onto it and hold no logic of their own (ADR 0006, 0009).
- **Logs carry no content,** and no operation, verb, tool or page returns them (ADR 0012).

## Rules for every prompt

- Docs are part of done: update the page you touch and `docs/softmap.toml`.
- Tests next to the code, no network, no Docker, no real mail. Never log a message body.
- Keep the repo green: `ruff check`, `ruff format --check`, `mypy`, `lint-imports`, `pytest`.
- Conventional Commits. Push only when asked. No dependency a prompt does not call for, unless you say why.
- If an ambiguity changes the design, stop and ask.

## Keep the session compact

- **Read what the prompt names:** this file and its track file. Not the folder, not generated files (`docs/**/*.html`, `uv.lock`,
  `__pycache__`), not other prompts. For what is built, read the status block at the top of its prompt
  and `docs/softmap.toml`, not the code.
- **Find, don't browse.** `grep` for the symbol. A search that would open more than a handful of files
  goes to a read-only subagent that returns the answer.
- **Do not re-derive** what is decided. Do not re-read an ADR to confirm it.
- **Quiet commands.** `-q`, then `| tail -20`. Do not re-read a file you just edited.
- **Write once.** From the requirements, not drafted in chat. Batch independent tool calls.
- **One prompt, one session.** Stop at the checkpoint and clear the conversation. The report-back and
  the status block are the handoff.
- **Compaction breaks.** A prompt with many parts marks `compact` lines between them. At one: checks green,
  status block updated, then compact the session and carry on.
- **Budget.** A prompt is about 150 lines and 12 requirements at most; more is two prompts. The
  report-back stays under about 40 lines.

## Report-back checkpoint

End your final message with: 1. **Done** 2. **Files** 3. **How I verified** 4. **Deviations**
5. **Open questions** 6. **Next prompt readiness**. Then stop.
