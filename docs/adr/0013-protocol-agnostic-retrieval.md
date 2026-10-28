# 13. Retrieval is protocol-agnostic: clients read through operations or a retriever plugin

- Status: proposed
- Date: 2026-10-28

## Context

Trunk replaced the local delivery step and said "no IMAP". Users still need to read their mail, and the
operator does not want to host mailboxes. Clients run on the user's machine. Oaken Mail (an ingestion
pipeline with no MUA) calls the consumer operations directly; it is the only native client today, not the
only one there can be. Mail clients (Thunderbird, Outlook) speak IMAP and nothing else. Trunk is only the
server side, and should not care which client connects.

## Decision

- **A no-server-side-mailbox spool.** Trunk replaces Dovecot and the mailboxes behind it: local delivery,
  mailbox storage and IMAP. Postfix stays in front. Mail lives on the server only until a client fetches
  it; the client is the mailbox. System mailboxes (`/var/mail` through Postfix's `local(8)`) are out of scope.
- **One way out: the consumer operations.** A native client calls lease, fetch, ack, nack and renew. Anyone
  may build one.
- **Retrievers translate.** A new plugin kind, `oaken_trunk.retrievers` (`BaseRetriever`), speaks a read
  protocol and maps it onto those operations. It holds no store and no index of its own (ADR 0009). IMAP is
  the first-party default; POP3, JMAP or anything else is another plugin of the same shape.
- **A full fetch is the whole cycle.** A core decorator, `@leased`, wraps lease, renew, ack on success and
  nack on failure. The IMAP retriever's `imap fetch` runs under it: when a mail client fetches a body, the
  message is leased, streamed, and acked. Listing and header reads lease nothing or nack. It is
  download-and-delete, spoken in the client's protocol.
- **Nothing is written in.** No APPEND, no Sent, Drafts or Trash on the server. A client saves those
  locally; a refused APPEND says so.
- **Spools stay queues.** No folders, no flags kept, no mailbox view in core or in any spool. Mail
  waits until a client acks it, bounded by the spool quota.
- **Same guard.** A retriever authenticates through the authenticator plugins (ADR 0010), over TLS, with the
  key's recipient scope. Logs carry no content (ADR 0012).

## Consequences

"No IMAP" leaves the docs; "no mailbox hosting" stays. A client set to keep mail on the server has
nothing to keep: a fetched body is gone. Acking when the stream completes trades the at-least-once
guarantee (ADR 0004) for simplicity: a client that crashes after receiving and before saving loses that
message. Two clients on one address race; the first to fetch a body gets it. Outbound submission for mail clients is `CORE_send`, not this ADR.
