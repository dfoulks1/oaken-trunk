# 12. Logs carry no content and are not a product surface

- Status: accepted
- Date: 2026-10-24

## Context

Trunk handles other people's mail. Its logs exist to diagnose the gateway, not to look through mail, and an operator
should be able to say that the logs hold nothing sensitive and are not browsable by anyone else.

## Decision

- **Metadata only.** A log line may carry the message id, byte size, surface, plugin, outcome and error code, timings
  and the connecting address. It never carries a body, a header value, a subject, or a signature or key. Sender and
  recipient addresses are not logged by default; `log.envelope = "hashed"` is an opt-in that logs a keyed hash.
- **Not exposed.** No API operation, CLI verb, MCP tool or management UI page returns log lines. Those surfaces show
  counts, states and `doctor` results. Logs go to the host's journal or a file created mode 0600 and are read on the host.
- **Tested.** A test drives messages with known sentinel content through every ingestor and asserts it never appears in
  any log, error or response.

## Consequences

Diagnosing a single message means using its id with the host's logs, not searching mail. Anything that would need content
to debug is out of scope by design.
