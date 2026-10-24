+++
title = "Mail authentication"
subtitle = "DKIM, SPF, DMARC and ARC"
lead = "Trunk verifies DKIM natively on every inbound message and signs outbound mail, without ever holding a whole message in memory."
badges = [["text-bg-warning", "Pre-alpha"]]
description = "Native DKIM and DMARC, when SPF and DMARC apply behind an MTA, and where the results go."
group = "concepts"
order = 45
+++

## Standards

| Mechanism | Standard | Role in Trunk |
|---|---|---|
| DKIM | [RFC 6376](https://www.rfc-editor.org/rfc/rfc6376), Ed25519 in [RFC 8463](https://www.rfc-editor.org/rfc/rfc8463) | Verified on every inbound message; signed on outbound |
| SPF | [RFC 7208](https://www.rfc-editor.org/rfc/rfc7208) | Evaluated when the client address is known |
| DMARC | [RFC 9989](https://www.rfc-editor.org/rfc/rfc9989), which obsoletes RFC 7489 | Evaluated from DKIM and SPF; policy is recorded or enforced |
| ARC | [RFC 8617](https://www.rfc-editor.org/rfc/rfc8617) (Experimental) | Verified and recorded, never acted on |
| Results header | [RFC 8601](https://www.rfc-editor.org/rfc/rfc8601) | `Authentication-Results` stamped on each message |

The request signing of the ports is a different thing: [RFC 9421](https://www.rfc-editor.org/rfc/rfc9421). See
[Security](security.md). Decisions are in [ADR 0011](repo:docs/adr/0011-native-email-authentication.md).

## Inbound, and the memory rule

Only the header block is held in memory, bounded by `max_header_bytes`. The DKIM body hash is computed incrementally
as the body streams into the spool, so a verified message is never buffered whole.

## Behind Postfix or qmail

DKIM needs nothing but the message, so it works the same behind an MTA or at the edge. SPF and DMARC alignment need the
address of the original client, which an MTA that hands mail over LMTP or a pipe does not pass. Trunk evaluates them at
the SMTP edge, and behind an MTA only when a trusted upstream supplies the address. Otherwise they are recorded as not
evaluated, never as a pass. An `Authentication-Results` field from outside is stripped unless it comes from a trusted hop.

## Enforcement

`mailauth.dmarc` is `off`, `record` (default for 0.1) or `enforce`. `enforce` answers a message whose published DMARC
policy is `reject` with a permanent 5xx at the protocol edge.

## Outbound

The sender signs with DKIM (RSA-2048 and Ed25519) from owner-only key files. The body hash comes from a streaming pass
over the spooled file, and the signature is added at send time, so signing also never holds a whole message.
