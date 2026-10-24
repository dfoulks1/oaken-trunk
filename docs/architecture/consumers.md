+++
title = "Consumers"
subtitle = "Lease, fetch, ack and nack"
lead = "How a consumer takes a message, what at-least-once delivery means, and how it is woken."
badges = [["text-bg-warning", "Pre-alpha"]]
description = "How consumers take messages."
group = "concepts"
order = 50
+++

A consumer is anything that leases messages: the Oaken Mail provider plugin (in its own repository),
a CLI, a webhook relay.

1. `lease` N messages for a visibility timeout.
2. `open` each as a stream and process it.
3. `ack` on success, `nack` on failure. A crash simply lets the lease expire.

Delivery is at-least-once; dedupe on message id. Consume tokens are separate from ingest tokens.
Notification is directory-based (inotify, else polling), so a consumer in another process wakes too.
The HTTP form is generated from the same operations as the CLI. The contract is versioned and stable
(ADR 0002), because consumers live in other repositories.
