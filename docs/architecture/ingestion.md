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

A 4xx is retryable, so the sender's own queue holds the backlog, not ours.

## Addresses

Postfix or qmail resolves aliases and virtual maps, then hands over the envelope. Trunk keeps no mailbox.
Each recipient becomes its own delivery (`<id>-<n>`) sharing one body. A recipient outside `[mail] local_domains`
is refused (`550 5.1.1`, exit 67), as is a recipient with no device (ADR 0013). A `consume` key is scoped to a list of addresses or `@domain`.

## Postfix and qmail

Postfix: `virtual_transport = lmtp:unix:/path/to/run/lmtp.sock`. qmail: a `.qmail` line piping to
`steamer submit`. Postfix uses the LMTP ingestor or `steamer postfix submit`, and qmail uses `steamer qmail submit`. Each is a
small first-party plugin (PLUGIN_mta-adapters) that wraps `submit` with that MTA's exit codes and environment.
The guides are DOCS_mta-guides.
