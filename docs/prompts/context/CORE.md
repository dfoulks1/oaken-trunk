# Context: CORE_ prompts

Read with [CONTEXT.md](../CONTEXT.md).

**Core is the product.** One wheel: the engine, the management layer and the plugin host. Core routes and
sequences. Plugins do the mail work. The engine is the only part that sees every plugin, so it owns the
order of events and the commit.

**Data path (engine)**
- Never a whole message in memory. `max_inflight` and `max_message_size` apply at the door. Over a limit is
  a retryable 4xx (`architecture/ingestion.md`).
- A spool stores through a writer. A message is visible only at `commit(annotations)`. (Tentative.)
- Durability: `strict` default, `batched` in 0.1, `volatile` explicit. Delivery is at-least-once: lease,
  fetch, ack, nack (ADR 0003, 0004).
- Listeners subscribe to `envelope`, `headers`, `end` (inline, time-bounded) and `stored` (after durable).
  They see headers and digests, never the body, and annotate only. A listener never removes a core protection.

**Command path (management layer)**
- Registry, the HTTP API generated from it, and the daemon. In the core wheel (ADR 0006, 0009).
- Core registers only what the product needs: mail flow, system, config, audit. The plugin host loads
  everything else, and plugin operations fill the registry. It seals after startup. (Tentative.)
- Ingestors enter through `submit`, never the spool. Mail-flow successes are counted, everything else audited.
- Local CLI over a Unix socket with peer credentials. Remote clients use signed HTTP.

**Security**
- Every HTTP surface refuses unsigned requests before any route (ADR 0010). The guard owns freshness, replay
  and the default deny. An authenticator only verifies. A surface belongs to the key and the operation.
  (Tentative.)
- Logs carry no content, and no door returns them (ADR 0012).

**Processes**
- 0.1 runs one worker with one I/O thread. `workers.count` and `workers.thread_count` are keys from the start,
  default 1. A count above 1 is refused until CORE_supervisor, and threads above 1 until a prompt tests them (ADR 0005).
