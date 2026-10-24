# 00 - Shared context (read this before every prompt)

This file is the contract for how to work here. If a prompt and this file disagree, **stop and
report** instead of picking one.

## Where the design lives

1. The code and its tests are the truth about what exists.
2. `docs/softmap.toml` says what is built, partial or planned. Never claim more than it says.
3. `docs/adr/` records decisions that are expensive to reverse.
4. `docs/architecture/*.md` describes how each part behaves.
5. This file holds the rules and the answers the user has given.
6. The numbered prompts are the build plan; a built prompt is history.

## What we are building

**Oaken Trunk** is a small, stateless mail gateway and a standalone project. It receives mail
(SMTP, LMTP, HTTP, pipe), streams it to a spool on disk, and notifies consumers who lease, process
and ack. It replaces the local *delivery* step (the LDA role), not mailbox access: no IMAP, no
index, no search. It must be light enough to run beside Postfix or qmail. Oaken Mail is one
consumer, through a provider plugin that lives in the oaken-mail repository. License: Apache-2.0.

## Decided

1. **Language and tooling:** Python >=3.11, uv, hatchling, ruff, `mypy --strict`, pytest,
   import-linter. Same standards and layout as oaken-mail.
2. **Identity parity:** the same home system as oaken-mail, with its own variable:
   `OAKEN_TRUNK_HOME` (`<dir>/config/config.toml`, `<dir>/data`). Settings env prefix `OAKEN_TRUNK_`.
   Package `oaken_trunk`, CLI `oaken-trunk`, plugin groups `oaken_trunk.*`.
3. **Standalone.** Trunk never imports oaken-mail. Consumers use a documented contract.
4. **Directions:** inbound is the priority; send is included (prompt 11) and has its own spool of
   outbound messages, bounded by a quota. Not for terabytes: efficiency over capacity.
5. **Memory (applies to the gateway process):** a message is never held whole in memory. Streams in fixed chunks. Concurrency is
   bounded by `max_inflight`; overload yields a retryable 4xx. First-party drivers are not RAM-resident; a third-party spool plugin decides where it stores bytes.
6. **Durability:** accepted means durable by default (`strict`: fsync file, rename, fsync dir).
   `batched` (group commit: concurrent messages share one fsync, ack after it) is in 0.1.
   `volatile` is explicit.
7. **Delivery:** at-least-once. `lease` (visibility timeout), `fetch`, `ack`, `nack`. Consumers
   dedupe on message id.
8. **Spool contract** is the notes' `Store`/`Notify`/`Delete` extended with lease/ack and a stream
   read. Notify is directory-based (inotify with a polling fallback), never in-process only,
   because workers are separate processes.
9. **Concurrency:** asyncio uses one core per process. Scale with `workers = N` processes
   (`SO_REUSEPORT`) that share only the spool. Blocking file I/O runs in a thread pool.
10. **Auth:** static API tokens (separate ingest and consume), SMTP AUTH PLAIN/LOGIN only after
    STARTTLS, recipient allowlist (no open relay), mTLS for consumers later. Plugin-extensible.
11. **One registry:** every capability is an operation; the HTTP API and CLI are generated from it,
    so every endpoint has a CLI command.
12. **First-party real in 0.1:** directory spool, HTTP, CLI stdin, LMTP. Planned: SMTP, Redis,
    S3+SQS, send.
13. **Postfix/qmail coexistence:** LMTP (`virtual_transport = lmtp:unix:...`) and a pipe command.

14. **A tool, not a project.** The owner wants to run and test it, not develop it. 0.1 must work out
    of the box: `oaken-trunk init` writes a config, `doctor` explains what is wrong, `status`
    shows the queue, and the docs carry a Postfix snippet, a qmail pipe line and a systemd unit.
15. **Cross-worker state:** the supervisor holds the counters and workers use batched credits over a pipe (control messages only). Outbound per-domain throttles shard by domain hash. Workers fail closed if the supervisor is gone (`docs/architecture/process-model.md`).

16. **Standard plugin base.** Ingestors, spools and senders extend `BaseIngestor`, `BaseSpool` and
    `BaseSender` (capabilities inferred from overridden methods, lenient returns, contract suites),
    as oaken-mail's plugins do. See `docs/plugins.md` and ADR 0006.

## Rules for every prompt

- Docs are part of done. Update the page you touch and `docs/softmap.toml`.
- Tests next to the code, no network, no Docker, no real mail. Never log a message body.
- Keep the repo green: `ruff check`, `ruff format --check`, `mypy`, `lint-imports`, `pytest`.
- Conventional Commits. Push only when the user asks.
- Do not add dependencies a prompt does not call for without saying why.
- If an ambiguity changes the design, stop and ask.

## Report-back checkpoint (end of every prompt)

End your final message with: 1. **Done** 2. **Files** 3. **How I verified** 4. **Deviations**
5. **Open questions** 6. **Next prompt readiness**. Then stop.
