# Request guard: one gate in front of every HTTP surface

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CORE.md`, `docs/architecture/security.md`,
ADR 0010.
**Depends on:** [CORE_plugin-host](CORE_plugin-host.md), [CORE_supervisor](CORE_supervisor.md), [CORE_store](CORE_store.md).
**Lift:** L
**Delivers:** The authenticator plugin kind, the guard pipeline and surfaces, and ed25519 signed requests
**Track:** `CORE_`. Model: oaken-mail's `oaken/api/guard.py` (its ADR 0005). Tested on a bare ASGI app, so this
needs no daemon.

## Goal

One guard in front of every HTTP surface refuses an unsigned request before any route runs. The scheme is an
authenticator plugin. Core owns the policy, the plugin owns the primitive.

## Decided

- Core owns freshness, replay, the default deny and the failure mode. An authenticator only implements
  `verify(request)` and returns a `Principal` or raises `AuthError`.
- A surface belongs to the key and to the operation, not to a path or a port.
- A `consume` key carries a recipient list: addresses or `@domain`, the same syntax as the `lease` filter. It
  reaches only deliveries to those recipients.
- The Unix socket is gated by CORE_daemon's built-in peer check. It is not an authenticator plugin.
- First-party schemes ship in `oaken_trunk_auth`: `ed25519` here, `apptoken` and `bearer` in CORE_keys.
  `hmac` and mTLS are later.
- Core depends on `cryptography` (Ed25519 here, encryption at rest, DKIM later).

## Not in scope

Key and token management, `apptoken`, `bearer` (CORE_keys). Listeners and routes (CORE_http-listener,
CORE_daemon). mTLS and `hmac` (later). Signing outbound DKIM (CORE_send).

## Requirements

**A. Kind and guard**

1. **Kind.** `BaseAuthenticator`, `Principal` (key id, surface), `AuthenticatorContract`, entry point
   `oaken_trunk.authenticators`. `verify` gets a read-only request view (method, target, headers, digest
   header, peer, TLS). It never reads the body.
2. **Guard.** Pure ASGI. Order: Host allow-list and content type; cheap pre-auth limits (header size,
   per-IP rate); the authenticator; per-principal rate, body size and concurrency. The only open route is
   `GET /v1/health`. Every error fails closed. A refusal is one uniform 401 or 403 with no detail.
3. **Surfaces.** A principal and an operation each belong to one of `ingest`, `consume`, `admin`, `mcp`,
   `enroll`. A mismatch is refused before the route. The listener sets the caller class, never the client.

`compact`

**B. ed25519**

4. **Strict RFC 9421 profile.** Required components: `@method`, `@target-uri`, `host`, `content-digest`,
   with `created`, `nonce`, `keyid`, `alg="ed25519"`. Anything else is refused.
5. **Body digest.** `Content-Digest` is verified incrementally while the body streams. A mismatch ends the
   request, and for `submit` aborts the writer so nothing becomes visible.
6. **Freshness and replay.** `created` must be within `max_clock_skew_seconds`. A nonce seen twice in the
   window is refused. Nonces go through `NonceStore` (CORE_store's coordination store, so every host
   shares them), bounded to rate times window. When full it refuses new nonces.

`compact`

**C. Close**

7. **Config and `doctor`.** `[security.<surface>] scheme = "..."`. `doctor` checks each surface and refuses a
   non-loopback surface with no authenticator.
8. **Never logged:** signatures, keys, bodies.
9. **Docs.** `security.md`, ADR 0010 amended (`hmac` later), `plugins.md`, softmap, status table.

## Acceptance criteria

- A request that is unsigned, badly signed, stale, replayed, for another surface or from a revoked key is
  refused before any route. A spy engine is never called.
- A `consume` key sees only its own recipients.
- A body changed after signing is detected at the end of the stream, and nothing is committed.
- A full nonce store refuses a new nonce. A different `alg`, a missing component or an extra one is refused.
- A raising or slow authenticator fails closed. A third-party authenticator works through the guard unchanged.
- A signature, key and body sentinel never appear in any log or error. Standard checks pass.

## Open questions (defaults in bold)

1. Cache full: refuse or evict? **Refuse.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
