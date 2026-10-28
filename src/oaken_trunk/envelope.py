# SPDX-License-Identifier: Apache-2.0
"""The envelope: who a message is from and for, and how it arrived. Immutable."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime

from oaken_trunk.errors import Condition, TrunkError


def normalise_address(address: str) -> str:
    """Lowercase the domain. The local part, ``+tag`` included, stays as given."""
    local, at, domain = address.rpartition("@")
    if not at or not local or not domain:
        raise TrunkError(Condition.MALFORMED, f"not an address: {address!r}")
    return f"{local}@{domain.lower()}"


def is_local(address: str, local_domains: list[str]) -> bool:
    """Whether Trunk accepts mail for ``address`` (``[mail] local_domains``, already lowercase)."""
    return normalise_address(address).rpartition("@")[2] in local_domains


@dataclass(frozen=True)
class Envelope:
    mail_from: str  # "" for the null sender
    recipients: tuple[str, ...]
    surface: str  # the ingest surface: http, cli, lmtp, smtp
    received_at: datetime
    original_recipient: str | None = None  # when the MTA gives one
    client_ip: str | None = None
    helo: str | None = None
    tls: bool = False
    principal: str | None = None  # the authenticated key or user

    def for_recipient(self, recipient: str) -> Envelope:
        """The envelope of one delivery: this one, with its one recipient."""
        return replace(self, recipients=(recipient,))
