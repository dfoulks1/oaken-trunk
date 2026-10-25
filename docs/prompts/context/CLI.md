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
- **`submit`** reads stdin and is the qmail and Postfix pipe target. 0 accepted. 75 (`EX_TEMPFAIL`) for any
  temporary failure, daemon down included, so the sender retries. 65 or 77 for a permanent refusal. No
  direct-to-spool bypass. Check the codes against Postfix `pipe(8)` and qmail when documenting.
- Reference: `architecture/api-and-cli.md`.
