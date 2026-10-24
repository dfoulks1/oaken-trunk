+++
title = "Spool"
subtitle = "The spool contract and the directory driver"
lead = "Store, lease, ack and nack, how the default spool survives a crash, and what each durability mode costs."
badges = [["text-bg-warning", "Pre-alpha"]]
description = "The spool contract, durability modes and quota."
group = "concepts"
order = 20
+++

A spool is a plugin. The contract is a bounded stream in and a stream out; where bytes live is the
plugin's decision (ADR 0003).

## Contract

| Operation | Meaning |
|---|---|
| `store(id, chunks, envelope)` | Persist a message from an async stream of chunks. Returns only when it is durable per the driver's durability. |
| `lease(consumer, limit, seconds)` | Reserve up to `limit` messages for a visibility timeout. Returns ids and lease tokens. |
| `open(id)` | Stream the bytes of a leased message. |
| `ack(id, token)` | The consumer is done; remove the message. |
| `nack(id, token)` | Return the message to the queue. |
| `delete(id)` | Remove regardless of lease (operator action, audited). |
| `watch()` | Wake consumers: inotify on directories, a poll otherwise. Never an in-process-only event. |
| `usage()` | Message count and bytes, for the quota and `status`. |

Delivery is at-least-once (ADR 0004). Expired leases return to the queue. Ids are time-ordered and
unique, so consumers dedupe on them.

## Directory driver (default)

Maildir-like, one file per message: the first line is the JSON envelope, the rest is the raw
RFC 822 bytes.

```
spool/tmp/<id>.msg                       being written
spool/new/<id>.msg                       ready
spool/leased/<id>.<expiry>.<token>.msg   leased; the name carries the lease
```

- **Store:** write to `tmp/`, fsync (per durability), rename into `new/`, fsync the directory, ack.
- **Lease:** atomic rename `new/` to `leased/` with expiry and token in the name. Two consumers
  cannot lease the same file.
- **Ack:** unlink. **Nack:** rename back to `new/`. **Recovery:** at start, delete stale `tmp/`
  files and return expired leases to `new/`.

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

Redis stream with consumer groups, and S3 + SQS with visibility timeouts. Both map onto lease, ack and
nack. They are not RAM-resident drivers of trunk, and each decides durability itself.
