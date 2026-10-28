# Foundations and contracts: paths, settings, ids, errors, and the shapes plugins and core agree on

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CORE.md`, `docs/architecture/ingestion.md`, `docs/architecture/spool.md`.
**Depends on:** [CORE_bootstrap](CORE_bootstrap.md).
**Lift:** L
**Delivers:** Paths, settings, the envelope, message ids, the error table, the Ingestor and Spool contracts, listener events, `Credits` and the test doubles
**Track:** `CORE_`. Data, config, shapes and fakes. No streaming behaviour, no I/O beyond the directories.

> **Status: In progress.** Built and green locally; waiting on review and CI. Open questions took
> their defaults. Where the code differs: the settings model covers every core table in
> `config.example.toml`; `[ingest.<name>]` and `[store.<name>]` pass through as plugin tables for
> CORE_plugin-host to validate. Unit-named keys (`lease_seconds`) also take a duration (`"5m"`).
> `commit` returns the delivery ids; `open` returns the delivery's envelope, annotations and a stream.
> Ids are Crockford base32 (26 characters), monotonic within a process. `n` in `<id>-<n>` starts at 1.

## Goal

The pieces everything else reads: where things live, how config loads, what a message is called, what an
error says, and the interfaces the engine, the spool and the plugins are built against separately. Nothing
here moves a message.

## Decided

- Settings are validated and strict. An unknown key is an error.
- `workers.count` and `workers.thread_count` default to 1. A count above 1 is refused until CORE_supervisor,
  and threads above 1 until a prompt tests them.
- Every error carries three codes: SMTP, HTTP and a `submit` exit code (sysexits, as Postfix reads them: 75
  temporary; 65, 67 or 77 permanent).
- A secret never lives in `config.toml`. It comes from a file, the environment or a secret manager.
- A spool stores through a writer. A message is visible only at `commit`, so listeners can annotate first.
- `commit` stores one body. Each queue entry is a delivery, `<id>-<n>`, and is the POP3 `UIDL`. With no
  registry yet there is one per recipient; the core spool (CORE_store) expands each recipient to one per
  device (ADR 0013). Lease, ack and nack work on deliveries.
- Ingestors reach the engine through the `submit` operation (CORE_operation-registry), never the spool.
- Listener events: `envelope`, `headers`, `end` (inline, time-bounded), `stored` (after durable). Listeners
  see headers and digests, never the body. They annotate only.
- Storage primitives and the core spool over them are CORE_store (ADR 0014). The Sender contract is
  CORE_send. The Authenticator contract is CORE_request-guard.

## Not in scope

Streaming and limits (CORE_engine). Plugin discovery, base classes and settings models (CORE_plugin-host).

## Requirements

**A. Foundations**

1. **Paths.** `OAKEN_TRUNK_HOME` gives `<dir>/config`, `<dir>/data`, `<dir>/run`. Unset on Linux:
   `/etc/oaken-trunk`, `/var/lib/oaken-trunk`, `/run/oaken-trunk`. Elsewhere platformdirs (development).
   Directories are owner-only. A world-writable one is refused. No last-known-home pointer.
2. **Settings.** pydantic-settings. Defaults < `config.toml` < `OAKEN_TRUNK_*`. An unknown key at any level
   is an error. Sizes (`25MiB`) and durations parse. A secret-named key (`password`, `token`, `secret`,
   `private_key`) is refused, and the error names the file or environment alternative.
3. **Envelope.** Mail from, recipients, `original_recipient` when the MTA gives one, client IP, HELO, TLS,
   principal, ingest surface, received time. Immutable. At commit each delivery gets its own envelope
   with its one recipient. How a spool keeps it is the spool's business.
4. **Addresses.** Normalise: lowercase the domain, keep the local part as given, keep `user+tag` as written.
   `[mail] local_domains` lists the domains Trunk accepts mail for.
5. **Message id.** 48-bit millisecond timestamp, 80 random bits, base32, standard library only. Ids sort by
   creation time and are unique. A delivery id is `<id>-<n>`, one per queue entry.
6. **Errors.** One table in code maps each condition to (SMTP, HTTP, exit): inflight limit, too large, spool
   full (`max_spool_bytes` or `max_deliveries`: `452 4.3.1`, HTTP 507, exit 75), spool unavailable, malformed,
   refused recipient (outside `local_domains` or no device: `550 5.1.1`, exit 67), unauthorised. A test fails
   if any lacks a code.

**B. Contracts**

7. **`Ingestor` and `Spool`.** Typed protocols, operations per `architecture/spool.md`. A spool stores through
   `writer(id, envelope)`, an async context manager with `write(chunk)` and `commit(annotations)`. Leaving the
   block without `commit` aborts: nothing becomes visible and temporary data is removed (`StoreAborted`).
   Annotations are an empty mapping until a listener supplies some, and are kept with the message.
8. **Listener events.** `EnvelopeEvent`, `HeadersEvent`, `EndEvent`, `StoredEvent`, a structured
   `ListenerResult`, and a `ListenerHost` protocol. No event type has a field that can hold body bytes.
9. **`Credits`.** The limiter interface: take, release, `retry_after_seconds` when none are left.
10. **Test doubles** in `oaken_trunk.testing`: `FakeSpool` (memory, tests only), `FakeIngestor`,
    `RecordingListenerHost`.
11. **Docs.** `config.example.toml`, `spool.md`, `plugins.md` if the shapes changed, `docs/softmap.toml`,
    status table.

## Acceptance criteria

- An unknown nested key, a secret-named key and `workers.count = 2` are each refused with a readable message.
  Environment beats file beats default.
- An address normalises as above. A delivery id is `<id>-<n>`.
- 10,000 ids are unique and sort by creation time. A world-writable directory is refused.
- Every error condition has all three codes.
- `FakeSpool` and `FakeIngestor` satisfy the protocols under `mypy`. A message written but not committed
  cannot be leased; an abort leaves nothing. No event type can carry body bytes (a test over the field types).
- `lint-imports` shows this imports no HTTP, CLI, registry or plugin module. Standard checks pass.

## Open questions (defaults in bold)

1. Linux layout as in requirement 1? **Yes.**
2. Envelope extras (trace id, HELO verification result)? **No. Add when a prompt needs one.**
3. What is an annotation value? **A JSON value, keyed by the listener's name.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
