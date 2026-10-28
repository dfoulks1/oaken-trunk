# MTA guides: qmail and Postfix

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/DOCS.md`, `docs/architecture/ingestion.md`.
**Depends on:** [PLUGIN_mta-adapters](PLUGIN_mta-adapters.md), [PLUGIN_lmtp-ingest](PLUGIN_lmtp-ingest.md), [CORE_request-guard](CORE_request-guard.md), [PLUGIN_pop3-retriever](PLUGIN_pop3-retriever.md).
**Lift:** M
**Delivers:** Tested guides for handing mail from qmail and Postfix to Trunk
**Track:** `DOCS_`. Pages and checked snippets only. No code.

## Goal

A mail admin can wire qmail or Postfix to Trunk from the page alone, and know what happens when it fails.

## Decided

- qmail first. qmail uses `steamer qmail submit`. Postfix uses the LMTP ingestor or `steamer postfix submit`
  (PLUGIN_mta-adapters).
- Every snippet is checked by `check_commands` against the real CLI flags.

## Not in scope

Any code. Other MTAs.

## Requirements

1. **qmail.** Which dot-file (`.qmail`, `.qmail-user-default`, a virtual domain's), the single delivery line
   (it must be the only or last line, or a deferral reruns the others), the absolute path to `steamer`, the
   `.qmail` line, the environment qmail passes (`SENDER`, `RECIPIENT`), the user it runs as and
   the key or socket access that user needs, the exit-code table, a test delivery, and what a refused or
   deferred message looks like in the qmail queue. Also: the delivering uid on the peer allow-list, dot-file
   and home permissions, the empty sender, the header lines qmail adds, and `--timeout` below qmail's patience.
   Verify the exit codes and variables against `qmail-command(8)`.
2. **Remote submit.** `--host` and `--port` with a signed key and TLS: creating the key, where the file lives,
   its permissions, and the `doctor` warning if it is group-readable.
3. **Postfix.** `virtual_transport = lmtp:unix:...`, and the `pipe(8)` form with `steamer postfix submit`.
4. **Addresses.** `local_domains`, per-recipient deliveries, and `consume` key recipient scope (addresses or `@domain`).
5. **Failure table.** Daemon down, spool full, refused recipient, bad signature: what each MTA does and what
   the admin sees. Include a consumer that is down: mail waits in the spool, the quota applies, and when it
   is full Trunk refuses with a retryable error.
6. **Reading mail.** A mail client points at the POP3 retriever (PLUGIN_pop3-retriever) with one app token per
   device; mail leaves Trunk once every device has deleted it. Oaken Mail pulls with its own Trunk source (built in the oaken-mail repo, link
   only). Show the consume key, its recipient scope and who can read the key file.

## Acceptance criteria

- Every command and flag on the pages exists, checked by `check_commands`. Exit-code tables match
  `pipe(8)` and `qmail-command(8)`, with the source named.
- A new reader follows the qmail page on a fresh install and a test message reaches `steamer lease`.
- `check_docs` passes.

## Open questions (defaults in bold)

1. One page per MTA, or one page with sections? **One page per MTA.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
