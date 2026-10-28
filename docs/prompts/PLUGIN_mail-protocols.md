# Mail protocols: LMTP in, POP3 out, and the SASL bridge for submission

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/PLUGIN.md`, ADR 0013, ADR 0014, `CORE_line-server.md` (its status block).
**Depends on:** [CORE_line-server](CORE_line-server.md), [CORE_consumer-api](CORE_consumer-api.md).
**Lift:** M
**Delivers:** Three command tables on the line server: LMTP (Postfix delivers), POP3 (clients read), Dovecot-auth (Postfix submission logs in)
**Track:** `PLUGIN_`. Packages `oaken_trunk_lmtp`, `oaken_trunk_pop3`, `oaken_trunk_sasl`, shipped in the core wheel. Core changes: none. TLS, limits, login, the device lock and the retriever session are the bases' (CORE_line-server).

## Goal

Postfix delivers to Trunk, a mail client reads its device queue, and the same login sends through Postfix.
Each protocol is a command table and a reply table, following Dovecot and Postfix wherever they already
answer (CONTEXT.md, "Follow the leader").

## Decided

- **LMTP** (RFC 2033) is a `BaseIngestor`; Unix socket by default, optional TCP.
- **POP3** (RFC 1939, `CAPA` RFC 2449, `STLS` RFC 2595, `AUTH` RFC 5034) is a `BaseRetriever`. `RETR` claims,
  `DELE` marks, a clean `QUIT` acks the marked and nacks the rest; a dropped session acks nothing. `TOP` reads
  and nacks. `UIDL` is the delivery id. Username the address, password the device's `toaken_`.
- **Dovecot auth protocol** (v1.x, major version must match; current docs describe 1.3) is a `BaseLineServer`
  on a Unix socket, mode 0660, group `postfix`. Postfix `smtpd_sasl_type = dovecot`. Checks go to `apptoken`.
- Each runs in its own worker process (CORE_supervisor), so a parser fault cannot reach core.
- Implemented from the RFCs and Dovecot's published protocol page. No Dovecot code is copied; Exim's
  `auths/dovecot.c` is GPL and is read for behaviour only, never copied.

## Not in scope

IMAP (ADR 0013). APOP. SMTP ingest (PLUGIN_smtp-ingest). saslauthd (a later plugin). qmail `checkpassword`.

## Requirements

**A. LMTP**

1. **Commands.** `LHLO`, `MAIL`, `RCPT`, `DATA`, `RSET`, `NOOP`, `QUIT`.
2. **Replies.** Unknown user `550 5.1.1` at `RCPT`, as Dovecot. Spool cap `452 4.3.1`, too large `552 5.3.4`,
   temporary failure `451 4.3.0`, as Postfix words them. Per-recipient replies after `DATA` from the engine.

`compact`

**B. POP3**

3. **Commands.** `USER`/`PASS`/`AUTH PLAIN` to login; `STAT`, `LIST`, `UIDL` to `list`; `RETR` to `read`;
   `TOP` to `read_head`; `DELE` to `mark`; `RSET` to `unmark`; `QUIT` to `commit`. Ports 995 and 110 (`STLS`).
4. **Replies.** `+OK` and `-ERR` per RFC 1939. A failed ack on `QUIT` answers `-ERR` and the message stays.

`compact`

**C. Dovecot auth**

5. **Handshake.** Server `VERSION`, `MECH PLAIN`, `MECH LOGIN`, `SPID`, `CUID`, `COOKIE`, `DONE`; read the
   client's `VERSION` and `CPID`. Refuse an unknown major version.
6. **`AUTH`.** PLAIN (one base64 response) and LOGIN (two `CONT` rounds). `OK user=<address>` or `FAIL`.

`compact`

**D. Close**

7. **Contracts.** `LineServerContract` for all three, `IngestorContract` for LMTP, the retriever suite for POP3.
8. **Docs.** `plugins.md`, `consumers.md`, `config.example.toml` (`[ingest.lmtp]`, `[retrieve.pop3]`,
   `[sasl]`), softmap, status table. The guides are DOCS_mta-guides.

## Acceptance criteria

- An in-process LMTP client delivers to `FakeSpool` with one reply per recipient; a recipient with no device
  gets `550 5.1.1`.
- A POP3 client logs in, `RETR`s bytes equal to the stored bytes, `DELE`s, `QUIT`s, and the message is gone
  from that device; a session dropped before `QUIT` leaves it queued; `UIDL` is stable across sessions.
- A fake Postfix authenticates over the Dovecot-auth socket with a valid token and fails, with one answer,
  on a wrong token, a revoked device or an address outside the key's scope.
- A body or token sentinel never reaches a log. A 1 GB body moves with flat memory. Standard checks pass.

## Open questions (defaults in bold)

1. Reply texts beyond the codes? **Copy the wording of current Dovecot and Postfix; name the versions checked.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
