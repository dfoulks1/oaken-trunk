# POP3 retriever: download-and-delete clients and webmail fetchers

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/PLUGIN.md`, ADR 0013, `docs/architecture/consumers.md`.
**Depends on:** [CORE_plugin-host](CORE_plugin-host.md), [CORE_consumer-api](CORE_consumer-api.md), [CORE_request-guard](CORE_request-guard.md).
**Lift:** M
**Delivers:** POP3 over TLS onto list, lease, fetch and ack, with the protocol's own delete-on-QUIT as the ack
**Track:** `PLUGIN_`. Package `oaken_trunk_pop3`, shipped in the core wheel. Core changes: none (`BaseRetriever` is built in CORE_plugin-host, `lease` by `ids` in CORE_consumer-api).

## Goal

Clients that only speak POP3, and webmail that fetches other accounts over POP3 (Gmail), read Trunk.

## Decided

- A `BaseRetriever` subclass: no store, no index (ADR 0013).
- POP3's own handshake is the ack. `RETR` claims and streams. `DELE` marks. A clean `QUIT` (the UPDATE
  state, RFC 1939) acks every marked message. A dropped session acks nothing; claims time out and requeue.
- `TOP` is a header read: lease, read, nack.
- `UIDL` is the delivery id, which is already stable. No sequence needed.
- Each device logs in with its own app token (`apptoken`, CORE_request-guard), never the user's password. A
  webmail fetcher is one more device.
- The plugin runs in its own worker process (CORE_supervisor), so a parser fault cannot reach core.
- A client set to leave mail on the server never sends `DELE`: `doctor` flags the device and points to
  Oaken Mail.

## Not in scope

IMAP (ADR 0013). APOP (needs a stored plaintext secret). Sending. Client setup guides (DOCS_mta-guides).

## Requirements

**A. Session**

1. **Listener.** POP3 (RFC 1939) with `CAPA` (RFC 2449), implicit TLS on 995 and `STLS` on 110 (RFC 2595).
   No `USER`, `PASS` or `AUTH` before TLS. Bounded connections per key and in total.
2. **Login.** The username is the email address; the password is the device's `toaken_` token. A username
   outside the key's recipient scope fails like any other login. `USER`/`PASS` and `AUTH PLAIN` (RFC 5034)
   go to the `apptoken` authenticator. One generic
   `-ERR`; rate limits and lockout are the authenticator's. One session per device at a time (RFC 1939 maildrop lock).
3. **Maildrop.** `STAT`, `LIST` and `UIDL` from core `list` for the device. Nothing leased yet.

`compact`

**B. Reading and ack**

4. **`RETR`.** Leases by id, streams from `fetch` with dot-stuffing, renews while streaming.
5. **`TOP`.** Leases, streams headers and N body lines, nacks.
6. **`DELE`, `RSET`, `QUIT`.** `DELE` marks; `RSET` clears marks; `QUIT` acks the marked and nacks the rest.
   A failed ack answers `-ERR` and the message stays.
7. **Contract.** `RetrieverContract`: no content in logs, no auth before TLS, flat memory on a 1 GB body,
   out-of-scope recipients look empty. A fuzz test of the command parser runs in the suite (bounded time);
   long runs are CORE_security-hardening's.
8. **Docs.** `plugins.md`, `consumers.md`, `config.example.toml` (`[retrieve.pop3]`), softmap, status table.

## Acceptance criteria

- An in-process POP3 client logs in, `RETR`s a message whose bytes equal the stored bytes, `DELE`s it, `QUIT`s,
  and it is gone from that device's `list`.
- A session dropped after `DELE` and before `QUIT` leaves the message queued.
- `UIDL` for a message is the same across sessions.
- A body sentinel never reaches a log or an error. A 1 GB body retrieves with flat memory.
- Standard checks pass. No network, Docker or real mail in tests.

## Open questions (defaults in bold)

1. Does Gmail's fetcher accept implicit TLS on 995 with an app token? **Assume yes; verify against Gmail's
   help page and say what it needs.**
2. Ship in 0.1? **Yes. It is the only way a stock mail client reads Trunk.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
