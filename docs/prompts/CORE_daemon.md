# Daemon: start, stop and the local socket

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CORE.md`, `docs/architecture/api-and-cli.md`,
`docs/architecture/process-model.md`.
**Depends on:** [CORE_operation-registry](CORE_operation-registry.md).
**Lift:** L
**Delivers:** The daemon: composition root, lifecycle, and the registry served over a local Unix socket
**Track:** `CORE_`. Model: oaken-mail's `oaken/daemon/` and `oaken/api/`.

## Goal

Run core as one process that serves the registry over a local socket and stops without losing a message.
No network listener yet.

## Decided

- One worker, one I/O thread (the defaults in CORE_supervisor). Starlette and uvicorn are core dependencies.
- Local only. A Unix socket gated by a built-in peer-credential check. TCP, TLS and the guard are
  CORE_http-listener.
- Routes are generated from the registry. No hand-written per-operation route.
- `steamer start` runs the daemon. `oaken-trunk.service` runs `steamer start`.
- A daemon with no spool and no plugins still starts. `status` says `not configured`.

## Not in scope

TCP, TLS, the guard and authenticators (CORE_http-listener, CORE_request-guard). The operations
(CORE_system-operations, CORE_audit-and-jobs, CORE_consumer-api). Plugin loading (CORE_plugin-host extends
the composition root). Multiple workers (CORE_supervisor). The UI.

## Requirements

**A. Start, reload, stop**

1. **Composition root.** Settings, plugins, spool, engine, registry, API, in that order. A step with nothing
   to load yet is a no-op. Any failure stops with a readable error and starts nothing.
2. **Lifecycle.** Implements the registry's `Lifecycle`. `start` runs in the foreground. `reload` re-reads the
   keys marked reloadable and rebuilds the registry in one step, and in-flight requests finish on the old
   one. systemd `Type=notify` through `NOTIFY_SOCKET`. A runtime file `<run>/runtime.json` (pid, socket,
   version), mode 0600. A stale one is replaced.
3. **Graceful stop.** On SIGTERM or `stop`: stop accepting, `/v1/health` says not ok, drain in-flight work
   within a timeout, abort writers that cannot finish, exit. Nothing partial is visible.

`compact`

**B. The socket**

4. **Routes.** `POST /v1/ops/{name}` (JSON body is the input; a streaming operation takes its fields in
   headers and the body as the stream), `GET /v1/ops`, `GET /v1/openapi.json`.
5. **Unix socket.** `<run>/trunk.sock`, mode 0600. A built-in peer check against a uid allow-list (default:
   the daemon's uid and root). Caller class `local`. Windows: loopback with an owner-only key, same gate.
6. **Backpressure.** The engine slot is taken before the first body chunk. Core errors map to HTTP codes
   through the table in CORE_foundations, with `Retry-After`.
7. **Timeouts.** Header read 10 seconds, body idle 30 seconds, both configurable, plus a header size cap. The
   whole request is bounded by `max_message_size`, not a clock.
8. **Error bodies and health.** A code, a message, a correlation id, no trace, no content. `GET /v1/health`
   returns ok or not ok and nothing else.

`compact`

**C. Platforms and close**

9. **Windows.** No SIGHUP, `sd_notify` or peer credentials. `reload` and `stop` are operations everywhere, and
   signals are a Unix convenience.
10. **Docs.** An `oaken-trunk.service` unit, the runtime layout, `api-and-cli.md`, softmap, status table.

## Acceptance criteria

- SIGTERM during an ingest leaves a committed message or nothing. `/v1/health` is not ok while draining.
- Reload with a request in flight finishes that request on the old registry.
- `GET /v1/ops` lists exactly the registry. `/v1/openapi.json` validates.
- A different uid on the socket is refused (skipped on Windows, with a reason). A stale runtime file is replaced.
- With no spool configured the daemon starts, `status` says `not configured`, and `submit` returns the
  retryable spool-unavailable error.
- A client that stalls on headers is dropped at 10 seconds, and one idle in the body at 30.
- A body sentinel never appears in any log or error body. Standard checks pass.

## Open questions (defaults in bold)

1. Is `/v1/health` open on the socket? **Yes, ok or not ok only.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
