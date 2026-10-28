# SPDX-License-Identifier: Apache-2.0
"""The engine: stream one message into the spool under limits, fire the listener events in order,
and commit (docs/architecture/ingestion.md).

Order: recipients, a slot, the spool caps, ``envelope``, the header block and ``headers``, the body
through the digest taps, ``end``, ``commit(annotations)``, ``stored``. It holds at most one chunk
plus the header block. It knows nothing of HTTP, the CLI or the registry.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import re
from collections.abc import AsyncGenerator, AsyncIterable, Callable, Mapping
from contextlib import aclosing
from dataclasses import dataclass, replace
from typing import Protocol

from oaken_trunk.credits import Credits, MemoryCredits
from oaken_trunk.devices import Devices
from oaken_trunk.envelope import Envelope, is_local, normalise_address
from oaken_trunk.errors import Condition, TrunkError
from oaken_trunk.events import (
    JSON,
    EndEvent,
    EnvelopeEvent,
    HeadersEvent,
    ListenerEvent,
    ListenerHost,
    StoredEvent,
)
from oaken_trunk.ids import new_id
from oaken_trunk.settings import Settings
from oaken_trunk.spool import Spool, SpoolWriter

CHUNK_SIZE = 64 * 1024
LISTENER_TIMEOUT_SECONDS = 5.0
_BLANK_LINE = re.compile(rb"(?:^|\n)\r?\n")
_EVENT_NAMES = {EnvelopeEvent: "envelope", HeadersEvent: "headers", EndEvent: "end"}
log = logging.getLogger(__name__)


class DigestTap(Protocol):
    def update(self, data: bytes, /) -> None: ...

    def hexdigest(self) -> str: ...


# Named taps over the raw body. CORE_mail-authentication adds more.
DIGEST_TAPS: Mapping[str, Callable[[], DigestTap]] = {"sha256": hashlib.sha256}


@dataclass(frozen=True)
class Receipt:
    """The answer per recipient: accepted ones were committed, refused ones say why."""

    message_id: str
    delivery_ids: tuple[str, ...]
    accepted: tuple[str, ...]
    refused: Mapping[str, TrunkError]


def parse_headers(block: bytes) -> tuple[tuple[str, str], ...]:
    """(name, value) pairs from a header block, unfolded. A line with no colon is skipped."""
    out: list[tuple[str, str]] = []
    for line in re.split(r"\r?\n", block.decode("utf-8", "replace")):
        if line[:1] in (" ", "\t") and out:
            out[-1] = (out[-1][0], out[-1][1] + line)
        elif ":" in line:
            name, _, value = line.partition(":")
            out.append((name.strip(), value.strip()))
    return tuple(out)


class Engine:
    def __init__(
        self,
        settings: Settings,
        spool: Spool,
        devices: Devices,
        listeners: ListenerHost | None = None,
        credits: Credits | None = None,
        digest_taps: Mapping[str, Callable[[], DigestTap]] = DIGEST_TAPS,
        listener_timeout: float = LISTENER_TIMEOUT_SECONDS,
    ) -> None:
        self._settings, self._spool, self._devices = settings, spool, devices
        self._listeners, self._taps, self._timeout = listeners, digest_taps, listener_timeout
        server = settings.server
        self._credits = credits or MemoryCredits(server.max_inflight, server.retry_after_seconds)

    async def ingest(self, envelope: Envelope, chunks: AsyncIterable[bytes]) -> Receipt:
        """Stream one message in. Raises a ``TrunkError`` when nothing was stored."""
        accepted, refused = await self._recipients(envelope.recipients)
        if not accepted:
            raise TrunkError(Condition.REFUSED_RECIPIENT, "no recipient accepted")
        if not await self._credits.take():
            raise TrunkError(
                Condition.INFLIGHT_LIMIT, retry_after_seconds=self._credits.retry_after_seconds()
            )
        try:
            mid = new_id()
            ids = await self._store(mid, replace(envelope, recipients=accepted), chunks)
            return Receipt(mid, ids, accepted, refused)
        finally:
            await self._credits.release()

    async def _recipients(
        self, recipients: tuple[str, ...]
    ) -> tuple[tuple[str, ...], dict[str, TrunkError]]:
        accepted: list[str] = []
        refused: dict[str, TrunkError] = {}
        domains = self._settings.mail.local_domains  # empty accepts nothing
        for rcpt in recipients:
            try:
                address = normalise_address(rcpt)
                if not is_local(address, domains):
                    raise TrunkError(Condition.REFUSED_RECIPIENT, "not a local domain")
                if not await self._devices.has_device(address):
                    raise TrunkError(Condition.REFUSED_RECIPIENT, "user doesn't exist")
            except TrunkError as e:
                refused[rcpt] = e
                continue
            if address not in accepted:
                accepted.append(address)
        return tuple(accepted), refused

    async def _store(
        self, mid: str, envelope: Envelope, source: AsyncIterable[bytes]
    ) -> tuple[str, ...]:
        caps = self._settings.spool
        max_header = self._settings.server.max_header_bytes
        annotations: dict[str, JSON] = {}
        errors: dict[str, str] = {}
        taps = {name: make() for name, make in self._taps.items()}
        head: bytearray | None = bytearray()  # None once the header block is written
        size = 0
        try:
            usage = await self._spool.usage()
            if (
                usage.body_bytes >= caps.max_spool_bytes
                or usage.deliveries + len(envelope.recipients) > caps.max_deliveries
            ):
                raise TrunkError(Condition.SPOOL_FULL)
            await self._emit(EnvelopeEvent(mid, envelope), annotations, errors)
            async with (
                self._spool.writer(mid, envelope) as writer,
                aclosing(self._bounded(source)) as chunks,
            ):
                async for chunk in chunks:
                    size += len(chunk)
                    if head is None:
                        for tap in taps.values():
                            tap.update(chunk)
                        await writer.write(chunk)
                        continue
                    searched = max(0, len(head) - 3)  # a blank line may straddle chunks
                    head += chunk
                    found = _BLANK_LINE.search(head, searched)
                    end = found.end() if found else len(head)
                    if end > max_header:
                        raise TrunkError(Condition.TOO_LARGE, "header block over max_header_bytes")
                    if found:
                        await self._flush_head(mid, head, end, taps, writer, annotations, errors)
                        head = None
                if head is not None:  # no blank line: the whole message is a header block
                    await self._flush_head(mid, head, len(head), taps, writer, annotations, errors)
                digests = {name: tap.hexdigest() for name, tap in taps.items()}
                await self._emit(EndEvent(mid, size, digests), annotations, errors)
                if errors:
                    annotations["engine"] = {"listener_errors": dict(errors)}
                ids = await writer.commit(annotations)
        except TrunkError:
            raise
        except Exception as e:
            raise TrunkError(Condition.SPOOL_UNAVAILABLE) from e
        await self._emit(StoredEvent(mid, ids, annotations), {}, {})
        return ids

    async def _flush_head(
        self,
        mid: str,
        head: bytearray,
        end: int,
        taps: Mapping[str, DigestTap],
        writer: SpoolWriter,
        annotations: dict[str, JSON],
        errors: dict[str, str],
    ) -> None:
        await self._emit(HeadersEvent(mid, parse_headers(bytes(head[:end]))), annotations, errors)
        body = bytes(head[end:])
        for tap in taps.values():
            tap.update(body)
        for i in range(0, len(head), CHUNK_SIZE):
            await writer.write(bytes(head[i : i + CHUNK_SIZE]))

    async def _bounded(self, source: AsyncIterable[bytes]) -> AsyncGenerator[bytes]:
        """Re-chunk to at most ``CHUNK_SIZE``. Stop reading at the first byte over the limit."""
        limit, size, it = self._settings.server.max_message_size, 0, aiter(source)
        while True:
            try:
                chunk = await anext(it)
            except StopAsyncIteration:
                return
            except TrunkError:
                raise
            except Exception as e:
                raise TrunkError(Condition.INTERRUPTED, "the message stream failed") from e
            size += len(chunk)
            if size > limit:
                raise TrunkError(Condition.TOO_LARGE, "over max_message_size")
            for i in range(0, len(chunk), CHUNK_SIZE):
                yield chunk[i : i + CHUNK_SIZE]

    async def _emit(
        self, event: ListenerEvent, annotations: dict[str, JSON], errors: dict[str, str]
    ) -> None:
        """Run listeners, time-bounded. A failure is recorded and never changes the answer."""
        if self._listeners is None:
            return
        name = _EVENT_NAMES.get(type(event), "stored")
        try:
            async with asyncio.timeout(self._timeout):
                annotations.update(await self._listeners.emit(event))
        except Exception as e:
            errors[name] = "timeout" if isinstance(e, TimeoutError) else type(e).__name__
            log.warning("%s listener failed for %s: %s", name, event.message_id, errors[name])
