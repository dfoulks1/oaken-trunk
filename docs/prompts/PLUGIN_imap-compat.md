# IMAP compatibility: every common client works unchanged

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/PLUGIN.md`, ADR 0013, `PLUGIN_imap-retriever.md` (its status block).
**Depends on:** [PLUGIN_imap-retriever](PLUGIN_imap-retriever.md), [CORE_engine](CORE_engine.md).
**Lift:** L
**Delivers:** The IMAP extensions, virtual folders, SEARCH and stable UIDs that real mail clients expect
**Track:** `PLUGIN_`. Same package, `oaken_trunk_imap`. Core touch point: a per-recipient `seq` on the envelope (requirement 7).

## Goal

Support as much of IMAP as a no-server-side-mailbox spool can honestly answer, so Thunderbird, Outlook,
Apple Mail, K-9 and the rest work with a server, a port and a login.

## Decided

- Advertise only what is honored. No CONDSTORE or QRESYNC: there are no stored change sequences.
- Every way a client deletes is an ack: STORE `\Deleted` then EXPUNGE, MOVE or COPY to Trash, and the full
  download of PLUGIN_imap-retriever.
- Nothing is written in. APPEND to any mailbox is `NO [CANNOT]`. No `\Sent` or `\Drafts` is advertised, so
  clients default to local folders (ADR 0013).
- Reads that are not a full download lease, read and nack, as in PLUGIN_imap-retriever.

## Not in scope

Persistent folders or flags. Server-side Sent or Drafts. Sending (CORE_send). System mailboxes.

## Requirements

**A. Capabilities**

1. **Extensions.** `IDLE`, `UIDPLUS`, `MOVE`, `UNSELECT`, `ENABLE`, `ID`, `NAMESPACE`, `LITERAL+`, `SASL-IR`,
   `SPECIAL-USE`, `COMPRESS=DEFLATE`, `UTF8=ACCEPT`. Each with its RFC named in the code.
2. **Auth mechanisms.** `PLAIN`, `LOGIN`, and `XOAUTH2` / `OAUTHBEARER` when an authenticator plugin offers
   them. The list comes from the authenticator chain, never hard-coded.

`compact`

**B. Mailboxes**

3. **LIST and STATUS.** INBOX, plus a virtual `Trash` marked `\Trash`, always empty. CREATE, DELETE and
   RENAME are `NO [CANNOT]`. SUBSCRIBE and LSUB succeed and change nothing.
4. **Deletes.** EXPUNGE and `UID EXPUNGE` ack `\Deleted` messages. MOVE or COPY to Trash acks. COPY or MOVE
   anywhere else is `NO [CANNOT]`.
5. **APPEND.** `NO [CANNOT]` with a text that says the server keeps no mailbox.

`compact`

**C. Search and UIDs**

6. **SEARCH.** Flags, dates, sizes and header keys from header reads (lease, read, nack); `BODY` and `TEXT`
   stream each body once within `search_max_bytes`, else `NO [LIMIT]`. Never holds a body in memory.
7. **Stable UIDs.** Core assigns a per-recipient `seq` at commit and stores it on the envelope. UID is `seq`;
   UIDVALIDITY is fixed per recipient. Touch point: CORE_engine's commit and the spool contract field.
8. **Conformance.** A replayed transcript per client (Thunderbird, Outlook, Apple Mail, K-9) as fixtures.
   `imaptest` (Dovecot) runs as a manual check, documented, outside the test suite.
9. **Docs.** `consumers.md` (what clients see, what they must set locally), softmap, status table.

## Acceptance criteria

- Each client transcript completes with no `BAD`, every message acked, none acked during header reads.
- APPEND, CREATE and COPY to a non-Trash mailbox return `NO [CANNOT]`; MOVE to Trash removes the message.
- UIDs for a recipient survive reconnects and a daemon restart.
- SEARCH over a 1 GB body runs with flat memory. A body sentinel never reaches a log.
- Standard checks pass. No network, Docker or real mail in tests.

## Open questions (defaults in bold)

1. Where does `seq` come from on a multi-host spool? **The spool assigns it at commit. Directory: a
   per-recipient counter file. Redis: `INCR`. S3+SQS: a conditional write; say if that is not enough.**
2. `imaptest` licence and setup? **Check both before documenting; drop it if it is not Apache-compatible to
   run.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
