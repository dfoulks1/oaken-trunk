# Enrollment: users add and remove their own devices

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CORE.md`, ADR 0010, ADR 0013.
**Depends on:** [CORE_http-listener](CORE_http-listener.md), [CORE_store](CORE_store.md).
**Lift:** M
**Delivers:** Self-service device registration over HTTP: an authenticated request for a token for device `IDENTIFIER`
**Track:** `CORE_`. Operations on a new `enroll` surface, behind the request guard. No new listener.

## Goal

A user gets a token for a new device without the operator: one authenticated request, one token back.

## Decided

- Operations `device_enroll(identifier)`, `device_list()` and `device_revoke(identifier)`, on the `enroll`
  surface, over the HTTP listener (`POST /v1/devices`, `GET /v1/devices`, `DELETE /v1/devices/{identifier}`).
- The caller is the recipient, proven by either an existing device's `toaken_` for that address, or a
  one-time enrollment code the operator issued (`steamer enroll-code --recipient ann@a.com`, single use,
  24 hours). A caller acts only on its own recipient.
- The new token is returned once and stored only as its hash (CORE_request-guard). The device is a consumer
  from that moment (ADR 0013).
- `identifier` is `[a-z0-9-]{1,32}`, unique per recipient.

## Not in scope

A web page for it (WEBUI_management-ui may add one). Account sign-up: a recipient exists when the operator
issues its first code.

## Requirements

1. **Operations.** As above, with typed inputs and outputs; `device_list` shows identifier, created, last
   used, queue depth, never a token.
2. **Auth.** HTTP Basic (address and `toaken_` or code) over TLS, through the `apptoken` authenticator, with its
   rate limits and lockout. A code is consumed on first success.
3. **Limits.** `max_devices` applies; over it is a clear refusal. Enrollments per recipient per day are rate
   limited.
4. **Revoke.** Ends the device's sessions and drops its queue. A device may revoke itself.
5. **Audit.** Every enroll, revoke and code use is audited, without the token.
6. **CLI.** `steamer device enroll --host H --address A --code C` (or `--token-stdin`) prints the new token.
7. **Docs.** `api-and-cli.md`, `consumers.md` (how a user adds a phone), softmap, status table.

## Acceptance criteria

- With a valid code, enroll returns a token that logs in to POP3; the same code fails a second time.
- With laptop's token, enroll "phone" works; laptop cannot enroll for another address.
- Revoking "phone" ends its session and empties its queue. A token sentinel never reaches a log.
- Standard checks pass. No network, Docker or real mail in tests.

## Open questions (defaults in bold)

1. Can a device enroll another device, or only a code? **Both. A lost-all-devices user asks the operator
   for a code.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
