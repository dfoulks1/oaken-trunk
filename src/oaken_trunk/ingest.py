# SPDX-License-Identifier: Apache-2.0
"""The ingestor contract. An ingestor reaches the engine through ``submit``, never the spool."""

from __future__ import annotations

from collections.abc import AsyncIterable, Awaitable, Callable
from typing import Protocol, TypeAlias

from oaken_trunk.envelope import Envelope

# The `submit` operation: stream one message in, get its id, or a TrunkError to reply with.
Submit: TypeAlias = Callable[[Envelope, AsyncIterable[bytes]], Awaitable[str]]


class Ingestor(Protocol):
    async def listen(self, submit: Submit) -> None:
        """Accept mail until cancelled, handing each message to ``submit``."""
        ...
