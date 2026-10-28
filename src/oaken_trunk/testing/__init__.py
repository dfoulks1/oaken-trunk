# SPDX-License-Identifier: Apache-2.0
"""Synthetic mail for tests. Every message here is fake and uses only ``example.org``.

Import this from tests only (an import-linter contract enforces it).
"""

from __future__ import annotations

from collections.abc import Iterator

CHUNK_SIZE = 64 * 1024

PLAIN = (
    b"From: Alice <alice@example.org>\r\n"
    b"To: Bob <bob@example.org>\r\n"
    b"Subject: Plain test message\r\n"
    b"Date: Thu, 01 Jan 2026 00:00:00 +0000\r\n"
    b"Message-ID: <plain.1@example.org>\r\n"
    b"MIME-Version: 1.0\r\n"
    b"Content-Type: text/plain; charset=us-ascii\r\n"
    b"\r\n"
    b"This is a synthetic test message.\r\n"
)

MULTIPART = (
    b"From: Alice <alice@example.org>\r\n"
    b"To: Bob <bob@example.org>\r\n"
    b"Subject: Multipart test message\r\n"
    b"Date: Thu, 01 Jan 2026 00:00:00 +0000\r\n"
    b"Message-ID: <multipart.1@example.org>\r\n"
    b"MIME-Version: 1.0\r\n"
    b'Content-Type: multipart/mixed; boundary="b1"\r\n'
    b"\r\n"
    b"--b1\r\n"
    b"Content-Type: text/plain; charset=us-ascii\r\n"
    b"\r\n"
    b"The text part.\r\n"
    b"--b1\r\n"
    b"Content-Type: application/octet-stream\r\n"
    b'Content-Disposition: attachment; filename="data.bin"\r\n'
    b"Content-Transfer-Encoding: base64\r\n"
    b"\r\n"
    b"AAECAwQFBgcICQ==\r\n"
    b"--b1--\r\n"
)

# One header line far over the RFC 5322 limit of 998 octets.
OVERSIZED_HEADER = (
    b"From: Alice <alice@example.org>\r\n"
    b"To: Bob <bob@example.org>\r\n"
    b"Subject: Oversized header test message\r\n"
    b"X-Oversized: " + b"a" * 4000 + b"\r\n"
    b"Message-ID: <oversized.1@example.org>\r\n"
    b"\r\n"
    b"Body after an oversized header.\r\n"
)

# Cut off mid-part: no closing boundary, no final CRLF.
TRUNCATED = MULTIPART[: MULTIPART.index(b"AAECAwQF") + 4]

MESSAGES: dict[str, bytes] = {
    "plain": PLAIN,
    "multipart": MULTIPART,
    "oversized_header": OVERSIZED_HEADER,
    "truncated": TRUNCATED,
}


def chunks(message: bytes, size: int = CHUNK_SIZE) -> Iterator[bytes]:
    """Yield ``message`` as a stream of ``size``-byte chunks (the last may be shorter)."""
    if size < 1:
        raise ValueError("chunk size must be at least 1")
    for start in range(0, len(message), size):
        yield message[start : start + size]
