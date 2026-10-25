# Contracts and core: the engine under limits

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CORE.md`, `docs/architecture/spool.md`,
`docs/architecture/ingestion.md`.
**Depends on:** [CORE_bootstrap](CORE_bootstrap.md).
**Track:** `CORE_`. The engine knows nothing of HTTP, the CLI or the registry (CORE_operation-registry, CORE_daemon).
**Delivers:** Ingestor and Spool contracts, envelope, ids, settings, paths, errors, the streaming engine under limits, listener events

## Goal

Stream a message from an ingestor into a spool under limits, with typed errors, settings, paths and
listener events. Prove it end to end with fakes.

## Decided

- One worker, one I/O thread (`workers`, `threads_per_worker`; default 1; higher is refused).
- Every error carries three codes: SMTP, HTTP, and a `submit` exit code (75 temporary, 65 or 77 permanent).
- Listener events: `envelope`, `headers`, `end` (inline, time-bounded), `stored` (after durable).
  Listeners see headers and digests, never the body. They annotate only.
- The Sender contract is 11. The Authenticator contract is 18.
- Tentative: a spool stores through a writer and a message is visible only at `commit`, so listeners can
  annotate first. Ingestors reach the engine through the `submit` operation (CORE_operation-registry), never the spool.
- Core is an async engine and pipeline fed by plugins. The engine owns the order of events and the commit.

## Not in scope

Registry, API, daemon (CORE_operation-registry, CORE_daemon, CORE_http-listener). Plugin discovery (CORE_plugin-host). Directory spool (PLUGIN_directory-spool). DKIM canonicalisation and
the mail-authentication listeners (CORE_mail-authentication). Supervisor (CORE_multi-worker). Audit and stats. Any ingest protocol.

## Requirements

1. **Paths.** `OAKEN_TRUNK_HOME` gives `<dir>/config`, `<dir>/data`, `<dir>/run`. Unset on Linux:
   `/etc/oaken-trunk`, `/var/lib/oaken-trunk`, `/run/oaken-trunk`. Elsewhere platformdirs (development).
   Directories are owner-only. A world-writable one is refused. No last-known-home pointer.
2. **Settings.** pydantic-settings. Defaults < `config.toml` < `OAKEN_TRUNK_*`. An unknown key at any level
   is an error. Sizes (`25MiB`) and durations parse. A secret-named key (`password`, `token`, `secret`,
   `private_key`) is refused, and the error names the file or environment alternative.
3. **Envelope.** Mail from, recipients, client IP, HELO, TLS, principal, ingest surface, received time.
   Immutable. How a spool keeps it is the spool's business.
4. **Message id.** 48-bit millisecond timestamp, 80 random bits, base32, standard library only. Ids sort
   by creation time and are unique.
5. **Contracts.** `Ingestor` and `Spool` as typed protocols (operations per `architecture/spool.md`).
   A spool stores through `writer(id, envelope)`, an async context manager with `write(chunk)` and
   `commit(annotations)`. The message is visible only after `commit`. Leaving the block without it (an error,
   a cancel, a dropped stream) aborts: nothing becomes visible and the spool removes its temporary data
   (`StoreAborted`). Annotations are an empty mapping until a listener supplies some. The spool keeps them
   with the message.
6. **Errors.** One table in code maps each condition to (SMTP, HTTP, exit): inflight limit, too large, spool
   full, spool unavailable, malformed, refused recipient, unauthorised. A test fails if any lacks a code.
7. **Limiter.** `max_inflight` behind a small `Credits` interface (CORE_multi-worker swaps in the supervisor's). Take
   a slot before the first chunk. Release on success, failure and cancellation. Over the limit is the
   retryable error with `retry_after_seconds`.
8. **Engine.** `ingest(envelope, chunks)` (what `submit` will call) assigns the id, re-chunks to at most 64 KiB (a constant), stops
   reading at the first byte over `max_message_size`, checks `usage()` against `max_spool_bytes` before
   `store`, and holds at most one chunk plus the header block.
9. **Header block and digest.** Keep the bytes up to the first blank line, bounded by `max_header_bytes`
   (default 64 KiB; over is a permanent refusal). Compute a raw SHA-256 of the body through named digest
   taps (19 adds more).
10. **Listener events.** `EnvelopeEvent`, `HeadersEvent`, `EndEvent`, `StoredEvent`, a structured
    `ListenerResult`, and an injected `ListenerHost` (default none). Inline events time out. An error or
    timeout is recorded and ingestion carries on. `stored` runs after durable and never changes the
    answer. No event carries body bytes.
11. **Test doubles** in `oaken_trunk.testing`: `FakeSpool` (memory, tests only), `FakeIngestor`,
    `RecordingListenerHost`.
12. **Docs.** `config.example.toml`, `docs/softmap.toml`, changed architecture pages, status table.

## Acceptance criteria

- 1 GiB of synthetic data streams into `FakeSpool` with chunks of at most 64 KiB and a traced peak
  allocation under 8 MiB.
- A message of exactly `max_message_size` is accepted. One byte more is refused and the source was not read
  to its end.
- A stream that fails partway leaves no visible message, and the error carries all three codes.
- A message written but not yet committed cannot be leased. It becomes leasable only after the `end`
  listeners have run and `commit` returns.
- `max_inflight + 1` concurrent ingests refuse the extra one with `retry_after_seconds`. The slot is free
  after success, failure and cancellation.
- An unknown nested key, a secret-named key and `workers = 2` are each refused with a readable message.
  Environment beats file beats default.
- 10,000 ids are unique and sort by creation time. A world-writable directory is refused.
- A slow inline listener times out, the timeout is recorded, ingestion succeeds. A failing `stored` listener
  changes nothing. No event carries body bytes.
- `lint-imports` shows the engine imports no HTTP, CLI or registry module. Standard checks pass, with no
  network, Docker or real mail.

## Open questions (defaults in bold)

1. Linux layout as in requirement 1. **Yes.**
2. Envelope extras (trace id, HELO verification result)? **No. Add when a prompt needs one.**
3. Chunk size configurable? **No.**
4. Exact quota (reserved bytes)? **03 and 10. Engine check only here.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
