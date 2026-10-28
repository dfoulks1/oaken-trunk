# SPDX-License-Identifier: Apache-2.0
"""The spool contract (docs/architecture/spool.md). Operations work on deliveries, ``<id>-<n>``."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from typing import Protocol

from oaken_trunk.envelope import Envelope
from oaken_trunk.events import Annotations


class StoreAborted(Exception):
    """A writer was left without ``commit``. Nothing became visible; partial data is gone."""


@dataclass(frozen=True)
class Lease:
    delivery_id: str
    token: str


@dataclass(frozen=True)
class Usage:
    body_bytes: int
    deliveries: int


@dataclass(frozen=True)
class Opened:
    """A leased delivery: its own envelope, the message's annotations, and the body as a stream."""

    envelope: Envelope
    annotations: Annotations
    chunks: AsyncIterator[bytes]


class SpoolWriter(Protocol):
    async def write(self, chunk: bytes) -> None: ...

    async def commit(self, annotations: Annotations) -> tuple[str, ...]:
        """Make the message visible and durable (per the store). Returns its delivery ids."""
        ...


class Spool(Protocol):
    def writer(
        self, message_id: str, envelope: Envelope
    ) -> AbstractAsyncContextManager[SpoolWriter]:
        """Leaving the block without ``commit`` aborts: nothing is visible, temporary data goes."""
        ...

    async def lease(self, consumer: str, limit: int, seconds: int) -> list[Lease]: ...

    async def open(self, delivery_id: str) -> Opened: ...

    async def ack(self, delivery_id: str, token: str) -> None: ...

    async def nack(self, delivery_id: str, token: str) -> None: ...

    async def delete(self, delivery_id: str) -> None: ...

    def watch(self) -> AsyncIterator[None]:
        """Yields whenever new deliveries may be waiting."""
        ...

    async def usage(self) -> Usage: ...
