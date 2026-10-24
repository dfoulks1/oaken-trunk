# Overview

Oaken Trunk is a stateless gateway with a durable spool. The processes hold no state; the spool does.
Decisions are in [ADR 0002-0005](../adr/).

```
 ingestors (plugins)      core                         spool (plugin)        consumers
 HTTP /v1/send  ----+                                                      +--> oaken-mail provider
 CLI stdin      ----+--> authenticate -> limits -> --> store (stream) --+--> +--> CLI / webhook
 LMTP / pipe    ----+    stream chunks, never whole     lease/ack/nack   notify
 SMTP (planned) ----+
                                       senders (plugin) <-- outbound spool
```

## Layers

| Layer | Responsibility |
|---|---|
| Ingestion | Speak a protocol, hand a byte stream and an envelope to core. One plugin per protocol (`oaken_trunk.ingestors`). |
| Core | Authenticate, apply limits (`max_inflight`, `max_message_size`, `max_spool_bytes`), assign a message id, stream to the spool, answer the sender. |
| Spool | Store, lease, stream out, ack, nack, delete, notify (`oaken_trunk.spools`). |
| Consumers | Anything that leases and acks. Outside trunk. |
| Senders | Relay outbound mail (`oaken_trunk.senders`), later. |

## One registry

Every capability is a registered operation (`submit`, `list`, `lease`, `fetch`, `ack`, `nack`,
`delete`, `status`, `doctor`, ...). The HTTP API and the CLI are generated from it, so every endpoint
has a command and there is no second path to anything. The CLI can run in-process against the spool
without a daemon.

## What trunk is not

No IMAP or POP3, no mailbox search, no spam filtering, no web UI. It replaces local delivery, not
mailbox access, and sits beside Postfix or qmail rather than replacing them.

## Memory rule

The gateway process never holds a whole message. Bodies move in fixed chunks (64 KiB). Load is bounded
at the door; overload gets a retryable 4xx (SMTP 451, HTTP 503 with `Retry-After`).
