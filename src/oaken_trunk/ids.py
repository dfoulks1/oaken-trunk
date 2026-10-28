# SPDX-License-Identifier: Apache-2.0
"""Message ids: a 48-bit millisecond timestamp and 80 random bits, in Crockford base32.

The alphabet is in ASCII order, so ids sort as strings by creation time. Ids made in the same
millisecond in one process increment the random part, so they sort in creation order too.
"""

from __future__ import annotations

import secrets
import threading
import time

_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_RANDOM_BITS = 80
_lock = threading.Lock()
_last = 0


def new_id() -> str:
    """A unique, time-ordered 26-character message id."""
    global _last
    with _lock:
        value = (time.time_ns() // 1_000_000) << _RANDOM_BITS | secrets.randbits(_RANDOM_BITS)
        # Same millisecond (or a clock step back): stay above the last id.
        value = max(value, _last + 1)
        _last = value
    return "".join(_ALPHABET[(value >> shift) & 31] for shift in range(125, -1, -5))


def delivery_id(message_id: str, n: int) -> str:
    """The id of one queue entry for ``message_id``: ``<id>-<n>``, also the POP3 ``UIDL``."""
    return f"{message_id}-{n}"
