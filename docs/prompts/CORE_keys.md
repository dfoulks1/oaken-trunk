# Keys and tokens: who holds which credential, kept in the registry

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CORE.md`, `docs/architecture/security.md`, ADR 0010, ADR 0013, `CORE_request-guard.md` (its status block).
**Depends on:** [CORE_request-guard](CORE_request-guard.md), [CORE_store](CORE_store.md).
**Lift:** M
**Delivers:** `apptoken` and `bearer` authenticators, and key operations in the registry, live on every host
**Track:** `CORE_`. Schemes ship in `oaken_trunk_auth` as authenticator plugins, registered as a third party's would be.

## Goal

Every credential (signing keys, device tokens) is issued, listed and revoked through operations, stored in
the registry, and takes effect on every host without a restart.

## Decided

- Keys and token hashes live in the registry (CORE_store), never in `<config>` files.
- `apptoken`: a per-device token `toaken_<key id>_<secret>`. The key id finds the record, the secret is
  checked; the prefix lets secret scanners spot a leak. Stored as `hashlib.scrypt`. Used by protocol logins
  (POP3, the Dovecot-auth bridge) and by HTTP Basic on the `enroll` surface (ADR 0013).
- `bearer`: off unless enabled, loopback only, refused elsewhere, `doctor` warns.
- Rotation is overlap: add the new key, then revoke the old. No expiry field yet.

## Not in scope

The guard and ed25519 (CORE_request-guard). Self-service enrollment (CORE_enrollment). `hmac` (later).

## Requirements

**A. Schemes**

1. **`apptoken`.** Constant-time verify. Rate limited per address and per username; locked out after
   `max_failures` (default 10) for `lockout_seconds`, counted through `Locks` so every worker and host agrees.
   One generic failure for every reason. The username must be in the key's recipient scope.
2. **`bearer`.** As decided. `AuthenticatorContract` for both.

`compact`

**B. Key operations**

3. **`keys_add`, `keys_list`, `keys_revoke`** per surface. `--recipients` for a `consume` key (required);
   `--device NAME` for an `apptoken`, printed once. An ed25519 private key is written once to `--out`, mode
   0600 from the first byte; the registry keeps only the public key.
4. **Revoke.** Ends the device's sessions on every host and drops its queue. Takes effect without a restart.
5. **Never logged:** tokens, keys, secrets, even on failure.
6. **Docs.** `security.md` (schemes, rotation, revoke), `api-and-cli.md`, softmap, status table.

## Acceptance criteria

- `keys_add --surface consume` with no `--recipients` is refused. A new token logs in; after revoke it fails
  on a second worker without a restart.
- Ten wrong tokens lock the username; the eleventh correct one is refused until the lockout ends.
- `bearer` on a non-loopback bind is refused.
- A token sentinel never appears in any log, error or audit record. Standard checks pass.

## Open questions (defaults in bold)

1. Lockout default? **10 failures, 15 minutes.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
