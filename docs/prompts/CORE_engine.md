# Engine: the streaming data path under limits

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CORE.md`, `docs/architecture/spool.md`,
`docs/architecture/ingestion.md`.
**Depends on:** [CORE_foundations](CORE_foundations.md).
**Lift:** L
**Delivers:** The engine: limiter, ingest pipeline, header block and digest, listener dispatch and the commit
**Track:** `CORE_`. The engine knows nothing of HTTP, the CLI or the registry.

## Goal

Stream a message from an ingestor into a spool under limits, fire the listener events in order, and commit.
Prove it end to end with fakes.

## Decided

- One worker, one I/O thread.
- Core is an async engine and pipeline fed by plugins. The engine owns the order of events and the commit.
- An inline listener that errors or times out is recorded, and ingestion carries on. `stored` never changes
  the answer.
- The chunk size is a constant (64 KiB), not a setting.

## Not in scope

The registry and `submit` (CORE_operation-registry). The daemon and listeners (CORE_daemon,
CORE_http-listener). Plugin discovery (CORE_plugin-host). The directory spool (PLUGIN_directory-spool). DKIM
(CORE_mail-authentication). The supervisor (CORE_supervisor). Audit and stats.

## Requirements

1. **Limiter.** `max_inflight` behind `Credits`, in memory here. Take a slot before the first chunk. Release on
   success, failure and cancellation. Over the limit is the retryable error with `retry_after_seconds`.
2. **Ingest.** `ingest(envelope, chunks)` (what `submit` will call) assigns the id, re-chunks to at most 64 KiB,
   stops reading at the first byte over `max_message_size`, checks `usage()` against `max_spool_bytes` and
   `max_deliveries` (ADR 0013) before writing, and holds at most one chunk plus the header block.
3. **Recipients.** Each recipient is checked against `[mail] local_domains` and must have at least one
   registered device (CORE_store's registry); otherwise it is an unknown user, as Dovecot treats one. The
   result is per recipient, accepted or refused (65, refused recipient). Only accepted ones are committed. None accepted is the
   refusal. An empty `local_domains` accepts nothing, and `doctor` says so.
4. **Header block and digest.** Keep the bytes up to the first blank line, bounded by `max_header_bytes`
   (default 64 KiB, over is a permanent refusal). Compute a raw SHA-256 of the body through named digest taps
   (CORE_mail-authentication adds more).

`compact`

5. **Listener dispatch.** Through `ListenerHost`, default none: `envelope`, `headers`, `end` inline with
   timeouts, then `commit(annotations)`, then `stored`. The `end` listeners run before the message is
   visible. No event carries body bytes.
6. **Docs.** `ingestion.md`, `spool.md`, `docs/softmap.toml`, status table.

## Acceptance criteria

- 1 GiB of synthetic data streams into `FakeSpool` in chunks of at most 64 KiB with a traced peak allocation
  under 8 MiB.
- A message of exactly `max_message_size` is accepted. One byte more is refused and the source was not read to
  its end.
- Three recipients, one outside `local_domains`: two deliveries commit, one is refused with its code. No
  accepted recipient is a refusal and nothing is stored.
- A stream that fails partway leaves no visible message, and the error carries all three codes.
- A message written but not committed cannot be leased. It is leasable only after the `end` listeners have run
  and `commit` returns.
- `max_inflight + 1` concurrent ingests refuse the extra one with `retry_after_seconds`. The slot is free
  after success, failure and cancellation.
- A slow inline listener times out, the timeout is recorded, ingestion succeeds. A failing `stored` listener
  changes nothing.
- `lint-imports` shows the engine imports no HTTP, CLI or registry module. Standard checks pass.

## Open questions (defaults in bold)

1. Exact quota (reserved bytes)? **Engine check only here. The spool and CORE_supervisor do the rest.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
