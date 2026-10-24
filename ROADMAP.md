# Roadmap

What is built is in [CHANGELOG.md](CHANGELOG.md); which numbered build prompts are done or open is
tracked in [CONTRIBUTING.md](CONTRIBUTING.md#status-of-the-prompts). This page is the *why* and the
open questions. Nothing here is a promise or a date.

## Next

- **Contracts and the directory spool** (prompts 02-03). Ingestor, Spool and Sender contracts, and a
  Maildir-style spool: write to `tmp/`, fsync, atomic rename into `new/`, lease by rename.
  `batched` durability (group commit, one fsync per batch) is in 0.1.
- **HTTP and CLI ingest** (05-06). `/v1/send` as submission into the spool; `oaken-trunk submit` on stdin.
- **LMTP** (07). The clean way to sit behind Postfix; a pipe target covers qmail.
- **Consumer API** (08). Lease, fetch, ack, nack over HTTP, plus CLI parity.

## Later

- **SMTP ingest** with STARTTLS, AUTH and a recipient allowlist.
- **Outbound** (send): a Sender plugin kind, queue semantics, bounces. *Open:* DSN format and retry policy.
- **Redis stream** and **S3 + SQS** spools, with their native consumer-group and visibility-timeout
  semantics mapped to lease/ack.
- **Write-behind tmpfs** over a disk journal. *Open:* recovery rules.
- **mTLS** for consumers.

## Not planned

IMAP or POP3, mailbox search, spam filtering, a web UI, and a RAM-resident spool driver.
