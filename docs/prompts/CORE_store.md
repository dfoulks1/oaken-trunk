# Store: storage primitives, and the spool and coordination core builds on them

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CORE.md`, ADR 0003, ADR 0004, ADR 0013, ADR 0014, `docs/architecture/spool.md`.
**Depends on:** [CORE_plugin-host](CORE_plugin-host.md), [CORE_supervisor](CORE_supervisor.md).
**Lift:** L
**Delivers:** `BaseStore` and its primitives, and the core spool, `Locks`, `Credits`, `NonceStore` and device registry built on them
**Track:** `CORE_`. A store plugin implements primitives only; everything else here is core.

## Goal

Write lease, ack, fan-out, cleanup, locks and counters once, so a storage backend is a few primitives and a
passing contract suite.

## Decided

- Primitives (ADR 0014): `blob_put(key, chunks)`, `blob_open(key)`, `blob_drop(key)`; `cas(key, expect,
  new, ttl=None) -> bool` on small values; `index_add(name, member, score)`, `index_remove(name, member)`,
  `index_range(name, lo, hi, limit)`; optional `watch(name)`. Blobs stream in bounded chunks (ADR 0003).
- Roles: `[store] bodies`, `queues`, `coordination` each name a configured store. One store may fill all three.
- Layout is core's: `body/<id>`, `meta/<id>/<n>`, index `dev/<device>` (queue, scored by arrival),
  index `lease/<device>` (scored by expiry), `ref/<id>` (holder count, by `cas`).
- A store may override `commit`, `lease`, `ack`, `nack` or `renew` for speed and must still pass the suite.

## Not in scope

The operations (CORE_consumer-api). Each backend (PLUGIN_directory-spool, PLUGIN_redis-spool,
PLUGIN_s3-sqs-spool). The checkup schedule (CORE_audit-and-jobs).

## Requirements

**A. Primitives and contract**

1. **`BaseStore`.** The primitives above, capabilities inferred from overrides, lenient returns (ADR 0006).
   Entry point `oaken_trunk.stores`.
2. **`StoreContract`.** Each primitive: streaming and memory, `cas` is atomic under concurrent callers,
   index order and bounds, `blob_drop` is idempotent. `FakeStore` (memory) passes it.

`compact`

**B. The spool, in core**

3. **Write and commit.** The `writer` of CORE_contracts over `blob_put`. `commit` writes meta, then one queue
   entry per (recipient, device) and the holder count, so a delivery is visible at its entry.
4. **Lease, ack, nack, renew.** A claim is `cas` on the entry's lease key plus `index_add` to `lease/<device>`.
   Ack removes the entry and decrements `ref/<id>`; at zero the body and meta are dropped. Nack and expiry
   return the entry. Exclusive within a device, never across devices (ADR 0013).
5. **Caps.** `max_spool_bytes`, `max_deliveries`, `max_devices` counted with `cas` counters, corrected by a
   rescan. Over a cap is the retryable refusal of CORE_engine.
6. **Checkup steps.** Reap expired leases, expire devices and their queues, drop bodies with no holder,
   rescan. Exposed for CORE_audit-and-jobs to schedule.
7. **One suite.** The spool suite that `FakeSpool` (CORE_contracts) passes runs against the core spool over
   `FakeStore` and over each store plugin.

`compact`

**C. Coordination, in core**

8. **`Locks`, `Credits`, `NonceStore`.** Built on the `coordination` store's `cas` with TTLs. CORE_supervisor
   uses them across workers and hosts; in-memory at one worker.
9. **Device registry.** Devices, their recipients and last-used, on the `coordination` store.
10. **Docs.** `spool.md` (primitives, roles, layout), `plugins.md` (a store in one screen), ADR 0006 amended,
    `config.example.toml` (`[store]`), softmap, status table.

## Acceptance criteria

- The spool suite passes over `FakeStore`: fan-out to three devices shares one body; each acks alone; the
  body is gone after the last ack; nothing is leasable before commit; a crash between steps leaves the
  message committed or absent.
- Two concurrent claims on one entry: exactly one wins. A lock with a TTL frees itself.
- A store that overrides `ack` passes the same suite.
- A 1 GiB body streams through with chunks of at most 64 KiB. Standard checks pass.

## Open questions (defaults in bold)

1. Meta in the body blob or its own key? **Its own key, so annotations change without rewriting the body.**
2. Is `index_range` paged? **Yes, `limit` plus a cursor score.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
