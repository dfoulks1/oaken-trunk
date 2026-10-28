# Roadmap

What is built is in [CHANGELOG.md](CHANGELOG.md); which numbered build prompts are done or open is
tracked in [CONTRIBUTING.md](CONTRIBUTING.md#status-of-the-prompts). This page is the *why* and the
open questions. Nothing here is a promise or a date.

## Next

- **Contracts and the directory spool** (CORE_foundations, CORE_contracts, CORE_engine and PLUGIN_directory-spool). Ingestor, Spool and Sender contracts, and a
  Maildir-style spool: write to `tmp/`, fsync, atomic rename into `new/`, lease by rename.
  `batched` durability (a shared directory fsync) is in 0.1.
- **HTTP listener and CLI** (CORE_http-listener, CLI_client). `submit` over HTTP on the ingest surface; `steamer submit` on stdin.
- **LMTP** (PLUGIN_lmtp-ingest). The clean way to sit behind Postfix; a pipe target covers qmail.
- **Consumer API** (CORE_consumer-api). Lease, fetch, ack, nack over HTTP, plus CLI parity.

## Later

- **MCP door** (MCP_mcp-door). Generated from the whole registry, gated by caller class: statistics by default, a
  confirm gate for changes, never message data, off by default. It may share the management UI's listener on its own
  path, authenticated and local-only by default.

- **Management UI** (WEBUI_management-ui). A separate web app on its own port for queue, spool, leases and failures, built
  only on operations the CLI already has.

- **SMTP ingest** with STARTTLS, AUTH and a recipient allowlist.
- **Outbound** (send): a Sender plugin kind, queue semantics, bounces. *Open:* DSN format and retry policy.
- **Redis** and **S3** stores: the same primitives as the directory store, for more than one host
  (ADR 0014).
- **Write-behind tmpfs** over a disk journal. *Open:* recovery rules.
- **mTLS** for consumers.
- **saslauthd bridge**: a second SASL plugin beside the Dovecot-auth one, so Postfix with Cyrus SASL checks
  device tokens. Before 1.0.

## Not planned

IMAP, server-side mailboxes and search, spam filtering, and a RAM-resident spool driver.
