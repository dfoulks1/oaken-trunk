+++
title = "Spool"
subtitle = "The spool contract and the directory driver"
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
| `lease(consumer, limit, seconds)` | Reserve up to `limit` messages for a visibility timeout. Returns ids and lease tokens. |
| `open(id)` | Stream the bytes of a leased message. |
| `ack(id, token)` | The consumer is done; remove the message. |
| `nack(id, token)` | Return the message to the queue. |
| `delete(id)` | Remove regardless of lease (operator action, audited). |
| `watch()` | Wake consumers: inotify on directories, a poll otherwise. Never an in-process-only event. |
| `usage()` | Message count and bytes, for the quota and `status`. |

`annotations` are results listeners recorded (empty until one does). The spool keeps them with the message
and hands them back with `open`. How a driver keeps them is its own business (PLUGIN_directory-spool settles it for the
directory driver).

Delivery is at-least-once (ADR 0004). Expired leases return to the queue. Ids are time-ordered and
unique, so consumers dedupe on them.

## Directory driver (default)

Maildir-like. One body file of raw RFC 822 bytes, and one delivery per recipient, each a hard link to the body.

```
spool/tmp/<id>.msg                       being written
spool/new/<id>-<n>.msg                   ready (a hard link per recipient)
spool/leased/<id>-<n>.<expiry>.<token>.msg leased; the name carries the lease
spool/meta/<id>-<n>.json                 envelope and annotations; never moves
```

- **Write and commit:** write to `tmp/`; on `commit`, write each delivery's `meta/` file, fsync (per durability), rename into `new/`, fsync the
  directory, ack.
- **Lease:** atomic rename `new/` to `leased/` with expiry and token in the name. Two consumers
  cannot lease the same file.
- **Ack:** unlink. **Nack:** rename back to `new/`. **Recovery:** at start, delete stale `tmp/`
  files, return expired leases to `new/`, and delete annotations that have no message.

### Durability

| Mode | Behaviour | Loss window |
|---|---|---|
| `strict` (default) | fsync file and directory per message before the 250 | none for accepted mail |
| `batched` | concurrent messages share one fsync; the 250 follows that batch | none, small latency |
| `volatile` | no fsync | everything in flight |

A tmpfs mount is the operator's choice for the same driver, not a separate driver.

### Quota

`max_spool_bytes` caps total size. At the limit, new mail gets a retryable 4xx (HTTP 507). Workers reserve bytes as credits from the supervisor, so the cap is exact in aggregate; a periodic rescan corrects drift.

## Other drivers (planned)

Redis (queues and coordination across hosts, small bodies) and S3 (bodies at scale, queues by prefix, SQS
as an optional wake-up). Both implement the same primitives. They are not RAM-resident drivers of trunk, and each decides durability itself.
