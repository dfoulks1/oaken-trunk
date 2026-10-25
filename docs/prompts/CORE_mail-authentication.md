# Mail authentication

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CORE.md`.
**Depends on:** [CORE_engine](CORE_engine.md), [CORE_plugin-host](CORE_plugin-host.md).
**Lift:** XL
**Delivers:** Native inbound DKIM, SPF, DMARC, ARC without buffering a message

## Goal

Native inbound DKIM, SPF, DMARC and ARC handling (ADR 0011), without holding a whole message in memory.

## Steps

1. A core stage that holds only the header block (`max_header_bytes`) and computes the DKIM body hash incrementally as the body streams to the spool.
2. DKIM verification per RFC 6376 with the Ed25519 algorithm of RFC 8463; SPF per RFC 7208; DMARC per RFC 9989; ARC per RFC 8617, recorded only. Cite the RFCs in the docs.
3. SPF and DMARC only when the client address is known (SMTP edge, or a trusted hop in `trusted_hops`); otherwise recorded as not evaluated, never as a pass.
4. Stamp `Authentication-Results` (RFC 8601); strip one arriving from outside unless it is from a trusted hop; record results in the envelope.
5. `mailauth.dmarc` = `off`, `record` (default) or `enforce`; `enforce` answers a published `reject` with a permanent 5xx at the protocol edge.
6. DNS lookups through an injectable resolver so tests use fakes; no real DNS in tests. Bounded lookups and timeouts, and a lookup failure is a temporary failure, never a pass.
7. Plugin hooks for key lookup and policy. Outbound signing is built in CORE_send.

## Acceptance criteria

- Test vectors (synthetic keys and messages) pass and fail DKIM, SPF and DMARC as expected; a message larger than memory is verified with only the header block held.
- A forged external `Authentication-Results` is stripped.
- `ruff check`, `ruff format --check`, `mypy`, `lint-imports` and `pytest` pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Checkpoint

Use the report format from `CONTEXT.md`, then stop.
