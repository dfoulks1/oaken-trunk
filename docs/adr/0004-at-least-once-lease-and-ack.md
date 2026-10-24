# 4. At-least-once delivery with lease and ack

- Status: accepted
- Date: 2026-10-24

**Decision.** A consumer `lease`s a message for a visibility timeout, reads it as a stream, then
`ack`s (removes it) or `nack`s (returns it). An expired lease returns the message to the queue.
Delivery is at-least-once, so consumers dedupe on message id. In the directory spool a lease is an
atomic rename that encodes the expiry and a token in the file name; a crash leaves state recoverable
by a scan at startup. Redis consumer groups and SQS visibility timeouts map onto the same four verbs.

**Consequences.** The spool contract is `store`, `lease`, `open`, `ack`, `nack`, `delete` plus a
directory-based notification, which is wider than the first notes' `Store`/`Notify`/`Delete`.
