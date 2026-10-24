# 18 - Request guard and authenticators

**Read first:** `docs/prompts/00-context.md`. **Depends on:** 04.

## Goal

One guard in front of every HTTP surface that refuses unsigned requests before any route runs, and the
authenticator plugin kind that decides what "signed" means (ADR 0010).

## Steps

1. `BaseAuthenticator`, `Principal` and `AuthenticatorContract` in the plugin layer; entry-point group `oaken_trunk.authenticators`; the contract suite covers unsigned, badly signed, stale, replayed and cross-surface requests.
2. A pure-ASGI guard, in the order: Host, Origin and content type; the surface's authenticator; per-client rate, body size and concurrency limits. A request passes it before any route exists. Only a health route is open, answering `ok` and nothing else. Any error fails closed.
3. Surfaces are path-and-port scoped (ingest, consume, admin, mcp), each with its own scheme, keys, limits and caller class; the surface sets the class and a client cannot raise it.
4. First-party authenticators: `ed25519` (RFC 9421 HTTP Message Signatures, `Content-Digest`, timestamp and nonce; public keys only on the server), `hmac` (SigV4-style), `mtls`, and `bearer` (off unless enabled, loopback only; `doctor` warns).
5. Freshness and replay: `max_clock_skew_seconds` window; the nonce cache is held by the supervisor so it is shared across workers; an unreachable supervisor fails closed.
6. Key management as operations with CLI commands: `oaken-trunk keys add|list|revoke --surface NAME`. Private keys are written for the client only and never kept on the server; key files are created mode 0600 from the first byte.
7. Config is `[security.<surface>] scheme = "..."` as in `config.example.toml`; `doctor` verifies each surface and refuses a configuration that leaves a non-loopback surface unauthenticated.
8. Signatures, keys and message content are never logged.

## Acceptance criteria

- With every first-party scheme, a request that is unsigned, badly signed, stale, replayed, signed for another surface or signed with a revoked key is refused before any route runs.
- Switching a surface's scheme is a one-line config change and passes the same tests.
- A third-party authenticator registered through an entry point works through the guard unchanged.
- `ruff check`, `ruff format --check`, `mypy`, `lint-imports` and `pytest` pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Checkpoint

Use the report format from `00-context.md`, then stop.
