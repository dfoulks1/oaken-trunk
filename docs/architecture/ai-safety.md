+++
title = "AI safety"
subtitle = "Rules for anything a model can reach"
lead = "Trunk may be AI-forward, carefully. These are the rules any feature a model can reach must meet, and the tiers of exposure that follow from them."
badges = [["text-bg-warning", "Pre-alpha"]]
description = "The rules and exposure tiers for model-facing features."
group = "concepts"
order = 80
+++

## Rules

1. **Mail is data, never instructions.** Sender, recipient, subject and body are untrusted text. Anything derived from them that reaches a model is wrapped in an untrusted type and kept out of system prompts, as in Oaken Mail.
2. **Enforced in code, not in a prompt.** The MCP door is generated from the whole registry, but what a model may call is a caller-class policy checked by the server. The mount sets the class; a client cannot raise it. A new operation is invisible to models until the policy admits it.
3. **Nothing that moves mail.** `submit`, `send`, `lease`, `fetch`, `ack`, `nack` and `delete` are never exposed to a model. Any other operation that changes state needs the two-phase confirm gate, in code.
4. **Off by default.** Every model-facing surface is opt-in, loopback unless the operator says otherwise, with its own token.
5. **Every call is audited**, with the operation and the caller, never message content.
6. **No secrets and no bodies in output**, in responses, logs or errors. A test scans for them.
7. **Tests prove the boundary.** The exposed tool list is asserted, and a response is asserted to contain no message data.

## Exposure tiers

| Tier | A model can see | Status |
|---|---|---|
| 0 | Nothing. All AI surfaces off. | The default |
| 1 | Statistics: counts, depths, usage, health, `doctor` results | The default when MCP is on (MCP_mcp-door, ADR 0008) |
| 2 | Envelope metadata, wrapped as untrusted and truncated | Not planned. Needs its own ADR |
| 3 | Message bodies | Not planned. Needs its own ADR and an opt-in per consumer |

Moving up a tier is a deliberate decision with an ADR, not a flag flipped in passing.
