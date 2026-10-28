# Directory store: the default, on local disk

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/PLUGIN.md`, `docs/architecture/spool.md`, ADR 0014.
**Depends on:** [CORE_store](CORE_store.md).
**Track:** `PLUGIN_`. Package `oaken_trunk_store_dir`, shipped in the core wheel. Core changes: none.
**Lift:** M
**Delivers:** `BaseStore` primitives on local disk: blobs as files, indexes as journals, strict/batched/volatile durability

## Goal

The default store for all three roles on one host. No dependencies, survives a crash at any step, and light
on inodes.

## Decided

- Primitives only (CORE_store). Fan-out, leases, acks and cleanup are core's.
- Blobs are files. An index is one append-only journal per name (one inode per device queue, not one per
  entry), replayed into memory at start and compacted by `checkup`. `cas` values are small files replaced by
  rename.
- One worker, one I/O thread. Across workers on one host, `cas` and journal appends take `flock`.
- A tmpfs mount is the operator's choice for this store, not another store.

## Not in scope

More than one host (PLUGIN_redis-spool, PLUGIN_s3-sqs-spool).

## Layout

```
store/tmp/<key>                 blob being written
store/blob/<key>                blob, raw bytes
store/cas/<key>                 small value
store/index/<name>.log          journal: add and remove records with scores
```

Names hold only ASCII ids and base32. Unknown names are ignored.

## Requirements

**A. Blobs and `cas`**

1. **Blobs.** `blob_put` writes `tmp/` with `O_EXCL`, mode 0600, directories 0700, fsyncs per durability and
   renames into `blob/`. `blob_open` streams bounded chunks. `blob_drop` unlinks and is idempotent.
2. **`cas`.** Read, compare, write `tmp/`, rename over, under `flock`. A TTL is stored with the value and
   checked on read.

`compact`

**B. Indexes and notify**

3. **Indexes.** `index_add` and `index_remove` append a record and fsync per durability; `index_range` reads
   the in-memory sorted view. Compaction rewrites a journal to its live members and renames it in.
4. **`watch`.** inotify on the journal through a small ctypes shim (no dependency), polling at
   `poll_interval_ms` otherwise. `notify = auto | inotify | poll`.
5. **Durability.** `strict`: fsync file and directory per operation. `batched`: one directory fsync per
   group. `volatile`: none. Windows has no directory fsync; the weaker guarantee is documented.
6. **Errors.** `ENOSPC` is `SpoolFull`, other `OSError`s `SpoolUnavailable`, per CORE_foundations.
7. **Suites.** `StoreContract`, the core spool suite over this store, and crash tests at named points
   (after a blob write, before and after each fsync and rename, mid-journal append, mid-compaction).

## Acceptance criteria

- At every crash point a blob is whole or absent, a journal replays to a consistent index, and a torn last
  record is ignored.
- A device queue of 10,000 entries uses one journal inode.
- `batched` makes one directory fsync per group, counted through an instrumented wrapper; `strict` makes N.
- Two workers on one host racing a `cas`: exactly one wins.
- Files are 0600 and directories 0700. Passes on Linux, macOS and Windows. Standard checks pass.

## Open questions (defaults in bold)

1. Compaction trigger? **At `checkup`, or when dead records exceed half the journal.**
2. inotify without a dependency? **Yes, a ctypes shim, with polling as the fallback.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
