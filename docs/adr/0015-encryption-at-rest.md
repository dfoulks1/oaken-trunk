# 15. Mail is encrypted at rest, in core, above every store

- Status: proposed
- Date: 2026-10-28

## Context

Trunk holds other people's mail until their devices take it. A stolen disk, a leaked bucket or a backup
should not expose it. Stores are plugins (ADR 0014), so encryption left to each store would be written three
times and missed once.

## Decision

- **Core encrypts before a store sees anything.** Bodies, meta and registry values reach every store as
  ciphertext. A store cannot opt out and needs no crypto of its own.
- **Envelope encryption per blob.** Each blob has a random 256-bit data key. The body is sealed with a
  streaming AEAD: AES-256-GCM over 64 KiB segments, each nonce a random prefix plus a segment counter plus a
  last-segment flag, so a reordered, dropped or truncated segment fails to open. The header holds a format
  version, the key-encryption key's id and the wrapped data key. Memory stays flat (ADR 0003).
- **Key-encryption keys** come from a file (default, written by `init`, mode 0600), the environment, or a
  key-provider plugin later (a KMS). Rotation adds a new key id; `checkup` rewraps data keys, never bodies. An
  old key is kept until no blob names it.
- **Dropping a blob's data key makes it unreadable**, so a missed orphan or a backup copy holds nothing.
- One dependency, `cryptography` (Apache-2.0 or BSD), for AES-GCM and key wrap. No hand-written crypto.

## Consequences

Losing the key-encryption key loses the mail: `doctor` says where it is and that it must be backed up apart
from the store. Encryption costs CPU per byte, paid once in and once out. A store-native encryption setting
(S3 SSE, an encrypted volume) is defence in depth, not a substitute.
