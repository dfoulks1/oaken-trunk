+++
title = "Process model"
subtitle = "Workers, threads, limits and shared counters"
lead = "How one supervisor, several worker processes and a small thread pool use your cores, and how limits stay exact."
badges = [["text-bg-warning", "Pre-alpha"]]
description = "Workers, threads and shared counters."
group = "concepts"
order = 30
+++

asyncio runs on one thread, so one process uses about one core. Ingest is mostly socket-to-disk
I/O, but TLS, MIME parsing and compression are CPU work and `fsync` blocks (ADR 0005).

```
supervisor  (opens the listening sockets, restarts crashed workers)
   |-- worker 1: one event loop + thread pool (threads_per_worker)
   |-- worker 2: one event loop + thread pool
   `-- worker N
```

## Settings

| Setting | Meaning |
|---|---|
| `workers` | Number of processes, or `auto` (usable CPUs, honouring cgroup limits and affinity). |
| `max_workers` | Ceiling for `auto` and any explicit value. |
| `threads_per_worker` | Blocking-I/O threads in each worker. |
| `max_threads` | Ceiling on `workers * threads_per_worker`. Startup refuses more. |
| `max_inflight` | Global, enforced exactly through supervisor credits. |

The supervisor passes sockets to workers, which works on every OS and avoids `SO_REUSEPORT`'s uneven
spread. Workers share no memory.

## Shared state: the supervisor holds the counters

The supervisor is the one place that sees every worker, so it holds the global counters and workers
reach it over a pipe (a socketpair per worker). Only control messages cross it; message bytes never do.

- **Credits.** A worker requests a batch of credits (for example 8 inflight slots, or a slice of the
  spool quota) and spends them locally. A message costs no round trip until the batch is spent, so
  `max_inflight`, `max_spool_bytes` and per-client rate limits stay exact in aggregate at about one
  pipe message per batch. Unused credits are returned when a worker goes idle.
- **Crash safety.** When a worker dies, the supervisor reclaims the credits it held.
- **Supervisor failure.** Workers fail closed: they finish what they hold, then shed new mail with a
  retryable 4xx until the supervisor is back.
- **Outbound throttles** still shard by destination-domain hash, which needs no round trip at all.

| State | Exact? | Approach |
|---|---|---|
| `max_inflight` | Yes | Credits from the supervisor |
| Spool quota | Yes | Credits for byte reservations, plus periodic rescan to correct drift |
| Inbound per-client rate limits | Yes | Credits keyed by client |
| Outbound per-domain throttles | Yes | Shard by domain hash; one worker owns each domain |
| Lease and ack | Yes | Atomic renames in the spool |
