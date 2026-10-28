# S3 store: bodies (and queues) in object storage, SQS as an optional signal

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/PLUGIN.md`, ADR 0014, `PLUGIN_directory-spool.md` (its status block).
**Depends on:** [PLUGIN_directory-spool](PLUGIN_directory-spool.md).
**Lift:** M
**Delivers:** `BaseStore` primitives on S3, with one optional SQS queue to wake consumers
**Track:** `PLUGIN_`. Package `oaken_trunk_store_s3`, a separate workspace package. Core changes: none.

## Goal

The store for the `bodies` role at scale, and for `queues` when Redis is not wanted. AWS lock-in is the
operator's choice: anything S3-compatible (MinIO, Ceph, R2) is the open path.

## Requirements

1. **Blobs.** One object per key, multipart upload from the chunk stream, ranged reads out.
2. **Indexes.** One object per member under `index/<name>/<score>-<member>`; `index_range` lists the prefix.
   POP3 listing is a prefix listing. S3 expires nothing unless told to, so mail never ages out.
3. **`cas`.** Conditional writes (`If-None-Match: *` to create, `If-Match` on the ETag to replace; the loser
   gets 412, a racing delete 409, which is retried). Correct but slow: `doctor` says so
   when S3 serves `coordination`, and recommends Redis.
4. **`watch`.** Optional: one SQS queue for the store, fed on `index_add`, long-polled. Not per device.
5. **Ops.** Credentials from the environment or instance role, never config. A lifecycle rule template as a
   backstop for orphan blobs older than `checkup` could miss.
6. **Suites.** `StoreContract` and the core spool suite against a fake; tests never use AWS.

## Acceptance criteria

- Contract and spool suites pass against the fake, including a racing `cas`.
- Standard checks pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Open questions (defaults in bold)

1. Verify S3 conditional-write support and its consistency, and name the S3-compatible stores that support
   it. **Refuse `coordination` on one that does not.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
