+++
title = "Spool"
subtitle = "The spool contract and the directory store"
lead = "Store, lease, ack and nack, how the default spool survives a crash, and what each durability mode costs."
badges = [["text-bg-warning", "Pre-alpha"]]
description = "The spool contract, durability modes and quota."
group = "concepts"
order = 20
+++

The spool is core logic over store plugins (ADR 0014). A store implements primitives: stream a blob in and
out, compare-and-set a small value, and keep ordered indexes. Core builds fan-out per device, leases, acks and
cleanup on them. `[store] bodies`, `queues` and `coordination` each name a store. The contract below is what
consumers see; where bytes live is the store's decision (ADR 0003).

## Contract

| Operation | Meaning |
|---|---|
| `writer(id, envelope)` | An async context manager: `write(chunk)` for each chunk, then `commit(annotations)`. The message is visible only after `commit`, which returns when it is durable per the driver's durability. Leaving the block without `commit` aborts and removes the partial data. |
| `lease(consumer, limit, seconds)` | Reserve up to `limit` of this device's deliveries for a visibility timeout. Returns delivery ids and lease tokens. |
| `open(id)` | Stream the bytes of a leased message. |
| `ack(id, token)` | The device is done; remove the delivery from its queue. The body goes when no queue holds it. |
| `nack(id, token)` | Return the delivery to its queue. |
| `delete(id)` | Remove regardless of lease (operator action, audited). |
| `watch()` | Wake consumers: inotify on directories, a poll otherwise. Never an in-process-only event. |
| `usage()` | Body bytes and delivery count, for the caps and `status`. |

`annotations` are results listeners recorded (empty until one does). The spool keeps them with the message
and hands them back with `open`. How a driver keeps them is its own business (PLUGIN_directory-spool settles it for the
directory driver).

Delivery is at-least-once (ADR 0004). Expired leases return to the queue. Ids are time-ordered and
unique, so consumers dedupe on them.

## Directory store (default)

One directory tree holds all three roles. Bodies are blobs that core seals before the store sees them
(ADR 0015), so a body file is ciphertext. Each device's queue is an ordered index of delivery ids that point
at one shared blob (ADR 0013). The file layout is PLUGIN_directory-spool's to settle.

- **Write and commit:** write the sealed blob to `tmp/`, fsync (per durability), rename into place, fsync the
  directory, then add one entry per delivery to each queue, then reply.
- **Lease:** compare-and-set on the entry, with expiry and token, so two consumers cannot lease the same
  delivery.
- **Ack:** remove the entry. **Nack:** clear the lease. **Recovery:** at start, delete stale `tmp/` files,
  return expired leases, and drop blobs and annotations no queue names.

### Durability

| Mode | Behaviour | Loss window |
|---|---|---|
| `strict` (default) | fsync file and directory per message before the 250 | none for accepted mail |
| `batched` | concurrent messages share one fsync; the 250 follows that batch | none, small latency |
| `volatile` | no fsync | everything in flight |

A tmpfs mount is the operator's choice for the same driver, not a separate driver.

### Quota

`max_spool_bytes` caps body bytes and `max_deliveries` caps queue entries. At either, new mail gets
`452 4.3.1` (HTTP 507), which the sender retries; Trunk never bounces (ADR 0013). Workers reserve bytes as credits from the supervisor, so the cap is exact in aggregate; a periodic rescan corrects drift.

## Other drivers (planned)

Redis (queues and coordination across hosts, small bodies) and S3 (bodies at scale, queues by prefix, SQS
as an optional wake-up). Both implement the same primitives. They are not RAM-resident drivers of trunk, and each decides durability itself.
