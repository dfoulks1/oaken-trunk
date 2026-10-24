# 11. DKIM and DMARC are native; SPF and ARC where the client is known

- Status: accepted
- Date: 2026-10-24

## Context

A gateway that receives and sends mail has to say whether a message is authentic and has to sign what it sends.
Trunk may sit behind Postfix or qmail, which already do some of this, or be the edge itself. Verification must
respect the memory rule: a message is never held whole in memory.

## Decision

- **Inbound.** DKIM verification (RFC 6376, with the Ed25519 algorithm of RFC 8463) is built in and on by default.
  Only the header block is held in memory, bounded by `max_header_bytes`; the body hash is computed incrementally
  while the body streams to the spool. SPF (RFC 7208) and DMARC (RFC 9989, which obsoletes RFC 7489) are evaluated
  when the connecting client address is known: always at the SMTP edge, and behind an MTA only when a trusted
  upstream passes it. ARC (RFC 8617) is verified and recorded, not acted on.
- **Result.** The outcome is stamped as an `Authentication-Results` field (RFC 8601) and recorded in the envelope.
  An `Authentication-Results` field arriving from outside is stripped unless it comes from a configured trusted hop.
- **Enforcement is a setting**, `mailauth.dmarc = "off" | "record" | "enforce"`. `enforce` refuses mail whose
  published policy is `reject` with a permanent 5xx at the protocol edge. The default for 0.1 is `record`.
- **Outbound.** The sender signs with DKIM (RSA-2048 and Ed25519). The body hash is computed from the spooled file in
  a streaming pass and the signature is added when the message is sent, so signing also never holds a whole message.
  Private keys are owner-only files, never in `config.toml`.
- **Native, not a plugin kind.** It is a core stage with plugin hooks for key lookup and policy, because it sits on
  the hot path of every message.

## Consequences

DKIM works the same behind an MTA or at the edge. SPF and DMARC are only as good as the client address they are given,
and the docs say so. A later reporting feature (RFC 9990 aggregate reports) can build on the recorded results.
