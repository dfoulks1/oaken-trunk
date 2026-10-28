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
