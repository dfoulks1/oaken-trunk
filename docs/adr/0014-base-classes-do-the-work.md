# 14. Base classes do the work: stores and line servers

- Status: proposed
- Date: 2026-10-28

## Context

ADR 0006 gives every plugin kind a base class. In the plan that followed, each spool still implemented
lease, ack, fan-out and cleanup on its own, and each socket plugin (LMTP, SMTP, POP3, the SASL bridge) still
handled TLS, line limits, timeouts and login on its own. Three spools and four protocol plugins would carry the
same logic, tested separately, drifting separately. Efficiency and efficacy are the goal: the least code per
plugin, and the hard parts written and proven once.

## Decision

- **Stores, not spools.** A storage backend extends `BaseStore` and implements a handful of primitives:
  stream a blob in and out and drop it; compare-and-set on a small key; add, remove and range over an ordered
  index; and optionally watch. The spool kind becomes the store kind (`oaken_trunk.stores`).
- **Core builds the rest on those primitives:** the spool (fan-out per device at commit, lease, ack, nack,
  renew, body cleanup), `Locks`, `Credits` and `NonceStore`, the device registry and last-used, the caps and
  the `checkup` steps. One implementation, one contract suite.
- **Roles by config.** `[store] bodies`, `queues` and `coordination` each name a store. A hybrid (bodies in S3,
  queues and locks in Redis) is configuration, not another plugin.
- **Overrides stay legal.** A store may override any higher-level operation for speed (Redis acks in one Lua
  script) if it passes the same contract suite. Capabilities still come from what a plugin overrides (ADR 0006).
- **One line server.** `BaseLineServer` owns TLS and STARTTLS, no auth before TLS, bounded lines, timeouts,
  connection caps, dot-stuffing as streams, login through the authenticator chain, and a fuzz harness.
  `BaseIngestor` (LMTP, SMTP) and `BaseRetriever` (POP3) extend it, and so does the SASL bridge. A retriever's
  session is a transaction the base runs: take the device lock, list, claim on read, ack on commit, nack on
  teardown. A protocol plugin maps its command words and nothing else.

## Consequences

The three store plugins and four protocol plugins shrink to their primitives and parsers. The contract suites
move to the bases, so a new backend or protocol proves only what it adds. The base classes are larger and
are stable surface (ADR 0006): changing a primitive needs an ADR. A store with a slow primitive (compare-and-set
on S3) is correct but slow until it overrides; `doctor` names the role it is serving.
