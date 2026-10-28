# Supervisor: one process now, many later

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CORE.md`, `docs/architecture/process-model.md`, ADR 0005.
**Depends on:** [CORE_daemon](CORE_daemon.md).
**Lift:** L
**Delivers:** The supervisor and worker management, running in-process at `workers.count = 1`
**Track:** `CORE_`.

## Goal

Put the supervisor in from the start, so raising `workers.count` later is a config change and not a rewrite. At the
defaults it behaves like a single process.

## Decided

- `workers.count = 1` and At `workers.count = 1` the supervisor and the worker share
  one process: no child, no pipe, counters in memory. Same code path as many workers.
- Development and tests run at the defaults. More workers or threads is a deliberate change for performance.
- The supervisor is the worker manager, in core. It owns the sockets (control socket included), the global counters and the nonce cache. Workers
  never share memory.
- `steamer start` runs the supervisor. Restart after a crash is systemd's job when it is the same process.
- Defaults are 1 and 1, a minimal install. `max_count` and `max_threads` always cap
  whatever sets the count.
- No policy interface. An autoscaler is a client of the worker operations (C): a plugin through its context,
  or any signed API client. It reads load from `list_workers` and `stats`, and acts with `add_worker` and
  `delete_worker`. The operations enforce `max_count` and `max_threads`, so no client can exceed them.
  There is no worker-manager plugin kind.
- Control messages only cross the pipe, never message bytes.

## Not in scope

Plugins running in other processes. The autoscaler itself. Outbound per-domain sharding (CORE_send). Any scale test beyond a
correctness one.

## Requirements

**A. Interfaces, in-process first**

1. **Counters.** `Credits` (`max_inflight`, spool quota, per-client rate), `NonceStore` and `Locks` behind
   interfaces. `Locks` is a named, expiring lock that any core part or plugin takes through `ctx` (one POP3
   session per device, `apptoken` failure counts). The in-memory version is the only one at `workers.count = 1`;
   across workers and hosts they run on the `coordination` store (CORE_store). CORE_engine's limiter uses `Credits`.
2. **Settings.** `workers.count` (a fixed number), `workers.max_count`, `workers.thread_count`,
   `workers.max_threads`. Startup refuses a product above `workers.max_threads`, and `workers.thread_count > 1` until a prompt
   tests it.
3. **One code path.** The supervisor runs a worker as a coroutine group in its own process at `workers.count = 1`,
   and as a child at more. The worker cannot tell which.

`compact`

**B. More than one worker**

4. **Spawn and restart.** Inherited sockets, not `SO_REUSEPORT`. A crashed worker is replaced.
5. **Counter service.** A socketpair per worker. Batched credits, reclaimed when a worker dies. A worker fails
   closed with a retryable 4xx if the supervisor is unreachable.
6. **Fleet operations.** `reload`, `stop` and `status` reach every worker. `status` lists them.
7. **Platforms.** Linux, macOS and Windows.

`compact`

**C. Worker management** (registry operations, owned by the supervisor)

8. **States.** `starting`, `running`, `stopping` (draining), `stopped`. A worker has an id, a pid, a start time,
   inflight, the credits it holds, a heartbeat and its plugin health.
9. **Operations.**

| Operation | Permission | What it does |
|---|---|---|
| `list_workers` | read | Id, state, pid, uptime, inflight. |
| `get_worker` | read | One worker in full, with credits, heartbeat and plugin health. |
| `add_worker` | mutate | Start one more, up to `max_count`. Uses the configured `thread_count`. |
| `delete_worker` | mutate | Stop it, drain, remove it. The last worker cannot be deleted. |
| `start_worker` | mutate | A stopped worker runs again. |
| `stop_worker` | mutate | Stop new work, drain, keep the slot. `now` aborts writers. |
| `restart_worker` | mutate | Stop, then start. Rolling: one at a time, the rest keep serving. |
| `run_on_worker` | mutate | Send one allow-listed control command: `ping`, `status`, `reload`, `plugin_health`. Never a registry operation, never code. mcp `never`. |

10. **Rules.** At `workers.count = 1` (in-process) every one of these except the two reads refuses with
    "one worker, use `reload` or `stop`". A change is runtime only and lasts until `reload` or a restart. Each is
    audited with the worker id. A worker that dies is replaced, not left `stopped`. `stopped` means an operator did it.
11. **Docs.** `process-model.md` (0.1 behaviour first), ADR 0005, ADR 0010 and `security.md` (nonce cache lives
   in the supervisor), `spool.md` quota, softmap, status table.

## Acceptance criteria

- At the defaults there is one process and no child, and the daemon tests pass unchanged.
- At `workers.count = 2` many messages are delivered with no loss or duplicate lease, global `max_inflight` is never
  exceeded, and a killed worker is replaced with its credits reclaimed.
- A replayed nonce is refused through either worker. `workers.thread_count = 2` is refused at startup.
- Standard checks pass. No network, Docker or real mail in tests.

- Delete the second of two workers: the first keeps serving and nothing is lost. `delete_worker` on the last is
  refused. `run_on_worker` with `rm` or a registry name is refused.
- At the defaults every mutating worker operation refuses, and the two reads show one worker.

## Open questions (defaults in bold)

1. Is `workers.count > 1` allowed in 0.1? **Yes, tested by this prompt. Threads stay at 1.**
2. Does a runtime add or delete write `workers.count`? **No. `save_config` does, on request.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
