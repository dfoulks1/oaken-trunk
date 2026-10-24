+++
title = "Logs"
subtitle = "Diagnostics only, never content"
lead = "Trunk's logs describe the gateway, not the mail. They hold no message content and no API, CLI, MCP tool or UI page returns them."
badges = [["text-bg-warning", "Pre-alpha"]]
description = "What a log line may contain, who can read it, and how that is tested."
group = "concepts"
order = 90
+++

Decision: [ADR 0012](repo:docs/adr/0012-logs-carry-no-content.md).

## What a line may carry

Message id, byte size, surface, plugin, outcome and error code, timings, and the connecting address. Never a body, a
header value, a subject, a signature or a key. Sender and recipient addresses are not logged by default; the opt-in
`log.envelope = "hashed"` logs a keyed hash instead.

## Who can read them

Only someone on the host. Logs go to the journal or a file created mode 0600. No operation, CLI verb, MCP tool or UI page
returns log lines; those surfaces show counts, states and `doctor` results.

## How it is checked

A test sends messages carrying sentinel content through every ingestor and asserts that it appears in no log line, error
or response.
