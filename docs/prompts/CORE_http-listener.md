# HTTP listener: the network door

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CORE.md`, `docs/architecture/security.md`,
`docs/architecture/ingestion.md`, ADR 0010.
**Depends on:** [CORE_daemon](CORE_daemon.md), [CORE_request-guard](CORE_request-guard.md).
**Delivers:** The TCP and TLS listener with the request guard in front, and HTTP submission on the ingest surface
**Track:** `CORE_`. Replaces the old HTTP ingest plugin: there is no separate ingestor.

## Goal

Serve the daemon's routes over TCP behind the guard, so remote clients (ingesters, consumers, the UI) can
reach core safely.

## Decided

- One HTTP listener, `[server] host` and `port`. Surfaces come from the key and the operation, not the path.
- Every request passes CORE_request-guard before any route runs.
- HTTP ingest is `submit` on the `ingest` surface: `POST /v1/ops/submit`, raw message as the body. There is no
  `/v1/send` route.
- Loopback by default.

## Not in scope

The guard and authenticators (CORE_request-guard). The operations. mTLS. The MCP and UI listeners.

## Requirements

**A. Listener and guard**

1. **Listener.** TCP from `[server] host` and `port`, serving the same app as the socket.
2. **Guard wiring.** The guard sees every request first. This builds its request view (method, target,
   headers, peer, TLS) and feeds the body through its incremental digest. A mismatch cancels the stream and
   aborts the writer.
3. **Binding.** Loopback by default. A non-loopback bind needs TLS and a signed scheme, or startup fails. A
   `bearer` surface on a non-loopback bind is refused.
4. **TLS.** Certificate and key from files, never config values. TLS 1.2 or later. Reloadable without a restart.

`compact`

**B. Submission over HTTP**

5. **Envelope.** Mail from and recipients arrive as headers named in `api-and-cli.md`. The client IP is the
   socket peer, never a header, unless a trusted proxy is configured.
6. **Surface.** A key for another surface is refused before the route.
7. **Backpressure.** 503 with `Retry-After` for the inflight limit, 413 too large, 507 spool full, per the
   error table.

`compact`

**C. Close**

8. **Docs.** `ingestion.md` (the HTTP row), `security.md`, a worked example of a signed `submit`, softmap,
   status table.

## Acceptance criteria

- An unsigned request is refused before any route. A key for the `consume` surface cannot `submit`.
- A body changed after signing aborts the writer and nothing is committed.
- A non-loopback bind without TLS fails startup. `bearer` on a non-loopback bind is refused.
- A client that stalls is dropped at the daemon's timeouts. The client IP in a header is ignored.
- Reloading the certificate does not drop an in-flight request. Standard checks pass.

## Open questions (defaults in bold)

1. A `/v1/send` alias for `submit`? **No. One route per operation.**
2. Trusted-proxy header for the client IP? **Off. Opt in per proxy address.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
