# SPDX-License-Identifier: Apache-2.0
import email
import email.policy

import pytest

from oaken_trunk.testing import CHUNK_SIZE, MESSAGES, OVERSIZED_HEADER, TRUNCATED, chunks


@pytest.mark.parametrize("name", sorted(MESSAGES))
def test_messages_are_synthetic(name: str) -> None:
    msg = MESSAGES[name]
    assert b"@" in msg
    for token in msg.split():
        if b"@" in token:
            assert token.strip(b"<>,").endswith(b"@example.org"), token


@pytest.mark.parametrize("name", ["plain", "multipart"])
def test_well_formed_messages_parse(name: str) -> None:
    msg = email.message_from_bytes(MESSAGES[name], policy=email.policy.default)
    assert msg.defects == []
    assert msg["From"].addresses[0].domain == "example.org"


def test_oversized_header_exceeds_rfc_5322_line_limit() -> None:
    assert max(len(line) for line in OVERSIZED_HEADER.split(b"\r\n")) > 998


def test_truncated_has_no_closing_boundary() -> None:
    assert b"--b1--" not in TRUNCATED
    assert not TRUNCATED.endswith(b"\r\n")


@pytest.mark.parametrize("size", [1, 7, CHUNK_SIZE])
def test_chunks_reassemble(size: int) -> None:
    parts = list(chunks(OVERSIZED_HEADER, size))
    assert b"".join(parts) == OVERSIZED_HEADER
    assert all(len(p) == size for p in parts[:-1])
    assert 0 < len(parts[-1]) <= size


def test_chunks_rejects_zero_size() -> None:
    with pytest.raises(ValueError):
        list(chunks(b"x", 0))
