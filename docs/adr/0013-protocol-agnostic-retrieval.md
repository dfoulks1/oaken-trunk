# 13. Retrieval is protocol-agnostic: clients read through operations or a retriever plugin

- Status: proposed
- Date: 2026-10-28

## Context

Trunk replaced the local delivery step and kept no way to read mail but the consumer API. Users still need
to read their mail, and the operator does not want to host mailboxes. Clients run on the user's machine.
Oaken Mail (an ingestion pipeline with no MUA) calls the consumer operations directly; it is the only native
client today, not the only one there can be. Mail clients and webmail fetchers (Gmail) speak POP3 or IMAP.
Trunk is only the server side, and should not care which client connects.

## Decision

- **A no-server-side-mailbox spool.** Trunk replaces Dovecot and the mailboxes behind it: local delivery and
  mailbox storage. Postfix stays in front. Mail lives on the server only until every device has taken it;
  the client is the mailbox. System mailboxes (`/var/mail` through Postfix's `local(8)`) are out of scope.
- **One way out: the consumer operations.** A native client calls lease, fetch, ack, nack and renew. Anyone
  may build one.
- **Retrievers translate.** A new plugin kind, `oaken_trunk.retrievers` (`BaseRetriever`), speaks a read
  protocol and maps it onto those operations. It holds no store and no index of its own (ADR 0009).
- **POP3 is the first-party retriever.** Its own handshake is the ack: `RETR` claims, `DELE` marks, a clean
  `QUIT` acks. A dropped session acks nothing and the claims time out. `UIDL` is the delivery id. IMAP is
  not shipped: its clients give no reliable "I have it" signal, and it invites server-side folders, uploads
  and search. It can be another plugin later, under this ADR.
- **Every device is a consumer.** Each device has its own key and gets every message for its recipient.
- **Spools stay queues: one per device.** A body is stored once; each device has its own queue of
  references to it, and an ack removes the device's entry. The body goes when no queue holds it. No
  folders, no flags, no uploads, no per-account state.
- **Devices go stale, mail does not.** Mail waits in a device's queue until acked. A device unused for
  `device_expiry_days` (30) expires with its queue, and `doctor` reports what was dropped.
- **Three caps, any backend.** `max_spool_bytes` (bodies), `max_deliveries` (queue entries: links, keys or
  objects) and `max_devices`. At either of the first two, ingest refuses with a retryable error and the
  sender's MTA retries and bounces; Trunk never bounces. At `max_devices`, adding a device is refused.
- **Same guard.** A retriever authenticates through the authenticator plugins (ADR 0010), over TLS, with the
  key's recipient scope. Logs carry no content (ADR 0012).

## Consequences

"No POP3" leaves the docs; "no mailbox hosting" stays. Delivery stays at-least-once (ADR 0004): only the
client's `QUIT` after `DELE` removes mail. A client set to leave mail on the server never acks; `doctor` flags
such a device and points to Oaken Mail. Webmail fetchers keep the mail on their own servers, which is the
user's choice. Outbound submission for mail clients is `CORE_send`, not this ADR.
