# SPDX-License-Identifier: Apache-2.0
"""Listener events. Listeners see the envelope, headers and digests, never the body. They annotate.

``envelope``, ``headers`` and ``end`` run inline and time-bounded; ``stored`` follows a commit.
No event has a field that can hold body bytes (a test checks the field types).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol, TypeAlias

from oaken_trunk.envelope import Envelope

JSON: TypeAlias = None | bool | int | float | str | list["JSON"] | Mapping[str, "JSON"]
# A listener's annotation, keyed by the listener's name. Empty until a listener supplies one.
Annotations: TypeAlias = Mapping[str, JSON]


@dataclass(frozen=True)
class EnvelopeEvent:
    message_id: str
    envelope: Envelope


@dataclass(frozen=True)
class HeadersEvent:
    message_id: str
    headers: tuple[tuple[str, str], ...]  # (name, value), in order


@dataclass(frozen=True)
class EndEvent:
    message_id: str
    size: int
    digests: Mapping[str, str]  # algorithm -> hex digest of the body


@dataclass(frozen=True)
class StoredEvent:
    message_id: str
    delivery_ids: tuple[str, ...]
    annotations: Annotations


ListenerEvent: TypeAlias = EnvelopeEvent | HeadersEvent | EndEvent | StoredEvent


@dataclass(frozen=True)
class ListenerResult:
    """What one listener returns for one event: an annotation, or nothing."""

    annotation: JSON = None


class ListenerHost(Protocol):
    async def emit(self, event: ListenerEvent) -> Annotations:
        """Run the listeners for ``event``. Returns their annotations (empty after ``stored``)."""
        ...
