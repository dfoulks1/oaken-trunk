# Prompt index

Generated from [`prompts.toml`](prompts.toml). Edit that, then run `uv run python docs/tools/prompts.py sync`.
Rules and shared context are in [CONTEXT.md](CONTEXT.md).

## Master list: done and not done

<!-- prompts:master -->
| Prompt | Status | Target | Lift | Delivers | Depends on |
|---|---|---|---|---|---|
| [CORE_bootstrap](CORE_bootstrap.md) | Built | 0.1 | M | uv workspace, tooling, legal files, a green empty project | — |
| [CORE_foundations](CORE_foundations.md) | Built | 0.1 | L | Paths, settings, the envelope, message ids, the error table, the Ingestor and Spool contracts, listener events, `Credits` and the test doubles | CORE_bootstrap |
| [CORE_engine](CORE_engine.md) | Built | 0.1 | L | The engine: limiter, ingest pipeline, header block and digest, listener dispatch and the commit | CORE_foundations |
| [CORE_operation-registry](CORE_operation-registry.md) | Written | 0.1 | L | Typed operations, surfaces, confirm gate, schemas, `submit` and `version`; the command path | CORE_engine |
| [CORE_daemon](CORE_daemon.md) | Written | 0.1 | L | The daemon: composition root, lifecycle, and the registry served over a local Unix socket | CORE_operation-registry |
| [CORE_supervisor](CORE_supervisor.md) | Written | 0.1 | L | The supervisor and worker management, running in-process at `workers.count = 1` | CORE_daemon |
| [CLI_client](CLI_client.md) | Written | 0.1 | M | The `steamer` command: start, stop, reload, a generic runner and verbs generated from schemas | CORE_daemon |
| [CORE_system-operations](CORE_system-operations.md) | Written | 0.1 | L | `init`, `doctor`, `status`, `stats` and the config operations | CORE_daemon, CORE_supervisor |
| [CORE_audit-and-jobs](CORE_audit-and-jobs.md) | Written | 0.1 | L | Content-free audit log, stats rollup, the job runner and `checkup`, the maintenance sweep | CORE_daemon, CORE_system-operations |
| [CORE_plugin-host](CORE_plugin-host.md) | Written | 0.1 | L | Entry-point discovery, base classes, lifecycle, contract suites | CORE_system-operations |
| [CORE_store](CORE_store.md) | Written | 0.1 | L | `BaseStore` and its primitives, and the core spool, `Locks`, `Credits`, `NonceStore` and device registry built on them | CORE_plugin-host, CORE_supervisor |
| [CORE_encryption](CORE_encryption.md) | Written | 0.1 | M | Streaming envelope encryption between the core spool and the stores, with key files, rotation and checks | CORE_store |
| [PLUGIN_directory-spool](PLUGIN_directory-spool.md) | Written | 0.1 | M | `BaseStore` primitives on local disk: blobs as files, indexes as journals, strict/batched/volatile durability | CORE_store |
| [CORE_consumer-api](CORE_consumer-api.md) | Written | 0.1 | M | The consumer operations, the lease rules and wake-up | PLUGIN_directory-spool |
| [CORE_diagnostics](CORE_diagnostics.md) | Written | 0.1 | M | Mail-path checks for `doctor`, and the operations an operator uses to trace a message or a device | CORE_system-operations, CORE_audit-and-jobs, CORE_consumer-api |
| [CORE_request-guard](CORE_request-guard.md) | Written | 0.1 | L | The authenticator plugin kind, the guard pipeline and surfaces, and ed25519 signed requests | CORE_plugin-host, CORE_supervisor, CORE_store |
| [CORE_keys](CORE_keys.md) | Written | 0.1 | M | `apptoken` and `bearer` authenticators, and key operations in the registry, live on every host | CORE_request-guard, CORE_store |
| [CORE_line-server](CORE_line-server.md) | Written | 0.1 | L | `BaseLineServer`, and `BaseIngestor` and `BaseRetriever` on top of it, with the retriever session as a transaction | CORE_store, CORE_keys |
| [PLUGIN_mail-protocols](PLUGIN_mail-protocols.md) | Written | 0.1 | M | Three command tables on the line server: LMTP (Postfix delivers), POP3 (clients read), Dovecot-auth (Postfix submission logs in) | CORE_line-server, CORE_consumer-api |
| [CORE_http-listener](CORE_http-listener.md) | Written | 0.1 | M | The TCP and TLS listener with the request guard in front, and HTTP submission on the ingest surface | CORE_daemon, CORE_request-guard |
| [CORE_enrollment](CORE_enrollment.md) | Written | 0.1 | M | Self-service device registration over HTTP: an authenticated request for a token for device `IDENTIFIER` | CORE_http-listener, CORE_keys |
| [CORE_security-hardening](CORE_security-hardening.md) | Written | 0.1 | M | Injection, auth and open-relay test pass across every ingestor | PLUGIN_mail-protocols, CORE_consumer-api, CORE_http-listener |
| [DOCS_docs-site](DOCS_docs-site.md) | Partly built | 0.1 | S | Docs site tooling | CORE_bootstrap, CORE_operation-registry, CORE_daemon |
| [PLUGIN_mta-adapters](PLUGIN_mta-adapters.md) | Written | 0.1 | S | First-party qmail and Postfix commands that wrap `submit` with each MTA's conventions | CORE_plugin-host, CLI_client, CORE_operation-registry |
| [DOCS_mta-guides](DOCS_mta-guides.md) | Written | 0.1 | M | Tested guides for handing mail from qmail and Postfix to Trunk | PLUGIN_mta-adapters, PLUGIN_mail-protocols, CORE_request-guard |
| [WEBUI_management-ui](WEBUI_management-ui.md) | Written | later | L | Operator web app on its own port: status, queue, leases, failures, configuration and `doctor`, read only | CORE_system-operations, CORE_audit-and-jobs, CORE_http-listener |
| [WEBUI_operator-actions](WEBUI_operator-actions.md) | Written | later | M | Devices, diagnostics and every mutating action the CLI has, as UI pages with confirmation | WEBUI_management-ui, CORE_diagnostics, CORE_enrollment |
| [CORE_mail-authentication](CORE_mail-authentication.md) | Written | later | L | A streaming authentication stage, an injectable DNS resolver, `Authentication-Results`, and DKIM verification | CORE_engine, CORE_plugin-host |
| [CORE_mail-policy](CORE_mail-policy.md) | Written | later | M | SPF, DMARC (record or enforce) and ARC (record only), on the stage and resolver of CORE_mail-authentication | CORE_mail-authentication |
| [CORE_send](CORE_send.md) | Written | later | L | Outbound spool, the Sender plugin kind, DKIM signing | CORE_consumer-api, CORE_request-guard |
| [PLUGIN_smtp-ingest](PLUGIN_smtp-ingest.md) | Written | later | M | SMTP on 25 and 587: STARTTLS, AUTH, recipient allowlist | PLUGIN_mail-protocols |
| [PLUGIN_redis-spool](PLUGIN_redis-spool.md) | Written | later | M | `BaseStore` primitives on Redis, with atomic overrides for the hot spool operations | PLUGIN_directory-spool |
| [PLUGIN_s3-sqs-spool](PLUGIN_s3-sqs-spool.md) | Written | later | M | `BaseStore` primitives on S3, with one optional SQS queue to wake consumers | PLUGIN_directory-spool |
| [MCP_mcp-door](MCP_mcp-door.md) | Written | later | L | Optional MCP door for diagnostics: off by default, each read-only operation enabled by name. Not part of 0.1 | CORE_operation-registry, CORE_system-operations, CORE_http-listener |
<!-- /prompts:master -->

## Build order

Computed from `depends`, so it cannot contradict them. Target 0.1 comes first.

<!-- prompts:order -->
**Target 0.1**

1. [CORE_bootstrap](CORE_bootstrap.md)
2. [CORE_foundations](CORE_foundations.md)
3. [CORE_engine](CORE_engine.md)
4. [CORE_operation-registry](CORE_operation-registry.md)
5. [CORE_daemon](CORE_daemon.md)
6. [CORE_supervisor](CORE_supervisor.md)
7. [CLI_client](CLI_client.md)
8. [CORE_system-operations](CORE_system-operations.md)
9. [CORE_audit-and-jobs](CORE_audit-and-jobs.md)
10. [CORE_plugin-host](CORE_plugin-host.md)
11. [CORE_store](CORE_store.md)
12. [CORE_encryption](CORE_encryption.md)
13. [PLUGIN_directory-spool](PLUGIN_directory-spool.md)
14. [CORE_consumer-api](CORE_consumer-api.md)
15. [CORE_diagnostics](CORE_diagnostics.md)
16. [CORE_request-guard](CORE_request-guard.md)
17. [CORE_keys](CORE_keys.md)
18. [CORE_line-server](CORE_line-server.md)
19. [PLUGIN_mail-protocols](PLUGIN_mail-protocols.md)
20. [CORE_http-listener](CORE_http-listener.md)
21. [CORE_enrollment](CORE_enrollment.md)
22. [CORE_security-hardening](CORE_security-hardening.md)
23. [DOCS_docs-site](DOCS_docs-site.md)
24. [PLUGIN_mta-adapters](PLUGIN_mta-adapters.md)
25. [DOCS_mta-guides](DOCS_mta-guides.md)

**Target later**

26. [WEBUI_management-ui](WEBUI_management-ui.md)
27. [WEBUI_operator-actions](WEBUI_operator-actions.md)
28. [CORE_mail-authentication](CORE_mail-authentication.md)
29. [CORE_mail-policy](CORE_mail-policy.md)
30. [CORE_send](CORE_send.md)
31. [PLUGIN_smtp-ingest](PLUGIN_smtp-ingest.md)
32. [PLUGIN_redis-spool](PLUGIN_redis-spool.md)
33. [PLUGIN_s3-sqs-spool](PLUGIN_s3-sqs-spool.md)
34. [MCP_mcp-door](MCP_mcp-door.md)
<!-- /prompts:order -->
