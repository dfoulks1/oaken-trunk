# Line server: one base under every socket protocol

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CORE.md`, ADR 0010, ADR 0012, ADR 0013, ADR 0014.
**Depends on:** [CORE_store](CORE_store.md), [CORE_request-guard](CORE_request-guard.md).
**Lift:** L
**Delivers:** `BaseLineServer`, and `BaseIngestor` and `BaseRetriever` on top of it, with the retriever session as a transaction
**Track:** `CORE_`. Protocol plugins (LMTP, SMTP, POP3, the SASL bridge) then map command words only.

## Goal

TLS, limits, login, streaming and fuzzing written once, so a protocol plugin is a parser and a table of
replies.

## Decided

- A protocol plugin subclasses a base and declares its commands as a table: name, allowed state, handler.
  The base reads lines, enforces the state machine, writes replies and closes on abuse.
- TCP or Unix socket, chosen by config. Unix sockets take a mode and a group.
- Login goes through the authenticator chain (CORE_request-guard). The base owns no credentials.
- Logs carry no content and no secret (ADR 0012).

## Not in scope

Each protocol (PLUGIN_mail-protocols, PLUGIN_smtp-ingest). The store
(CORE_store).

## Requirements

**A. `BaseLineServer`**

1. **Transport.** Implicit TLS or STARTTLS-style upgrade; no auth command before TLS on TCP. Certificate
   and key are files, as Dovecot and Postfix read them, so a Let's Encrypt certificate (certbot or any ACME
   client) and the one Postfix uses both work. The base reloads them on `steamer reload` or when the files
   change, without dropping sessions; `doctor` warns 14 days before expiry. No ACME client in Trunk. Bounded line
   length, idle and total timeouts, connection caps per principal and in total.
2. **Commands.** The command table and state machine. Unknown or out-of-state commands get the protocol's
   error reply; too many in a row closes the connection.
3. **Streams.** Dot-stuffed bodies in and out as async iterators of bounded chunks.
4. **Login.** Mechanisms come from the authenticator chain (`PLAIN`, `LOGIN`, `apptoken`). One generic
   failure; rate limits and lockout are the authenticator's.
5. **`LineServerContract`.** No auth before TLS, line and time limits, flat memory, no content or secret in
   logs, and a bounded fuzz run over the subclass's command table.

`compact`

**B. Kinds on top**

6. **`BaseIngestor`.** `listen(submit)` as before, plus per-recipient replies mapped from the engine's results.
7. **`BaseRetriever`.** The session as a transaction: on login take the device `Lock`; list the device's
   queue; claim a message when it is read; record deletes; on a clean end ack the deleted and nack the rest;
   on teardown nack everything. A subclass maps its commands onto `list`, `read(id)`, `read_head(id, lines)`,
   `mark(id)`, `unmark()` and `commit()`.
8. **Docs.** `plugins.md` (a protocol plugin in one screen), ADR 0006 amended, softmap, status table.

## Acceptance criteria

- A toy line protocol of five commands, written as a table, passes `LineServerContract`.
- A toy retriever: dropping the connection after reads returns every claim; a clean end acks only the marked.
- A second login for the same device while a session is open is refused.
- Standard checks pass. No network, Docker or real mail in tests.

## Open questions (defaults in bold)

1. Fuzzer? **A bounded property-based run in the suite, licence checked; long runs in CORE_security-hardening.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
