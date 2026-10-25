# Foundations: paths, settings, ids, errors

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CORE.md`, `docs/architecture/ingestion.md`.
**Depends on:** [CORE_bootstrap](CORE_bootstrap.md).
**Lift:** M
**Delivers:** Paths, settings, the envelope, message ids and the error table
**Track:** `CORE_`. Data and config only. No streaming, no I/O beyond the directories.

## Goal

The pieces everything else reads: where things live, how config loads, what a message is called, what an
error says. Nothing here moves a message.

## Decided

- Settings are validated and strict. An unknown key is an error.
- `workers.count` and `workers.thread_count` default to 1. A count above 1 is refused until CORE_supervisor,
  and threads above 1 until a prompt tests them.
- Every error carries three codes: SMTP, HTTP and a `submit` exit code (75 temporary, 65 or 77 permanent).
- A secret never lives in `config.toml`. It comes from a file, the environment or a secret manager.

## Not in scope

The contracts (CORE_contracts). Streaming and limits (CORE_engine). Plugin settings models (CORE_plugin-host).

## Requirements

1. **Paths.** `OAKEN_TRUNK_HOME` gives `<dir>/config`, `<dir>/data`, `<dir>/run`. Unset on Linux:
   `/etc/oaken-trunk`, `/var/lib/oaken-trunk`, `/run/oaken-trunk`. Elsewhere platformdirs (development).
   Directories are owner-only. A world-writable one is refused. No last-known-home pointer.
2. **Settings.** pydantic-settings. Defaults < `config.toml` < `OAKEN_TRUNK_*`. An unknown key at any level
   is an error. Sizes (`25MiB`) and durations parse. A secret-named key (`password`, `token`, `secret`,
   `private_key`) is refused, and the error names the file or environment alternative.
3. **Envelope.** Mail from, recipients, `original_recipient` when the MTA gives one, client IP, HELO, TLS,
   principal, ingest surface, received time. Immutable. At commit each recipient becomes its own delivery
   with its own envelope (one recipient). How a spool keeps it is the spool's business.
4. **Addresses.** Normalise: lowercase the domain, keep the local part as given, keep `user+tag` as written.
   `[mail] local_domains` lists the domains Trunk accepts mail for.
5. **Message id.** 48-bit millisecond timestamp, 80 random bits, base32, standard library only. Ids sort by
   creation time and are unique. A delivery id is `<id>-<n>`, one per recipient.
6. **Errors.** One table in code maps each condition to (SMTP, HTTP, exit): inflight limit, too large, spool
   full, spool unavailable, malformed, refused recipient, unauthorised. A test fails if any lacks a code.
7. **Docs.** `config.example.toml`, `docs/softmap.toml`, status table.

## Acceptance criteria

- An unknown nested key, a secret-named key and `workers.count = 2` are each refused with a readable message.
  Environment beats file beats default.
- An address normalises as above. A delivery id is `<id>-<n>`.
- 10,000 ids are unique and sort by creation time. A world-writable directory is refused.
- Every error condition has all three codes.
- `lint-imports` shows this imports no HTTP, CLI, registry or plugin module. Standard checks pass.

## Open questions (defaults in bold)

1. Linux layout as in requirement 1? **Yes.**
2. Envelope extras (trace id, HELO verification result)? **No. Add when a prompt needs one.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
