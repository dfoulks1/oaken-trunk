# SASL bridge: Postfix checks device tokens for submission

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/PLUGIN.md`, ADR 0013, `docs/architecture/security.md`.
**Depends on:** [CORE_plugin-host](CORE_plugin-host.md), [CORE_request-guard](CORE_request-guard.md).
**Lift:** S
**Delivers:** A Dovecot-auth socket, so Postfix submission authenticates with `toaken_` device tokens
**Track:** `PLUGIN_`. Package `oaken_trunk_sasl`, shipped in the core wheel. Core touch point: a plain plugin may own a Unix socket (CORE_plugin-host), as an ingestor does.

## Goal

A POP3 user sends mail through the operator's Postfix (587) with the same login they read with: their email
address and their device's token. Postfix keeps submission, queueing and signing. No Dovecot.

## Decided

- The Dovecot auth protocol only (Postfix `smtpd_sasl_type = dovecot`).
- It checks through the `apptoken` authenticator (CORE_request-guard): rate limits, lockout and one generic
  failure come from there. The username is the email address and must be in the key's recipient scope.
- Implemented from the published protocol descriptions. No Dovecot code is copied.
- Unix sockets only, created mode 0660 with a configured group (`postfix`). Never TCP.
- Never logs a password or token (ADR 0012).

## Not in scope

Submission inside Trunk (CORE_send). saslauthd (a second plugin of its own, likely before 1.0). qmail `checkpassword` (open question). SASL mechanisms other than PLAIN
and LOGIN.

## Requirements

**A. Dovecot auth protocol**

1. **Handshake.** Server `VERSION`, `MECH PLAIN`, `MECH LOGIN`, `SPID`, `CUID`, `COOKIE`, `DONE`; read the
   client's `VERSION` and `CPID`. Refuse an unknown major version.
2. **`AUTH`.** PLAIN (one base64 response) and LOGIN (two `CONT` rounds). Answer `OK user=<address>` or `FAIL`.
   Bounded line length and pending requests per connection.

`compact`

**B. Close**

3. **Contract.** No secret in logs or errors, sockets created with the right mode and group, a malformed
   frame closes the connection, the protocol fuzzed briefly in the suite.
4. **Docs.** `DOCS_mta-guides` gains the Postfix `master.cf` submission lines, with
   `smtpd_sender_login_maps` and `reject_sender_login_mismatch` so a device sends only as its address.
   `config.example.toml` (`[sasl]`), softmap, status table.

## Acceptance criteria

- A fake Postfix client authenticates over the socket with a valid token, and fails with a wrong token, a
  revoked device, or an address outside the key's scope, all with the same answer.
- Repeated failures hit the `apptoken` lockout.
- A token sentinel never reaches a log or an error.
- Standard checks pass. No network, Docker or real mail in tests.

## Open questions (defaults in bold)

1. qmail SMTP AUTH (`checkpassword` interface)? **Not here. A `steamer checkpassword` command is a small
   follow-up if a qmail operator asks.**
2. Verify the protocol description against current Dovecot docs. **Name the versions checked.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
