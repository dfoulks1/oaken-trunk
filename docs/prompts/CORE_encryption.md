# Encryption at rest: every blob and record sealed before a store sees it

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CORE.md`, ADR 0003, ADR 0014, ADR 0015.
**Depends on:** [CORE_store](CORE_store.md).
**Lift:** M
**Delivers:** Streaming envelope encryption between the core spool and the stores, with key files, rotation and checks
**Track:** `CORE_`. Sits between CORE_store's spool and the primitives; no store changes.

## Goal

A store holds only ciphertext. A stolen disk, bucket or backup exposes nothing without the key file.

## Decided

- As ADR 0015: a data key per blob, AES-256-GCM in 64 KiB segments with counter and last-segment flag in the
  nonce, the data key wrapped by a key-encryption key named in the header.
- Registry values and meta are sealed the same way, as single segments.
- `cryptography` is the only new dependency. No hand-written primitives.

## Not in scope

A KMS key provider (a later plugin kind). Encrypting logs (they carry no content, ADR 0012).

## Requirements

**A. Seal and open**

1. **Format.** Header: magic, version, key id, wrapped data key, nonce prefix. Then sealed segments. The
   header is authenticated as associated data of every segment.
2. **Streams.** `seal(chunks)` and `open(chunks)` as async iterators, one segment in memory at a time.
3. **Placement.** The core spool seals before `blob_put` and opens after `blob_open`; meta and registry
   values through the same layer. Stores see ciphertext only.

`compact`

**B. Keys**

4. **Key file.** `init` writes `<config>/secrets/kek-<id>`, mode 0600, from the OS random source. Also
   `OAKEN_TRUNK_KEK_<id>` from the environment. `doctor` refuses a group- or world-readable key file.
5. **Rotation.** `steamer keys rotate-kek` adds a key and makes it current. `checkup` rewraps data keys under
   the current key; a key no blob names can be retired.
6. **Errors.** A missing key, a bad tag or a truncated stream is `SpoolUnavailable` for that message, never
   plaintext, never partial output. Logged by id only.
7. **Docs.** `security.md` (what is encrypted, where the key lives, back it up apart from the store),
   `config.example.toml` (`[encryption]`), softmap, status table.

## Acceptance criteria

- A plaintext sentinel never appears in any store file, object or key after commit.
- Flipping a byte, dropping a segment, swapping two segments or cutting the stream makes open fail with no
  output.
- A 1 GiB body seals and opens with flat memory.
- After rotation and `checkup`, every header names the new key; the old key can be removed and every message
  still opens.
- Standard checks pass. No network, Docker or real mail in tests.

## Open questions (defaults in bold)

1. Data-key wrap? **AES-KW (RFC 3394) via `cryptography`.**
2. Encrypt the audit file? **No. It holds no content; it stays readable on the host.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
