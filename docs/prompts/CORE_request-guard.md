# Request guard and authenticators

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CORE.md`, `docs/architecture/security.md`,
ADR 0010.
**Depends on:** [CORE_plugin-host](CORE_plugin-host.md), [CORE_supervisor](CORE_supervisor.md).
**Track:** `CORE_`. Model: oaken-mail's `oaken/api/guard.py` (its ADR 0005). Tested on a bare ASGI app, so
**Lift:** XL
**Delivers:** Signed-requests guard and the authenticator plugin kind
this needs no daemon.

## Goal

One guard in front of every HTTP surface refuses an unsigned request before any route runs. The scheme is an
authenticator plugin. Core owns the policy, the plugin owns the primitive.

## Decided

- Core owns freshness, replay, the default deny and the failure mode. An authenticator only implements
  `verify(request)` and returns a `Principal` or raises `AuthError`. (Tentative.)
- A surface belongs to the key and to the operation, not to a path or a port.
- A `consume` key carries a recipient list: addresses or `@domain`, the same syntax as the `lease` filter. It
  reaches only deliveries to those recipients.
- The Unix socket is gated by CORE_daemon's built-in peer check. It is not an authenticator plugin.
- One first-party package, `oaken_trunk_auth`, ships `ed25519`, `hmac` and `bearer`. mTLS is later.
- Core depends on `cryptography` (Ed25519 now, DKIM later).

## Not in scope

Listeners and routes (CORE_http-listener, CORE_daemon). mTLS (needs the listener's TLS). SMTP AUTH (PLUGIN_smtp-ingest). Signing outbound DKIM (CORE_send).

## Requirements

**A. Kind and guard**

1. **Kind.** `BaseAuthenticator`, `Principal` (key id, surface), `AuthenticatorContract`, entry point
   `oaken_trunk.authenticators`. `verify` gets a read-only request view (method, target, headers, digest
   header, peer, TLS). It never reads the body.
2. **Guard.** Pure ASGI. Order: Host allow-list and content type; cheap pre-auth limits (header size,
   per-IP rate); the authenticator; per-principal rate, body size and concurrency. The only open route is
   `GET /v1/health`. Every error fails closed. A refusal is one uniform 401 or 403 with no detail.
3. **Surfaces.** A principal and an operation each belong to one of `ingest`, `consume`, `admin`, `mcp`.
   A mismatch is refused before the route. The listener sets the caller class, never the client.

`compact`

**B. ed25519**

4. **Strict RFC 9421 profile.** Required components: `@method`, `@target-uri`, `host`, `content-digest`,
   with `created`, `nonce`, `keyid`, `alg="ed25519"`. Anything else is refused.
5. **Body digest.** `Content-Digest` is verified incrementally while the body streams. A mismatch ends the
   request, and for `submit` aborts the writer so nothing becomes visible.
6. **Freshness and replay.** `created` must be within `max_clock_skew_seconds`. A nonce seen twice in the
   window is refused. The nonce cache is in memory, bounded to rate times window, behind a `NonceStore`
   interface (CORE_supervisor moves it). When full it refuses new nonces.

`compact`

**C. The other schemes**

7. **`hmac`** (SigV4-style over the same components, constant-time compare). **`bearer`** (off unless
   enabled, loopback only, refused elsewhere, `doctor` warns). **`apptoken`** for protocol logins (POP3): a
   per-device token, stored hashed with `hashlib.scrypt`, constant-time verify, rate limited per address and
   per username, locked out after `max_failures` (default 10), one generic failure (ADR 0013).
8. **Packaging.** All four in `oaken_trunk_auth`, registered as a third party's would be.

`compact`

**D. Keys and close**

9. **Key operations.** `keys_add`, `keys_list`, `keys_revoke` per surface. `keys_add` takes `--recipients` for a `consume` key, and `--device NAME` for an `apptoken`, printed once. Revoking a
   device ends its sessions and drops its deliveries. It writes the private key
   once to `--out`, mode 0600 from the first byte. The server keeps public keys in `<config>/keys/<surface>`.
   A change takes effect without a restart.
10. **Config and `doctor`.** `[security.<surface>] scheme = "..."`. `doctor` checks each surface and refuses a
    non-loopback surface with no authenticator.
11. **Never logged:** signatures, keys, bodies.
12. **Docs.** `security.md`, ADR 0010 amended, `plugins.md`, softmap, status table.

## Acceptance criteria

- With every scheme, a request that is unsigned, badly signed, stale, replayed, for another surface or from a
  revoked key is refused before any route. A spy engine is never called.
- A `consume` key sees only its own recipients. `keys_add --surface consume` with no `--recipients` is refused.
- A body changed after signing is detected at the end of the stream, and nothing is committed.
- A full nonce cache refuses a new nonce. A different `alg`, a missing component or an extra one is refused.
- A raising or slow authenticator fails closed. `bearer` on a non-loopback bind is refused.
- A third-party authenticator works through the guard unchanged. Switching scheme is one config line.
- A signature, key and body sentinel never appear in any log or error. Standard checks pass.

## Open questions (defaults in bold)

1. Is `hmac` in 0.1? **Yes, it is the easy second scheme.**
2. Key expiry or overlap for rotation? **Overlap by adding before revoking. No expiry field yet.**
3. Cache full: refuse or evict? **Refuse.**
4. A crypto dependency? **`cryptography`.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
