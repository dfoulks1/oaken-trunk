+++
title = "Architecture overview"
subtitle = "Layers, the operation registry and what trunk is not"
lead = "How mail moves from an ingestor, through core, into a spool and out to consumers."
badges = [["text-bg-warning", "Pre-alpha"]]
description = "How the gateway is put together."
group = "concepts"
order = 10
+++

Oaken Trunk is a stateless gateway with a durable spool. The processes hold no state; the spool does.
Decisions are in [ADR 0002-0005](../adr).

```
 ingestors (plugins)      core                         spool (core/stores)   consumers
 HTTP submit   ----+                                                      +--> oaken-mail provider
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
| Spool | Store, lease, stream out, ack, nack, delete, notify. Core logic over store plugins (`oaken_trunk.stores`, ADR 0014). |
| Consumers | Anything that leases and acks. Outside trunk. |
| Senders | Relay outbound mail (`oaken_trunk.senders`), later. |

## One registry

Every capability is a registered operation (`submit`, `list`, `lease`, `fetch`, `ack`, `nack`,
`delete`, `status`, `doctor`, ...). The HTTP API exposes all of them, the CLI is a thin client of the API, and the MCP server is generated from
the same registry, so there is no second path to anything ([API and CLI](api-and-cli.md)). The CLI can also run
in-process without a daemon.

## Clients

The CLI (`steamer`) and the management UI are clients of the operation registry. The UI is a separate
app on its own port, off by default (ADR 0007). An optional MCP door is generated from the same registry and gated by caller class; it
shows statistics by default and never exposes message data or mutating operations without a deliberate
tier change (ADR 0008).

## What trunk is not

A no-server-side-mailbox spool. Trunk replaces Dovecot and the mailboxes behind it, and sits behind
Postfix or qmail rather than replacing them. Mail clients read over POP3 through a retriever plugin, and a
message is gone once every device has it: the client is the mailbox. No IMAP, no folders, no uploads, no
system mailboxes (`/var/mail`) and no spam filtering (ADR 0013).

## Memory rule

The gateway process never holds a whole message. Bodies move in fixed chunks (64 KiB). Load is bounded
at the door; overload gets a retryable 4xx (SMTP 451, HTTP 503 with `Retry-After`).
