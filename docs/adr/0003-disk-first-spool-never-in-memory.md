# 3. Messages are never held whole in memory; the default spool is on disk

- Status: accepted
- Date: 2026-10-24

**Context.** The first notes made RAM disk the first driver. A crash after an SMTP 250 then loses
accepted mail, and a burst of large messages can exhaust memory.

**Decision.** Bodies stream from the socket to a file in fixed chunks (default 64 KiB). The default
directory spool is Maildir-like: write to `tmp/`, fsync, atomic rename into `new/`, fsync the
directory, and only then acknowledge to the sender. Durability is a setting: `strict` (default) or
`batched` (concurrent messages share one fsync) or `volatile` (no fsync, an explicit opt-in). A tmpfs mount is an operator choice for the same driver,
not a driver of its own. Where a spool *plugin* keeps bytes (Redis, S3) is that plugin's decision;
the contract is only a bounded stream in and a stream out. `max_inflight` and `max_message_size` bound load; beyond them the sender
receives a retryable 4xx (SMTP 451, HTTP 503 with `Retry-After`).

**Consequences.** Idle RAM stays small and independent of volume. Throughput depends on the disk's
fsync cost, so `batched` ships in 0.1. First-party drivers are not RAM-resident.
