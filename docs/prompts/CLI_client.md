# CLI client: the early thin command

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CLI.md`, `docs/architecture/api-and-cli.md`.
**Depends on:** [CORE_daemon](CORE_daemon.md).
**Lift:** M
**Delivers:** The `steamer` command: start, stop, reload, a generic runner and verbs generated from schemas
**Track:** `CLI_`. Model: oaken-mail's CLI.

## Goal

One command to run and drive the daemon over its local socket, before most operations exist.

## Decided

- Everything in `context/CLI.md`: thin, one command, offline operations, exit codes, `submit` codes.
- Local socket only here. Remote use needs signing and the HTTP listener.

## Not in scope

Remote (TCP, signed) use. Hand-written verbs for operations later prompts add: they are generated.

## Requirements

1. **Entry point.** `steamer`, from the console script of CORE_bootstrap. argparse, lazy imports.
2. **Lifecycle verbs.** `steamer start` runs the daemon in the foreground (imported lazily). `stop` and
   `reload` call the operations.
3. **Generic runner.** `steamer operation NAME --json '{...}'`. `steamer operation` lists them.
4. **Generated verbs.** One per operation, flags from the input schema (`foo_bar` is `--foo-bar`, a list is a
   repeated flag, an enum limits the choices). A secret field has only `--NAME-stdin`. Plugin operations are
   `steamer PLUGIN VERB`.
5. **Socket client.** Find the socket from the runtime file or `--socket`. HTTP over the Unix socket. No logic.
6. **Output and exit codes.** `--json` on any command. Codes 0 to 5 as in `context/CLI.md`. A mutating
   operation needs `--yes`, or exits 5.
7. **`submit`.** Streams stdin. Exit 0, 75 or 65 and 77, as in `context/CLI.md`.
8. **Offline.** `init`, `version` and the offline part of `doctor` run with no daemon. `--in-process` is an
   explicit flag for offline operations only. `submit` refuses it.
9. **Docs.** The CLI reference is generated from the registry. `api-and-cli.md`, softmap, status table.

## Acceptance criteria

- `steamer version` runs offline. `steamer stop` with no daemon exits 3.
- `steamer submit` with the daemon down exits 75 and writes nothing anywhere.
- A test operation registered with no CLI code appears as a verb with the right flags.
- A secret field has no value flag. A mutate without `--yes` exits 5.
- `--in-process` on `submit` is refused. `--help` and `--version` import no daemon code.
- Standard checks pass, with no network, Docker or real mail.

## Open questions (defaults in bold)

1. Remote CLI (TCP, signed requests)? **A later prompt, after CORE_http-listener and CORE_request-guard.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
