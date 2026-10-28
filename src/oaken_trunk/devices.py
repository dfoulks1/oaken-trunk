# SPDX-License-Identifier: Apache-2.0
"""What the engine asks of the device registry (ADR 0013). CORE_store's registry implements it."""

from __future__ import annotations

from typing import Protocol


class Devices(Protocol):
    async def has_device(self, address: str) -> bool:
        """Whether ``address`` (normalised) has at least one registered device."""
        ...
