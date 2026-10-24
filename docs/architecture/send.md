# Send

Outbound mail is submitted (HTTP, CLI, SMTP 587), stored in an outbound spool, and drained by a sender
plugin at a controlled rate. The spool absorbs bursts: tens of thousands of messages are accepted
quickly and sent at the pace remote servers allow.

- **Sizing.** 10-50k messages at 75-100 KB is about 1-5 GB. `max_spool_bytes` caps it; at the limit,
  submitters get a retryable 4xx. Trunk is not meant for terabytes.
- **Bulk bodies** are stored once, with a small per-recipient envelope pointing at them.
- **Drain.** Per-destination-domain concurrency and rate limits, reused connections, retry with
  exponential backoff and jitter, and a bounce for permanent failures.
- **Sharding.** Outbound work is sharded by destination-domain hash, so each domain's throttle is
  exact inside one worker.
- **Open:** DSN format and the retry schedule.
