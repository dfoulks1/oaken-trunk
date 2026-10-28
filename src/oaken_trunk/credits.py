# SPDX-License-Identifier: Apache-2.0
"""The limiter interface behind ``max_inflight`` and the spool caps."""

from __future__ import annotations

from typing import Protocol


class Credits(Protocol):
    async def take(self, n: int = 1) -> bool:
        """Take ``n`` credits, or none and return False."""
        ...

    async def release(self, n: int = 1) -> None: ...

    def retry_after_seconds(self) -> int:
        """How long a refused caller should wait (``Retry-After``) when none are left."""
        ...


class MemoryCredits:
    """``Credits`` in one process, a counter. Credits across workers are CORE_supervisor's."""

    def __init__(self, limit: int, retry_after_seconds: int) -> None:
        self.limit, self.used, self._retry_after = limit, 0, retry_after_seconds

    async def take(self, n: int = 1) -> bool:
        if self.used + n > self.limit:
            return False
        self.used += n
        return True

    async def release(self, n: int = 1) -> None:
        self.used = max(0, self.used - n)

    def retry_after_seconds(self) -> int:
        return self._retry_after
