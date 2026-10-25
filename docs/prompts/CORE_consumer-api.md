# Consumer API: lease, fetch, ack

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CORE.md`, `docs/architecture/spool.md`, ADR 0004.
**Depends on:** [PLUGIN_directory-spool](PLUGIN_directory-spool.md).
**Lift:** M
**Delivers:** The consumer operations, the lease rules and wake-up
**Track:** `CORE_`.

## Goal

How a consumer takes mail out. At-least-once, never buffered, same operations on the CLI and HTTP.

## Decided

- Six operations plus `renew`. Surface `consume`, set by the key, never by the caller.
- A consumer is named by its key id. Leases belong to that name.
- Bodies stream out in bounded chunks. Core never holds a whole message.
- Expired leases return to the queue. Consumers dedupe on the message id (ADR 0004).
- `delete` is audited. Lease, ack and nack are counted in stats, not audited.

## Not in scope

Push to a webhook (a consumer does that). Priorities and routing. The guard (CORE_request-guard).

## Requirements

**A. Operations**

1. **`lease`.** `limit` (default 10, max 100) and `seconds` (default 60, max 3600). Returns ids and tokens. No
   mail returns an empty list, not an error.
2. **`fetch`.** Streams a leased message with its envelope and annotations. A wrong or expired token is
   `lease_invalid`.
3. **`ack` and `nack`.** A wrong or expired token is `lease_invalid`. A repeat ack of a message already gone
   succeeds quietly. `nack` returns it to the queue at once.
4. **`renew`.** Extends a live lease up to `max_lease_total` (default 1 hour). Never an expired one.
5. **`list` and `delete`.** `list` shows id, size, age, state (`ready` or `leased`) and never content. `delete`
   removes regardless of lease and is audited.

`compact`

**B. Wake-up and limits**

6. **Wake-up.** Long-poll on `lease` (`wait` seconds, default 0, max 30), backed by the spool's `watch()`. SSE
   is later. A wake with nothing to take is harmless.
7. **Poison.** A message nacked or expired `max_attempts` times (default 10) moves to a dead state and shows
   in `list`. It is not delivered again until an operator releases it.
8. **Limits.** Per-consumer open leases (default 1000). Over it is a retryable error.
9. **Docs.** An example consumer (CLI loop and a webhook relay), `api-and-cli.md`, softmap, status table. The
   Oaken Mail provider is built in the oaken-mail repo.

## Acceptance criteria

- A fake consumer leases, crashes, and the message returns after expiry with the same id.
- Two consumers never get the same message. Ack of an expired lease is `lease_invalid`.
- A message that fails `max_attempts` times is dead and not leased again.
- A 1 GB body fetches with flat memory. A body sentinel never reaches a log or error.
- `lease` with `wait` returns within a second of a commit.
- Standard checks pass. No network, Docker or real mail in tests.

## Open questions (defaults in bold)

1. Does `fetch` return annotations with the body? **Yes, as headers before the stream.**
2. Is a dead message kept forever? **Until an operator deletes or releases it.**
3. Can one key consume many names? **No, one key is one consumer.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
