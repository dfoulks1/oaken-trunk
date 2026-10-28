# Prompt index

Generated from [`prompts.toml`](prompts.toml). Edit that, then run `uv run python docs/tools/prompts.py sync`.
Rules and shared context are in [CONTEXT.md](CONTEXT.md).

## Master list: done and not done

<!-- prompts:master -->
| Prompt | Status | Target | Lift | Delivers | Depends on |
|---|---|---|---|---|---|
| [CORE_bootstrap](CORE_bootstrap.md) | Open | 0.1 | M | uv workspace, tooling, legal files, a green empty project | — |
| [CORE_foundations](CORE_foundations.md) | Written | 0.1 | M | Paths, settings, the envelope, message ids and the error table | CORE_bootstrap |
| [CORE_contracts](CORE_contracts.md) | Written | 0.1 | M | Ingestor and Spool contracts with the writer, listener event types, `Credits`, and the test doubles | CORE_foundations |
| [CORE_engine](CORE_engine.md) | Written | 0.1 | L | The engine: limiter, ingest pipeline, header block and digest, listener dispatch and the commit | CORE_contracts |
| [CORE_operation-registry](CORE_operation-registry.md) | Written | 0.1 | L | Typed operations, surfaces, confirm gate, schemas, `submit` and `version`; the command path | CORE_engine |
| [CORE_daemon](CORE_daemon.md) | Written | 0.1 | L | The daemon: composition root, lifecycle, and the registry served over a local Unix socket | CORE_operation-registry |
| [CORE_supervisor](CORE_supervisor.md) | Written | 0.1 | L | The supervisor and worker management, running in-process at `workers.count = 1` | CORE_daemon |
| [CLI_client](CLI_client.md) | Written | 0.1 | M | The `steamer` command: start, stop, reload, a generic runner and verbs generated from schemas | CORE_daemon |
| [CORE_system-operations](CORE_system-operations.md) | Written | 0.1 | L | `init`, `doctor`, `status`, `stats` and the config operations | CORE_daemon, CORE_supervisor |
| [CORE_audit-and-jobs](CORE_audit-and-jobs.md) | Written | 0.1 | L | Content-free audit log, stats rollup, the job runner and `checkup`, the maintenance sweep | CORE_daemon, CORE_system-operations |
| [CORE_diagnostics](CORE_diagnostics.md) | Written | 0.1 | M | Mail-path checks for `doctor`, and the operations an operator uses to trace a message or a device | CORE_system-operations, CORE_audit-and-jobs, CORE_consumer-api |
| [CORE_plugin-host](CORE_plugin-host.md) | Written | 0.1 | L | Entry-point discovery, base classes, lifecycle, contract suites | CORE_system-operations |
| [CORE_store](CORE_store.md) | Written | 0.1 | L | `BaseStore` and its primitives, and the core spool, `Locks`, `Credits`, `NonceStore` and device registry built on them | CORE_plugin-host, CORE_supervisor |
| [CORE_line-server](CORE_line-server.md) | Written | 0.1 | L | `BaseLineServer`, and `BaseIngestor` and `BaseRetriever` on top of it, with the retriever session as a transaction | CORE_store, CORE_request-guard |
| [PLUGIN_directory-spool](PLUGIN_directory-spool.md) | Written | 0.1 | M | `BaseStore` primitives on local disk: blobs as files, indexes as journals, strict/batched/volatile durability | CORE_store |
| [CORE_consumer-api](CORE_consumer-api.md) | Written | 0.1 | M | The consumer operations, the lease rules and wake-up | PLUGIN_directory-spool |
| [PLUGIN_lmtp-ingest](PLUGIN_lmtp-ingest.md) | Written | 0.1 | S | LMTP over a Unix socket: the Postfix delivery target | CORE_line-server, CORE_daemon |
| [CORE_request-guard](CORE_request-guard.md) | Written | 0.1 | XL | Signed-requests guard and the authenticator plugin kind | CORE_plugin-host, CORE_supervisor |
| [CORE_http-listener](CORE_http-listener.md) | Written | 0.1 | M | The TCP and TLS listener with the request guard in front, and HTTP submission on the ingest surface | CORE_daemon, CORE_request-guard |
| [CORE_security-hardening](CORE_security-hardening.md) | Written | 0.1 | M | Injection, auth and open-relay test pass across every ingestor | PLUGIN_lmtp-ingest, CORE_consumer-api, CORE_http-listener, PLUGIN_pop3-retriever |
| [DOCS_docs-site](DOCS_docs-site.md) | Partly built | 0.1 | S | Docs site tooling | CORE_bootstrap, CORE_operation-registry, CORE_daemon |
| [PLUGIN_mta-adapters](PLUGIN_mta-adapters.md) | Written | 0.1 | S | First-party qmail and Postfix commands that wrap `submit` with each MTA's conventions | CORE_plugin-host, CLI_client, CORE_operation-registry |
| [PLUGIN_pop3-retriever](PLUGIN_pop3-retriever.md) | Written | 0.1 | S | POP3 over TLS onto list, lease, fetch and ack, with the protocol's own delete-on-QUIT as the ack | CORE_line-server, CORE_consumer-api |
| [PLUGIN_sasl-bridge](PLUGIN_sasl-bridge.md) | Written | 0.1 | S | A Dovecot-auth socket, so Postfix submission authenticates with `toaken_` device tokens | CORE_line-server |
| [DOCS_mta-guides](DOCS_mta-guides.md) | Written | 0.1 | M | Tested guides for handing mail from qmail and Postfix to Trunk | PLUGIN_mta-adapters, PLUGIN_lmtp-ingest, CORE_request-guard, PLUGIN_pop3-retriever, PLUGIN_sasl-bridge |
| [WEBUI_management-ui](WEBUI_management-ui.md) | Written | 0.1 | XL | Operator web app on its own port, built only on operations the CLI has | CORE_system-operations, CORE_audit-and-jobs, CORE_http-listener |
| [CORE_mail-authentication](CORE_mail-authentication.md) | Written | later | XL | Native inbound DKIM, SPF, DMARC, ARC without buffering a message | CORE_engine, CORE_plugin-host |
| [CORE_send](CORE_send.md) | Written | later | L | Outbound spool, the Sender plugin kind, DKIM signing | CORE_consumer-api, CORE_request-guard |
| [PLUGIN_smtp-ingest](PLUGIN_smtp-ingest.md) | Written | later | M | SMTP on 25 and 587: STARTTLS, AUTH, recipient allowlist | PLUGIN_lmtp-ingest |
| [PLUGIN_redis-spool](PLUGIN_redis-spool.md) | Written | later | M | `BaseStore` primitives on Redis, with atomic overrides for the hot spool operations | PLUGIN_directory-spool |
| [PLUGIN_s3-sqs-spool](PLUGIN_s3-sqs-spool.md) | Written | later | M | `BaseStore` primitives on S3, with one optional SQS queue to wake consumers | PLUGIN_directory-spool |
| [MCP_mcp-door](MCP_mcp-door.md) | Written | later | L | Optional MCP door gated by caller class. Not part of 0.1 | CORE_operation-registry, CORE_system-operations, CORE_http-listener |
<!-- /prompts:master -->

## Build order

Computed from `depends`, so it cannot contradict them. Target 0.1 comes first.

<!-- prompts:order -->
**Target 0.1**

1. [CORE_bootstrap](CORE_bootstrap.md)
2. [CORE_foundations](CORE_foundations.md)
3. [CORE_contracts](CORE_contracts.md)
4. [CORE_engine](CORE_engine.md)
5. [CORE_operation-registry](CORE_operation-registry.md)
6. [CORE_daemon](CORE_daemon.md)
7. [CORE_supervisor](CORE_supervisor.md)
8. [CLI_client](CLI_client.md)
9. [CORE_system-operations](CORE_system-operations.md)
10. [CORE_audit-and-jobs](CORE_audit-and-jobs.md)
11. [CORE_plugin-host](CORE_plugin-host.md)
12. [CORE_store](CORE_store.md)
13. [PLUGIN_directory-spool](PLUGIN_directory-spool.md)
14. [CORE_consumer-api](CORE_consumer-api.md)
15. [CORE_diagnostics](CORE_diagnostics.md)
16. [CORE_request-guard](CORE_request-guard.md)
17. [CORE_line-server](CORE_line-server.md)
18. [PLUGIN_lmtp-ingest](PLUGIN_lmtp-ingest.md)
19. [CORE_http-listener](CORE_http-listener.md)
20. [DOCS_docs-site](DOCS_docs-site.md)
21. [PLUGIN_mta-adapters](PLUGIN_mta-adapters.md)
22. [PLUGIN_pop3-retriever](PLUGIN_pop3-retriever.md)
23. [CORE_security-hardening](CORE_security-hardening.md)
24. [PLUGIN_sasl-bridge](PLUGIN_sasl-bridge.md)
25. [DOCS_mta-guides](DOCS_mta-guides.md)
26. [WEBUI_management-ui](WEBUI_management-ui.md)

**Target later**

27. [CORE_mail-authentication](CORE_mail-authentication.md)
28. [CORE_send](CORE_send.md)
29. [PLUGIN_smtp-ingest](PLUGIN_smtp-ingest.md)
30. [PLUGIN_redis-spool](PLUGIN_redis-spool.md)
31. [PLUGIN_s3-sqs-spool](PLUGIN_s3-sqs-spool.md)
32. [MCP_mcp-door](MCP_mcp-door.md)
<!-- /prompts:order -->
