# SPDX-License-Identifier: Apache-2.0
import asyncio
import hashlib
import time
import tracemalloc
from collections.abc import AsyncIterator, Iterable
from datetime import UTC, datetime
from typing import Any

import pytest

from oaken_trunk.credits import MemoryCredits
from oaken_trunk.devices import Devices
from oaken_trunk.engine import CHUNK_SIZE, Engine, Receipt
from oaken_trunk.envelope import Envelope
from oaken_trunk.errors import Condition, TrunkError
from oaken_trunk.events import Annotations, EndEvent, HeadersEvent, ListenerEvent, StoredEvent
from oaken_trunk.settings import Mail, Server, Settings, Spool
from oaken_trunk.testing import (
    PLAIN,
    FakeDevices,
    FakeIngestor,
    FakeSpool,
    RecordingListenerHost,
    chunks,
    fakes,
)

BOB = "bob@example.org"
_devices: Devices = FakeDevices()  # under mypy, proves the double satisfies the protocol


def _env(*recipients: str) -> Envelope:
    return Envelope("alice@example.org", recipients or (BOB,), "cli", datetime.now(UTC))


def _engine(
    spool: FakeSpool | None = None,
    *,
    server: dict[str, Any] | None = None,
    spool_caps: dict[str, Any] | None = None,
    domains: Iterable[str] = ("example.org",),
    **kw: Any,
) -> Engine:
    settings = Settings(
        server=Server(**(server or {})),
        spool=Spool(**(spool_caps or {})),
        mail=Mail(local_domains=list(domains)),
    )
    return Engine(settings, spool or FakeSpool(), FakeDevices([BOB]), **kw)


async def _src(body: bytes, size: int = CHUNK_SIZE) -> AsyncIterator[bytes]:
    for c in chunks(body, size):
        yield c


async def _lease_all(spool: FakeSpool, who: str = BOB) -> list[str]:
    return [lease.delivery_id for lease in await spool.lease(who, 10, 60)]


async def test_one_gib_streams_in_bounded_chunks_and_memory() -> None:
    total, filler = 1 << 30, b"x" * CHUNK_SIZE

    async def source() -> AsyncIterator[bytes]:
        yield PLAIN
        for _ in range((total - len(PLAIN)) // CHUNK_SIZE):
            yield filler

    spool = FakeSpool(keep_bodies=False)
    engine = _engine(spool, server={"max_message_size": 2 << 30})
    start = time.perf_counter()
    tracemalloc.start()
    try:
        receipt = await engine.ingest(_env(), source())
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    print(f"1 GiB: {time.perf_counter() - start:.1f}s, peak {peak / 2**20:.2f} MiB")
    assert len(receipt.delivery_ids) == 1
    assert spool.largest_write <= CHUNK_SIZE
    assert peak < 8 << 20


async def test_end_to_end_through_an_ingestor() -> None:
    spool, host = FakeSpool(), RecordingListenerHost({"spam": {"score": 1}})
    engine = _engine(spool, listeners=host)

    async def submit(envelope: Envelope, source: Any) -> str:
        return (await engine.ingest(envelope, source)).message_id

    ingestor = FakeIngestor([(_env(), PLAIN)])
    await ingestor.listen(submit)
    [mid] = ingestor.results
    assert spool.bodies[str(mid)] == PLAIN
    assert spool.annotations[str(mid)] == {"spam": {"score": 1}}
    assert [type(e).__name__ for e in host.events] == [
        "EnvelopeEvent",
        "HeadersEvent",
        "EndEvent",
        "StoredEvent",
    ]
    headers, end = host.events[1], host.events[2]
    assert isinstance(headers, HeadersEvent) and isinstance(end, EndEvent)
    assert ("Subject", "Plain test message") in headers.headers
    body = PLAIN.split(b"\r\n\r\n", 1)[1]
    assert end.size == len(PLAIN)
    assert end.digests == {"sha256": hashlib.sha256(body).hexdigest()}


@pytest.mark.parametrize("size", [1, 7, 200 << 10])
async def test_rechunks_and_finds_the_header_block_at_any_chunking(size: int) -> None:
    message = PLAIN + b"y" * (130 << 10)
    spool, host = FakeSpool(), RecordingListenerHost()
    receipt = await _engine(spool, listeners=host).ingest(_env(), _src(message, size))
    assert spool.bodies[receipt.message_id] == message
    assert spool.largest_write <= CHUNK_SIZE
    end = host.events[2]
    assert isinstance(end, EndEvent)
    assert end.digests["sha256"] == hashlib.sha256(message.split(b"\r\n\r\n", 1)[1]).hexdigest()


async def test_message_of_exactly_max_size_is_accepted() -> None:
    spool = FakeSpool()
    receipt = await _engine(spool, server={"max_message_size": len(PLAIN)}).ingest(
        _env(), _src(PLAIN, 10)
    )
    assert spool.bodies[receipt.message_id] == PLAIN


async def test_one_byte_over_is_refused_and_the_source_not_read_to_its_end() -> None:
    message = PLAIN + b"z" * 10_000
    read = 0

    async def source() -> AsyncIterator[bytes]:
        nonlocal read
        for c in chunks(message, 10):
            read += len(c)
            yield c

    spool = FakeSpool()
    engine = _engine(spool, server={"max_message_size": len(PLAIN) - 1})
    with pytest.raises(TrunkError) as e:
        await engine.ingest(_env(), source())
    assert e.value.codes == ("552 5.3.4", 413, 65)
    assert read < len(PLAIN) + 10  # the chunk holding the first byte over, and no more
    assert not spool.bodies


async def test_header_block_over_max_header_bytes_is_refused() -> None:
    engine = _engine(server={"max_header_bytes": PLAIN.index(b"\r\n\r\n")})
    with pytest.raises(TrunkError) as e:
        await engine.ingest(_env(), _src(PLAIN))
    assert e.value.codes[::2] == ("552 5.3.4", 65)


async def test_recipients_are_accepted_or_refused_one_by_one() -> None:
    spool = FakeSpool()
    receipt = await _engine(spool).ingest(
        _env(BOB, "carol@example.org", "dave@elsewhere.example"), _src(PLAIN)
    )
    assert isinstance(receipt, Receipt)
    assert receipt.accepted == (BOB,) and len(receipt.delivery_ids) == 1
    assert sorted(receipt.refused) == ["carol@example.org", "dave@elsewhere.example"]
    assert {e.codes[::2] for e in receipt.refused.values()} == {("550 5.1.1", 67)}
    assert await _lease_all(spool) == list(receipt.delivery_ids)
    assert await _lease_all(spool, "carol@example.org") == []


@pytest.mark.parametrize("domains", [("example.org",), ()])
async def test_no_accepted_recipient_is_a_refusal_and_nothing_is_stored(
    domains: tuple[str, ...],
) -> None:
    spool = FakeSpool()
    recipients = ("carol@example.org",) if domains else (BOB,)
    with pytest.raises(TrunkError) as e:
        await _engine(spool, domains=domains).ingest(_env(*recipients), _src(PLAIN))
    assert e.value.codes == ("550 5.1.1", 422, 67)
    assert not spool.bodies


async def test_a_full_spool_refuses_before_writing() -> None:
    spool = FakeSpool()
    engine = _engine(spool, spool_caps={"max_deliveries": 1})
    await engine.ingest(_env(), _src(PLAIN))
    with pytest.raises(TrunkError) as e:
        await engine.ingest(_env(), _src(PLAIN))
    assert e.value.codes == ("452 4.3.1", 507, 75)
    assert len(spool.bodies) == 1


async def test_a_stream_failing_partway_leaves_nothing_visible() -> None:
    async def source() -> AsyncIterator[bytes]:
        yield PLAIN
        raise ConnectionResetError

    spool = FakeSpool()
    with pytest.raises(TrunkError) as e:
        await _engine(spool).ingest(_env(), source())
    assert e.value.codes == ("451 4.4.2", 400, 75)
    assert not spool.bodies and await _lease_all(spool) == []


async def test_a_spool_failing_partway_leaves_nothing_visible(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def broken(self: object, chunk: bytes) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(fakes._FakeWriter, "write", broken)
    spool = FakeSpool()
    with pytest.raises(TrunkError) as e:
        await _engine(spool).ingest(_env(), _src(PLAIN))
    assert e.value.codes == ("451 4.3.0", 503, 75)
    assert not spool.bodies


async def test_not_leasable_until_end_listeners_ran_and_commit_returned() -> None:
    spool = FakeSpool()
    seen: list[list[str]] = []

    class LeasingHost(RecordingListenerHost):
        async def emit(self, event: ListenerEvent) -> Annotations:
            if isinstance(event, EndEvent):
                seen.append(await _lease_all(spool))
            return await super().emit(event)

    receipt = await _engine(spool, listeners=LeasingHost()).ingest(_env(), _src(PLAIN))
    assert seen == [[]]
    assert await _lease_all(spool) == list(receipt.delivery_ids)


async def test_inflight_limit_and_the_slot_is_freed_every_way() -> None:
    credits = MemoryCredits(2, 30)
    engine = _engine(credits=credits)
    gate, entered = asyncio.Event(), asyncio.Queue[None]()

    async def gated() -> AsyncIterator[bytes]:
        entered.put_nowait(None)  # the engine reads only after it holds a slot
        await gate.wait()
        yield PLAIN

    async def held(n: int) -> None:
        async with asyncio.timeout(1):
            for _ in range(n):
                await entered.get()
        assert credits.used == n

    tasks = [asyncio.create_task(engine.ingest(_env(), gated())) for _ in range(2)]
    await held(2)
    with pytest.raises(TrunkError) as e:
        await engine.ingest(_env(), _src(PLAIN))
    assert e.value.condition is Condition.INFLIGHT_LIMIT
    assert e.value.retry_after_seconds == 30
    gate.set()
    await asyncio.gather(*tasks)  # success
    assert credits.used == 0

    with pytest.raises(TrunkError):  # failure
        await engine.ingest(_env(), _src(PLAIN + b"x" * (30 << 20)))
    assert credits.used == 0

    gate.clear()
    task = asyncio.create_task(engine.ingest(_env(), gated()))
    await held(1)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert credits.used == 0


async def test_slow_inline_listener_times_out_and_ingestion_succeeds() -> None:
    class SlowHeaders(RecordingListenerHost):
        async def emit(self, event: ListenerEvent) -> Annotations:
            if isinstance(event, HeadersEvent):
                await asyncio.sleep(10)
            return await super().emit(event)

    spool = FakeSpool()
    receipt = await _engine(spool, listeners=SlowHeaders(), listener_timeout=0.05).ingest(
        _env(), _src(PLAIN)
    )
    assert spool.annotations[receipt.message_id] == {
        "engine": {"listener_errors": {"headers": "timeout"}}
    }


async def test_a_failing_stored_listener_changes_nothing() -> None:
    class FailingStored(RecordingListenerHost):
        async def emit(self, event: ListenerEvent) -> Annotations:
            if isinstance(event, StoredEvent):
                raise RuntimeError("boom")
            return await super().emit(event)

    spool = FakeSpool()
    receipt = await _engine(spool, listeners=FailingStored()).ingest(_env(), _src(PLAIN))
    assert spool.annotations[receipt.message_id] == {}
    assert await _lease_all(spool) == list(receipt.delivery_ids)
