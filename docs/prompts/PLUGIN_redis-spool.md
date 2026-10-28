# Redis store: queues and coordination across hosts

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/PLUGIN.md`, ADR 0014, `PLUGIN_directory-spool.md` (its status block).
**Depends on:** [PLUGIN_directory-spool](PLUGIN_directory-spool.md).
**Lift:** M
**Delivers:** `BaseStore` primitives on Redis, with atomic overrides for the hot spool operations
**Track:** `PLUGIN_`. Package `oaken_trunk_store_redis`, a separate workspace package. Core changes: none.

## Goal

The store for the `queues` and `coordination` roles when Trunk runs on more than one host. It can hold
bodies too, for small mail.

## Requirements

1. **Primitives.** Blobs as `blob:<key>:<n>` chunks of at most 64 KiB, never one large value. `cas` as a
   Lua compare-and-set with `PX` for the TTL. Indexes as sorted sets. `watch` through keyspace notifications,
   polling otherwise.
2. **Overrides.** `ack` and `commit` as single Lua scripts (entry, lease and holder count in one step), passing
   the same core spool suite.
3. **Limits.** `doctor` warns when the store holds bodies and `max_message_size` exceeds a configured
   `max_blob_bytes`, since bodies sit in memory.
4. **Ops.** AOF and persistence guidance in the docs. Credentials from the environment or a file, never config.
5. **Suites.** `StoreContract` and the core spool suite against a fake or in-process server; tests never use a
   real Redis.

## Acceptance criteria

- Contract and spool suites pass. A concurrent ack race leaves no orphan body.
- Standard checks pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
