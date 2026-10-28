# LMTP ingest

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/PLUGIN.md`, ADR 0014, `CORE_line-server.md` (its status block).
**Depends on:** [CORE_line-server](CORE_line-server.md), [CORE_daemon](CORE_daemon.md).
**Lift:** S
**Delivers:** LMTP over a Unix socket: the Postfix delivery target
**Track:** `PLUGIN_`. Package `oaken_trunk_lmtp`, shipped in the core wheel. Core changes: none.

## Goal

`oaken_trunk_lmtp`: the Postfix delivery target, as a command table on `BaseIngestor` (CORE_line-server).

## Requirements

1. **Command table** (RFC 2033): `LHLO`, `MAIL`, `RCPT`, `DATA`, `RSET`, `NOOP`, `QUIT`. Unix socket by
   default, optional TCP.
2. **Replies.** Per-recipient replies after `DATA` from the engine's results; backpressure as 451, 452 and 552.
3. **Contract.** `LineServerContract` and `IngestorContract` over this table.
4. **Docs.** The guides are DOCS_mta-guides.

## Acceptance criteria

- An in-process LMTP client delivers to `FakeSpool` with one reply per recipient.
- Standard checks pass; no network, Docker or real mail in tests.

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
