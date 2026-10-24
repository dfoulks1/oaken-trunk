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
| HTTP `/v1/send` | built | Submission into the spool. Streaming request body. Bearer token. |
| CLI stdin | built | `oaken-trunk submit < message.eml`; also the qmail pipe target. |
| LMTP | built | Unix or TCP socket. The Postfix `virtual_transport` target. |
| SMTP 25/587 | planned | STARTTLS, AUTH PLAIN/LOGIN only after TLS, recipient allowlist, no open relay. |

## Backpressure

| Condition | SMTP / LMTP | HTTP |
|---|---|---|
| `max_inflight` reached | 451 | 503 + `Retry-After` |
| over `max_message_size` | 552 | 413 |
| spool at `max_spool_bytes` | 452 | 507 |
| spool unavailable | 451 | 503 |

A 4xx is retryable, so the sender's own queue holds the backlog, not ours.

## Postfix and qmail

Postfix: `virtual_transport = lmtp:unix:/path/to/run/lmtp.sock`. qmail: a `.qmail` line piping to
`oaken-trunk submit`. Exact snippets belong in the 01 and 07 prompts' docs deliverables.
