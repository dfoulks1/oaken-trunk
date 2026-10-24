+++
title = "Security"
subtitle = "Secure by default, signed requests on every port"
lead = "Every network surface refuses requests that are not signed, before any route runs. The scheme is a plugin you choose per surface, and every setting fails closed."
badges = [["text-bg-warning", "Pre-alpha"]]
description = "The request guard, the signing schemes, keys, replay protection and the threat model."
group = "concepts"
order = 85
+++

## Secure by default

Decisions are in [ADR 0010](repo:docs/adr/0010-signed-requests-by-default.md). The short version:

- Each HTTP surface (ingest, consume, admin, MCP) has its own guard, keys, limits and caller class.
- An unsigned, badly signed, stale, replayed or cross-surface request is refused before any route exists.
- Only a health route is open, and it answers `ok` and nothing else.
- A setting that is missing or invalid fails closed. A non-loopback surface with no authenticator will not start.

## The guard

In the order a request meets it: Host, Origin and content type; the surface's authenticator; then per-client
rate, body size and concurrency limits. The surface sets the caller class and a client cannot raise it.

## Schemes

| Scheme | Notes |
|---|---|
| `ed25519` | Default. RFC 9421 HTTP Message Signatures with `Content-Digest`, timestamp and nonce. The server stores public keys only. |
| `hmac` | SigV4-style shared secret. Simple, but the server holds every secret. |
| `mtls` | Client certificates at the TLS layer. |
| `bearer` | Off unless enabled, loopback only, and `doctor` warns. |

Change it with one line per surface: `[security.ingest] scheme = "hmac"`. A third party can add a scheme as an
authenticator plugin ([Writing a plugin](../plugins.md)).

## Keys and replay

- `oaken-trunk keys add|list|revoke --surface NAME` manages keys. Private keys go to the client and are never
  kept on the server. Key files are created mode 0600 from the first byte.
- A timestamp window (`max_clock_skew_seconds`) and a nonce cache shared across workers through the
  supervisor stop replays. If the supervisor is unreachable, the guard refuses requests.
- Signatures, keys and message content are never logged.

## Other protocols

SMTP uses STARTTLS and AUTH over TLS, with a recipient allowlist and no open relay. LMTP uses a Unix socket
with file permissions and peer credentials. Each is an authenticator, not a signed HTTP request.
