# SPDX-License-Identifier: Apache-2.0
"""Test doubles for the core contracts. Memory only, tests only."""

from __future__ import annotations

import asyncio
import secrets
import time
from collections.abc import AsyncIterator, Iterable
from contextlib import asynccontextmanager
from dataclasses import dataclass

from oaken_trunk.envelope import Envelope
from oaken_trunk.errors import TrunkError
from oaken_trunk.events import Annotations, ListenerEvent, StoredEvent
from oaken_trunk.ids import delivery_id
from oaken_trunk.ingest import Submit
from oaken_trunk.spool import Lease, Opened, StoreAborted, Usage
from oaken_trunk.testing.messages import chunks


async def _stream(body: bytes) -> AsyncIterator[bytes]:
    for chunk in chunks(body):
        yield chunk


@dataclass
class _Delivery:
    message_id: str
    envelope: Envelope
    queue: str
    token: str | None = None
    expires: float = 0.0


class _FakeWriter:
    def __init__(self, spool: FakeSpool, message_id: str, envelope: Envelope) -> None:
        self._spool, self._id, self._envelope = spool, message_id, envelope
        self._parts: list[bytes] = []
        self.done = False

    async def write(self, chunk: bytes) -> None:
        if self.done:
            raise RuntimeError("writer is closed")
        self._parts.append(chunk)

    async def commit(self, annotations: Annotations) -> tuple[str, ...]:
        if self.done:
            raise RuntimeError("writer is closed")
        self.done = True
        return self._spool._commit(self._id, self._envelope, b"".join(self._parts), annotations)


class FakeSpool:
    """The spool contract in memory. One queue per recipient (no registry yet): lease by address."""

    def __init__(self) -> None:
        self.bodies: dict[str, bytes] = {}
        self.annotations: dict[str, Annotations] = {}
        self._deliveries: dict[str, _Delivery] = {}  # insertion order is queue order
        self._changed = asyncio.Event()

    @asynccontextmanager
    async def writer(self, message_id: str, envelope: Envelope) -> AsyncIterator[_FakeWriter]:
        w = _FakeWriter(self, message_id, envelope)
        try:
            yield w
        finally:
            committed, w.done = w.done, True
        if not committed:
            raise StoreAborted(f"{message_id}: left without commit")

    def _commit(
        self, message_id: str, envelope: Envelope, body: bytes, annotations: Annotations
    ) -> tuple[str, ...]:
        self.bodies[message_id] = body
        self.annotations[message_id] = dict(annotations)
        ids = []
        for n, rcpt in enumerate(envelope.recipients, 1):
            did = delivery_id(message_id, n)
            self._deliveries[did] = _Delivery(message_id, envelope.for_recipient(rcpt), rcpt)
            ids.append(did)
        self._changed.set()
        return tuple(ids)

    async def lease(self, consumer: str, limit: int, seconds: int) -> list[Lease]:
        now = time.monotonic()
        out: list[Lease] = []
        for did, d in self._deliveries.items():
            if len(out) >= limit:
                break
            if d.queue == consumer and (d.token is None or d.expires <= now):
                d.token, d.expires = secrets.token_hex(8), now + seconds
                out.append(Lease(did, d.token))
        return out

    def _held(self, delivery_id: str, token: str | None = None) -> _Delivery:
        d = self._deliveries[delivery_id]
        held = d.token is not None and (d.token == token if token else d.expires > time.monotonic())
        if not held:
            raise KeyError(f"{delivery_id} is not leased" + (" with that token" if token else ""))
        return d

    async def open(self, delivery_id: str) -> Opened:
        d = self._held(delivery_id)
        body = self.bodies[d.message_id]
        return Opened(d.envelope, self.annotations[d.message_id], _stream(body))

    async def ack(self, delivery_id: str, token: str) -> None:
        self._held(delivery_id, token)
        await self.delete(delivery_id)

    async def nack(self, delivery_id: str, token: str) -> None:
        self._held(delivery_id, token).token = None
        self._changed.set()

    async def delete(self, delivery_id: str) -> None:
        mid = self._deliveries.pop(delivery_id).message_id
        if all(d.message_id != mid for d in self._deliveries.values()):
            del self.bodies[mid], self.annotations[mid]

    async def watch(self) -> AsyncIterator[None]:
        while True:
            await self._changed.wait()
            self._changed.clear()
            yield

    async def usage(self) -> Usage:
        return Usage(sum(map(len, self.bodies.values())), len(self._deliveries))


class FakeIngestor:
    """Submits each message once, then returns. ``results`` holds each id or the TrunkError."""

    def __init__(self, messages: Iterable[tuple[Envelope, bytes]]) -> None:
        self.messages = list(messages)
        self.results: list[str | TrunkError] = []

    async def listen(self, submit: Submit) -> None:
        for envelope, body in self.messages:
            try:
                self.results.append(await submit(envelope, _stream(body)))
            except TrunkError as e:
                self.results.append(e)


class RecordingListenerHost:
    """Records every event. Returns ``annotations`` for inline events, nothing after ``stored``."""

    def __init__(self, annotations: Annotations | None = None) -> None:
        self.events: list[ListenerEvent] = []
        self.annotations: Annotations = annotations or {}

    async def emit(self, event: ListenerEvent) -> Annotations:
        self.events.append(event)
        return {} if isinstance(event, StoredEvent) else self.annotations
