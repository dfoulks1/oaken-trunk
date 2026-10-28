+++
title = "Oaken Trunk"
subtitle = "A stateless mail gateway with a durable spool"
lead = "Oaken Trunk receives mail over SMTP, LMTP, HTTP or a pipe, streams it into a spool, and lets consumers lease, process and acknowledge it. It sits beside Postfix or qmail and replaces the local delivery step, not mailbox access."
badges = [["text-bg-warning", "Pre-alpha"], ["text-bg-secondary", "Stateless gateway"], ["text-bg-primary", "Open source"]]
description = "A lightweight, plugin-extensible mail gateway: ingest, spool, lease, ack."
+++

## What it is for

- **Server-side software.** Oaken Mail is the client; Oaken Trunk runs on the host that receives mail, is operated rather than used, binds to the network, and takes its secrets from files or the environment.
- **Replace local delivery, not your MTA.** Postfix or qmail hand mail to Trunk over LMTP or a pipe. Mail clients read over IMAP, and there is no mailbox: a fetched message is gone.
- **Never holds a message in memory.** Bodies stream into the spool in fixed chunks, and overload gets a retryable 4xx.
- **Accepted means durable.** The default spool syncs to disk before the sender is told yes.
- **Consumers set their own pace.** They lease a message, process it and acknowledge it. Delivery is at-least-once.
- **Uses your cores.** A supervisor runs worker processes, each an event loop with a small thread pool, all configurable.
- **Extensible.** Ingestors, spools and senders are plugins on standard base classes.

::: callout
**Where things stand.** Oaken Trunk is pre-alpha. This site is the design and the build plan; there is no code yet. See the [roadmap](repo:ROADMAP.md).
:::

## The documents

{{doc-cards}}
