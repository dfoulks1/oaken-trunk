# POP3 retriever: download-and-delete clients and webmail fetchers

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/PLUGIN.md`, ADR 0013, ADR 0014, `CORE_line-server.md` (its status block).
**Depends on:** [CORE_line-server](CORE_line-server.md), [CORE_consumer-api](CORE_consumer-api.md).
**Lift:** S
**Delivers:** POP3 over TLS onto list, lease, fetch and ack, with the protocol's own delete-on-QUIT as the ack
**Track:** `PLUGIN_`. Package `oaken_trunk_pop3`, shipped in the core wheel. Core changes: none. TLS, limits, login, the device lock and the session transaction are `BaseRetriever`'s (CORE_line-server).

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

1. **Command table** (RFC 1939, `CAPA` RFC 2449, `STLS` RFC 2595, `AUTH` RFC 5034), mapped onto the
   retriever session: `USER`/`PASS`/`AUTH PLAIN` to login (username the address, password the `toaken_`);
   `STAT`, `LIST`, `UIDL` to `list`; `RETR` to `read`; `TOP` to `read_head`; `DELE` to `mark`; `RSET` to
   `unmark`; `QUIT` to `commit`. Ports 995 (implicit TLS) and 110 (`STLS`).
2. **Replies.** `+OK` and `-ERR` texts per RFC 1939; a failed ack on `QUIT` answers `-ERR` and the message stays.
3. **Contract.** `LineServerContract` and the retriever suite of CORE_line-server, over this command table.
4. **Docs.** `plugins.md`, `consumers.md`, `config.example.toml` (`[retrieve.pop3]`), softmap, status table.

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
