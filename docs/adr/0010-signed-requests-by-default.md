# 10. Every network surface refuses unsigned requests; the scheme is a plugin

- Status: accepted
- Date: 2026-10-24
- Amended: 2026-10-24 (see Amendment)

## Context

Trunk is server-side and network-facing. Oaken Mail's API defends a loopback port with one pure-ASGI guard
that every request passes before any route (its ADR 0005), and both products are plugin-extensible. The
owner wants security by default, with requests to a port accepted only if signed, and the scheme easy to
change.

## Decision

- **Every HTTP surface** (ingest, consumer API, management UI, MCP) runs behind one guard. A request that is
  unsigned, badly signed, stale or replayed is refused before any route runs. The only open route is a
  health check that says `ok` and nothing else. Failing closed is the default for every setting.
- **The scheme is a plugin kind**, the authenticator (`oaken_trunk.authenticators`, base class
  `BaseAuthenticator`), chosen per surface in config. First-party schemes: `ed25519` (RFC 9421 HTTP Message
  Signatures with `Content-Digest`, the default), `hmac` (SigV4-style shared secret), `mtls`, and `bearer`
  (off unless explicitly enabled, loopback only, and `doctor` warns).
- **Per-surface keys.** A key opens only its own surface. With `ed25519` the server stores public keys only.
- **Replay and freshness.** A timestamp window and a nonce, with the nonce cache held by the supervisor so
  it is shared across workers (see Amendment).
- **Guard order:** Host, Origin and content type, authenticator, then per-client rate, body size and
  concurrency limits. The caller class is set by the surface, never by the client.
- **Not HTTP, so not signed requests:** SMTP uses STARTTLS and AUTH over TLS, LMTP uses a Unix socket with
  file permissions and peer credentials, each through its own authenticator.
- **Secrets:** private keys never live on the server, key files are created `0600` from the first byte, and
  signatures and keys are never logged.
- **Easy to configure:** `[security.<surface>] scheme = "..."` is one line, `steamer keys add|list|revoke`
  manages keys, and `doctor` verifies the result.

## Consequences

Changing scheme is a config change, and a third party can add one. Every client, including the CLI and the
MCP bridge, must sign; they do so automatically from a key file. The supervisor's counter service also carries
the nonce cache, so a supervisor outage fails closed.

## Amendment

Settled while reviewing the prompts.

- **Core owns the policy.** Freshness, replay, the default deny and the guard order are core's. An
  authenticator only `verify`s: it returns a principal or refuses. A scheme cannot weaken them.
- **Surfaces belong to the key and the operation**, not to a path or port. One guard, one HTTP listener. A key
  opens only the surfaces it was issued for, and each operation declares its surface (`ingest`, `consume`,
  `admin`, `mcp`; default `admin`).
- **`ed25519` is a strict RFC 9421 profile.** `Content-Digest` is verified incrementally as the body streams,
  and a mismatch aborts the spool writer, so nothing is committed. `cryptography` is a core dependency.
- **Nonce cache.** Bounded and in memory behind a `NonceStore` interface. At `workers.count = 1` the supervisor
  runs in the same process, so the cache is in-process. With more workers it lives in the supervisor
  (CORE_supervisor). A restart empties it, so the timestamp window is the bound on replay across a restart.
- **Local CLI.** It uses the Unix socket, gated by the daemon's built-in peer-credential check. That is not an
  authenticator plugin, and it never reaches the network guard. Windows uses loopback plus an owner-only key.
- **`mtls` and `hmac` are later.** `bearer` (loopback only) and `apptoken` (device logins, ADR 0013) ship with
  `ed25519`. (Amended 2026-10-28: `hmac` moved later.)
- **No supervisor outage in 0.1.** The supervisor is in-process at the defaults, so "supervisor unreachable"
  only exists with more than one worker.
