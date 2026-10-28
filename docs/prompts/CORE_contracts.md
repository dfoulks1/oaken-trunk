# Contracts: the shapes plugins and core agree on

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CORE.md`, `docs/architecture/spool.md`.
**Depends on:** [CORE_foundations](CORE_foundations.md).
**Lift:** M
**Delivers:** Ingestor and Spool contracts with the writer, listener event types, `Credits`, and the test doubles
**Track:** `CORE_`. Shapes and fakes only. No behaviour.

## Goal

Pin the interfaces so the engine, the spool and the plugins can be built against them separately.

## Decided

- A spool stores through a writer. A message is visible only at `commit`, so listeners can annotate first.
  (Tentative.)
- `commit` makes one delivery per recipient and device (ADR 0013), sharing one body. Delivery ids are `<id>-<n>`.
  Lease, ack and nack work on deliveries.
- Ingestors reach the engine through the `submit` operation (CORE_operation-registry), never the spool.
- Listener events: `envelope`, `headers`, `end` (inline, time-bounded), `stored` (after durable). Listeners
  see headers and digests, never the body. They annotate only.
- Storage primitives and the core spool over them are CORE_store (ADR 0014). The Sender contract is CORE_send. The Authenticator contract is CORE_request-guard.

## Not in scope

The engine that drives them (CORE_engine). Plugin discovery and base classes (CORE_plugin-host). The directory
spool (PLUGIN_directory-spool).

## Requirements

1. **`Ingestor` and `Spool`.** Typed protocols, operations per `architecture/spool.md`. A spool stores through
   `writer(id, envelope)`, an async context manager with `write(chunk)` and `commit(annotations)`. Leaving the
   block without `commit` (an error, a cancel, a dropped stream) aborts: nothing becomes visible and the spool
   removes its temporary data (`StoreAborted`). Annotations are an empty mapping until a listener supplies some,
   and the spool keeps them with the message.
2. **Listener events.** `EnvelopeEvent`, `HeadersEvent`, `EndEvent`, `StoredEvent`, a structured
   `ListenerResult`, and a `ListenerHost` protocol. No event type has a field that can hold body bytes.
3. **`Credits`.** The limiter interface: take, release, `retry_after_seconds` when none are left.
   CORE_supervisor swaps in its own.
4. **Test doubles** in `oaken_trunk.testing`: `FakeSpool` (memory, tests only), `FakeIngestor`,
   `RecordingListenerHost`.
5. **Docs.** `spool.md`, `plugins.md` if the shapes changed, `docs/softmap.toml`, status table.

## Acceptance criteria

- `FakeSpool` and `FakeIngestor` satisfy the protocols under `mypy`.
- A message written but not committed cannot be leased. An abort leaves nothing and removes its data.
- No event type can carry body bytes (a test over the field types).
- `lint-imports` shows the contracts import only CORE_foundations. Standard checks pass.

## Open questions (defaults in bold)

1. What is an annotation value? **A JSON value, keyed by the listener's name.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
