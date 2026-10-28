+++
title = "Ingestion"
subtitle = "HTTP, CLI, LMTP and SMTP"
lead = "The ways mail gets in, how backpressure is reported, and how to sit beside Postfix or qmail."
badges = [["text-bg-warning", "Pre-alpha"]]
description = "How mail enters the gateway."
group = "concepts"
order = 40
+++

An ingestor speaks one protocol and gives core a byte stream and an envelope. Core does the rest.

| Ingestor | 0.1 | Notes |
|---|---|---|
| HTTP `POST /v1/ops/submit` | planned | `submit` on the ingest surface. Streaming request body. Signed requests. |
| CLI stdin | planned | `steamer submit < message.eml`; also the qmail pipe target. |
| LMTP | planned | Unix or TCP socket. The Postfix `virtual_transport` target. |
| SMTP 25/587 | planned | STARTTLS, AUTH PLAIN/LOGIN only after TLS, recipient allowlist, no open relay. |

## Backpressure

| Condition | SMTP / LMTP | HTTP |
|---|---|---|
| `max_inflight` reached | 451 | 503 + `Retry-After` |
| over `max_message_size` | 552 | 413 |
| spool at `max_spool_bytes` | 452 4.3.1 | 507 |
| spool at `max_deliveries` | 452 4.3.1 | 507 |
| spool unavailable | 451 | 503 |
| header block over `max_header_bytes` | 552 | 413 |
| stream failed partway | 451 4.4.2 | 400 |

A 4xx is retryable, so the sender's own queue holds the backlog, not ours. Every refusal carries its
SMTP reply, HTTP status and `submit` exit code (`oaken_trunk.errors`); the inflight refusal also carries
`retry_after_seconds`.

## The engine

`oaken_trunk.engine.Engine.ingest(envelope, chunks)` is what `submit` calls. In order:

1. **Recipients.** Each is checked on its own: outside `[mail] local_domains`, or with no device
   (`Devices.has_device`), it is refused (`550 5.1.1`, exit 67). An empty `local_domains` accepts
   nothing. None accepted is the refusal, and nothing is read or stored.
2. **A slot.** `max_inflight` through `Credits`, taken before the first chunk and released on success,
   failure and cancellation.
3. **Caps.** `usage()` against `max_spool_bytes` and `max_deliveries` before writing. The engine
   checks only; the spool and CORE_supervisor make it exact.
4. **Stream.** Chunks are cut to at most 64 KiB. Reading stops at the first byte over
   `max_message_size`. The bytes up to the first blank line are the header block, bounded by
   `max_header_bytes`. The body after it goes through named digest taps (`sha256` here). The engine
   holds at most one chunk plus the header block.
5. **Events.** `envelope`, `headers` and `end` run inline, each time-bounded; a listener that fails or
   times out is recorded under the `engine` annotation and ingestion carries on. Then
   `commit(annotations)`, then `stored`, which never changes the answer. No event carries body bytes,
   and the message is visible only after `end` and `commit`.

The answer is a receipt: the message id, its delivery ids, and each recipient accepted or refused.

## Addresses

Postfix or qmail resolves aliases and virtual maps, then hands over the envelope. Trunk keeps no mailbox.
Each recipient becomes its own delivery (`<id>-<n>`) sharing one body. A recipient outside `[mail] local_domains`
is refused (`550 5.1.1`, exit 67), as is a recipient with no device (ADR 0013). A `consume` key is scoped to a list of addresses or `@domain`.

## Postfix and qmail

Postfix: `virtual_transport = lmtp:unix:/path/to/run/lmtp.sock`. qmail: a `.qmail` line piping to
`steamer submit`. Postfix uses the LMTP ingestor or `steamer postfix submit`, and qmail uses `steamer qmail submit`. Each is a
small first-party plugin (PLUGIN_mta-adapters) that wraps `submit` with that MTA's exit codes and environment.
The guides are DOCS_mta-guides.
