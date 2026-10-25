# Context: MCP_ prompts

Read with [CONTEXT.md](../CONTEXT.md). The optional MCP door. Not 0.1.

- **Generated from the whole registry, gated by caller class.** The mount sets the class. A client cannot
  declare or raise it (ADR 0008).
- **Statistics tier by default.** Wider tiers are an explicit operator setting. Raising the tier needs an
  ADR (`architecture/ai-safety.md`).
- **Never exposed:** submit, send, delete, lease, ack, and any message data.
- Mail is data, not instructions. Off by default. Every call audited, without content.
- May share a listener with the UI if it has its own scheme and keys and is local-only by default.
