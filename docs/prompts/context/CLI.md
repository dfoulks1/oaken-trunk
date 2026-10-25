# Context: CLI_ prompts

Read with [CONTEXT.md](../CONTEXT.md). The `steamer` command (the project stays Oaken Trunk).

- **Thin.** argparse, lazy imports, so `--help` and `--version` are fast. All logic is in the registry.
- **Every operation is reachable:** `steamer operation NAME --json '{...}'`. Verbs and flags come from the
  operation's input schema. A secret field has only `--NAME-stdin`. Plugin operations are
  `steamer PLUGIN VERB`. `--json` gives machine output.
- **One command.** `steamer start` runs the daemon. The rest is the client, over the Unix socket.
- **Offline.** `init`, `version` and the offline part of `doctor` need no daemon. In-process is an explicit
  flag, never a fallback, and `submit` refuses it.
- **Exit codes:** 0 ok, 1 error, 2 usage, 3 not running, 4 authentication failed, 5 needs confirmation.
- **`submit`** reads stdin and is the qmail and Postfix pipe target. Core `submit` exits as sysexits:
  0 accepted, 75 temporary (daemon down included), 65 or 77 permanent. An MTA with other rules gets its own
  command from a plugin: `steamer qmail submit` (0, 111 temporary, 100 permanent) and `steamer postfix submit`.
  The plugin declares the exit map as data, and the CLI applies it. No direct-to-spool bypass. Verify the tables
  against `pipe(8)` and `qmail-command(8)` when documenting.
- Reference: `architecture/api-and-cli.md`.
