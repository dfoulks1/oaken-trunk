# 5. Process model: supervised worker processes, each an event loop plus a small thread pool

Status: accepted

**Context.** asyncio runs on one thread and so uses about one core per process. Ingest is mostly
socket-to-disk I/O, but TLS, MIME parsing and compression are CPU work, and `fsync` blocks.

**Decision.** A supervisor opens the listening sockets and starts `workers` child processes that
inherit them (this works on every OS, unlike `SO_REUSEPORT`, and the supervisor can restart a
crashed worker). Each worker runs one event loop and a thread pool of `threads_per_worker` for
blocking file I/O. Workers share no memory; the spool is the only shared state, and it is safe for
many writers and consumers because it relies on atomic renames. Limits are configurable and capped:
`workers` (a number or `auto`), `max_workers`, `threads_per_worker`, `max_threads`. `auto` counts
usable CPUs honouring cgroup limits and CPU affinity. The supervisor also holds the global counters (`max_inflight`, spool quota, per-client rate limits) and hands workers batched credits over a pipe; message bytes never cross it.

**Consequences.** Notification cannot depend on an in-process event: it is inotify with a polling
fallback. Limits are exact in aggregate, at the cost of a small supervisor protocol; workers fail closed with a 4xx if the supervisor is unreachable. Startup refuses
a configuration whose `workers * threads_per_worker` exceeds `max_threads`.
