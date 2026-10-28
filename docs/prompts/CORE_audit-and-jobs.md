# Audit and jobs: what happened, and the work in the background

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CORE.md`, `docs/architecture/ai-safety.md`,
`docs/architecture/logging.md`, ADR 0012.
**Depends on:** [CORE_daemon](CORE_daemon.md), [CORE_system-operations](CORE_system-operations.md).
**Track:** `CORE_`. Model: oaken-mail's `core/jobs.py` and `core/eventlog.py`.
**Lift:** L
**Delivers:** Content-free audit log, stats rollup, the job runner and `checkup`, the maintenance sweep

## Goal

Every call leaves a content-free record an operator can read, and the housekeeping Trunk needs runs
reliably in the background.

## Decided

- Core owns the audit sink and fails closed: no sink, no start. A plugin cannot switch it off.
- State that is not mail (audit, counters, job state, device last-used) lives in a small SQLite file in `<data>/`. The spool
  stays the only mail state. The interfaces are in core, SQLite is the default behind them.
- Audit records and logs never carry message content or a secret.

## Not in scope

A second storage backend. Dead-letter, retention purge, and pause, resume and retry controls (after 0.1).
The UI pages (WEBUI_management-ui).

## Requirements

1. **`AuditSink` in SQLite.** Operation, caller class, principal, surface, outcome, time, correlation id.
   Append only. A write failure refuses the call.
2. **`audit` operation.** Read with filters (time, operation, principal, outcome), paged. No content.
3. **Stats rollup.** Persist counter totals per hour. `stats` can read history.
4. **Jobs.** A small runner for periodic work with state in the same file: last run, outcome, next run.
5. **`checkup`.** One sweep, run by the job runner on `checkup.schedule` (default hourly) and on demand
   (`steamer checkup`, `--dry-run` reports without changing anything). Each step idempotent and safe across a
   crash: return expired leases to the queue; expire devices unused for `device_expiry_days` with their
   queues (ADR 0013); remove bodies no queue holds; rescan spool usage against the caps. The result is a
   job record and stats; what was dropped is named for `doctor`.
6. **Device last-used.** Updated on login and lease, written at most once per `checkup` interval per device
   so a busy device costs no writes. `checkup` reads it; nothing else decides expiry.
7. **`list_jobs`** (read only in 0.1).
8. **Retention of the audit file.** A size or age cap, rotated, never silently dropping a record unrecorded.
9. **Docs.** `ai-safety.md` and `logging.md` state where audit lives. Softmap, status table.

## Acceptance criteria

- Every operation call, including a refused one, writes a record. A body sentinel and a secret sentinel never
  appear in the database.
- Starting with the audit file unwritable fails with a readable error.
- A lease that expired while the daemon was down returns to the queue at the next start.
- `audit` filters work and are paged. `list_jobs` shows the reaper's last run. Standard checks pass.

## Open questions (defaults in bold)

1. Audit retention default? **90 days, then rotate.**
2. Is the reaper a job or part of the spool? **A job, calling the spool's recovery.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
