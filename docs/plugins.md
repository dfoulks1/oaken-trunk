# Writing a plugin

Everything Oaken Trunk can be extended with is a plugin: a small class registered with a Python entry
point. Start from a base class, override what your plugin does, and run the contract suite. This is
the same model as Oaken Mail's plugins, so the habits carry over.

## The three kinds

| Kind | Entry-point group | Base class | What it does |
|---|---|---|---|
| Ingestor | `oaken_trunk.ingestors` | `BaseIngestor` | Speaks a protocol and hands core a byte stream and an envelope. |
| Spool | `oaken_trunk.spools` | `BaseSpool` | Stores messages and runs lease, ack and nack. |
| Sender | `oaken_trunk.senders` | `BaseSender` | Relays an outbound message to its destination. |

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

    async def store(self, message_id, chunks, envelope):
        async for chunk in chunks:           # bounded chunks, never the whole body
            await self.backend.append(message_id, chunk)
        await self.backend.commit(message_id)  # return only when durable

    async def lease(self, consumer, limit, seconds):
        return [Leased(m.id, m.token) for m in await self.backend.claim(consumer, limit, seconds)]

    def open(self, message_id):               # an async iterator of chunks
        return self.backend.read(message_id)

    async def ack(self, message_id, token):
        await self.backend.remove(message_id, token)
```

| You write | You gain |
|---|---|
| `store`, `lease`, `open`, `ack` | A working spool (all four are required) |
| `nack(id, token)` | Immediate return to the queue; without it a nack waits for lease expiry |
| `delete(id)` | Operator delete regardless of lease |
| `watch()` | Event-driven wake-up; without it the host polls |
| `usage()` | Quota enforcement and `status` totals |

## An ingestor in one screen

```python
from oaken_trunk.plugins.base import BaseIngestor

class MyIngestor(BaseIngestor):
    async def listen(self, sink):
        async for conn in self.accept():
            # sink.submit streams the body into the spool under core's limits and raises a
            # typed error (TooLarge, Overloaded, Rejected) you map to your protocol's reply.
            await sink.submit(conn.body_chunks(), conn.envelope)
```

Raise `oaken_trunk.core.errors.AuthError` when credentials are refused. Core records it and your
protocol replies with its auth failure; other ingestors carry on.

| You write | You gain |
|---|---|
| `listen(sink)` | A working ingestor (required) |
| `authenticate(ctx, credentials)` | `auth` capability |
| `tls_context()` | `tls` capability (STARTTLS or implicit) |

## A sender in one screen

A sender implements `send(envelope, chunks)` and returns a result: delivered, temporary failure
(retry with backoff) or permanent failure (bounce). Per-domain limits and retries belong to the host,
not the plugin.

## Testing a plugin

The shared contract suites live in `oaken_trunk.testing.contracts` (`SpoolContract`, `IngestorContract`,
`SenderContract`). Subclass one, point it at your plugin, and run `pytest`. The suites cover required
behaviour, lease expiry, crash recovery for spools, the streaming and memory rule, and the
backpressure replies. Tests never use the network, Docker, Redis or AWS: use fakes (`FakeSpool`,
`FakeIngestor`, `FakeSender`) and synthetic fixtures.

## Registering

```toml
[project.entry-points."oaken_trunk.spools"]
mine = "my_package:MySpool"
```
