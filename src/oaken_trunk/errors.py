# SPDX-License-Identifier: Apache-2.0
"""The error table: each condition maps to an SMTP reply, an HTTP status and a ``submit`` exit.

Exit codes are sysexits as Postfix reads them: 75 is temporary, 65, 67 and 77 are permanent.
"""

from __future__ import annotations

from enum import Enum
from typing import NamedTuple


class Codes(NamedTuple):
    smtp: str
    http: int
    exit: int


class Condition(Enum):
    INFLIGHT_LIMIT = "inflight limit"
    TOO_LARGE = "too large"
    SPOOL_FULL = "spool full"
    SPOOL_UNAVAILABLE = "spool unavailable"
    MALFORMED = "malformed"
    REFUSED_RECIPIENT = "refused recipient"
    UNAUTHORISED = "unauthorised"
    INTERRUPTED = "interrupted"


CODES: dict[Condition, Codes] = {
    Condition.INFLIGHT_LIMIT: Codes("451 4.3.2", 503, 75),
    Condition.TOO_LARGE: Codes("552 5.3.4", 413, 65),
    # max_spool_bytes or max_deliveries
    Condition.SPOOL_FULL: Codes("452 4.3.1", 507, 75),
    Condition.SPOOL_UNAVAILABLE: Codes("451 4.3.0", 503, 75),
    Condition.MALFORMED: Codes("554 5.6.0", 400, 65),
    # outside [mail] local_domains, or no device (ADR 0013)
    Condition.REFUSED_RECIPIENT: Codes("550 5.1.1", 422, 67),
    Condition.UNAUTHORISED: Codes("530 5.7.0", 401, 77),
    # the sender's stream failed partway; nothing was stored
    Condition.INTERRUPTED: Codes("451 4.4.2", 400, 75),
}


class TrunkError(Exception):
    """An error a door turns into a reply. ``codes`` gives all three forms.

    ``retry_after_seconds`` is set when the door should say when to retry (HTTP ``Retry-After``).
    """

    def __init__(
        self, condition: Condition, detail: str = "", *, retry_after_seconds: int | None = None
    ) -> None:
        super().__init__(detail or condition.value)
        self.condition = condition
        self.retry_after_seconds = retry_after_seconds

    @property
    def codes(self) -> Codes:
        return CODES[self.condition]
