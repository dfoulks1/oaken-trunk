# IMAP retriever: mail clients read the queue over IMAP

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/PLUGIN.md`, ADR 0013, `docs/architecture/consumers.md`.
**Depends on:** [CORE_plugin-host](CORE_plugin-host.md), [CORE_consumer-api](CORE_consumer-api.md), [CORE_request-guard](CORE_request-guard.md).
**Lift:** L
**Delivers:** The default retriever: IMAP over TLS onto list, lease, fetch and ack, so a mail client reads Trunk
**Track:** `PLUGIN_`. Package `oaken_trunk_imap`, shipped in the core wheel. Core changes: none (`BaseRetriever` and `@leased` are built in CORE_plugin-host, `lease` by `ids` in CORE_consumer-api).

## Goal

A user points Thunderbird or Outlook at Trunk and reads their mail, from any spool, with no mailbox on the
server. Oaken Mail and other native clients keep calling the operations directly.

## Decided

- A `BaseRetriever` subclass. It translates IMAP into operations and holds no store, no index and no flags
  (ADR 0013).
- **`imap fetch`** is the one convenience call: a `@command` on the `consume` surface under `@leased`. It
  leases a message by id, streams it from core `fetch`, renews while streaming, and acks when the stream
  completes (nacks on any failure). `steamer imap fetch ID > file` does the same from the CLI.
- The client only sends ordinary IMAP. The server runs the cycle; no MUA is expected to know it exists.
- The ack trigger is bytes, not command shape: once the session has sent every byte of a body (one fetch or
  chunked partials, `PEEK` or not), that message is acked. Header-only reads use `@leased` with `ack=False`.
- SELECT lists with core `list`, which never returns content. Nothing is leased until a FETCH.
- INBOX only here (PLUGIN_imap-compat adds the rest). APPEND is refused with `NO [CANNOT]`: there is no
  server-side mailbox (ADR 0013). Login goes through the authenticator plugins; the key's recipient scope
  bounds a session.
- Bodies stream in chunks. A whole message is never held in memory (ADR 0003).

## Not in scope

Sending (CORE_send). Extensions, virtual folders, SEARCH, stable UIDs and conformance (PLUGIN_imap-compat).
POP3 or JMAP (another retriever). Client setup guides (DOCS_mta-guides).

## Requirements

**A. Session**

1. **Listener.** IMAP4rev2 (RFC 9051) with IMAP4rev1 compatibility, implicit TLS on 993 and STARTTLS on 143.
   No LOGIN or AUTHENTICATE before TLS. Bounded connections per key and in total.
2. **Login.** `LOGIN` and `AUTHENTICATE PLAIN` hand the credential to the authenticator chain. A failure is
   one generic `NO`, rate limited.
3. **SELECT INBOX.** `list` for the logged-in recipient gives `EXISTS` and `RFC822.SIZE`. UIDs are a session
   counter in list order; UIDVALIDITY is new each session.

`compact`

**B. Fetching**

4. **Body.** `BODY[]`, `BODY.PEEK[]`, `RFC822` and partials of them stream from `fetch`. The session tracks
   bytes sent per message; at the last byte it acks through `imap fetch`'s `@leased`. The next response point
   reports the message `EXPUNGE`d. A failed fetch returns `NO` and the mail stays queued.
5. **Headers.** `ENVELOPE`, `BODY[HEADER]`, `HEADER.FIELDS` and their `PEEK` forms lease, read and nack.
   Header reads stop at the blank line.
6. **STORE and EXPUNGE.** Accepted and ignored: there is nothing left to delete. `\Seen` is reported only in
   the session.

`compact`

**C. Live mail and limits**

7. **IDLE.** Wakes on new mail through `lease` with `wait` (leasing nothing: `limit=0`), then `list` again
   and report `EXISTS`.
8. **Teardown.** Logout, timeout or a dropped socket mid-fetch nacks through `@leased`.
9. **Contract.** `RetrieverContract`: no content in logs, no auth before TLS, flat memory on a 1 GB body,
   out-of-scope recipients look empty.
10. **Docs.** `plugins.md` example, `consumers.md`, `config.example.toml` (`[retrieve.imap]`), softmap,
    status table.

## Acceptance criteria

- An in-process IMAP client logs in, selects INBOX, fetches headers (the message stays in `list`), then fetches
  the body: the bytes equal the stored bytes and the message is gone from `list`.
- A connection dropped mid-body returns the message to the queue with the same id.
- Replayed command transcripts from Thunderbird and Outlook (recorded once, kept as fixtures) end with every
  message acked and none acked during the header pass.
- `steamer imap fetch ID` streams and acks; a broken pipe nacks.
- A key scoped to `ann@a.com` never sees `bob@a.com`'s mail.
- A body sentinel never reaches a log or an error. A 1 GB body fetches with flat memory.
- Standard checks pass. No network, Docker or real mail in tests.

## Open questions (defaults in bold)

1. Stable UIDs across sessions? **Not here. New UIDVALIDITY each session until PLUGIN_imap-compat.**
2. Two clients on one address? **Whoever fetches the body first gets it; the other sees it expunged.**
3. Does every common MUA eventually read whole bodies? **Assume yes; the transcript fixtures prove it for
   Thunderbird and Outlook. A client that never does leaves mail queued until the quota.**
4. IMAP library? **Pick an Apache-compatible server parser if a maintained one exists; otherwise a minimal
   parser for the commands above. Say which, and why.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
