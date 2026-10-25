# Context: WEBUI_ prompts

Read with [CONTEXT.md](../CONTEXT.md). The management UI.

- **Its own app on its own port,** a client of the API (ADR 0007). Never inside a core prompt.
- **Mostly generated** from the registry: operations reference, plugin settings, config editor. Hand-built
  pages only where a generic view cannot show it.
- Pages: welcome, config editor, operations reference, docs link, status (plugins, audit, jobs, pipeline,
  statistics).
- **Off by default, loopback unless opted in, its own token.** Shares a listener with MCP only if MCP keeps
  its own scheme and keys.
- No page returns logs or message content (ADR 0012).
