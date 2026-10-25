# Plugin host: the loader and the base classes

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CORE.md`, `docs/prompts/context/PLUGIN.md`,
`docs/plugins.md`, ADR 0006.
**Depends on:** [CORE_system-operations](CORE_system-operations.md).
**Track:** `CORE_`. Model: oaken-mail's `oaken/plugins/` (`base`, `host`, `contracts`, `plugin_ops`).
**Delivers:** Entry-point discovery, base classes, lifecycle, contract suites

## Goal

Load plugins, give them a small base class, and fill the registry with what they declare. A bad plugin
never stops core.

## Decided

- The loader populates the registry. Core ships only the operations the product needs.
- Import path: `oaken_trunk.plugins.base` (as oaken-mail), re-exported from `oaken_trunk.plugins`. That, and the
  contract types, is all a plugin may import from core.
- `BasePlugin` is the root. Each kind extends it. A plugin that is none of the kinds (an autoscaler, a
  reporter) extends it directly, in the group `oaken_trunk.plugins`: lifecycle, `@command` and `ctx.ops`, and
  nothing else. Its only power is its declared `calls` and its commands.
- Kinds: ingestor, spool, listener here. Sender is CORE_send. Authenticator is CORE_request-guard.
- A listener has up to four methods, `on_envelope`, `on_headers`, `on_end`, `on_stored`. Capabilities
  come from which are overridden.
- A plugin calls operations through `ctx.ops`, not an import. The host builds it at load from the registry:
  `ctx.ops.add_worker(...)`, typed like the operation. It lists the operations it may call (`calls = [...]`)
  and gets only those. A call goes through the same permission check and audit as an operator's, under the
  plugin's name. `submit` for ingestors is the first case.
- Plugins are trusted in-process code. The decorator limits what is exposed, not what the code can do.

**Operations added:** none. This prompt is the mechanism. The core list is in CORE_operation-registry.

## Not in scope

The operations plugins add (each plugin's own prompt). Sender and authenticator bases (CORE_send, CORE_request-guard). The guard.
The listeners themselves (CORE_mail-authentication).

## Requirements

Stop at each `compact` line: checks green, status block updated, then compact the session.

**A. Loader and bridge**

1. **`BasePlugin`.** The root of every kind, and usable alone. `ctx` (settings, logger, clock, limits, `ops`), `start`, `stop`, `health`, capabilities
   inferred from overrides, lenient returns with readable errors.
2. **Loader.** Entry points `oaken_trunk.plugins`, `.ingestors`, `.spools`, `.listeners`. First-party plugins register
   as a third party's would. A plugin that fails to load adds nothing, and `doctor` says why.
3. **Contract version.** A plugin states the contract it targets. A mismatch is refused with a clear message.
4. **`@command`.** A marked method becomes `plugin.verb`: typed input and output, `permission`, `mcp` (`off`
   or `never`), optional `preview`. Default surface `admin`. A core name cannot be taken. An unmarked method
   is unreachable.
5. **Seal.** Plugin operations register until startup ends, then the registry seals. Enable and disable apply
   by reload, which rebuilds it in one step. A disabled plugin's operation is refused at call time.
6. **Settings.** Validated by the plugin's pydantic model. A secret-named key is refused. `setup_help` and
   `config_example` are class attributes. The operator can switch off a capability or operation per plugin.

`compact`

**B. Spool**

7. **`BaseSpool`.** The author writes `write`, `commit`, `abort`, `lease`, `open`, `ack`. The base presents the
   first three to core as the `writer`. The spool adapter owns timeouts and isolation.
8. **`SpoolContract`.** Streaming and memory, abort leaves nothing, nothing leasable before `commit`, lease
   expiry, recovery.

`compact`

**C. Ingestor**

9. **`BaseIngestor`.** The author writes `listen(submit)`. `submit` is the registry's operation, called
   in-process as caller class `plugin`. The ingestor never touches the spool. `IngestorContract` covers
   backpressure replies and the streaming rule.

`compact`

**D. Listener**

10. **`BaseListener`.** Up to four methods, `on_envelope`, `on_headers`, `on_end`, `on_stored`. The adapter
    calls them in order with the timeouts of CORE_contracts-and-core, validates each structured result, and allows a header only
    if the listener declared its name. `ListenerContract` covers the same.

`compact`

**E. Close**

11. **Import contracts.** Plugins import only the contract layer. Core imports no plugin.
12. **Docs.** `plugins.md` (five kinds, `@command`, writer shape, `listen(submit)`), ADR 0006 amended,
    softmap, status table.

## Acceptance criteria

- A fake third-party plugin of each kind registers and passes its suite.
- A plugin that raises on load, on start and in a handler is reported by `doctor`. Core keeps running.
- A plugin operation named like a core one is refused. An unmarked method cannot be called.
- A plugin added after seal is refused. Reload with a plugin disabled removes its operations.
- A listener that adds `From:` is rejected. A result that is not valid is recorded and ingestion carries on.
- A plugin that buffers a whole message fails the streaming test.
- A contract-version mismatch is refused with the version in the message. Standard checks pass.

## Open questions (defaults in bold)

1. Is HTTP ingest an ingestor plugin? **No. It is `submit` on the `ingest` surface (CORE_http-listener). Socket-owning
   ingestors (LMTP, SMTP) run `listen(submit)`.**
2. Where do settings live? **Per-kind tables as in `config.example.toml` (`[ingest.x]`, `[spool.x]`,
   `[listener.x]`).**
3. Contract-version policy? **Exact match until 1.0.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
