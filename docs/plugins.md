+++
title = "Writing a plugin"
subtitle = "Ingestors, spools and senders"
lead = "Everything Trunk can be extended with is a plugin: a small class registered with an entry point. Start from a base class and run the contract suite."
badges = [["text-bg-warning", "Pre-alpha"]]
description = "How to write an ingestor, spool or sender."
group = "concepts"
order = 70
+++

Everything Oaken Trunk can be extended with is a plugin: a small class registered with a Python entry
point. Start from a base class, override what your plugin does, and run the contract suite. This is
the same model as Oaken Mail's plugins, so the habits carry over.

## The seven kinds, and the plain plugin

| Kind | Entry-point group | Base class | What it does |
|---|---|---|---|
| Ingestor | `oaken_trunk.ingestors` | `BaseIngestor` | Speaks a protocol and hands core a byte stream and an envelope. |
| Retriever | `oaken_trunk.retrievers` | `BaseRetriever` | Speaks a read protocol (POP3) and maps it onto list, lease, fetch and ack. Holds no store. |
| Spool | `oaken_trunk.spools` | `BaseSpool` | Stores messages and runs lease, ack and nack. |
| Sender | `oaken_trunk.senders` | `BaseSender` | Relays an outbound message to its destination. |
| Authenticator | `oaken_trunk.authenticators` | `BaseAuthenticator` | Verifies a request or connection: signed requests, SMTP AUTH, mTLS. Core owns freshness, replay and the default deny. |
| MTA | `oaken_trunk.mtas` | `BaseMTA` | Declares how an MTA hands over mail: env names, arguments, exit codes. The base supplies `steamer NAME submit`. |
| Listener | `oaken_trunk.listeners` | `BaseListener` | Watches the `envelope`, `headers`, `end` and `stored` events. Sees headers and digests only, annotates, never removes a core protection. |

Every base class extends `BasePlugin`, which gives the context, lifecycle, health, `@command` and
`ctx.ops` (the operations the plugin declared in `calls`). A plugin that fits no kind, such as an
autoscaler, extends `BasePlugin` directly and registers in `oaken_trunk.plugins`. It has no kind-specific
role, so its only power is the commands it exposes and the operations it declared.

Import them from `oaken_trunk.plugins.base`, or from `oaken_trunk.plugins`, which re-exports them.

First-party plugins (`oaken_trunk_*`) register exactly as a third party's would. The exact signatures
are on the generated plugin contracts page.

## What every base class gives you

- `self.ctx`: your settings (the `[ingest.<name>]`, `[spool.<name>]` or `[sender.<name>]` table of
  `config.toml`), a logger, the clock, the worker's thread pool, and the global limits. Secrets come
  from the environment or files, never from config.
- `start()` and `stop()` lifecycle hooks, called by the host, with health reported to `doctor`.
- **Capabilities inferred from what you wrote**, so there is no second list to keep in step.
- Lenient return types: a dict, tuple or plain value is coerced to the strict contract type, and a
  mistake produces a readable message such as `spool 'mine': lease() returned 3 ids for limit 2`.
- Isolation: an error fails that one message or operation and is logged. It never stops core.

## Commands

Mark a method with `@command` and it becomes the operation `plugin.verb`, with typed input and output,
a permission (`read` or `mutate`) and an mcp setting (`off` or `never`). The CLI, HTTP API, web UI and
MCP all take it from the registry. An unmarked method is unreachable, and a plugin cannot take a core
name. The decorator limits what a plugin exposes, not what its code can do.

Plugins run in-process and are not sandboxed in v1. Core never imports a plugin, and a plugin never
touches core's counters or another plugin's storage; it returns data and receives streams.

## Memory rule for plugin authors

Never read a whole message into memory. Bodies arrive and leave as async iterators of bounded
chunks. A plugin that buffers a message breaks the gateway's memory guarantee and fails the contract
suite's streaming test.

## A spool in one screen

```python
from oaken_trunk.plugins.base import BaseSpool
from oaken_trunk.plugins.contracts import Leased

class MySpool(BaseSpool):
    version = "0.1"

    async def write(self, message_id, chunk, envelope):   # one bounded chunk, never the whole body
        await self.backend.append(message_id, chunk)

    async def commit(self, message_id, annotations):      # visible from here; return only when durable
        await self.backend.commit(message_id, annotations)

    async def abort(self, message_id):                    # an error or a drop: remove the partial data
        await self.backend.discard(message_id)

    async def lease(self, consumer, limit, seconds):
        return [Leased(m.id, m.token) for m in await self.backend.claim(consumer, limit, seconds)]

    def open(self, message_id):               # an async iterator of chunks
        return self.backend.read(message_id)

    async def ack(self, message_id, token):
        await self.backend.remove(message_id, token)
```

| You write | You gain |
|---|---|
| `write`, `commit`, `abort`, `lease`, `open`, `ack` | A working spool (all six are required). The base class presents `write`, `commit` and `abort` to core as the `writer` of the spool contract |
| `nack(id, token)` | Immediate return to the queue; without it a nack waits for lease expiry |
| `delete(id)` | Operator delete regardless of lease |
| `watch()` | Event-driven wake-up; without it the host polls |
| `usage()` | Quota enforcement and `status` totals |

## An ingestor in one screen

```python
from oaken_trunk.plugins.base import BaseIngestor

class MyIngestor(BaseIngestor):
    async def listen(self, submit):
        async for conn in self.accept():
            # submit streams the body into the spool under core's limits and raises a
            # typed error (TooLarge, Overloaded, Rejected) you map to your protocol's reply.
            await submit(conn.body_chunks(), conn.envelope)
```

Raise `oaken_trunk.core.errors.AuthError` when credentials are refused. Core records it and your
protocol replies with its auth failure; other ingestors carry on.

| You write | You gain |
|---|---|
| `listen(submit)` | A working ingestor (required) |
| `authenticate(ctx, credentials)` | `auth` capability |
| `tls_context()` | `tls` capability (STARTTLS or implicit) |

## A sender in one screen

A sender implements `send(envelope, chunks)` and returns a result: delivered, temporary failure
(retry with backoff) or permanent failure (bounce). Per-domain limits and retries belong to the host,
not the plugin.

## An authenticator in one screen

```python
from oaken_trunk.plugins.base import BaseAuthenticator

class MyAuthenticator(BaseAuthenticator):
    async def verify(self, request):
        # request is a read-only view: method, path, query, headers, body digest, peer.
        # Return a Principal (key id and surface) or raise AuthError. Never read the body here.
        key = self.keys.get(request.key_id)
        if key is None or not key.verify(request.signature_base, request.signature):
            raise AuthError("bad signature")
        return Principal(key_id=request.key_id, surface=self.surface)
```

| You write | You gain |
|---|---|
| `verify(request)` | A working authenticator (required) |
| `add_key`, `revoke_key`, `list_keys` | Key management through `steamer keys` |
| `challenge()` | A protocol-level challenge (SMTP AUTH, for example) |

The guard runs it before any route, enforces freshness and replay protection around it, and fails closed on
any error. See [Security](architecture/security.md) and ADR 0010.

## A listener in one screen

```python
from oaken_trunk.plugins.base import BaseListener

class MyListener(BaseListener):
    adds_headers = ["X-My-Check"]          # declared up front; anything else is refused

    async def on_headers(self, event):     # inline and time-bounded; may record a result
        return self.annotate("my-check", "pass")
```

`stored` fires after the message is durable and cannot delay acceptance. Mail authentication (DKIM,
SPF, DMARC, ARC) will ship as a listener bundle.

## Testing a plugin

The shared contract suites live in `oaken_trunk.testing.contracts` (`SpoolContract`, `IngestorContract`,
`SenderContract`, `AuthenticatorContract`, `ListenerContract`). Subclass one, point it at your plugin, and run `pytest`. The suites cover required
behaviour, lease expiry, crash recovery for spools, the streaming and memory rule, and the
backpressure replies. Tests never use the network, Docker, Redis or AWS: use fakes (`FakeSpool`,
`FakeIngestor`, `FakeSender`) and synthetic fixtures.

## Registering

```toml
[project.entry-points."oaken_trunk.spools"]
mine = "my_package:MySpool"
```
