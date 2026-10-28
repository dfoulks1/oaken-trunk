# SPDX-License-Identifier: Apache-2.0
import asyncio
import dataclasses
import types
import typing
from collections.abc import AsyncIterable, Iterator
from datetime import UTC, datetime

import pytest

from oaken_trunk import events
from oaken_trunk.envelope import Envelope
from oaken_trunk.errors import Condition, TrunkError
from oaken_trunk.events import EndEvent, ListenerHost
from oaken_trunk.ingest import Ingestor
from oaken_trunk.spool import Spool, StoreAborted
from oaken_trunk.testing import PLAIN, FakeIngestor, FakeSpool, RecordingListenerHost, chunks

ENV = Envelope(
    mail_from="alice@example.org",
    recipients=("bob@example.org", "carol@example.org"),
    surface="cli",
    received_at=datetime(2026, 1, 1, tzinfo=UTC),
)

# Under mypy these assignments prove the doubles satisfy the protocols.
_spool: Spool = FakeSpool()
_ingestor: Ingestor = FakeIngestor([])
_host: ListenerHost = RecordingListenerHost()


async def _store(spool: Spool, mid: str = "M1") -> tuple[str, ...]:
    async with spool.writer(mid, ENV) as w:
        for c in chunks(PLAIN, 16):
            await w.write(c)
        return await w.commit({"spam": {"score": 1}})


async def test_commit_fans_out_one_delivery_per_recipient() -> None:
    spool = FakeSpool()
    assert await _store(spool) == ("M1-1", "M1-2")
    (lease,) = await spool.lease("carol@example.org", 10, 60)
    opened = await spool.open(lease.delivery_id)
    assert opened.envelope.recipients == ("carol@example.org",)
    assert opened.annotations == {"spam": {"score": 1}}
    assert b"".join([c async for c in opened.chunks]) == PLAIN
    usage = await spool.usage()
    assert (usage.body_bytes, usage.deliveries) == (len(PLAIN), 2)


async def test_ack_removes_delivery_and_last_ack_removes_body() -> None:
    spool = FakeSpool()
    await _store(spool)
    for rcpt in ENV.recipients:
        (lease,) = await spool.lease(rcpt, 10, 60)
        await spool.ack(lease.delivery_id, lease.token)
    assert spool.bodies == {}
    assert (await spool.usage()).deliveries == 0


async def test_nack_and_expiry_return_to_queue() -> None:
    spool = FakeSpool()
    await _store(spool)
    (lease,) = await spool.lease("bob@example.org", 10, 60)
    assert await spool.lease("bob@example.org", 10, 60) == []
    with pytest.raises(KeyError):
        await spool.ack(lease.delivery_id, "wrong")
    await spool.nack(lease.delivery_id, lease.token)
    (expired,) = await spool.lease("bob@example.org", 10, 0)
    assert len(await spool.lease("bob@example.org", 10, 60)) == 1
    with pytest.raises(KeyError):
        await spool.ack(expired.delivery_id, expired.token)


async def test_uncommitted_cannot_be_leased_and_abort_leaves_nothing() -> None:
    spool = FakeSpool()
    with pytest.raises(StoreAborted):
        async with spool.writer("M1", ENV) as w:
            await w.write(PLAIN)
    with pytest.raises(ValueError):
        async with spool.writer("M2", ENV) as w:
            await w.write(PLAIN)
            raise ValueError("client went away")
    assert await spool.lease("bob@example.org", 10, 60) == []
    assert (spool.bodies, spool.annotations) == ({}, {})
    assert (await spool.usage()).deliveries == 0


async def test_watch_wakes_on_commit() -> None:
    spool = FakeSpool()
    waiter = asyncio.ensure_future(anext(spool.watch()))
    await asyncio.sleep(0)
    assert not waiter.done()
    await _store(spool)
    await asyncio.wait_for(waiter, 1)


async def test_fake_ingestor_submits_and_records() -> None:
    async def submit(envelope: Envelope, body: AsyncIterable[bytes]) -> str:
        data = b"".join([c async for c in body])
        if not data:
            raise TrunkError(Condition.MALFORMED)
        return "M1"

    ingestor = FakeIngestor([(ENV, PLAIN), (ENV, b"")])
    await ingestor.listen(submit)
    assert ingestor.results[0] == "M1"
    assert isinstance(ingestor.results[1], TrunkError)


async def test_recording_host() -> None:
    host = RecordingListenerHost({"x": True})
    event = EndEvent("M1", 10, {"sha256": "00"})
    assert await host.emit(event) == {"x": True}
    assert await host.emit(events.StoredEvent("M1", ("M1-1",), {})) == {}
    assert host.events[0] is event


_BYTES_LIKE = {bytes, bytearray, memoryview, typing.Any, object}


def _leaf_types(hint: object, seen: set[int]) -> Iterator[object]:
    if id(hint) in seen:
        return
    seen.add(id(hint))
    if isinstance(hint, typing.ForwardRef):
        hint = getattr(events, hint.__forward_arg__)
    args = typing.get_args(hint)
    if isinstance(hint, types.UnionType) or args:
        for a in args:
            yield from _leaf_types(a, seen)
        origin = typing.get_origin(hint)
        if origin is not None and not isinstance(hint, types.UnionType):
            yield origin
    elif dataclasses.is_dataclass(hint) and isinstance(hint, type):
        for f in typing.get_type_hints(hint).values():
            yield from _leaf_types(f, seen)
    else:
        yield hint


@pytest.mark.parametrize("event", [*typing.get_args(events.ListenerEvent), events.ListenerResult])
def test_no_event_field_can_hold_body_bytes(event: type) -> None:
    leaves = set(_leaf_types(event, set()))
    assert str in leaves  # the walk reached the fields
    assert not leaves & _BYTES_LIKE, leaves & _BYTES_LIKE
