# Directory spool: the default spool

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/PLUGIN.md`, `docs/architecture/spool.md`.

**Depends on:** [CORE_plugin-host](CORE_plugin-host.md).
**Track:** `PLUGIN_`. Package `oaken_trunk_spool_dir`, shipped in the core wheel. Core changes: none.
**Lift:** L
**Delivers:** Default spool: Maildir-style store, lease by rename, strict/batched/volatile durability

## Goal

The default spool. Maildir-style, no dependencies, survives a crash at any step.

## Decided

- The author-facing methods are `write`, `commit`, `abort`, `lease`, `open`, `ack` (CORE_plugin-host). Optional: `nack`,
  `delete`, `watch`, `usage`.
- One worker, one I/O thread. A message is visible only after `commit`.
- One body, one delivery per recipient: each is a hard link to the body. The envelope (one recipient) and the
  annotations live in `meta/<id>-<n>.json`, which never moves.
- A tmpfs mount is the operator's choice for this driver, not another driver.

## Not in scope

Cross-process quota and shared counters (CORE_supervisor). Redis and S3 (PLUGIN_redis-spool, PLUGIN_s3-sqs-spool). Reading annotations to stamp headers (CORE_mail-authentication).

## Layout

```
spool/tmp/<id>.msg                           body being written
spool/new/<id>-<n>.msg                       ready: a hard link to the body, one per recipient
spool/leased/<id>-<n>.<expiry>.<token>.msg   leased; the name carries the lease
spool/meta/<id>-<n>.json                     envelope and annotations for that delivery
```

A body file is the raw bytes only. Names hold only ASCII ids,
integer expiry seconds and base32 tokens. Unknown names are ignored.

## Requirements

**A. Write and commit**

1. **`write`/`abort`.** Create `tmp/<id>.msg` with `O_EXCL`, mode 0600, in a directory of mode 0700. `write`
   appends. `abort` removes the file.
2. **`commit(annotations)`.** Write `meta/<id>-<n>.json` for every recipient (each records `of: N`), fsync
   the body, hard-link it into `new/` once per recipient, unlink `tmp/`, fsync the directory, per the
   durability mode. A delivery is visible at its link. Recovery rolls a half-done commit forward when all N
   meta files exist, and back otherwise.

`compact`

**B. Lease, ack, nack, delete, recovery**

3. **`lease`.** Atomic rename `new/` to `leased/` with expiry and a random token. Two consumers never get the
   same file. Oldest id first, from an in-memory index of `new/` built at start.
4. **`open`.** Stream the body in bounded chunks. Return the envelope and annotations from `meta/`.
5. **`ack` and `nack`.** Ack unlinks that delivery's link and its meta file. The body goes with the last link. Nack renames back to `new/`. A wrong or
   expired token is refused.
6. **`delete`.** Remove regardless of lease.
7. **Recovery** at start, and callable by the reaper (CORE_audit-and-jobs): delete stale `tmp/`, return expired leases to
   `new/`, delete meta files with no delivery, finish or undo a half-done commit. Idempotent.

`compact`

**C. Durability and quota**

8. **Durability.** `strict`: fsync file and directory per message. `batched`: fsync each file, then one
   directory fsync for the group (not N). `volatile`: none. Windows has no directory fsync, so there
   `strict` is a file fsync and the weaker guarantee is documented.
9. **Quota.** `usage()` counts each delivery at the body size (a safe overcount with links), from an in-memory count built by a scan at start, updated on commit, ack and
   delete, with a periodic rescan to correct drift. Over `max_spool_bytes` gives `SpoolFull`.
10. **Disk errors.** `ENOSPC` is `SpoolFull`. Other `OSError`s are `SpoolUnavailable`. Both map through the
    table of CORE_foundations.

`compact`

**D. Notify and proof**

11. **`watch`.** Polling at `poll_interval_ms`, plus inotify on Linux through a small ctypes shim (no
    dependency). `notify = auto | inotify | poll`.
12. **Suites.** `SpoolContract` plus crash tests at named points (after `write`, before and after each
    fsync, after the rename, after the directory fsync, during lease, during ack) using a fault hook.

## Acceptance criteria

- At every crash point recovery gives the message committed or nothing. Never a partial file, never two
  copies, never a visible delivery without its meta file.
- Two concurrent consumers never lease the same message. A message is not leasable before `commit`.
- A batch of N commits in `batched` makes one directory fsync, counted through an instrumented wrapper. The
  same N in `strict` make N.
- Three recipients share one body (link count 3), and each leases and acks on its own. The body is gone after the last ack.
- Annotations survive lease, nack and a restart, and are gone after `ack`. An orphan meta file is removed.
- A full disk returns the retryable error with all three codes. Files are 0600 and directories 0700.
- An unknown file in `new/` is ignored. A 1 GiB message streams with chunks of at most 64 KiB.
- Passes on Linux, macOS and Windows (directory fsync skipped on Windows, with a reason). Standard checks pass.

## Open questions (defaults in bold)

1. Meta layout? **`meta/<id>-<n>.json`, as above.**
2. What does `batched` save? **The directory fsync only. File fsyncs cannot overlap with one thread.**
3. Batch window? **None. Commits that arrive while an fsync runs join the next group.**
4. inotify without a dependency? **Yes, a ctypes shim, with polling as the fallback.**
5. Cross-process `watch` in 0.1? **Implemented, tested properly in 10.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
