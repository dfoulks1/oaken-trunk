# Mail policy: SPF, DMARC and ARC on the authentication stage

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CORE.md`, ADR 0011, `CORE_mail-authentication.md` (its status block).
**Depends on:** [CORE_mail-authentication](CORE_mail-authentication.md).
**Lift:** M
**Delivers:** SPF, DMARC (record or enforce) and ARC (record only), on the stage and resolver of CORE_mail-authentication
**Track:** `CORE_`. No new stage, no new resolver.

## Goal

The policy checks that sit on DKIM's results, evaluated only when Trunk knows enough to evaluate them.

## Requirements

1. **SPF** per RFC 7208, and **DMARC** per RFC 9989, only when the client address is known (the SMTP edge, or
   a host in `trusted_hops`). Otherwise recorded as not evaluated, never as a pass.
2. **ARC** per RFC 8617, recorded only.
3. **`mailauth.dmarc`** = `off`, `record` (default) or `enforce`. `enforce` answers a published `reject` with a
   permanent 5xx at the protocol edge, worded as Postfix's milters (OpenDMARC) answer it.
4. **Hooks.** Plugin hooks for policy decisions, after core's.
5. **Docs.** `mail-authentication.md`, softmap, status table.

## Acceptance criteria

- Synthetic records pass and fail SPF and DMARC as expected; an unknown client address records "not evaluated".
- `enforce` with a published `reject` refuses with a 5xx; `record` accepts and records.
- No real DNS in tests. Standard checks pass.

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
