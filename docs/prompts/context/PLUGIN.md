# Context: PLUGIN_ prompts

Read with [CONTEXT.md](../CONTEXT.md). One first-party ingestor or spool.

- **Extend a base class.** `BaseIngestor` or `BaseSpool`. Capabilities come from the methods you override,
  returns are coerced with readable errors, and the contract suite is the test (ADR 0006, `plugins.md`).
- **Kinds:** ingestor, retriever, spool, listener, sender, authenticator. The plugin does the primitive. Core's host
  adapter for the kind owns timeouts, isolation, validation and policy.
- **Packaging.** The core wheel ships a default plugin set. Heavy plugins (Redis, S3+SQS) are separate
  workspace packages. Entry points: `oaken_trunk.ingestors`, `.retrievers`, `.spools`, `.listeners`, `.senders`,
  `.authenticators`.
- **Boundaries.** Import only the contract layer. Never another plugin, never another plugin's storage.
- **Operations.** A method marked `@command` becomes `plugin.verb` in the registry, on the `admin` surface,
  MCP off. An unmarked method is unreachable. A plugin cannot add routes or listeners, or take a core name.
  The operator's allow-list can switch any operation off.
- **Trust.** Plugins are trusted in-process code. The decorator limits what is exposed, not what the code
  can do.
- **Model:** oaken-mail's `command` decorator (`oaken.plugins.base`) and `oaken_gmail`. A mutating command
  can name a `preview` method.
- **Touch points.** Name the core files you change. Need more, stop and ask.
