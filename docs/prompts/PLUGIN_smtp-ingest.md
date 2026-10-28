# SMTP ingest

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/PLUGIN.md`, ADR 0014, `PLUGIN_lmtp-ingest.md` (its status block).
**Depends on:** [PLUGIN_lmtp-ingest](PLUGIN_lmtp-ingest.md).
**Lift:** M
**Delivers:** SMTP on 25 and 587: STARTTLS, AUTH, recipient allowlist
**Track:** `PLUGIN_`. Package `oaken_trunk_smtp`. Core changes: none. TLS, limits and login are `BaseIngestor`'s (CORE_line-server).

## Goal

`oaken_trunk_smtp`: SMTP on 25 and 587, as a command table on `BaseIngestor`.

## Requirements

1. **Command table** (RFC 5321, `STARTTLS` RFC 3207, `AUTH` RFC 4954, `SIZE` RFC 1870): `EHLO`, `HELO`,
   `MAIL`, `RCPT`, `DATA`, `RSET`, `NOOP`, `QUIT`.
2. **Recipients.** An allowlist (`accept_domains`); empty refuses all. No open relay.
3. **Size and load.** The size limit is enforced before the 250; overload is a 4xx.
4. **Contract.** `LineServerContract` and `IngestorContract` over this table.

## Acceptance criteria

- No relaying for unlisted domains. No AUTH offered before STARTTLS.
- Standard checks pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
