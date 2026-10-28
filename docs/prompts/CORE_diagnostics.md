# Diagnostics: find out why mail did not arrive

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CORE.md`, ADR 0012, ADR 0013, `docs/architecture/consumers.md`.
**Depends on:** [CORE_system-operations](CORE_system-operations.md), [CORE_audit-and-jobs](CORE_audit-and-jobs.md), [CORE_consumer-api](CORE_consumer-api.md).
**Lift:** M
**Delivers:** Mail-path checks for `doctor`, and the operations an operator uses to trace a message or a device
**Track:** `CORE_`. Builds on the sections and checks of CORE_system-operations; adds no new mechanism.

## Goal

When a user says "my mail never came", an operator can answer from operations alone: was it accepted, which
devices it is queued for, whether they took it, and what is wrong with the device or the limits.

## Decided

- Metadata only: ids, addresses as stored, sizes, ages, states, outcomes. Never a body, a header value or a
  token (ADR 0012). Addresses follow `log.envelope` for anything that also lands in logs.
- Every tool is an operation on the `admin` surface, read only, reachable from the CLI and the API.
- `doctor` stays the name and the entry point. New checks register as sections, as CORE_system-operations says.

## Not in scope

Log search (logs are read on the host). Running `checkup` (CORE_audit-and-jobs). Fixing anything: these tools
report and name the fix.

## Requirements

**A. Doctor checks**

1. **Devices.** A device that only ever reads headers or never sends `DELE` (leave-on-server), a device near
   `device_expiry_days`, a device with a backlog far older than the rest.
2. **Caps.** `max_spool_bytes`, `max_deliveries` and `max_devices` above 80 percent, with what is using them.
3. **Mail path.** A recipient in `local_domains` with no device, a device whose key scope matches no
   `local_domains`, the SASL socket missing or with the wrong group, POP3 or submission without TLS.

`compact`

**B. Tracing**

4. **`trace MESSAGE_ID`.** Accepted when, from which ingestor, its recipients, and per device: queued,
   leased, acked or dropped with the device's expiry, with times. Audit records for it, by correlation id.
5. **`devices [--recipient X]`.** Each device: recipient, created, last used, queue depth, oldest entry,
   acks and nacks in the last day, and the doctor flags above.
6. **`refusals [--since T]`.** Refused mail by reason (cap, recipient, auth, size) and by recipient, from
   stats and audit.
7. **`probe RECIPIENT`.** Submit a synthetic message (marked as a probe, ignored by retention counts) and
   report each device it queued for. `--wait` follows it until every device acks or a timeout.

`compact`

**C. Close**

8. **Docs.** `api-and-cli.md`, a "Mail did not arrive" page that walks `doctor`, `trace`, `devices`,
   `refusals` and `probe` in that order. Softmap, status table.

## Acceptance criteria

- `trace` on a message with two devices, one acked, shows one queued and one acked, with no content.
- `doctor` flags a fake device that only sends `TOP`, and a spool at 85 percent of `max_deliveries`.
- `probe` reaches a fake POP3 device and reports its ack with `--wait`.
- A body sentinel and a token sentinel never appear in any output here.
- Standard checks pass. No network, Docker or real mail in tests.

## Open questions (defaults in bold)

1. Does a probe count against caps? **Yes. It is real mail; it is just labelled.**
2. Keep per-message trace data after the last ack? **Only the audit records, for the audit retention period.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
