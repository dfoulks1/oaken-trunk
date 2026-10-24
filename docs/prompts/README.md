# Build prompts

One self-contained prompt per session. Read [00-context.md](00-context.md) first. Status is tracked
in [CONTRIBUTING.md](../../CONTRIBUTING.md#status-of-the-prompts).

| # | File | Depends on |
|---|---|---|
| 01 | [bootstrap](01-bootstrap.md) | |
| 02 | [contracts-and-core](02-contracts-and-core.md) | 01 |
| 03 | [directory-spool](03-directory-spool.md) | 02 |
| 04 | [plugin-host](04-plugin-host.md) | 02 |
| 05 | [http-ingest](05-http-ingest.md) | 03, 04, 18 |
| 06 | [cli-client](06-cli-client.md) | 03, 04 |
| 07 | [lmtp-ingest](07-lmtp-ingest.md) | 03, 04 |
| 08 | [consumer-api](08-consumer-api.md) | 05, 06, 18 |
| 09 | [smtp-ingest](09-smtp-ingest.md) | 07 |
| 10 | [multi-worker](10-multi-worker.md) | 03, 05 |
| 11 | [send](11-send.md) | 08 |
| 12 | [redis-spool](12-redis-spool.md) | 03 |
| 13 | [s3-sqs-spool](13-s3-sqs-spool.md) | 03 |
| 14 | [security-hardening](14-security-hardening.md) | 05, 07, 08, 09 |
| 15 | [docs-site](15-docs-site.md) | 01 |
| 16 | [management-ui](16-management-ui.md) | 06, 08, 18 |
| 17 | [mcp-door](17-mcp-door.md) | 06, 08, 18 |
| 18 | [request-guard](18-request-guard.md) | 04 |
| 19 | [mail-authentication](19-mail-authentication.md) | 03, 07 |
