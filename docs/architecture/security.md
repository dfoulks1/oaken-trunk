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

- One guard sits in front of every HTTP surface (ingest, consume, admin, MCP). A key opens only the surfaces it
  was issued for, and each operation declares its surface. The surface sets the limits and caller class.
- An unsigned, badly signed, stale, replayed or cross-surface request is refused before any route exists.
- Only a health route is open, and it answers `ok` and nothing else.
- A setting that is missing or invalid fails closed. A non-loopback surface with no authenticator will not start.

## The guard

Core owns freshness, replay and the default deny. An authenticator only verifies, and cannot weaken them. In the order a request meets it: Host, Origin and content type; the surface's authenticator; then per-client
rate, body size and concurrency limits. The surface sets the caller class and a client cannot raise it.

## Schemes

| Scheme | Notes |
|---|---|
| `ed25519` | Default. A strict RFC 9421 profile with `Content-Digest` checked as the body streams (a mismatch aborts the write), timestamp and nonce. The server stores public keys only. |
| `apptoken` | Per-device `toaken_` tokens for POP3, the Dovecot-auth bridge and enrollment. Stored as scrypt hashes, with lockout. |
| `hmac` | Later. SigV4-style shared secret; the server would hold every secret. |
| `mtls` | Later. Client certificates at the TLS layer. |
| `bearer` | Off unless enabled, loopback only, and `doctor` warns. |

Change it with one line per surface: `[security.ingest] scheme = "ed25519"`. A third party can add a scheme as an
authenticator plugin ([Writing a plugin](../plugins.md)).

## Keys and replay

- `steamer keys add|list|revoke --surface NAME` manages keys. Private keys go to the client and are never
  kept on the server. Key files are created mode 0600 from the first byte.
- A timestamp window (`max_clock_skew_seconds`) and a bounded in-memory nonce cache stop replays. It is in-process at one worker, and held by the supervisor
  with more (a restart empties it, and the window bounds replay). With more than one worker, an unreachable
  supervisor makes the guard refuse requests.
- Signatures, keys and message content are never logged.

## The local CLI

`steamer` talks to the daemon over a Unix socket, gated by a built-in peer-credential check. It is not an
authenticator and never meets the network guard. Windows uses loopback and an owner-only key.

## Other protocols

SMTP uses STARTTLS and AUTH over TLS, with a recipient allowlist and no open relay. LMTP uses a Unix socket
with file permissions and peer credentials. Each is an authenticator, not a signed HTTP request.
