# Mail authentication: the stage, the resolver and DKIM

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CORE.md`, ADR 0011.
**Depends on:** [CORE_engine](CORE_engine.md), [CORE_plugin-host](CORE_plugin-host.md).
**Lift:** L
**Delivers:** A streaming authentication stage, an injectable DNS resolver, `Authentication-Results`, and DKIM verification
**Track:** `CORE_`. CORE_mail-policy adds SPF, DMARC and ARC on this stage.

## Goal

Native inbound DKIM (ADR 0011) without holding a whole message in memory, and the stage the other checks
plug into.

## Requirements

**A. Stage and resolver**

1. **Stage.** Holds only the header block (`max_header_bytes`) and computes DKIM body hashes incrementally as
   the body streams to the spool, through the engine's digest taps.
2. **Resolver.** Injectable, so tests use fakes and never real DNS. Bounded lookups and timeouts. A lookup
   failure is a temporary failure, never a pass.
3. **`Authentication-Results`** (RFC 8601). Stamp one; strip one arriving from outside unless it is from a
   host in `trusted_hops`. Results also go on the envelope.

`compact`

**B. DKIM**

4. **Verify** per RFC 6376, with Ed25519 per RFC 8463. Every signature is evaluated; the result is recorded,
   never used to refuse here.
5. **Hooks.** Plugin hooks for key lookup. Outbound signing is CORE_send.
6. **Docs.** `mail-authentication.md` citing the RFCs, softmap, status table.

## Acceptance criteria

- Synthetic keys and messages pass and fail DKIM as expected. A message larger than memory is verified with
  only the header block held.
- A forged external `Authentication-Results` is stripped; a trusted hop's is kept.
- No real DNS in tests. Standard checks pass.

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
