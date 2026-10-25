# Prompt index

Generated from [`prompts.toml`](prompts.toml). Edit that, then run `uv run python docs/tools/prompts.py sync`.
Rules and shared context are in [CONTEXT.md](CONTEXT.md).

## Master list: done and not done

<!-- prompts:master -->
| Prompt | Status | Target | Delivers | Depends on |
|---|---|---|---|---|
| [CORE_bootstrap](CORE_bootstrap.md) | Open | 0.1 | uv workspace, tooling, legal files, a green empty project | — |
| [CORE_contracts-and-core](CORE_contracts-and-core.md) | Written | 0.1 | Ingestor and Spool contracts, envelope, ids, settings, paths, errors, the streaming engine under limits, listener events | CORE_bootstrap |
| [CORE_operation-registry](CORE_operation-registry.md) | Written | 0.1 | Typed operations, surfaces, confirm gate, schemas, `submit` and `version`; the command path | CORE_contracts-and-core |
| [CORE_daemon](CORE_daemon.md) | Written | 0.1 | The daemon: composition root, lifecycle, and the registry served over a local Unix socket | CORE_operation-registry |
| [CLI_client](CLI_client.md) | Written | 0.1 | The `steamer` command: start, stop, reload, a generic runner and verbs generated from schemas | CORE_daemon |
| [CORE_system-operations](CORE_system-operations.md) | Written | 0.1 | `init`, `doctor`, `status`, `stats` and the config operations | CORE_daemon |
| [CORE_audit-and-jobs](CORE_audit-and-jobs.md) | Written | 0.1 | Content-free audit log, stats rollup, the lease reaper and job runner | CORE_daemon, CORE_system-operations |
| [CORE_plugin-host](CORE_plugin-host.md) | Written | 0.1 | Entry-point discovery, base classes, lifecycle, contract suites | CORE_system-operations |
| [PLUGIN_directory-spool](PLUGIN_directory-spool.md) | Written | 0.1 | Default spool: Maildir-style store, lease by rename, strict/batched/volatile durability | CORE_plugin-host |
| [CORE_consumer-api](CORE_consumer-api.md) | Written | 0.1 | Lease, fetch, ack, nack over HTTP with CLI parity and wake-up | PLUGIN_directory-spool |
| [PLUGIN_lmtp-ingest](PLUGIN_lmtp-ingest.md) | Written | 0.1 | LMTP over a Unix socket: the Postfix delivery target | CORE_plugin-host, CORE_daemon |
| [CORE_request-guard](CORE_request-guard.md) | Written | 0.1 | Signed-requests guard and the authenticator plugin kind | CORE_plugin-host |
| [CORE_http-listener](CORE_http-listener.md) | Written | 0.1 | The TCP and TLS listener with the request guard in front, and HTTP submission on the ingest surface | CORE_daemon, CORE_request-guard |
| [CORE_security-hardening](CORE_security-hardening.md) | Written | 0.1 | Injection, auth and open-relay test pass across every ingestor | PLUGIN_lmtp-ingest, CORE_consumer-api, CORE_http-listener |
| [DOCS_docs-site](DOCS_docs-site.md) | Partly built | 0.1 | Docs site tooling | CORE_bootstrap, CORE_operation-registry, CORE_daemon |
| [WEBUI_management-ui](WEBUI_management-ui.md) | Written | 0.1 | Operator web app on its own port, built only on operations the CLI has | CORE_system-operations, CORE_audit-and-jobs, CORE_http-listener |
| [CORE_mail-authentication](CORE_mail-authentication.md) | Written | later | Native inbound DKIM, SPF, DMARC, ARC without buffering a message | CORE_contracts-and-core, CORE_plugin-host |
| [CORE_send](CORE_send.md) | Written | later | Outbound spool, the Sender plugin kind, DKIM signing | CORE_consumer-api, CORE_request-guard |
| [PLUGIN_smtp-ingest](PLUGIN_smtp-ingest.md) | Written | later | SMTP on 25 and 587: STARTTLS, AUTH, recipient allowlist | PLUGIN_lmtp-ingest |
| [CORE_multi-worker](CORE_multi-worker.md) | Written | later | Supervisor and worker processes, bounded concurrency | PLUGIN_directory-spool, CORE_daemon |
| [PLUGIN_redis-spool](PLUGIN_redis-spool.md) | Written | later | Redis stream spool, consumer groups mapped to lease/ack | PLUGIN_directory-spool, CORE_plugin-host |
| [PLUGIN_s3-sqs-spool](PLUGIN_s3-sqs-spool.md) | Written | later | S3 bodies, SQS visibility timeouts as leases | PLUGIN_directory-spool, CORE_plugin-host |
| [MCP_mcp-door](MCP_mcp-door.md) | Written | later | Optional MCP door gated by caller class. Not part of 0.1 | CORE_operation-registry, CORE_system-operations, CORE_http-listener |
<!-- /prompts:master -->

## Build order

Computed from `depends`, so it cannot contradict them. Target 0.1 comes first.

<!-- prompts:order -->
**Target 0.1**

1. [CORE_bootstrap](CORE_bootstrap.md)
2. [CORE_contracts-and-core](CORE_contracts-and-core.md)
3. [CORE_operation-registry](CORE_operation-registry.md)
4. [CORE_daemon](CORE_daemon.md)
5. [CLI_client](CLI_client.md)
6. [CORE_system-operations](CORE_system-operations.md)
7. [CORE_audit-and-jobs](CORE_audit-and-jobs.md)
8. [CORE_plugin-host](CORE_plugin-host.md)
9. [PLUGIN_directory-spool](PLUGIN_directory-spool.md)
10. [CORE_consumer-api](CORE_consumer-api.md)
11. [PLUGIN_lmtp-ingest](PLUGIN_lmtp-ingest.md)
12. [CORE_request-guard](CORE_request-guard.md)
13. [CORE_http-listener](CORE_http-listener.md)
14. [CORE_security-hardening](CORE_security-hardening.md)
15. [DOCS_docs-site](DOCS_docs-site.md)
16. [WEBUI_management-ui](WEBUI_management-ui.md)

**Target later**

17. [CORE_mail-authentication](CORE_mail-authentication.md)
18. [CORE_send](CORE_send.md)
19. [PLUGIN_smtp-ingest](PLUGIN_smtp-ingest.md)
20. [CORE_multi-worker](CORE_multi-worker.md)
21. [PLUGIN_redis-spool](PLUGIN_redis-spool.md)
22. [PLUGIN_s3-sqs-spool](PLUGIN_s3-sqs-spool.md)
23. [MCP_mcp-door](MCP_mcp-door.md)
<!-- /prompts:order -->
