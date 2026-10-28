# SPDX-License-Identifier: Apache-2.0
"""Synthetic mail and test doubles. Tests only (an import-linter contract enforces it)."""

from oaken_trunk.testing.fakes import FakeDevices, FakeIngestor, FakeSpool, RecordingListenerHost
from oaken_trunk.testing.messages import (
    CHUNK_SIZE,
    MESSAGES,
    MULTIPART,
    OVERSIZED_HEADER,
    PLAIN,
    TRUNCATED,
    chunks,
)

__all__ = [
    "CHUNK_SIZE",
    "MESSAGES",
    "MULTIPART",
    "OVERSIZED_HEADER",
    "PLAIN",
    "TRUNCATED",
    "FakeDevices",
    "FakeIngestor",
    "FakeSpool",
    "RecordingListenerHost",
    "chunks",
]
