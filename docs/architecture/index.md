+++
title = "Architecture"
subtitle = "Where to start"
lead = "A map of the architecture pages."
badges = [["text-bg-warning", "Pre-alpha"]]
description = "A map of the architecture pages."
group = "concepts"
order = 5
+++

- [Writing a plugin](../plugins.md): base classes, capabilities, contract suites
- [Overview](overview.md): layers, the operation registry, what trunk is not
- [API and CLI](api-and-cli.md): one registry, the HTTP API, the CLI, MCP
- [Spool](spool.md): the spool contract, the directory driver, durability, quotas
- [Process model](process-model.md): workers, threads, limits, shared state
- [Ingestion](ingestion.md): HTTP, CLI, LMTP, SMTP, backpressure
- [Consumers](consumers.md): lease, fetch, ack, nack, notification
- [Mail authentication](mail-authentication.md): DKIM, SPF, DMARC and ARC
- [Logs](logging.md): diagnostics only, never content
- [Security](security.md): the request guard, signed requests, keys and replay protection
- [AI safety](ai-safety.md): rules and exposure tiers for anything a model can reach
- [Send](send.md): the outbound path and bursts
